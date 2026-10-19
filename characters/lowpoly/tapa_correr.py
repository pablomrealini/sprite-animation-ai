"""El arma de run_gun: la tapa de la boca de un cuadro limpio, pegada en todos (revisión del 2026-10-18).

En el clip de correr (set toma 2 de correr, Kling), el disco cian de la boca se prende y Kling dispara un rayo cada ~7
cuadros. apagar_video.py --sin-rayos borra los rayos y después pinta del gris del arma todo lo cian: el disco, pero
también el halo de luz alrededor de la boca, que queda recortado en rectángulo donde terminó el borrado del rayo. Así,
en la mitad de los cuadros la tapa crece, se corre o queda cortada con un borde lila: el arma "salta".

Acá, en cada cuadro del clip sin rayos:
  1. se sigue el cuerpo del arma (la franja roja y el gris de atrás de la tapa, que la luz no cambia) contra el cuadro
     de referencia, con giro (±12°: al correr el brazo baja el arma hasta ~10°) y corrimiento;
  2. alrededor de la boca (la tapa, el halo y lo que quedó del rayo) se pinta el fondo;
  3. se pega ahí la tapa apagada del cuadro de referencia (el 14 del clip apagado, el cuadro 0 de run_gun, que está
     bien), girada y corrida como el arma de ese cuadro.

Uso (desde la raíz del repo):

    uv run --project pipeline python characters/lowpoly/tapa_correr.py [salida.mp4] [--hoja]

Escribe clips/retocado/correr_a_2_tapa.mp4, el clip de run_gun en character.toml (aprobado por Pablo, 2026-10-18):
correrlo antes del run si falta (git lo ignora).
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from spritepipe import chroma, imgio

HERE = Path(__file__).resolve().parent
SIN_RAYOS = HERE / "clips" / "correr" / "kling-o3-std_correr_a_2_sin_rayos.mp4"
APAGADO = HERE / "clips" / "apagado" / "correr_a_2.mp4"
MUZZLE = HERE / "clips" / "correr" / "kling-o3-std_correr_a_2_sin_rayos.muzzle.json"
REF = 14                         # el cuadro de referencia: la tapa apagada bien (el 0 de run_gun)
BODY = (-135, -40, -32, 24)      # el cuerpo del arma, desde la boca del cuadro de referencia: x0, x1, y0, y1 (px del video)
ZONE = (-44, 48, -52, 52)        # la tapa y el halo alrededor de la boca
FEATHER = 14                     # la rampa del borde de atrás de la zona (sobre el caño)
ANGLES = np.arange(-12, 12.1, 1.0)
SEARCH = 28                      # cuánto puede estar corrida el arma del lugar que dice la boca medida al borrar los rayos
KEY_LO, KEY_HI = 0.12, 0.8       # la rampa del key (character.toml)


def feat(rgb: np.ndarray) -> np.ndarray:
    """Luminancia y rojo: el gris y la franja del arma; la luz cian del cañón casi no los mueve."""
    f = rgb.astype(np.float32) / 255.0
    return np.ascontiguousarray(np.dstack([f @ np.array([0.3, 0.59, 0.11], np.float32), f[..., 0]]))


def alpha(rgb: np.ndarray) -> np.ndarray:
    f = rgb.astype(np.float32) / 255.0
    a = chroma.estimate_alpha(f, chroma.border_color(f), "distance")
    return np.clip((a - KEY_LO) / (KEY_HI - KEY_LO), 0, 1)


def seguir(ref: np.ndarray, fr: np.ndarray, rx: int, ry: int, hint: tuple[int, int]) -> tuple[float, int, int, float]:
    """(giro, dx, dy, error) que lleva el cuerpo del arma de la referencia (boca en rx, ry) al cuadro."""
    x0, x1, y0, y1 = BODY
    c = (rx + (x0 + x1) / 2, ry + (y0 + y1) / 2)
    fref, ffr = feat(ref), feat(fr)
    hx, hy = hint[0] - rx, hint[1] - ry
    wx0, wy0 = rx + x0 + hx - SEARCH, ry + y0 + hy - SEARCH
    win = ffr[wy0:ry + y1 + hy + SEARCH, wx0:rx + x1 + hx + SEARCH]
    best = (np.inf, 0.0, 0, 0)
    for ang in ANGLES:
        M = cv2.getRotationMatrix2D(c, float(ang), 1.0)
        rot = cv2.warpAffine(fref, M, (fref.shape[1], fref.shape[0]), flags=cv2.INTER_LINEAR)
        tpl = np.ascontiguousarray(rot[ry + y0:ry + y1, rx + x0:rx + x1])
        res = cv2.matchTemplate(win, tpl, cv2.TM_SQDIFF_NORMED)
        mn, _, (mx, my), _ = cv2.minMaxLoc(res)
        if mn < best[0]:
            best = (mn, float(ang), wx0 + mx - (rx + x0), wy0 + my - (ry + y0))
    err, ang, dx, dy = best
    return ang, dx, dy, err


def pegar(fr: np.ndarray, cap_src: np.ndarray, cap_a: np.ndarray, rx: int, ry: int, ang: float, dx: int, dy: int) -> np.ndarray:
    x0, x1, y0, y1 = BODY
    c = (rx + (x0 + x1) / 2, ry + (y0 + y1) / 2)
    M = cv2.getRotationMatrix2D(c, ang, 1.0)
    M[0, 2] += dx
    M[1, 2] += dy
    h, w = fr.shape[:2]
    zone = np.zeros((h, w), np.float32)
    zx0, zx1, zy0, zy1 = ZONE
    zone[ry + zy0:ry + zy1, rx + zx0:rx + zx1] = 1.0
    # el borde de atrás de la zona corta el caño: una rampa de FEATHER px mezcla el caño del cuadro con el pegado
    ramp = np.clip((np.arange(w, dtype=np.float32) - (rx + zx0)) / FEATHER, 0, 1)
    zone *= ramp[None, :]
    zone[ry + zy0:ry + zy1, rx + zx0 - FEATHER:rx + zx0] = 0.0
    zone = cv2.warpAffine(zone, M, (w, h), flags=cv2.INTER_LINEAR)
    src = cv2.warpAffine(cap_src.astype(np.float32), M, (w, h), flags=cv2.INTER_LINEAR)
    a = cv2.warpAffine(cap_a, M, (w, h), flags=cv2.INTER_LINEAR) * zone
    bg = chroma.border_color(fr.astype(np.float32) / 255.0) * 255.0
    out = fr.astype(np.float32)
    out = out * (1 - zone[..., None]) + bg * zone[..., None]          # la zona, del fondo
    out = out * (1 - a[..., None]) + src * a[..., None]               # y la tapa de la referencia encima
    return np.clip(out + 0.5, 0, 255).astype(np.uint8)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out", type=Path, nargs="?", default=HERE / "clips" / "retocado" / "correr_a_2_tapa.mp4")
    ap.add_argument("--hoja", action="store_true", help="también <salida>.png (antes y después, del lado del clip)")
    args = ap.parse_args()
    muzzle = json.loads(MUZZLE.read_text(encoding="utf-8"))["muzzle"]
    with tempfile.TemporaryDirectory() as tmp:
        frames = {}
        for name, clip in (("sin_rayos", SIN_RAYOS), ("apagado", APAGADO)):
            info = imgio.probe(clip)
            d = Path(tmp) / name
            imgio.extract(clip, d, info, None if info.get("color_space") else "bt601")
            frames[name] = [np.array(Image.open(p).convert("RGB")) for p in imgio.frames(d)]
    sr, apg = frames["sin_rayos"], frames["apagado"]
    rx, ry = muzzle[REF]["x"], round(muzzle[REF]["y"])
    cap_src, cap_a = apg[REF], alpha(apg[REF])
    out, log = [], []
    for n, fr in enumerate(apg):
        if n == REF:
            out.append(fr)
            continue
        ang, dx, dy, err = seguir(sr[REF], sr[n], rx, ry, (muzzle[n]["x"], round(muzzle[n]["y"])))
        out.append(pegar(sr[n], cap_src, cap_a, rx, ry, ang, dx, dy))
        log.append((n, ang, dx, dy, err))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    imgio.encode_rgb_video(out, args.out, info["fps"], crf=0, pix_fmt="yuv444p")
    worst = max(log, key=lambda t: t[4])
    print(f"✓ {args.out}: {len(out)} cuadros, tapa del {REF} en todos; giro {min(t[1] for t in log):+.0f}° a "
          f"{max(t[1] for t in log):+.0f}°, error máximo {worst[4]:.3f} (cuadro {worst[0]})")
    for n, ang, dx, dy, err in log:
        if 12 <= n <= 42:
            print(f"  n{n}: giro {ang:+.0f}°, corrido {dx:+d}, {dy:+d}, error {err:.3f}")
    if args.hoja:
        sel = [14, 16, 18, 20, 22, 24, 26, 32, 34, 38, 40]
        tiles = []
        for src in (apg, out):
            for n in sel:
                mx, my = muzzle[n]["x"], round(muzzle[n]["y"])
                t = Image.fromarray(src[n]).crop((mx - 130, my - 55, mx + 60, my + 65)).resize((228, 144), Image.NEAREST)
                ImageDraw.Draw(t).text((4, 4), f"n{n}", fill=(255, 255, 0))
                tiles.append(t)
        s = Image.new("RGB", (len(sel) * 232, 2 * 148), (240, 240, 240))
        for i, t in enumerate(tiles):
            s.paste(t, ((i % len(sel)) * 232, (i // len(sel)) * 148))
        dest = args.out.with_suffix(".png")
        s.save(dest)
        print(f"✓ {dest} (arriba el apagado de hoy, abajo la tapa pegada)")


if __name__ == "__main__":
    main()
