"""Análisis rápido de un clip a baja resolución: fondo, máscara aproximada, bbox y movimiento.

Lo usan el QA (paso 4) y la búsqueda de loop (paso 6). Trabaja a ~240 px de ancho para
que un clip de 8 s se analice en un par de segundos.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from . import chroma, imgio

ANALYSIS_WIDTH = 240


@dataclass
class ClipAnalysis:
    n: int
    full_size: tuple[int, int]  # (W, H) a resolución completa
    factor: float  # full / small
    keys: np.ndarray  # (n, 3) color de fondo por frame, 0..1
    masks: list[np.ndarray]  # máscara bool aproximada por frame (baja resolución)
    gray: list[np.ndarray]  # luma float32 del personaje con el fondo en 0 (baja resolución)
    bbox: np.ndarray  # (n, 4) x0, y0, x1, y1 en px de resolución completa (NaN si no hay personaje)
    centroid: np.ndarray  # (n, 2) en px de resolución completa
    diff_global: np.ndarray  # (n-1,) MAD 0..255 entre frames consecutivos, todo el cuadro
    diff_char: np.ndarray  # (n-1,) MAD 0..255 dentro de la unión de máscaras: movimiento real
    bg_std: np.ndarray  # (n,) desvío del fondo en 0..255: gradientes, ruido, flicker
    touches_edge: np.ndarray  # (n,) bool: el personaje toca el borde del cuadro

    @property
    def heights(self) -> np.ndarray:
        return self.bbox[:, 3] - self.bbox[:, 1]


def analyze(frame_paths: list[Path], key_override: np.ndarray | None = None) -> ClipAnalysis:
    first = imgio.load(frame_paths[0])
    H, W = first.shape[:2]
    factor = W / ANALYSIS_WIDTH
    size = (ANALYSIS_WIDTH, max(1, round(H / factor)))
    kernel = np.ones((3, 3), np.uint8)

    n = len(frame_paths)
    keys = np.zeros((n, 3), np.float32)
    masks, grays = [], []
    bbox = np.full((n, 4), np.nan)
    centroid = np.full((n, 2), np.nan)
    bg_std = np.zeros(n)
    touches = np.zeros(n, bool)
    small_prev = None
    diff_g, diff_c = [], []

    for i, p in enumerate(frame_paths):
        img = first if i == 0 else imgio.load(p)
        small = cv2.resize(img[..., :3], size, interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
        key = key_override if key_override is not None else chroma.border_color(small, width=3)
        keys[i] = key
        a = chroma.estimate_alpha(small, key)
        m = cv2.morphologyEx((a > 0.5).astype(np.uint8), cv2.MORPH_OPEN, kernel).astype(bool)
        masks.append(m)
        luma = small @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        grays.append(np.where(m, luma, 0.0).astype(np.float32))
        bg = small[a < 0.05]
        bg_std[i] = float(bg.std(axis=0).mean() * 255) if len(bg) else np.nan

        ys, xs = np.nonzero(m)
        if len(xs):
            bbox[i] = [xs.min() * factor, ys.min() * factor, (xs.max() + 1) * factor, (ys.max() + 1) * factor]
            centroid[i] = [(xs.mean() + 0.5) * factor, (ys.mean() + 0.5) * factor]
            touches[i] = xs.min() <= 1 or ys.min() <= 1 or xs.max() >= size[0] - 2 or ys.max() >= size[1] - 2

        if small_prev is not None:
            d = np.abs(small - small_prev[0]).mean(axis=-1) * 255
            diff_g.append(float(d.mean()))
            union = m | small_prev[1]
            diff_c.append(float(d[union].mean()) if union.any() else 0.0)
        small_prev = (small, m)

    return ClipAnalysis(
        n=n, full_size=(W, H), factor=factor, keys=keys, masks=masks, gray=grays,
        bbox=bbox, centroid=centroid, diff_global=np.array(diff_g), diff_char=np.array(diff_c),
        bg_std=bg_std, touches_edge=touches,
    )


def linear_trend(values: np.ndarray) -> tuple[float, float]:
    """Pendiente por frame y ordenada de un ajuste lineal, ignorando NaN."""
    t = np.arange(len(values), dtype=float)
    ok = ~np.isnan(values)
    if ok.sum() < 2:
        return 0.0, float(np.nanmean(values)) if ok.any() else 0.0
    slope, intercept = np.polyfit(t[ok], values[ok], 1)
    return float(slope), float(intercept)
