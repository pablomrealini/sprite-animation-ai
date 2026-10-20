"""Las revisiones de los efectos de salto, a tamaño de juego y con el personaje low-poly parado (o en el aire, en el doble
salto): cada cuadro con su capa de atrás, el personaje y su capa de adelante.

Desde la raíz del repo:
  uv run --project pipeline python backgrounds/lowpoly_saltos/revision.py hojas   # las dos hojas de cada efecto
  uv run --project pipeline python backgrounds/lowpoly_saltos/revision.py         # la elegida contra el concepto y hoy

En la de la Refinería, el polvo va teñido como lo tiñe el juego (dustImg: la luma del dibujo, sobre la de referencia,
por el color de lo que se pisa); el de hoy, con su referencia (116), y el nuevo, con la mediana del suyo.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import entrega  # noqa: E402
import revision_concepto as rc  # noqa: E402
from capas import split_layers  # noqa: E402

F = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 14)
FONDO = Image.open(ROOT / "backgrounds/lowpoly_fondos/entrega/abierta_3.webp").convert("RGBA")
GREEN = (0, 177, 64)


def piso():
    """el color de lo que se pisa en la Refinería: la cara de arriba, 5 a 10 px bajo la línea de los pies"""
    a = np.array(FONDO)[1264 + 5:1264 + 10, 300:2200, :3].reshape(-1, 3).astype(np.float32)
    return np.median(a, 0)


PISO = piso()


def tint(f, ref):
    """como dustImg: la luma sobre `ref`, a la 0,85, por el color del piso"""
    a = f.astype(np.float32)
    L = np.power((a[..., :3] @ np.array([0.299, 0.587, 0.114], np.float32)) / ref, 0.85)
    a[..., :3] = np.minimum(255, PISO[None, None, :] * L[..., None])
    return a.astype(np.uint8)


def game(frs, k_extra=1.0):
    """los cuadros de entrega.scaled (al doble) a px del juego"""
    out = []
    for f, ax, ay in frs:
        w, h = max(1, round(f.shape[1] / 2 * k_extra)), max(1, round(f.shape[0] / 2 * k_extra))
        out.append((entrega.premul_resize(f, w, h), ax / 2 * k_extra, ay / 2 * k_extra))
    return out


def scene(frs, bg, air=0, cell=None, floor_y=None, split=True):
    ch, px, py = rc.char("idle_combat")
    cell = cell or max(300, max(f.shape[1] for f, _, _ in frs) + 40)
    floor_y = floor_y or (150 + air)
    W, H = cell * len(frs), floor_y + 26
    c = FONDO.crop((600, 1264 - floor_y, 600 + W, 1264 - floor_y + H)).copy() if bg == "fondo" else Image.new("RGBA", (W, H), bg + (255,))
    for i, (f, ax, ay) in enumerate(frs):
        cx, fy = i * cell + cell // 2, floor_y - air
        back, front = split_layers(f, ax, ay) if split else (f, np.zeros_like(f))
        pos = (int(round(cx - ax)), int(round(fy - ay)))
        c.alpha_composite(Image.fromarray(back), pos)
        c.alpha_composite(ch, (cx - px, fy - py))
        c.alpha_composite(Image.fromarray(front), pos)
    return c.convert("RGB")


def save(rows, path, zoom=2):
    W = max(r.width for _, r in rows) * zoom
    out = Image.new("RGB", (W, sum(r.height * zoom + 24 for _, r in rows)), (255, 255, 255))
    d, y = ImageDraw.Draw(out), 0
    for lab, r in rows:
        d.text((8, y + 4), lab, fill=(0, 0, 0), font=F)
        out.paste(r.resize((r.width * zoom, r.height * zoom), Image.NEAREST), (0, y + 24)); y += r.height * zoom + 24
    out.save(path, quality=86)
    print("→", path, out.size)


def dims(frs):
    return ", ".join(f"{f.shape[1]}×{f.shape[0]}" for f, _, _ in frs)


def hojas():
    rows = []
    for asset, groups in entrega.FILAS.items():
        for n in (1, 2):
            fr, _ = entrega.scaled(asset, n)
            for names in groups:
                frs = game([fr[c] for c in names])
                air = 90 if asset == "doble" else 0
                rows.append((f"{asset} hoja {n} · {', '.join(names)} · {dims(frs)} px del juego", scene(frs, GREEN, air=air)))
    save(rows, HERE / "revision_hojas.jpg")


def viejo(kind):
    """el polvo de hoy (backgrounds/lowpoly_dust, hoja 1), al tamaño de DUST_ART y con el ancla en el centro de abajo"""
    if kind == "hard":
        names, ref, w = ["h1", "h2", "h3", "h4"], "h2", 150
        d = ROOT / "backgrounds/lowpoly_dust/post/hard/gpt-image-2.5-sunburst-fal_1"
    else:
        names = ["t1", "t2", "t3", "t4"] if kind == "takeoff" else ["l1", "l2", "l3", "l4"]
        ref, w = "l2", 77
        d = ROOT / "backgrounds/lowpoly_dust/post/dust/gpt-image-2.5-sunburst-fal_1"
    k = w / Image.open(d / f"{ref}.png").width
    out = []
    for n in names:
        im = np.array(Image.open(d / f"{n}.png").convert("RGBA"))
        ww, hh = max(1, round(im.shape[1] * k)), max(1, round(im.shape[0] * k))
        out.append((entrega.premul_resize(im, ww, hh), ww / 2, hh))
    return out


def concepto(kind):
    land = rc.frames(rc.keyed(HERE / "refs/concepto_aterrizaje.png"), rc.CUADROS["aterrizaje"])
    dbl = rc.frames(rc.keyed(HERE / "refs/concepto_doble.png"), rc.CUADROS["doble"])
    src, width = (dbl, 108) if kind == "doble" else (land, {"despegue": 131, "aterrizaje": 193, "fuerte": 270}[kind])
    k = width / max(f.shape[1] for f in src)
    out = []
    for f in src:
        g = rc.scale(f, k)
        out.append((g, g.shape[1] / 2, g.shape[0] * (0.45 if kind == "doble" else 1.0)))
    return out


def final():
    fr = {}
    for asset in entrega.FILAS:
        s, _ = entrega.scaled(asset)
        fr.update(s)
    new_ref = float(np.median([entrega.stats(fr[c][0])[0] for c in ("l1", "l2", "l3", "h1", "h2", "h3", "h4")]))
    tn = lambda frs, ref: [(tint(f, ref), ax, ay) for f, ax, ay in frs]
    rows = []
    for name, cs, old, kc in (("despegue", ["t1", "t2", "t3"], "takeoff", "despegue"), ("aterrizaje", ["l1", "l2", "l3"], "land", "aterrizaje"),
                              ("aterrizaje fuerte", ["h1", "h2", "h3", "h4"], "hard", "fuerte")):
        new = game([fr[c] for c in cs])
        rows.append((f"{name} · NUEVO · {dims(new)} px del juego · sobre verde, tal cual", scene(new, GREEN)))
        rows.append((f"{name} · NUEVO · sobre la Refinería, teñido como en el juego (luma de referencia {new_ref:.0f})", scene(tn(new, new_ref), "fondo")))
        rows.append((f"{name} · el concepto de Pablo, al mismo ancho (con sus piedritas; en el juego van por código)", scene(concepto(kc), "fondo")))
        rows.append((f"{name} · HOY (backgrounds/lowpoly_dust), teñido como en el juego, todo detrás del personaje", scene(tn(viejo(old), 116), "fondo", split=False)))
    new = game([fr[c] for c in ("d1", "d2", "d3")])
    rows.append((f"doble salto · NUEVO · {dims(new)} px del juego · los pies a 90 del piso", scene(new, GREEN, air=90)))
    rows.append(("doble salto · NUEVO · sobre la Refinería", scene(new, "fondo", air=90)))
    blanco = [(entrega.blanco(f), ax, ay) for f, ax, ay in new]
    rows.append(("doble salto · la versión en blanco (para teñir por equipo, si se elige)", scene(blanco, "fondo", air=90)))
    rows.append(("doble salto · el concepto de Pablo, al mismo ancho (hoy es un anillo de pedazos por código)", scene(concepto("doble"), "fondo", air=90)))
    save(rows, HERE / "revision.jpg")


if __name__ == "__main__":
    hojas() if sys.argv[1:] == ["hojas"] else final()
