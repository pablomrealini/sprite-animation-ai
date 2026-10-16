"""Arma un juego de prueba a partir del atlas que sacó spritepipe.

uso (desde la raíz del repo):
    uv run --project pipeline python prototypes/build.py ranger
    uv run --project pipeline python prototypes/build.py comando

Lee characters/<personaje>/out/, mide por frame la boca del arma, la subida y el punto más alto
(la mano en el colgado), mete esos datos en prototypes/<personaje>/src.html y deja la página y el
atlas en prototypes/<personaje>/dist/. Esa carpeta es la que se publica como artifact.
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def measure(out: Path, name: str) -> dict:
    at = json.loads((out / f"{name}_1x-0.json").read_text())
    idx = json.loads((out / f"{name}.json").read_text())["variants"]["1x"]
    img = np.asarray(Image.open(out / f"{name}_1x-0.png").convert("RGBA"))[..., 3]
    cw, ch = idx["canvas"]["w"], idx["canvas"]["h"]
    px, py = idx["pivot_px"]["x"], idx["pivot_px"]["y"]
    anims = {}
    for an, a in idx["animations"].items():
        frames = []
        for f in a["frames"]:
            d = at["frames"][f["name"]]
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
            # [x, y, w, h del atlas, x, y del trim, boca dx, dy, subida, punto alto dx, dy] relativos al pivot
            frames.append([F["x"], F["y"], F["w"], F["h"], s["x"], s["y"],
                           round(mx + 1 - px, 1), round(my - py, 1), round(py - bottom, 1),
                           round(tx - px, 1), round(top - py, 1)])
        anims[an] = {"loop": a["loop"], "ms": a["frames"][0]["duration"], "f": frames}
    return {"cell": [cw, ch], "pivot": [px, py], "anims": anims}


def main(name: str) -> None:
    proto, out = ROOT / "prototypes" / name, ROOT / "characters" / name / "out"
    data = measure(out, name)
    dist = proto / "dist"
    dist.mkdir(exist_ok=True)
    html = (proto / "src.html").read_text(encoding="utf-8")
    (dist / "index.html").write_text(html.replace("__SPRITE_DATA__", json.dumps(data, separators=(",", ":"))), encoding="utf-8")
    shutil.copy(out / f"{name}_1x-0.png", dist / f"{name}_1x-0.png")
    print(f"✓ {dist / 'index.html'}  ({', '.join(f'{k} {len(v['f'])}' for k, v in data['anims'].items())})")


if __name__ == "__main__":
    main(sys.argv[1])
