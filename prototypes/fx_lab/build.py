"""Arma el banco de pruebas de efectos del ranger: fogonazo e impactos por código, con sprites de IA o mezclados.

uso (desde la raíz del repo):
    uv run --project pipeline python prototypes/fx_lab/build.py

Mide el atlas del ranger con la misma función que el juego (`measure` de prototypes/build.py, sin tocarlo),
achica las piezas de backgrounds/ranger_fx/post/ (spritepipe gen-images) a dist/fx/, les mide el ancla y deja
prototypes/fx_lab/dist/index.html con el atlas al lado. dist/ es lo que se publica como artifact.
"""
import importlib.util
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent.parent
LAB = ROOT / "prototypes" / "fx_lab"
FX_SET = ROOT / "backgrounds" / "ranger_fx"
MODEL = "gpt-image-2.5-sunburst-fal"
EXPORT = 1 / 3   # px exportados por px de la hoja: a ×4 de lupa, un fogonazo de 32 px del juego pide ~190 px


def _game_measure():
    spec = importlib.util.spec_from_file_location("proto_build", ROOT / "prototypes" / "build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.measure


def _shrink(src: Path) -> Image.Image:
    im = Image.open(src).convert("RGBA")
    a = np.asarray(im).copy()
    a[..., 3][a[..., 3] >= 250] = 255   # GPT Image devuelve 254 como máximo: lo opaco, opaco
    im = Image.fromarray(a, "RGBA").convert("RGBa")   # premultiplicado: que el achique no ensucie el borde
    size = (max(1, round(im.width * EXPORT)), max(1, round(im.height * EXPORT)))
    return im.resize(size, Image.LANCZOS).convert("RGBA")


def _anchor(im: Image.Image, where: str) -> list[float]:
    """El punto que va pegado a la boca (fogonazo) o al punto de contacto (impacto), en px de la pieza."""
    a = np.asarray(im)[..., 3] >= 128
    ys, xs = np.nonzero(a)
    if where == "center":
        return [round(float(xs.mean()), 1), round(float(ys.mean()), 1)]
    edge = int(xs.min()) if where == "left" else int(xs.max())
    band = max(2, round(0.04 * im.width))   # filas que ocupa la punta, en el 4% del ancho más cercano al borde
    cols = slice(edge, edge + band) if where == "left" else slice(edge - band + 1, edge + 1)
    rows = np.nonzero(a[:, cols].any(1))[0]
    return [float(edge), round(float(rows.mean()), 1)]


def export_fx(dist: Path) -> dict:
    out = dist / "fx"
    out.mkdir(exist_ok=True)
    data = {}
    for asset in ("muzzle", "impact"):
        data[asset] = {}
        for raw in sorted((FX_SET / "raw" / asset).glob(f"{MODEL}_*.json")):
            opt = raw.stem.rsplit("_", 1)[1]
            post = json.loads(raw.read_text())["post"]
            pieces = {}
            for name, f in post["files"].items():
                im = _shrink(FX_SET / "post" / asset / raw.stem / f["file"])
                # fogonazo: la boca a la izquierda. Impacto: el primer frame (la estrella) centrado en el contacto;
                # los demás salpican hacia atrás desde la punta derecha
                where = "left" if asset == "muzzle" else "center" if name.endswith("1") else "right"
                dst = f"fx/{asset}_{opt}_{name}.png"
                im.save(dist / dst, optimize=True)
                ax, ay = _anchor(im, where)
                pieces[name] = {"src": dst, "w": im.width, "h": im.height, "ax": ax, "ay": ay}
            data[asset][opt] = pieces
    return data


def main() -> None:
    out = ROOT / "characters" / "ranger" / "out"
    spr = _game_measure()(out, "ranger")
    dist = LAB / "dist"
    dist.mkdir(exist_ok=True)
    fx = export_fx(dist)
    html = (LAB / "src.html").read_text(encoding="utf-8")
    html = html.replace("__SPRITE_DATA__", json.dumps(spr, separators=(",", ":")))
    html = html.replace("__FX_DATA__", json.dumps(fx, separators=(",", ":")))
    (dist / "index.html").write_text(html, encoding="utf-8")
    shutil.copy(out / "ranger_1x-0.png", dist / "ranger_1x-0.png")
    n = sum(len(p) for a in fx.values() for p in a.values())
    print(f"✓ {dist / 'index.html'}  ({n} piezas de efecto: "
          f"{', '.join(f'{a} {len(o)} opciones' for a, o in fx.items())})")


if __name__ == "__main__":
    main()
