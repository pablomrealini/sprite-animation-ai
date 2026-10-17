"""Cuadro a cuadro de cada animación del atlas low-poly sobre verde (cuadros/<anim>.png), para revisarlas antes de
usarlas en el juego. Cada cuadro lleva su número y su duración; las animaciones del ranger con el mismo nombre se
arman al lado (cuadros/<anim>_ranger.png) para comparar.

Uso (desde la raíz del repo, después de `spritepipe run characters/lowpoly/character.toml`):

    uv run --project pipeline python characters/lowpoly/cuadros.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
GREEN = (0, 255, 0, 255)
COLS = 12
H = 220  # alto de cada cuadro en la hoja, en px


def sheet(char: Path, name: str, anim: str, out: Path) -> int:
    idx = json.loads((char / "out" / f"{name}.json").read_text(encoding="utf-8"))
    frames = idx["variants"]["1x"]["animations"].get(anim, {}).get("frames")
    grid = char / "out" / "sheets" / "1x" / f"{anim}.png"
    meta = char / "out" / "sheets" / "1x" / f"{anim}.json"
    if not frames or not grid.exists():
        return 0
    g = json.loads(meta.read_text(encoding="utf-8"))
    cw, ch = g.get("cell", g.get("frame", {})).get("w"), g.get("cell", g.get("frame", {})).get("h")
    im = Image.open(grid).convert("RGBA")
    cols = im.width // cw
    cells = [im.crop(((i % cols) * cw, (i // cols) * ch, (i % cols + 1) * cw, (i // cols + 1) * ch)) for i in range(len(frames))]
    m = np.zeros((ch, cw), bool)
    for c in cells:
        m |= np.array(c)[..., 3] > 20
    ys, xs = np.nonzero(m)
    box = (max(0, xs.min() - 6), max(0, ys.min() - 6), min(cw, xs.max() + 7), min(ch, ys.max() + 7))
    k = H / (box[3] - box[1])
    w = round((box[2] - box[0]) * k)
    n = len(cells)
    rows = -(-n // COLS)
    s = Image.new("RGB", (min(n, COLS) * (w + 4), rows * (H + 22)), (255, 255, 255))
    d = ImageDraw.Draw(s)
    for i, (c, f) in enumerate(zip(cells, frames)):
        bg = Image.new("RGBA", c.size, GREEN)
        bg.alpha_composite(c)
        t = bg.convert("RGB").crop(box).resize((w, H), Image.LANCZOS)
        x, y = (i % COLS) * (w + 4), (i // COLS) * (H + 22)
        s.paste(t, (x, y + 20))
        d.text((x + 2, y + 4), f"{i}  {round(f['duration'])} ms", fill=(0, 0, 0))
    out.parent.mkdir(parents=True, exist_ok=True)
    s.save(out)
    return n


def main() -> None:
    idx = json.loads((ROOT / "out" / "lowpoly.json").read_text(encoding="utf-8"))
    for anim in idx["variants"]["1x"]["animations"]:
        n = sheet(ROOT, "lowpoly", anim, ROOT / "cuadros" / f"{anim}.png")
        r = sheet(ROOT.parent / "ranger", "ranger", anim, ROOT / "cuadros" / f"{anim}_ranger.png")
        print(f"{anim:14s} {n:3d} cuadros" + (f"  (ranger {r})" if r else ""))


if __name__ == "__main__":
    main()
