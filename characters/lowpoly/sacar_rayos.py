"""Borra los rayos que Kling dispara aunque nadie se lo pida, sin comerse la boca del arma.

`remove_flash` corta desde el contorno oscuro más a la derecha del arma; en el arma low-poly la boca es una tapa con un
disco cian, y cuando el rayo sale pegado al disco se lleva la tapa y el disco: el arma queda corta. Acá la boca se
sigue con la forma del arma: el cuerpo del arma del cuadro 0 (sin la punta, donde pega el brillo del rayo) se busca
en cada cuadro por template matching, y la boca está siempre a la misma distancia de ese cuerpo. Se pinta con el color
del fondo todo lo que queda delante de la boca, en una franja alrededor de la altura del arma.

El cuadro 0 tiene que tener el arma entera y sin rayo (es la pose). Sale un H.264 sin pérdida (BT.709) y, al lado,
`<salida>.muzzle.json` con la boca por cuadro en px del clip, como el de `spritepipe remove-flash`.

Uso (desde la raíz del repo):

    uv run --project pipeline python characters/lowpoly/sacar_rayos.py clip.mp4 salida.mp4 --color-matrix bt601
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np

from spritepipe import chroma, imgio

SEARCH = 0.06  # cuánto puede moverse el arma respecto del cuadro anterior, en fracción del alto del clip


def lab(rgb: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(np.ascontiguousarray(rgb, np.float32) / 255.0, cv2.COLOR_RGB2LAB)


def muzzle_frame0(f: np.ndarray, key: np.ndarray) -> tuple[int, int, int, int]:
    """Boca del arma en el cuadro 0: el disco cian (G y B altos, R bajo) más a la derecha del personaje."""
    x = f.astype(int)
    cyan = (x[..., 1] > 140) & (x[..., 2] > 140) & (x[..., 0] < 140)
    n, lab_, st, _ = cv2.connectedComponentsWithStats(cyan.astype(np.uint8))
    if n < 2:
        raise ValueError("no encuentro el disco cian de la boca en el cuadro 0")
    i = 1 + max(range(n - 1), key=lambda k: st[k + 1, 0] + st[k + 1, 2])  # el que llega más a la derecha
    cx, cy, cw, ch = st[i, :4]
    # el frente de la boca: lo último que es personaje en las filas del disco
    alpha = chroma.estimate_alpha(f.astype(np.float32) / 255, key / 255, method="distance") > 0.5
    rows = alpha[cy:cy + ch]
    front = max(int(np.nonzero(r)[0].max()) for r in rows if r.any())
    return front, cy, cy + ch, ch


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("clip", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--color-matrix", choices=["bt601", "bt709"], help="los clips de fal vienen en BT.601 sin tag")
    a = ap.parse_args()

    info = imgio.probe(a.clip)
    frames = imgio.read_video(a.clip, info, a.color_matrix)
    n, H, W, _ = frames.shape
    key = chroma.border_color(frames[0].astype(np.float32))
    front0, y0, y1, dh = muzzle_frame0(frames[0], key)
    gun_len = round(0.135 * H)  # el arma mide ~96 px a 720p (144 px en la pose de 1080)
    pad = max(3, dh // 2)
    # el cuerpo del arma sin la punta: de la empuñadura a un disco antes de la boca
    tx0, tx1 = front0 - gun_len, front0 - 2 * dh
    ty0, ty1 = y0 - 2 * dh, y1 + dh
    tmpl = lab(frames[0][ty0:ty1, tx0:tx1])
    band = 3 * dh  # alto de la franja que se limpia arriba y abajo del disco (el halo del rayo)
    step = max(4, round(SEARCH * H))

    out_frames, track, px, py = [], [], tx0, ty0
    for i in range(n):
        f = frames[i].copy()
        sx0, sy0 = max(0, px - step), max(0, py - step)
        sx1, sy1 = min(W, px + (tx1 - tx0) + step), min(H, py + (ty1 - ty0) + step)
        res = cv2.matchTemplate(lab(f[sy0:sy1, sx0:sx1]), tmpl, cv2.TM_SQDIFF)
        _, _, (mx, my), _ = cv2.minMaxLoc(res)
        px, py = sx0 + mx, sy0 + my
        dx, dy = px - tx0, py - ty0
        fx, cy = front0 + dx + 1, (y0 + y1) // 2 + dy
        r0, r1 = max(0, cy - band), min(H, cy + band)
        before = int((np.abs(f[r0:r1, fx:].astype(int) - key).sum(-1) > 60).sum())
        f[r0:r1, fx:] = key.round().astype(np.uint8)
        out_frames.append(f)
        track.append({"frame": i, "x": int(fx), "y": int(cy), "px_borrados": before})

    imgio.encode_rgb_video(out_frames, a.out, info["fps"], crf=0, pix_fmt="yuv444p")
    a.out.with_suffix(".muzzle.json").write_text(json.dumps(
        {"clip": str(a.clip), "color_matrix": a.color_matrix, "nota": "x, y de la boca en px del clip",
         "muzzle": track}, indent=1, ensure_ascii=False))
    borr = [t["px_borrados"] for t in track]
    print(f"✓ {a.out}: {n} cuadros, boca en x {min(t['x'] for t in track)}–{max(t['x'] for t in track)}, "
          f"{sum(b > 50 for b in borr)} cuadros con rayo (hasta {max(borr)} px borrados)")


if __name__ == "__main__":
    main()
