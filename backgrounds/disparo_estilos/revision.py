"""La revisión de las direcciones del fogonazo: cada hoja generada, cortada en sus cuadros, puesta en la boca del arma a
tamaño de juego y sumada (lighter) sobre la Refinería low-poly, al lado del fogonazo de hoy. Abajo de cada una, el
impacto en el mismo estilo.

Desde la raíz del repo:
  uv run --project pipeline python backgrounds/disparo_estilos/revision.py

- Cuadros: la hoja es negra; lo que tiene luz (el canal más alto > 12) se corta en 2 filas y cada fila en 4 cuadros,
  por los 3 huecos de columnas vacías más anchos.
- Fogonazo: el cuadro arranca en la boca (su borde izquierdo, a la altura del medio de la fila). El pico (cuadro 2)
  mide 62 px del juego de largo, lo mismo que hoy (FX.muzzle.len 26 × FXK 1,5 × 1,6).
- Impacto: centrado en el punto del golpe; el cuadro 2 mide 60 px del juego.
- La boca: shoot/0000 del low-poly, a (+58, -58) de los pies (characters/lowpoly/out/fx/shoot_muzzle.json, 0,5x × 0,8).
- d_3d está en blanco: se muestra teñido con dos colores de equipo (multiplicado, con el centro blanco).
- Mezclas: "suma" (lighter, como hoy), "normal" (alfa = el canal más alto, color des-multiplicado: fondo × (1 - alfa) +
  luz) y "normal + núcleo" (la normal más la mitad de la luz sumada donde es más blanca). Screen se probó: sobre claro
  quema casi como la suma, así que no está.
- Arenas: la Refinería low-poly (clara) y Low-poly · Duelo (de noche): el mismo fondo con el color de
  arenas/lowpoly_duelo.json (la paleta de Pablo al 0,3, saturación, contraste, brillo y bruma, como color.js).
- Salen dos hojas: revision.jpg, el detalle de todas las hojas, y revision_corta.jpg, el pico de cada estilo en sus dos
  mezclas sobre claro y sobre oscuro, al lado del de hoy.
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FONDO = Image.open(ROOT / "backgrounds/lowpoly_fondos/entrega/abierta_3.webp").convert("RGB")
ASSETS = ["a_fuego", "b_plasma", "c_pintado", "d_3d"]
LARGO, IMPACTO = 62, 60
EQUIPOS = {"rojo": (255, 70, 60), "azul": (70, 140, 255)}


def char(anim="shoot", n=0):
    for page in sorted((ROOT / "characters/lowpoly/out").glob("lowpoly_0.5x-*.json")):
        fr = json.loads(page.read_text())["frames"].get(f"{anim}/{n:04d}")
        if fr:
            f = fr["frame"]
            im = Image.open(page.with_suffix(".png")).convert("RGBA").crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))
            im = im.resize((round(im.width * 0.8), round(im.height * 0.8)), Image.LANCZOS)
            px = round((fr["pivot"]["x"] * fr["sourceSize"]["w"] - fr["spriteSourceSize"]["x"]) * 0.8)
            py = round((fr["pivot"]["y"] * fr["sourceSize"]["h"] - fr["spriteSourceSize"]["y"]) * 0.8)
            return im, px, py


def muzzle():
    d = json.loads((ROOT / "characters/lowpoly/out/fx/shoot_muzzle.json").read_text())["variants"]["0.5x"]["frames"][0]
    return d["dx"] * 0.8, d["dy"] * 0.8


def bands(lit, pad=30):
    rows = lit.any(1)
    ys = np.nonzero(rows)[0]
    out, y = [], ys.min()
    while y <= ys.max():
        if rows[y]:
            y0 = y
            while y <= ys.max() and rows[y:y + pad].any():
                y += 1
            out.append((y0, y))
        y += 1
    return out


def cut(lit, n):
    occ = lit.any(0)
    xs = np.nonzero(occ)[0]
    runs, x = [], xs.min()
    while x < xs.max():
        if not occ[x]:
            x0 = x
            while not occ[x]:
                x += 1
            runs.append((x - x0, x0, x))
        x += 1
    cuts = sorted(r[1:] for r in sorted(runs, reverse=True)[:n - 1])
    edges = [xs.min()] + [c for r in cuts for c in r] + [xs.max() + 1]
    return [(edges[2 * i], edges[2 * i + 1]) for i in range(n)]


def frames(path):
    """{"flash": [4 × (rgb, ax, ay)], "impact": [...]}: el ancla es la boca (fogonazo) o el centro (impacto)"""
    a = np.array(Image.open(path).convert("RGB")).astype(np.float32)
    lit = a.max(2) > 12
    bs = bands(lit)
    if len(bs) < 2:
        return None
    bs = sorted(bs, key=lambda b: -(b[1] - b[0]))[:2]
    bs.sort()
    out = {}
    for kind, (y0, y1) in zip(("flash", "impact"), bs):
        cols = cut(lit[y0:y1], 4)
        cy = (y0 + y1) / 2
        fr = []
        for x0, x1 in cols:
            sub = lit[y0:y1, x0:x1]
            ys, xs = np.nonzero(sub.any(1))[0], np.nonzero(sub.any(0))[0]
            bx0, by0, bx1, by1 = x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1
            f = a[by0:by1, bx0:bx1]
            ax = 0 if kind == "flash" else (bx1 - bx0) / 2
            fr.append((f, ax, cy - by0 if kind == "flash" else (by1 - by0) / 2))
        out[kind] = fr
    return out


def scale(fr, width):
    k = width / fr[1][0].shape[1]
    out = []
    for f, ax, ay in fr:
        im = Image.fromarray(f.clip(0, 255).astype(np.uint8)).resize((max(1, round(f.shape[1] * k)), max(1, round(f.shape[0] * k))), Image.LANCZOS)
        out.append((np.array(im).astype(np.float32), ax * k, ay * k))
    return out


def tint(f, rgb):
    """luz blanca teñida: el color del equipo por la luma, y sólo lo más fuerte (el núcleo) vuelve al blanco"""
    lum = f.mean(2, keepdims=True) / 255
    col = np.array(rgb, np.float32)[None, None, :]
    return (lum * col + np.clip((lum - 0.88) / 0.12, 0, 1) * (255 - col) * lum).clip(0, 255)


def hue(f, deg):
    """el plasma con otro tono (rota el matiz y deja la luz): para teñirlo por equipo"""
    im = Image.fromarray(f.clip(0, 255).astype(np.uint8)).convert("HSV")
    a = np.array(im).astype(np.int32)
    a[..., 0] = (a[..., 0] + int(deg / 360 * 255)) % 256
    return np.array(Image.fromarray(a.astype(np.uint8), "HSV").convert("RGB")).astype(np.float32)


def today():
    """el fogonazo de hoy: m1–m3 de lowpoly_fx (rojo, sin teñir) con el halo radial sumado, como drawFlash"""
    d = ROOT / "backgrounds/lowpoly_fx/post/muzzle/gpt-image-2.5-sunburst-fal_2"
    ims = [Image.open(d / f"m{i}.png").convert("RGBA") for i in (1, 2, 3)]
    k = LARGO / ims[0].width
    out = []
    for i, im in enumerate(ims):
        w, h = max(1, round(im.width * k)), max(1, round(im.height * k))
        out.append((im.resize((w, h), Image.LANCZOS), 0, h / 2))
    return out



def noche(im):
    """el fondo con el color de Low-poly · Duelo (color.js en Python): fondo arriba del piso y plataformas abajo"""
    spec = importlib.util.spec_from_file_location("paleta", ROOT / "prototypes/arena/paleta.py")
    pal = importlib.util.module_from_spec(spec); spec.loader.exec_module(pal)
    lut = pal.fit_lut(ROOT / "prototypes/arena/refs/refineria.webp", ROOT / "prototypes/arena/refs/refineria_paleta_pablo.webp")
    col = json.loads((ROOT / "prototypes/arena/arenas/lowpoly_duelo.json").read_text())["color"]
    h = col["bruma_color"].lstrip("#")
    haze = np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)

    def grade(g):
        a = np.array(pal.apply_lut(im, lut, g["paleta"]).convert("RGB")).astype(np.float32)
        l = a @ np.array([0.299, 0.587, 0.114], np.float32)
        a = l[..., None] + (a - l[..., None]) * g["saturacion"]
        a = (a - 128) * g["contraste"] + 128
        a *= g["brillo"]
        return (a + (haze - a) * g["bruma"]).clip(0, 255)

    out = grade(col["fondo"])
    out[1264:] = grade(col["plataformas"])[1264:]
    return Image.fromarray(out.astype(np.uint8))


FONDOS = {"claro": FONDO, "oscuro": noche(FONDO)}
MEZCLAS = ["suma", "normal", "normal + núcleo"]


def blend(bg, f, mode):
    if mode == "suma":
        return bg + f
    a = f.max(2, keepdims=True) / 255
    out = bg * (1 - a) + f
    if mode == "normal + núcleo":
        core = np.clip((f.mean(2, keepdims=True) / 255 - 0.55) / 0.45, 0, 1)
        out = out + 0.5 * f * core
    return out


def put(acc, f, ox, oy, mode):
    H, W = acc.shape[:2]
    h, w = f.shape[:2]
    x0, y0, x1, y1 = max(0, ox), max(0, oy), min(W, ox + w), min(H, oy + h)
    if x1 > x0 and y1 > y0:
        acc[y0:y1, x0:x1] = blend(acc[y0:y1, x0:x1], f[y0 - oy:y1 - oy, x0 - ox:x1 - ox], mode)


def scene(items, mode, back="claro", cell=170, H=150):
    """el personaje tirando y cada cuadro en la boca del arma; mode es una de MEZCLAS, o "hoy" (la estrella normal
    sobre el halo sumado, como drawFlash)"""
    ch, px, py = char()
    mx, my = muzzle()
    W = cell * len(items)
    base = FONDOS[back].crop((700, 1264 - H + 20, 700 + W, 1264 + 20)).convert("RGBA")
    for i in range(len(items)):
        base.alpha_composite(ch, (i * cell + 40 - px, H - 20 - py))
    acc = np.array(base.convert("RGB")).astype(np.float32)
    for i, (f, ax, ay) in enumerate(items):
        fx, fy = i * cell + 40, H - 20
        ox, oy = int(round(fx + mx - ax)), int(round(fy + my - ay))
        if mode == "hoy":
            r = LARGO * 0.6
            yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
            d = np.sqrt(((xx - (fx + mx + r * 0.45)) / r) ** 2 + ((yy - (fy + my)) / (r * 0.65)) ** 2)
            acc += (np.clip(1 - d, 0, 1) ** 1.5 * 0.6 * (1 - i / 3))[..., None] * np.array([255, 120, 110], np.float32)
            im = Image.fromarray(acc.clip(0, 255).astype(np.uint8)).convert("RGBA")
            im.alpha_composite(f, (ox, oy))
            acc = np.array(im.convert("RGB")).astype(np.float32)
        else:
            put(acc, f, ox, oy, mode)
    return Image.fromarray(acc.clip(0, 255).astype(np.uint8))


def impact_scene(items, mode, back="claro", cell=170, H=150):
    W = cell * len(items)
    acc = np.array(FONDOS[back].crop((1400, 1264 - H + 20, 1400 + W, 1264 + 20)).convert("RGB")).astype(np.float32)
    for i, (f, ax, ay) in enumerate(items):
        put(acc, f, int(round(i * cell + cell / 2 - ax)), int(round(H / 2 - ay)), mode)
    return Image.fromarray(acc.clip(0, 255).astype(np.uint8))


def save(rows, path, Z=2):
    F = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 14)
    W = max(r.width for _, r in rows) * Z
    out = Image.new("RGB", (W, sum(r.height * Z + 24 for _, r in rows)), (255, 255, 255))
    d, y = ImageDraw.Draw(out), 0
    for lab, r in rows:
        d.text((8, y + 4), lab, fill=(0, 0, 0), font=F)
        out.paste(r.resize((r.width * Z, r.height * Z), Image.NEAREST), (0, y + 24)); y += r.height * Z + 24
    out.save(path, quality=86)
    print("→", path, out.size, f"({len(rows)} filas)")


def estilos():
    """(nombre, hoja, fogonazo, impacto) de cada hoja generada, ya a tamaño de juego; d_3d teñido de rojo y de azul"""
    out = []
    for asset in ASSETS:
        for n in (1, 2):
            p = HERE / "post" / asset / f"gpt-image-2.5-sunburst-fal_{n}.png"
            fr = frames(p) if p.exists() else None
            if not fr:
                continue
            fl, im = scale(fr["flash"], LARGO), scale(fr["impact"], IMPACTO)
            if asset == "d_3d":
                for team, rgb in EQUIPOS.items():
                    out.append((f"{asset} teñido {team}", n, [(tint(f, rgb), ax, ay) for f, ax, ay in fl], [(tint(f, rgb), ax, ay) for f, ax, ay in im]))
            else:
                out.append((asset, n, fl, im))
    return out


# el mejor de cada estilo para la hoja corta: la hoja y, en d_3d, el equipo
CORTA = [("a_fuego", 2), ("b_plasma", 2), ("c_pintado", 1), ("d_3d teñido rojo", 2), ("d_3d teñido azul", 2)]


def main():
    hoy = today()
    est = estilos()
    rows = []
    for back in FONDOS:
        rows.append((f"HOY sobre {back}: la estrella low-poly (m1–m3, sin teñir) con el halo radial de drawFlash · 62 px del juego", scene(hoy, "hoy", back)))
    for name, n, fl, im in est:
        for back in FONDOS:
            for mode in MEZCLAS:
                rows.append((f"{name} hoja {n} · fogonazo · {back} · {mode}", scene(fl, mode, back)))
            rows.append((f"{name} hoja {n} · impacto · {back} · normal + núcleo", impact_scene(im, "normal + núcleo", back)))
    save(rows, HERE / "revision.jpg")
    corta(hoy, est)


def corta(hoy, est):
    """una pantalla: por estilo, el pico (cuadro 2) en la boca, con suma y con normal + núcleo, sobre claro y sobre
    oscuro, y el pico del impacto; arriba, el de hoy. Más el plasma con el tono rotado al rojo de un equipo"""
    F = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 15)
    B = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 15)
    cols = [("claro", "suma"), ("claro", "normal + núcleo"), ("oscuro", "suma"), ("oscuro", "normal + núcleo")]
    by = {(name, n): (fl, im) for name, n, fl, im in est}
    lines = [("HOY (low-poly)", None, None)]
    for name, n in CORTA:
        if (name, n) in by:
            lines.append((f"{name} (hoja {n})", *by[(name, n)]))
    if ("b_plasma", 2) in by:
        fl, im = by[("b_plasma", 2)]
        lines.append(("b_plasma, tono rotado al rojo", [(hue(f, 170), ax, ay) for f, ax, ay in fl], [(hue(f, 170), ax, ay) for f, ax, ay in im]))
    Z, cell, H, labw = 2, 170, 150, 230
    W = labw + (len(cols) + 1) * cell * Z
    out = Image.new("RGB", (W, 40 + len(lines) * H * Z), (255, 255, 255))
    d = ImageDraw.Draw(out)
    for j, (back, mode) in enumerate(cols):
        d.text((labw + j * cell * Z + 8, 12), f"{back} · {mode}", fill=(0, 0, 0), font=B)
    d.text((labw + len(cols) * cell * Z + 8, 12), "impacto · claro · normal + núcleo", fill=(0, 0, 0), font=B)
    for i, (lab, fl, im) in enumerate(lines):
        y = 40 + i * H * Z
        d.text((8, y + H * Z // 2 - 8), lab, fill=(0, 0, 0), font=F)
        for j, (back, mode) in enumerate(cols):
            tile = scene([hoy[0]], "hoy", back) if fl is None else scene([fl[1]], mode, back)
            out.paste(tile.resize((tile.width * Z, tile.height * Z), Image.NEAREST), (labw + j * cell * Z, y))
        if im is not None:
            tile = impact_scene([im[1]], "normal + núcleo", "claro")
            out.paste(tile.resize((tile.width * Z, tile.height * Z), Image.NEAREST), (labw + len(cols) * cell * Z, y))
    out.save(HERE / "revision_corta.jpg", quality=88)
    print("→", HERE / "revision_corta.jpg", out.size)


if __name__ == "__main__":
    main()
