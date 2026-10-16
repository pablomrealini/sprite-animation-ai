"""Arma kit.html: el kit industrial de este set a escala del juego, armado en un tramo de nivel de prueba con el ranger,
y cada hoja con sus opciones (las piezas que se repiten, repetidas) para elegir.

    uv run --project pipeline python backgrounds/ranger_industrial/build_page.py

Lee lo que dejó `spritepipe gen-images` (raw/<hoja>/<opción>.json y post/<hoja>/<opción>/...). Cada hoja tiene su
escala: la pieza ancla va a la medida de ANCHOR en px del juego (plan.md, sección 3) y las demás quedan a la escala
en que las dibujó el modelo, así el contorno tiene el mismo grosor en toda la hoja. La página referencia las
imágenes con rutas relativas: se abre con cualquier servidor estático en la raíz del repo.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
PIECES_MODEL, LAYERS_MODEL = "gpt-image-2.5-sunburst-fal", "nano-banana-2.1"
LAYERS = ("sky", "far", "mid", "mid2", "near")   # mid2: la tanda nueva de mid (gen.toml)

# pieza ancla de cada hoja: (pieza, eje, medida en px del juego), con el ranger al 80% (104 px de alto)
ANCHOR = {
    "walkway": ("top_a", "h", 44),          # la placa con su canto
    "substructure": ("truss_a", "h", 128),
    "bridge": ("bridge_a", "h", 140),
    "platforms": ("float_m", "w", 230),
    "pipes": ("thick", "h", 50),             # el diámetro del caño grueso
    "landmarks": ("blast_door", "h", 560),
    "small_props": ("crate_x_s", "h", 75),
}


def joints(path: Path) -> dict:
    """En un codo que viene de la izquierda y dobla para abajo: la altura del centro del brazo izquierdo y la x del
    centro del brazo de abajo, en px de la pieza (la esquina del caño)."""
    a = np.asarray(Image.open(path).convert("RGBA"))[..., 3] >= 128
    h, w = a.shape
    band = max(2, round(0.03 * w))
    rows = np.nonzero(a[:, :band].any(1))[0]
    cols = np.nonzero(a[h - max(2, round(0.03 * h)):, :].any(0))[0]
    return {"jy": round(float(rows.mean()), 1), "jx": round(float(cols.mean()), 1)}


def sheets() -> dict:
    out = {}
    for asset, (anchor, axis, size) in ANCHOR.items():
        out[asset] = {}
        for raw in sorted((HERE / "raw" / asset).glob(f"{PIECES_MODEL}_*.json")):
            post = json.loads(raw.read_text())["post"]
            folder = HERE / "post" / asset / raw.stem
            files = post.get("files", {})
            if anchor not in files:
                print(f"  ! {asset} {raw.stem}: no hay {anchor} (piezas: {', '.join(files)})")
                continue
            k = size / files[anchor][axis]
            pieces = {}
            for name, f in files.items():
                p = {"src": f"post/{asset}/{raw.stem}/{f['file']}", "w": f["w"], "h": f["h"]}
                if name.endswith("elbow"):
                    p |= joints(folder / f["file"])
                pieces[name] = p
            seams = {key: [v.get("before", {}).get("verdict"), v.get("after", {}).get("verdict")]
                     for key, v in post.get("seam", {}).items()}
            out[asset][raw.stem.rsplit("_", 1)[1]] = {"k": round(k, 5), "pieces": pieces, "seams": seams,
                                                      "notes": post.get("notes", [])}
    return out


def layers() -> dict:
    out = {}
    for layer in LAYERS:
        out[layer] = {}
        for raw in sorted((HERE / "raw" / layer).glob(f"{LAYERS_MODEL}_*.json")):
            post = json.loads(raw.read_text())["post"]
            f = post["files"]["image"] if "files" in post else {"file": Path(post["file"]).name}
            src = HERE / "post" / layer / f["file"]
            w, h = Image.open(src).size
            y0 = post.get("trim", {}).get("image", [0, 0])[1]
            out[layer][raw.stem.rsplit("_", 1)[1]] = {"src": f"post/{layer}/{f['file']}", "w": w, "h": h,
                                                      "src_h": post["source"]["h"], "y0": y0,
                                                      "seam": post.get("seam", {})}
    return out


def ranger() -> dict:
    """El primer dibujo de idle_combat, recortado del atlas, con su lugar respecto de los pies (px a 1x)."""
    out = ROOT / "characters" / "ranger" / "out"
    idx = json.loads((out / "ranger.json").read_text())["variants"]["1x"]
    at = json.loads((out / "ranger_1x-0.json").read_text())["frames"]["idle_combat/0000"]
    F, s = at["frame"], at["spriteSourceSize"]
    dst = HERE / "review"
    dst.mkdir(exist_ok=True)
    Image.open(out / "ranger_1x-0.png").crop((F["x"], F["y"], F["x"] + F["w"], F["y"] + F["h"])).save(dst / "ranger_idle.png")
    return {"src": "review/ranger_idle.png", "w": F["w"], "h": F["h"],
            "dx": s["x"] - idx["pivot_px"]["x"], "dy": s["y"] - idx["pivot_px"]["y"]}


def main() -> None:
    data = {"sheets": sheets(), "layers": layers(), "ranger": ranger(), "char": 0.8}
    html = (HERE / "kit_template.html").read_text(encoding="utf-8")
    (HERE / "kit.html").write_text(html.replace("__DATA__", json.dumps(data, separators=(",", ":"))), encoding="utf-8")
    n = sum(len(o) for o in data["sheets"].values())
    m = sum(len(o) for o in data["layers"].values())
    print(f"✓ {HERE / 'kit.html'}  ({n} opciones de hojas, {m} de capas)")


if __name__ == "__main__":
    main()
