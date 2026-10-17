"""Pinta de rojo el cinturón de una pose de costado (concept RGBA), sin tocar nada más ni cambiar el tamaño.

La hoja de vistas buena (refs/vistas_tpose_cinturon_rojo_alfa.png) tiene el cinturón rojo; las poses de costado
(recortadas de refs/costado_con_arma.png) lo tienen gris oscuro, como el traje. El cinturón es una banda entre una
línea de arriba y una de abajo (polilíneas en px del concept, medidas a ojo con zoom); dentro de la banda se pintan
sólo los píxeles opacos grises (no la manga ni el guante, que son rojos).

El color nuevo es un cambio de albedo en luz lineal: cada píxel conserva su sombreado (su luminancia relativa a la del
gris del traje más iluminado de la pose) y toma el rojo iluminado del cinturón de la hoja.

Uso (desde la raíz del repo):

    uv run --project pipeline python characters/lowpoly/cinturon_rojo.py perfil
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).parent
RED_LIT = np.array([250, 40, 36], np.float64)  # rojo iluminado del cinturón en la hoja (p75 de su luminancia)
GAIN = 1.0  # sombreado extra, si el rojo queda muy oscuro al lado de la manga

# banda del cinturón por pose: polilínea de arriba y de abajo (x, y) en px del concept
BANDS = {
    "perfil": {
        "top": [(96, 666), (150, 664), (160, 672), (190, 682), (205, 686), (330, 686)],
        "bottom": [(96, 722), (220, 723), (330, 723)],
    },
    "tq": {  # arriba lo tapan la manga y el puño (rojos, quedan afuera); abajo, la costura que baja a la derecha
        "top": [(266, 668), (300, 668), (570, 668)],
        "bottom": [(266, 720), (310, 716), (350, 718), (400, 722), (450, 725), (500, 722), (570, 722)],
    },
}


def srgb_to_lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c):
    c = np.clip(c, 0, 1)
    return 255.0 * np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def band_mask(shape, band) -> np.ndarray:
    poly = band["top"] + band["bottom"][::-1]
    m = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(m).polygon(poly, fill=255)
    return np.array(m) > 0


def paint(name: str) -> Path:
    src = ROOT / "poses" / f"{name}_concept.png"
    im = np.array(Image.open(src)).astype(np.float64)
    rgb, a = im[..., :3], im[..., 3]
    sat = rgb.max(-1) - rgb.min(-1)
    lin = srgb_to_lin(rgb)
    y_lum = lin @ np.array([0.2126, 0.7152, 0.0722])
    suit = (a > 200) & (sat < 40) & (rgb.mean(-1) < 140)  # gris del traje (sin el casco blanco)
    lit = np.percentile(y_lum[suit], 99)
    belt = band_mask(a.shape, BANDS[name]) & (a > 8) & (sat < 50)
    shade = np.clip(y_lum / lit * GAIN, 0, 1.2)[..., None]
    red = lin_to_srgb(srgb_to_lin(RED_LIT) * shade)
    out = im.copy()
    out[..., :3] = np.where(belt[..., None], red, rgb)
    dst = ROOT / "poses" / f"{name}_cinturon_rojo_concept.png"
    Image.fromarray(out.round().astype(np.uint8), "RGBA").save(dst)
    print(f"✓ {dst}: {int(belt.sum())} px pintados (gris iluminado del traje: lum lineal {lit:.3f})")
    return dst


if __name__ == "__main__":
    for n in sys.argv[1:] or list(BANDS):
        paint(n)
