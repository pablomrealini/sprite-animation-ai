"""Estrategia C: el clip trae al personaje sin arma (la mano en pose de agarre) y el arma se pega como sprite.

Por cuadro, el puño se sigue con template matching (traslación y un giro chico) contra el puño del cuadro 0, y el
arma se dibuja con la misma traslación y el mismo giro, **detrás** del personaje: así el puño tapa la empuñadura,
como en la pose con arma. Sale un clip sobre el mismo fondo (lo procesa `spritepipe run` como cualquier otro) y la
posición del arma por cuadro en JSON, que es lo que usaría el engine para dibujar el arma él mismo.

Uso (desde la raíz del repo):

    uv run --project pipeline python characters/lowpoly/pegar_arma.py clip.mp4 out.mp4 \
        --pose characters/lowpoly/poses/sin_arma_dullmagenta_16x9.png --mano 960,560,1045,645 \
        --arma characters/lowpoly/poses/arma_lateral.png --arma-en 987,520,0.1875

`--mano` es la caja del puño y `--arma-en` el x,y (arriba a la izquierda) y la escala del sprite, en px de la pose.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np

from spritepipe import chroma, imgio

ANGLES = np.arange(-12, 12.1, 2.0)  # grados que se prueban para el giro del puño
SEARCH = 0.05  # radio de búsqueda respecto del cuadro 0, en fracción del alto del clip
STEP = 0.045  # cuánto puede moverse el puño de un cuadro al siguiente, en fracción del alto



def fal_matrix(info: dict) -> str | None:
    """fal entrega los videos en BT.601 sin tag (con BT.709 el rojo se corre a naranja); si el video trae tag, se usa."""
    return None if info.get("color_space") else "bt601"

def lab(rgb: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(np.ascontiguousarray(rgb, np.float32) / 255.0, cv2.COLOR_RGB2LAB)


def rotate(img: np.ndarray, deg: float, center: tuple[float, float]) -> np.ndarray:
    m = cv2.getRotationMatrix2D(center, deg, 1.0)
    return cv2.warpAffine(img, m, (img.shape[1], img.shape[0]), flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REPLICATE)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("clip", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--pose", type=Path, required=True)
    ap.add_argument("--mano", required=True, help="x0,y0,x1,y1 del puño en px de la pose")
    ap.add_argument("--arma", type=Path, required=True, help="sprite RGBA del arma")
    ap.add_argument("--arma-en", required=True, help="x,y,escala del sprite en px de la pose")
    ap.add_argument("--buscar", type=float, default=SEARCH, help="radio de búsqueda del puño, fracción del alto")
    a = ap.parse_args()

    info = imgio.probe(a.clip)
    frames = imgio.read_video(a.clip, info, fal_matrix(info))
    n, H, W, _ = frames.shape
    ph, pw = imgio.load(a.pose).shape[:2]
    sx, sy = W / pw, H / ph  # H3 Max devuelve 1344×768: no siempre es 16:9 exacto
    mx0, my0, mx1, my1 = (float(v) for v in a.mano.split(","))
    x0, x1, y0, y1 = round(mx0 * sx), round(mx1 * sx), round(my0 * sy), round(my1 * sy)
    gx, gy, gscale = (float(v) for v in a.arma_en.split(","))
    gun = imgio.load(a.arma).astype(np.float32)
    gun = cv2.resize(gun, None, fx=gscale * sx, fy=gscale * sy, interpolation=cv2.INTER_AREA)
    gx, gy = gx * sx, gy * sy
    key = chroma.border_color(frames[0].astype(np.float32))

    # el puño del cuadro 0, girado: un template por ángulo
    r = max(4, round(a.buscar * H))
    pad = r
    big = lab(frames[0][max(0, y0 - pad):y1 + pad, max(0, x0 - pad):x1 + pad])
    c = (x0 - max(0, x0 - pad) + (x1 - x0) / 2, y0 - max(0, y0 - pad) + (y1 - y0) / 2)
    tx, ty = round(c[0] - (x1 - x0) / 2), round(c[1] - (y1 - y0) / 2)
    templates = {ang: rotate(big, ang, c)[ty:ty + (y1 - y0), tx:tx + (x1 - x0)] for ang in ANGLES}
    hand_c = ((x0 + x1) / 2, (y0 + y1) / 2)

    # el puño se busca alrededor de donde estaba en el cuadro anterior (paso de hasta STEP del alto por cuadro), así
    # no salta a la otra mano cuando el modelo la levanta; el radio total respecto del cuadro 0 sigue siendo r
    step = max(4, round(STEP * H))
    px, py = x0, y0
    track, out_frames, errs = [], [], []
    for i in range(n):
        f = frames[i]
        sx0, sy0 = max(0, x0 - r, px - step), max(0, y0 - r, py - step)
        sx1, sy1 = min(W, x1 + r, px + (x1 - x0) + step), min(H, y1 + r, py + (y1 - y0) + step)
        region = lab(f[sy0:sy1, sx0:sx1])
        best = None
        for ang, t in templates.items():
            res = cv2.matchTemplate(region, t, cv2.TM_SQDIFF)
            v, _, loc, _ = cv2.minMaxLoc(res)
            if best is None or v < best[0]:
                best = (v, ang, loc)
        err, ang, (mx, my) = best
        errs.append(err / templates[ang].size)  # SQDIFF por canal y píxel, en Lab: cuánto se parece al puño del cuadro 0
        px, py = sx0 + mx, sy0 + my
        dx, dy = px - x0, py - y0
        # el arma: giro alrededor del centro del puño del cuadro 0 y después la traslación del puño
        m = cv2.getRotationMatrix2D(hand_c, -ang, 1.0)  # el template se giró +ang para parecerse: el puño giró -ang
        m[:, 2] += (dx, dy)
        place = np.float32([[1, 0, gx], [0, 1, gy]])
        full = cv2.warpAffine(gun, np.vstack([m, [0, 0, 1]])[:2] @ np.vstack([place, [0, 0, 1]]), (W, H),
                              flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        ga = full[..., 3:4] / 255.0
        under = full[..., :3] * ga + key * (1 - ga)  # arma sobre el fondo
        ca = np.clip(chroma.estimate_alpha(f.astype(np.float32) / 255.0, key / 255.0, method="distance"), 0, 1)[..., None]
        comp = f.astype(np.float32) * ca + under * (1 - ca)  # el personaje encima del arma
        out_frames.append(np.clip(comp, 0, 255).round().astype(np.uint8))
        track.append({"frame": i, "dx": round(dx / sx, 2), "dy": round(dy / sy, 2), "deg": float(-ang)})

    fps = info.get("fps") or 24
    imgio.encode_rgb_video(out_frames, a.out, fps, crf=0, pix_fmt="yuv444p")
    meta = {"clip": str(a.clip), "pose": str(a.pose), "mano": a.mano, "arma": str(a.arma), "arma_en": a.arma_en,
            "nota": "dx, dy en px de la pose; deg: giro del arma alrededor del centro del puño del cuadro 0",
            "track": track}
    a.out.with_suffix(".arma.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False))
    dxs = [abs(t["dx"]) for t in track]
    dys = [abs(t["dy"]) for t in track]
    print(f"✓ {a.out}: {n} cuadros, puño hasta {max(dxs):.1f}/{max(dys):.1f} px (x/y de la pose), "
          f"giro {min(t['deg'] for t in track):+.0f}..{max(t['deg'] for t in track):+.0f}°, "
          f"error del puño mediana {np.median(errs):.0f} / máx {max(errs):.0f} (cuadro 0: {errs[0]:.0f})")


if __name__ == "__main__":
    main()
