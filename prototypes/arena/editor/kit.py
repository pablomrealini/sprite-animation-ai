"""Pasa el kit de piezas de Arte a las arenas: prototypes/arena/arenas/kit_lowpoly/ con las piezas, el fondo y kit.json.

uso (desde la raíz del repo; no gasta):
    uv run --project pipeline python prototypes/arena/editor/kit.py
    uv run --project pipeline python prototypes/arena/editor/kit.py --entrega backgrounds/lowpoly_kit/entrega \
        --fondo backgrounds/lowpoly_fondos/entrega/abierta_3.webp

La entrega de Arte (backgrounds/lowpoly_kit/entrega: PNG a px del juego y medidas.json con el tamaño y la línea de los
pies de cada pieza) se copia tal cual a arenas/kit_lowpoly/, y el fondo de 2496 × 1404 a arenas/kit_lowpoly/fondos/. Las
imágenes tienen que estar adentro de arenas/: el juego las busca ahí (build.py copia a dist/arenas/ las que usa cada
arena). kit.json es lo que muestra el editor en "Kit low-poly"; al poner una pieza, su definición se copia a la arena
(pieces), así que el juego no necesita nada nuevo. Por pieza:
- solids: la colisión, con la y en la línea de los pies y el ancho de lo que se ve de la cara de arriba;
- legs: la franja que se estira a lo alto (patas, pilares, el caño vertical), medida en el alfa: la tira más larga de
  filas iguales (sólo cosas verticales), con 2 filas de margen. legsGap: cuántos px por encima de la línea de los pies de
  lo de abajo terminan: APOYO = −8, 8 px adentro de la cara de arriba de lo de abajo, así la base la pisa (con el 16 de
  la revisión de Arte, una pasarela sobre otra quedaba 13 px flotando sobre la losa);
- espejo (sólo del editor): con qué se hace la copia del otro lado. "mismo": la misma pieza sin espejar (las simétricas,
  así la luz sigue viniendo de la izquierda); otra pieza: la del otro lado (las puntas). Sin espejo: se espeja (flip);
- deco (sólo del editor): decorado sin colisión, que se pone detrás de todo;
- tramo (sólo del editor): "x" las que se repiten a lo ancho una al lado de la otra (los medios de la pasarela, el caño
  horizontal), "y" la que se estira a lo alto (el caño vertical).
"""
import argparse
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
APOYO = -8   # legsGap de lo que se apoya (ver arriba)
ARENA = HERE.parent
ROOT = ARENA.parent.parent
OUT = ARENA / "arenas" / "kit_lowpoly"

# grupo de la paleta, colisión (bridge se atraviesa desde abajo; walk es bloque), si se estira y cómo se espeja
PIEZAS = {
    "pasarela_punta_izq": dict(grupo="Pasarelas", solido="bridge", patas=True, gap=APOYO, espejo="pasarela_punta_der"),
    "pasarela_medio_a": dict(grupo="Pasarelas", solido="bridge", patas=True, gap=APOYO, espejo="mismo", tramo="x"),
    "pasarela_medio_b": dict(grupo="Pasarelas", solido="bridge", espejo="mismo", tramo="x"),
    "pasarela_punta_der": dict(grupo="Pasarelas", solido="bridge", patas=True, gap=APOYO, espejo="pasarela_punta_izq"),
    "flotante_200": dict(grupo="Flotantes", solido="bridge", espejo="mismo"),
    "flotante_300": dict(grupo="Flotantes", solido="bridge", espejo="mismo"),
    "flotante_450": dict(grupo="Flotantes", solido="bridge", espejo="mismo"),
    "ascensor": dict(grupo="Flotantes", solido="bridge", espejo="mismo"),
    "columna_ancha": dict(grupo="Columnas y bloques", solido="bridge", patas=True, gap=APOYO, espejo="mismo"),
    "columna_angosta": dict(grupo="Columnas y bloques", patas=True, gap=APOYO, espejo="mismo"),
    # bloque y pared frenan balas (walk): no se estiran, porque el juego no le suma el estirado al alto de la colisión
    "bloque": dict(grupo="Columnas y bloques", solido="walk", espejo="mismo"),
    "pared": dict(grupo="Columnas y bloques", solido="walk", espejo="mismo"),
    "guia_ascensor": dict(grupo="Columnas y bloques", patas=True, gap=APOYO, espejo="mismo", deco=True),
    "deco_tanque": dict(grupo="Decorado", deco=True),
    "deco_chimenea": dict(grupo="Decorado", deco=True),
    "deco_torre": dict(grupo="Decorado", deco=True),
    "deco_codo": dict(grupo="Decorado", deco=True),
    "deco_cano_h": dict(grupo="Decorado", deco=True, espejo="mismo", tramo="x"),
    "deco_cano_v": dict(grupo="Decorado", deco=True, patas="todo", gap=APOYO, espejo="mismo", tramo="y"),
}


def band(alpha: np.ndarray, start: int) -> list[int] | None:
    """La tira más larga de filas con el mismo alfa (sólo cosas verticales) desde la fila start, con 2 de margen."""
    m = alpha > 128
    best, run0 = (0, 0), None
    for y in range(max(1, start), m.shape[0]):
        same = m[y].any() and np.array_equal(m[y], m[y - 1])
        if same and run0 is None:
            run0 = y - 1
        if (not same or y == m.shape[0] - 1) and run0 is not None:
            end = y if same else y - 1
            if end - run0 > best[1] - best[0]:
                best = (run0, end)
            run0 = None
    return [best[0] + 2, best[1] - 2] if best[1] - best[0] >= 12 else None


def top_span(alpha: np.ndarray, feet: int) -> tuple[int, int]:
    """Lo que se ve de la cara de arriba: las columnas con algo en la fila de los pies + 4."""
    cols = np.nonzero(alpha[min(alpha.shape[0] - 1, feet + 4)] > 128)[0]
    return (int(cols[0]), int(cols[-1]) + 1) if len(cols) else (0, alpha.shape[1])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--entrega", default="backgrounds/lowpoly_kit/entrega")
    ap.add_argument("--fondo", action="append", default=None, help="fondo de 2496 × 1404 (se puede repetir)")
    args = ap.parse_args()
    src = ROOT / args.entrega
    med = json.loads((src / "medidas.json").read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    pieces, seams = {}, []
    for name, cfg in PIEZAS.items():
        if name not in med:
            print(f"  falta {name} en la entrega")
            continue
        m, png = med[name], src / f"{name}.png"
        im = Image.open(png).convert("RGBA")
        a = np.asarray(im)[..., 3]
        if im.size != (m["w"], m["h"]):
            raise SystemExit(f"{name}: el PNG mide {im.size} y medidas.json dice {m['w']} × {m['h']}")
        shutil.copy2(png, OUT / png.name)
        p = {"src": f"kit_lowpoly/{png.name}", "w": m["w"], "h": m["h"], "grupo": cfg["grupo"]}
        feet = m.get("pies")
        if cfg.get("solido") and feet is not None:
            x0, x1 = (0, m["w"]) if cfg.get("tramo") == "x" else top_span(a, feet)
            s = {"kind": cfg["solido"], "x": x0, "y": feet, "w": x1 - x0}
            if cfg["solido"] == "walk":
                s["h"] = m["h"] - feet
            p["solids"] = [s]
        if cfg.get("patas") == "todo":
            p["legs"], p["legsGap"] = [2, m["h"] - 2], cfg.get("gap", 0)
        elif cfg.get("patas"):
            L = band(a, (feet or 0) + 40)
            if L:
                p["legs"], p["legsGap"] = L, cfg.get("gap", 0)
        for k in ("espejo", "deco", "tramo"):
            if cfg.get(k):
                p[k] = cfg[k]
        pieces[name] = p
        if cfg.get("tramo") == "x" or name.startswith("pasarela_punta"):
            # el borde que empalma: alfa de las columnas de los costados en las filas de la losa
            rows = slice((feet or 0) + 2, (feet or 0) + 50) if feet is not None else slice(0, m["h"])
            seams.append(f"{name}: alfa del borde izq {int(a[rows, 0].min())}–{int(a[rows, 0].max())}, der {int(a[rows, -1].min())}–{int(a[rows, -1].max())}")
    fondos = []
    for f in args.fondo or ["backgrounds/lowpoly_fondos/entrega/abierta_3.webp"]:
        fp = ROOT / f
        im = Image.open(fp)
        (OUT / "fondos").mkdir(exist_ok=True)
        shutil.copy2(fp, OUT / "fondos" / fp.name)
        fondos.append({"src": f"kit_lowpoly/fondos/{fp.name}", "size": list(im.size), "piso": im.size[1] - 140})
    kit = {"name": "Kit low-poly", "origen": args.entrega, "nota": "Lo arma prototypes/arena/editor/kit.py; no se edita a mano.",
           "fondos": fondos, "pieces": pieces}
    (OUT / "kit.json").write_text(json.dumps(kit, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"✓ {OUT.relative_to(ROOT)}/kit.json: {len(pieces)} piezas, {len(fondos)} fondo(s)")
    for n, p in pieces.items():
        print(f"  {n:20s} {p['w']:4d} × {p['h']:3d}  sólido {p.get('solids')}  patas {p.get('legs')} (hueco {p.get('legsGap')})")
    print("bordes:", *seams, sep="\n  ")


if __name__ == "__main__":
    main()
