"""El arma en run_gun, cuadro por cuadro: dónde salta y por qué (revisión del 2026-10-18, "como que salta raro el arma").

Mide en el atlas (1x, pasado a px de juego: × 0,5 × 0,8) el cuerpo del arma (template matching del tramo con la
franja roja, sin la tapa de la boca), la punta (lo más adelante en las filas del arma) y el casco, y compara la tapa de
cada cuadro con la del cuadro 0 (corrida lo que se movió el cuerpo); los cuadros con la tapa mal están en TAPA,
mirados a ojo. Arma las hojas para Pablo:

    revision/para_pablo/arma_correr_tabla.png    el gráfico y la tabla
    revision/para_pablo/arma_correr_detalle.png  el arma agrandada sobre verde, en orden de loop (13 → 0 al final)
    revision/para_pablo/arma_correr_juego.png    el personaje entero a tamaño de juego, sobre verde y oscuro
    revision/para_pablo/arma_correr_causa.png    el mismo cuadro en el video de Kling, sin rayos, apagado y en el atlas

Con --out OTRO_OUT (y --sufijo), mide otra corrida del atlas (p. ej. la propuesta en work_revisar/).

Uso (desde la raíz del repo): uv run --project pipeline python characters/lowpoly/arma_correr.py
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import revisar as rv  # noqa: E402
from spritepipe import imgio  # noqa: E402

DEST = HERE / "revision" / "para_pablo"
GAME = 0.4                 # px de 1x → px de juego (0,5× × 0,8)
CLIPS = {"Kling": HERE / "clips" / "correr" / "kling-o3-std_correr_a_2.mp4",
         "sin rayos": HERE / "clips" / "correr" / "kling-o3-std_correr_a_2_sin_rayos.mp4",
         "apagado": HERE / "clips" / "apagado" / "correr_a_2.mp4"}


def feat(c: np.ndarray) -> np.ndarray:
    a = c[..., 3:4].astype(np.float32) / 255.0
    lum = (c[..., :3].astype(np.float32) @ np.array([0.3, 0.59, 0.11], np.float32)) / 255.0
    return np.ascontiguousarray(np.dstack([a[..., 0], lum * a[..., 0]]), np.float32)


def tip(c: np.ndarray, band: tuple[int, int]) -> tuple[int, float]:
    a = c[..., 3] > 128
    a[:band[0]] = a[band[1]:] = False
    ys, xs = np.nonzero(a)
    x = xs.max()
    return int(x), float(ys[xs >= x - 3].mean())


def helmet(c: np.ndarray) -> tuple[float, float]:
    a = c[..., 3] > 128
    hsv = cv2.cvtColor(c[..., :3], cv2.COLOR_RGB2HSV)
    top = np.nonzero(a.any(1))[0].min()
    w = a & (hsv[..., 1] < 45) & (hsv[..., 2] > 170)
    w[top + 120:] = False
    ys, xs = np.nonzero(w)
    return float(xs.mean()), float(ys.mean())


def medir(out: Path) -> tuple[list[dict], list[np.ndarray], dict]:
    cs = rv.cells(out, "1x", "run_gun")
    j = json.loads((out / "lowpoly.json").read_text(encoding="utf-8"))["variants"]["1x"]
    piv = j["pivot_px"]
    nat = rv.provenance(out, "run_gun")["timing"]["native_indices"]
    top0 = np.nonzero((cs[0][..., 3] > 128).any(1))[0].min()
    band = (top0 + 110, top0 + 190)
    tx, ty = tip(cs[0], band)
    # el cuerpo del arma (la franja roja y el gris de atrás de la tapa), sin la tapa: 30–80 px atrás de la punta
    bx0, bx1, by0, by1 = tx - 80, tx - 30, int(ty) - 24, int(ty) + 20
    tpl = feat(cs[0])[by0:by1, bx0:bx1]
    R = 30
    hx0, hy0 = helmet(cs[0])
    rows = []
    for i, c in enumerate(cs):
        res = cv2.matchTemplate(feat(c)[by0 - R:by1 + R, bx0 - R:bx1 + R], tpl, cv2.TM_SQDIFF_NORMED)
        err, _, (mx, my), _ = cv2.minMaxLoc(res)
        dx, dy = mx - R, my - R
        x, y = tip(c, (band[0] + dy - 10, band[1] + dy + 10))
        hx, hy = helmet(c)
        rows.append({"cuadro": i, "nativo": nat[i], "cuerpo": (dx, dy), "casco": (hx - hx0, hy - hy0),
                     "arma_casco": (dx - (hx - hx0), dy - (hy - hy0)), "largo": x - (tx + dx), "baja": y - (ty + dy),
                     "punta": ((x - piv["x"]) * GAME, (piv["y"] - y) * GAME), "err": err})
    geo = {"tip": (tx, ty), "piv": piv}
    return rows, cs, geo


# la tapa de la boca, mirada cuadro por cuadro sobre verde (las medidas de forma se confunden con el giro del arma, que
# en 4 y 11 apunta ~8° para abajo y está bien): los cuadros donde no es la tapa del arma
TAPA = {2: "cortada en recto, con borde lila", 3: "corrida abajo y adelante, con un escalón", 5: "cuadrada, con borde lila",
        6: "una esquina lila arriba", 9: "borde lila adelante", 10: "corrida abajo y adelante, con un escalón",
        12: "cortada, con borde lila", 13: "una esquina lila arriba"}


def malo(r: dict) -> bool:
    return r["cuadro"] in TAPA


def tabla(rows: list[dict], dest: Path, titulo: str) -> None:
    f1, f2, ft = rv.font(15, True), rv.font(14), rv.font(22, True)
    W, H = 1500, 900
    s = Image.new("RGB", (W, H), (250, 250, 250))
    d = ImageDraw.Draw(s)
    d.text((16, 12), titulo, fill=(0, 0, 0), font=ft)
    d.text((16, 42), "En rojo los cuadros donde la tapa de la boca no es la del arma (el gris pegado de más, corrido o cortado). "
           "Todo en px de juego (0,5× × 0,8).", fill=(60, 60, 60), font=f2)
    n = len(rows)
    gx0, gx1 = 90, W - 40
    xs = [gx0 + (gx1 - gx0) * i / n for i in range(n + 1)]   # el loop: 0..13 y el 0 de nuevo
    seq = rows + [rows[0]]

    def graf(y0: int, h: int, series: list[tuple[str, list[float], tuple[int, int, int]]], lo: float, hi: float, t: str):
        d.text((16, y0 - 22), t, fill=(0, 0, 0), font=f1)
        d.rectangle((gx0, y0, gx1, y0 + h), outline=(200, 200, 200))
        for v in np.arange(np.ceil(lo), hi + 0.01, 1 if hi - lo <= 8 else 2):
            y = y0 + h - (v - lo) / (hi - lo) * h
            d.line((gx0, y, gx1, y), fill=(232, 232, 232))
            d.text((gx0 - 34, y - 8), f"{v:+.0f}", fill=(120, 120, 120), font=f2)
        for k, (name, vals, col) in enumerate(series):
            pts = [(xs[i], y0 + h - (v - lo) / (hi - lo) * h) for i, v in enumerate(vals)]
            d.line(pts, fill=col, width=3)
            for i, p in enumerate(pts):
                bad = malo(seq[i])
                d.ellipse((p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5), fill=(220, 0, 0) if bad else col)
            d.text((gx1 - 300 + 150 * k, y0 + 4), name, fill=col, font=f1)
        for i, r in enumerate(seq):
            d.text((xs[i] - 6, y0 + h + 4), str(r["cuadro"]), fill=(220, 0, 0) if malo(r) else (0, 0, 0), font=f1)

    graf(100, 170, [("adelante", [r["arma_casco"][0] * GAME for r in seq], (30, 90, 200)),
                    ("arriba", [-r["arma_casco"][1] * GAME for r in seq], (0, 150, 80))], -4, 4,
         "1. El cuerpo del arma contra el casco (lo que se mueve con el brazo al correr): suave, ±2 px")
    graf(330, 170, [("adelante", [r["largo"] * GAME for r in seq], (130, 60, 170)),
                    ("arriba", [-r["baja"] * GAME for r in seq], (200, 120, 0))], -5, 3,
         "2. La punta (lo que el juego mide como boca) contra el cuerpo del arma: con la tapa bien sería plana (4 y 11 apuntan abajo)")
    d.text((16, 560), "3. La tapa de la boca, mirada sobre verde:", fill=(0, 0, 0), font=f1)
    for k, (i, t) in enumerate(TAPA.items()):
        d.text((40 + 480 * (k // 4), 588 + 24 * (k % 4)), f"cuadro {i} (n{rows[i]['nativo']}): {t}", fill=(220, 0, 0), font=f2)
    d.text((40, 690), "Los demás (0, 1, 4, 7, 8, 11) tienen la tapa del arma; en 4 y 11 el arma apunta ~8° para abajo "
           "(el brazo al correr, de Kling: está bien).", fill=(30, 30, 30), font=f2)
    y = 790
    d.text((16, y), "La tabla (px de juego; la punta, desde los pies del personaje)", fill=(0, 0, 0), font=f1)
    # la tabla, en dos columnas debajo del encabezado
    s2 = Image.new("RGB", (W, H + 140), (250, 250, 250))
    s2.paste(s, (0, 0))
    d2 = ImageDraw.Draw(s2)
    for k, r in enumerate(rows):
        cx, cy = 16 + 740 * (k // 7), y + 22 + 22 * (k % 7)
        line = (f"{r['cuadro']:2d}  n{r['nativo']:2d}   arma-casco {r['arma_casco'][0] * GAME:+4.1f}, {-r['arma_casco'][1] * GAME:+4.1f}"
                f"   punta {r['punta'][0]:4.1f}, {r['punta'][1]:4.1f}   " + TAPA.get(r["cuadro"], "tapa bien"))
        d2.text((cx, cy), line, fill=(220, 0, 0) if malo(r) else (30, 30, 30), font=f2)
    dest.parent.mkdir(parents=True, exist_ok=True)
    s2.save(dest)


def detalle(rows: list[dict], cs: list[np.ndarray], geo: dict, dest: Path, titulo: str) -> None:
    tx, ty = geo["tip"]
    x0, y0, w, h = tx - 95, int(ty) - 48, 125, 80
    k = 3
    f1, f2, ft = rv.font(16, True), rv.font(14), rv.font(22, True)
    order = list(range(len(cs))) + [0]
    cols = 8
    tw, th = w * k, h * k
    s = Image.new("RGB", (16 + cols * (tw + 8), 70 + ((len(order) + cols - 1) // cols) * (th + 44)), (245, 245, 245))
    d = ImageDraw.Draw(s)
    d.text((16, 10), titulo, fill=(0, 0, 0), font=ft)
    d.text((16, 40), "Ventana fija de la celda (se ve cómo se mueve el arma), ×3, en orden de loop: después del 13 vuelve el 0. "
           "Rojo: la tapa de la boca no es la del arma (ver abajo de cada uno).", fill=(60, 60, 60), font=f2)
    for j, i in enumerate(order):
        c = cs[i]
        im = Image.new("RGBA", (c.shape[1] + 2 * w, c.shape[0] + 2 * h), (*rv.GREEN, 255))   # con margen: la ventana
        im.alpha_composite(Image.fromarray(c, "RGBA"), (w, h))                                  # puede salir de la celda
        t = im.crop((x0 + w, y0 + h, x0 + 2 * w, y0 + 2 * h)).resize((tw, th), Image.NEAREST).convert("RGB")
        x, y = 16 + (j % cols) * (tw + 8), 70 + (j // cols) * (th + 44)
        s.paste(t, (x, y))
        r = rows[i]
        bad = malo(r)
        if bad:
            ImageDraw.Draw(s).rectangle((x - 3, y - 3, x + tw + 2, y + th + 2), outline=(220, 0, 0), width=3)
        d.text((x, y + th + 4), f"cuadro {i} · n{r['nativo']}" + ("   (loop: vuelve al 0)" if j == len(cs) else ""),
               fill=(220, 0, 0) if bad else (0, 0, 0), font=f1)
        d.text((x, y + th + 22), TAPA.get(i, "bien"), fill=(60, 60, 60), font=f2)
    s.save(dest)


def juego(rows: list[dict], out: Path, dest: Path, titulo: str) -> None:
    cs = rv.cells(out, "0.5x", "run_gun")
    box = rv.union_box(cs, 3)
    k = rv.GAME_K * 1.5    # retina × 1,5, para que se vea el arma
    tw, th = round((box[2] - box[0]) * k), round((box[3] - box[1]) * k)
    order = list(range(len(cs))) + [0]
    f1, ft = rv.font(15, True), rv.font(20, True)
    s = Image.new("RGB", (16 + len(order) * (tw + 6), 50 + 2 * th + 34), rv.DARK)
    d = ImageDraw.Draw(s)
    d.text((16, 12), titulo, fill=(240, 240, 240), font=ft)
    for j, i in enumerate(order):
        c = cs[i]
        x = 16 + j * (tw + 6)
        for kk, bg in enumerate((rv.GREEN, rv.DARK)):
            im = Image.new("RGBA", (c.shape[1], c.shape[0]), (*bg, 255))
            im.alpha_composite(Image.fromarray(c, "RGBA"))
            s.paste(im.crop(box).resize((tw, th), Image.BILINEAR).convert("RGB"), (x, 46 + kk * th))
        d.text((x, 50 + 2 * th), f"{i}", fill=(255, 90, 90) if malo(rows[i]) else (240, 240, 240), font=f1)
    s.save(dest)


def causa(rows: list[dict], dest: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        frames = {}
        for name, clip in CLIPS.items():
            info = imgio.probe(clip)
            dd = Path(tmp) / name.replace(" ", "_")
            imgio.extract(clip, dd, info, None if info.get("color_space") else "bt601")
            frames[name] = imgio.frames(dd)
        muzzle = json.loads((HERE / "clips" / "correr" / "kling-o3-std_correr_a_2_sin_rayos.muzzle.json")
                            .read_text(encoding="utf-8"))["muzzle"]
        sel = [r for r in rows if r["cuadro"] in (0, 2, 3, 5, 10)]
        f1, f2, ft = rv.font(16, True), rv.font(14), rv.font(22, True)
        tw, th = 300, 190
        s = Image.new("RGB", (16 + 3 * (tw + 8), 96 + len(sel) * (th + 30)), (245, 245, 245))
        d = ImageDraw.Draw(s)
        d.text((16, 10), "Por qué: el gris de apagar_arma.py sobre el halo del cañón prendido", fill=(0, 0, 0), font=ft)
        d.text((16, 40), "Kling prende el disco cian y dispara cada ~7 cuadros. Borrar los rayos deja el halo cian alrededor de "
               "la boca; al apagar el disco,", fill=(60, 60, 60), font=f2)
        d.text((16, 58), "todo lo cian (disco y halo) se pinta del gris del arma: la tapa crece y queda cortada en rectángulo "
               "donde terminaba el borrado del rayo.", fill=(60, 60, 60), font=f2)
        for k, name in enumerate(CLIPS):
            d.text((16 + k * (tw + 8), 78), name, fill=(0, 0, 0), font=f1)
        for j, r in enumerate(sel):
            n = r["nativo"]
            mx, my = muzzle[n]["x"], int(muzzle[n]["y"])
            for k, name in enumerate(CLIPS):
                t = Image.open(frames[name][n]).convert("RGB").crop((mx - 130, my - 55, mx + 60, my + 65))
                s.paste(t.resize((tw, th), Image.NEAREST), (16 + k * (tw + 8), 96 + j * (th + 30)))
            d.text((16, 96 + j * (th + 30) + th + 4), f"cuadro {r['cuadro']} · nativo {n}" + ("  (bien)" if not malo(r) else ""),
                   fill=(220, 0, 0) if malo(r) else (0, 0, 0), font=f1)
        s.save(dest)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=HERE / "out")
    ap.add_argument("--sufijo", default="")
    ap.add_argument("--titulo", default="run_gun hoy")
    ap.add_argument("--tapas-bien", action="store_true", help="la corrida no tiene los cuadros de TAPA (la propuesta)")
    args = ap.parse_args()
    if args.tapas_bien:
        TAPA.clear()
    rows, cs, geo = medir(args.out)
    sf = args.sufijo
    tabla(rows, DEST / f"arma_correr_tabla{sf}.png", f"El arma en run_gun ({args.titulo}): cuadro por cuadro")
    detalle(rows, cs, geo, DEST / f"arma_correr_detalle{sf}.png", f"El arma en run_gun ({args.titulo}), sobre verde")
    juego(rows, args.out, DEST / f"arma_correr_juego{sf}.png", f"run_gun ({args.titulo}) a tamaño de juego ×1,5, en orden de loop")
    if not sf:
        causa(rows, DEST / "arma_correr_causa.png")
    for r in rows:
        print(f"{r['cuadro']:2d} n{r['nativo']:2d} arma-casco {r['arma_casco'][0] * GAME:+5.1f} {-r['arma_casco'][1] * GAME:+5.1f}"
              f"  punta {r['punta'][0]:5.1f} {r['punta'][1]:5.1f}  " + TAPA.get(r["cuadro"], "bien"))


if __name__ == "__main__":
    main()
