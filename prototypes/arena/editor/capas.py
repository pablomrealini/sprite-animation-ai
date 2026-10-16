"""Pasa una arena de lámina entera a "lámina en capas": el fondo sin las pasarelas y cada pasarela como pieza que se mueve.

uso (desde la raíz del repo):
    uv run --project pipeline python prototypes/arena/editor/capas.py refineria \
        backgrounds/arena_refineria/post/plate_no_walkways/nano-banana-2.1_1.png \
        --fill backgrounds/arena_refineria/post/plate_no_walkways_fill/nano-banana-2.1_2.png \
        --fill-ref backgrounds/arena_refineria/refs/no_walkways_hueco.png

No gasta: usa la arena de lámina entera (arenas/<arena>/entera.json: la lámina con la colisión calcada; la primera vez
se copia de arenas/<arena>.json) y una edición del modelo con las pasarelas sacadas.
1. La edición vuelve estirada (2752 × 1536 por una referencia de 1920 × 1080): se achica a 1920 × 1080 sin recortar y
   se prueba correrla hasta ±4 px; queda el corrimiento con menos diferencia fuera de las piezas. Si la edición dejó
   algo (en Refinería, un muñón de cada pasarela pegado a la pared), --fill es una segunda edición que rellenó lo que
   estaba en magenta en --fill-ref: de ella se usa sólo eso.
2. La máscara de cada pieza es lo que no es neblina azul del fondo (las patas son grises oscuras, las losas claras, las
   luces cian), dentro de la zona de esa pieza (LEFT: la losa y lo que cuelga abajo, hasta lo de abajo) y pegado a la
   losa. Por diferencia con la edición no alcanzaba: donde el modelo pintó una torre oscura detrás, la pata se perdía.
3. Cada pieza es un PNG con alfa recortado de la lámina, con su colisión (el puente del JSON) y sus recortes de adelante
   (plate.solid) relativos a la pieza. El fondo es la lámina con la edición sólo debajo de las piezas, así lo demás
   queda píxel a píxel.
Escribe arenas/<arena>/fondo.webp, arenas/<arena>/<pieza>.png y arenas/<arena>.json, la arena en capas del menú del
juego (con las piezas donde estaban en la lámina). Si esa ya está en capas no la pisa (pueden ser cambios del editor),
salvo con --force. --check deja imágenes para comprobar: la arena armada de nuevo contra la lámina, y las piezas.
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ARENA = HERE.parent
ROOT = ARENA.parent.parent
AW, AH = 1920, 1080

# las piezas de cada arena: nombre, el sólido del JSON (índice en solids) y el recorte de adelante (índice en
# plate.solid) que van con ella, y su zona en px del juego: [x, y, w, h], primero la losa y después lo que cuelga.
# Las de la derecha son las de la izquierda espejadas (la arena es simétrica)
LEFT = {
    "refineria": [
        ("pasarela_abajo", 1, 4, [[0, 708, 668, 78], [112, 784, 614, 147], [636, 724, 92, 207]]),
        ("pasarela_medio", 3, 2, [[362, 518, 442, 70], [376, 586, 316, 122]]),
        ("pasarela_arriba", 5, 0, [[0, 328, 530, 70], [200, 398, 330, 120]]),
    ],
}
RIGHT_OF = {1: 2, 3: 4, 5: 6, 4: 5, 2: 3, 0: 1}   # el sólido / recorte de la derecha de cada uno de la izquierda
# las patas de cada pieza (las dos de cada par, que son espejo): la franja de filas entre la losa y los pies que se estira
# cuando la pasarela sube (legs, relativa a la pieza recortada) y cuántos px por encima de la línea de los pies de lo de
# abajo terminan (legsGap, medido con las piezas donde estaban en la lámina). Si cambia el recorte, hay que medirlas de nuevo
LEGS = {
    "refineria": {"pasarela_abajo": ([80, 160], 8), "pasarela_medio": ([68, 178], 15), "pasarela_arriba": ([78, 176], 13)},
}


def pieces_for(name: str, arena: dict) -> list:
    out = []
    for base, si, fi, rects in LEFT[name]:
        out.append((f"{base}_izq", si, fi, rects))
        out.append((f"{base}_der", RIGHT_OF[si], RIGHT_OF[fi], [[AW - x - w, y, w, h] for x, y, w, h in rects]))
    return out


def align(big: Image.Image, plate: np.ndarray, keep: np.ndarray) -> tuple[np.ndarray, tuple[int, int], float]:
    """La edición a 1920 × 1080 (sin recortar) y corrida lo que haga falta para calzar con la lámina fuera de `keep`."""
    e = np.asarray(big.convert("RGB").resize((AW, AH), Image.LANCZOS)).astype(np.float32)
    best = None
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            sh = np.roll(e, (dy, dx), axis=(0, 1))
            d = np.abs(sh - plate).max(2)[8:-8, 8:-8][~keep[8:-8, 8:-8]]
            score = float(np.mean(np.minimum(d, 60)))
            if best is None or score < best[2]:
                best = (sh, (dx, dy), score)
    return best


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("arena")
    ap.add_argument("empty", help="la edición sin pasarelas (post/<asset>/<modelo>_<n>.png)")
    ap.add_argument("--fill", help="la edición que rellenó el magenta de --fill-ref")
    ap.add_argument("--fill-ref", help="la referencia de --fill: la edición alineada, con lo que sobraba en magenta")
    ap.add_argument("--check", type=Path, help="carpeta donde dejar las imágenes de comprobación")
    ap.add_argument("--force", action="store_true", help="pisar arenas/<arena>.json aunque ya esté en capas")
    args = ap.parse_args()

    out_dir = ARENA / "arenas" / args.arena
    out_dir.mkdir(exist_ok=True)
    menu, src = ARENA / "arenas" / f"{args.arena}.json", out_dir / "entera.json"
    if not src.exists():   # la primera vez: la arena de lámina entera queda como fuente, fuera del menú
        if "pieces" in json.loads(menu.read_text(encoding="utf-8")):
            raise SystemExit(f"{menu.relative_to(ROOT)} ya está en capas y no hay {src.relative_to(ROOT)}")
        src.write_text(menu.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"  {menu.relative_to(ROOT)} → {src.relative_to(ROOT)} (la fuente, de lámina entera)")
    if menu.exists() and "pieces" in json.loads(menu.read_text(encoding="utf-8")) and not args.force:
        raise SystemExit(f"{menu.relative_to(ROOT)} ya está en capas (¿cambios del editor?): --force para pisarla")
    arena = json.loads(src.read_text(encoding="utf-8"))
    plate_rgb = np.asarray(Image.open(ARENA / "arenas" / arena["plate"]["src"]).convert("RGB")).astype(np.float32)
    pieces = pieces_for(args.arena, arena)

    zones = []
    for name, si, fi, rects in pieces:
        z = np.zeros((AH, AW), bool)
        for x, y, w, h in rects:
            z[max(0, y):y + h, max(0, x):x + w] = True
        zones.append(z)
    anyzone = np.any(zones, axis=0)
    empty, shift, score = align(Image.open(ROOT / args.empty), plate_rgb, anyzone)
    print(f"edición alineada: corrida {shift[0]:+d}, {shift[1]:+d} px (diferencia media fuera de las piezas {score:.1f})")
    mag = None
    if args.fill:
        ref = np.asarray(Image.open(ROOT / args.fill_ref).convert("RGB")).astype(np.int16)
        mag = (ref[..., 0] > 250) & (ref[..., 1] < 5) & (ref[..., 2] > 250)
        fill, fshift, fscore = align(Image.open(ROOT / args.fill), plate_rgb, anyzone | mag)
        print(f"relleno alineado: corrida {fshift[0]:+d}, {fshift[1]:+d} px ({fscore:.1f}); se usan {int(mag.sum())} px")
        m = cv2.GaussianBlur(cv2.dilate(mag.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(np.float32), (9, 9), 0)[..., None]
        empty = empty * (1 - m) + fill * m

    plate_rgba = np.dstack([plate_rgb, np.full((AH, AW), 255, np.float32)]).astype(np.uint8)
    owner = np.full((AH, AW), -1, np.int16)   # de qué pieza es cada píxel: las losas primero
    for k, (name, si, fi, rects) in enumerate(pieces):
        x, y, w, h = rects[0]
        owner[y:y + h, max(0, x):x + w] = np.where(owner[y:y + h, max(0, x):x + w] < 0, k, owner[y:y + h, max(0, x):x + w])
    for k, z in enumerate(zones):
        owner[(owner < 0) & z] = k

    # la neblina azul del fondo (cielo, refinería lejana): lo que se ve entre las patas y las cruces de un andamio no es
    # de la pieza. Las patas son grises oscuras y las luces, cian
    R, G, B = plate_rgb[..., 0], plate_rgb[..., 1], plate_rgb[..., 2]
    # la neblina es clara (las sombras azul oscuro de un andamio no), y el brillo alrededor de una luz cian es de la luz
    bright = cv2.dilate(((G > 200) & (B > 220)).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
    haze = (B - R > 30) & (B - G > 15) & (G < 190) & (G < 0.72 * B) & (B >= 95) & ~bright

    # lo que el modelo dejó igual, en manchas grandes, es del fondo aunque toque la pasarela (un caño que pasa por
    # debajo, la pared): no va en la pieza. Las motas sueltas iguales son ruido y quedan
    same = (np.abs(cv2.GaussianBlur(plate_rgb, (5, 5), 0) - cv2.GaussianBlur(empty, (5, 5), 0)).max(2) < 12).astype(np.uint8)
    # (lo que se rellenó del magenta es nuevo: ahí nada quedó). Los caños rojos, con más tolerancia y con su contorno
    fresh = np.zeros((AH, AW), bool) if not args.fill else mag
    def big(m, min_area, red=False):
        n, lab, st, _ = cv2.connectedComponentsWithStats((m & anyzone & ~haze & ~fresh).astype(np.uint8), connectivity=8)
        ok = [i for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= min_area
              and (not red or plate_rgb[..., 0][lab == i].mean() > plate_rgb[..., 1][lab == i].mean() + 40)]
        return np.isin(lab, ok)
    alike = np.abs(cv2.GaussianBlur(plate_rgb, (5, 5), 0) - cv2.GaussianBlur(empty, (5, 5), 0)).max(2) < 20
    kept_bg = big(same > 0, 2500) | cv2.dilate(big(alike, 1500, red=True).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)

    defs, objects, allmask, allcore = {}, [], np.zeros((AH, AW), np.float32), np.zeros((AH, AW), bool)
    for k, (name, si, fi, rects) in enumerate(pieces):
        mine = owner == k
        # la losa, entera: el recorte de adelante (plate.solid) es opaco aunque el modelo haya dejado algo parecido
        fx, fy, fw, fh = arena["plate"]["solid"][fi]
        deck = np.zeros((AH, AW), bool)
        deck[fy:fy + fh, max(0, fx):fx + fw] = True
        deck &= mine
        core = (mine & ~haze & ~kept_bg) | deck
        # sin líneas sueltas de 1 o 2 px (el contorno de algo del fondo que quedó afuera)
        core = cv2.morphologyEx(core.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)).astype(bool) | deck
        # sólo lo que está pegado a la losa: los pedazos sueltos (un caño, una mota) quedan en el fondo
        n, lab = cv2.connectedComponents(core.astype(np.uint8), connectivity=8)
        keep = np.unique(lab[deck & (lab > 0)])
        core = np.isin(lab, keep) & (lab > 0)
        # los agujeros chicos (el brillo de una luz, una mota de neblina en un panel) se tapan; los grandes (entre las
        # cruces de un andamio) son fondo y quedan
        n, lab, st, _ = cv2.connectedComponentsWithStats((~core).astype(np.uint8), connectivity=4)
        for i in np.nonzero(st[1:, cv2.CC_STAT_AREA] < 600)[0] + 1:
            core |= (lab == i) & mine
        m8 = core.astype(np.uint8)
        allcore |= core
        alpha = np.clip(cv2.GaussianBlur(m8.astype(np.float32), (3, 3), 0) * 1.35, 0, 1)   # borde de 1 px, suave
        ys, xs = np.nonzero(alpha > 0.02)
        bx, by, bx1, by1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
        rgba = plate_rgba[by:by1, bx:bx1].copy()
        rgba[..., 3] = np.round(alpha[by:by1, bx:bx1] * 255).astype(np.uint8)
        Image.fromarray(rgba, "RGBA").save(out_dir / f"{name}.png", optimize=True)
        allmask = np.maximum(allmask, alpha)
        s = arena["solids"][si]
        defs[name] = {
            "src": f"{args.arena}/{name}.png", "w": bx1 - bx, "h": by1 - by,
            "solids": [{"kind": s["kind"], "x": s["x"] - bx, "y": s["y"] - by, "w": s["w"], "ledge": "both"}],
            "front": [[fx - bx, fy - by, fw, fh]],
        }
        legs = LEGS.get(args.arena, {}).get(name.rsplit("_", 1)[0])
        if legs:
            defs[name]["legs"], defs[name]["legsGap"] = legs
        objects.append({"piece": name, "x": bx, "y": by})
        print(f"  {name}: {bx1 - bx} × {by1 - by} en {bx}, {by}  ({int(m8.sum())} px)")

    # lo que es de una pieza pero la edición dejó igual (un brazo de una cruz, una luz) no puede quedar en el fondo: se
    # borra rellenando con lo de alrededor
    left = cv2.dilate((allcore & (same > 0)).astype(np.uint8), np.ones((5, 5), np.uint8))
    print(f"  lo que la edición dejó de las piezas: {int(left.sum())} px, rellenados con lo de alrededor")
    if left.any():
        empty = cv2.inpaint(np.clip(empty, 0, 255).astype(np.uint8), left, 9, cv2.INPAINT_TELEA).astype(np.float32)
    # el fondo: la lámina, y la edición sólo donde había pieza (un poco más ancho, sin salir de su zona, con transición)
    grow = (cv2.dilate((allmask > 0.02).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) & anyzone).astype(np.float32)
    grow = cv2.GaussianBlur(grow, (7, 7), 0)[..., None]
    fondo = plate_rgb * (1 - grow) + empty * grow
    Image.fromarray(np.clip(np.round(fondo), 0, 255).astype(np.uint8), "RGB").save(out_dir / "fondo.webp", quality=92, method=6)

    # la arena en capas: lo fijo (piso, columna y su recorte) queda; las pasarelas pasan a objetos con su pieza
    used_s = {si for _, si, _, _ in pieces}
    used_f = {fi for _, _, fi, _ in pieces}
    layered = {k: v for k, v in arena.items() if k not in ("plate", "solids", "objects")}
    layered["note"] = (f"Px del juego, y para abajo. Lámina en capas: la armó prototypes/arena/editor/capas.py desde "
                       f"arenas/{args.arena}/entera.json (la lámina entera con la colisión calcada, y su historia). plate.src "
                       "es el fondo sin las pasarelas y cada pasarela es una pieza pintada (pieces: PNG con alfa, 1 px = 1 px "
                       "del juego) puesta como objeto (x, y: su esquina de arriba a la izquierda; flip la espeja), con su "
                       "colisión y su recorte de adelante (front: delante del colgado) relativos a la pieza. Las patas: legs "
                       "[y0, y1] es la franja de filas de la pieza entre la losa y los pies que se alarga cuando el objeto "
                       "trae stretch (px de más hacia abajo): la pieza mide h + stretch, lo de arriba de y0 queda igual, la "
                       "franja se estira a y1 - y0 + stretch y lo de abajo de y1 baja stretch (negativo la acorta). legsGap: "
                       "cuántos px por encima de la línea de los pies de lo de abajo terminan las patas (lo usa el botón "
                       "\"Que llegue abajo\" del editor). La y de cada "
                       "sólido es la línea de los pies: el borde de atrás de la cara de arriba pintada. Se mueven con el "
                       "editor (prototypes/arena/editor)")
    layered["plate"] = {"src": f"{args.arena}/fondo.webp", "solid": [r for i, r in enumerate(arena["plate"]["solid"]) if i not in used_f]}
    layered["pieces"] = defs
    layered["solids"] = [s for i, s in enumerate(arena["solids"]) if i not in used_s]
    layered["objects"] = objects + arena.get("objects", [])
    order = ["name", "note", "size", "seed", "plate", "pieces", "solids", "objects", "spawns", "decor", "pipes"]
    layered = {k: layered[k] for k in order if k in layered} | {k: v for k, v in layered.items() if k not in order}
    import importlib.util
    spec = importlib.util.spec_from_file_location("serve", HERE / "serve.py")
    serve = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(serve)
    menu.write_text(serve.fmt(layered) + "\n", encoding="utf-8")
    print(f"✓ {out_dir.relative_to(ROOT)}/: fondo.webp y {len(defs)} piezas; {menu.relative_to(ROOT)} en capas")

    if args.check:   # la arena armada de nuevo (fondo + piezas en su lugar) contra la lámina, y la máscara
        args.check.mkdir(parents=True, exist_ok=True)
        comp = Image.open(out_dir / "fondo.webp").convert("RGBA")
        for o in objects:
            comp.alpha_composite(Image.open(out_dir / f"{o['piece']}.png"), (o["x"], o["y"]))
        comp = np.asarray(comp.convert("RGB")).astype(np.float32)
        err = np.abs(comp - plate_rgb).max(2)
        print(f"  armada de nuevo contra la lámina: diferencia media {err.mean():.2f}, máx {err.max():.0f}, "
              f"{(err > 24).sum()} px con más de 24")
        Image.fromarray(np.clip(err * 4, 0, 255).astype(np.uint8)).save(args.check / "rearmada_diff.png")
        vis = plate_rgb * 0.35
        vis[allmask > 0.5] = plate_rgb[allmask > 0.5]
        Image.fromarray(vis.astype(np.uint8)).save(args.check / "piezas.png")
        Image.fromarray(np.clip(empty, 0, 255).astype(np.uint8)).save(args.check / "edicion_alineada.png")


if __name__ == "__main__":
    main()
