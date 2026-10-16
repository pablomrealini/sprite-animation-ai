"""Paso 4: QA automático de un clip, antes de que lo mire un humano.

Descarta por script lo que falla en lo mecánico: el frame 0 que no respeta la pose, cámara
que se mueve o hace zoom, personaje que se va de cuadro, cortes de escena, fondo sucio y
clips casi quietos. Los umbrales son heurísticos: calibrarlos con el bake-off.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import cv2
import numpy as np

from . import chroma, decimate, imgio, select
from .analysis import ClipAnalysis, analyze, linear_trend

# (warn, fail)
POSE_REGION_MAD = (15.0, 35.0)
DRIFT_PCT = (4.0, 20.0)  # deriva lineal total sobre el clip, % del alto del personaje
ZOOM_PCT = (5.0, 15.0)  # cambio lineal del alto del bbox sobre el clip
BG_STD = 6.0
BG_DRIFT = 8.0
CUT_FACTOR, CUT_MIN = 6.0, 12.0
LOW_MOTION = 1.0  # MAD 0..255 dentro del personaje por frame


def _fit_pose(pose_path: Path, size: tuple[int, int], key: np.ndarray) -> np.ndarray:
    pose = imgio.load(pose_path).astype(np.float32) / 255.0
    if pose.shape[2] == 4:  # componer sobre el color de fondo del clip
        a = pose[..., 3:4]
        pose = pose[..., :3] * a + key * (1 - a)
    W, H = size
    ph, pw = pose.shape[:2]
    if abs(pw / ph - W / H) < 0.02:
        return cv2.resize(pose, (W, H), interpolation=cv2.INTER_AREA)
    s = min(W / pw, H / ph)  # contain + relleno con el color de fondo
    rw, rh = round(pw * s), round(ph * s)
    canvas = np.empty((H, W, 3), np.float32)
    canvas[:] = key
    x, y = (W - rw) // 2, (H - rh) // 2
    canvas[y:y + rh, x:x + rw] = cv2.resize(pose, (rw, rh), interpolation=cv2.INTER_AREA)
    return canvas


def run(an: ClipAnalysis, first_frame: Path, kind: str, fps: float, pose: Path | None) -> dict:
    flags: list[tuple[str, str]] = []
    m: dict = {"frames": an.n, "fps": fps, "seconds": round(an.n / fps, 2)}

    have = ~np.isnan(an.bbox[:, 0])
    if not have.all():
        missing = int((~have).sum())
        flags.append(("fail", f"no se detecta el personaje en {missing} frames (¿fondo que no es de key?)"))
    key0 = an.keys[0]
    strength = chroma.key_strength(np.median(an.keys, axis=0))
    m["bg_color"] = "#" + "".join(f"{round(c * 255):02X}" for c in np.median(an.keys, axis=0))
    m["key_strength"] = round(strength, 3)
    m["key_method"] = "chroma" if strength >= chroma.CHROMA_MIN_STRENGTH else "distance"
    if m["key_method"] == "distance":
        flags.append(("warn", f"el fondo {m['bg_color']} no es verde ni magenta: uso key por distancia en modo "
                              "connected; funciona si el personaje tiene contorno y el fondo es plano"))

    h_med = float(np.nanmedian(an.heights)) if have.any() else 1.0
    m["char_height_px"] = round(h_med, 1)
    m["char_height_pct"] = round(100 * h_med / an.full_size[1], 1)

    # Frame 0 contra la pose de entrada
    if pose is not None and pose.exists():
        full0 = imgio.load(first_frame)[..., :3].astype(np.float32) / 255.0
        fitted = _fit_pose(pose, an.full_size, chroma.border_color(full0))
        size = an.masks[0].shape[::-1]
        a = cv2.resize(full0, size, interpolation=cv2.INTER_AREA)
        b = cv2.resize(fitted, size, interpolation=cv2.INTER_AREA)
        d = np.abs(a - b).mean(axis=-1) * 255
        pose_mask = chroma.estimate_alpha(b, key0) > 0.5
        region = an.masks[0] | pose_mask
        m["pose_mad_global"] = round(float(d.mean()), 2)
        m["pose_mad_region"] = round(float(d[region].mean()) if region.any() else 0.0, 2)
        w, f = POSE_REGION_MAD
        if m["pose_mad_region"] > f:
            flags.append(("fail", f"el frame 0 no respeta la pose (MAD {m['pose_mad_region']}): el modelo re-renderizó"))
        elif m["pose_mad_region"] > w:
            flags.append(("warn", f"el frame 0 se aparta de la pose (MAD {m['pose_mad_region']})"))

    # Deriva y zoom (en ciclos; en acciones de una pasada el movimiento es legítimo)
    sx, _ = linear_trend(an.centroid[:, 0])
    sy, _ = linear_trend(an.bbox[:, 3])
    sh, _ = linear_trend(an.heights)
    span = an.n - 1
    drift = 100 * np.hypot(sx, sy) * span / h_med
    zoom = 100 * abs(sh) * span / h_med
    m["drift_pct"] = round(float(drift), 1)
    m["drift_px_per_s"] = [round(sx * fps, 2), round(sy * fps, 2)]
    m["zoom_pct"] = round(float(zoom), 1)
    if kind == "cycle":
        for value, (w, f), what, note in (
            (drift, DRIFT_PCT, "deriva/paneo o el personaje se traslada", "la alineación saca la deriva lineal"),
            (zoom, ZOOM_PCT, "zoom o cambio de escala", "la alineación no lo corrige: regenerá o descartá"),
        ):
            if value > f:
                flags.append(("fail", f"{what}: {value:.1f}% del alto"))
            elif value > w:
                flags.append(("warn", f"{what}: {value:.1f}% del alto ({note})"))

    edge = int(an.touches_edge.sum())
    m["frames_touching_edge"] = edge
    if edge:
        flags.append(("warn", f"el personaje toca el borde del cuadro en {edge} frames (arma o capa cortada)"))

    # Fondo
    m["bg_std"] = round(float(np.nanmedian(an.bg_std)), 2)
    bg_drift = float(np.abs(an.keys - np.median(an.keys, axis=0)).max() * 255)
    m["bg_drift"] = round(bg_drift, 2)
    if m["bg_std"] > BG_STD:
        flags.append(("warn", f"fondo poco plano (desvío {m['bg_std']}): el key va a necesitar más tolerancia"))
    if bg_drift > BG_DRIFT:
        flags.append(("warn", f"el color del fondo cambia durante el clip ({bg_drift:.1f}/255)"))

    # Cortes de escena y movimiento
    if len(an.diff_global):
        med = float(np.median(an.diff_global))
        cuts = [i + 1 for i, d in enumerate(an.diff_global) if d > max(CUT_FACTOR * med, CUT_MIN)]
        m["scene_cuts_at"] = cuts
        if cuts:
            flags.append(("fail", f"posible corte de escena en los frames {cuts}"))
        motion = float(np.median(an.diff_char))
        m["motion"] = round(motion, 2)
        if motion < LOW_MOTION:
            flags.append(("warn", f"casi sin movimiento (mediana {motion:.2f}): típico de first==last"))
        tail = 0
        for d in an.diff_char[::-1]:
            if d >= 0.15 * motion:
                break
            tail += 1
        m["static_tail_frames"] = tail
        if tail > 0.25 * an.n:
            flags.append(("warn", f"el clip queda quieto en los últimos {tail} frames"))

    verdict = "fail" if any(l == "fail" for l, _ in flags) else "warn" if flags else "ok"
    return {"verdict": verdict, "flags": [{"level": l, "msg": s} for l, s in flags], "metrics": m}


def check_clip(clip: Path, pose: Path | None, kind: str, game_fps: int) -> dict:
    """QA y loop de un clip suelto, sin config: lo que comparan `check` y `bakeoff`."""
    tmp = Path(tempfile.mkdtemp(prefix="spritepipe_"))
    try:
        info = imgio.probe(clip)
        imgio.extract(clip, tmp, info)
        raw = imgio.frames(tmp)
        an = analyze(raw)
        res = run(an, raw[0], kind, info["fps"], pose)
        K, _, _ = decimate.factor(info["fps"], game_fps)
        loop = None
        if kind == "cycle":
            try:
                loop = select.find_loop(an, info["fps"], K, (0.5, 2.0), 0.25)
            except ValueError as e:
                loop = {"error": str(e)}
        return {"clip": clip, "frames": len(raw), "video": info, "qa": res, "loop": loop}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
