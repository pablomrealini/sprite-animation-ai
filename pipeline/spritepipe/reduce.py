"""Paso 10: reducir una sola vez, desde los frames alineados a resolución completa.

HD: área (o Lanczos si se agranda) siempre en alfa premultiplicado; sin premultiplicar, el
color de los píxeles transparentes se mete en el borde como halo. Unsharp opcional sólo
sobre RGB. Variantes 0,5× y otras desde el mismo master.

Pixel art: factor entero F, promedio de área, UNA paleta para todas las animaciones del
personaje (k-means en Lab con semilla fija, o una paleta dada), sin dithering y con alfa
binario. Cuantizar cada frame por separado es lo que hace "hervir" la textura.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from . import imgio
from .config import Character


def _premul_resize(rgba: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    f = rgba.astype(np.float32) / 255.0
    a = f[..., 3:4]
    pm = np.dstack([f[..., :3] * a, a])
    shrink = size[0] < rgba.shape[1]
    out = cv2.resize(pm, size, interpolation=cv2.INTER_AREA if shrink else cv2.INTER_LANCZOS4)
    out = np.clip(out, 0.0, 1.0)
    a = out[..., 3:4]
    rgb = np.where(a > 1e-4, out[..., :3] / np.maximum(a, 1e-4), 0.0)
    return np.dstack([np.clip(rgb, 0, 1), a])


def _sharpen(rgba: np.ndarray, amount: float) -> np.ndarray:
    if amount <= 0:
        return rgba
    rgb = rgba[..., :3]
    blur = cv2.GaussianBlur(rgb, (0, 0), 0.8)
    rgba = rgba.copy()
    rgba[..., :3] = np.clip(rgb + amount * (rgb - blur), 0, 1)
    return rgba


def _to_u8(f: np.ndarray) -> np.ndarray:
    out = (f * 255 + 0.5).astype(np.uint8)
    out[out[..., 3] == 0, :3] = 0
    return out


def scale_tag(scale: float) -> str:
    return f"{scale:g}x"


def run_hd(ch: Character, aligned: dict[str, Path], out_root: Path, base_scale: float,
           canvas: dict) -> dict:
    variants = {}
    for mult in [1.0] + [s for s in ch.extra_scales if s != 1.0]:
        s = base_scale * mult
        size = (max(1, round(canvas["w"] * s)), max(1, round(canvas["h"] * s)))
        tag = scale_tag(mult)
        for name, d in aligned.items():
            out = imgio.reset_dir(out_root / tag / name)
            for p in imgio.frames(d):
                small = _premul_resize(imgio.load(p), size)
                imgio.save(out / p.name, _to_u8(_sharpen(small, ch.sharpen)))
        variants[tag] = {"w": size[0], "h": size[1], "scale": s}
    return variants


def _palette_from_file(path: Path) -> np.ndarray:
    img = imgio.load(path)
    px = img[..., :3].reshape(-1, 3) if img.shape[2] == 3 else img[img[..., 3] > 0][:, :3]
    return np.unique(px, axis=0).astype(np.uint8)


def _lab(rgb_u8: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(rgb_u8.reshape(-1, 1, 3), cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float32)


def _build_palette(samples: np.ndarray, k: int) -> np.ndarray:
    lab = _lab(samples)
    k = min(k, len(np.unique(samples, axis=0)))
    cv2.setRNGSeed(0)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.2)
    _, _, centers = cv2.kmeans(lab, k, None, crit, 4, cv2.KMEANS_PP_CENTERS)
    rgb = cv2.cvtColor(np.clip(centers, 0, 255).astype(np.uint8).reshape(-1, 1, 3), cv2.COLOR_LAB2RGB)
    return np.unique(rgb.reshape(-1, 3), axis=0)


def _quantize(rgba: np.ndarray, palette: np.ndarray, pal_lab: np.ndarray) -> np.ndarray:
    out = rgba.copy()
    solid = rgba[..., 3] >= 128
    px = rgba[solid][:, :3]
    if len(px):
        lab = _lab(px)
        d = ((lab[:, None, :] - pal_lab[None, :, :]) ** 2).sum(-1)
        out[solid, :3] = palette[d.argmin(1)]
    out[..., 3] = np.where(solid, 255, 0)
    out[~solid, :3] = 0
    return out


def run_pixel(ch: Character, aligned: dict[str, Path], out_root: Path, F: int, canvas: dict) -> dict:
    size = (canvas["w"] // F, canvas["h"] // F)
    small = {}
    for name, d in aligned.items():
        small[name] = [(p.name, _to_u8(_premul_resize(imgio.load(p), size))) for p in imgio.frames(d)]

    if ch.palette:
        palette = _palette_from_file(ch.palette)
    else:
        allpx = np.concatenate([img[img[..., 3] >= 128][:, :3] for frames in small.values() for _, img in frames])
        rng = np.random.default_rng(0)
        if len(allpx) > 200_000:
            allpx = allpx[rng.choice(len(allpx), 200_000, replace=False)]
        palette = _build_palette(allpx, ch.palette_colors)
    pal_lab = _lab(palette)

    tag = scale_tag(1.0)
    for name, frames in small.items():
        out = imgio.reset_dir(out_root / tag / name)
        for fname, img in frames:
            imgio.save(out / fname, _quantize(img, palette, pal_lab))
    swatch = palette.reshape(1, -1, 3)
    imgio.save(out_root / "palette.png", swatch)
    return {tag: {"w": size[0], "h": size[1], "scale": 1.0 / F, "palette_colors": int(len(palette))}}
