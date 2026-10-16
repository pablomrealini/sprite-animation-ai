"""Paso 9: bajar al fps del juego por un factor entero K (24->12 es K=2, 24->8 es K=3).

Nunca mezcla frames: sólo elige. Las relaciones no enteras tartamudean en ciclos cortos.
En oneshots puede elegir el frame más nítido de cada grupo de K, porque el video de IA mete
motion blur en los golpes rápidos. Los holds se expresan como duración por frame, no
duplicando frames.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import cv2
import numpy as np

from . import imgio


def factor(native_fps: float, game_fps: int) -> tuple[int, float, str | None]:
    raw = native_fps / game_fps
    K = max(1, round(raw))
    warn = None
    if abs(raw - K) > 0.02:
        warn = (f"{native_fps:g} fps -> {game_fps} fps no es entero (K={raw:.2f}); "
                f"uso K={K}, o sea {native_fps / K:.2f} fps efectivos")
    return K, native_fps / K, warn


def _sharpness(path: Path) -> float:
    gray = cv2.cvtColor(imgio.load(path)[..., :3], cv2.COLOR_RGB2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_32F).var())


def pick(raw_frames: list[Path], indices: list[int], K: int, mode: str, kind: str) -> list[int]:
    if mode == "sharpest" and K > 1:
        picked = []
        for g in range(0, len(indices), K):
            group = indices[g:g + K]
            picked.append(max(group, key=lambda i: _sharpness(raw_frames[i])))
    else:
        picked = indices[::K]
    if kind == "oneshot" and picked[-1] != indices[-1]:
        picked.append(indices[-1])  # la pose final (guardia o cuerpo en el piso) tiene que estar
    return picked


def run(raw_dir: Path, out_dir: Path, indices: list[int], K: int, eff_fps: float, mode: str,
        kind: str, holds: dict[int, float]) -> dict:
    raw = imgio.frames(raw_dir)
    picked = pick(raw, indices, K, mode, kind)
    imgio.reset_dir(out_dir)
    for j, i in enumerate(picked):
        shutil.copyfile(raw[i], out_dir / imgio.frame_name(j))
    base = 1000.0 / eff_fps
    durations = [round(base * holds.get(j, 1.0), 1) for j in range(len(picked))]
    return {"K": K, "effective_fps": round(eff_fps, 3), "native_indices": picked, "durations_ms": durations}
