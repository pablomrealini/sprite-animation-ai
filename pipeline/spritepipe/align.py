"""Paso 8: un canvas, un pivot y una escala para todas las animaciones del personaje.

Por frame, sobre el alfa ya limpio: la fila opaca más baja es la línea de piso y el
centroide del alfa es el ancla horizontal (en un walk es más estable que el pie).
- En ciclos se saca sólo la deriva lineal (la cámara que se corre de a poco) y se conserva
  el bob propio de la animación.
- En oneshots se fija el ancla del frame 0 y se aplica el mismo desplazamiento a todos.
Después se calcula la unión de bboxes de TODAS las animaciones y un canvas simétrico
alrededor del pivot (abajo al centro), así el flipX en runtime no corre al personaje.
Los desplazamientos son enteros (sin resampleo); en pixel art, múltiplos del factor de grilla,
para que todos los frames compartan la misma fase de grilla.

Antes de eso, cada clip se lleva a los px de video de la animación de referencia. Los clips salen
de poses distintas y el modelo los devuelve en resoluciones distintas, así que el personaje no mide
lo mismo en px en todos. La escala de un clip es cuerpo de referencia / cuerpo del clip, donde el
cuerpo es el alto del personaje parado en px del video de cada uno:
- `body_height_px` en la animación lo fija a mano;
- con `pose`, si el frame 0 coincide con la pose (el QA no la rechaza), sale de comparar el alto
  del frame 0 con el de la pose: cuerpo = frame 0 × parado / pose, donde parado es el alto de la
  misma pose o, si no es de cuerpo parado (colgado, agachado), el de `scale_pose`, una pose parada
  armada a la misma escala, o `pose_body_height_px`, el alto parado en px de la pose;
- sin nada de eso, el clip queda a la escala de la referencia (×1) y, si su frame 0 mide más de un
  10% distinto que el de la referencia, se avisa.
El cuerpo de referencia es el que declara la animación de referencia o, si no declara nada, el
alto de referencia que se lleva a target_height. Una escala sacada de la pose a menos de un 2%
de 1 se deja en 1, porque es ruido de la medición. Los frames re-escalados quedan en
work/<anim>/03_scaled, y el canvas y el pivot se calculan después, sobre ellos.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from . import imgio, key, qa, reduce
from .analysis import linear_trend
from .config import Animation, Character
from .pose import OPAQUE

SCALE_TOLERANCE = 0.02  # una escala sacada de la pose a menos de esto de 1 se deja en 1
SCALE_MISMATCH = 0.10  # frame 0 sin escala declarada que difiere de la referencia en más de esto: aviso
POSE_SOURCES = ("pose", "scale_pose", "pose_body_height_px")  # escalas que salen de comparar frame 0 y pose


def _measure(alpha: np.ndarray) -> dict | None:
    solid = alpha >= 128
    if not solid.any():
        return None
    rows = solid.sum(axis=1)
    ys = np.nonzero(rows >= max(2, 0.01 * alpha.shape[1]))[0]
    if not len(ys):
        ys = np.nonzero(rows)[0]
    yy, xx = np.nonzero(solid)
    w = alpha.astype(np.float64)
    return {
        "ground": float(ys.max() + 1),
        "anchor_x": float((w.sum(axis=0) * (np.arange(alpha.shape[1]) + 0.5)).sum() / w.sum()),
        "bbox": (int(xx.min()), int(yy.min()), int(xx.max()) + 1, int(yy.max()) + 1),
    }


def image_anchor_x(img: np.ndarray, ch: Character, fixed_key: np.ndarray | None) -> float | None:
    """Ancla horizontal (centroide del alfa) de un frame sin keyear, en px del clip."""
    m = _measure(key.key_frame(img[..., :3], ch, fixed_key)[0][..., 3])
    return m["anchor_x"] if m else None


def body_height(alpha: np.ndarray) -> float | None:
    """Alto del personaje en px: desde la fila opaca más alta hasta la línea de piso."""
    m = _measure(alpha)
    return m["ground"] - m["bbox"][1] if m else None


def _image_body(img: np.ndarray, ch: Character, fixed_key: np.ndarray | None) -> float | None:
    """Alto del cuerpo en una imagen sin keyear (el frame 0 de un clip o una pose), con el key del personaje."""
    if img.shape[2] == 4 and (img[..., 3] < 255).any():  # concept con transparencia: sin la sombra de piso
        return body_height(np.where(img[..., 3] > OPAQUE, 255, 0).astype(np.uint8))
    return body_height(key.key_frame(img[..., :3], ch, fixed_key)[0][..., 3])


def clip_body(ch: Character, anim: Animation, frame0: np.ndarray, pose_mad: float | None,
              fixed_key: np.ndarray | None = None) -> dict:
    """Cuerpo del clip en px de su video, para la escala (ver clip_scales).

    frame0_px es el alto medido en el frame 0; body_px, el del cuerpo parado si la animación lo
    declara (`body_height_px`) o sale de la pose. pose_mad es el MAD del frame 0 contra la pose
    que da el QA: si la rechaza, la pose no sirve para la escala.
    """
    info = {"video": [frame0.shape[1], frame0.shape[0]], "frame0_px": _image_body(frame0, ch, fixed_key),
            "source": None, "body_px": None}
    if anim.body_height_px:
        info.update(source="body_height_px", body_px=anim.body_height_px)
    elif anim.pose is not None:
        if not anim.pose.exists():
            info["note"] = f"no encuentro la pose {anim.pose.name}: la escala no sale de la pose"
        elif pose_mad is None or pose_mad > qa.POSE_REGION_MAD[1]:
            info["note"] = (f"el frame 0 no coincide con la pose (MAD {pose_mad}): "
                            "la escala no sale de la pose; declarale body_height_px")
        elif info["frame0_px"]:
            if anim.scale_pose is not None and not anim.scale_pose.exists():
                raise FileNotFoundError(f"{anim.name}: no existe scale_pose {anim.scale_pose}")
            pose = imgio.load(anim.pose)
            pose_px = _image_body(pose, ch, None)
            standing, source = pose_px, "pose"
            if anim.scale_pose:
                standing, source = _image_body(imgio.load(anim.scale_pose), ch, None), "scale_pose"
            elif anim.pose_body_height_px:
                standing, source = anim.pose_body_height_px, "pose_body_height_px"
            if pose_px and standing:
                info.update(source=source,
                            body_px=info["frame0_px"] * (standing / pose_px),
                            pose_size=[pose.shape[1], pose.shape[0]], pose_px=pose_px, standing_pose_px=standing)
    return info


def _pose_group(b: dict) -> tuple | None:
    """Clips con poses del mismo tamaño y el mismo alto parado, devueltos a la misma resolución,
    están a la misma escala por construcción: la diferencia que se mida entre sus frames 0 es ruido."""
    if b.get("source") not in POSE_SOURCES:
        return None
    return tuple(b["video"]), tuple(b["pose_size"]), b["standing_pose_px"]


def clip_scales(ch: Character, names: list[str], bodies: dict[str, dict], ref_h: float,
                scale: float) -> dict[str, dict]:
    """Escala de cada clip para llevarlo a px de video de la referencia (1 = sin re-escalar).

    scale es la escala global (px finales por px de la referencia): sólo para informar el alto final.
    """
    ref = ch.scale_reference
    rb = bodies.get(ref, {})
    ref_body = rb.get("body_px") or ref_h
    ref_f0 = rb.get("frame0_px")
    groups: dict[tuple, list[str]] = {}
    for name in names:
        g = _pose_group(bodies.get(name, {}))
        if g:
            groups.setdefault(g, []).append(name)
    group_body = {g: rb["body_px"] if ref in m else float(np.median([bodies[n]["body_px"] for n in m]))
                  for g, m in groups.items()}

    out = {}
    for name in names:
        b = bodies.get(name, {})
        info = {"source": None, "body_px": None, **b, "scale": 1.0}
        g = _pose_group(b)
        if g and len(groups[g]) > 1:
            info["same_pose_as"] = [n for n in groups[g] if n != name]
            if group_body[g] != b["body_px"]:
                info["measured_body_px"], info["body_px"] = b["body_px"], group_body[g]
        if name == ref:
            info["reference_body_px"] = ref_body
        elif info["body_px"]:
            k = ref_body / info["body_px"]
            if info["source"] != "body_height_px" and k != 1 and abs(k - 1) <= SCALE_TOLERANCE:
                info["measured_scale"], k = k, 1.0
            info["scale"] = k
        elif b.get("frame0_px") and ref_f0 and abs(b["frame0_px"] / ref_f0 - 1) > SCALE_MISMATCH:
            f0 = b["frame0_px"]
            info["warning"] = (
                f"el frame 0 mide {f0:.0f} px y el de {ref} {ref_f0:.0f} px ({100 * (f0 / ref_f0 - 1):+.0f}%) "
                f"y no declara escala: sale a la escala de {ref}, con el cuerpo a ~{f0 * scale:.0f} px. "
                "Declarale `pose` (con `scale_pose` o `pose_body_height_px` si no arranca parado) o `body_height_px`")
        if info["body_px"] or name == ref:
            info["final_body_px"] = (info["body_px"] or ref_body) * info["scale"] * scale
        out[name] = {k: round(v, 4) if isinstance(v, float) else v for k, v in info.items()}
    return out


def _resample(paths: list[Path], out_dir: Path, k: float) -> tuple[list[Path], tuple[float, float]]:
    """Re-escala los frames keyeados en alfa premultiplicado. Devuelve las rutas y la escala real (x, y)."""
    out = imgio.reset_dir(out_dir)
    size = None
    for p in paths:
        img = imgio.load(p)
        if size is None:
            h, w = img.shape[:2]
            size = (max(1, round(w * k)), max(1, round(h * k)))
        imgio.save(out / p.name, reduce._to_u8(reduce._premul_resize(img, size)))
    return imgio.frames(out), (size[0] / w, size[1] / h)


def _snap(v: float, grid: int) -> int:
    return int(round(v / grid)) * grid


def _ceil_to(v: float, grid: int) -> int:
    return int(math.ceil(v / grid)) * grid


def _shifts(meas: list[dict | None], kind: str, grid: int,
            drift: tuple[float, float] | None) -> tuple[list[tuple[int, int]], list[float]]:
    """drift: deriva por frame de salida medida en el clip completo (ver select.periodic_drift).

    Sobre un solo ciclo la deriva no se puede estimar: una rampa muestreada en un período es
    indistinguible de un componente periódico. Sin ese dato se cae a una recta, que sesga.
    """
    ax = np.array([m["anchor_x"] if m else np.nan for m in meas])
    gy = np.array([m["ground"] if m else np.nan for m in meas])
    n = len(meas)
    if kind == "cycle":
        sx, sy = drift if drift is not None else (linear_trend(ax)[0], linear_trend(gy)[0])
        tc = np.arange(n) - (n - 1) / 2
        ref_x = np.nanmean(ax - sx * tc)
        ref_y = np.nanmean(gy - sy * tc)
        dx = -(sx * tc) - ref_x
        dy = -(sy * tc) - ref_y
        drift = [sx, sy]
    else:
        if meas[0] is None:
            raise ValueError("el frame 0 de un oneshot no tiene personaje: revisá el key o el trim")
        dx = np.full(n, -ax[0])
        dy = np.full(n, -gy[0])
        drift = [0.0, 0.0]
    return [(_snap(x, grid), _snap(y, grid)) for x, y in zip(dx, dy)], drift


def run(ch: Character, key_dirs: dict[str, Path], kinds: dict[str, str], out_dirs: dict[str, Path],
        drifts_in: dict[str, tuple[float, float]], bodies: dict[str, dict] | None = None) -> dict:
    """bodies: clip_body de cada animación. Sin eso, todos los clips quedan a la escala de la referencia."""
    frames = {name: imgio.frames(d) for name, d in key_dirs.items()}
    ref = ch.scale_reference
    meas = {ref: [_measure(imgio.load(p)[..., 3]) for p in frames[ref]]}

    ref_meas = [m for m in meas[ref] if m]
    ref_h = ch.body_height_px or float(np.median([m["ground"] - m["bbox"][1] for m in ref_meas]))
    if ch.style == "pixel":
        F = int(ch.pixel_factor or max(1, round(ref_h / ch.target_height)))
        scale, grid = 1.0 / F, F
    else:
        F, scale, grid = None, ch.target_height / ref_h, 1

    scales = clip_scales(ch, list(frames), bodies or {}, ref_h, scale)
    kxy = {}
    for name in frames:
        kxy[name] = (1.0, 1.0)
        if scales[name]["scale"] != 1.0:
            frames[name], kxy[name] = _resample(frames[name], ch.work_dir / name / "03_scaled", scales[name]["scale"])
            scales[name]["scale_xy"] = [round(v, 5) for v in kxy[name]]
        if name not in meas:
            meas[name] = [_measure(imgio.load(p)[..., 3]) for p in frames[name]]

    shifts, drifts = {}, {}
    minx = miny = math.inf
    maxx = maxy = -math.inf
    for name in frames:
        drift = drifts_in.get(name)
        if drift is not None:  # medida en px del clip
            drift = (drift[0] * kxy[name][0], drift[1] * kxy[name][1])
        shifts[name], drifts[name] = _shifts(meas[name], kinds[name], grid, drift)
        b = (bodies or {}).get(name, {})
        if ch.anchor == "clip" and b.get("frame0_anchor_x") is not None and b.get("native_indices"):
            # Todas las animaciones de un clip comparten el ancla de su frame 0 (la pose parada), corrida por la
            # deriva de cámara hasta cada frame. Así el cuerpo no salta cuando el brazo se extiende (el centroide
            # sí se corre) y las animaciones encadenadas de clips distintos arrancan en el mismo lugar.
            k, d = kxy[name][0], b.get("camera_drift_x", 0.0)
            shifts[name] = [(_snap(-(b["frame0_anchor_x"] + d * n) * k, grid), sy)
                            for n, (_, sy) in zip(b["native_indices"], shifts[name])]
        for m, (dx, dy) in zip(meas[name], shifts[name]):
            if m:
                x0, y0, x1, y1 = m["bbox"]
                minx, miny = min(minx, x0 + dx), min(miny, y0 + dy)
                maxx, maxy = max(maxx, x1 + dx), max(maxy, y1 + dy)

    margin = _ceil_to(ch.margin_px, grid)
    half = _ceil_to(max(-minx, maxx), grid) + margin
    top = _ceil_to(-miny, grid) + margin
    bottom = _ceil_to(max(maxy, 0), grid) + margin
    W, H = 2 * half, top + bottom

    for name, paths in frames.items():
        out = imgio.reset_dir(out_dirs[name])
        for p, (dx, dy) in zip(paths, shifts[name]):
            src = imgio.load(p)
            canvas = np.zeros((H, W, 4), np.uint8)
            ox, oy = half + dx, top + dy  # dónde cae el (0,0) del frame en el canvas
            sx0, sy0 = max(0, -ox), max(0, -oy)
            sx1, sy1 = min(src.shape[1], W - ox), min(src.shape[0], H - oy)
            if sx1 > sx0 and sy1 > sy0:
                canvas[sy0 + oy:sy1 + oy, sx0 + ox:sx1 + ox] = src[sy0:sy1, sx0:sx1]
            imgio.save(out / p.name, canvas)

    return {
        "canvas": {"w": W, "h": H},
        "pivot_px": {"x": half, "y": top},
        "scale": scale,
        "pixel_factor": F,
        "reference_height_px": round(ref_h, 1),
        "animations": {
            name: {
                "drift_removed_px_per_frame": [round(d, 3) for d in drifts[name]],
                "shifts": [list(s) for s in shifts[name]],
                "clip_scale": scales[name],
            }
            for name in frames
        },
    }
