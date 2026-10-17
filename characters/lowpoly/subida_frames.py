"""Primer y último frame de la subida a la cornisa del low-poly, en 16:9 sobre magenta apagado.

Copia de characters/ranger/poses_gen/climb_frames.py con una sola diferencia: el ancho del casco se mide en el
componente blanco más grande (la cáscara del casco) y no en cualquier columna con un píxel casi blanco. En el render
low-poly hay brillos claros fuera del casco (puños, botas), y con la medida del ranger la pose parada salía 30% más
chica que la colgada.

uso (desde la raíz del repo):
    uv run --project pipeline python characters/lowpoly/subida_frames.py characters/lowpoly/poses/colgado_dos_concept.png

- Primero: la pose colgada (cutout de gen-images) chica y abajo, con lugar arriba para subir.
- Último: el concept parado sobre el canto, a la misma escala que la colgada. La escala sale del ancho del blanco
  del casco, que no cambia con la pose: en el colgado de r07 da el alto parado medido a mano (473 px) con 1,3%. El
  área daría 0,1% ahí, pero con los dos brazos arriba el de adelante tapa el casco y el parado sale 30% más chico.
  El canto es el tope de las manos más el grosor de los dedos; la pared, lo más adelantado del cuerpo debajo de
  las manos. Parado, el centro de los pies queda `--inside` altos de cuerpo adentro de la pared.

Imprime el alto parado en px de los dos frames (para `pose_body_height_px`) y deja un .json al lado con lo medido.
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BG = (0xC4, 0x2D, 0x7D)   # magenta apagado: con magenta puro Seedance pinta reflejos en el casco


def helmet_width(a: np.ndarray) -> int:
    """Ancho de la cáscara del casco: el componente blanco más grande (los brillos sueltos no cuentan)."""
    rgb = a[..., :3].astype(int)
    white = ((a[..., 3] > 200) & (rgb.min(-1) > 170) & ((rgb.max(-1) - rgb.min(-1)) < 35)).astype(np.uint8)
    white = cv2.morphologyEx(white, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, _, st, _ = cv2.connectedComponentsWithStats(white)
    return int(st[1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])), cv2.CC_STAT_WIDTH])


def bbox(a: np.ndarray) -> tuple[int, int, int, int]:
    ys, xs = np.nonzero(a[..., 3] > 200)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("hang", type=Path, help="pose colgada con alfa (post de gen-images)")
    ap.add_argument("--stand", type=Path, default=ROOT / "characters/lowpoly/poses/perfil_cinturon_rojo_concept.png",
                    help="pose parada con alfa")
    ap.add_argument("--out", type=Path, default=ROOT / "characters/lowpoly/poses", help="carpeta de salida")
    ap.add_argument("--name", default="climb", help="prefijo de los archivos")
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--hang-height", type=float, default=0.40, help="alto del colgado (manos a pies), fracción del cuadro")
    ap.add_argument("--feet", type=float, default=0.95, help="pies del colgado, fracción del alto")
    ap.add_argument("--x", type=float, default=0.42, help="centro del colgado, fracción del ancho")
    ap.add_argument("--fingers", type=float, default=0.035, help="grosor de los dedos sobre el canto, fracción del colgado")
    ap.add_argument("--inside", type=float, default=0.30, help="pies parados adentro de la pared, en altos de cuerpo")
    args = ap.parse_args()
    W, H = map(int, args.size.split("x"))

    hang = np.array(Image.open(args.hang).convert("RGBA"))
    stand = np.array(Image.open(args.stand).convert("RGBA"))
    hx0, hy0, hx1, hy1 = bbox(hang)
    sx0, sy0, sx1, sy1 = bbox(stand)
    k_hang = H * args.hang_height / (hy1 - hy0)
    # la misma escala para los dos: el blanco del casco tiene que medir lo mismo de ancho
    k_stand = k_hang * helmet_width(hang) / helmet_width(stand)
    stand_h = (sy1 - sy0) * k_stand            # alto parado en px del cuadro

    def place(a, box, k, left, top):
        x0, y0, x1, y1 = box
        sprite = Image.fromarray(a[y0:y1, x0:x1]).resize((round((x1 - x0) * k), round((y1 - y0) * k)), Image.LANCZOS)
        canvas = Image.new("RGBA", (W, H), BG + (255,))
        canvas.alpha_composite(sprite, (round(left), round(top)))
        return canvas.convert("RGB"), sprite

    hang_w, hang_h = (hx1 - hx0) * k_hang, (hy1 - hy0) * k_hang
    left, top = W * args.x - hang_w / 2, H * args.feet - hang_h
    first, sprite = place(hang, (hx0, hy0, hx1, hy1), k_hang, left, top)
    sa = np.array(sprite)[..., 3] > 200
    ledge_y = top + args.fingers * hang_h
    body = sa[int(sa.shape[0] * 0.25):]                     # debajo de las manos
    wall_x = left + int(np.nonzero(body.any(0))[0].max()) + 1
    # parado: pies sobre el canto, con el centro de las botas `inside` altos de cuerpo adentro de la pared
    st = stand[sy0:sy1, sx0:sx1, 3] > 200
    feet_rows = st[int(st.shape[0] * 0.9):]
    feet_cx = float(np.nonzero(feet_rows.any(0))[0].mean()) * k_stand
    s_left = wall_x + args.inside * stand_h - feet_cx
    s_top = ledge_y - stand_h
    if s_top < 0 or s_left + (sx1 - sx0) * k_stand > W:
        raise SystemExit(f"el parado no entra en el cuadro (arriba {s_top:.0f}, derecha {s_left + (sx1 - sx0) * k_stand:.0f})")
    last, _ = place(stand, (sx0, sy0, sx1, sy1), k_stand, s_left, s_top)

    args.out.mkdir(parents=True, exist_ok=True)
    f_first, f_last = args.out / f"{args.name}_first_dullmagenta_16x9.png", args.out / f"{args.name}_last_dullmagenta_16x9.png"
    first.save(f_first)
    last.save(f_last)
    info = {"hang": str(args.hang), "stand": str(args.stand), "size": [W, H], "stand_height_px": round(stand_h, 1),
            "hang_height_px": round(hang_h, 1), "ledge_y": round(ledge_y, 1), "wall_x": round(wall_x, 1),
            "hang_bbox": [round(left), round(top), round(left + hang_w), round(top + hang_h)],
            "stand_bbox": [round(s_left), round(s_top), round(s_left + (sx1 - sx0) * k_stand), round(ledge_y)],
            "rise_px": round(top + hang_h - ledge_y, 1), "forward_px": round(s_left + feet_cx - (left + hang_w / 2), 1)}
    (args.out / f"{args.name}_frames.json").write_text(json.dumps(info, indent=2) + "\n")
    print(f"✓ {f_first.name}, {f_last.name}: parado {stand_h:.0f} px, colgado {hang_h:.0f} px, canto en y {ledge_y:.0f}, "
          f"pared en x {wall_x:.0f}; sube {info['rise_px']:.0f} px y avanza {info['forward_px']:.0f}")


if __name__ == "__main__":
    main()
