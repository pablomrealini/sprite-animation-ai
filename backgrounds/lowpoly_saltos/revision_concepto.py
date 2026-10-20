"""La propuesta antes de generar: los efectos del concepto de Pablo (conceptos/efectos_salto_pablo.webp, la tira de abajo
de cada lado, sin el personaje) recortados del azul, a los tamaños que se proponen para el juego y en dos capas, con el
personaje low-poly en el medio, sobre verde y sobre la Refinería low-poly. Sirve para ver tamaños y capas; el dibujo
nuevo sale de la generación (gen.toml).

Desde la raíz del repo:
  uv run --project pipeline python backgrounds/lowpoly_saltos/revision_concepto.py
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from capas import split_layers  # noqa: E402

REFS = HERE / "refs"
# los tamaños que se proponen, en px del juego: el ancho del cuadro más ancho de cada efecto (el personaje mide ~105 de
# alto). Salen del concepto: ahí las nubes del aterrizaje miden 1,84 veces el alto del personaje y el anillo del doble
# salto, 0,73 (1,03 cuando se abre)
ANCHO = {"despegue": 120, "aterrizaje": 193, "fuerte": 270, "doble": 108}


def keyed(path):
    """el efecto sin el azul del concepto: el fondo de cada fila es la mediana de sus bordes"""
    a = np.array(Image.open(path).convert("RGB")).astype(np.float32)
    bg = np.median(np.concatenate([a[:, :24], a[:, -24:]], 1), axis=1)[:, None, :]
    d = np.sqrt(((a - bg) ** 2).sum(2))
    al = np.clip((d - 22) / 55, 0, 1)
    fg = (a - bg * (1 - al[..., None])) / np.maximum(al[..., None], 1e-3)
    return np.concatenate([fg.clip(0, 255), (al * 255)[..., None]], 2).astype(np.uint8)


# los cuadros de cada tira del concepto, en x del recorte (el tercero de cada uno viene partido en pedazos sueltos)
CUADROS = {"aterrizaje": [(15, 235), (268, 580), (615, 812)], "doble": [(15, 200), (250, 515), (550, 805)]}


def frames(rgba, cols):
    """los cuadros de una tira, recortados a lo que tienen"""
    out = []
    for x0, x1 in cols:
        f = rgba[:, x0:x1]
        al = f[..., 3] > 40
        ys, xs = np.nonzero(al.any(1))[0], np.nonzero(al.any(0))[0]
        out.append(f[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    return out


def scale(f, k):
    im = Image.fromarray(f)
    return np.array(im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS))


def char(anim, n=0):
    for page in sorted((ROOT / "characters/lowpoly/out").glob("lowpoly_0.5x-*.json")):
        fr = json.loads(page.read_text())["frames"].get(f"{anim}/{n:04d}")
        if fr:
            f = fr["frame"]
            im = Image.open(page.with_suffix(".png")).convert("RGBA").crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))
            im = im.resize((round(im.width * 0.8), round(im.height * 0.8)), Image.LANCZOS)
            px = round((fr["pivot"]["x"] * fr["sourceSize"]["w"] - fr["spriteSourceSize"]["x"]) * 0.8)
            py = round((fr["pivot"]["y"] * fr["sourceSize"]["h"] - fr["spriteSourceSize"]["y"]) * 0.8)
            return im, px, py


def scene(effects, ch, bg, floor_y=150, cell=300, air=0):
    """cada efecto con el personaje: capa de atrás, personaje, capa de adelante; los pies en (centro, floor_y - air)"""
    W, H = cell * len(effects), floor_y + 30
    if bg == "fondo":
        p = Image.open(ROOT / "backgrounds/lowpoly_fondos/entrega/abierta_3.webp").convert("RGBA")
        c = p.crop((700, 1264 - floor_y, 700 + W, 1264 - floor_y + H)).copy()
    else:
        c = Image.new("RGBA", (W, H), bg + (255,))
    im, px, py = ch
    for i, f in enumerate(effects):
        cx, fy = i * cell + cell // 2, floor_y - air
        if f is None:
            c.alpha_composite(im, (cx - px, fy - py)); continue
        ax, ay = f.shape[1] / 2, f.shape[0] - (0 if not air else f.shape[0] * 0.55)
        back, front = split_layers(f, ax, ay)
        pos = (int(round(cx - ax)), int(round(fy - ay)))
        c.alpha_composite(Image.fromarray(back), pos)
        c.alpha_composite(im, (cx - px, fy - py))
        c.alpha_composite(Image.fromarray(front), pos)
    return c.convert("RGB")


def main():
    F = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 14)
    land = frames(keyed(REFS / "concepto_aterrizaje.png"), CUADROS["aterrizaje"])
    dbl = frames(keyed(REFS / "concepto_doble.png"), CUADROS["doble"])
    kl = ANCHO["aterrizaje"] / max(f.shape[1] for f in land)
    kd = ANCHO["doble"] / max(f.shape[1] for f in dbl)
    sets = {
        "despegue (≈ el aterrizaje a 0,62)": [scale(f, kl * ANCHO["despegue"] / ANCHO["aterrizaje"]) for f in land],
        "aterrizaje normal": [scale(f, kl) for f in land],
        "aterrizaje fuerte (≈ el aterrizaje a 1,4)": [scale(f, kl * ANCHO["fuerte"] / ANCHO["aterrizaje"]) for f in land],
    }
    parado = char("idle_combat")
    rows = []
    for name, fs in sets.items():
        for bg in ((0, 177, 64), "fondo"):
            rows.append((f"{name} · {', '.join(f'{f.shape[1]}×{f.shape[0]}' for f in fs)} px del juego · las piedritas del concepto, en el juego van por código", scene(fs, parado, bg)))
    fs = [scale(f, kd) for f in dbl]
    for bg in ((0, 177, 64), "fondo"):
        rows.append((f"doble salto · {', '.join(f'{f.shape[1]}×{f.shape[0]}' for f in fs)} px del juego · los pies a 90 px del piso", scene(fs, parado, bg, floor_y=250, air=90)))
    # cómo se parte un cuadro: rojo = detrás del personaje, azul = delante
    f = sets["aterrizaje fuerte (≈ el aterrizaje a 1,4)"][1]
    back, front = split_layers(f, f.shape[1] / 2, f.shape[0])
    vis = np.zeros_like(f)
    vis[..., 0] = back[..., 3]; vis[..., 2] = front[..., 3]; vis[..., 3] = np.maximum(back[..., 3], front[..., 3])
    v = Image.new("RGBA", (900, f.shape[0] + 40), (255, 255, 255, 255))
    v.alpha_composite(Image.fromarray(vis), (20, 20))
    rows.append(("las dos capas de un cuadro del fuerte: rojo = detrás del personaje (la ventana de 44 px de ancho por encima de "
                 "los 14 px de abajo), azul = delante", v.convert("RGB")))
    Z = 2
    W = max(r.width for _, r in rows) * Z
    out = Image.new("RGB", (W, sum(r.height * Z + 24 for _, r in rows)), (255, 255, 255))
    d, y = ImageDraw.Draw(out), 0
    for lab, r in rows:
        d.text((8, y + 4), lab, fill=(0, 0, 0), font=F)
        out.paste(r.resize((r.width * Z, r.height * Z), Image.NEAREST), (0, y + 24)); y += r.height * Z + 24
    out.save(HERE / "revision_concepto.jpg", quality=86)
    print("→", HERE / "revision_concepto.jpg", out.size)


if __name__ == "__main__":
    main()
