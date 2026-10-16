"""Arma la arena de prueba: VS local de 4 rangers (jugadores o bots) en una pantalla, con el kit industrial.

uso (desde la raíz del repo):
    uv run --project pipeline python prototypes/arena/build.py

Mide el atlas del ranger con la misma función que el polígono (`measure` de prototypes/build.py), achica las piezas
elegidas de backgrounds/ranger_industrial (ver KIT) a dist/kit/, los efectos de backgrounds/ranger_fx a dist/fx/, y
deja prototypes/arena/dist/index.html con el atlas (en base64), las medidas y las arenas de arenas/*.json adentro. Los
colores de los otros tres jugadores salen del mismo atlas en la página (el rojo de la armadura cambia de tono), así se
baja una sola vez. dist/ es lo que se publica como artifact.
"""
import base64
import importlib.util
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent.parent
HERE = ROOT / "prototypes" / "arena"
SET = ROOT / "backgrounds" / "ranger_industrial"
PIECES, LAYERS = "gpt-image-2.5-sunburst-fal", "nano-banana-2.1"

# las opciones elegidas el 2026-10-16 en backgrounds/ranger_industrial/kit.html, y la pieza que da la escala de cada hoja
# con su medida en px del juego (la misma que en kit.html: el ranger al 80% mide ~104 px)
KIT = {
    "walkway": (1, "top_a", "h", 44),
    "substructure": (1, "truss_a", "h", 128),
    "bridge": (2, "bridge_a", "h", 140),
    "platforms": (1, "float_m", "w", 230),
    "pipes": (1, "thick", "h", 50),
    "landmarks": (2, "blast_door", "h", 560),
    "small_props": (2, "crate_x_s", "h", 75),
}
SCREEN_LAYERS = {"sky": 1, "far": 1, "mid": 2, "near": 1}
# la granada y su explosión (backgrounds/ranger_grenade): la opción elegida de cada hoja y la medida en px del juego de
# la pieza que da la escala. None mientras no se eligió: el juego las dibuja por código
GRENADE_SET = ROOT / "backgrounds" / "ranger_grenade"
GRENADE_ART = {   # elegidas el 2026-10-16: la opción 1 de las dos hojas
    "grenade": (1, "off", "h", 24),           # la granada, ~24 px de alto con la tapa
    "explosion": (1, "pieza_3", "w", 300),    # el dibujo más grande, 300 px de ancho (el radio del daño es 150). El post
}                                             # sacó 7 piezas (el humo del final vino en dos): el juego usa las 6 primeras
EXPORT = 1         # px de las piezas por px del juego: con la cámara al 50% y pantalla 2x, uno a uno
VIEW_H = 540       # alto de la pantalla del juego
LAYER_SCALE = 2    # las capas, a 2 px por px de pantalla


def _proto_build():
    spec = importlib.util.spec_from_file_location("proto_build", ROOT / "prototypes" / "build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def export_kit(pb, dist: Path) -> dict:
    out = dist / "kit"
    out.mkdir(exist_ok=True)
    data = {"pieces": {}, "layers": {}}
    for asset, (opt, anchor, axis, size) in KIT.items():
        stem = f"{PIECES}_{opt}"
        post = json.loads((SET / "raw" / asset / f"{stem}.json").read_text())["post"]
        k = size / post["files"][anchor][axis]
        for piece, f in post["files"].items():
            dst = out / f"{asset}-{piece}.png"
            pb.export_image(SET / "post" / asset / stem / f["file"], dst, k * EXPORT)
            p = {"src": f"kit/{dst.name}", "w": round(f["w"] * k, 2), "h": round(f["h"] * k, 2)}
            a = np.asarray(Image.open(dst))[..., 3] >= 128
            if asset == "platforms":   # dónde empieza la placa que se pisa: la primera fila opaca en más de la mitad del ancho
                p["top"] = round(float(np.argmax(a.sum(1) > 0.5 * a.shape[1])) / EXPORT, 1)
            if piece.endswith("elbow"):   # la esquina del caño: el centro del brazo izquierdo (y) y el del de abajo (x)
                band = max(2, round(0.03 * a.shape[1]))
                p["jy"] = round(float(np.nonzero(a[:, :band].any(1))[0].mean()) / EXPORT, 1)
                p["jx"] = round(float(np.nonzero(a[-band:].any(0))[0].mean()) / EXPORT, 1)
            data["pieces"][f"{asset}/{piece}"] = p
    for layer, opt in SCREEN_LAYERS.items():
        stem = f"{LAYERS}_{opt}"
        post = json.loads((SET / "raw" / layer / f"{stem}.json").read_text())["post"]
        f, src_h = post["files"]["image"], post["source"]["h"]
        k = VIEW_H / src_h   # px de pantalla por px del lienzo del modelo: el lienzo entero, al alto de la pantalla
        dst = out / f"{layer}.webp"
        pb.export_image(SET / "post" / layer / f["file"], dst, k * LAYER_SCALE)
        data["layers"][layer] = {"src": f"kit/{dst.name}", "w": round(f["w"] * k, 2), "h": round(f["h"] * k, 2),
                                 "y": round(post.get("trim", {}).get("image", [0, 0])[1] * k, 2)}
    return data


def export_grenade(pb, dist: Path) -> dict:
    """Achica las piezas elegidas de la granada y la explosión a dist/kit/; devuelve su tamaño en px del juego."""
    data = {}
    for asset, (opt, anchor, axis, size) in GRENADE_ART.items():
        if opt is None:
            continue
        stem = f"{PIECES}_{opt}"
        post = json.loads((GRENADE_SET / "raw" / asset / f"{stem}.json").read_text())["post"]
        k = size / post["files"][anchor][axis]
        data[asset] = {}
        for piece, f in post["files"].items():
            dst = dist / "kit" / f"grenade-{asset}-{piece}.png"
            pb.export_image(GRENADE_SET / "post" / asset / stem / f["file"], dst, k * EXPORT)
            data[asset][piece] = {"src": f"kit/{dst.name}", "w": round(f["w"] * k, 2), "h": round(f["h"] * k, 2)}
        if asset == "grenade":   # el ícono del HUD y del power-up: la apagada, a 3 px por px del juego (se dibuja más grande)
            f, dst = post["files"]["off"], dist / "kit" / "grenade-grenade-hud.png"
            pb.export_image(GRENADE_SET / "post" / asset / stem / f["file"], dst, k * 3)
            data[asset]["hud"] = {"src": f"kit/{dst.name}", "w": round(f["w"] * k, 2), "h": round(f["h"] * k, 2)}
    return data


def color_lut() -> dict:
    """La paleta de Pablo para graduar las arenas (paleta.py): el LUT que lleva refs/refineria.webp a
    refs/refineria_paleta_pablo.webp, como {n, data} en base64. El juego lo aplica según ARENA.color."""
    spec = importlib.util.spec_from_file_location("paleta", HERE / "paleta.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.lut_payload(mod.fit_lut(HERE / "refs" / "refineria.webp", HERE / "refs" / "refineria_paleta_pablo.webp"))


def main() -> None:
    pb = _proto_build()
    out = ROOT / "characters" / "ranger" / "out"
    dist = HERE / "dist"
    dist.mkdir(exist_ok=True)
    spr = pb.measure(out, "ranger")
    kit = export_kit(pb, dist)
    fx = pb.export_fx("ranger", dist)
    gren = export_grenade(pb, dist)
    arenas = {p.stem: json.loads(p.read_text()) for p in sorted((HERE / "arenas").glob("*.json"))}
    # las arenas pintadas: su lámina y sus piezas pintadas (`pieces`, pueden estar en una subcarpeta de arenas/) van al
    # lado de la página
    for a in arenas.values():
        srcs = ([a["plate"]["src"]] if "plate" in a else []) + [pc["src"] for pc in a.get("pieces", {}).values()]
        for src in srcs:
            dst = dist / "arenas" / src
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(HERE / "arenas" / src, dst)
    html = (HERE / "src.html").read_text(encoding="utf-8")
    # la graduación de color (color.js, la misma que usa el editor) va adentro de la página, con la paleta de Pablo
    html = html.replace("__COLOR_JS__", (HERE / "color.js").read_text(encoding="utf-8"))
    for key, val in (("__SPRITE_DATA__", spr), ("__KIT_DATA__", kit), ("__FX_DATA__", fx), ("__ARENA_DATA__", arenas), ("__GRENADE_DATA__", gren),
                     ("__COLOR_LUT__", color_lut())):
        html = html.replace(key, json.dumps(val, separators=(",", ":"), ensure_ascii=False))
    # el atlas, adentro: la página le lee los píxeles para los colores, y abierta desde el disco un PNG de al lado no deja
    atlas = base64.b64encode((out / "ranger_1x-0.png").read_bytes()).decode()
    html = html.replace("__ATLAS_SRC__", f"data:image/png;base64,{atlas}")
    (dist / "index.html").write_text(html, encoding="utf-8")
    size = sum(p.stat().st_size for p in dist.rglob("*") if p.is_file()) / 1e6
    print(f"✓ {dist / 'index.html'}  ({len(kit['pieces'])} piezas, {len(kit['layers'])} capas, arenas: "
          f"{', '.join(arenas)}; {size:.1f} MB en dist/)")


if __name__ == "__main__":
    main()
