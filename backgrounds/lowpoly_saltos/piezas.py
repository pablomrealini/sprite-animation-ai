"""Los efectos de salto en piezas sueltas, para que el código anime cada una a 60 fps (Pablo, 2026-10-20: con cuadros
"son medias duras y poco smooth").

Desde la raíz del repo:
  uv run --project pipeline python backgrounds/lowpoly_saltos/piezas.py

De la hoja elegida de cada efecto (entrega.ELEGIDAS) toma el cuadro más completo (t2, l2, h2, d2) y la estrella o el
destello del primero (t1, l1, h1, d1), y escribe en piezas/ cada pedazo como su propio PNG, al doble del juego, más
piezas.json y revision_piezas.jpg (las piezas numeradas, armadas en su lugar sobre verde y con el personaje).

- Pedazos: las manchas opacas (alfa ≥ 200) del cuadro. Lo translúcido de alrededor (el borde, el brillo, la banda del
  piso) va con la mancha más cercana, hasta R px de la hoja; más lejos se descarta.
- h2 tiene las dos nubes unidas por la banda del piso: se corta al medio, donde lo opaco mide 7 px. Cada mitad se queda
  con su nube y su esquirla del centro.
- d1: el destello es el fogonazo del medio, que está pegado al anillo y a la punta. Se saca con una máscara blanda
  centrada en el fogonazo: los arcos y la punta ya vienen de d2.
- Tipo: en el polvo, las dos manchas más grandes son "nube" y el resto "esquirla"; la estrella entera es "estrella". En
  el doble salto, los rombos chicos son "destello", la punta para abajo es "esquirla" y el resto, "anillo".
- Capa: con la regla de capas.py, por el centro de la pieza. Atrás va lo que cae en la ventana del cuerpo (|x| < 22,
  y < -14; en el doble salto, y < -2: el arco de atrás del anillo). La estrella y el destello se parten en las dos capas
  (dos entradas con el mismo "junto": se mueven juntas).
- x, y: el centro de la pieza respecto del ancla de los pies, y w, h: su tamaño, en px del juego al tamaño de hoy del
  dibujo. Para arriba, y negativo.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import entrega  # noqa: E402
import revision  # noqa: E402
from capas import split_layers, MEDIO_ANCHO, FRANJA  # noqa: E402

OUT = HERE / "piezas"
EFECTOS = {   # efecto: (asset, primer cuadro, cuadro completo)
    "despegue": ("aterrizaje", "t1", "t2"),
    "aterrizaje": ("aterrizaje", "l1", "l2"),
    "fuerte": ("fuerte", "h1", "h2"),
    "doble": ("doble", "d1", "d2"),
}
OPACO = 200
R = 40            # px de la hoja: hasta dónde lo translúcido se pega a la mancha más cercana
MIN_AREA = 150    # px de la hoja: menos que esto no es una pieza
CORTE_H2 = 335    # x de la hoja (en el cuadro h2) donde se separan las dos nubes


def manchas(f, corte=None):
    """etiquetas (0 = nada) de cada pieza del cuadro f (rgba de la hoja): las manchas opacas y lo translúcido cercano.
    Con `corte`, lo que quede en una sola pieza a los dos lados de esa x se parte en dos ahí"""
    a = f[..., 3]
    m = (a >= OPACO).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    keep = [i for i in range(1, n) if st[i, 4] >= MIN_AREA]
    seeds = np.zeros_like(lab)
    for j, i in enumerate(keep, 1):
        seeds[lab == i] = j
    # cada px con algo de alfa, a la pieza más cercana (hasta R)
    inv = (seeds == 0).astype(np.uint8)
    dist, near = cv2.distanceTransformWithLabels(inv, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    idx = np.zeros(near.max() + 1, np.int32)
    zero_px = np.argwhere(inv == 0)                     # los px semilla, en el orden de las etiquetas de cv2
    idx[np.arange(1, len(zero_px) + 1)] = seeds[zero_px[:, 0], zero_px[:, 1]]
    out = np.where((a > 0) & (dist <= R), idx[near], 0)
    if corte is not None:
        nxt = out.max() + 1
        for i in range(1, nxt):
            xs = np.nonzero(out == i)[1]
            if len(xs) and xs.min() < corte <= xs.max():
                right = (out == i) & (np.arange(out.shape[1])[None, :] >= corte)
                out[right] = nxt
                nxt += 1
    return out


def destello(f, ax, ay):
    """el fogonazo del medio de d1: una máscara elíptica blanda (más alta para arriba, donde está su punta)"""
    h, w = f.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx, dy = (xx - ax) / 150, np.where(yy < ay, (yy - ay) / 150, (yy - ay) / 70)
    r = np.sqrt(dx * dx + dy * dy)
    m = np.clip((1 - r) / 0.45, 0, 1)
    g = f.copy()
    g[..., 3] = (f[..., 3] * m).astype(np.uint8)
    return g


def crop(f):
    ys, xs = np.nonzero(f[..., 3] > 0)
    return f[ys.min():ys.max() + 1, xs.min():xs.max() + 1], xs.min(), ys.min()


def main():
    OUT.mkdir(exist_ok=True)
    for p in OUT.glob("*.png"):
        p.unlink()
    data = {}
    for efecto, (asset, first, full) in EFECTOS.items():
        fr = entrega.frames(asset)
        _, k = entrega.scaled(asset)          # px del archivo por px de la hoja
        g = k / entrega.ARCHIVO               # px del juego por px de la hoja
        doble = asset == "doble"
        fr_y = 2 if doble else FRANJA         # la franja de la regla de capas, para el doble: la línea del anillo
        items = []

        def add(img, x0, y0, ax, ay, tipo, de, capa=None, junto=None):
            piece, cx0, cy0 = crop(img)
            x0, y0 = x0 + cx0, y0 + cy0
            cx, cy = (x0 + piece.shape[1] / 2 - ax) * g, (y0 + piece.shape[0] / 2 - ay) * g
            if capa is None:
                capa = "atras" if abs(cx) < MEDIO_ANCHO and cy < -fr_y else "adelante"
            w, h = max(1, round(piece.shape[1] * k)), max(1, round(piece.shape[0] * k))
            name = f"{efecto}_{len(items) + 1:02d}_{tipo}.png"
            Image.fromarray(entrega.premul_resize(piece, w, h)).save(OUT / name, optimize=True)
            items.append({"src": f"piezas/{name}", "x": round(cx, 1), "y": round(cy, 1), "w": round(w / entrega.ARCHIVO, 1),
                          "h": round(h / entrega.ARCHIVO, 1), "capa": capa, "tipo": tipo, "de": de, **({"junto": junto} if junto else {})})

        # la estrella (o el destello), en las dos capas
        f, ax, ay = fr[first]
        src = destello(f, ax, ay) if doble else f
        back, front = split_layers(src, ax, ay, medio=MEDIO_ANCHO / g, franja=fr_y / g, fundido=6 / g)
        tipo = "destello" if doble else "estrella"
        for capa, img in (("atras", back), ("adelante", front)):
            if (img[..., 3] > 8).sum() > MIN_AREA:
                add(img, 0, 0, ax, ay, tipo, first, capa, junto=f"{efecto}_{tipo}")
        # los pedazos del cuadro completo
        f, ax, ay = fr[full]
        lab = manchas(f, CORTE_H2 if full == "h2" else None)
        ids = [i for i in range(1, lab.max() + 1) if (lab == i).any()]
        areas = {i: int(((lab == i) & (f[..., 3] >= OPACO)).sum()) for i in ids}
        big = sorted(ids, key=lambda i: -areas[i])[:2]
        for i in sorted(ids, key=lambda i: (np.nonzero(lab == i)[1].mean())):   # de izquierda a derecha
            piece = f.copy()
            piece[lab != i, 3] = 0
            if doble:
                ys, xs = np.nonzero((lab == i) & (f[..., 3] >= OPACO))
                bw, bh = np.ptp(xs) + 1, np.ptp(ys) + 1
                if areas[i] < 2500 and 0.6 < bw / bh < 1.4:
                    tipo = "destello"
                elif bh > 1.3 * bw and ys.max() > ay + 60:
                    tipo = "esquirla"
                else:
                    tipo = "anillo"
            else:
                tipo = "nube" if i in big else "esquirla"
            add(piece, 0, 0, ax, ay, tipo, full)
        data[efecto] = items
        print(efecto, len(items), "piezas:", ", ".join(f"{it['tipo']} {it['w']:.0f}×{it['h']:.0f} en ({it['x']:+.0f}, {it['y']:+.0f}) {it['capa']}" for it in items))
    nota = ("Px del juego: x, y es el centro de la pieza respecto del ancla de los pies (para arriba, y negativo); w, h, su "
            "tamaño al tamaño de hoy del dibujo. Los PNG van al doble. capa: atras se dibuja antes del personaje, adelante "
            "después. junto: las dos mitades (atrás y adelante) de la estrella o del destello, que se mueven juntas. de: "
            "el cuadro de donde sale (hoja elegida de entrega.ELEGIDAS).")
    (OUT / "piezas.json").write_text(json.dumps({"_nota": nota, **data}, indent=1, ensure_ascii=False) + "\n")
    hoja(data)


def hoja(data):
    """cada efecto: el cuadro original y las piezas armadas en su lugar, numeradas, con el personaje (x2, sobre verde)"""
    F = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 13)
    ch, px, py = revision.rc.char("idle_combat")
    rows = []
    for efecto, items in data.items():
        asset, first, full = EFECTOS[efecto]
        fr, _ = entrega.scaled(asset)
        air = 90 if asset == "doble" else 0
        W = int(max(max(abs(it["x"]) + it["w"] / 2 for it in items) * 2 + 60, 260))
        H = 190 + air
        fy = H - 30 - air
        panels = []
        for mode in ("cuadros", "piezas"):
            c = Image.new("RGBA", (W, H), revision.GREEN + (255,))
            cx = W // 2
            if mode == "cuadros":
                for n in (first, full):
                    f, ax, ay = revision.game([fr[n]])[0]
                    b, fz = split_layers(f, ax, ay, franja=2 if asset == "doble" else FRANJA)
                    if n == full:
                        c.alpha_composite(Image.fromarray(b), (int(round(cx - ax)), int(round(fy - ay))))
                c.alpha_composite(ch, (cx - px, fy - py))
                f, ax, ay = revision.game([fr[full]])[0]
                b, fz = split_layers(f, ax, ay, franja=2 if asset == "doble" else FRANJA)
                c.alpha_composite(Image.fromarray(fz), (int(round(cx - ax)), int(round(fy - ay))))
            else:
                ims = {}
                for it in items:
                    im = Image.open(HERE / it["src"]).convert("RGBA")
                    ims[it["src"]] = im.resize((max(1, round(it["w"])), max(1, round(it["h"]))), Image.LANCZOS)
                for capa in ("atras", "personaje", "adelante"):
                    if capa == "personaje":
                        c.alpha_composite(ch, (cx - px, fy - py)); continue
                    for it in items:
                        if it["capa"] == capa:
                            im = ims[it["src"]]
                            c.alpha_composite(im, (int(round(cx + it["x"] - im.width / 2)), int(round(fy + it["y"] - im.height / 2))))
            panels.append(c.convert("RGB").resize((W * 2, H * 2), Image.NEAREST))
        # los números, sobre el panel de las piezas
        d = ImageDraw.Draw(panels[1])
        used = []
        for j, it in enumerate(items, 1):
            x, y = (W // 2 + it["x"]) * 2, (fy + it["y"]) * 2
            while any(abs(x - ux) < 20 and abs(y - uy) < 20 for ux, uy in used):   # que no se encimen
                y += 20
            used.append((x, y))
            r = 9
            d.ellipse((x - r, y - r, x + r, y + r), fill=(20, 20, 20) if it["capa"] == "atras" else (230, 30, 30))
            d.text((x, y), str(j), fill=(255, 255, 255), font=F, anchor="mm")
        row = Image.new("RGB", (panels[0].width * 2 + 20, panels[0].height), (255, 255, 255))
        row.paste(panels[0], (0, 0)); row.paste(panels[1], (panels[0].width + 20, 0))
        lab = (f"{efecto}: a la izquierda, {full} como cuadro (con sus dos capas); a la derecha, las {len(items)} piezas en su lugar "
               f"(número negro = atrás, rojo = adelante)\n"
               + " · ".join(f"{j} {it['tipo']} {it['capa']} ({it['de']})" for j, it in enumerate(items, 1)))
        rows.append((lab, row))
    W = max(r.width for _, r in rows)
    out = Image.new("RGB", (W, sum(r.height + 44 for _, r in rows)), (255, 255, 255))
    d, y = ImageDraw.Draw(out), 0
    for lab, r in rows:
        d.multiline_text((8, y + 5), lab, fill=(0, 0, 0), font=F, spacing=4); out.paste(r, (0, y + 44)); y += r.height + 44
    out.save(HERE / "revision_piezas.jpg", quality=88)
    print("→", HERE / "revision_piezas.jpg", out.size)


if __name__ == "__main__":
    main()
