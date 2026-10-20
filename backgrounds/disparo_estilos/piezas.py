"""El fogonazo y el impacto elegidos (d_3d, hoja 2: Pablo, 2026-10-20, "me gusta diseño 3d teñido de rojo hoja 2") en
piezas sueltas, para que el código las anime a 60 fps como los efectos de salto.

Desde la raíz del repo:
  uv run --project pipeline python backgrounds/disparo_estilos/piezas.py

Del pico de cada fila de la hoja (el cuadro 2 del fogonazo y el del impacto) saca el núcleo, cada rayo y cada chispa, y
escribe en piezas/ cada pieza en dos PNG al doble del juego, en blanco y grises para teñir por equipo:
- <pieza>_alfa.png: se dibuja normal. Alfa = el brillo (el canal más alto de la hoja negra) y el color des-multiplicado.
- <pieza>_nucleo.png: se suma (lighter) a 0,5. El mismo color, con el alfa sólo donde la luz es más blanca (luma de
  0,55 a 1). Juntas dan la mezcla "normal + núcleo" de la revisión, que se lee en claro y en oscuro.
Más piezas.json y revision_piezas.jpg.

Cómo se separan:
- Lo sólido es lo que tiene brillo > 0,55. La mancha más grande es el cuerpo; las demás manchas sueltas son rayos si
  son largas (más del 22% del ancho del cuadro: las estelas) y chispas si no (los rombos facetados).
- El cuerpo se abre con un disco de radio 34 px de la hoja: lo que queda es el núcleo y lo que se va, cada pincho, un
  rayo. Lo que toca la boca (la barrita de luz pegada al cañón) vuelve al núcleo.
- El brillo de alrededor va con la pieza más cercana, hasta R px de la hoja.
- ang: hacia dónde apunta la pieza, en grados, 0 = hacia adelante del tiro (+x) y positivo hacia abajo (como el canvas).
  Rayos: su eje mayor, para el lado de afuera del núcleo. Chispas: desde el centro del núcleo hacia la chispa.
- x, y: el centro de la pieza desde la boca del arma (fogonazo: el borde de atrás del cuadro, a la altura de la barrita)
  o desde el punto del impacto (el centro del núcleo), en px del juego, con el pico del fogonazo a 62 de largo (como
  hoy) y el del impacto a 60 de ancho. w, h: su tamaño en px del juego.
"""
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import revision as rv  # noqa: E402

HOJA = HERE / "post/d_3d/gpt-image-2.5-sunburst-fal_2.png"
OUT = HERE / "piezas"
ARCHIVO = 2
SOLIDO, RADIO, R, MIN_RAYO, MIN_CHISPA = 0.55, 34, 30, 120, 20
EFECTOS = {"fogonazo": ("flash", rv.LARGO), "impacto": ("impact", rv.IMPACTO)}


def axes(mask):
    """centro, ángulo del eje mayor (grados) y largo de una mancha (el de una barra con esa varianza: 3,46 σ)"""
    ys, xs = np.nonzero(mask)
    c = np.array([xs.mean(), ys.mean()])
    if len(xs) < 3:
        return c, 0.0, 0.0
    cov = np.cov(np.stack([xs - c[0], ys - c[1]]))
    w, v = np.linalg.eigh(cov)
    major = v[:, 1]
    return c, math.degrees(math.atan2(major[1], major[0])), 3.46 * math.sqrt(max(w[1], 0))


def segment(f, ax, ay, kind):
    """las piezas del pico: [(tipo, máscara de la pieza con su brillo)] y el centro del núcleo"""
    a = f.max(2) / 255
    solid = (a > SOLIDO).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(solid, connectivity=8)
    main = 1 + int(np.argmax(st[1:, 4]))
    body = (lab == main).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * RADIO + 1, 2 * RADIO + 1))
    core = cv2.morphologyEx(body, cv2.MORPH_OPEN, k)
    nc, lc, sc, _ = cv2.connectedComponentsWithStats(core, connectivity=8)
    core = (lc == 1 + int(np.argmax(sc[1:, 4]))).astype(np.uint8)
    rest = body & (1 - cv2.dilate(core, np.ones((5, 5), np.uint8)))
    nr, lr, sr, _ = cv2.connectedComponentsWithStats(rest, connectivity=8)
    seeds = [("nucleo", core > 0)]
    for i in range(1, nr):
        m = lr == i
        if sr[i, 4] < MIN_RAYO:
            core |= m.astype(np.uint8)            # los pedacitos de la base vuelven al núcleo
            continue
        if kind == "flash" and np.nonzero(m)[1].min() <= 4:
            core |= m.astype(np.uint8)            # la barrita de la boca es núcleo
            continue
        seeds.append(("rayo", m))
    seeds[0] = ("nucleo", core > 0)
    for i in range(1, n):
        if i != main and st[i, 4] >= MIN_CHISPA:
            m = lab == i
            _, _, largo = axes(m)
            seeds.append(("rayo" if largo > 0.22 * f.shape[1] else "chispa", m))
    # el brillo de alrededor, a la semilla más cercana
    lbl = np.zeros(a.shape, np.int32)
    for j, (_, m) in enumerate(seeds, 1):
        lbl[m] = j
    inv = (lbl == 0).astype(np.uint8)
    dist, near = cv2.distanceTransformWithLabels(inv, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    idx = np.zeros(near.max() + 1, np.int32)
    zp = np.argwhere(inv == 0)
    idx[np.arange(1, len(zp) + 1)] = lbl[zp[:, 0], zp[:, 1]]
    full = np.where((a > 0.01) & (dist <= R), idx[near], 0)
    cc, _, _ = axes(core > 0)
    return [(t, full == j) for j, (t, _) in enumerate(seeds, 1)], cc, seeds


def layers(f, mask):
    """(alfa, núcleo) RGBA de la pieza: color des-multiplicado, alfa = brillo; el núcleo, sólo en lo más blanco"""
    a = f.max(2) / 255
    col = np.where(a[..., None] > 0, f / np.maximum(a[..., None], 1e-3), 0).clip(0, 255)
    lum = f.mean(2) / 255
    alpha = (a * mask * 255).clip(0, 255)
    core = np.clip((lum - 0.55) / 0.45, 0, 1)
    return (np.dstack([col, alpha]).astype(np.uint8), np.dstack([col, alpha * core]).astype(np.uint8))


def crop(img, box):
    x0, y0, x1, y1 = box
    return img[y0:y1, x0:x1]


def resize(img, k):
    h, w = img.shape[:2]
    return np.array(Image.fromarray(img).resize((max(1, round(w * k)), max(1, round(h * k))), Image.LANCZOS))


def main():
    OUT.mkdir(exist_ok=True)
    for p in OUT.glob("*.png"):
        p.unlink()
    fr = rv.frames(HOJA)
    data, origen = {}, {}
    for efecto, (kind, ancho) in EFECTOS.items():
        f, ax, ay = fr[kind][1]
        k = ancho * ARCHIVO / f.shape[1]            # px del archivo por px de la hoja
        g = k / ARCHIVO
        pieces, cc, seeds = segment(f, ax, ay, kind)
        if kind == "flash":                          # la boca: el borde de atrás, a la altura de la barrita
            a = f.max(2) / 255
            ys = np.nonzero(a[:, :12] > SOLIDO)[0]
            org = (0.0, float(ys.mean()) if len(ys) else ay)
        else:
            org = (float(cc[0]), float(cc[1]))
        items = []
        order = sorted(range(len(pieces)), key=lambda j: (pieces[j][0] != "nucleo", pieces[j][0] != "rayo"))
        for j in order:
            tipo, m = pieces[j]
            ys, xs = np.nonzero(m)
            if not len(xs):
                continue
            box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
            al, nu = layers(f, m)
            al, nu = resize(crop(al, box), k), resize(crop(nu, box), k)
            c, deg, _ = axes(seeds[j][1])
            if tipo == "rayo":                       # el eje, para el lado de afuera del núcleo
                v = np.array([math.cos(math.radians(deg)), math.sin(math.radians(deg))])
                if np.dot(c - cc, v) < 0:
                    deg = (deg + 180) % 360
            elif tipo == "chispa":
                deg = math.degrees(math.atan2(c[1] - cc[1], c[0] - cc[0]))
            else:
                deg = 0.0
            deg = (deg + 180) % 360 - 180
            name = f"{efecto}_{len(items) + 1:02d}_{tipo}"
            Image.fromarray(al).save(OUT / f"{name}_alfa.png", optimize=True)
            Image.fromarray(nu).save(OUT / f"{name}_nucleo.png", optimize=True)
            cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
            items.append({"src": f"piezas/{name}_alfa.png", "nucleo": f"piezas/{name}_nucleo.png",
                          "x": round((cx - org[0]) * g, 1), "y": round((cy - org[1]) * g, 1),
                          "w": round(al.shape[1] / ARCHIVO, 1), "h": round(al.shape[0] / ARCHIVO, 1),
                          "tipo": tipo, "ang": round(deg, 1)})
        data[efecto] = items
        origen[efecto] = (org, g)
        tipos = {t: sum(1 for it in items if it["tipo"] == t) for t in ("nucleo", "rayo", "chispa")}
        print(efecto, len(items), "piezas:", tipos)
    nota = ("Px del juego. x, y: el centro de la pieza desde la boca del arma (fogonazo) o desde el punto del impacto "
            "(impacto), para arriba y negativo; el fogonazo, con el pico a 62 de largo y el impacto a 60 de ancho. w, h: "
            "su tamaño. ang: hacia dónde apunta, en grados, 0 = adelante del tiro (+x), positivo hacia abajo. src (_alfa) "
            "se dibuja normal y nucleo (_nucleo) se suma (lighter) a 0,5; los dos en blanco y grises, para teñir con el "
            "color del equipo. El teñido va sobre la luz l = luma(color) × alfa / 255, no sobre el color: "
            "luz teñida = equipo × l + (blanco - equipo) × l × clamp((l - 0,88) / 0,12), y se guarda dividida por alfa. "
            "Del pico de d_3d, hoja 2 (backgrounds/disparo_estilos).")
    (OUT / "piezas.json").write_text(json.dumps({"_nota": nota, **data}, indent=1, ensure_ascii=False) + "\n")
    hoja(data, fr, origen)


def tinted(path, team):
    """el teñido va sobre la luz (color × alfa), no sobre el color: el color des-multiplicado de este arte es casi todo
    blanco. Se tiñe la luz con rv.tint y se vuelve a des-multiplicar"""
    im = np.array(Image.open(HERE / path).convert("RGBA")).astype(np.float32)
    a = im[..., 3:] / 255
    light = rv.tint(im[..., :3] * a, team)
    col = np.where(a > 0, light / np.maximum(a, 1e-3), 0).clip(0, 255)
    return np.dstack([col, im[..., 3]])


def draw(acc, ox, oy, items, team, base_scale=1.0):
    """las piezas en (ox, oy) del lienzo: cada _alfa normal y su _nucleo sumado a 0,5 (al tamaño del juego)"""
    for it in items:
        for path, mode in ((it["src"], "normal"), (it["nucleo"], "suma")):
            im = tinted(path, team)
            w, h = max(1, round(it["w"])), max(1, round(it["h"]))
            im = np.array(Image.fromarray(im.clip(0, 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)).astype(np.float32)
            x0, y0 = int(round(ox + it["x"] - w / 2)), int(round(oy + it["y"] - h / 2))
            H, W = acc.shape[:2]
            X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
            if X1 <= X0 or Y1 <= Y0:
                continue
            p = im[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
            a = p[..., 3:] / 255
            if mode == "normal":
                acc[Y0:Y1, X0:X1] = acc[Y0:Y1, X0:X1] * (1 - a) + p[..., :3] * a
            else:
                acc[Y0:Y1, X0:X1] += p[..., :3] * a * 0.5


def numerado(efecto, items, Z=4):
    """las piezas sin teñir sobre gris oscuro, a x4, cada una con su número en el centro y una raya hacia donde apunta;
    la leyenda, en varias líneas"""
    F = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 12)
    xs = [it["x"] - it["w"] / 2 for it in items] + [it["x"] + it["w"] / 2 for it in items]
    ys = [it["y"] - it["h"] / 2 for it in items] + [it["y"] + it["h"] / 2 for it in items]
    pad = 6
    W, H = int(max(xs) - min(xs)) + 2 * pad, int(max(ys) - min(ys)) + 2 * pad
    ox, oy = pad - min(xs), pad - min(ys)
    acc = np.full((H, W, 3), 45, np.float32)
    draw(acc, ox, oy, items, (255, 255, 255))
    im = Image.fromarray(acc.clip(0, 255).astype(np.uint8)).resize((W * Z, H * Z), Image.NEAREST)
    d = ImageDraw.Draw(im)
    col = {"nucleo": (20, 20, 20), "rayo": (230, 30, 30), "chispa": (30, 90, 230), "destello": (240, 180, 0)}
    for j, it in enumerate(items, 1):
        x, y = (ox + it["x"]) * Z, (oy + it["y"]) * Z
        if it["tipo"] != "nucleo":
            L = 22
            d.line((x, y, x + L * math.cos(math.radians(it["ang"])), y + L * math.sin(math.radians(it["ang"]))), fill=col[it["tipo"]], width=3)
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=col[it["tipo"]], outline=(255, 255, 255))
        d.text((x, y), str(j), fill=(255, 255, 255), font=F, anchor="mm")
    parts = [f"{j} {it['tipo']} {it['ang']:+.0f}°" for j, it in enumerate(items, 1)]
    lines = [" · ".join(parts[i:i + 11]) for i in range(0, len(parts), 11)]
    lab = (f"{efecto}: las {len(items)} piezas a x4, sin teñir, con su número (negro núcleo, rojo rayo, azul chispa) y una raya "
           "hacia donde apunta (ang)\n" + "\n".join(lines))
    return lab, im


def hoja(data, fr, origen):
    """por efecto, equipo y fondo: el pico entero (izquierda) y las piezas armadas en su lugar (derecha), con los números
    en la primera fila de cada efecto"""
    F = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 13)
    ch, px, py = rv.char()
    mx, my = rv.muzzle()
    rows = []
    for efecto, items in data.items():
        kind, ancho = EFECTOS[efecto]
        f, ax, ay = fr[kind][1]
        # el pico entero, como una sola pieza con el mismo origen
        whole = [{"src": None}]
        for team_name, team in rv.EQUIPOS.items():
            for back in ("claro", "oscuro"):
                panels = []
                for mode in ("pico", "piezas"):
                    W, H = 230, 170
                    if efecto == "fogonazo":
                        base = rv.FONDOS[back].crop((700, 1264 - H + 20, 700 + W, 1264 + 20)).convert("RGBA")
                        base.alpha_composite(ch, (40 - px, H - 20 - py))
                        ox, oy = 40 + mx, H - 20 + my
                    else:
                        base = rv.FONDOS[back].crop((1400, 1264 - H + 20, 1400 + W, 1264 + 20)).convert("RGBA")
                        ox, oy = W / 2, H / 2
                    acc = np.array(base.convert("RGB")).astype(np.float32)
                    if mode == "pico":
                        g = rv.scale(fr[kind], ancho)[1]
                        t = rv.tint(g[0], team)
                        (orx, ory), gk = origen[efecto]    # el mismo origen que las piezas
                        rv.put(acc, t, int(round(ox - orx * gk)), int(round(oy - ory * gk)), "normal + núcleo")
                    else:
                        draw(acc, ox, oy, items, team)
                    im = Image.fromarray(acc.clip(0, 255).astype(np.uint8)).resize((W * 2, H * 2), Image.NEAREST)
                    panels.append(im)
                row = Image.new("RGB", (panels[0].width * 2 + 16, panels[0].height), (255, 255, 255))
                row.paste(panels[0], (0, 0)); row.paste(panels[1], (panels[0].width + 16, 0))
                rows.append((f"{efecto} · teñido {team_name} · {back} · izquierda el pico entero, derecha las {len(items)} piezas "
                             f"en su lugar (normal + núcleo)", row))
        rows.insert(len(rows) - 4, numerado(efecto, items))
    W = max(r.width for _, r in rows)
    heads = [lab.count("\n") * 17 + 22 for lab, _ in rows]
    out = Image.new("RGB", (max(W, 1200), sum(r.height + h for (_, r), h in zip(rows, heads))), (255, 255, 255))
    d, y = ImageDraw.Draw(out), 0
    for (lab, r), h in zip(rows, heads):
        d.multiline_text((8, y + 4), lab, fill=(0, 0, 0), font=F, spacing=4); out.paste(r, (0, y + h)); y += r.height + h
    out.save(HERE / "revision_piezas.jpg", quality=88)
    print("→", HERE / "revision_piezas.jpg", out.size)


if __name__ == "__main__":
    main()
