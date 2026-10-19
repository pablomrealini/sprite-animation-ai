"""Hoja de revisión de dibujos de gen-images a tamaño de juego: cada fila sobre verde, sobre oscuro y sobre la Refinería
low-poly, ampliada x2 sin suavizar para ver los px del juego. Además imprime por pieza el tamaño, la saturación (para el
gris neutro) y el alfa del centro (para lo semitransparente).

Desde la raíz del repo:
  uv run --project pipeline python .claude/skills/arte/hoja_juego.py salida.png \
      --fila "escudos · 46 px de alto" alto=46 a.png b.png \
      --fila "polvo · 80 px el más ancho" ancho_max=80 base t1.png t2.png t3.png \
      --fila "burbuja · 130 px" alto=130 base personaje dome.png

Medidas (px del juego; el archivo exportado va al doble):
  alto=N / ancho=N          cada pieza a esa medida, por separado (power-ups: todos a la misma altura)
  alto_max=N / ancho_max=N  la más grande de la fila a esa medida y las demás a la misma escala (cuadros de una animación)
Opciones de fila: base (apoyadas abajo, como el polvo en el piso), personaje (el low-poly en idle_combat detrás, a
escala de juego, centrado y con los pies abajo), tinte=#rrggbb (multiplica el gris por ese color en la fila de la
Refinería).
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path.cwd()
GREEN, DARK = (0, 177, 64), (27, 31, 42)
ZOOM, PAD = 2, 12
PLATE = ROOT / "prototypes/arena/arenas/refineria_lowpoly/fondo.webp"   # 1920 × 1080 px del juego, el piso en y 940
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"


def font():
    try:
        return ImageFont.truetype(FONT_PATH, 13)
    except OSError:
        return ImageFont.load_default()


def character():
    """el low-poly en idle_combat/0000 a escala de juego: atlas 0,5x × S.char (0,8)"""
    for page in sorted((ROOT / "characters/lowpoly/out").glob("lowpoly_0.5x-*.json")):
        fr = json.loads(page.read_text())["frames"].get("idle_combat/0000")
        if fr:
            f = fr["frame"]
            im = Image.open(page.with_suffix(".png")).convert("RGBA").crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))
            return im.resize((round(im.width * 0.8), round(im.height * 0.8)), Image.LANCZOS)
    return None


def plate(w, h):
    p = Image.open(PLATE).convert("RGBA")
    p = p.resize((round(p.width * 1080 / p.height), 1080), Image.LANCZOS)
    return p.crop((260, 940 - h + 8, 260 + w, 948))


def tint(im, rgb):
    a = np.array(im).astype(np.float32)
    a[..., :3] *= np.array(rgb, np.float32) / 255
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def stats(path, im):
    a = np.array(im).astype(np.float32)
    on = a[..., 3] >= 128
    rgb = a[..., :3][on]
    h, w = a.shape[:2]
    sat = float((rgb.max(1) - rgb.min(1)).mean()) if len(rgb) else 0.0
    centro = float(a[h // 3: 2 * h // 3, w // 3: 2 * w // 3, 3].mean())
    print(f"{path}: {w}×{h} px, saturación {sat:.1f}, luma {float(rgb.mean()) if len(rgb) else 0:.0f}, "
          f"alfa del centro {centro:.0f}/255, opaco {on.mean():.0%}")


def parse(argv):
    out, rows, row = Path(argv[0]), [], None
    for a in argv[1:]:
        if a == "--fila":
            row = {"label": None, "paths": [], "base": False, "char": False, "tint": None}
            rows.append(row)
        elif row is not None and row["label"] is None:
            row["label"] = a
        elif "=" in a and a.split("=")[0] in ("alto", "ancho", "alto_max", "ancho_max"):
            row["size"] = (a.split("=")[0], float(a.split("=")[1]))
        elif a.startswith("tinte="):
            c = a.split("=")[1].lstrip("#")
            row["tint"] = tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
        elif a == "base":
            row["base"] = True
        elif a == "personaje":
            row["char"] = True
        else:
            row["paths"].append(Path(a))
    return out, rows


def scaled(row):
    ims = [Image.open(p).convert("RGBA") for p in row["paths"]]
    for p, im in zip(row["paths"], ims):
        stats(p, im)
    kind, n = row.get("size", ("alto", 46))
    axis = 1 if kind.startswith("alto") else 0
    if kind.endswith("_max"):
        k = n / max(im.size[axis] for im in ims)
        ks = [k] * len(ims)
    else:
        ks = [n / im.size[axis] for im in ims]
    return [im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS) for im, k in zip(ims, ks)]


def strip(ims, bg, row, ch):
    h = max(i.height for i in ims) + 2 * PAD
    w = sum(i.width for i in ims) + PAD * (len(ims) + 1)
    canvas = plate(w, h) if bg == "plate" else Image.new("RGBA", (w, h), bg + (255,))
    x = PAD
    for i in ims:
        y = h - PAD - i.height if row["base"] else (h - i.height) // 2
        if ch is not None:
            canvas.alpha_composite(ch, (x + (i.width - ch.width) // 2, min(h - ch.height, y + i.height - ch.height - 10)))
        canvas.alpha_composite(tint(i, row["tint"]) if (bg == "plate" and row["tint"]) else i, (x, y))
        x += i.width + PAD
    return canvas


def main():
    out, rows = parse(sys.argv[1:])
    ch = character()
    f, lab = font(), 18
    strips = []
    for row in rows:
        ims = scaled(row)
        for bg in (GREEN, DARK, "plate"):
            strips.append((row["label"], strip(ims, bg, row, ch if row["char"] else None)))
    W = max(s.width for _, s in strips) * ZOOM
    sheet = Image.new("RGB", (W, sum(s.height * ZOOM + lab for _, s in strips)), (255, 255, 255))
    d, y = ImageDraw.Draw(sheet), 0
    for label, s in strips:
        d.text((4, y + 2), label, fill=(0, 0, 0), font=f)
        sheet.paste(s.convert("RGB").resize((s.width * ZOOM, s.height * ZOOM), Image.NEAREST), (0, y + lab))
        y += s.height * ZOOM + lab
    sheet.save(out, optimize=True)
    print(f"→ {out} ({sheet.width}×{sheet.height})")


main()
