"""La entrega de los efectos de salto: los cuadros de la hoja elegida de cada asset, en dos capas (detrás y delante del
personaje), con el ancla en los pies, más medidas.json y las hojas de revisión.

Desde la raíz del repo:
  uv run --project pipeline python backgrounds/lowpoly_saltos/entrega.py

- Los cuadros salen de la hoja cruda (raw/), no de las piezas del post: el modelo dejó pedazos sueltos (fragmentos,
  destellos) y el post las numeró. Cada fila de la hoja se corta en sus cuadros por los N - 1 huecos de columnas
  vacías más anchos, y todo lo que cae entre dos cortes es de ese cuadro.
- Ancla: en el polvo, el medio del cuadro y la línea del piso de su fila (la mediana del borde de abajo de los cuadros
  de esa fila: así no tiemblan). En el doble salto, el medio del cuadro y la fila del anillo (la más ancha del cuadro
  2), la misma para los tres.
- Escala: el cuadro más ancho de cada efecto a su ancho en el juego (ANCHO). El despegue sale de la misma hoja que el
  aterrizaje y queda a su escala. Los archivos van al doble del juego (como DUST_ART y LOWFX_ART); medidas.json da todo
  en px del juego.
- Capas: capas.split_layers, con el ancla en los pies.
- El doble salto sale además en blanco (sin el celeste), para teñirlo por equipo si se elige así.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from capas import split_layers, MEDIO_ANCHO, FRANJA  # noqa: E402

OUT = HERE / "entrega"
ELEGIDAS = {"aterrizaje": 1, "fuerte": 1, "doble": 2}   # la hoja de cada asset (ver el encabezado de gen.toml)
# filas de cada hoja, con sus cuadros, y el ancho en el juego del más ancho de cada efecto
FILAS = {"aterrizaje": [["l1", "l2", "l3"], ["t1", "t2", "t3"]], "fuerte": [["h1", "h2", "h3", "h4"]], "doble": [["d1", "d2", "d3"]]}
ANCHO = {"aterrizaje": 193, "fuerte": 270, "doble": 108}
ARCHIVO = 2      # px del archivo por px del juego
ALPHA_ON = 8


def sheet(asset, n=None):
    return np.array(Image.open(HERE / "raw" / asset / f"gpt-image-2.5-sunburst-fal_{n or ELEGIDAS[asset]}.png").convert("RGBA"))


def bands(al, pad=40):
    rows = al.any(1)
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


def cut(al, n):
    """las columnas de los n cuadros de una banda: cortes en los n - 1 huecos más anchos"""
    occ = al.any(0)
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


def frames(asset, n=None):
    """{cuadro: (rgba recortado, ancla x, ancla y)} en px de la hoja"""
    a = sheet(asset, n)
    al = a[..., 3] >= ALPHA_ON
    out = {}
    for names, (y0, y1) in zip(FILAS[asset], bands(al)):
        cols = cut(al[y0:y1], len(names))
        boxes = []
        for (x0, x1) in cols:
            sub = al[y0:y1, x0:x1]
            ys, xs = np.nonzero(sub.any(1))[0], np.nonzero(sub.any(0))[0]
            boxes.append((x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1))
        if asset == "doble":   # la fila del anillo: la más ancha del cuadro 2
            bx0, by0, bx1, by1 = boxes[1]
            widths = [np.ptp(np.nonzero(al[y, bx0:bx1])[0]) if al[y, bx0:bx1].any() else 0 for y in range(by0, by1)]
            ay = by0 + int(np.argmax(widths))
        else:
            ay = int(np.median([b[3] for b in boxes]))
        for name, (bx0, by0, bx1, by1) in zip(names, boxes):
            f = a[by0:by1, bx0:bx1].copy()
            f[~al[by0:by1, bx0:bx1]] = 0
            out[name] = (f, (bx0 + bx1) / 2 - bx0, ay - by0)
    return out


def premul_resize(a, w, h):
    f = a.astype(np.float32)
    f[..., :3] *= f[..., 3:] / 255
    out = np.zeros((h, w, 4), np.float32)
    for c in range(4):
        out[..., c] = np.array(Image.fromarray(f[..., c]).resize((w, h), Image.LANCZOS))
    out = out.clip(0, 255)
    rgb = np.where(out[..., 3:] > 0, out[..., :3] * 255 / np.maximum(out[..., 3:], 1e-3), 0)
    return np.concatenate([rgb.clip(0, 255), out[..., 3:]], 2).astype(np.uint8)


def scaled(asset, n=None, archivo=ARCHIVO):
    """los cuadros a `archivo` px por px del juego, con el ancla escalada"""
    fr = frames(asset, n)
    first = FILAS[asset][0]
    k = ANCHO[asset] * archivo / max(fr[c][0].shape[1] for c in first)
    out = {}
    for name, (f, ax, ay) in fr.items():
        w, h = max(1, round(f.shape[1] * k)), max(1, round(f.shape[0] * k))
        out[name] = (premul_resize(f, w, h), ax * k, ay * k)
    return out, k


def blanco(a):
    f = a.astype(np.float32)
    lum = f[..., :3] @ np.array([0.299, 0.587, 0.114], np.float32)
    f[..., :3] = lum[..., None]
    return f.clip(0, 255).astype(np.uint8)


def stats(a):
    on = a[..., 3] >= 128
    rgb = a[..., :3][on].astype(np.float32)
    lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
    return round(float(np.median(lum)), 1), round(float((rgb.max(1) - rgb.min(1)).mean()), 1)


def main():
    OUT.mkdir(exist_ok=True)
    med = {}
    for asset in FILAS:
        fr, k = scaled(asset)
        for name, (f, ax, ay) in fr.items():
            back, front = split_layers(f, ax, ay, medio=MEDIO_ANCHO * ARCHIVO, franja=FRANJA * ARCHIVO, fundido=6 * ARCHIVO)
            Image.fromarray(back).save(OUT / f"{name}_atras.png", optimize=True)
            Image.fromarray(front).save(OUT / f"{name}_adelante.png", optimize=True)
            if asset == "doble":
                for capa, im in (("atras", back), ("adelante", front)):
                    Image.fromarray(blanco(im)).save(OUT / f"{name}_{capa}_blanco.png", optimize=True)
            lum, sat = stats(f)
            med[name] = {"asset": asset, "hoja": ELEGIDAS[asset], "w": round(f.shape[1] / ARCHIVO, 1), "h": round(f.shape[0] / ARCHIVO, 1),
                         "ancla": [round(ax / ARCHIVO, 1), round(ay / ARCHIVO, 1)], "archivo": [f.shape[1], f.shape[0]],
                         "luma_mediana": lum, "saturacion": sat}
            print(f"{name}: {f.shape[1] / ARCHIVO:.0f} × {f.shape[0] / ARCHIVO:.0f} del juego, ancla {ax / ARCHIVO:.1f}, {ay / ARCHIVO:.1f}  luma {lum}  sat {sat}")
    nota = {"_nota": "px del juego; los archivos van al doble. Ancla: los pies (x al medio; y en el piso, o en la fila del anillo "
                     "en el doble salto), desde arriba a la izquierda del PNG. Cada cuadro en dos capas del mismo tamaño: "
                     "<cuadro>_atras.png va antes del personaje y <cuadro>_adelante.png después. El doble salto también en "
                     "blanco (_blanco), para teñir por equipo."}
    (OUT / "medidas.json").write_text(json.dumps({**nota, **med}, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
