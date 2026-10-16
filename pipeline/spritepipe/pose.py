"""Pasos 1 y 2 (antes del video): la pose que se le pasa al modelo como primer frame.

El concept sale de ChatGPT como PNG con transparencia, recortado justo y con una sombra de piso
semitransparente. El modelo de video necesita otra cosa: un cuadro 16:9 de color plano (el mismo
que después se keyea), con aire alrededor para que el personaje no toque el borde cuando se
mueve, y sin sombra, porque el modelo la anima como si fuera parte del personaje.

- El bbox se mide sobre el alfa casi opaco (> 200), así el ruido y la sombra no lo agrandan.
- La sombra es lo semitransparente (< 160) en la franja de los pies; el ruido (< 16) se borra en
  todo el cuadro.
- El personaje ocupa `height` del alto del canvas, centrado, con la línea de pies en `feet`:
  0.72 deja lugar abajo para un run; para un salto, 0.92 deja lugar arriba.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

OPAQUE = 200  # alfa que cuenta como personaje para el bbox
NOISE = 16  # alfa por debajo del cual es ruido, en todo el cuadro
SHADOW = 160  # alfa por debajo del cual es sombra, en la franja de los pies


def parse_rgb(value: str) -> tuple[int, int, int]:
    v = value.lstrip("#")
    if len(v) != 6:
        raise ValueError(f"color inválido {value!r}: usá RRGGBB, por ejemplo FF00FF")
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


def pad(src: Path, dst: Path, size: tuple[int, int] = (1920, 1080), height: float = 0.48,
        feet: float = 0.72, bg: str = "#FF00FF", shadow_from: float = 0.94) -> dict:
    """Pone el personaje de `src` (RGBA) en un canvas de color plano y lo guarda en `dst` (RGB).

    shadow_from: desde qué fracción del bbox, medida desde arriba, se borra la sombra de piso.
    """
    if not 0 < height <= feet <= 1:
        raise ValueError(f"tiene que valer 0 < height ({height}) <= feet ({feet}) <= 1")
    im = Image.open(src)
    if "A" not in im.getbands():
        raise ValueError(f"{src} no tiene transparencia: exportá el concept como PNG con fondo transparente")
    im = im.convert("RGBA")
    alpha = np.array(im.getchannel("A"))

    ys, xs = np.nonzero(alpha > OPAQUE)
    if not len(ys):
        raise ValueError(f"{src} no tiene ningún píxel opaco")
    x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1

    shadow_y = y0 + int((y1 - y0) * shadow_from)
    rows = np.arange(alpha.shape[0])[:, None]
    alpha[(alpha < NOISE) | ((rows >= shadow_y) & (alpha < SHADOW))] = 0
    im.putalpha(Image.fromarray(alpha))

    sprite = im.crop((x0, y0, x1, y1))
    scale = size[1] * height / sprite.height
    sprite = sprite.resize((round(sprite.width * scale), round(sprite.height * scale)), Image.LANCZOS)

    canvas = Image.new("RGBA", size, parse_rgb(bg) + (255,))
    left = (size[0] - sprite.width) // 2
    top = round(size[1] * feet) - sprite.height
    if left < 0:
        raise ValueError(f"el personaje ({sprite.width} px) no entra a lo ancho en {size[0]} px: bajá height")
    canvas.alpha_composite(sprite, (left, top))
    dst.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(dst)
    return {"sprite": list(sprite.size), "at": [left, top], "canvas": list(size)}
