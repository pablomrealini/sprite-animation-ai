"""Consistencia del torso en clips de video: cuánto cambia (o inventa) el modelo el torso cuadro a cuadro.

El torso (de la base del casco al cinturón, con el brazo que lo cruza) se recorta en cada cuadro y se compara:

- **deriva**: contra el torso del cuadro 0 (que es la pose) después de alinearlo por traslación. Es ΔE (CIE76,
  Lab) medio sobre los píxeles que son personaje en alguno de los dos; `cambio` es la fracción de esos píxeles
  con ΔE > 20, o sea, lo que a ojo es otra cosa. Mediana y p95 sobre los cuadros del clip.
- **ajeno**: contra la hoja de vistas. La hoja no tiene vista de costado, así que no se compara forma sino color:
  la fracción de píxeles del torso cuyo color no está en la hoja (ΔE > 15 al más cercano de su paleta). Un
  panel, una franja o un brillo que el modelo inventa aparece acá.
- **entre clips**: el torso medio de cada clip (alineado) contra el de los otros clips de la misma pose.
- **movimiento**: cuánto se traslada el torso respecto del cuadro 0, en px de la pose (p95 y máximo). Un idle casi
  quieto da un torso consistente sin mérito: los números de arriba se leen junto con este.

Uso (desde la raíz del repo):

    uv run --project pipeline python characters/lowpoly/medir_torso.py \
        --pose characters/lowpoly/poses/perfil_dullmagenta_16x9.png --box 820,478,985,645 \
        --hoja characters/lowpoly/refs/vistas_tpose_cinturon_rojo_alfa.png --out characters/lowpoly/torso/perfil clip1.mp4 clip2.mp4

`--box` va en px de la pose (x0,y0,x1,y1). Escribe `torso.json` y, por clip, una tira de torsos sobre verde.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np

from spritepipe import chroma, imgio

CHANGED_DE = 20.0  # ΔE a partir del cual un píxel "es otra cosa"
ALIEN_DE = 15.0  # ΔE al color más cercano de la hoja a partir del cual el color es inventado
SEARCH = 0.06  # radio de búsqueda de la traslación, en fracción del alto del clip
GREEN = np.array([0, 255, 0], np.float32)



def fal_matrix(info: dict) -> str | None:
    """fal entrega los videos en BT.601 sin tag (con BT.709 el rojo se corre a naranja); si el video trae tag, se usa."""
    return None if info.get("color_space") else "bt601"

def lab(rgb_u8: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(np.ascontiguousarray(rgb_u8, np.float32) / 255.0, cv2.COLOR_RGB2LAB)


def fg_mask(img: np.ndarray, key: np.ndarray) -> np.ndarray:
    # por distancia (ΔE > 20) y no por croma: con fondo magenta, el keyer de croma lee el rojo como fondo
    a = chroma.estimate_alpha(img.astype(np.float32) / 255.0, key / 255.0, method="distance")
    return a > 0.5


def sheet_palette(path: Path, k: int = 96) -> np.ndarray:
    """Colores Lab del personaje en la hoja: lo opaco si es transparente, o lo que se aleja del fondo de su fila."""
    raw = imgio.load(path)
    im = raw[..., :3]
    if raw.shape[2] == 4:  # hoja transparente: el personaje es lo opaco
        m = raw[..., 3] > 240
    else:
        f = im.astype(np.float32)
        bg_row = np.median(np.concatenate([f[:, :16], f[:, -16:]], 1), axis=1)  # fondo por fila
        m = np.linalg.norm(f - bg_row[:, None, :], axis=-1) > 30
    m = cv2.erode(m.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    px = lab(im)[m].reshape(-1, 3)
    rng = np.random.default_rng(0)
    px = px[rng.choice(len(px), min(len(px), 60000), replace=False)].astype(np.float32)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.2)
    _, _, centers = cv2.kmeans(px, k, None, crit, 2, cv2.KMEANS_PP_CENTERS)
    return centers


def alien_fraction(lab_px: np.ndarray, palette: np.ndarray) -> float:
    if not len(lab_px):
        return float("nan")
    d = np.sqrt(((lab_px[:, None, :] - palette[None]) ** 2).sum(-1)).min(1)
    return float((d > ALIEN_DE).mean())


def measure_clip(clip: Path, pose: np.ndarray, box: tuple[int, int, int, int], palette: np.ndarray | None,
                 strip_dir: Path | None, name: str | None = None) -> dict:
    info = imgio.probe(clip)
    frames = imgio.read_video(clip, info, fal_matrix(info))
    n, H, W, _ = frames.shape
    sx, sy = W / pose.shape[1], H / pose.shape[0]  # H3 Max devuelve 1344×768: no siempre es 16:9 exacto
    x0, x1 = round(box[0] * sx), round(box[2] * sx)
    y0, y1 = round(box[1] * sy), round(box[3] * sy)
    r = max(4, round(SEARCH * H))
    key = chroma.border_color(frames[0].astype(np.float32))

    # el cuadro 0 contra la pose, en la caja del torso: ¿se respetó el primer cuadro?
    pose_s = cv2.resize(pose, (W, H), interpolation=cv2.INTER_AREA)
    f0_mad = float(np.abs(frames[0][y0:y1, x0:x1].astype(np.float32) - pose_s[y0:y1, x0:x1]).mean())

    tmpl = frames[0][y0:y1, x0:x1]
    t_lab, t_fg = lab(tmpl), fg_mask(tmpl, key)
    t_er = cv2.erode(t_fg.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    sx0, sy0 = max(0, x0 - r), max(0, y0 - r)
    sx1, sy1 = min(W, x1 + r), min(H, y1 + r)

    per_frame, crops, acc, acc_n = [], [], np.zeros_like(t_lab), np.zeros(t_lab.shape[:2], np.float32)
    for i in range(n):
        f = frames[i]
        region = lab(f[sy0:sy1, sx0:sx1])
        res = cv2.matchTemplate(region, t_lab, cv2.TM_SQDIFF)
        _, _, (mx, my), _ = cv2.minMaxLoc(res)
        cx, cy = sx0 + mx, sy0 + my
        crop = f[cy:cy + (y1 - y0), cx:cx + (x1 - x0)]
        c_lab, c_fg = lab(crop), fg_mask(crop, key)
        union = t_fg | c_fg
        de = np.sqrt(((c_lab - t_lab) ** 2).sum(-1))
        de = np.where(t_fg & c_fg, de, 50.0)  # silueta distinta: cuenta como cambio total
        row = {"frame": i, "dx": cx - x0, "dy": cy - y0,
               "de": float(de[union].mean()) if union.any() else 0.0,
               "changed": float((de[union] > CHANGED_DE).mean()) if union.any() else 0.0}
        if palette is not None:
            c_er = cv2.erode(c_fg.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
            row["alien"] = alien_fraction(c_lab[c_er][::3], palette)
        per_frame.append(row)
        acc += np.where(c_fg[..., None], c_lab, 0)
        acc_n += c_fg
        crops.append(crop)

    rest = per_frame[1:] or per_frame
    de = np.array([p["de"] for p in rest])
    ch = np.array([p["changed"] for p in rest])
    out = {
        "clip": str(clip), "frames": n, "size": [W, H], "box_px": [x0, y0, x1, y1], "frame0_mad": round(f0_mad, 2),
        "de_median": round(float(np.median(de)), 2), "de_p95": round(float(np.percentile(de, 95)), 2),
        "changed_median": round(float(np.median(ch)), 4), "changed_p95": round(float(np.percentile(ch, 95)), 4),
        "max_shift_px": int(max(max(abs(p["dx"]), abs(p["dy"])) for p in per_frame)),
        # cuánto se mueve el torso (px de la pose): un idle quieto tiene un torso "consistente" sin mérito
        "move_p95": round(float(np.percentile([np.hypot(p["dx"] / sx, p["dy"] / sy) for p in per_frame], 95)), 1),
        "move_max": round(float(max(np.hypot(p["dx"] / sx, p["dy"] / sy) for p in per_frame)), 1),
    }
    if palette is not None:
        al = np.array([p["alien"] for p in per_frame])
        out["alien_pose"] = round(alien_fraction(lab(pose_s[y0:y1, x0:x1].astype(np.uint8))[t_er][::3], palette), 4)
        out["alien_median"] = round(float(np.nanmedian(al)), 4)
        out["alien_p95"] = round(float(np.nanpercentile(al, 95)), 4)
    out["per_frame"] = [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in p.items()} for p in per_frame]

    mean = acc / np.maximum(acc_n[..., None], 1)
    if strip_dir is not None:
        strip_dir.mkdir(parents=True, exist_ok=True)
        idx = np.linspace(0, n - 1, 9).round().astype(int)
        tiles = []
        for i in idx:
            c = crops[i]
            m = fg_mask(c, key)[..., None]
            tiles.append(np.where(m, c, GREEN).astype(np.uint8))
        gap = np.full((tiles[0].shape[0], 4, 3), 255, np.uint8)
        strip = np.concatenate(sum(([t, gap] for t in tiles), [])[:-1], 1)
        name = name or clip.stem
        imgio.save(strip_dir / f"{name}_torso.png", strip)
        out["name"] = name
        out["strip"] = str(strip_dir / f"{name}_torso.png")
        out["strip_frames"] = idx.tolist()
    # a px de la pose, para comparar clips de resoluciones distintas (H3 Max 1344×768, Seedance 1280×720...)
    bw, bh = box[2] - box[0], box[3] - box[1]
    out["_mean_lab"] = cv2.resize(mean, (bw, bh), interpolation=cv2.INTER_AREA)
    out["_mean_fg"] = cv2.resize((acc_n > (n / 2)).astype(np.uint8), (bw, bh), interpolation=cv2.INTER_NEAREST) > 0
    return out


def between(a: dict, b: dict) -> float:
    m = a["_mean_fg"] | b["_mean_fg"]
    de = np.sqrt(((a["_mean_lab"] - b["_mean_lab"]) ** 2).sum(-1))
    de = np.where(a["_mean_fg"] & b["_mean_fg"], de, 50.0)
    return round(float(de[m].mean()), 2)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("clips", nargs="+", type=Path)
    ap.add_argument("--pose", type=Path, required=True)
    ap.add_argument("--box", required=True, help="x0,y0,x1,y1 en px de la pose")
    ap.add_argument("--hoja", type=Path, help="hoja de vistas: paleta de colores válidos")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    box = tuple(int(v) for v in a.box.split(","))
    pose = imgio.load(a.pose)[..., :3].astype(np.float32)
    palette = sheet_palette(a.hoja) if a.hoja else None
    stems = [c.stem for c in a.clips]
    names = [f"{c.parent.name}_{c.stem}" if stems.count(c.stem) > 1 else c.stem for c in a.clips]
    results = [measure_clip(c, pose, box, palette, a.out, nm) for c, nm in zip(a.clips, names)]
    matrix = {names[i]: {names[j]: between(results[i], results[j]) for j in range(len(results)) if j != i}
              for i in range(len(results))}
    for r in results:
        del r["_mean_lab"], r["_mean_fg"]
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "torso.json").write_text(json.dumps({"pose": str(a.pose), "box": box, "hoja": str(a.hoja) if a.hoja else None,
                                                  "clips": results, "between": matrix}, indent=1, ensure_ascii=False))
    for r, nm in zip(results, names):
        al = f"  ajeno {r['alien_median']:.1%} (pose {r['alien_pose']:.1%})" if "alien_median" in r else ""
        others = list(matrix[nm].values())
        btw = f"  entre clips {np.mean(others):.1f}" if others else ""
        print(f"{nm:40s} f0 {r['frame0_mad']:5.1f}  mov p95 {r['move_p95']:4.1f}px  ΔE med {r['de_median']:5.1f} p95 {r['de_p95']:5.1f}  "
              f"cambio med {r['changed_median']:.1%} p95 {r['changed_p95']:.1%}{al}{btw}")


if __name__ == "__main__":
    main()
