"""Apaga el disco cian de la boca del arma en un clip, cuadro por cuadro (la regla: el cañón se prende sólo al disparar).

Por defecto apaga todos los cuadros; con `--cuadros 0-31,95-120` sólo esos tramos (los que no disparan); con
`--cuadros ninguno`, ninguno. Con `--sin-rayos`, antes borra los rayos que Kling dispara sin que se lo pidan
(remove_flash con method = "shape"): si no, el gris se pega a la raíz del rayo.

Con `--sin-fogonazo 30-33 --ref 29`, en los cuadros del tiro borra el fogonazo y el rayo del video (el juego dibuja el
suyo) y deja el cañón prendido y la luz sobre el personaje. La boca se ubica siguiendo el arma desde el cuadro de
reposo `--ref`, apuntando con el brazo estirado (la boca es lo más adelante del personaje), porque sin contorno no hay
otra forma de encontrarla. Se pinta con el color del fondo lo que está delante de la boca, en una franja alta (la
estrella del fogonazo), y el halo arriba y abajo de la punta del cañón.

Sale un H.264 sin pérdida en BT.709 con tag, que spritepipe lee directo.

Uso (desde la raíz del repo):

    uv run --project pipeline python characters/lowpoly/apagar_video.py clip.mp4 salida.mp4 [--cuadros 0-31] \
        [--sin-rayos] [--sin-fogonazo 30-33 --ref 29]
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apagar_arma import apagar_rgb  # noqa: E402
from spritepipe import chroma, config, flash, imgio  # noqa: E402

SOLID = 60  # suma de |RGB - fondo| a partir de la cual un píxel es personaje
GUN = 0.28  # largo del arma, en altos del cuerpo
REACH = 0.40  # media altura de la franja que se borra delante de la boca, en altos del cuerpo
STEP = 0.06  # cuánto puede moverse el arma entre cuadros, en altos del cuerpo


def rangos(texto: str | None, n: int) -> set[int]:
    if not texto:
        return set(range(n))
    out = set()
    for parte in texto.split(","):
        a, _, b = parte.partition("-")
        out.update(range(int(a), (int(b) if b else int(a)) + 1))
    return {i for i in out if i < n}


def sin_fogonazo(frames: list[np.ndarray], tiro: set[int], ref: int) -> int:
    """Borra el fogonazo y el rayo de los cuadros del tiro, con la boca seguida desde el cuadro de reposo `ref`."""
    a = frames[ref].astype(int)
    bg = chroma.border_color(frames[ref].astype(np.float32)).astype(int)
    solid = np.abs(a - bg).sum(-1) > SOLID
    ys, xs = np.nonzero(solid)
    h = int(ys.max() - ys.min())
    front = int(xs.max())  # apuntando con el brazo estirado, la boca es lo más adelante
    rows = np.nonzero(solid[:, front - 3:front + 1].any(1))[0]
    g0, g1 = int(rows.min()), int(rows.max()) + 1
    dh = max(4, g1 - g0)
    tx0, tx1, ty0, ty1 = front - round(GUN * h), front - 2 * dh, g0 - 2 * dh, g1 + dh
    tmpl = flash._lab(frames[ref][ty0:ty1, tx0:tx1])
    H, W = a.shape[:2]
    step, reach, borrados = round(STEP * h), round(REACH * h), 0
    for i in sorted(tiro):
        f = frames[i]
        sx0, sy0 = max(0, tx0 - step), max(0, ty0 - step)
        sx1, sy1 = min(W, tx1 + step), min(H, ty1 + step)
        _, _, (mx, my), _ = cv2.minMaxLoc(cv2.matchTemplate(flash._lab(f[sy0:sy1, sx0:sx1]), tmpl, cv2.TM_SQDIFF))
        dx, dy = sx0 + mx - tx0, sy0 + my - ty0
        tip, yc = front + dx, (g0 + g1) / 2 + dy
        r0, r1 = max(0, round(yc - reach)), min(H, round(yc + reach))
        fb = chroma.border_color(f.astype(np.float32)).round().astype(np.uint8)
        before = int((np.abs(f[r0:r1, tip + 2:].astype(int) - fb).sum(-1) > SOLID).sum())
        f[r0:r1, tip + 2:] = fb  # delante de la boca
        hx0 = tip - 2 * dh  # la punta del cañón: arriba y abajo sólo puede haber halo
        f[r0:max(r0, g0 + dy - 1), hx0:tip + 2] = fb
        f[min(r1, g1 + dy + 1):r1, hx0:tip + 2] = fb
        borrados += before
    return borrados


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("clip", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--cuadros", help="tramos a apagar, p. ej. 0-31,95-120 (por defecto, todos)")
    ap.add_argument("--sin-rayos", action="store_true", help="borrar antes los rayos (remove_flash shape)")
    ap.add_argument("--sin-fogonazo", help="cuadros del tiro donde se borra el fogonazo del video, p. ej. 30-33")
    ap.add_argument("--ref", type=int, help="con --sin-fogonazo: cuadro de reposo apuntando, de donde sale la boca")
    a = ap.parse_args()
    info = imgio.probe(a.clip)
    matrix = None if info.get("color_space") else "bt601"  # fal entrega BT.601 sin tag
    tmp = Path(tempfile.mkdtemp(prefix="apagar_"))
    try:
        imgio.extract(a.clip, tmp / "raw", info, matrix)
        src = tmp / "raw"
        if a.sin_rayos:
            res = flash.run(src, tmp / "clean", config.FlashRemoval(method="shape"))
            src = tmp / "clean"
            print(f"  rayos borrados (boca en x {res['muzzle_x'][0]}–{res['muzzle_x'][1]})")
        paths = imgio.frames(src)
        sel = set() if a.cuadros == "ninguno" else rangos(a.cuadros, len(paths))
        frames = [imgio.load(p)[..., :3].copy() for p in paths]
        if a.sin_fogonazo:
            if a.ref is None:
                raise SystemExit("--sin-fogonazo necesita --ref (el cuadro de reposo apuntando)")
            n = sin_fogonazo(frames, rangos(a.sin_fogonazo, len(frames)), a.ref)
            print(f"  fogonazo borrado en {a.sin_fogonazo} ({n} px)")
        total = 0
        for i in sel:
            frames[i], n = apagar_rgb(frames[i])
            total += n
        imgio.encode_rgb_video(frames, a.out, info["fps"], crf=0, pix_fmt="yuv444p")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"✓ {a.out}: {len(paths)} cuadros, {len(sel)} apagados ({total / max(1, len(sel)):.0f} px por cuadro)")


if __name__ == "__main__":
    main()
