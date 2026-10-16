"""Arma props.html, props.md y picked.json: los props de este set a escala del juego, sobre las capas elegidas de
ranger_base, con el ranger al lado, para elegir cuáles quedan y ver dónde irían en el nivel.

    uv run --project pipeline python backgrounds/ranger_props/build_page.py

Lee lo que dejó `spritepipe gen-images` (raw/<hoja>/<opción>.json y post/<hoja>/<opción>/<pieza>.png). Cada hoja
tiene su escala: la pieza ancla de la hoja va al alto de ANCHOR en px del juego y las demás quedan a la escala en
que las dibujó el modelo. La página referencia las imágenes con rutas relativas: se abre desde el disco o con
cualquier servidor estático en la raíz del repo.

picked.json es lo que lee el juego (ver integrar.md): por pieza elegida, el archivo, su `k` (px del juego por px
de la hoja), su tamaño en px del juego, su papel en el nivel y los puntos medidos (en px de la hoja).
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
MODEL = "gpt-image-2.5-sunburst-fal"
OPTIONS = (1, 2)

# pieza ancla de cada hoja y su alto en px del juego (el ranger, al 80%, mide 102)
ANCHOR = {"low_a": ("barrel", 50), "low_b": ("beacon_off", 30), "mid_a": ("console", 70),
          "mid_b": ("monitor_off", 64), "tall": ("door_frame", 140)}

# un prop es una o más piezas de una hoja; los de dos piezas se animan juntos
CONCEPTS = {
    "barrel": ("low_a", ["barrel"]), "explosive_barrel": ("low_a", ["explosive_barrel"]),
    "crate_breakable": ("low_a", ["crate_breakable"]), "cable_coil": ("low_a", ["cable_coil"]),
    "beacon": ("low_b", ["beacon_off", "beacon_on"]), "switch": ("low_b", ["switch_off", "switch_on"]),
    "drone": ("low_b", ["drone"]),
    "console": ("mid_a", ["console"]), "fuel_tank": ("mid_a", ["fuel_tank"]), "turret_off": ("mid_a", ["turret_off"]),
    "crate_stack": ("mid_a", ["crate_stack"]),
    "monitor": ("mid_b", ["monitor_off", "monitor_static"]), "panel_spark": ("mid_b", ["panel_spark"]),
    "fan": ("mid_b", ["fan_housing", "fan_blades"]),
    "antenna": ("tall", ["antenna"]), "signboard": ("tall", ["signboard"]), "door": ("tall", ["door_frame", "door_leaf"]),
}

# la elección del usuario (2026-10-16): la opción de cada prop
PICKED = {"barrel": 2, "explosive_barrel": 2, "crate_breakable": 2, "cable_coil": 1, "beacon": 2, "switch": 1,
          "drone": 1, "console": 2, "fuel_tank": 2, "turret_off": 2, "crate_stack": 1, "monitor": 1, "panel_spark": 2,
          "fan": 2, "antenna": 2, "signboard": 2, "door": 1}

# papel en el nivel: back = detrás de todo lo jugable, con tinte violeta (decorado voluminoso que no hace nada: el
# prototipo sacó las cajas porque "no hacían nada"); fixture = adelante, chico y fijo, se anima; face = en la cara
# de un bloque; target = blanco que se rompe; gate = interruptor y puerta
ROLE = {"barrel": "back", "cable_coil": "back", "console": "back", "fuel_tank": "back", "turret_off": "back",
        "crate_stack": "back", "antenna": "back", "signboard": "back",
        "beacon": "fixture", "monitor": "fixture", "panel_spark": "fixture", "drone": "fixture", "fan": "face",
        "explosive_barrel": "target", "crate_breakable": "target", "switch": "gate", "door": "gate"}

# por pieza: tipo (decorado | vida | función), capa en el juego y qué haría
META = {
    "barrel": ("decorado", "fondo", "Barril de acero. Al fondo, al lado de los explosivos: el rojo es el que se rompe."),
    "explosive_barrel": ("función", "juego · blanco", "Blanco: con dos tiros revienta (burst naranja y rojo grande, "
                                                      "shake). Más adelante, daño en área."),
    "crate_breakable": ("función", "juego · blanco", "Blanco con hp, como el tablero; al romperse, astillas con burst()."),
    "cable_coil": ("decorado", "fondo", "Rollo de cable al pie de la antena o de la consola."),
    "beacon_off": ("vida", "juego · tope de bloques", "Baliza apagada: alterna con la prendida."),
    "beacon_on": ("vida", "juego · tope de bloques", "Baliza prendida, con su halo: parpadeo cada ~0,5 s, desfasadas "
                                                     "entre sí."),
    "switch_off": ("función", "juego · puerta", "Interruptor: al dispararle pasa a on y abre la puerta."),
    "switch_on": ("función", "juego · puerta", "El interruptor accionado."),
    "drone": ("vida", "juego", "Dron estacionado en su base; más adelante puede despegar cuando el ranger se acerca."),
    "console": ("decorado", "fondo", "Consola con pantallas."),
    "fuel_tank": ("decorado", "fondo", "Tanque de combustible."),
    "turret_off": ("decorado", "fondo", "Torreta apagada; más adelante, un enemigo que se prende y pasa al juego."),
    "crate_stack": ("decorado", "fondo", "Cajas apiladas. Si se quieren en el juego, como sólido que se sube."),
    "monitor_off": ("vida", "juego", "Monitor apagado: alterna con la estática."),
    "monitor_static": ("vida", "juego", "Estática: se anima espejando la pantalla cada ~80 ms y a ratos se apaga."),
    "panel_spark": ("vida", "juego", "Tablero abierto: chispas cian con burst() cada 0,6–2 s."),
    "fan_housing": ("vida", "juego · cara de un bloque", "Marco del ventilador, pegado a la cara de un bloque."),
    "fan_blades": ("vida", "juego · cara de un bloque", "Aspas: giran por código dentro del marco (escaladas al hueco)."),
    "antenna": ("decorado", "fondo", "Mástil de comunicaciones, detrás de la capa de juego."),
    "signboard": ("decorado", "fondo", "Cartel de la base con emblema."),
    "door_frame": ("función", "juego · puerta", "Marco de la puerta: detrás del ranger, adelante de la hoja."),
    "door_leaf": ("función", "juego · puerta", "Hoja: sólido que corta el paso; sube detrás del marco cuando se acciona "
                                               "el interruptor."),
}

# el nivel del prototipo, copiado de prototypes/ranger/src.html el 2026-10-16 (con los cambios sin commitear de la
# sesión que lo edita): bloques (x, alto, ancho), plataformas (x, alto del tope, ancho), blancos (x, alto de la base)
LEVEL = {
    "w": 5000, "ranger": 300, "signs": [470, 3170],
    "blocks": [[860, 84, 220], [1240, 196, 200], [1960, 150, 150], [2110, 230, 170], [2800, 250, 260],
               [3300, 230, 130], [3590, 370, 150], [4450, 220, 240]],
    "slabs": [[1560, 300, 240], [2420, 330, 200], [4125, 360, 160]],
    "boards": [[640, 0], [1340, 196], [1690, 300], [2520, 330], [2620, 0], [2930, 250], [3680, 370], [4190, 360],
               [4860, 0]],
    "cans": [[930, 84], [1010, 84], [2030, 150], [2190, 230], [2240, 230], [3365, 230], [4600, 220]],
}
# dónde irían: prop, x del centro, alto de la base sobre el piso (0 = piso; en un bloque, su alto) y, en los
# ventiladores, el bloque en cuya cara van
PLAN = [
    ["antenna", 120, 0], ["cable_coil", 232, 0], ["console", 385, 0], ["monitor", 548, 0],
    ["beacon", 1055, 84], ["barrel", 1122, 0], ["explosive_barrel", 1168, 0], ["beacon", 1400, 196],
    ["panel_spark", 1512, 0], ["fuel_tank", 1680, 0], ["drone", 1885, 0],
    ["fan", 2195, 230, {"block": 3}], ["crate_stack", 2350, 0], ["crate_breakable", 2560, 0], ["turret_off", 2730, 0],
    ["beacon", 3030, 250], ["beacon", 3722, 370], ["fan", 3665, 370, {"block": 6}],
    ["switch", 3790, 0], ["door", 3890, 0], ["explosive_barrel", 4060, 0], ["signboard", 4370, 0],
    ["crate_breakable", 4745, 0],
]


def measure(piece: str, im: np.ndarray) -> dict:
    """Puntos que usa la escena, en px de la pieza: lo opaco (sin el halo, para apoyarla en el piso), el hueco del
    ventilador, el vano de la puerta, la pantalla del monitor, la chispa."""
    a, rgb = im[..., 3], im[..., :3].astype(int)
    h, w = a.shape
    ys, xs = np.nonzero(a > 200)
    out = {"solid": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1]}
    if piece == "monitor_static":
        # la estática: grises y blancos claros (el marco es azul acero, más oscuro)
        ys, xs = np.nonzero((a > 200) & (rgb.min(2) > 110) & (rgb.max(2) - rgb.min(2) < 40))
        out["screen"] = [int(xs.min()), int(ys.min()), int(xs.max() - xs.min()) + 1, int(ys.max() - ys.min()) + 1]
    elif piece == "fan_housing":
        dark = (a > 200) & (rgb.max(2) < 40)
        dark[: h // 6], dark[-h // 6:], dark[:, : w // 6], dark[:, -w // 6:] = False, False, False, False
        ys, xs = np.nonzero(dark)
        out["hole"] = [round(float(xs.mean()), 1), round(float(ys.mean()), 1), round((xs.max() - xs.min()) / 2, 1)]
    elif piece == "door_frame":
        xs = np.nonzero(a[int(h * 0.6)] < 20)[0]
        xs = xs[(xs > w * 0.1) & (xs < w * 0.9)]
        ys = np.nonzero(a[:, w // 2] < 20)[0]
        out["opening"] = [int(xs.min()), int(ys.min()), int(xs.max()) + 1, h]
    elif piece == "panel_spark":
        ys, xs = np.nonzero((a > 200) & (rgb[..., 0] > 200) & (rgb[..., 1] > 230) & (rgb[..., 2] > 230))
        if len(xs):
            out["spark"] = [round(float(xs.mean()), 1), round(float(ys.mean()), 1)]
    return out


def collect() -> dict:
    sheets = {}
    for sheet, (anchor, anchor_h) in ANCHOR.items():
        sheets[sheet] = {}
        for n in OPTIONS:
            opt = f"{MODEL}_{n}"
            rep = HERE / "raw" / sheet / f"{opt}.json"
            if not rep.exists():
                continue
            post = json.loads(rep.read_text())["post"]
            files = post["files"]
            k = anchor_h / files[anchor]["h"]
            pieces = {}
            for piece, f in files.items():
                src = HERE / "post" / sheet / opt / f["file"]
                pieces[piece] = {"src": f"post/{sheet}/{opt}/{f['file']}", "w": f["w"], "h": f["h"],
                                 "gw": round(f["w"] * k, 1), "gh": round(f["h"] * k, 1),
                                 **measure(piece, np.asarray(Image.open(src).convert("RGBA")))}
            sheets[sheet][str(n)] = {"k": round(k, 5), "pieces": pieces, "notes": post.get("notes", [])}
    return sheets


def picked(sheets: dict) -> dict:
    """Lo que lee el juego: las piezas elegidas, cada una con su k. Las aspas van al diámetro del hueco del marco."""
    out = {}
    for concept, n in PICKED.items():
        sheet, names = CONCEPTS[concept]
        o = sheets[sheet][str(n)]
        for name in names:
            p, k = o["pieces"][name], o["k"]
            if name == "fan_blades":
                hr = o["pieces"]["fan_housing"]["hole"][2]
                k = k * 2 * hr * 1.02 / p["w"]
            out[name] = {"file": p["src"], "sheet": sheet, "option": n, "role": ROLE[concept], "k": round(k, 5),
                         "w": round(p["w"] * k, 2), "h": round(p["h"] * k, 2),
                         **{m: p[m] for m in ("solid", "screen", "hole", "opening", "spark") if m in p}}
    return {"set": "ranger_props", "chosen": "2026-10-16",
            "note": "w y h en px del juego; solid, screen, hole, opening y spark en px de la hoja (por k da px del "
                    "juego). role: back | fixture | face | target | gate (ver integrar.md)",
            "pieces": out}


def base_data() -> dict:
    """Las capas, el kit y los props elegidos de ranger_base, como los usa prototypes/build.py."""
    base = HERE.parent / "ranger_base"
    layers = {}
    for layer, opt in {"sky": "nano-banana-2.1_3", "far": "nano-banana-2.1_2", "mid": "nano-banana-2.1_1",
                       "near": "nano-banana-2.1_2"}.items():
        post = json.loads((base / "raw" / layer / f"{opt}.json").read_text())["post"]
        k, f = 540 / post["source"]["h"], post["files"]["image"]
        layers[layer] = {"src": f"../ranger_base/post/{layer}/{f['file']}", "w": round(f["w"] * k, 2),
                         "h": round(f["h"] * k, 2)}
    kit, props = {}, {}
    for out, asset, k in ((kit, "platform_kit", 0.2), (props, "props", 92 / 876)):
        opt = f"{MODEL}_1"
        post = json.loads((base / "raw" / asset / f"{opt}.json").read_text())["post"]
        for piece, f in post["files"].items():
            out[piece] = {"src": f"../ranger_base/post/{asset}/{opt}/{f['file']}", "w": round(f["w"] * k, 2),
                          "h": round(f["h"] * k, 2), "k": round(k, 5)}
    idx = json.loads((HERE.parents[1] / "characters/ranger/out/sheets/1x/idle.json").read_text())
    ranger = {"src": "../../characters/ranger/out/sheets/1x/idle.png", "cw": idx["cell"]["w"],
              "ch": idx["cell"]["h"], "n": idx["count"], "px": idx["pivot"]["x"] * idx["cell"]["w"],
              "py": idx["pivot"]["y"] * idx["cell"]["h"], "ms": idx["durations_ms"][0]}
    return {"layers": layers, "kit": kit, "props": props, "ranger": ranger}


def write_md(sheets: dict) -> None:
    rows = ["# ranger_props: props de prueba", "",
            "Tamaño en px del juego (vista de 960×540, piso en y = 474, el ranger al 80% mide 102 px). Cada hoja va "
            "a su propia escala: la pieza ancla al alto de `ANCHOR` en `build_page.py`. Capa: *fondo* es detrás de "
            "todo lo jugable, a la velocidad del mundo y con un tinte violeta; *juego* es el plano del ranger. "
            "**Elegida** es la opción que quedó (2026-10-16). Abrí `props.html` para verlos en la escena y en el "
            "nivel, y `integrar.md` para meterlos al prototipo.", "",
            "| prop | hoja | tipo | capa | opción 1 (px) | opción 2 (px) | elegida | idea |",
            "|---|---|---|---|---|---|---|---|"]
    by_piece = {p: c for c, (_, names) in CONCEPTS.items() for p in names}
    for sheet, opts in sheets.items():
        for piece in next(iter(opts.values()))["pieces"]:
            kind, layer, idea = META.get(piece, ("?", "?", ""))
            size = [f"{round(o['pieces'][piece]['gw'])}×{round(o['pieces'][piece]['gh'])}"
                    if piece in o["pieces"] else "—" for o in (opts.get(str(n), {"pieces": {}}) for n in OPTIONS)]
            chosen = PICKED.get(by_piece.get(piece))
            rows.append(f"| `{piece}` | {sheet} | {kind} | {layer} | {size[0]} | {size[1]} | "
                        f"{chosen or '—'} | {idea} |")
    rows += ["", "Escala de cada hoja (px del juego por px de la hoja): " + ", ".join(
        f"{s} {' / '.join(str(o['k']) for o in opts.values())}" for s, opts in sheets.items()) + "."]
    (HERE / "props.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    sheets = collect()
    pick = picked(sheets)
    (HERE / "picked.json").write_text(json.dumps(pick, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    data = {"sheets": sheets, "anchor": ANCHOR, "meta": META, "base": base_data(), "concepts": CONCEPTS,
            "picked": {c: str(n) for c, n in PICKED.items()}, "role": ROLE, "level": LEVEL, "plan": PLAN}
    tpl = (HERE / "props_template.html").read_text(encoding="utf-8")
    html = tpl.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    (HERE / "props.html").write_text(html, encoding="utf-8")
    write_md(sheets)
    print(f"✓ {HERE / 'props.html'}, props.md y picked.json ({len(sheets)} hojas, "
          f"{sum(len(o) for o in sheets.values())} imágenes, {len(pick['pieces'])} piezas elegidas)")


if __name__ == "__main__":
    main()
