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
import re
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
# drop: animaciones del atlas que el juego no usa y no van a la página (Pablo, 2026-10-19: "sacando de la página las
# animaciones apagadas"); con drop_off, además, las de los interruptores apagados de src.html (OFF_ANIMS). Siguen en el
# atlas: si se prende el interruptor, vuelven a entrar al compilar
CHARACTERS = {
    "ranger": {"label": "2D", "variant": "1x"},
    "lowpoly": {"label": "Low-poly", "variant": "0.5x", "fx_muzzle": True,
                "frames": {"shoot_in": 4, "shoot2h_in": 4, "crouch_in": 4, "crouch_out": 4},
                # el tiro viejo (el juego usa throw2) y el mortal viejo (?mortal=1 usa double_jump_fix)
                "drop": ["throw", "double_jump"], "drop_off": True},
}
# las animaciones de cada interruptor de src.html (`const NOMBRE = true|false`): apagado, no van a la página
OFF_ANIMS = {"HANG_ON": ["hang_in", "hang", "hang_two", "climb"], "TWO_HAND_ON": ["shoot2h_in", "shoot2h", "shoot2h_out"]}
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
# el escudo low-poly (backgrounds/lowpoly_shield): el power-up (va con los otros, en PICKUP_DATA.pickups.shield) y la
# burbuja, entera (dome) y rajada (crack). En px del archivo, el doble del juego: el power-up flota a 46 de alto como los
# otros y la burbuja mide 126 × 130
SHIELD_SET = ROOT / "backgrounds" / "lowpoly_shield"
SHIELD_ART = {   # elegidas el 2026-10-18 (backgrounds/lowpoly_shield/revision.png): el escudo de la hoja 1, la burbuja de la 2
    "pickup": ("gpt-image-2.5-sunburst-fal_1", "shield", "h", 96),
    "bubble": ("gpt-image-2.5-sunburst-fal_2", "dome", "h", 260),
}
# los efectos del salto low-poly (backgrounds/lowpoly_saltos/entrega, de entrega.py; aprobados por Pablo el 2026-10-20:
# "Aprobados así, con el doble salto celeste fijo"): despegue t1–t3, aterrizaje l1–l3, fuerte h1–h4 y doble salto d1–d3,
# cada cuadro en dos capas del mismo tamaño (atras va antes del personaje y adelante después), al doble del juego, con
# el ancla en los pies (medidas.json, en px del juego). El polvo, en gris claro (~215 de luma): el juego lo tiñe con el
# color de la arena; el doble salto va en celeste fijo (las versiones _blanco no se usan). Reemplaza a lowpoly_dust
SALTOS_SET = ROOT / "backgrounds" / "lowpoly_saltos" / "entrega"
# las piezas sueltas de cada efecto, para animarlas por código (el modo "piezas"; Pablo, 2026-10-20: "tienen pocos cuadros,
# son medias duras"): las de Arte en backgrounds/lowpoly_saltos/piezas/piezas.json ({efecto: [{src, x, y, w, h, capa,
# tipo, de}]}, x e y el centro respecto de los pies, en px del juego) y, mientras no estén, las manchas de las capas de la
# entrega (AUTO_PIEZAS: de qué cuadro sale cada tipo). Lo fuerte (hard y heavy) usa las mismas
PIEZAS_JSON = ROOT / "backgrounds" / "lowpoly_saltos" / "piezas" / "piezas.json"
PIEZAS_NOMBRES = {"despegue": ["takeoff"], "aterrizaje": ["land"], "fuerte": ["hard", "heavy"], "doble": ["double"],
                  "takeoff": ["takeoff"], "land": ["land"], "hard": ["hard"], "heavy": ["heavy"], "double": ["double"]}
AUTO_PIEZAS = {
    "despegue": [("t1", "estrella"), ("t2", "nube"), ("t3", "esquirla")],
    "aterrizaje": [("l1", "estrella"), ("l2", "nube"), ("l3", "esquirla")],
    "fuerte": [("h1", "estrella"), ("h2", "nube"), ("h3", "esquirla")],
    "doble": [("d1", "destello"), ("d2", "anillo")],
}
# el fogonazo y el impacto del disparo en piezas (Pablo, 2026-10-20: "me gusta diseño 3d teñido de rojo hoja 2": d_3d,
# hoja 2, de backgrounds/disparo_estilos, con mezcla normal + núcleo y teñido por equipo). Las piezas de Arte en
# backgrounds/disparo_estilos/piezas/piezas.json ({fogonazo|impacto: [{src, x, y, w, h, tipo, ang}]}, cada pieza en
# _alfa, que va normal, y _nucleo, que va sumado a 0,5; x e y desde la boca o el punto del golpe, en px del juego, al
# largo de hoy de 62 px) y, mientras no estén, piezas de mentira: el cuadro 2 (el pico) de cada fila de la hoja elegida,
# partido en núcleo, rayos (sectores) y chispas (manchas sueltas)
DISPARO_SET = ROOT / "backgrounds" / "disparo_estilos"
DISPARO_HOJA = DISPARO_SET / "raw" / "d_3d" / "gpt-image-2.5-sunburst-fal_2.png"
DISPARO_JSON = DISPARO_SET / "piezas" / "piezas.json"
DISPARO_LARGO = {"fogonazo": 62, "impacto": 60}   # px del juego del pico (de la boca a la punta; el impacto, de ancho)
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


def export_hud(pb, dist: Path, set_dir: Path = HUD_SET, art: dict = HUD_ART, prefix: str = "hud", only: dict | None = None) -> dict:
    """Achica las piezas de la hoja elegida de cada asset de `art` (de backgrounds/<set>) a dist/kit/<prefix>-…; devuelve
    su tamaño en px del archivo. Sirve para el retrato del HUD, los power-ups, el escudo y el polvo. only: {asset: [piezas]}
    para exportar sólo esas (sin él, todas)."""
    data = {}
    for asset, (stem, anchor, axis, size) in art.items():
        if stem is None:
            continue
        post = json.loads((set_dir / "raw" / asset / f"{stem}.json").read_text())["post"]
        k = size / post["files"][anchor][axis]
        data[asset] = {}
        for piece, f in post["files"].items():
            if only and asset in only and piece not in only[asset]:
                continue
            dst = dist / "kit" / f"{prefix}-{asset}-{piece}.png"
            pb.export_image(set_dir / "post" / asset / stem / f["file"], dst, k)
            data[asset][piece] = {"src": f"kit/{dst.name}", "w": round(f["w"] * k, 2), "h": round(f["h"] * k, 2)}
    return data


def export_saltos(dist: Path) -> dict:
    """Los cuadros de los efectos del salto a dist/kit/salto-<capa>-<cuadro>.png: {capa: {cuadro: {src, w, h, ax, ay}}},
    con w y h del archivo (al doble del juego, como export_hud) y el ancla en px del juego."""
    meas = json.loads((SALTOS_SET / "medidas.json").read_text())
    for old in (dist / "kit").glob("dust-*.png"):   # el polvo de antes (lowpoly_dust)
        old.unlink()
    data = {"atras": {}, "adelante": {}}
    for piece, m in meas.items():
        if piece.startswith("_"):
            continue
        for layer in data:
            dst = dist / "kit" / f"salto-{layer}-{piece}.png"
            Image.open(SALTOS_SET / f"{piece}_{layer}.png").convert("RGBA").save(dst, optimize=True)
            w, h = m["archivo"]
            data[layer][piece] = {"src": f"kit/{dst.name}", "w": w, "h": h, "ax": m["ancla"][0], "ay": m["ancla"][1]}
    return data


def export_piezas(dist: Path) -> dict:
    """Las piezas de cada efecto a dist/kit/pieza-…png: {tipo de efecto del juego: [{src, x, y, w, h, capa, tipo, g}]} (x, y,
    w y h en px del juego; g: el grupo, las piezas que se mueven juntas, como la parte de atrás y la de adelante de una
    mancha). Las de Arte si están; si no, las manchas de las capas de la entrega."""
    for old in (dist / "kit").glob("pieza-*.png"):
        old.unlink()
    out: dict = {}
    if PIEZAS_JSON.exists():
        src = json.loads(PIEZAS_JSON.read_text())
        for efecto, pieces in src.items():
            if efecto.startswith("_"):
                continue
            lst, groups = [], {}
            for i, pc in enumerate(pieces):
                dst = dist / "kit" / f"pieza-{efecto}-{i}.png"
                # src: relativo a backgrounds/lowpoly_saltos (así lo escribe Arte) o a la carpeta de piezas.json
                path = next(p for p in (PIEZAS_JSON.parent.parent / pc["src"], PIEZAS_JSON.parent / pc["src"]) if p.exists())
                Image.open(path).convert("RGBA").save(dst, optimize=True)
                g = groups.setdefault(pc.get("junto") or pc.get("grupo") or f"_{i}", len(groups))   # junto: las mitades que se mueven juntas
                lst.append({"src": f"kit/{dst.name}", "x": pc["x"], "y": pc["y"], "w": pc["w"], "h": pc["h"], "capa": pc["capa"],
                            "tipo": pc["tipo"], "g": g})
            for kind in PIEZAS_NOMBRES.get(efecto, []):
                out[kind] = lst
        return {"de": "arte", "piezas": out}
    import cv2
    meas = json.loads((SALTOS_SET / "medidas.json").read_text())
    for efecto, fuentes in AUTO_PIEZAS.items():
        lst, g = [], 0
        for cuadro, tipo in fuentes:
            ax, ay = (v * 2 for v in meas[cuadro]["ancla"])
            layers = {c: np.asarray(Image.open(SALTOS_SET / f"{cuadro}_{c}.png").convert("RGBA")) for c in ("atras", "adelante")}
            alpha = np.maximum(layers["atras"][..., 3], layers["adelante"][..., 3])
            if tipo in ("estrella", "destello"):   # entera, una pieza por capa
                labels, comps = (alpha > 8).astype(np.int32), [1]
            elif tipo in ("anillo", "nube"):   # en sectores alrededor del ancla (10 el óvalo, 8 la nube), para que se abran
                ns = 10 if tipo == "anillo" else 8
                yy, xx = np.mgrid[0:alpha.shape[0], 0:alpha.shape[1]]
                sector = ((np.arctan2((yy - ay) * 2.5, xx - ax) + np.pi) / (2 * np.pi) * ns).astype(np.int32) % ns
                labels = np.where(alpha > 8, sector + 1, 0)
                comps = [i for i in range(1, ns + 1) if (labels == i).sum() >= 30]
            else:   # manchas: lo que se toca (engordado un poco, así las motas se pegan a su nube), las más grandes primero
                k = 7 if tipo == "nube" else 3
                fat = cv2.dilate((alpha > 24).astype(np.uint8), np.ones((k, k), np.uint8))
                n, labels, stats, _ = cv2.connectedComponentsWithStats(fat, 8)
                comps = [i for i in sorted(range(1, n), key=lambda i: -stats[i, 4]) if stats[i, 4] >= (120 if tipo == "nube" else 30)]
                comps = comps[: (10 if tipo == "nube" else 14)]
            for ci in comps:
                mask = (labels == ci) & (alpha > 0)
                ys, xs = np.nonzero(mask)
                if not len(xs):
                    continue
                x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
                for capa, im in layers.items():
                    crop = im[y0:y1, x0:x1].copy()
                    crop[..., 3] = np.where(mask[y0:y1, x0:x1], crop[..., 3], 0)
                    if (crop[..., 3] > 8).sum() < 6:
                        continue
                    dst = dist / "kit" / f"pieza-{efecto}-{len(lst)}.png"
                    Image.fromarray(crop).save(dst, optimize=True)
                    lst.append({"src": f"kit/{dst.name}", "x": round(((x0 + x1) / 2 - ax) / 2, 1), "y": round(((y0 + y1) / 2 - ay) / 2, 1),
                                "w": round((x1 - x0) / 2, 1), "h": round((y1 - y0) / 2, 1), "capa": capa, "tipo": tipo, "g": g})
                g += 1
        for kind in PIEZAS_NOMBRES[efecto]:
            out[kind] = lst
    return {"de": "manchas", "piezas": out}


def _disparo_cuadros(a: np.ndarray) -> dict:
    """{"fogonazo"|"impacto": (rgb del cuadro 2, ax, ay)} de la hoja negra (como backgrounds/disparo_estilos/revision.py):
    2 filas, cada una en 4 cuadros por los 3 huecos de columnas vacías más anchos; el ancla, la boca (el borde
    izquierdo a media fila) o el centro"""
    lit = a.max(2) > 12
    rows = lit.any(1)
    ys = np.nonzero(rows)[0]
    bands, y = [], ys.min()
    while y <= ys.max():
        if rows[y]:
            y0 = y
            while y <= ys.max() and rows[y:y + 30].any():
                y += 1
            bands.append((y0, y))
        y += 1
    bands = sorted(sorted(bands, key=lambda b: -(b[1] - b[0]))[:2])
    out = {}
    for kind, (y0, y1) in zip(("fogonazo", "impacto"), bands):
        occ = lit[y0:y1].any(0)
        xs = np.nonzero(occ)[0]
        runs, x = [], xs.min()
        while x < xs.max():
            if not occ[x]:
                x0 = x
                while not occ[x]:
                    x += 1
                runs.append((x - x0, x0, x))
            x += 1
        cuts = sorted(r[1:] for r in sorted(runs, reverse=True)[:3])
        edges = [xs.min()] + [c for r in cuts for c in r] + [xs.max() + 1]
        x0, x1 = edges[2], edges[3]   # el cuadro 2
        sub = lit[y0:y1, x0:x1]
        ry, rx = np.nonzero(sub.any(1))[0], np.nonzero(sub.any(0))[0]
        bx0, by0, bx1, by1 = x0 + rx.min(), y0 + ry.min(), x0 + rx.max() + 1, y0 + ry.max() + 1
        f = a[by0:by1, bx0:bx1]
        cy = (y0 + y1) / 2
        out[kind] = (f, 0.0 if kind == "fogonazo" else (bx1 - bx0) / 2, cy - by0 if kind == "fogonazo" else (by1 - by0) / 2)
    return out


def export_disparo(dist: Path) -> dict:
    """Las piezas del fogonazo y del impacto a dist/kit/disparo-…png: {de, fogonazo|impacto: [{alfa, nucleo, x, y, w, h,
    tipo, ang}]} (alfa y nucleo: los PNG de las dos mezclas; x, y, w, h en px del juego al largo de hoy; ang en grados)"""
    for old in (dist / "kit").glob("disparo-*.png"):
        old.unlink()
    out: dict = {"de": None}
    if DISPARO_JSON.exists():
        src = json.loads(DISPARO_JSON.read_text())
        for efecto in ("fogonazo", "impacto"):
            lst = []
            for i, pc in enumerate(src.get(efecto, [])):
                names = {"alfa": pc.get("alfa"), "nucleo": pc.get("nucleo")}
                base = pc.get("src", "")
                if not names["alfa"]:
                    names["alfa"] = base if "_alfa" in base else base.replace(".png", "_alfa.png")
                if not names["nucleo"]:
                    names["nucleo"] = names["alfa"].replace("_alfa", "_nucleo")
                item = {"x": pc["x"], "y": pc["y"], "w": pc["w"], "h": pc["h"], "tipo": pc["tipo"], "ang": pc.get("ang")}
                for capa, name in names.items():
                    path = next((p for p in (DISPARO_JSON.parent / name, DISPARO_SET / name) if p.exists()), None)
                    if path is None:
                        continue
                    dst = dist / "kit" / f"disparo-{efecto}-{i}-{capa}.png"
                    Image.open(path).convert("RGBA").save(dst, optimize=True)
                    item[capa] = f"kit/{dst.name}"
                if "alfa" in item:
                    lst.append(item)
            out[efecto] = lst
        out["de"] = "arte"
        return out
    import cv2
    a = np.asarray(Image.open(DISPARO_HOJA).convert("RGB")).astype(np.float32)
    for efecto, (f, ax, ay) in _disparo_cuadros(a).items():
        k = DISPARO_LARGO[efecto] * 2 / f.shape[1]   # al doble del juego
        im = Image.fromarray(f.clip(0, 255).astype(np.uint8)).resize((max(1, round(f.shape[1] * k)), max(1, round(f.shape[0] * k))), Image.LANCZOS)
        f, ax, ay = np.asarray(im).astype(np.float32), ax * k, ay * k
        alpha = f.max(2) / 255
        gray = np.where(alpha[..., None] > 0, f / np.maximum(alpha[..., None], 1e-3), 0).mean(2).clip(0, 255)   # el color des-multiplicado, en gris
        core = np.clip((f.mean(2) / 255 - 0.55) / 0.45, 0, 1)
        yy, xx = np.mgrid[0:f.shape[0], 0:f.shape[1]]
        r = np.hypot(xx - ax, yy - ay)
        lit = alpha > 0.05
        rn = (14 if efecto == "fogonazo" else 10) * 2
        labels = np.zeros(lit.shape, np.int32)
        labels[lit & (r < rn)] = 1   # el núcleo
        rest = lit & (r >= rn)
        n, comp, stats, _ = cv2.connectedComponentsWithStats(cv2.dilate(rest.astype(np.uint8), np.ones((3, 3), np.uint8)), 8)
        big = max(range(1, n), key=lambda i: stats[i, 4]) if n > 1 else 0
        tipos = {1: "nucleo"}
        # el cuerpo grande, en rayos (sectores alrededor del ancla); lo suelto, chispas
        ang = np.degrees(np.arctan2(yy - ay, xx - ax))
        ns = 7 if efecto == "fogonazo" else 8
        lo, hi = (-75, 75) if efecto == "fogonazo" else (-180, 180)
        sector = np.clip(((ang - lo) / (hi - lo) * ns).astype(np.int32), 0, ns - 1)
        nxt = 2
        for si in range(ns):
            m = rest & (comp == big) & (sector == si)
            if m.sum() >= 20:
                labels[m] = nxt; tipos[nxt] = "rayo"; nxt += 1
        for ci in range(1, n):
            if ci == big or stats[ci, 4] < 6:
                continue
            m = rest & (comp == ci)
            if m.sum():
                labels[m] = nxt; tipos[nxt] = "chispa"; nxt += 1
        lst = []
        for li, tipo in tipos.items():
            m = labels == li
            ys_, xs_ = np.nonzero(m)
            if not len(xs_):
                continue
            x0, x1, y0, y1 = xs_.min(), xs_.max() + 1, ys_.min(), ys_.max() + 1
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            item = {"x": round((cx - ax) / 2, 1), "y": round((cy - ay) / 2, 1), "w": round((x1 - x0) / 2, 1), "h": round((y1 - y0) / 2, 1),
                    "tipo": tipo, "ang": round(float(np.degrees(np.arctan2(cy - ay, cx - ax))), 1)}
            mm = m[y0:y1, x0:x1]
            for capa, aa in (("alfa", alpha), ("nucleo", alpha * core)):
                rgba = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
                rgba[..., :3] = gray[y0:y1, x0:x1, None].astype(np.uint8)
                rgba[..., 3] = np.where(mm, aa[y0:y1, x0:x1] * 255, 0).clip(0, 255).astype(np.uint8)
                if capa == "nucleo" and rgba[..., 3].max() < 8:
                    continue
                dst = dist / "kit" / f"disparo-{efecto}-{len(lst)}-{capa}.png"
                Image.fromarray(rgba).save(dst, optimize=True)
                item[capa] = f"kit/{dst.name}"
            lst.append(item)
        out[efecto] = lst
    out["de"] = "mentira"
    return out


def switches_off() -> list[str]:
    """Las animaciones de los interruptores apagados en src.html (OFF_ANIMS)."""
    src = (HERE / "src.html").read_text(encoding="utf-8")
    off = []
    for sw, names in OFF_ANIMS.items():
        m = re.search(rf"\b{sw} = (true|false)\b", src)
        if m and m.group(1) == "false":
            off += names
    return off


def repack(sheet: Image.Image, anims: dict, width: int = 2048, pad: int = 2) -> Image.Image:
    """Un atlas nuevo con sólo los cuadros de `anims` (los mismos recortes, sin repetir los que comparten), en estantes
    de `width`, y los cuadros corridos a su lugar nuevo (x, y del atlas: f[0], f[1])."""
    frames = {id(f): f for a in anims.values() for f in a["f"]}.values()   # shoot_out comparte los de shoot_in
    rects = sorted({tuple(f[:4]) for f in frames}, key=lambda r: (-r[3], -r[2]))
    pos, x, y, shelf = {}, 0, 0, 0
    for r in rects:
        if x + r[2] > width:
            x, y, shelf = 0, y + shelf + pad, 0
        pos[r] = (x, y)
        x += r[2] + pad
        shelf = max(shelf, r[3])
    out = Image.new("RGBA", (width, y + shelf))
    for r, (px, py) in pos.items():
        out.paste(sheet.crop((r[0], r[1], r[0] + r[2], r[1] + r[3])), (px, py))
    for f in frames:
        f[0], f[1] = pos[tuple(f[:4])]
    return out


def export_character(pb, name: str, cfg: dict) -> dict:
    """Las medidas y el atlas de un personaje del selector: {label, spr, atlas} con el atlas como data: URI. El de una
    página va tal cual (PNG); el unido de varias, en WebP sin pérdida (los colores exactos para el recoloreo, ~20%
    menos que en PNG). Lo de `drop` (y, con drop_off, lo apagado en src.html) se saca y el atlas se rearma sin eso."""
    out = ROOT / "characters" / name / "out"
    sheet, frames = pb.load_atlas(out, name, cfg["variant"])
    spr = pb.measure(out, name, cfg["variant"], (sheet, frames))
    drop = [an for an in cfg.get("drop", []) + (switches_off() if cfg.get("drop_off") else []) if an in spr["anims"]]
    for an in drop:
        del spr["anims"][an]
    # nat: el cuadro del clip (nativo) de cada cuadro, de provenance.json; con él, RIG puede nombrar los cuadros por su
    # nativo y sirven a 12 o a 24 fps (natRig en src.html)
    prov = out / "provenance.json"
    if prov.exists():
        pa = json.loads(prov.read_text())["animations"]
        for an, a in spr["anims"].items():
            nat = (pa.get(an, {}).get("timing") or {}).get("native_indices")
            if nat and len(nat) == len(a["f"]):
                a["nat"] = nat
    for an, a in spr["anims"].items():
        fxp = out / "fx" / f"{an}_muzzle.json"
        if cfg.get("fx_muzzle") and fxp.exists():
            fx = json.loads(fxp.read_text())["variants"][cfg["variant"]]["frames"]
            assert len(fx) == len(a["f"]), f"{name}/{an}: {len(fx)} bocas para {len(a['f'])} cuadros"
            for f, m in zip(a["f"], fx):
                f[6], f[7] = round(m["dx"], 1), round(m["dy"], 1)
    for an, n in cfg.get("frames", {}).items():
        if an not in spr["anims"]:
            continue
        a = spr["anims"][an]
        pick = np.round(np.linspace(0, len(a["f"]) - 1, n)).astype(int)
        a["f"] = [a["f"][i] for i in pick]
        if "nat" in a:
            a["nat"] = [a["nat"][i] for i in pick]
    # sin salida de apuntar (el low-poly no la tiene): la entrada al revés
    for b in ("shoot", "shoot2h"):
        if f"{b}_out" not in spr["anims"] and f"{b}_in" in spr["anims"]:
            a = spr["anims"][f"{b}_in"]
            spr["anims"][f"{b}_out"] = {**a, "f": a["f"][::-1], **({"nat": a["nat"][::-1]} if "nat" in a else {})}
    pages = json.loads((out / f"{name}.json").read_text())["variants"][cfg["variant"]]["atlas"]
    if drop:
        sheet = repack(sheet, spr["anims"])
        print(f"  {name}: sin {', '.join(drop)} (atlas de la página {sheet.width} × {sheet.height})")
    if len(pages) == 1 and not drop:
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
    shield = export_hud(pb, dist, SHIELD_SET, SHIELD_ART, "shield", only={"pickup": ["shield"]})
    if "pickup" in shield:   # el power-up del escudo va con los otros dos
        pick.setdefault("pickups", {})["shield"] = shield.pop("pickup")["shield"]
    dust = export_saltos(dist)
    dust["piezas"] = export_piezas(dist)
    dust["disparo"] = export_disparo(dist)
    print(f"  disparo: piezas de {dust['disparo']['de']}: fogonazo {len(dust['disparo'].get('fogonazo', []))}, impacto {len(dust['disparo'].get('impacto', []))}")
    print(f"  efectos del salto: piezas de {dust['piezas']['de']}: " + ", ".join(f"{k} {len(v)}" for k, v in dust["piezas"]["piezas"].items()))
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
    for key, val in (("__CHAR_DATA__", chars), ("__KIT_DATA__", kit), ("__FX_DATA__", fx), ("__ARENA_DATA__", arenas), ("__GRENADE_DATA__", gren), ("__HUD_DATA__", hud), ("__PICKUP_DATA__", pick), ("__LOWFX_DATA__", lowfx), ("__SHIELD_DATA__", shield), ("__DUST_DATA__", dust),
                     ("__COLOR_LUT__", color_lut())):
        html = html.replace(key, json.dumps(val, separators=(",", ":"), ensure_ascii=False))
    (dist / "index.html").write_text(html, encoding="utf-8")
    size = sum(p.stat().st_size for p in dist.rglob("*") if p.is_file()) / 1e6
    print(f"✓ {dist / 'index.html'}  ({len(kit['pieces'])} piezas, {len(kit['layers'])} capas, arenas: "
          f"{', '.join(arenas)}; personajes: {', '.join(chars)}; {size:.1f} MB en dist/, "
          f"{(dist / 'index.html').stat().st_size / 1e6:.1f} MB la página)")


if __name__ == "__main__":
    main()
