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
# plataformas y los props van a `scale` px del juego por px de la hoja
BACKGROUNDS = {
    "ranger": {
        "set": "ranger_base", "view_h": 540,
        "layers": {"sky": "nano-banana-2.1_3", "far": "nano-banana-2.1_2", "mid": "nano-banana-2.1_1", "near": "nano-banana-2.1_2"},
        "sheets": {"kit": ("platform_kit", "gpt-image-2.5-sunburst-fal_1", 0.2),     # el tope de un bloque, 71 px
                   "props": ("props", "gpt-image-2.5-sunburst-fal_1", 92 / 876)},   # el blanco, al alto del tablero
    },
}


def measure(out: Path, name: str) -> dict:
    at = json.loads((out / f"{name}_1x-0.json").read_text())
    idx = json.loads((out / f"{name}.json").read_text())["variants"]["1x"]
    rgba = np.asarray(Image.open(out / f"{name}_1x-0.png").convert("RGBA")).astype(np.int16)
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
    return data


def main(name: str) -> None:
    proto, out = ROOT / "prototypes" / name, ROOT / "characters" / name / "out"
    data = measure(out, name)
    dist = proto / "dist"
    dist.mkdir(exist_ok=True)
    html = (proto / "src.html").read_text(encoding="utf-8").replace("__SPRITE_DATA__", json.dumps(data, separators=(",", ":")))
    if name in BACKGROUNDS:
        html = html.replace("__BG_DATA__", json.dumps(export_backgrounds(name, dist), separators=(",", ":")))
    (dist / "index.html").write_text(html, encoding="utf-8")
    shutil.copy(out / f"{name}_1x-0.png", dist / f"{name}_1x-0.png")
    print(f"✓ {dist / 'index.html'}  ({', '.join(f'{k} {len(v['f'])}' for k, v in data['anims'].items())})")


if __name__ == "__main__":
    main(sys.argv[1])
