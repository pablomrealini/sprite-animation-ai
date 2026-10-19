"""Patas más sutiles para el kit (pedido de Pablo, 2026-10-19: "las columnas nuevas las veo medio grotescas... los
módulos viejos tenían columnas más sutiles"). Reemplaza las patas de la pasarela y de las dos columnas del kit por el
poste de las pasarelas viejas de la Refinería low-poly: fino (40 px de fuste), con la franja oscura a la izquierda, un
capitel de 50 y una base chica de dos escalones (50 y 63). Sin generar nada.

Desde la raíz del repo:
  uv run --project pipeline python backgrounds/lowpoly_kit/patas_viejas.py              # propuesta + hoja
  uv run --project pipeline python backgrounds/lowpoly_kit/patas_viejas.py --entregar   # pisa entrega/ (con el OK)

El poste sale de prototypes/arena/arenas/refineria_lowpoly/pasarela_medio_der.png (x 361 – 423, y 60 – 193), que ya
está a 1 px = 1 px del juego, como el kit. Se arma de cualquier alto: capitel + fuste estirado + base. En la pasarela va
debajo de la losa, en el mismo x que la pata que reemplaza, con el capitel asomando debajo de la losa y la base en el
piso (fila 200). Así la franja que se estira (sólo fuste) queda entre las filas ~92 y ~170.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "backgrounds/lowpoly_kit"
ENTREGA = KIT / "entrega"
PROPUESTA = KIT / "propuesta_patas"
VIEJA = ROOT / "prototypes/arena/arenas/refineria_lowpoly"

ALPHA_ON = 128
# el poste viejo, en filas del recorte (y 60 – 193 de la pieza vieja): 0 – 6 la panza de la losa vieja (queda detrás
# de la losa del kit), 6 – 32 capitel, 32 – 104 fuste (lo que se estira), 104 – 134 base
TOP, SHAFT0, SHAFT1 = 6, 32, 104


def poste():
    a = np.array(Image.open(VIEJA / "pasarela_medio_der.png").convert("RGBA"))
    p = a[60:194, 356:430].copy()
    p[:, :5] = 0                          # a la izquierda de x 361, abajo, está el pie de la riostra
    p[SHAFT0:SHAFT1, 56:] = 0             # una mota clara pegada al fuste (x 412 – 413)
    return p


def poste_alto(p, h, con_panza=True, desde=None):
    """el poste de h filas: capitel + fuste estirado + base (con o sin la tira de losa vieja de arriba; `desde` corta
    el capitel desde esa fila del recorte)"""
    top = p[desde if desde is not None else (0 if con_panza else TOP):SHAFT0]
    base = p[SHAFT1:]
    n = h - len(top) - len(base)
    shaft = np.array(Image.fromarray(p[SHAFT0:SHAFT1]).resize((p.shape[1], n), Image.LANCZOS))
    return np.concatenate([top, shaft, base])


def center_x(piece, y0=95, y1=145):
    """el centro de la pata vieja del kit, en el tramo del fuste"""
    al = piece[y0:y1, :, 3] >= ALPHA_ON
    xs = np.nonzero(al.any(0))[0]
    return (xs.min() + xs.max() + 1) / 2


def paste(dst, src, x, y):
    """compone src sobre dst en (x, y), con alfa"""
    h, w = src.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(dst.shape[1], x + w), min(dst.shape[0], y + h)
    s = src[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32)
    d = dst[y0:y1, x0:x1].astype(np.float32)
    sa, da = s[..., 3:] / 255, d[..., 3:] / 255
    oa = sa + da * (1 - sa)
    rgb = (s[..., :3] * sa + d[..., :3] * da * (1 - sa)) / np.maximum(oa, 1e-6)
    dst[y0:y1, x0:x1] = np.concatenate([rgb, oa * 255], 2).clip(0, 255).astype(np.uint8)


def pasarela(piece, p, slab_end=72):
    """la losa del kit (filas 0 – slab_end) sobre el poste viejo, que va de la fila 60 al piso"""
    out = np.zeros_like(piece)
    post = poste_alto(p, 200 - 60)
    shaft_c = 16 + 40 / 2                 # el centro del fuste dentro del recorte (x 372 – 411 de la pieza vieja)
    paste(out, post, int(round(center_x(piece) - shaft_c)), 60)
    slab = piece.copy()
    slab[slab_end:] = 0
    paste(out, slab, 0, 0)
    return out


def ensanchar(p, extra, x=38):
    """el poste más ancho: `extra` copias de una columna de su cara lisa (capitel, fuste y base son lisos ahí)"""
    return np.concatenate([p[:, :x], np.repeat(p[:, x:x + 1], extra, axis=1), p[:, x:]], 1)


def columna_angosta(piece, p, cap_end=37, post_top=33):
    """el capitel rojo de la columna del kit (filas 0 – cap_end, hasta donde terminan los tacos) sobre el poste viejo:
    su capitel desde la fila 12 del recorte (sin el labio en sombra de arriba), asomando debajo de los tacos"""
    cap = piece[:cap_end].copy()
    xs = np.nonzero((cap[..., 3] >= ALPHA_ON).any(0))[0]
    cx = (xs.min() + xs.max() + 1) / 2
    post = poste_alto(p, 200 - post_top, desde=12)
    w = max(piece.shape[1], post.shape[1])
    out = np.zeros((200, w, 4), np.uint8)
    paste(out, post, int(round(cx - (16 + 20))), post_top)
    paste(out, cap, 0, 0)
    xs = np.nonzero((out[..., 3] >= 8).any(0))[0]
    return out[:, xs.min():xs.max() + 1]


def columna_ancha(piece, p, extra=8, top_end=48, post_top=36):
    """el tope pisable de la columna del kit (filas 0 – top_end, tal cual) sobre el poste viejo ensanchado"""
    top = piece[:top_end].copy()
    post = poste_alto(ensanchar(p, extra), 200 - post_top)
    out = np.zeros((200, piece.shape[1], 4), np.uint8)
    paste(out, post, int(round(piece.shape[1] / 2 - (16 + (40 + extra) / 2))), post_top)
    paste(out, top, 0, 0)
    return out


def hoja(antes, despues, path):
    """antes y después a 1:1 sobre el fondo elegido y a x2 sobre verde, con la pasarela vieja de referencia"""
    F = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 15)
    fondo = Image.open(ROOT / "backgrounds/lowpoly_fondos/entrega/abierta_3.webp").convert("RGBA")
    vieja = Image.open(VIEJA / "pasarela_medio_der.png").convert("RGBA")
    ch = None
    for page in sorted((ROOT / "characters/lowpoly/out").glob("lowpoly_0.5x-*.json")):
        fr = json.loads(page.read_text())["frames"].get("idle_combat/0000")
        if fr:
            f = fr["frame"]
            im = Image.open(page.with_suffix(".png")).convert("RGBA").crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))
            ch = im.resize((round(im.width * 0.8), round(im.height * 0.8)), Image.LANCZOS)
            pivot = round((fr["pivot"]["y"] * fr["sourceSize"]["h"] - fr["spriteSourceSize"]["y"]) * 0.8)

    def escena(P):
        """una tira del fondo con: la pasarela vieja, una pasarela del kit (punta + a + b + a + punta) y las dos
        columnas, todo con los pies en el piso del fondo"""
        W, H = 1900, 330
        c = fondo.crop((300, 1264 - H + 40, 300 + W, 1264 + 40)).copy()
        floor = H - 40
        x = 30
        c.alpha_composite(vieja, (x, floor - vieja.height)); x += vieja.width + 50
        seq = ["pasarela_punta_izq", "pasarela_medio_a", "pasarela_medio_b", "pasarela_medio_a", "pasarela_punta_der"]
        x0 = x
        for n in seq:
            c.alpha_composite(Image.fromarray(P[n]), (x, floor - 200)); x += P[n].shape[1]
        c.alpha_composite(ch, (x0 + 300, floor - 200 + 16 - pivot))
        x += 60
        for n in ("columna_angosta", "columna_ancha"):
            c.alpha_composite(Image.fromarray(P[n]), (x, floor - 200)); x += P[n].shape[1] + 60
        c.alpha_composite(ch, (x, floor - pivot))
        return c.convert("RGB")

    def verde(P):
        seq = ["pasarela_punta_izq", "pasarela_medio_a", "pasarela_medio_b", "pasarela_punta_der", None,
               "columna_angosta", None, "columna_ancha"]
        W = sum(P[n].shape[1] if n else 30 for n in seq) + 40
        c = Image.new("RGBA", (W, 240), (0, 177, 64, 255)); x = 20
        for n in seq:
            if n is None:
                x += 30; continue
            c.alpha_composite(Image.fromarray(P[n]), (x, 20)); x += P[n].shape[1]
        c = c.convert("RGB")
        return c.resize((c.width * 2, c.height * 2), Image.NEAREST)

    numeros = Image.new("RGB", (1900, 92), (255, 255, 255))
    dn = ImageDraw.Draw(numeros)
    for i, t in enumerate([
            "Poste viejo (pasarelas de la Refinería): fuste 31–40 px, capitel 43–50, base 38–63 y ~25 de alto, franja oscura a la izquierda; uno cada ~250–400 px, con riostras.",
            "Patas del kit, antes: fuste 42–44, se abren a 58–61 arriba y a 83–87 abajo, con zapata de ~38 de alto. Columna angosta: fuste 31, pie 69. Ancha: fuste 44, base escalonada de 96–103 × 62.",
            "Después: el poste viejo tal cual (fuste 40, capitel 50, base 50/63, 26 de alto) en las patas de la pasarela (una por medio_a y por punta, en el mismo x)",
            "y en la columna angosta (con el capitel rojo del kit); en la ancha, el mismo poste con fuste de 48 bajo su tope de 113. Lo que se estira es sólo fuste: filas ~92 a ~170."]):
        dn.text((8, 4 + 22 * i), t, fill=(0, 0, 0), font=F)
    items = [("Medidas en px del juego", numeros),
             ("ANTES · 1:1 sobre el fondo · a la izquierda, la pasarela vieja de la Refinería (referencia)", escena(antes)),
             ("DESPUÉS · las patas y columnas con el poste viejo", escena(despues)),
             ("ANTES · x2 sobre verde", verde(antes)), ("DESPUÉS · x2 sobre verde", verde(despues))]
    W = max(i.width for _, i in items)
    out = Image.new("RGB", (W, sum(i.height + 26 for _, i in items)), (255, 255, 255))
    d, y = ImageDraw.Draw(out), 0
    for lab, i in items:
        d.text((8, y + 4), lab, fill=(0, 0, 0), font=F); out.paste(i, (0, y + 26)); y += i.height + 26
    out.save(path, quality=88)


def main():
    entregar = "--entregar" in sys.argv
    p = poste()
    antes = {n: np.array(Image.open(ENTREGA / f"{n}.png").convert("RGBA")) for n in
             ("pasarela_punta_izq", "pasarela_medio_a", "pasarela_medio_b", "pasarela_punta_der", "columna_angosta", "columna_ancha")}
    despues = dict(antes)
    for n in ("pasarela_punta_izq", "pasarela_medio_a", "pasarela_punta_der"):
        despues[n] = pasarela(antes[n], p)
    despues["columna_angosta"] = columna_angosta(antes["columna_angosta"], p)
    despues["columna_ancha"] = columna_ancha(antes["columna_ancha"], p)
    dst = ENTREGA if entregar else PROPUESTA
    dst.mkdir(parents=True, exist_ok=True)
    for n in ("pasarela_punta_izq", "pasarela_medio_a", "pasarela_punta_der", "columna_angosta", "columna_ancha"):
        Image.fromarray(despues[n]).save(dst / f"{n}.png", optimize=True)
        print(f"{n:20s} {despues[n].shape[1]} × {despues[n].shape[0]}")
    hoja(antes, despues, (KIT if entregar else PROPUESTA) / "patas_antes_despues.jpg")
    if entregar:
        m = json.loads((ENTREGA / "medidas.json").read_text())
        for n in ("columna_angosta", "columna_ancha"):
            m[n]["w"] = int(despues[n].shape[1])
        for n in ("pasarela_punta_izq", "pasarela_medio_a", "pasarela_punta_der", "columna_angosta", "columna_ancha"):
            m[n]["patas"] = "poste de pasarela_medio_der de la Refinería low-poly (patas_viejas.py)"
        (ENTREGA / "medidas.json").write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
