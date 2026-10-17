"""Arma un juego de prueba a partir del atlas que sacó spritepipe.

uso (desde la raíz del repo):
    uv run --project pipeline python prototypes/build.py ranger
    uv run --project pipeline python prototypes/build.py comando

Lee characters/<personaje>/out/, mide por frame la boca del arma, la subida y el punto más alto
(la mano en el colgado), mete esos datos en prototypes/<personaje>/src.html y deja la página y el
atlas en prototypes/<personaje>/dist/. Si el personaje tiene fondos en BACKGROUNDS, los achica a dist/bg/ y
mete sus medidas en la página. Esa carpeta es la que se publica como artifact.
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
EXPORT = 2      # px de las imágenes del fondo por px del juego (el canvas dibuja hasta a 2x)

# fondos de spritepipe gen-images (backgrounds/<set>/post/): la opción elegida de cada asset. Las capas de
# parallax llevan el lienzo del modelo al alto de la pantalla (`view_h`) y quedan alineadas abajo; el kit de
# plataformas y los props van a `scale` px del juego por px de la hoja. `deco` es la utilería de otro set: su
# picked.json (ver backgrounds/ranger_props/integrar.md) trae cada pieza con su k, su papel y sus puntos medidos
BACKGROUNDS = {
    "ranger": {
        "set": "ranger_base", "view_h": 540,
        "layers": {"sky": "nano-banana-2.1_3", "far": "nano-banana-2.1_2", "mid": "nano-banana-2.1_1", "near": "nano-banana-2.1_2"},
        "sheets": {"kit": ("platform_kit", "gpt-image-2.5-sunburst-fal_1", 0.2),     # el tope de un bloque, 71 px
                   "props": ("props", "gpt-image-2.5-sunburst-fal_1", 92 / 876)},   # el blanco, al alto del tablero
        "deco": "ranger_props",
    },
}

# efectos de spritepipe gen-images (backgrounds/<set>/post/), elegidos en prototypes/fx_lab: la hoja de cada efecto y su
# tamaño en px del juego con el personaje al 80%. El fogonazo se mide por el ancho medio de sus primeros dibujos; el
# impacto, por el alto medio de los más grandes (los 2)
FX = {
    "ranger": {
        "set": "ranger_fx",
        "muzzle": {"opt": "gpt-image-2.5-sunburst-fal_2", "len": 26, "ref": ("w", ["a1", "a2", "a3"])},
        "impact": {"opt": "gpt-image-2.5-sunburst-fal_1", "len": 50, "ref": ("h", ["a2", "b2"])},
    },
}


def load_atlas(out: Path, name: str, variant: str = "1x") -> tuple[Image.Image, dict]:
    """El atlas de una variante en una sola imagen: si viene en varias páginas, las apila una debajo de la otra y corre
    los cuadros de cada una. Devuelve la imagen y los cuadros ({nombre: datos del JSON de la página})."""
    pages = json.loads((out / f"{name}.json").read_text())["variants"][variant]["atlas"]
    ims = [Image.open(out / p["image"]).convert("RGBA") for p in pages]
    if len(ims) == 1:
        return ims[0], json.loads((out / pages[0]["data"]).read_text())["frames"]
    sheet, frames, y0 = Image.new("RGBA", (max(im.width for im in ims), sum(im.height for im in ims))), {}, 0
    for p, im in zip(pages, ims):
        sheet.paste(im, (0, y0))
        for k, d in json.loads((out / p["data"]).read_text())["frames"].items():
            frames[k] = {**d, "frame": {**d["frame"], "y": d["frame"]["y"] + y0}}
        y0 += im.height
    return sheet, frames


def measure(out: Path, name: str, variant: str = "1x", atlas: tuple[Image.Image, dict] | None = None) -> dict:
    """Las medidas por cuadro de una variante (la boca está calibrada para un cuerpo de 128 px). `atlas`: lo que devolvió
    load_atlas, si ya se cargó."""
    sheet, frames = atlas or load_atlas(out, name, variant)
    at = {"frames": frames}
    idx = json.loads((out / f"{name}.json").read_text())["variants"][variant]
    rgba = np.asarray(sheet).astype(np.int16)
    img = rgba[..., 3]
    cw, ch = idx["canvas"]["w"], idx["canvas"]["h"]
    px, py = idx["pivot_px"]["x"], idx["pivot_px"]["y"]
    anims = {}
    for an, a in idx["animations"].items():
        frames, glows = [], []
        for f in a["frames"]:
            d = at["frames"][f["name"]]
            F0 = d["frame"]
            reg = rgba[F0["y"]:F0["y"] + F0["h"], F0["x"]:F0["x"] + F0["w"]]
            glows.append(int(((reg[..., 3] > 40) & (reg[..., 1] > 170) & (reg[..., 2] > 180) & (reg[..., 0] < 210)).sum()))
            F, s = d["frame"], d["spriteSourceSize"]
            cell = np.zeros((ch, cw), bool)
            cell[s["y"]:s["y"] + s["h"], s["x"]:s["x"] + s["w"]] = img[F["y"]:F["y"] + F["h"], F["x"]:F["x"] + F["w"]] > 128
            rows = np.where(cell.any(1))[0]
            top, bottom = int(rows.min()), int(rows.max()) + 1
            # boca: la columna opaca más a la derecha en la franja del arma (25-100 px sobre los pies)
            band = cell[max(0, bottom - 100):bottom - 25]
            mx = int(np.where(band.any(0))[0].max())
            my = float(np.where(cell[:, max(0, mx - 2):mx + 1].any(1))[0].mean())
            tx = float(np.where(cell[top:top + 4].any(0))[0].mean())
            # [x, y, w, h del atlas, x, y del trim, boca dx, dy, subida, punto alto dx, dy] relativos al pivot,
            # y al final 1 si el frame trae fogonazo dibujado
            frames.append([F["x"], F["y"], F["w"], F["h"], s["x"], s["y"],
                           round(mx + 1 - px, 1), round(my - py, 1), round(py - bottom, 1),
                           round(tx - px, 1), round(top - py, 1)])
        # fogonazo: el frame donde el cian brillante (lente del arma + destello) pasa del doble de lo normal
        base = float(np.median(glows)) if glows else 0.0
        for fr, g in zip(frames, glows):
            fr.append(1 if g > max(60, 2 * base) else 0)
        anims[an] = {"loop": a["loop"], "ms": a["frames"][0]["duration"], "f": frames}
    return {"cell": [cw, ch], "pivot": [px, py], "anims": anims}


def export_image(src: Path, dst: Path, scale: float) -> None:
    im = Image.open(src).convert("RGBa")       # premultiplicado: que el achique no ensucie los bordes con el fondo
    size = (max(1, round(im.width * scale)), max(1, round(im.height * scale)))
    im = im.resize(size, Image.LANCZOS).convert("RGBA")
    if dst.suffix == ".webp":                  # las capas: el ruido fino del modelo infla el PNG (6,7 MB contra 0,6)
        im.save(dst, quality=92, alpha_quality=100, method=6)
    else:
        im.save(dst, optimize=True)


def export_backgrounds(name: str, dist: Path) -> dict:
    """Achica los fondos elegidos a EXPORT px por px del juego y devuelve sus medidas en px del juego."""
    cfg = BACKGROUNDS[name]
    base, bg = ROOT / "backgrounds" / cfg["set"], dist / "bg"
    bg.mkdir(exist_ok=True)
    data = {"layers": {}}
    for layer, opt in cfg["layers"].items():
        post = json.loads((base / "raw" / layer / f"{opt}.json").read_text())["post"]
        k = cfg["view_h"] / post["source"]["h"]
        f, y0 = post["files"]["image"], post.get("trim", {}).get("image", [0, 0])[1]
        export_image(base / "post" / layer / f["file"], bg / f"{layer}.webp", k * EXPORT)
        data["layers"][layer] = {"src": f"bg/{layer}.webp", "w": round(f["w"] * k, 2), "h": round(f["h"] * k, 2), "y": round(y0 * k, 2)}
    for key, (asset, opt, k) in cfg["sheets"].items():
        post = json.loads((base / "raw" / asset / f"{opt}.json").read_text())["post"]
        data[key] = {}
        for piece, f in post["files"].items():
            export_image(base / "post" / asset / opt / f["file"], bg / f"{piece}.png", k * EXPORT)
            data[key][piece] = {"src": f"bg/{piece}.png", "w": round(f["w"] * k, 2), "h": round(f["h"] * k, 2), "k": round(k, 5)}
    if "deco" in cfg:   # cada pieza ya trae su tamaño en px del juego; los puntos van en px de la hoja (por k)
        dset = ROOT / "backgrounds" / cfg["deco"]
        data["deco"] = {}
        for piece, p in json.loads((dset / "picked.json").read_text())["pieces"].items():
            export_image(dset / p["file"], bg / f"{piece}.png", p["k"] * EXPORT)
            data["deco"][piece] = {key: v for key, v in p.items() if key not in ("file", "sheet", "option")} | {"src": f"bg/{piece}.png"}
    return data


def fx_anchor(a: np.ndarray, where: str) -> tuple[float, float]:
    """El punto que va en la boca (fogonazo: el borde izquierdo) o en el contacto (impacto: el centro del primer
    frame y la punta derecha de los demás), en px de la imagen."""
    ys, xs = np.nonzero(a >= 128)
    if where == "center":
        return float(xs.mean()), float(ys.mean())
    edge = int(xs.min()) if where == "left" else int(xs.max())
    band = max(2, round(0.04 * a.shape[1]))   # las filas de la punta, en el 4% del ancho más cerca del borde
    cols = slice(edge, edge + band) if where == "left" else slice(edge - band + 1, edge + 1)
    return float(edge), float(np.nonzero((a[:, cols] >= 128).any(1))[0].mean())


def export_fx(name: str, dist: Path) -> dict:
    """Achica las piezas elegidas a EXPORT px por px del juego; devuelve su tamaño y su ancla en px del juego."""
    cfg = FX[name]
    post, out = ROOT / "backgrounds" / cfg["set"] / "post", dist / "fx"
    out.mkdir(exist_ok=True)
    data = {}
    for asset in ("muzzle", "impact"):
        c = cfg[asset]
        pieces = {p.stem: Image.open(p).convert("RGBA") for p in sorted((post / asset / c["opt"]).glob("*.png"))}
        axis, ref = c["ref"]
        k = c["len"] / float(np.mean([pieces[r].width if axis == "w" else pieces[r].height for r in ref]))
        data[asset] = {"len": c["len"], "pieces": {}}
        for piece, im in pieces.items():
            a = np.asarray(im).copy()
            a[..., 3][a[..., 3] >= 250] = 255   # GPT Image llega a 254: lo opaco, opaco
            im = Image.fromarray(a, "RGBA").convert("RGBa")   # premultiplicado, como export_image
            im = im.resize((max(1, round(im.width * k * EXPORT)), max(1, round(im.height * k * EXPORT))), Image.LANCZOS).convert("RGBA")
            im.save(out / f"{asset}_{piece}.png", optimize=True)
            where = "left" if asset == "muzzle" else "center" if piece.endswith("1") else "right"
            ax, ay = fx_anchor(np.asarray(im)[..., 3], where)
            data[asset]["pieces"][piece] = {"src": f"fx/{asset}_{piece}.png", "w": round(im.width / EXPORT, 2),
                                            "h": round(im.height / EXPORT, 2), "ax": round(ax / EXPORT, 2),
                                            "ay": round(ay / EXPORT, 2)}
    return data


def main(name: str) -> None:
    proto, out = ROOT / "prototypes" / name, ROOT / "characters" / name / "out"
    data = measure(out, name)
    dist = proto / "dist"
    dist.mkdir(exist_ok=True)
    html = (proto / "src.html").read_text(encoding="utf-8").replace("__SPRITE_DATA__", json.dumps(data, separators=(",", ":")))
    if name in BACKGROUNDS:
        html = html.replace("__BG_DATA__", json.dumps(export_backgrounds(name, dist), separators=(",", ":")))
    if name in FX:
        html = html.replace("__FX_DATA__", json.dumps(export_fx(name, dist), separators=(",", ":")))
    (dist / "index.html").write_text(html, encoding="utf-8")
    shutil.copy(out / f"{name}_1x-0.png", dist / f"{name}_1x-0.png")
    print(f"✓ {dist / 'index.html'}  ({', '.join(f'{k} {len(v['f'])}' for k, v in data['anims'].items())})")


if __name__ == "__main__":
    main(sys.argv[1])
