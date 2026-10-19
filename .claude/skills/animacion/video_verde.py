"""El tramo útil de una o más tomas sobre verde, como .mp4 (y su hoja de contacto), para que Pablo lo apruebe.

Mismo keyer que hoja_toma.py (por distancia, contra el color del borde), todo con un solo recorte (la caja del
personaje en todos los cuadros: lo que sale volando lejos, como una explosión fuera de cuadro, queda afuera) y con el
número nativo de cada cuadro en la esquina, el mismo de las hojas y de `trim`/`frames` de character.toml. Con varias
tomas, el número lleva el nombre corto de la toma (`slide_in_1 47`).

Cada tramo es `clip.mp4` (entero, o --desde/--hasta) o `clip.mp4:40-72` o `clip.mp4:18-35,38-44` (rangos de cuadros
nativos, incluidos los dos extremos). Los tramos se pegan en orden: sirve para mostrar una entrada y una salida que
salen de clips distintos y empalman en la misma pose. Todas las tomas tienen que tener la misma resolución. Un `@dx`
al final (`clip.mp4:18-46@-46`) corre ese tramo dx px en x, para mostrar el empalme como lo alinearía Limpieza
cuando Kling dejó al personaje en otro lugar.

Uso (desde la raíz del repo):

    uv run --project pipeline python .claude/skills/animacion/video_verde.py clips/x.mp4 --desde 16 --hasta 80 \
        --out characters/lowpoly/revision/para_pablo/throw.mp4
    uv run --project pipeline python .claude/skills/animacion/video_verde.py clips/in.mp4:40-72 clips/out.mp4:18-35,38-44 \
        --out characters/lowpoly/revision/para_pablo/slide.mp4 --hoja characters/lowpoly/revision/para_pablo/slide.png
    [--fps 24] [--alto 540] [--recorte x0,y0,x1,y1]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from hoja_toma import GREEN, font, keyed
from spritepipe import imgio


def parse_tramo(spec: str, desde: int, hasta: int) -> tuple[Path, list[tuple[int, int]], int]:
    dx = 0
    if "@" in spec:
        spec, _, d = spec.rpartition("@")
        dx = int(d)
    path, _, rangos = spec.rpartition(":") if spec.rsplit(":", 1)[-1][:1].isdigit() else (spec, "", "")
    if not rangos:
        return Path(spec), [(desde, hasta)], dx
    out = []
    for r in rangos.split(","):
        a, _, b = r.partition("-")
        out.append((int(a), int(b or a)))
    return Path(path), out, dx


def shift_x(img: np.ndarray, dx: int) -> np.ndarray:
    """Corre la imagen dx px en x; lo que queda descubierto va en 0 (en el alfa: fondo)."""
    out = np.zeros_like(img)
    if dx > 0:
        out[:, dx:] = img[:, :-dx]
    elif dx < 0:
        out[:, :dx] = img[:, -dx:]
    else:
        out[:] = img
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("tramos", nargs="+", help="clip.mp4, clip.mp4:40-72 o clip.mp4:18-35,38-44")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--hoja", type=Path, help="también la hoja de contacto de los mismos cuadros (.png)")
    ap.add_argument("--desde", type=int, default=0)
    ap.add_argument("--hasta", type=int, default=10**6)
    ap.add_argument("--fps", type=float, help="por defecto, los del clip; 12 toma uno de cada dos")
    ap.add_argument("--alto", type=int, default=540, help="alto del video, en px")
    ap.add_argument("--recorte", help="x0,y0,x1,y1 en px del video (por defecto, la caja del personaje)")
    args = ap.parse_args()

    tramos = [parse_tramo(t, args.desde, args.hasta) for t in args.tramos]
    varios = len({p for p, _, _ in tramos}) > 1
    frames, alphas, labels, src_fps = [], [], [], None
    for path, rangos, dx in tramos:
        info = imgio.probe(path)
        video = imgio.read_video(path, info)
        src_fps = src_fps or info.get("fps", 24)
        step = max(1, round(src_fps / (args.fps or src_fps)))
        idx = [i for a, b in rangos for i in range(max(0, a), min(len(video) - 1, b) + 1, step)]
        corto = path.stem.removeprefix("kling-o3-std_")
        frames += [shift_x(video[i], dx) for i in idx]
        alphas += [shift_x(a, dx) for a in keyed(video[idx])]
        labels += [f"{corto} {i}" if varios else str(i) for i in idx]
    fps = args.fps or src_fps

    if args.recorte:
        x0, y0, x1, y1 = (int(v) for v in args.recorte.split(","))
    else:
        boxes = []
        for a in alphas:
            n, _, st, _ = cv2.connectedComponentsWithStats((a > 0.5).astype(np.uint8), connectivity=8)
            if n > 1:
                i = 1 + int(st[1:, cv2.CC_STAT_AREA].argmax())
                x, y, w, h = st[i, :4]
                boxes.append((x, y, x + w, y + h))
        pad = 40
        x0 = max(0, min(b[0] for b in boxes) - pad)
        y0 = max(0, min(b[1] for b in boxes) - pad)
        x1 = min(frames[0].shape[1], max(b[2] for b in boxes) + pad)
        y1 = min(frames[0].shape[0], max(b[3] for b in boxes) + pad)
    s = args.alto / (y1 - y0)
    w = round((x1 - x0) * s) // 2 * 2
    h = args.alto // 2 * 2
    f = font(max(14, h // 22))
    out, limpios = [], []
    for fr, a, label in zip(frames, alphas, labels):
        rgb = fr[y0:y1, x0:x1].astype(np.float32)
        aa = a[y0:y1, x0:x1, None]
        comp = rgb * aa + np.array(GREEN, np.float32) * (1 - aa)
        im = Image.fromarray(comp.round().astype(np.uint8)).resize((w, h), Image.LANCZOS)
        limpios.append(im.copy())
        ImageDraw.Draw(im).text((8, 6), label, fill=(0, 0, 0), font=f)
        out.append(im)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    imgio.encode_rgb_video([np.asarray(im) for im in out], args.out, fps)
    print(f"✓ {args.out}: {len(out)} cuadros, {w}×{h}, {fps:g} fps, recorte x {x0}-{x1}, y {y0}-{y1}")

    if args.hoja:
        cols, tw, th, lh = 12, round(w * 200 / h), 200, 22
        rows = (len(out) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tw, 34 + rows * (th + lh)), (30, 30, 30))
        sd = ImageDraw.Draw(sheet)
        ImageDraw.Draw(sheet).text((8, 6), f"{args.out.name}  ·  {len(out)} cuadros a {fps:g} fps  ·  "
                                           + "  +  ".join(Path(t).name for t in args.tramos),
                                   fill=(230, 230, 230), font=font(18))
        for k, (im, label) in enumerate(zip(limpios, labels)):
            cx, cy = (k % cols) * tw, 34 + (k // cols) * (th + lh)
            sheet.paste(im.resize((tw, th), Image.LANCZOS), (cx, cy + lh))
            sd.text((cx + 4, cy + 2), label, fill=(255, 255, 255), font=font(16))
        sheet.save(args.hoja)
        print(f"✓ {args.hoja}")


if __name__ == "__main__":
    main()
