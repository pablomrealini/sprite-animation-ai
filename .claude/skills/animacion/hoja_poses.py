"""Hoja para comparar proporciones: poses de poses_gen al lado de una pose de referencia, a la misma escala de casco.

Cada pose se escala para que el casco (la cáscara blanca de perfil) mida lo mismo que en la referencia, todas apoyadas
en la misma línea de piso, sobre verde, con una regla de cascos de fondo (una raya cada medio casco) y abajo el
largo y el alto de cada una en cascos. Así se ve enseguida si una pose agrandó las piernas o los brazos.

Uso (desde la raíz del repo):

    uv run --project pipeline python .claude/skills/animacion/hoja_poses.py characters/lowpoly/poses_gen/post/x/*.png \
        --ref characters/lowpoly/poses/perfil_apagada_concept.png --out characters/lowpoly/revision/para_pablo/x.png
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from hoja_toma import font
from pose_16x9 import helmet_width

GREEN = (0, 255, 0)
CASCO = 160  # px del casco en la hoja


def cargar(path: Path) -> tuple[Image.Image, int]:
    im = Image.open(path).convert("RGBA")
    a = np.array(im)
    a[..., 3][a[..., 3] < 8] = 0
    im = Image.fromarray(a)
    im = im.crop(im.getbbox())
    return im, helmet_width(np.array(im)[..., :3], np.array(im)[..., 3])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("poses", type=Path, nargs="+")
    ap.add_argument("--ref", type=Path, required=True, help="pose de referencia con alfa (la de perfil)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--pierna", type=float, help="marca de este largo (en cascos) que termina en la suela de adelante "
                    "de cada pose: la pierna estirada con las proporciones de la referencia")
    ap.add_argument("--leyenda", default="", help="qué es la marca, para el encabezado")
    ap.add_argument("--notas", nargs="*", default=[], help="una línea más debajo de cada pose (en orden, sin la ref.)")
    args = ap.parse_args()

    items = []
    for p in [args.ref, *args.poses]:
        im, casco = cargar(p)
        s = CASCO / casco
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        nombre = p.stem if p != args.ref else "referencia: " + p.stem.removesuffix("_concept")
        if p.parent.name and p != args.ref:
            nombre = f"{p.parent.name}/{p.stem}"
        items.append((nombre, im))

    pad, head, foot = 40, 40, 78
    f = font(16)
    titulo = (f"casco = {CASCO} px en todas · rayas cada 1/2 casco desde el piso"
              + (f" · en magenta, {args.pierna} casco: {args.leyenda}" if args.pierna else ""))
    medir = ImageDraw.Draw(Image.new("RGB", (1, 1)))

    def lugar(k: int, nombre: str, im: Image.Image) -> int:
        """Ancho del lugar de cada pose: la pose o su texto, lo que sea más ancho."""
        textos = [nombre, "0.00 × 0.00 cascos (largo × alto)"]
        if k and k - 1 < len(args.notas):
            textos.append(args.notas[k - 1])
        return max(im.width, *(round(medir.textlength(t, font=f)) for t in textos))

    anchos = [lugar(k, n, im) for k, (n, im) in enumerate(items)]
    alto = max(im.height for _, im in items)
    ancho = max(sum(anchos) + pad * (len(items) + 1), round(medir.textlength(titulo, font=font(18))) + 16)
    piso = head + alto + 20
    hoja = Image.new("RGB", (ancho, piso + foot), GREEN)
    d = ImageDraw.Draw(hoja)
    for k in range(0, int(alto / (CASCO / 2)) + 2):  # regla: una raya cada medio casco, desde el piso
        y = piso - k * CASCO // 2
        d.line([(0, y), (ancho, y)], fill=(0, 200, 0) if k % 2 else (0, 150, 0), width=1)
    d.rectangle([0, 0, ancho, head - 6], fill=(30, 30, 30))
    d.text((8, 8), titulo, fill=(230, 230, 230), font=font(18))
    d.rectangle([0, piso, ancho, piso + foot], fill=(30, 30, 30))
    x = pad
    for k, (nombre, im) in enumerate(items):
        hoja.paste(im, (x, piso - im.height), im)
        d.text((x, piso + 8), nombre, fill=(255, 255, 255), font=f)
        d.text((x, piso + 32), f"{im.width / CASCO:.2f} × {im.height / CASCO:.2f} cascos (largo × alto)",
               fill=(200, 200, 200), font=f)
        if k and k - 1 < len(args.notas):
            d.text((x, piso + 52), args.notas[k - 1], fill=(255, 220, 120), font=f)
        if args.pierna:
            L = round(args.pierna * CASCO)
            if k:  # en el piso, terminando en la suela de adelante
                a = np.array(im)[..., 3]
                cols = np.nonzero(a[-max(1, im.height // 3):].max(0) > 128)[0]
                x1 = x + int(cols.max())
                d.line([(x1 - L, piso - 3), (x1, piso - 3)], fill=(255, 0, 255), width=5)
                d.line([(x1 - L, piso - 14), (x1 - L, piso + 6)], fill=(255, 0, 255), width=4)
        x += anchos[k] + pad
    args.out.parent.mkdir(parents=True, exist_ok=True)
    hoja.save(args.out)
    print(f"✓ {args.out}")
    for nombre, im in items:
        print(f"  {nombre}: {im.width / CASCO:.2f} × {im.height / CASCO:.2f} cascos")


if __name__ == "__main__":
    main()
