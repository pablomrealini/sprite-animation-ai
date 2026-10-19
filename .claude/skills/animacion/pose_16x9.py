"""Una pose RGBA (de poses_gen) a 16:9 sobre magenta apagado, a la escala de otra pose 16:9 por el ancho del casco.

pad-pose lleva el alto del personaje al 48% del cuadro: sirve para poses paradas, pero una pose baja (deslizándose,
agachado, en bolita) saldría agrandada. Acá la escala sale del casco (la cáscara blanca de perfil, que no cambia con
la pose): el casco queda del mismo ancho que en la pose de referencia, la fila más baja del personaje queda en la
línea de piso de la referencia y el centro de la caja en el centro de la referencia (o en --centro).

Uso (desde la raíz del repo):

    uv run --project pipeline python .claude/skills/animacion/pose_16x9.py characters/lowpoly/poses_gen/post/x/y.png \
        --ref characters/lowpoly/poses/correr_apagada_dullmagenta_16x9.png \
        --out characters/lowpoly/poses/deslizarse_dullmagenta_16x9.png [--centro 960]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

BG = (0xC4, 0x2D, 0x7D)
HELMET_H_OVER_W = 0.9  # de perfil, el casco mide de alto 0,9 de su ancho (como subida_frames.py)


def helmet_width(rgb: np.ndarray, alpha: np.ndarray) -> int:
    """Ancho de la cáscara del casco: las partes blancas grandes juntas; vale el mayor entre el ancho y alto / 0,9."""
    c = rgb.astype(int)
    white = ((alpha > 200) & (c.min(-1) > 170) & ((c.max(-1) - c.min(-1)) < 35)).astype(np.uint8)
    white = cv2.morphologyEx(white, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, _, st, _ = cv2.connectedComponentsWithStats(white)
    big = st[1:, cv2.CC_STAT_AREA].max()
    parts = [st[i] for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= 0.15 * big]
    x0 = min(p[0] for p in parts)
    x1 = max(p[0] + p[2] for p in parts)
    y0 = min(p[1] for p in parts)
    y1 = max(p[1] + p[3] for p in parts)
    return int(max(x1 - x0, (y1 - y0) / HELMET_H_OVER_W))


def fondo_alpha(rgb: np.ndarray) -> np.ndarray:
    """Alfa de una pose 16:9 sobre magenta apagado (lo que no es fondo)."""
    return ((np.abs(rgb.astype(int) - np.array(BG)).sum(-1) > 40) * 255).astype(np.uint8)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pose", type=Path, help="pose con alfa (poses_gen/post/...)")
    ap.add_argument("--ref", type=Path, required=True, help="pose 16:9 de la que se copian casco, piso y centro")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--centro", type=float, help="x del centro de la caja; por defecto, el de la referencia")
    args = ap.parse_args()

    ref = np.array(Image.open(args.ref).convert("RGB"))
    ref_a = fondo_alpha(ref)
    ys, xs = np.nonzero(ref_a)
    floor, cx = int(ys.max()), args.centro if args.centro is not None else (xs.min() + xs.max()) / 2
    want = helmet_width(ref, ref_a)

    im = Image.open(args.pose).convert("RGBA")
    a = np.array(im)
    a[..., 3][a[..., 3] < 8] = 0
    have = helmet_width(a[..., :3], a[..., 3])
    s = want / have
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    al = np.array(im)[..., 3]
    ys, xs = np.nonzero(al > 128)
    left = round(cx - (xs.min() + xs.max()) / 2)
    top = floor - int(ys.max())
    canvas = Image.new("RGBA", ref.shape[1::-1], BG + (255,))
    canvas.alpha_composite(im, (left, top))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(args.out)
    out = np.array(canvas.convert("RGB"))
    oys, oxs = np.nonzero(fondo_alpha(out))
    print(f"✓ {args.out}: escala {s:.3f} (casco {have} → {want} px), caja x {oxs.min()}-{oxs.max()}, "
          f"y {oys.min()}-{oys.max()} (alto {oys.max() - oys.min()}), piso {floor}, centro {cx:.0f}")


if __name__ == "__main__":
    main()
