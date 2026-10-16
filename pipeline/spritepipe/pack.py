"""Paso 12: empaquetar e importar.

Sale, por escala:
- atlas MaxRects con trim (los offsets se guardan, el pivot no se mueve), extrude, shape y
  border padding, frames idénticos fusionados (holds, ping-pongs) y multipack si no entra;
  el JSON sigue el formato "JSON (Hash)" de TexturePacker, que Phaser carga con load.atlas;
- una grilla sin trim por animación (celda = canvas), para Unity "Grid By Cell Size" y
  Godot "Add frames from a Sprite Sheet" sin plugins;
- un índice <personaje>.json con animaciones, duraciones, loop y pivot.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import imgio


@dataclass
class Sprite:
    name: str  # "walk/0000"
    img: np.ndarray  # recorte RGBA
    offset: tuple[int, int]  # posición del recorte dentro del canvas
    source: tuple[int, int]  # tamaño del canvas
    digest: str


class MaxRects:
    """MaxRects con heurística Best Short Side Fit (Jylänki, 2010)."""

    def __init__(self, w: int, h: int):
        self.free = [(0, 0, w, h)]

    def insert(self, rw: int, rh: int):
        best, best_key = None, None
        for fx, fy, fw, fh in self.free:
            if rw <= fw and rh <= fh:
                key = (min(fw - rw, fh - rh), max(fw - rw, fh - rh))
                if best_key is None or key < best_key:
                    best, best_key = (fx, fy), key
        if best is None:
            return None
        used = (best[0], best[1], rw, rh)
        self._split(used)
        return used

    def _split(self, u):
        ux, uy, uw, uh = u
        out = []
        for f in self.free:
            fx, fy, fw, fh = f
            if ux >= fx + fw or ux + uw <= fx or uy >= fy + fh or uy + uh <= fy:
                out.append(f)
                continue
            if ux > fx:
                out.append((fx, fy, ux - fx, fh))
            if ux + uw < fx + fw:
                out.append((ux + uw, fy, fx + fw - ux - uw, fh))
            if uy > fy:
                out.append((fx, fy, fw, uy - fy))
            if uy + uh < fy + fh:
                out.append((fx, uy + uh, fw, fy + fh - uy - uh))
        pruned = []
        for i, a in enumerate(out):
            contained = False
            for j, b in enumerate(out):
                if i != j and b[0] <= a[0] and b[1] <= a[1] and a[0] + a[2] <= b[0] + b[2] and a[1] + a[3] <= b[1] + b[3]:
                    if a == b and i < j:
                        continue  # de dos rectángulos iguales se queda el primero
                    contained = True
                    break
            if not contained:
                pruned.append(a)
        self.free = pruned


def trim(rgba: np.ndarray) -> tuple[np.ndarray, tuple[int, int]]:
    ys, xs = np.nonzero(rgba[..., 3])
    if not len(xs):
        return np.zeros((1, 1, 4), np.uint8), (0, 0)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    return rgba[y0:y1, x0:x1], (int(x0), int(y0))


def _try_pack(sizes: list[tuple[int, int]], w: int, h: int) -> list:
    mr = MaxRects(w, h)
    return [mr.insert(rw, rh) for rw, rh in sizes]


def _pages(sizes: list[tuple[int, int]], max_size: int, inner_pad: int, pot: bool) -> list[dict]:
    """Devuelve páginas {w, h, placements: {indice: (x, y)}} lo más compactas posible."""
    order = sorted(range(len(sizes)), key=lambda i: -max(sizes[i]))
    pages, remaining = [], order
    limit = max_size + inner_pad  # cada rect incluye su padding a derecha y abajo
    while remaining:
        rs = [sizes[i] for i in remaining]
        side = max(max(w for w, _ in rs), max(h for _, h in rs), int(math.sqrt(sum(w * h for w, h in rs))))
        w = h = min(limit, side)
        placed = None
        while True:
            res = _try_pack(rs, w, h)
            if all(r is not None for r in res):
                placed = res
                break
            if w >= limit and h >= limit:
                break
            if w <= h:
                w = min(limit, int(w * 1.08) + 8)
            else:
                h = min(limit, int(h * 1.08) + 8)
        if placed is None:
            placed = _try_pack(rs, limit, limit)
            if all(r is None for r in placed):
                raise ValueError(f"un frame de {rs[0]} no entra en un atlas de {max_size}")
        page = {"placements": {}}
        rest = []
        for i, r in zip(remaining, placed):
            if r is None:
                rest.append(i)
            else:
                page["placements"][i] = (r[0], r[1])
        used_w = max(page["placements"][i][0] + sizes[i][0] for i in page["placements"]) - inner_pad
        used_h = max(page["placements"][i][1] + sizes[i][1] for i in page["placements"]) - inner_pad
        if pot:
            used_w, used_h = (1 << max(0, (v - 1).bit_length()) for v in (used_w, used_h))
        page["w"], page["h"] = used_w, used_h
        pages.append(page)
        remaining = rest
    return pages


def _extrude(img: np.ndarray, e: int) -> np.ndarray:
    return np.pad(img, ((e, e), (e, e), (0, 0)), mode="edge") if e > 0 else img


def build_atlas(sprites: list[Sprite], out_dir: Path, base: str, max_size: int, padding: int,
                border: int, extrude: int, pot: bool, durations: dict[str, float],
                anim_frames: dict[str, list[str]], pivot: tuple[float, float]) -> list[dict]:
    """Escribe <base>-N.png y <base>-N.json. Devuelve, por página, sus frames."""
    unique: dict[str, int] = {}
    uniq_sprites: list[Sprite] = []
    for s in sprites:
        if s.digest not in unique:
            unique[s.digest] = len(uniq_sprites)
            uniq_sprites.append(s)
    e = extrude
    sizes = [(s.img.shape[1] + 2 * e + padding, s.img.shape[0] + 2 * e + padding) for s in uniq_sprites]
    pages = _pages(sizes, max_size - 2 * border, padding, pot)

    result = []
    for pi, page in enumerate(pages):
        W, H = page["w"] + 2 * border, page["h"] + 2 * border
        atlas = np.zeros((H, W, 4), np.uint8)
        rects = {}
        for ui, (x, y) in page["placements"].items():
            s = uniq_sprites[ui]
            ex = _extrude(s.img, e)
            atlas[border + y:border + y + ex.shape[0], border + x:border + x + ex.shape[1]] = ex
            rects[ui] = (border + x + e, border + y + e, s.img.shape[1], s.img.shape[0])
        frames = {}
        for s in sprites:
            ui = unique[s.digest]
            if ui not in rects:
                continue
            fx, fy, fw, fh = rects[ui]
            frames[s.name] = {
                "frame": {"x": fx, "y": fy, "w": fw, "h": fh},
                "rotated": False,
                "trimmed": (fw, fh) != s.source,
                "spriteSourceSize": {"x": s.offset[0], "y": s.offset[1], "w": fw, "h": fh},
                "sourceSize": {"w": s.source[0], "h": s.source[1]},
                "pivot": {"x": pivot[0], "y": pivot[1]},
                "duration": durations[s.name],
            }
        image = f"{base}-{pi}.png"
        imgio.save(out_dir / image, atlas, compression=9)
        anims = {a: [f for f in fs if f in frames] for a, fs in anim_frames.items()}
        imgio.write_json(out_dir / f"{base}-{pi}.json", {
            "frames": frames,
            "animations": {a: fs for a, fs in anims.items() if fs},
            "meta": {"app": "spritepipe", "version": "0.1", "image": image, "format": "RGBA8888",
                     "size": {"w": W, "h": H}, "scale": "1"},
        })
        result.append({"image": image, "data": f"{base}-{pi}.json", "w": W, "h": H, "frames": frames,
                       "unique_sprites": len(rects)})
    return result


def build_grid(frames: list[np.ndarray], out_png: Path, max_size: int) -> dict:
    h, w = frames[0].shape[:2]
    cols = max(1, min(len(frames), max_size // w))
    rows = math.ceil(len(frames) / cols)
    sheet = np.zeros((rows * h, cols * w, 4), np.uint8)
    for i, f in enumerate(frames):
        r, c = divmod(i, cols)
        sheet[r * h:(r + 1) * h, c * w:(c + 1) * w] = f
    imgio.save(out_png, sheet, compression=9)
    return {"cell": {"w": w, "h": h}, "cols": cols, "rows": rows, "count": len(frames),
            "oversize": sheet.shape[0] > max_size or sheet.shape[1] > max_size}


def sprite_from(name: str, rgba: np.ndarray) -> Sprite:
    img, off = trim(rgba)
    digest = hashlib.sha1(img.tobytes() + str(img.shape).encode()).hexdigest()
    return Sprite(name=name, img=img, offset=off, source=(rgba.shape[1], rgba.shape[0]), digest=digest)
