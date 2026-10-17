"""Del render de Blender (PNG con alfa por cuadro) al clip 16:9 sobre #C42D7D y a la tira cuadro por cuadro sobre verde.

    uv run --project pipeline python characters/lowpoly/3d/post.py idle correr

Por clip escribe `clips/<clip>.mp4` (1920×1080, 24 fps, el ciclo repetido hasta pasar los 5 s, como los clips de
video del bake-off), `clips/<clip>_ciclo.mp4` (un solo ciclo) y `tiras/<clip>_verde.png` (todos los cuadros del
ciclo a 12 fps, recortados al personaje, sobre verde y numerados).
"""

from __future__ import annotations

import argparse
import math
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

AQUI = Path(__file__).resolve().parent
FONDO = (0xC4, 0x2D, 0x7D)
VERDE = (0, 255, 0)
FPS = 24
MIN_S = 5.0


def cuadros(clip: str) -> list[Path]:
    fs = sorted((AQUI / "render" / clip).glob("*.png"))
    if not fs:
        raise SystemExit(f"no hay cuadros en render/{clip}/: correr antes render.py")
    return fs


def sobre(rgba: Image.Image, color) -> Image.Image:
    fondo = Image.new("RGBA", rgba.size, color + (255,))
    return Image.alpha_composite(fondo, rgba).convert("RGB")


def video(frames: list[Path], dest: Path, repetir: int) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(".txt")
    lines = []
    for _ in range(repetir):
        lines += [f"file '{f.as_posix()}'\nduration {1 / FPS:.6f}" for f in frames]
    tmp.write_text("\n".join(lines) + f"\nfile '{frames[-1].as_posix()}'\n")
    # mismo color de fondo que la pose; yuv420p como los clips de los modelos de video
    subprocess.run([
        "ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp),
        "-filter_complex", f"color=c=0x{''.join(f'{c:02X}' for c in FONDO)}:s=1920x1080:r={FPS}[bg];"
                           "[bg][0:v]overlay=shortest=1:format=auto,format=yuv420p",
        "-r", str(FPS), "-c:v", "libx264", "-crf", "10", "-preset", "slow", "-movflags", "+faststart", str(dest)],
        check=True)
    tmp.unlink()


def tira(frames: list[Path], dest: Path, paso: int = 2, cols: int = 8) -> None:
    ims = [Image.open(f).convert("RGBA") for f in frames[::paso]]
    caja = None
    for im in ims:
        b = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
        if b:
            caja = b if caja is None else (min(caja[0], b[0]), min(caja[1], b[1]), max(caja[2], b[2]), max(caja[3], b[3]))
    m = 12
    caja = (caja[0] - m, caja[1] - m, caja[2] + m, caja[3] + m)
    w, h = caja[2] - caja[0], caja[3] - caja[1]
    filas = math.ceil(len(ims) / cols)
    hoja = Image.new("RGB", (cols * (w + 4) - 4, filas * (h + 22)), (255, 255, 255))
    d = ImageDraw.Draw(hoja)
    for i, im in enumerate(ims):
        x, y = (i % cols) * (w + 4), (i // cols) * (h + 22)
        hoja.paste(sobre(im.crop(caja), VERDE), (x, y + 20))
        d.text((x + 4, y + 4), f"{i * paso}", fill=(0, 0, 0))
    dest.parent.mkdir(parents=True, exist_ok=True)
    hoja.save(dest)


def contra_pose(frame: Path, dest: Path) -> None:
    """La pose y el cuadro 0 lado a lado (recortados al personaje) y superpuestos al 50 %."""
    pose = Image.open(AQUI.parent / "poses" / "perfil_dullmagenta_16x9.png").convert("RGB")
    r = sobre(Image.open(frame).convert("RGBA"), FONDO)
    caja = (700, 200, 1220, 820)
    a, b = pose.crop(caja), r.crop(caja)
    mezcla = Image.blend(a, b, 0.5)
    w, h = a.size
    hoja = Image.new("RGB", (3 * w + 8, h), (255, 255, 255))
    for i, im in enumerate((a, b, mezcla)):
        hoja.paste(im, (i * (w + 4), 0))
    dest.parent.mkdir(parents=True, exist_ok=True)
    hoja.save(dest)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("clips", nargs="+")
    ap.add_argument("--contra-pose", action="store_true", help="sólo la comparación del cuadro 0 con la pose")
    a = ap.parse_args()
    for c in a.clips:
        if a.contra_pose:
            contra_pose(cuadros(c)[0], AQUI / "tiras" / f"{c}_contra_pose.png")
            continue
        fs = cuadros(c)
        rep = max(1, math.ceil(MIN_S * FPS / len(fs)))
        video(fs, AQUI / "clips" / f"{c}.mp4", rep)
        video(fs, AQUI / "clips" / f"{c}_ciclo.mp4", 1)
        tira(fs, AQUI / "tiras" / f"{c}_verde.png")
        a0 = np.asarray(Image.open(fs[0]).getchannel("A")) > 8
        ys, xs = np.nonzero(a0)
        print(f"{c}: {len(fs)} cuadros ({len(fs) / FPS:.2f} s), x{rep} → clips/{c}.mp4; cuadro 0 caja "
              f"x {xs.min()}–{xs.max()} y {ys.min()}–{ys.max()} (alto {ys.max() - ys.min() + 1} px)")


if __name__ == "__main__":
    main()
