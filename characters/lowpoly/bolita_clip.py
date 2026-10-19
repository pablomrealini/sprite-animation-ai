"""La bolita del doble salto como clip (clips/bolita/bolita.mp4), para que pase por el pipeline como cualquier toma.

En el doble salto de la tanda 3 (clips/tanda3/kling-o3-std_double_jump_1.mp4), mientras sostiene la bolita (23–41) el
casco crece ~30 % y pierde la franja roja: a tamaño de juego se lee como un huevo blanco. La bolita sostenida es
entonces poses/bolita.png (el juego la gira), y del video van sólo el encogerse y el abrirse.

Acá se pone poses/bolita.png sobre el magenta del clip, a la escala del video: el auricular rojo del casco (un disco,
que no cambia con el giro de la cabeza) mide 59,5 px en los nativos 20–21 del clip y se mide en la imagen. Así sale con
el mismo key, la misma escala (×1, la del idle), la misma nitidez y el mismo pivot que el resto del atlas. Tres
cuadros iguales a 24 fps, H.264 sin pérdida (yuv444p, BT.709 con tag).

Uso (desde la raíz del repo, antes de `spritepipe run characters/lowpoly/character.toml`):

    uv run --project pipeline python characters/lowpoly/bolita_clip.py
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from spritepipe import imgio

ROOT = Path(__file__).resolve().parent
POSE = ROOT / "poses" / "bolita.png"
OUT = ROOT / "clips" / "bolita" / "bolita.mp4"
BG = (0xC2, 0x2F, 0x7E)       # el fondo del clip del doble salto (key medido)
EARMUFF_VIDEO_PX = 59.5       # diámetro del auricular en el video (nativos 20 y 21: 60 × 58 y 59 × 55 px)
SIZE = (1280, 720)
CENTER = (640, 360)


def earmuff_px(rgba: np.ndarray) -> float:
    """El diámetro del auricular: la mancha roja más redonda (área contra el círculo de su caja, por lo cuadrada)."""
    c = rgba.astype(int)
    red = (c[..., 0] > 140) & (c[..., 1] < 100) & (c[..., 2] < 100) & (c[..., 0] - c[..., 1] > 80) & (c[..., 3] > 200)
    n, _, st, _ = cv2.connectedComponentsWithStats(red.astype(np.uint8), 8)
    best = max((st[i] for i in range(1, n) if st[i][4] > 200),
               key=lambda s: s[4] / (np.pi * (max(s[2], s[3]) / 2) ** 2) * min(s[2], s[3]) / max(s[2], s[3]))
    return (best[2] + best[3]) / 2


def main() -> None:
    im = np.array(Image.open(POSE).convert("RGBA"))
    k = EARMUFF_VIDEO_PX / earmuff_px(im)
    a = im[..., 3:4].astype(np.float32) / 255.0
    pre = np.dstack([im[..., :3].astype(np.float32) * a, a[..., 0] * 255.0])   # premultiplicado: el borde no arrastra color
    w, h = round(im.shape[1] * k), round(im.shape[0] * k)
    small = np.dstack([np.array(Image.fromarray(pre[..., i], "F").resize((w, h), Image.LANCZOS)) for i in range(4)])
    small = np.clip(small, 0, 255)
    frame = np.zeros((SIZE[1], SIZE[0], 3), np.float32)
    frame[:] = BG
    x0, y0 = CENTER[0] - w // 2, CENTER[1] - h // 2
    sa = small[..., 3:4] / 255.0
    frame[y0:y0 + h, x0:x0 + w] = small[..., :3] + (1 - sa) * frame[y0:y0 + h, x0:x0 + w]
    frame = np.clip(frame + 0.5, 0, 255).astype(np.uint8)
    imgio.encode_rgb_video([frame] * 3, OUT, 24, crf=0, pix_fmt="yuv444p")
    print(f"✓ {OUT}: bolita a ×{k:.4f} ({w} × {h} px de video, auricular {EARMUFF_VIDEO_PX} px)")


if __name__ == "__main__":
    main()
