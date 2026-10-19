"""Video lado a lado de dos corridas del atlas (p. ej. 12 contra 24 fps), sobre verde y a tamaño de juego (0,5× × 1,6).

Cada fila es una animación: a la izquierda la corrida A, a la derecha la B, cada una a su fps (el de su JSON). Los
ciclos dan vueltas; los oneshot se repiten con una pausa en el primer y el último cuadro.

    uv run --project pipeline python characters/lowpoly/video_fps.py OUT_A OUT_B salida.mp4 --anims run_gun,idle_combat,jump
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import revisar as rv  # noqa: E402
from spritepipe import imgio  # noqa: E402

K = rv.GAME_K          # 0,5× → px de pantalla en retina 1080p
FPS = 24               # el del video


def datos(out: Path, anim: str) -> tuple[list[np.ndarray], dict, float, bool]:
    j = json.loads((out / "lowpoly.json").read_text(encoding="utf-8"))["variants"]["0.5x"]
    a = j["animations"][anim]
    return rv.cells(out, "0.5x", anim), j["pivot_px"], float(round(1000.0 / a["frames"][0]["duration"])), a["loop"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("a", type=Path)
    ap.add_argument("b", type=Path)
    ap.add_argument("dest", type=Path)
    ap.add_argument("--anims", default="run_gun,idle_combat,jump")
    ap.add_argument("--rotulos", default="12 fps (hoy),24 fps (prueba)")
    ap.add_argument("--segundos", type=float, default=10.0)
    args = ap.parse_args()
    anims = args.anims.split(",")
    rot = args.rotulos.split(",")
    # la ventana, relativa al pivot (los pies), la misma para las dos corridas: la unión de todas las celdas
    win = {}
    for an in anims:
        x0 = y0 = 10 ** 9
        x1 = y1 = -10 ** 9
        for out in (args.a, args.b):
            cs, piv, _, _ = datos(out, an)
            for c in cs:
                ys, xs = np.nonzero(c[..., 3] > 20)
                if len(xs):
                    x0, x1 = min(x0, xs.min() - piv["x"]), max(x1, xs.max() - piv["x"])
                    y0, y1 = min(y0, ys.min() - piv["y"]), max(y1, ys.max() - piv["y"])
        win[an] = (int(x0) - 4, int(y0) - 4, int(x1) + 5, int(y1) + 5)
    tw = max(round((w[2] - w[0]) * K) for w in win.values())
    rows = [round((win[an][3] - win[an][1]) * K) for an in anims]
    pad, top, lab = 16, 40, 26
    W = 160 + 2 * (tw + pad) + pad
    H = top + sum(h + lab for h in rows) + pad
    W += W % 2
    H += H % 2
    f1, f2 = rv.font(20, True), rv.font(16, True)
    data = {(an, k): datos(out, an) for an in anims for k, out in enumerate((args.a, args.b))}

    def frame(t: float) -> np.ndarray:
        s = Image.new("RGB", (W, H), (30, 32, 40))
        d = ImageDraw.Draw(s)
        for k in range(2):
            d.text((160 + pad + k * (tw + pad), 10), rot[k], fill=(240, 240, 240), font=f1)
        y = top
        for an, rh in zip(anims, rows):
            d.text((12, y + rh // 2 - 10), an, fill=(240, 240, 240), font=f2)
            for k in range(2):
                cs, piv, fps, loop = data[(an, k)]
                n = len(cs)
                if loop:
                    i = int(t * fps) % n
                else:   # una vez, con 0,4 s quieto al principio y 0,6 s al final
                    per = 0.4 + n / fps + 0.6
                    u = t % per
                    i = 0 if u < 0.4 else min(n - 1, int((u - 0.4) * fps))
                c = cs[i]
                x0, y0, x1, y1 = win[an]
                im = Image.new("RGBA", (x1 - x0, y1 - y0), (*rv.GREEN, 255))
                im.alpha_composite(Image.fromarray(c, "RGBA"), (int(-piv["x"] - x0), int(-piv["y"] - y0)))
                im = im.resize((round((x1 - x0) * K), rh), Image.BILINEAR).convert("RGB")
                s.paste(im, (160 + pad + k * (tw + pad) + (tw - im.width) // 2, y))
                d.text((160 + pad + k * (tw + pad), y + rh + 3), f"{n} cuadros", fill=(200, 200, 200), font=f2)
            y += rh + lab
        return np.array(s)

    frames = [frame(i / FPS) for i in range(int(args.segundos * FPS))]
    args.dest.parent.mkdir(parents=True, exist_ok=True)
    imgio.encode_rgb_video(frames, args.dest, FPS, crf=16, pix_fmt="yuv420p")
    Image.fromarray(frames[int(1.2 * FPS)]).save(args.dest.with_suffix(".png"))
    print(f"✓ {args.dest} ({W}×{H}, {len(frames)} cuadros a {FPS} fps) y {args.dest.with_suffix('.png').name}")


if __name__ == "__main__":
    main()
