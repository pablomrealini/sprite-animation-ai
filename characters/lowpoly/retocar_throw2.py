"""El tiro de granada nuevo (tanda 3b, throw_cerca_2) retocado para el atlas: clips/retocado/throw_cerca_2.mp4.

Dos retoques sobre el video (BT.601, sin tag, como viene de fal), cuadro por cuadro:
  - **una sola granada**: la de la mano que dibujó Kling (gris oscura con franja roja, la de poses/granada.png) no es la
    que tira el juego (la blanca y roja de backgrounds/lowpoly_grenade, la del power-up y el HUD). En los cuadros con
    la granada en la mano se pega encima la del juego, a su tamaño en la arena (24 px de juego, build.py: ~81 px del
    video) y con su cuerpo centrado en la esfera de la mano, espejada (la argolla para atrás, como la de Kling) y girada
    como va el brazo;
  - **sólo el personaje** en la suelta y lo que sigue: la granada que vuela (51–52) la pone el juego y la explosión que
    dibuja Kling a la derecha (53–55) no va. Queda el componente más grande; lo demás se pinta del fondo.

Uso (desde la raíz del repo, antes de `spritepipe run characters/lowpoly/character.toml`):

    uv run --project pipeline python characters/lowpoly/retocar_throw2.py [--hoja]

Con --hoja arma además revision/throw2_retoque.png: los cuadros tocados, antes y después, ampliados.
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
REPO = ROOT.parents[1]
CLIP = ROOT / "clips" / "tanda3b" / "kling-o3-std_throw_cerca_2.mp4"
OUT = ROOT / "clips" / "retocado" / "throw_cerca_2.mp4"
GRENADE = REPO / "backgrounds" / "lowpoly_grenade" / "post" / "grenade" / "gpt-image-2.5-sunburst-fal_2" / "off.png"
GRENADE_H = 81.0          # alto de la granada del juego en px del video: 24 px de juego × 345 / 102,4 (el cuerpo parado)
BODY_CENTER = (389, 795)  # centro del cuerpo (lo rojo y blanco) en off.png, sin la tapa ni la argolla
SOLO = range(51, 57)      # sólo el personaje: la granada que vuela y la explosión
KEY_LO = 0.12             # lo que el key cuenta como personaje (la tolerancia baja de [key])

# la granada de la mano, por cuadro nativo: centro de la esfera en px del video y el giro en grados (horario, 0 = la tapa
# arriba). En 24–45, la esfera detectada (la mancha oscura más grande cerca de la mano, ver `esfera`); en 47–50 el brazo
# va borroso y la granada es una mancha gris que no se detecta bien: el centro y el giro, a ojo sobre un recorte con
# grilla del video (en 47 la tapa apunta para atrás y arriba; en 49–50, la tapa arriba y un poco adelante).
MANO = {
    24: (463, 290, -15), 28: (463, 291, -12), 36: (464, 290, -15), 44: (479, 300, -10), 45: (494, 297, -5),
    47: (512, 312, -40), 49: (780, 276, 15), 50: (805, 272, 25),
}
# a 24 fps (2026-10-19) se usan todos los nativos con la granada en la mano: en los que no están en MANO, el centro y el
# giro salen de interpolar entre los de MANO; hasta el 45 (la esfera se ve) el centro se corrige con `esfera`, con el
# mismo corrimiento promedio que tienen los de MANO contra lo detectado
GRANADA = [n for n in range(24, 51) if n != 48]   # el 48 sale movido y no se usa: la interpolación caía en la cara


def esfera(frame: np.ndarray, hint: tuple[int, int], r: int = 60) -> tuple[float, float, float] | None:
    """La granada de Kling: la mancha oscura (gris azulado, no el rojo oscuro del guante) más grande cerca de `hint`."""
    a = frame.astype(int)
    mx = a.max(2)
    dark = (mx < 95) & (a[..., 2] >= a[..., 0] - 10)
    yy, xx = np.ogrid[:a.shape[0], :a.shape[1]]
    m = (dark & ((xx - hint[0]) ** 2 + (yy - hint[1]) ** 2 < r * r)).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    if n < 2:
        return None
    i = 1 + int(np.argmax(st[1:, 4]))
    ys, xs = np.nonzero(lab == i)
    (cx, cy), rad = cv2.minEnclosingCircle(np.column_stack([xs, ys]).astype(np.float32))
    return cx, cy, rad


def manos(frames: list[np.ndarray]) -> dict[int, tuple[float, float, float]]:
    """Centro y giro de la granada de la mano en cada nativo de GRANADA (ver arriba)."""
    det = {n: esfera(frames[n], MANO[n][:2]) for n in MANO if n <= 45}
    off = np.mean([(MANO[n][0] - d[0], MANO[n][1] - d[1]) for n, d in det.items() if d], axis=0)
    out = {}
    for n in GRANADA:
        if n in MANO:
            out[n] = MANO[n]
            continue
        a, b = max(k for k in MANO if k < n), min(k for k in MANO if k > n)
        t = (n - a) / (b - a)
        cx, cy, ang = (MANO[a][i] + (MANO[b][i] - MANO[a][i]) * t for i in range(3))
        if n <= 45:
            e = esfera(frames[n], (round(cx), round(cy)))
            if e and e[2] > 15 and abs(e[0] + off[0] - cx) < 25 and abs(e[1] + off[1] - cy) < 25:
                cx, cy = e[0] + off[0], e[1] + off[1]
        out[n] = (cx, cy, ang)
    return out


def granada_juego() -> Image.Image:
    """La granada del juego espejada, a su alto en px del video, en un cuadrado con el centro del cuerpo en el medio."""
    g = Image.open(GRENADE).convert("RGBA").transpose(Image.FLIP_LEFT_RIGHT)
    k = GRENADE_H / g.height
    g = g.convert("RGBa").resize((round(g.width * k), round(g.height * k)), Image.LANCZOS)
    bx, by = (g.width - 1 - BODY_CENTER[0] * k), BODY_CENTER[1] * k   # espejada: el centro del cuerpo también
    side = int(2 * max(bx, by, g.width - bx, g.height - by)) + 4
    sq = Image.new("RGBa", (side, side), (0, 0, 0, 0))
    sq.paste(g, (round(side / 2 - bx), round(side / 2 - by)))
    return sq


def pegar(frame: np.ndarray, g: Image.Image, cx: float, cy: float, ang: float) -> np.ndarray:
    rot = g.rotate(-ang, resample=Image.BICUBIC).convert("RGBA")
    im = Image.fromarray(frame).convert("RGBA")
    im.alpha_composite(rot, (round(cx - rot.width / 2), round(cy - rot.height / 2)))
    return np.array(im.convert("RGB"))


def solo_personaje(frame: np.ndarray) -> np.ndarray:
    f = frame.astype(np.float32) / 255.0
    key = chroma.border_color(f)
    fg = (chroma.estimate_alpha(f, key, "distance") > KEY_LO).astype(np.uint8)
    fg = cv2.dilate(fg, np.ones((7, 7), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(fg, 8)
    if n < 3:
        return frame
    keep = lab == 1 + int(np.argmax(st[1:, 4]))
    out = frame.copy()
    out[~keep] = np.round(key * 255).astype(np.uint8)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hoja", action="store_true", help="también revision/throw2_retoque.png")
    args = ap.parse_args()
    info = imgio.probe(CLIP)
    g = granada_juego()
    with tempfile.TemporaryDirectory() as tmp:
        imgio.extract(CLIP, Path(tmp), info, "bt601")
        paths = imgio.frames(Path(tmp))
        frames = [np.array(Image.open(p).convert("RGB")) for p in paths]
    pos = manos(frames)
    antes = {n: frames[n].copy() for n in list(GRANADA) + list(SOLO)}
    for n, (cx, cy, ang) in pos.items():
        frames[n] = pegar(frames[n], g, cx, cy, ang)
    for n in SOLO:
        frames[n] = solo_personaje(frames[n])
    imgio.encode_rgb_video(frames, OUT, info["fps"], crf=0, pix_fmt="yuv444p")
    print(f"✓ {OUT}: {len(frames)} cuadros; granada del juego en {GRANADA[0]}–{GRANADA[-1]} (sin el 48); "
          f"sólo el personaje en {SOLO.start}–{SOLO.stop - 1}")
    if args.hoja:
        hoja(antes, frames, pos, ROOT / "revision" / "throw2_retoque.png")


def hoja(antes: dict[int, np.ndarray], frames: list[np.ndarray], pos: dict, dest: Path) -> None:
    tiles = []
    for n in pos:
        cx, cy, _ = pos[n]
        box = (round(cx) - 70, round(cy) - 80, round(cx) + 70, round(cy) + 60)
        for f in (antes[n], frames[n]):
            t = Image.fromarray(f).crop(box).resize((280, 280), Image.NEAREST)
            ImageDraw.Draw(t).text((4, 4), f"n{n}", fill=(255, 255, 0))
            tiles.append(t)
    for n in SOLO:
        for f in (antes[n], frames[n]):
            t = Image.fromarray(f).crop((380, 120, 1280, 560)).resize((280, 137), Image.BILINEAR)
            ImageDraw.Draw(t).text((4, 4), f"n{n}", fill=(255, 255, 0))
            tiles.append(t)
    cols = 8
    s = Image.new("RGB", (cols * 286, ((len(tiles) + cols - 1) // cols) * 286), (240, 240, 240))
    for k, t in enumerate(tiles):
        s.paste(t, ((k % cols) * 286, (k // cols) * 286))
    s.save(dest)
    print(f"✓ {dest} (de a pares: antes, después)")


if __name__ == "__main__":
    main()
