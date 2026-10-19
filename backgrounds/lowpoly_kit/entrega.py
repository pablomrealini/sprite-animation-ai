"""La entrega del kit low-poly y del fondo elegido, a px del juego, para la paleta del editor de arenas.

Desde la raíz del repo:
  uv run --project pipeline python backgrounds/lowpoly_kit/entrega.py

Lee las piezas elegidas de post/ (ELEGIDAS, abajo) y escribe en backgrounds/lowpoly_kit/entrega/ cada pieza a 1 px = 1 px
del juego, más medidas.json (tamaño, línea de los pies y escala de cada pieza) y las hojas de revisión. El fondo elegido
va a backgrounds/lowpoly_fondos/entrega/ en WebP, a 2496 × 1404. Las medidas que se buscan son las de
prototypes/arena/editor/kit_medidas.md:
- pasarela: una sola escala para los cuatro tramos (tienen que empalmar), la que lleva de la línea de los pies al piso a
  184 px. Lienzo de 200 de alto con los pies en la fila 16. Los medios, a 256 de ancho exactos (se estiran en x menos de
  un 2%). Las puntas se cortan en la losa lisa, 4 px después de la zapata: más angostas no se puede sin cortar el pie.
- columnas: lienzo de 200 con el piso abajo. En las que tienen tope pisable, los pies en 16 (cada una a su escala,
  que difiere menos de un 3%). Las demás, a la escala mediana.
- flotantes: una escala, la que lleva de los pies a abajo a 72. Lienzo de 80 con los pies en 8; el ascensor, más alto
  por el pistón. El ancho se lleva a 200, 300 y 450 sacando o duplicando columnas de los tramos lisos (losa, panza y
  luz), nunca de los tacos rojos. El ascensor queda a su ancho: tiene franjas diagonales en todo el frente.
- deco y caños: la torre a 600 de alto y los caños a 48 de grueso; los rectos se estiran a lo largo a 256 (un caño liso
  no cambia). Llevan bruma hacia el azul lejano del fondo (BRUMA): el modelo los dibujó tan nítidos como lo jugable.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "backgrounds/lowpoly_kit"
FONDOS = ROOT / "backgrounds/lowpoly_fondos"
OUT = KIT / "entrega"
OUT_FONDO = FONDOS / "entrega"

ELEGIDAS = {   # 2026-10-18: la hoja de cada asset (ver el encabezado de gen.toml)
    "pasarela": 2, "columnas": 1, "flotantes": 1, "deco": 1, "canos": 1,
}
FONDO = 3                      # backgrounds/lowpoly_fondos/post/abierta/nano-banana-2.1_3.png
BRUMA = ((129, 154, 197), 0.35)   # la mediana de la zona lejana del fondo elegido y cuánto se mezcla
ALPHA_ON = 128


def load(asset, name):
    p = KIT / "post" / asset / f"gpt-image-2.5-sunburst-fal_{ELEGIDAS[asset]}" / f"{name}.png"
    return np.array(Image.open(p).convert("RGBA"))


def feet_row(a):
    """la línea de los pies: la primera fila clara bajo el contorno de arriba, en las columnas sin rojo del medio"""
    h, w = a.shape[:2]
    f = a.astype(np.float32)
    lum, al = f[..., :3].mean(2), f[..., 3]
    red = (f[..., 0] - f[..., 1] > 60) & (al > ALPHA_ON)
    rows = []
    for x in range(int(w * 0.15), int(w * 0.85)):
        if red[: h // 3, x].any() or not (al[:, x] >= ALPHA_ON).any():
            continue
        r0 = int(np.argmax(al[:, x] >= ALPHA_ON))
        rows.append(r0 + int(np.argmax(lum[r0:r0 + 80, x] > 150)))
    return int(np.median(rows))


def to_img(a):
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def premul_resize(a, w, h):
    """achica sin halo: premultiplicado"""
    f = a.astype(np.float32)
    f[..., :3] *= f[..., 3:] / 255
    out = np.zeros((h, w, 4), np.float32)
    for c in range(4):
        out[..., c] = np.array(Image.fromarray(f[..., c]).resize((w, h), Image.LANCZOS))
    out = out.clip(0, 255)
    rgb = np.where(out[..., 3:] > 0, out[..., :3] * 255 / np.maximum(out[..., 3:], 1e-3), 0)
    return np.concatenate([rgb.clip(0, 255), out[..., 3:]], 2).astype(np.uint8)


def place(a, k, feet_post=None, feet_to=None, canvas_h=None, width=None, bottom=False):
    """escala a k (el ancho, a `width` si se da) y la pone en un lienzo de canvas_h: con los pies en feet_to o apoyada
    abajo. Devuelve la imagen y la fila de los pies en el resultado"""
    if feet_post is not None and feet_to is not None:
        pad = int(round(feet_to / k - feet_post))
        a = np.concatenate([np.zeros((pad,) + a.shape[1:], np.uint8), a]) if pad > 0 else a[-pad:]
        feet_post += pad
    w = width or max(1, round(a.shape[1] * k))
    h = max(1, round(a.shape[0] * k))
    r = premul_resize(a, w, h)
    if canvas_h is None:
        return r, (round(feet_post * k) if feet_post is not None else None)
    c = np.zeros((canvas_h, w, 4), np.uint8)
    if bottom:
        hh = min(h, canvas_h)
        c[canvas_h - hh:] = r[h - hh:]
    else:
        hh = min(h, canvas_h)
        c[:hh] = r[:hh]
    return c, (feet_to if feet_post is not None else None)


def flat_runs(a, lo=0.12, hi=0.88, thr=0.6, min_len=10):
    f = a.astype(np.float32)
    p = np.concatenate([f[..., :3] * f[..., 3:] / 255, f[..., 3:]], 2)
    d = np.abs(np.diff(p, axis=1)).mean((0, 2))
    w, runs, x = a.shape[1], [], 0
    while x < len(d):
        if d[x] < thr:
            x0 = x
            while x < len(d) and d[x] < thr:
                x += 1
            if x - x0 >= min_len and x0 >= lo * w and x <= hi * w:
                runs.append((x0, x))
        x += 1
    return runs


def fit_width(a, target):
    """lleva el ancho a `target` sacando o duplicando columnas del medio de los tramos lisos, repartido por largo"""
    runs = flat_runs(a)
    delta = target - a.shape[1]
    if not delta or not runs:
        return a, []
    total = sum(x1 - x0 for x0, x1 in runs)
    if delta < 0 and -delta > 0.8 * total:
        raise ValueError(f"no alcanzan los tramos lisos: {total} px para sacar {-delta}")
    share = [round(delta * (x1 - x0) / total) for x0, x1 in runs]
    share[-1] += delta - sum(share)
    cols = list(range(a.shape[1]))
    for (x0, x1), n in sorted(zip(runs, share), reverse=True):   # de derecha a izquierda, así los índices valen
        c = (x0 + x1) // 2
        if n < 0:
            del cols[c + n // 2: c + n // 2 - n]
        elif n > 0:
            cols[c:c] = [c] * n
    return a[:, cols], list(zip(runs, share))


def haze(a, color, t):
    f = a.astype(np.float32)
    f[..., :3] = f[..., :3] * (1 - t) + np.array(color, np.float32) * t
    return f.clip(0, 255).astype(np.uint8)


def despeck(a):
    """la mota blanca de la torre (deco hoja 1): cada píxel casi blanco toma el color mediano de su vecindad no blanca"""
    f = a.copy()
    white = (a[..., :3].min(2) > 235) & (a[..., 3] > 200)
    ys, xs = np.nonzero(white)
    for y, x in zip(ys, xs):
        y0, y1, x0, x1 = max(0, y - 12), y + 13, max(0, x - 12), x + 13
        win = a[y0:y1, x0:x1].reshape(-1, 4)
        ok = win[(win[:, :3].min(1) <= 235) & (win[:, 3] > 200)]
        if len(ok):
            f[y, x] = np.median(ok, 0)
    return f, int(white.sum())


def match_edges(img, ref, sides, fade=48):
    """corrige el color de los bordes (l, r) hacia `ref` (un color por fila, RGBA), en lo opaco y desvaneciéndose
    hacia adentro; los ruidos de una fila se suavizan con sus vecinas"""
    f = img.astype(np.float32)
    w = f.shape[1]
    for s in sides:
        edge = f[:, :3].mean(1) if s == "l" else f[:, -3:].mean(1)
        d = ref[:, :3] - edge[:, :3]
        d *= ((ref[:, 3:] > 200) & (edge[:, 3:] > 200))
        d = np.stack([np.convolve(d[:, c], np.ones(3) / 3, mode="same") for c in range(3)], 1)
        ramp = np.clip(1 - np.arange(w) / fade, 0, 1)
        if s == "r":
            ramp = ramp[::-1]
        f[..., :3] += d[:, None, :] * ramp[None, :, None] * (f[..., 3:] > 0)
    return f.clip(0, 255).astype(np.uint8)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    OUT_FONDO.mkdir(parents=True, exist_ok=True)
    med, out = {}, {}

    # --- pasarela ---------------------------------------------------------------------------------------------
    names = ["pasarela_punta_izq", "pasarela_medio_a", "pasarela_medio_b", "pasarela_punta_der"]
    src = {n: load("pasarela", n) for n in names}
    fr = {n: feet_row(src[n]) for n in names}
    full = [n for n in names if src[n].shape[0] > 300]
    k = 184 / np.median([src[n].shape[0] - fr[n] for n in full])
    for n in names:
        a, cut = src[n], None
        if "punta" in n:   # cortar en la losa lisa, 4 px del juego después de la zapata
            al = a[..., 3] >= ALPHA_ON
            legs = al[fr[n] + int(0.45 * (a.shape[0] - fr[n])):]
            xs = np.nonzero(legs.any(0))[0]
            m = int(round(4 / k))
            if n.endswith("izq"):
                cut = min(a.shape[1], xs.max() + 1 + m)
                a = a[:, :cut]
            else:
                cut = max(0, xs.min() - m)
                a = a[:, cut:]
        width = 256 if "medio" in n else None
        img, f = place(a, k, fr[n], 16, 200, width=width)
        out[n] = img
        med[n] = {"w": img.shape[1], "h": 200, "pies": 16, "escala": round(k, 5), "hoja": ELEGIDAS["pasarela"],
                  **({"corte_post_px": int(cut)} if cut is not None else {})}
    # las uniones: las filas caen iguales en los cuatro tramos, pero el tono del borde difiere de 2 a 5 niveles. El
    # borde de cada tramo se lleva al del medio a (que empalma consigo mismo) con una corrección por fila que se
    # desvanece en 48 px
    ref = (out["pasarela_medio_a"][:, :3].astype(np.float32).mean(1) + out["pasarela_medio_a"][:, -3:].astype(np.float32).mean(1)) / 2
    for n, sides in (("pasarela_medio_b", "lr"), ("pasarela_punta_izq", "r"), ("pasarela_punta_der", "l"),
                     ("pasarela_medio_a", "lr")):
        out[n] = match_edges(out[n], ref, sides)

    # --- columnas ---------------------------------------------------------------------------------------------
    names = ["columna_angosta", "columna_ancha", "bloque", "pared", "guia_ascensor"]
    walk = {"columna_ancha", "bloque", "pared"}
    src = {n: load("columnas", n) for n in names}
    fr = {n: feet_row(src[n]) for n in walk}
    ks = {n: 184 / (src[n].shape[0] - fr[n]) for n in walk}
    kmed = float(np.median(list(ks.values())))
    for n in names:
        if n in walk:
            img, f = place(src[n], ks[n], fr[n], 16, 200)
            med[n] = {"w": img.shape[1], "h": 200, "pies": 16, "escala": round(ks[n], 5)}
        else:
            img, f = place(src[n], kmed, canvas_h=200, bottom=True)
            med[n] = {"w": img.shape[1], "h": 200, "pies": None, "escala": round(kmed, 5)}
        med[n]["hoja"] = ELEGIDAS["columnas"]
        out[n] = img

    # --- flotantes --------------------------------------------------------------------------------------------
    names = {"flotante_200": 200, "flotante_300": 300, "flotante_450": 450, "ascensor": None}
    src = {n: load("flotantes", n) for n in names}
    fr = {n: feet_row(src[n]) for n in names}
    k = 72 / np.median([src[n].shape[0] - fr[n] for n in names if n != "ascensor"])
    for n, target in names.items():
        a, cambios = src[n], []
        if target:
            a, cambios = fit_width(a, int(round(target / k)))
        h = 80 if n != "ascensor" else int(round(8 + (a.shape[0] - fr[n]) * k))
        img, f = place(a, k, fr[n], 8, h, width=target)
        out[n] = img
        med[n] = {"w": img.shape[1], "h": h, "pies": 8, "escala": round(k, 5), "hoja": ELEGIDAS["flotantes"],
                  "ancho_sin_ajuste": round(src[n].shape[1] * k), **({"columnas_post": cambios} if cambios else {})}

    # --- deco y caños -----------------------------------------------------------------------------------------
    k = 600 / load("deco", "deco_torre").shape[0]
    for n in ("deco_tanque", "deco_chimenea", "deco_torre"):
        a = load("deco", n)
        motas = 0
        if n == "deco_torre":
            a, motas = despeck(a)
        img, _ = place(haze(a, *BRUMA), k)
        out[n] = img
        med[n] = {"w": img.shape[1], "h": img.shape[0], "pies": None, "escala": round(k, 5), "hoja": ELEGIDAS["deco"],
                  "bruma": BRUMA[1], **({"motas_borradas": motas} if motas else {})}
    h_ = load("canos", "deco_cano_h"); v_ = load("canos", "deco_cano_v"); c_ = load("canos", "deco_codo")
    img, _ = place(haze(h_, *BRUMA), 48 / h_.shape[0], width=256); img = img[:48] if img.shape[0] > 48 else img
    out["deco_cano_h"] = img
    kv = 48 / v_.shape[1]
    vv = premul_resize(haze(v_, *BRUMA), 48, 256)
    out["deco_cano_v"] = vv
    kc = 2 * 48 / (h_.shape[0] + v_.shape[1])
    out["deco_codo"], _ = place(haze(c_, *BRUMA), kc)
    for n, kk in (("deco_cano_h", 48 / h_.shape[0]), ("deco_cano_v", kv), ("deco_codo", kc)):
        med[n] = {"w": out[n].shape[1], "h": out[n].shape[0], "pies": None, "escala": round(kk, 5),
                  "hoja": ELEGIDAS["canos"], "bruma": BRUMA[1],
                  **({"se_repite": "x"} if n == "deco_cano_h" else {"se_repite": "y"} if n == "deco_cano_v" else {})}

    for n, a in out.items():
        to_img(a).save(OUT / f"{n}.png", optimize=True)
    (OUT / "medidas.json").write_text(json.dumps(med, indent=1, ensure_ascii=False) + "\n")

    # --- el fondo: 2516 × 1404 → 2496 × 1404, una fila para arriba (pies del piso de 1265 a 1264) -----------------
    f = Image.open(FONDOS / "post/abierta" / f"nano-banana-2.1_{FONDO}.png").convert("RGB")
    a = np.array(f)
    a = np.concatenate([a[1:], a[-1:]])[:, 10:2506]
    Image.fromarray(a).save(OUT_FONDO / f"abierta_{FONDO}.webp", quality=88, method=6)
    for n, m in med.items():
        print(f"{n:20s} {m['w']:4d} × {m['h']:3d}  pies {m['pies']}  k {m['escala']}")
    print("fondo", a.shape[1], "×", a.shape[0], (OUT_FONDO / f"abierta_{FONDO}.webp").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()


# --- revisión ---------------------------------------------------------------------------------------------------
def revision():
    """hojas para revisar la entrega: los tramos de pasarela armados y repetidos, sobre verde (x2) y sobre el fondo;
    todas las piezas con el personaje; los caños repetidos; y una arena de prueba armada encima del fondo"""
    F = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 14)
    P = {p.stem: Image.open(p).convert("RGBA") for p in OUT.glob("*.png") if not p.stem.startswith("revision")}
    fondo = Image.open(OUT_FONDO / f"abierta_{FONDO}.webp").convert("RGBA")
    ch = None
    for page in sorted((ROOT / "characters/lowpoly/out").glob("lowpoly_0.5x-*.json")):
        fr = json.loads(page.read_text())["frames"].get("idle_combat/0000")
        if fr:
            f = fr["frame"]
            im = Image.open(page.with_suffix(".png")).convert("RGBA").crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))
            ch = im.resize((round(im.width * 0.8), round(im.height * 0.8)), Image.LANCZOS)
            pivot_y = round((fr["pivot"]["y"] * fr["sourceSize"]["h"] - fr["spriteSourceSize"]["y"]) * 0.8)

    def chain(seq):
        w = sum(P[n].width for n in seq)
        c = Image.new("RGBA", (w, 200), (0, 0, 0, 0)); x = 0
        for n in seq:
            c.alpha_composite(P[n], (x, 0)); x += P[n].width
        return c

    def on(bg, im, zoom=1):
        if bg == "fondo":
            c = fondo.crop((200, 1264 - 16 - 260, 200 + im.width + 40, 1264 - 16 + im.height - 260 + 280)).copy()
            c.alpha_composite(im, (20, 260))
        else:
            c = Image.new("RGBA", (im.width + 40, im.height + 40), bg + (255,)); c.alpha_composite(im, (20, 20))
        c = c.convert("RGB")
        return c.resize((c.width * zoom, c.height * zoom), Image.NEAREST) if zoom > 1 else c

    def stack(items, path):
        W = max(i.width for _, i in items)
        out = Image.new("RGB", (W, sum(i.height + 22 for _, i in items)), (255, 255, 255))
        d, y = ImageDraw.Draw(out), 0
        for lab, i in items:
            d.text((6, y + 3), lab, fill=(0, 0, 0), font=F); out.paste(i, (0, y + 22)); y += i.height + 22
        out.save(path, optimize=True)

    a, b, L, R = "pasarela_medio_a", "pasarela_medio_b", "pasarela_punta_izq", "pasarela_punta_der"
    seqs = [[L, a, R], [L, a, a, a, a, R], [L, b, b, b, b, R], [L, a, b, a, b, a, R]]
    items = []
    for s in seqs:
        lab = " + ".join(n.replace("pasarela_", "") for n in s) + f" · {sum(P[n].width for n in s)} px"
        items.append((lab + " · sobre verde, x2", on((0, 177, 64), chain(s), 2)))
    stack(items, OUT / "revision_pasarela.png")

    # la arena de prueba: el fondo con pasarelas, columnas, flotantes y el personaje parado en cada piso
    arena = fondo.copy()
    def put(n, x, feet_y):
        im = P[n]; m = json.loads((OUT / "medidas.json").read_text())[n]
        arena.alpha_composite(im, (x, feet_y - (m["pies"] if m["pies"] is not None else im.height)))
    def walkway(x, y, mids):
        for n in [L] + mids + [R]:
            put(n, x, y); x += P[n].width
        return x
    for n, x, y in (("deco_torre", 520, 1264), ("deco_chimenea", 1960, 1264), ("deco_tanque", 860, 1264)):
        put(n, x, y)
    walkway(330, 1064, [a, b])                      # piso 1, izquierda: 113 + 512 + 113
    walkway(2496 - 330 - 738, 1064, [b, a])
    walkway(900, 864, [a, b, a])                    # piso 2, al medio
    put("columna_ancha", 400, 864); put("columna_ancha", 2496 - 400 - P["columna_ancha"].width, 864)
    put("bloque", 1183, 1264)
    put("flotante_300", 430, 670); put("flotante_300", 2496 - 430 - 300, 670)
    put("flotante_450", 1023, 520); put("ascensor", 1128, 1000)
    put("flotante_200", 330, 470); put("flotante_200", 2496 - 330 - 200, 470)
    for x, y in ((700, 1264), (520, 1064), (1300, 864), (560, 670), (1250, 520), (1700, 1064)):
        arena.alpha_composite(ch, (x - ch.width // 2, y - pivot_y))
    d = ImageDraw.Draw(arena)
    d.rectangle((1876, 0, 2495, 194), outline=(255, 255, 0), width=3)      # el HUD
    arena.convert("RGB").save(OUT / "revision_arena.jpg", quality=85)

    # todas las piezas a 1:1 sobre el fondo, con el personaje, y los caños repetidos
    row1 = [L, a, b, R, "columna_angosta", "columna_ancha", "bloque", "pared", "guia_ascensor"]
    row2 = ["flotante_200", "flotante_300", "flotante_450", "ascensor"]
    W = 2496
    c = fondo.crop((0, 1264 - 900, W, 1264 + 60)).copy()
    x = 20; c.alpha_composite(ch, (x, 900 - pivot_y)); x += ch.width + 20
    for n in row1:
        c.alpha_composite(P[n], (x, 900 - 200)); x += P[n].width + 20
    x1, x = x, 20
    for n in row2:
        c.alpha_composite(P[n], (x, 520)); x += P[n].width + 30
    x = max(x, x1) + 10
    for n in ("deco_tanque", "deco_chimenea", "deco_torre"):
        c.alpha_composite(P[n], (x, 900 - P[n].height)); x += P[n].width + 20
    for i in range(4):
        c.alpha_composite(P["deco_cano_h"], (20 + 256 * i, 120))
    c.alpha_composite(P["deco_codo"], (20 + 1024, 120 + 48 - P["deco_codo"].height + P["deco_codo"].height - 48))
    for i in range(3):
        c.alpha_composite(P["deco_cano_v"], (20 + 1024 + P["deco_codo"].width - 48, 120 + P["deco_codo"].height + 256 * i))
    c.convert("RGB").save(OUT / "revision_piezas.jpg", quality=85)


if __name__ == "__main__":
    revision()
