"""Paso 1: concepts sobre fondo blanco a un plantel de PNG con transparencia, todos iguales.

Cuando el concept no sale con transparencia viene aplanado sobre blanco, con la sombra de piso
dibujada como una línea negra que pasa por debajo de las botas y, a veces, con basura suelta en
el borde. Para un plantel además conviene que todos compartan canvas, escala y pivot, así las
animaciones se comparan y se intercambian sin acomodar nada.

- Fondo: lo casi blanco y neutro conectado al borde. Los blancos del personaje (casco, ojos,
  vincha) quedan encerrados por el contorno negro, así que no se tocan. El borde se desmezcla
  contra el blanco suponiendo que es contorno negro: α = (blanco - luminancia) / (blanco - tinta).
- Sombra: por columna, la racha opaca de más abajo en la franja del piso; si es corta
  (<= SHADOW_MAX_PX) es la línea y no una bota. Al sacarla, el blanco entre las piernas queda
  conectado al borde y se va con el fondo.
- Basura: sólo sobrevive la componente más grande.
- Plantel: escala nativa (no se re-muestrea), los pies en la misma fila y el centro de las botas
  en el centro del canvas, que es el pivot de todas las animaciones.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from . import imgio, pose

NEAR_WHITE = 238  # canal mínimo para contar como fondo
NEUTRAL = 10  # y diferencia máxima entre canales: un crema o un celeste claro no es fondo
INK = 30  # luminancia del contorno negro: de acá para abajo el borde es opaco
EDGE_PX = 2.5  # ancho de la banda del borde que se desmezcla contra el blanco
SHADOW_BAND_PX = 12  # alto de la franja del piso donde se busca la línea de sombra
SHADOW_MAX_PX = 8  # la línea mide 2-8 px; una bota de color, 20 o más
BG_TOL = 5  # un hueco entre las piernas a menos de esto del fondo, y neutro, es fondo
FEET_PX = 8  # filas sobre el piso que definen el ancho de las botas (el pivot)


def _from_border(mask: np.ndarray) -> np.ndarray:
    count, labels = cv2.connectedComponents(mask.astype(np.uint8), connectivity=4)
    edge = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
    keep = np.zeros(count, bool)
    keep[edge] = True
    keep[0] = False
    return keep[labels]


def _largest(mask: np.ndarray) -> np.ndarray:
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
    if count < 2:
        raise ValueError("no encontré ningún personaje sobre el fondo")
    return labels == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))


def _bottom_runs(ink: np.ndarray, floor: int) -> list[tuple[int, int, int]]:
    """Por columna con tinta en la franja del piso: (x, fila de arriba de la racha, fila de abajo)."""
    top = max(0, floor - SHADOW_BAND_PX)
    runs = []
    for x in np.nonzero(ink[top:floor + 1].any(0))[0]:
        col = ink[:, x]
        bottom = top + int(np.nonzero(col[top:floor + 1])[0].max())
        y = bottom
        while y >= 0 and col[y]:
            y -= 1
        runs.append((int(x), y + 1, bottom))
    return runs


def floor_shadow(rgb: np.ndarray, near: np.ndarray, fg: np.ndarray, white: float) -> np.ndarray:
    """La línea de sombra y el blanco que encierra entre las piernas: lo que hay que borrar.

    Afuera de las botas, la línea es una racha corta de tinta con fondo arriba. Entre las piernas
    tiene arriba un hueco blanco, igual que una bota blanca (ahí la línea es la suela), así que el
    hueco sólo cuenta como fondo si toca el piso, cae en el centro de las botas y es del color
    del fondo; una bota blanca es más oscura o más cálida.
    """
    ink = fg & ~near
    floor = int(np.nonzero(fg.any(1))[0].max())
    runs = [r for r in _bottom_runs(ink, floor) if r[2] - r[1] < SHADOW_MAX_PX]
    drop = np.zeros_like(fg)
    for x, y0, y1 in runs:
        if y0 == 0 or not fg[y0 - 1, x]:
            drop[y0:y1 + 1, x] = True

    xs = np.nonzero(fg[floor - SHADOW_BAND_PX:floor + 1].any(0) & ~drop.any(0))[0]
    if not len(xs):
        return drop
    center = (xs.min() + xs.max()) // 2
    count, labels, stats, _ = cv2.connectedComponentsWithStats((near & fg).astype(np.uint8), connectivity=4)
    for k in range(1, count):
        x, y, w, h, _ = stats[k]
        if not (x <= center < x + w and y + h >= floor - SHADOW_BAND_PX):
            continue
        hole = labels == k
        color = np.median(rgb[hole], axis=0)
        if np.abs(color - white).max() <= BG_TOL and np.ptp(color) <= BG_TOL / 2:
            drop |= hole
            for rx, y0, y1 in runs:
                if y0 > 0 and hole[y0 - 1, rx]:
                    drop[y0:y1 + 1, rx] = True
    return drop


def clean(img: np.ndarray) -> tuple[np.ndarray, dict]:
    """Concept RGB sobre blanco a RGBA, sin fondo, sin sombra de piso y sin basura suelta."""
    rgb = img[..., :3].astype(np.float32)
    white = float(np.median(np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])))
    near = (rgb.min(-1) >= NEAR_WHITE) & (np.ptp(rgb, -1) <= NEUTRAL)
    fg = _largest(~_from_border(near))
    shadow = floor_shadow(rgb, near, fg, white)
    fg = _largest(fg & ~shadow)

    dist = cv2.distanceTransform(fg.astype(np.uint8), cv2.DIST_L2, 3)
    edge = fg & (dist <= EDGE_PX)
    a_edge = np.clip((white - rgb.mean(-1)) / (white - INK), 0.0, 1.0)
    alpha = np.where(edge, a_edge, fg.astype(np.float32))
    a = np.maximum(alpha, 0.15)[..., None]
    unmixed = np.clip((rgb - (1 - a) * white) / a, 0, 255)
    out = np.dstack([np.where(edge[..., None], unmixed, rgb), alpha * 255])
    out[alpha == 0] = 0
    return (out + 0.5).astype(np.uint8), {"background": round(white), "shadow_px": int(shadow.sum())}


def _feet(alpha: np.ndarray) -> tuple[int, float, int]:
    """Fila del piso, centro y ancho de las botas en las FEET_PX filas de abajo."""
    solid = alpha > 127
    floor = int(np.nonzero(solid.any(1))[0].max())
    xs = np.nonzero(solid[floor - FEET_PX:floor + 1].any(0))[0]
    return floor, (xs.min() + xs.max() + 1) / 2, int(xs.max() + 1 - xs.min())


def roster(srcs: list[Path], out_dir: Path, size: tuple[int, int] = (512, 512), feet: float = 0.94,
           magenta: bool = False, magenta_height: float = 0.48) -> list[dict]:
    """Limpia cada concept y lo pone en un canvas común: pies en la fila `feet`, botas centradas.

    Con `magenta`, además arma la pose 16:9 de cada uno en out_dir/magenta/ con una sola escala
    para todo el plantel: el personaje más alto ocupa `magenta_height` del alto.
    """
    cells, infos = [], []
    for src in srcs:
        rgba, info = clean(imgio.load(src))
        floor, cx, width = _feet(rgba[..., 3])
        ys, xs = np.nonzero(rgba[..., 3])
        left = size[0] // 2 - round(cx)
        top = round(size[1] * feet) - 1 - floor
        x0, y0, x1, y1 = xs.min() + left, ys.min() + top, xs.max() + 1 + left, ys.max() + 1 + top
        if x0 < 0 or y0 < 0 or x1 > size[0] or y1 > size[1]:
            raise ValueError(f"{src.name} no entra en {size[0]}×{size[1]} con los pies en {feet}: "
                             f"ocupa x {x0}..{x1}, y {y0}..{y1}; agrandá --size")
        cell = np.zeros((size[1], size[0], 4), np.uint8)
        h, w = rgba.shape[:2]
        sx0, sy0 = max(0, -left), max(0, -top)
        sx1, sy1 = min(w, size[0] - left), min(h, size[1] - top)
        cell[sy0 + top:sy1 + top, sx0 + left:sx1 + left] = rgba[sy0:sy1, sx0:sx1]
        cells.append(cell)
        infos.append({"name": src.stem, **info, "feet_width": width, "height": int(y1 - y0),
                      "bbox": [int(x0), int(y0), int(x1), int(y1)]})

    out_dir.mkdir(parents=True, exist_ok=True)
    for cell, info in zip(cells, infos):
        info["out"] = out_dir / f"{info['name']}.png"
        imgio.save(info["out"], cell, compression=9)
    if magenta:
        tallest = max(i["height"] for i in infos)
        for info in infos:
            info["magenta"] = out_dir / "magenta" / f"{info['name']}.png"
            pose.pad(info["out"], info["magenta"], height=magenta_height * info["height"] / tallest,
                     shadow_from=1.0)
    return infos
