"""Arma la arena de prueba: VS local de 4 rangers (jugadores o bots) en una pantalla, con el kit industrial.

uso (desde la raíz del repo):
    uv run --project pipeline python prototypes/arena/build.py

Mide los atlas de los personajes del selector (CHARACTERS: el ranger 2D y el low-poly) con la misma función que el
polígono (`measure` de prototypes/build.py), achica las piezas elegidas de backgrounds/ranger_industrial (ver KIT) a
dist/kit/, los efectos de backgrounds/ranger_fx a dist/fx/, y deja prototypes/arena/dist/index.html con los atlas (en
base64), las medidas y las arenas de arenas/*.json adentro. Los colores de los otros tres jugadores salen del mismo atlas
en la página (el rojo de la armadura cambia de tono), así se baja una sola vez. dist/ es lo que se publica como artifact.
"""
import base64
import importlib.util
import io
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
# la granada y su explosión (backgrounds/lowpoly_grenade): la opción elegida de cada hoja y la medida en px del juego de
# la pieza que da la escala. None mientras no se eligió: el juego las dibuja por código
GRENADE_SET = ROOT / "backgrounds" / "lowpoly_grenade"   # antes ranger_grenade (cel 2D); el 2026-10-17 pasó a low-poly
GRENADE_ART = {   # elegidas el 2026-10-17: la 2 de las dos hojas (la granada 1 venía cortada abajo)
    "grenade": (2, "off", "h", 24),           # la granada, ~24 px de alto con la tapa
    "explosion": (2, "e3", "w", 300),         # el dibujo más grande, 300 px de ancho (el radio del daño es 150)
}
# el retrato del HUD (backgrounds/ranger_hud): la hoja elegida (modelo_n), la pieza que da la escala, el eje y su medida
# en px del archivo exportado. None mientras no se eligió: el juego usa la cabeza del atlas
HUD_SET = ROOT / "backgrounds" / "ranger_hud"
HUD_ART = {   # elegida el 2026-10-17: la 2 de Nano Banana (las tres caras con el mismo encuadre)
    "portrait": ("nano-banana-2.1_2", "normal", "w", 160),   # 160 px de ancho: el círculo mide 36 de pantalla (72 en retina)
}
# los personajes del selector del menú (y la tecla C): el ranger 2D, con su atlas 1x de 128 px, y el low-poly
# (characters/lowpoly), con su variante 0,5x, que mide 128 px como el ranger y viene en dos páginas (load_atlas las
# junta). fx_muzzle: donde hay out/fx/<anim>_muzzle.json (hoy los tres tiros: shoot, shoot2h y crouch_shoot, de
# characters/lowpoly/boca_disparos.py), esa boca manda sobre la medida del sprite. Los cuadros con fogonazo dibujado los
# marca measure, como en el ranger. frames: las transiciones a tantos cuadros parejos como las del ranger, porque el
# juego da 0,04 s por cuadro a las entradas y no deja disparar hasta que terminan (con los 9 del clip, el primer tiro
# salía a los 0,36 s y no a los 0,16)
CHARACTERS = {
    "ranger": {"label": "2D", "variant": "1x"},
    "lowpoly": {"label": "Low-poly", "variant": "0.5x", "fx_muzzle": True,
                "frames": {"shoot_in": 4, "shoot2h_in": 4, "crouch_in": 4, "crouch_out": 4}},
}
# los power-ups low-poly (backgrounds/lowpoly_pickups): la hoja elegida y el alto de la pieza que da la escala, en px del
# archivo exportado (en el juego flotan a 46 px de alto: el doble, para que se vean nítidos en retina)
PICKUP_SET = ROOT / "backgrounds" / "lowpoly_pickups"
PICKUP_ART = {   # elegida el 2026-10-17: la 1 de GPT Image (la cruz grande y las luces se leen a 42 px)
    "pickups": ("gpt-image-2.5-sunburst-fal_1", "hp", "h", 96),
}
# el fogonazo y el impacto low-poly (backgrounds/lowpoly_fx), en rojo con el centro blanco: el juego los recolorea por
# equipo. La medida es la del cuadro más grande, en px del archivo (el doble de lo que miden en el juego)
LOWFX_SET = ROOT / "backgrounds" / "lowpoly_fx"
LOWFX_ART = {   # elegidas el 2026-10-17: la 2 de cada hoja (el impacto 1 salió partido en cinco piezas)
    "muzzle": ("gpt-image-2.5-sunburst-fal_2", "m1", "w", 128),
    "impact": ("gpt-image-2.5-sunburst-fal_2", "i2", "w", 128),
}
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


def export_hud(pb, dist: Path, set_dir: Path = HUD_SET, art: dict = HUD_ART, prefix: str = "hud") -> dict:
    """Achica las piezas de la hoja elegida de cada asset de `art` (de backgrounds/<set>) a dist/kit/<prefix>-…; devuelve
    su tamaño en px del archivo. Sirve para el retrato del HUD y para los power-ups."""
    data = {}
    for asset, (stem, anchor, axis, size) in art.items():
        if stem is None:
            continue
        post = json.loads((set_dir / "raw" / asset / f"{stem}.json").read_text())["post"]
        k = size / post["files"][anchor][axis]
        data[asset] = {}
        for piece, f in post["files"].items():
            dst = dist / "kit" / f"{prefix}-{asset}-{piece}.png"
            pb.export_image(set_dir / "post" / asset / stem / f["file"], dst, k)
            data[asset][piece] = {"src": f"kit/{dst.name}", "w": round(f["w"] * k, 2), "h": round(f["h"] * k, 2)}
    return data


def export_character(pb, name: str, cfg: dict) -> dict:
    """Las medidas y el atlas de un personaje del selector: {label, spr, atlas} con el atlas como data: URI. El de una
    página va tal cual (PNG); el unido de varias, en WebP sin pérdida (los colores exactos para el recoloreo, ~20%
    menos que en PNG)."""
    out = ROOT / "characters" / name / "out"
    sheet, frames = pb.load_atlas(out, name, cfg["variant"])
    spr = pb.measure(out, name, cfg["variant"], (sheet, frames))
    for an, a in spr["anims"].items():
        fxp = out / "fx" / f"{an}_muzzle.json"
        if cfg.get("fx_muzzle") and fxp.exists():
            fx = json.loads(fxp.read_text())["variants"][cfg["variant"]]["frames"]
            assert len(fx) == len(a["f"]), f"{name}/{an}: {len(fx)} bocas para {len(a['f'])} cuadros"
            for f, m in zip(a["f"], fx):
                f[6], f[7] = round(m["dx"], 1), round(m["dy"], 1)
    for an, n in cfg.get("frames", {}).items():
        a = spr["anims"][an]
        a["f"] = [a["f"][i] for i in np.round(np.linspace(0, len(a["f"]) - 1, n)).astype(int)]
    # sin salida de apuntar (el low-poly no la tiene): la entrada al revés
    for b in ("shoot", "shoot2h"):
        if f"{b}_out" not in spr["anims"] and f"{b}_in" in spr["anims"]:
            a = spr["anims"][f"{b}_in"]
            spr["anims"][f"{b}_out"] = {**a, "f": a["f"][::-1]}
    pages = json.loads((out / f"{name}.json").read_text())["variants"][cfg["variant"]]["atlas"]
    if len(pages) == 1:
        src = "data:image/png;base64," + base64.b64encode((out / pages[0]["image"]).read_bytes()).decode()
    else:
        buf = io.BytesIO()
        sheet.save(buf, "WEBP", lossless=True, quality=100, method=4)
        src = "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()
    return {"label": cfg["label"], "spr": spr, "atlas": src}


def main() -> None:
    pb = _proto_build()
    dist = HERE / "dist"
    dist.mkdir(exist_ok=True)
    chars = {name: export_character(pb, name, cfg) for name, cfg in CHARACTERS.items()}
    kit = export_kit(pb, dist)
    fx = pb.export_fx("ranger", dist)
    gren = export_grenade(pb, dist)
    hud = export_hud(pb, dist)
    pick = export_hud(pb, dist, PICKUP_SET, PICKUP_ART, "pick")
    lowfx = export_hud(pb, dist, LOWFX_SET, LOWFX_ART, "lfx")
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
    for key, val in (("__CHAR_DATA__", chars), ("__KIT_DATA__", kit), ("__FX_DATA__", fx), ("__ARENA_DATA__", arenas), ("__GRENADE_DATA__", gren), ("__HUD_DATA__", hud), ("__PICKUP_DATA__", pick), ("__LOWFX_DATA__", lowfx),
                     ("__COLOR_LUT__", color_lut())):
        html = html.replace(key, json.dumps(val, separators=(",", ":"), ensure_ascii=False))
    (dist / "index.html").write_text(html, encoding="utf-8")
    size = sum(p.stat().st_size for p in dist.rglob("*") if p.is_file()) / 1e6
    print(f"✓ {dist / 'index.html'}  ({len(kit['pieces'])} piezas, {len(kit['layers'])} capas, arenas: "
          f"{', '.join(arenas)}; personajes: {', '.join(chars)}; {size:.1f} MB en dist/, "
          f"{(dist / 'index.html').stat().st_size / 1e6:.1f} MB la página)")


if __name__ == "__main__":
    main()
