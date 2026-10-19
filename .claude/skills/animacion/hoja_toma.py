"""Hoja de contacto de una toma cruda (el .mp4 tal como sale de Kling) sobre verde, para elegir tomas y cuadros.

Recorta el fondo con el mismo keyer por distancia que usa el pipeline (contra el color del borde del cuadro), pega cada
cuadro sobre verde puro y los pone en grilla, todos con el mismo recorte (la unión de las cajas de todos los cuadros):
así se ve si el personaje se mueve en el cuadro, crece o se encoge. Cada cuadro lleva su número nativo (24 fps), el
que se usa en `trim` y `frames` de character.toml. Por defecto muestra uno de cada dos (12 fps, el del juego).

Uso (desde la raíz del repo):

    uv run --project pipeline python .claude/skills/animacion/hoja_toma.py clips/x.mp4 [más.mp4 ...] \
        --out characters/lowpoly/revision [--step 2] [--cols 12] [--alto 200] [--desde 0] [--hasta 999]
        [--cuadros 22,26,48] [--recorte x0,y0,x1,y1] [--sufijo _detalle] [--nombre throw]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from spritepipe import chroma, imgio

GREEN = (0, 255, 0)


def keyed(frames: np.ndarray) -> np.ndarray:
    """Alfa por cuadro (N×H×W, 0..1) con el keyer por distancia contra el color del borde del primer cuadro."""
    key = chroma.border_color(frames[0].astype(np.float32) / 255.0)
    out = []
    for f in frames:
        a = np.clip(chroma.estimate_alpha(f.astype(np.float32) / 255.0, key, "distance"), 0, 1)
        a = np.clip((a - 0.12) / (0.80 - 0.12), 0, 1)
        solid = (a > 0.5).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(solid, connectivity=8)
        keep = np.zeros(n, bool)
        keep[1:] = st[1:, cv2.CC_STAT_AREA] >= 64
        near = cv2.dilate(keep[lab].astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
        a[~near] = 0
        out.append(a)
    return np.stack(out)


def font(size: int) -> ImageFont.ImageFont:
    for p in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"):
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            pass
    return ImageFont.load_default()


def sheet(clip: Path, out_dir: Path, step: int, cols: int, alto: int, desde: int, hasta: int,
          cuadros: list[int] | None = None, recorte: tuple[int, int, int, int] | None = None, sufijo: str = "",
          nombre: str | None = None) -> Path:
    info = imgio.probe(clip)
    frames = imgio.read_video(clip, info)
    if cuadros:
        idx = [i for i in cuadros if 0 <= i < len(frames)]
    else:
        idx = [i for i in range(len(frames)) if desde <= i <= hasta and (i - desde) % step == 0]
    alpha = keyed(frames[idx])
    # el recorte sigue al personaje (el componente más grande de cada cuadro): lo que sale volando (granada, rayos)
    # se ve sólo si pasa cerca, y no achica todo
    boxes = []
    for a in alpha:
        n, _, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8), connectivity=8)
        if n > 1:
            i = 1 + int(st[1:, cv2.CC_STAT_AREA].argmax())
            x, y, w, h = st[i, :4]
            boxes.append((x, y, x + w, y + h))
    pad = 24
    y0 = max(0, min(b[1] for b in boxes) - pad)
    y1 = min(frames.shape[1], max(b[3] for b in boxes) + pad)
    x0 = max(0, min(b[0] for b in boxes) - pad)
    x1 = min(frames.shape[2], max(b[2] for b in boxes) + pad)
    if recorte:
        x0, y0, x1, y1 = recorte
    s = alto / (y1 - y0)
    w = max(1, round((x1 - x0) * s))
    rows = (len(idx) + cols - 1) // cols
    head = 34
    img = Image.new("RGB", (cols * w, head + rows * (alto + 22)), (30, 30, 30))
    d = ImageDraw.Draw(img)
    d.text((8, 6), f"{clip.name}  ·  {len(frames)} cuadros a {info.get('fps', 24):g} fps  ·  "
                   f"{'cuadros sueltos' if cuadros else f'uno de cada {step}'}  ·  "
                   f"recorte x {x0}-{x1}, y {y0}-{y1}", fill=(230, 230, 230), font=font(18))
    f = font(16)
    for k, (i, a) in enumerate(zip(idx, alpha)):
        rgb = frames[i, y0:y1, x0:x1].astype(np.float32)
        aa = a[y0:y1, x0:x1, None]
        comp = rgb * aa + np.array(GREEN, np.float32) * (1 - aa)
        tile = Image.fromarray(comp.round().astype(np.uint8)).resize((w, alto), Image.LANCZOS)
        cx, cy = (k % cols) * w, head + (k // cols) * (alto + 22)
        img.paste(tile, (cx, cy + 22))
        d.text((cx + 4, cy + 2), str(i), fill=(255, 255, 255), font=f)
    out_dir.mkdir(parents=True, exist_ok=True)
    tramo = f"_{desde}-{min(hasta, len(frames) - 1)}" if not cuadros and (desde > 0 or hasta < len(frames) - 1) else ""
    dst = out_dir / f"{nombre or clip.stem + tramo}{sufijo}.png"
    img.save(dst)
    return dst


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", type=Path, nargs="+")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--step", type=int, default=2, help="uno de cada N cuadros nativos (2: 24 → 12 fps)")
    ap.add_argument("--cols", type=int, default=12)
    ap.add_argument("--alto", type=int, default=200, help="alto de cada cuadro en la hoja, en px")
    ap.add_argument("--desde", type=int, default=0)
    ap.add_argument("--hasta", type=int, default=10**6)
    ap.add_argument("--cuadros", help="cuadros sueltos, separados por coma (pisa --step, --desde y --hasta)")
    ap.add_argument("--recorte", help="x0,y0,x1,y1 en px del video (por defecto, la caja del personaje)")
    ap.add_argument("--sufijo", default="", help="se agrega al nombre de la hoja")
    ap.add_argument("--nombre", help="nombre de la hoja (sin .png); por defecto, el del clip y el tramo")
    args = ap.parse_args()
    cuadros = [int(x) for x in args.cuadros.split(",")] if args.cuadros else None
    recorte = tuple(int(x) for x in args.recorte.split(",")) if args.recorte else None
    for c in args.clips:
        print(sheet(c, args.out, args.step, args.cols, args.alto, args.desde, args.hasta, cuadros, recorte,
                    args.sufijo, args.nombre))


if __name__ == "__main__":
    main()
