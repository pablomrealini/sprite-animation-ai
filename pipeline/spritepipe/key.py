"""Paso 7: sacar el fondo con un chroma key determinístico.

Verde o magenta usan diferencia de color; un fondo plano no cromático (blanco, gris, crema)
usa distancia ΔE en Lab, que anda bien si el personaje tiene contorno. Con un fondo plano, el key le gana a cualquier matting por IA: aplica la misma regla en
todos los frames, así que no parpadea. Por frame:
  1. color de fondo real (mediana del borde) o el que fija la config;
  2. alpha_raw por diferencia de color (ver chroma.py) y rampa entre las tolerancias;
  3. islas chicas fuera (ruido de compresión, motas);
  4. modo "connected" (por defecto con fondos no cromáticos): los huecos chicos del color de
     fondo que no tocan el borde se conservan (ojos, brillos);
  5. unmix del borde: F = (C - (1-α)K) / α, que saca el halo verde en vez de taparlo;
  6. despill en una banda angosta alrededor del borde, por si quedó contaminación;
  7. RGB en 0 donde α = 0, para que ningún resize posterior arrastre el verde.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from . import chroma, imgio
from .config import Character


def key_frame(img_u8: np.ndarray, ch: Character, fixed_key: np.ndarray | None) -> tuple[np.ndarray, np.ndarray]:
    img = img_u8[..., :3].astype(np.float32) / 255.0
    key = fixed_key if fixed_key is not None else chroma.border_color(img)
    method = ch.key_method if ch.key_method != "auto" else chroma.method_for(key)
    mode = ch.key_mode if ch.key_mode != "auto" else ("global" if method == "chroma" else "connected")
    a_true = np.clip(chroma.estimate_alpha(img, key, method), 0.0, 1.0)
    lo, hi = ch.key_tolerance
    alpha = np.clip((a_true - lo) / (hi - lo), 0.0, 1.0)

    solid = (alpha > 0.5).astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(solid, connectivity=8)
    keep = np.zeros(count, bool)
    keep[1:] = stats[1:, cv2.CC_STAT_AREA] >= ch.min_island_px
    solid = keep[labels]
    near = cv2.dilate(solid.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    alpha[~near] = 0.0  # semitransparentes sueltos lejos del personaje

    if mode == "connected":
        # Huecos del color de fondo que no tocan el borde y son chicos (ojos, brillos, dientes)
        # quedan opacos. Los grandes (brazo contra el torso) son fondo de verdad.
        bg = (alpha == 0).astype(np.uint8)
        count, labels, stats, _ = cv2.connectedComponentsWithStats(bg, connectivity=4)
        border_labels = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
        small = stats[:, cv2.CC_STAT_AREA] < ch.hole_max_frac * max(1, int(solid.sum()))
        fill = np.zeros(count, bool)
        fill[1:] = small[1:]
        fill[border_labels] = False
        interior = fill[labels]
        alpha[interior] = 1.0
        a_true[interior] = 1.0

    edge = (alpha > 0) & (alpha < 1)
    a = np.maximum(a_true, 0.15)[..., None]
    unmixed = np.clip((img - (1 - a) * key) / a, 0.0, 1.0)
    rgb = np.where(edge[..., None], unmixed, img)

    if ch.despill > 0 and method == "chroma":
        transparent = (alpha < 0.5).astype(np.uint8)
        k = 2 * ch.despill_band_px + 1
        band = cv2.dilate(transparent, np.ones((k, k), np.uint8)).astype(bool) & (alpha > 0)
        rgb[band] = chroma.despill(rgb[band], key, ch.despill)

    rgba = np.dstack([np.clip(rgb, 0, 1), alpha])
    rgba[alpha == 0] = 0.0
    return (rgba * 255 + 0.5).astype(np.uint8), key, method, mode


def run(in_dir: Path, out_dir: Path, ch: Character) -> dict:
    fixed = None if ch.key_color == "auto" else chroma.parse_hex(ch.key_color)
    imgio.reset_dir(out_dir)
    keys, methods = [], set()
    for p in imgio.frames(in_dir):
        rgba, key, method, mode = key_frame(imgio.load(p), ch, fixed)
        keys.append(key)
        methods.add((method, mode))
        imgio.save(out_dir / p.name, rgba)
    k = np.median(np.array(keys), axis=0)
    return {
        "key_color": "#" + "".join(f"{round(c * 255):02X}" for c in k),
        "method": sorted(methods), "tolerance": list(ch.key_tolerance), "despill": ch.despill,
    }
