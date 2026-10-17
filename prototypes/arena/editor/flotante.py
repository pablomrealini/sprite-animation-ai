"""Recorta de la lámina de una arena en capas la flotante que el modelo dibujó, como pieza pintada que se mueve.

uso (desde la raíz del repo):
    uv run --project pipeline python prototypes/arena/editor/flotante.py refineria_lowpoly [--check carpeta]

No gasta. En la Refinería low-poly, el restyle (backgrounds/arena_refineria_lowpoly, lowpoly_restyle opción 1) le dibujó
a la columna una plataforma con franjas amarillas y negras y tapas rojas (x 856–1064, y 661–736). capas.py la saca del
fondo (FROM_EDIT): ahí el fondo es la columna sola, de la edición. Esto la recorta de arenas/<arena>/lamina.webp:
- la forma es un polígono medido a mano (las tapas, la panza que se angosta y el collar a los costados de la columna),
  sin lo que es neblina azul del cielo (la misma regla que capas.py para la low-poly) y con el borde azulado pelado;
- la columna queda afuera: arriba de la cara de arriba y abajo de la panza (ahí, en la lámina, la columna está en la
  sombra de la plataforma; la del fondo está iluminada). El corte contra la columna es duro; contra el cielo, suave;
- la pieza queda en arenas/<arena>/flotante.png, 1 px = 1 px del juego.
Escribe la definición de la pieza (src, w, h, cut, solids, front) para pegar en arenas/<arena>.json; no toca el JSON.
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

# por arena: el contorno de afuera (px del juego, un poco holgado: la neblina lo ajusta), los rectángulos de la columna
# que no van ([x0, y0, x1, y1), sin el borde de abajo y derecho), la línea de los pies (y de la cara de arriba + 3, como
# las pasarelas: cara 529 → 532) y lo que se pisa en x
FLOATS = {
    "refineria_lowpoly": {
        "outline": [(865, 659), (894, 659), (894, 662), (1027, 662), (1027, 659), (1055, 659), (1067, 671),
                    (1067, 698), (1053, 710), (1038, 710), (1023, 730), (1006, 730), (1000, 737), (920, 737),
                    (914, 730), (897, 730), (881, 710), (867, 710), (854, 698), (854, 671)],
        "column": [(920, 640, 1005, 662), (924, 730, 997, 760)],
        "foot": 667,                 # la cara de arriba empieza en 664 (la raya oscura de atrás está en 662)
        "walk": (857, 1063),         # de punta a punta de las tapas rojas
        "front_to": 710,             # el front: desde 8 px arriba de los pies hasta abajo de las tapas
        "unlight": (935, 722, 990, 730),   # [x0, y0, x1, y1): donde asoma la luz cian de la columna, bajo la panza
    },
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("arena")
    ap.add_argument("--check", type=Path, help="carpeta donde dejar la pieza sobre verde y sobre el fondo")
    args = ap.parse_args()
    F = FLOATS[args.arena]
    out_dir = ARENA / "arenas" / args.arena
    lam = np.asarray(Image.open(out_dir / "lamina.webp").convert("RGB")).astype(np.float32)
    H, W = lam.shape[:2]

    shape = np.zeros((H, W), np.uint8)
    cv2.fillPoly(shape, [np.array(F["outline"], np.int32)], 1)
    shape = shape.astype(bool)
    col = np.zeros((H, W), bool)
    for x0, y0, x1, y1 in F["column"]:
        col[y0:y1, x0:x1] = True
    shape &= ~col

    # la neblina (cielo y refinería lejana): clara y más azul que verde; el metal es gris neutro, las tapas rojas
    R, G, B = lam[..., 0], lam[..., 1], lam[..., 2]
    haze = (B - G > 22) & (B > 120)
    bluish = (B - G > 18) & (B > 110)   # el antialias con el cielo (la panza oscura, con reflejo azul, no)
    core = shape & ~haze
    # sólo lo pegado a lo más grande (la plataforma). Sin apertura: el contorno ya es ajustado, y un núcleo par la corre 1 px
    n, lab, st, _ = cv2.connectedComponentsWithStats(core.astype(np.uint8), connectivity=8)
    core = lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    # los agujeros chicos se tapan (una mota en una franja)
    n, lab, st, _ = cv2.connectedComponentsWithStats((~core).astype(np.uint8), connectivity=4)
    for i in np.nonzero(st[1:, cv2.CC_STAT_AREA] < 60)[0] + 1:
        core |= (lab == i) & shape
    # el borde que da al cielo (no el corte contra la columna), pelado: el antialias deja una línea azulada
    for _ in range(2):
        edge = core & cv2.dilate((~core & ~col).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        core &= ~(edge & bluish)
    # el alfa: duro adentro y contra la columna; suave (1 px) donde toca el cielo
    soft = np.clip(cv2.GaussianBlur(core.astype(np.float32), (3, 3), 0) * 1.35, 0, 1)
    sky_edge = cv2.dilate((haze & ~core & ~col).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    alpha = np.where(core, np.where(sky_edge, soft, 1.0), 0.0)
    # la luz cian de la columna que asoma debajo de la panza: con la pieza en otro lado quedaría colgada. Pasa al gris del
    # metal de alrededor (el rojo de cada píxel, con el tinte azulado de la panza: verde +3, azul +15)
    x0, y0, x1, y1 = F["unlight"]
    teal = np.zeros((H, W), bool)
    teal[y0:y1, x0:x1] = ((G - R > 12) & (B - R > 20))[y0:y1, x0:x1]
    teal &= core
    lam = lam.copy()
    lam[teal] = np.stack([R[teal], R[teal] + 3, R[teal] + 15], 1)

    ys, xs = np.nonzero(alpha > 0.02)
    bx, by, bx1, by1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    rgba = np.dstack([lam, alpha * 255])[by:by1, bx:bx1]
    Image.fromarray(np.round(rgba).astype(np.uint8), "RGBA").save(out_dir / "flotante.png", optimize=True)
    w, h = bx1 - bx, by1 - by
    wx0, wx1 = F["walk"]
    fy = max(0, F["foot"] - 8 - by)   # recortado a la caja de la pieza, como en capas.py
    piece = {"src": f"{args.arena}/flotante.png", "w": w, "h": h, "cut": [bx, by],
             "solids": [{"kind": "bridge", "x": wx0 - bx, "y": F["foot"] - by, "w": wx1 - wx0, "ledge": "none"}],
             "front": [[0, fy, w, F["front_to"] - by - fy]]}
    print(f"  luz de la columna rellenada: {int(teal.sum())} px")
    print(f"✓ {(out_dir / 'flotante.png').relative_to(ROOT)}: {w} × {h} en {bx}, {by} ({int((alpha > 0.5).sum())} px)")
    print(json.dumps({"flotante": piece}, ensure_ascii=False))

    if args.check:
        args.check.mkdir(parents=True, exist_ok=True)
        pc = Image.fromarray(np.round(rgba).astype(np.uint8), "RGBA")
        green = Image.new("RGBA", (w + 40, h + 40), (0, 200, 0, 255))
        green.alpha_composite(pc, (20, 20))
        green.resize((green.width * 4, green.height * 4), Image.NEAREST).save(args.check / "flotante_verde.png")
        # sobre el fondo, donde estaba y en las dos puntas del recorrido de la Refinería (pies a 780 y a 532)
        fondo = Image.open(out_dir / "fondo.webp").convert("RGBA")
        tiles = []
        for foot in (F["foot"], 780, 532):
            c = fondo.copy()
            c.alpha_composite(pc, (bx, by + foot - F["foot"]))
            tiles.append(c.crop((800, 380, 1120, 960)))
        sheet = Image.new("RGBA", (320 * len(tiles), 580))
        for i, t in enumerate(tiles):
            sheet.paste(t, (320 * i, 0))
        sheet.save(args.check / "flotante_fondo.png")


if __name__ == "__main__":
    main()
