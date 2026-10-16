"""Keyer por diferencia de color (la familia de Keylight/Primatte).

Para un fondo verde, la "cantidad de pantalla" de un píxel es g - max(r, b). En el color de
key vale screen(key); en un píxel del personaje vale 0 o menos. Para una mezcla de borde
α·F + (1-α)·K con F neutro, screen = (1-α)·screen(key) exacto, así que
alpha_raw = 1 - screen(p)/screen(key) estima α sin calibración. Generaliza a magenta y azul
tomando canales dominantes D y opuestos O: screen = min(D) - max(O).
"""

from __future__ import annotations

import numpy as np


def parse_hex(value: str) -> np.ndarray:
    v = value.lstrip("#")
    return np.array([int(v[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32) / 255.0


def split_channels(key: np.ndarray) -> tuple[list[int], list[int]]:
    """Canales dominantes del color de key (verde -> [g], magenta -> [r, b])."""
    mid = (key.max() + key.min()) / 2
    dom = [i for i in range(3) if key[i] > mid]
    opp = [i for i in range(3) if key[i] <= mid]
    return dom, opp


def screen(img: np.ndarray, dom: list[int], opp: list[int]) -> np.ndarray:
    return img[..., dom].min(axis=-1) - img[..., opp].max(axis=-1)


def key_strength(key: np.ndarray) -> float:
    dom, opp = split_channels(key)
    if not dom or not opp:  # gris o blanco exacto: no hay canal dominante, no es un color de key
        return 0.0
    return float(screen(key[None, :], dom, opp)[0])


def raw_alpha(img: np.ndarray, key: np.ndarray) -> np.ndarray:
    """img float32 0..1 HxWx3. 0 = fondo, 1 = personaje (puede pasar de 1)."""
    dom, opp = split_channels(key)
    s_key = screen(key[None, :], dom, opp)[0]
    return 1.0 - screen(img, dom, opp) / s_key


CHROMA_MIN_STRENGTH = 0.25  # por debajo, el fondo no es un color de key (blanco, gris, crema)
DISTANCE_SCALE = 40.0  # ΔE (Lab) que cuenta como personaje opaco en el key por distancia


def method_for(key: np.ndarray) -> str:
    return "chroma" if key_strength(key) >= CHROMA_MIN_STRENGTH else "distance"


def _lab(img: np.ndarray) -> np.ndarray:
    import cv2
    return cv2.cvtColor(np.ascontiguousarray(img, np.float32), cv2.COLOR_RGB2LAB)


def estimate_alpha(img: np.ndarray, key: np.ndarray, method: str | None = None) -> np.ndarray:
    """Alpha aproximado 0..1+ para cualquier fondo plano.

    chroma: diferencia de color (exacto para bordes contra colores neutros).
    distance: ΔE en Lab contra el color de fondo / DISTANCE_SCALE. Sirve para fondos blancos o
    grises cuando el personaje tiene contorno, que es el caso de un concept tipo Kingdom Rush.
    """
    method = method or method_for(key)
    if method == "chroma":
        return raw_alpha(img, key)
    lab = _lab(img)
    klab = _lab(key.reshape(1, 1, 3)).reshape(3)
    return np.sqrt(((lab - klab) ** 2).sum(-1)) / DISTANCE_SCALE


def border_color(img: np.ndarray, width: int = 8) -> np.ndarray:
    """Mediana de un marco de `width` px: el color real del fondo, que nunca es #00FF00 exacto."""
    strips = [img[:width].reshape(-1, 3), img[-width:].reshape(-1, 3),
              img[:, :width].reshape(-1, 3), img[:, -width:].reshape(-1, 3)]
    return np.median(np.concatenate(strips), axis=0).astype(np.float32)


def despill(img: np.ndarray, key: np.ndarray, strength: float = 1.0) -> np.ndarray:
    """Limita los canales dominantes al máximo de los opuestos (g <= max(r, b) para verde)."""
    dom, opp = split_channels(key)
    spill = np.maximum(screen(img, dom, opp), 0.0) * strength
    out = img.copy()
    for c in dom:
        out[..., c] -= spill
    return out
