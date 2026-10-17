"""Primer y último cuadro de colgarse de una mano (hang_in) y el cuadro del colgado (hang), en 16:9 sobre magenta apagado.

El personaje parado (la pose de perfil con el arma apagada) con lugar arriba, y la pose colgada de una mano a la misma
escala (el ancho de la cáscara del casco, como subida_frames.py), con los pies `--lift` altos de cuerpo sobre el piso y
el cuerpo centrado donde estaba parado: salta en el lugar y se agarra de un canto que no se dibuja. El colgado en loop
usa el mismo cuadro de la pose colgada, así empalma con hang_in.

Uso (desde la raíz del repo):

    uv run --project pipeline python characters/lowpoly/colgarse_frames.py characters/lowpoly/poses/colgado_una_concept.png
"""

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

from subida_frames import BG, bbox, helmet_width

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("hang", type=Path, help="pose colgada de una mano, con alfa")
    ap.add_argument("--stand", type=Path, default=ROOT / "characters/lowpoly/poses/perfil_apagada_concept.png")
    ap.add_argument("--out", type=Path, default=ROOT / "characters/lowpoly/poses")
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--stand-height", type=float, default=0.48, help="alto parado, fracción del cuadro (como pad-pose)")
    ap.add_argument("--feet", type=float, default=0.92, help="pies parado, fracción del alto")
    ap.add_argument("--lift", type=float, default=0.35, help="pies colgado sobre el piso, en altos de cuerpo")
    a = ap.parse_args()
    W, H = map(int, a.size.split("x"))
    hang, stand = np.array(Image.open(a.hang).convert("RGBA")), np.array(Image.open(a.stand).convert("RGBA"))
    sx0, sy0, sx1, sy1 = bbox(stand)
    hx0, hy0, hx1, hy1 = bbox(hang)
    k_stand = H * a.stand_height / (sy1 - sy0)
    k_hang = k_stand * helmet_width(stand) / helmet_width(hang)
    stand_h = (sy1 - sy0) * k_stand
    floor = H * a.feet
    cx = W / 2

    def place(img, box, k, left, top):
        x0, y0, x1, y1 = box
        sprite = Image.fromarray(img[y0:y1, x0:x1]).resize((round((x1 - x0) * k), round((y1 - y0) * k)), Image.LANCZOS)
        canvas = Image.new("RGBA", (W, H), BG + (255,))
        canvas.alpha_composite(sprite, (round(left), round(top)))
        return canvas.convert("RGB")

    sw = (sx1 - sx0) * k_stand
    first = place(stand, (sx0, sy0, sx1, sy1), k_stand, cx - sw / 2, floor - stand_h)
    hw, hh = (hx1 - hx0) * k_hang, (hy1 - hy0) * k_hang
    top = floor - a.lift * stand_h - hh
    if top < 0:
        raise SystemExit(f"la pose colgada no entra en el cuadro (arriba en {top:.0f}): bajá --lift o --stand-height")
    last = place(hang, (hx0, hy0, hx1, hy1), k_hang, cx - hw / 2, top)
    a.out.mkdir(parents=True, exist_ok=True)
    first.save(a.out / "colgarse_first_dullmagenta_16x9.png")
    last.save(a.out / "colgado_una_dullmagenta_16x9.png")
    info = {"hang": str(a.hang), "stand": str(a.stand), "stand_height_px": round(stand_h, 1),
            "hang_height_px": round(hh, 1), "hand_top_y": round(top, 1), "lift_px": round(a.lift * stand_h, 1)}
    (a.out / "colgarse_frames.json").write_text(json.dumps(info, indent=2) + "\n")
    print(f"✓ colgarse_first_dullmagenta_16x9.png, colgado_una_dullmagenta_16x9.png: parado {stand_h:.0f} px, "
          f"colgado {hh:.0f} px, la mano arriba en y {top:.0f}, los pies a {a.lift * stand_h:.0f} px del piso")


if __name__ == "__main__":
    main()
