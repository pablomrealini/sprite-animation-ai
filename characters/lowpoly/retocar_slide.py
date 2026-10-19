"""El deslizamiento de la tanda 5 (slide_3) fijado al piso y al lugar: clips/retocado/slide_3.mp4.

Mientras se tira, se desliza, se levanta y da los primeros pasos (42–83), Kling corre la escena: el apoyo baja de 518 (los pies de la pose,
el piso de correr) a 563, y el personaje se va ~200 px para atrás, como si la cinta lo llevara (el casco, de 624 a
403). El juego pone el movimiento, así que en esos cuadros se corre todo el cuadro:
  - en y, para que lo más bajo del personaje quede en 518;
  - en x, para que el casco quede donde está corriendo (624): la cabeza se queda sobre el jugador y las piernas salen
    para adelante, como en un deslizamiento de verdad.
Lo que se destapa se pinta del fondo. Los cuadros de correr (0–41 y 84–96) quedan como están: ahí el rebote del
cuerpo es el de run_gun (corriendo, Kling baja todo el cuerpo ~25 px en la mitad de la zancada). 81–83 también se
fijan al piso: si no, el 82 de slide_out quedaba 22 px de 1x abajo del piso. Los ojos cerrados del sostenido (46–75) se dejan: Pablo lo aprobó así.

Uso (desde la raíz del repo, antes de `spritepipe run characters/lowpoly/character.toml`):

    uv run --project pipeline python characters/lowpoly/retocar_slide.py [--hoja]

Con --hoja arma además revision/slide_retoque.png: piso y casco por cuadro, antes y después.
"""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from spritepipe import chroma, imgio

ROOT = Path(__file__).resolve().parent
CLIP = ROOT / "clips" / "tanda5" / "kling-o3-std_slide_3.mp4"
OUT = ROOT / "clips" / "retocado" / "slide_3.mp4"
FIX = range(42, 84)       # se tira (42–46), se desliza (46–73), se levanta (74–80) y los primeros pasos (81–83)
FLOOR = 518               # el piso de correr: los pies de la pose (777 de 1080)
HELMET_X = 624            # el casco corriendo (n41; 622–636 en la carrera de 0–41)


def medir(frame: np.ndarray) -> tuple[int, float]:
    """(fila más baja del personaje, x del casco): el componente más grande del key por distancia; el piso como en
    align (la fila más baja con al menos el 1% del ancho), el casco, lo blanco de las 120 filas de arriba."""
    f = frame.astype(np.float32) / 255.0
    key = chroma.border_color(f)
    a = (chroma.estimate_alpha(f, key, "distance") > 0.5).astype(np.uint8)
    a = cv2.morphologyEx(a, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(a, 8)
    body = lab == 1 + int(np.argmax(st[1:, 4]))
    rows = np.nonzero(body.sum(1) >= max(2, 0.01 * body.shape[1]))[0]
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    top = np.nonzero(body.any(1))[0].min()
    white = body & (hsv[..., 1] < 45) & (hsv[..., 2] > 170)
    white[top + 120:] = False
    return int(rows.max()) + 1, float(np.nonzero(white)[1].mean())


def correr(frame: np.ndarray, dx: int, dy: int) -> np.ndarray:
    bg = np.round(chroma.border_color(frame.astype(np.float32) / 255.0) * 255).astype(np.uint8)
    out = np.empty_like(frame)
    out[:] = bg
    h, w = frame.shape[:2]
    out[max(0, dy):h + min(0, dy), max(0, dx):w + min(0, dx)] = frame[max(0, -dy):h - max(0, dy), max(0, -dx):w - max(0, dx)]
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hoja", action="store_true", help="también revision/slide_retoque.png")
    args = ap.parse_args()
    info = imgio.probe(CLIP)
    with tempfile.TemporaryDirectory() as tmp:
        imgio.extract(CLIP, Path(tmp), info, "bt601")
        frames = [np.array(Image.open(p).convert("RGB")) for p in imgio.frames(Path(tmp))]
    log = {}
    antes = {}
    for n in FIX:
        g, hx = medir(frames[n])
        dx, dy = round(HELMET_X - hx), FLOOR - g
        antes[n] = frames[n]
        frames[n] = correr(frames[n], dx, dy)
        log[n] = (g, hx, dx, dy)
    imgio.encode_rgb_video(frames, OUT, info["fps"], crf=0, pix_fmt="yuv444p")
    print(f"✓ {OUT}: {len(frames)} cuadros; corridos {FIX.start}–{FIX.stop - 1} "
          f"(dx {min(v[2] for v in log.values())} a {max(v[2] for v in log.values())}, "
          f"dy {min(v[3] for v in log.values())} a {max(v[3] for v in log.values())} px del video)")
    for n, (g, hx, dx, dy) in log.items():
        print(f"  n{n}: piso {g} → {FLOOR}, casco x {hx:.0f} → {hx + dx:.0f} (dx {dx:+d}, dy {dy:+d})")
    if args.hoja:
        hoja(antes, frames, ROOT / "revision" / "slide_retoque.png")


def hoja(antes: dict[int, np.ndarray], frames: list[np.ndarray], dest: Path) -> None:
    sel = [41, 43, 46, 52, 60, 68, 72, 76, 78, 80, 84]
    tiles = []
    for k, src in enumerate(({n: antes.get(n, frames[n]) for n in sel}, {n: frames[n] for n in sel})):
        for n in sel:
            t = Image.fromarray(src[n]).crop((250, 140, 850, 600)).resize((240, 184), Image.BILINEAR)
            d = ImageDraw.Draw(t)
            for y, c in ((FLOOR, (0, 255, 0)), (563, (255, 255, 0))):
                d.line((0, (y - 140) * 0.4, 240, (y - 140) * 0.4), fill=c)
            d.line(((HELMET_X - 250) * 0.4, 0, (HELMET_X - 250) * 0.4, 184), fill=(0, 255, 255))
            d.text((4, 4), f"{'antes' if k == 0 else 'ahora'} n{n}", fill=(255, 255, 255))
            tiles.append(t)
    cols = len(sel)
    s = Image.new("RGB", (cols * 244, 2 * 188), (240, 240, 240))
    for i, t in enumerate(tiles):
        s.paste(t, ((i % cols) * 244, (i // cols) * 188))
    s.save(dest)
    print(f"✓ {dest} (verde: el piso de correr; amarillo: donde apoyaba deslizando; cian: el casco corriendo)")


if __name__ == "__main__":
    main()
