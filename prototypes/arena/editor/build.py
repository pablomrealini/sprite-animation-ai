"""Arma el editor de arenas: prototypes/arena/editor/dist/index.html, con las piezas del kit y un ranger parado.

uso (desde la raíz del repo):
    uv run --project pipeline python prototypes/arena/editor/build.py
    uv run --project pipeline python prototypes/arena/editor/build.py --page   # sólo la página (el kit ya exportado)

Usa las mismas funciones que el juego (export_kit de prototypes/arena/build.py y measure de prototypes/build.py), así
las piezas del kit tienen las mismas medidas. El color es el del juego: el LUT de color_lut() (la paleta de Pablo, de
prototypes/arena/paleta.py) y prototypes/arena/color.js en línea (gradePixels, la misma cuenta que gradúa el juego). La
física, el colgado, la caída que saca vida y el HUD salen de src.html (export_game): si Programación los cambia, alcanza
con volver a armar el editor. Las arenas no van adentro: el editor las lee de prototypes/arena/arenas/
por el servidor (serve.py); las de este momento quedan en la página como respaldo para abrirla sin servidor.
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ARENA = HERE.parent
ROOT = ARENA.parent.parent
CHAR = 0.8        # el ranger en la arena, al 80% (CHAR de src.html)
FOOT_SINK = 3     # px que se hunden los pies en lo que se pisa (FOOT_SINK de src.html)


def _arena_build():
    spec = importlib.util.spec_from_file_location("arena_build", ARENA / "build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def export_ranger(pb, dist: Path) -> dict:
    """El primer cuadro de la guardia, recortado del atlas: lo que se dibuja en cada spawn."""
    out = ROOT / "characters" / "ranger" / "out"
    spr = pb.measure(out, "ranger")
    name = "idle_combat" if "idle_combat" in spr["anims"] else "idle"
    ax, ay, w, h, tx, ty = spr["anims"][name]["f"][0][:6]
    px, py = spr["pivot"]
    Image.open(out / "ranger_1x-0.png").convert("RGBA").crop((ax, ay, ax + w, ay + h)).save(dist / "ranger.png", optimize=True)
    # dónde va la esquina del recorte respecto de los pies, y su tamaño, en px del juego
    return {"src": "ranger.png", "x": round((tx - px) * CHAR, 1), "y": round((ty - py) * CHAR + FOOT_SINK, 1),
            "w": round(w * CHAR, 1), "h": round(h * CHAR, 1)}


def export_lut() -> dict | None:
    """El LUT de la paleta, el mismo del juego ({"n": 17, "data": base64}); None si falta algo."""
    try:
        return _arena_build().color_lut()
    except (AttributeError, OSError) as err:
        print(f"  sin LUT de color: {err}")
        return None


def export_game() -> str:
    """Las reglas del juego que importan para armar una arena, leídas de src.html (sólo se lee): FEEL y DOUBLE_V (el
    salto y el doble, para el alcance), HANG_ON (colgarse), FALL (la caída que saca vida) y HUD2 (lo que tapa el HUD).
    Van como texto JS, tal cual están en el juego; la que no se encuentra va en null y el editor usa la de respaldo."""
    src = (ARENA / "src.html").read_text(encoding="utf-8")
    pats = {"FEEL": r"^const FEEL = (\{[^\n]*?\});", "HANG_ON": r"^const HANG_ON = (true|false);",
            "FALL": r"^const FALL = (\{[^\n]*?\});", "HUD2": r"^const HUD2 = (\{[^\n]*?\});",
            "DOUBLE_V": r"\bDOUBLE_V = ([0-9.]+)"}
    vals = {}
    for k, p in pats.items():
        m = re.search(p, src, re.M)
        vals[k] = m.group(1) if m else "null"
        if not m:
            print(f"  ojo: no encontré {k} en src.html (el editor usa el de respaldo)")
    return "{ " + ", ".join(f"{k}: {v}" for k, v in vals.items()) + " }"


def main() -> None:
    dist = HERE / "dist"
    dist.mkdir(exist_ok=True)
    cache = dist / "data.json"
    if "--page" in sys.argv and cache.exists():
        kit, ranger = json.loads(cache.read_text())[:2]
    else:
        ab = _arena_build()
        pb = ab._proto_build()
        kit = ab.export_kit(pb, dist)
        ranger = export_ranger(pb, dist)
        cache.write_text(json.dumps([kit, ranger]))
    lut = export_lut()
    arenas = {p.stem: json.loads(p.read_text()) for p in sorted((ARENA / "arenas").glob("*.json"))}
    kits = {p.parent.name: json.loads(p.read_text()) for p in sorted((ARENA / "arenas").glob("*/kit.json"))}
    html = (HERE / "editor.html").read_text(encoding="utf-8")
    color_js = ARENA / "color.js"
    html = html.replace("__COLOR_JS__", color_js.read_text(encoding="utf-8") if color_js.exists() else "")
    html = html.replace("__GAME_DATA__", export_game())
    for key, val in (("__KIT_DATA__", kit), ("__RANGER_DATA__", ranger), ("__ARENA_DATA__", arenas), ("__LUT_DATA__", lut),
                     ("__KITS_DATA__", kits)):
        html = html.replace(key, json.dumps(val, separators=(",", ":"), ensure_ascii=False))
    (dist / "index.html").write_text(html, encoding="utf-8")
    print(f"✓ {dist / 'index.html'}  ({len(kit['pieces'])} piezas del kit 2D, kits: {', '.join(kits) or 'ninguno'}, "
          f"arenas: {', '.join(arenas)})")


if __name__ == "__main__":
    main()
