"""Paso 6: encontrar el loop dentro del clip (ciclos) o recortar la acción (oneshots).

El loop se busca, no se le pide al modelo. Para cada inicio s y largo L se mide la costura
entre la ventana de tres frames alrededor de s y la de s+L: comparar ventanas y no frames
sueltos evita confundir dos poses de passing que se parecen pero van en sentidos opuestos.
La costura se normaliza por el movimiento medio dentro del loop, para no premiar tramos
quietos. L tiene que ser múltiplo de K (el factor de decimación), así el salto del último
frame al primero dura lo mismo que los demás.
"""

from __future__ import annotations

import cv2
import numpy as np

from .analysis import ClipAnalysis

DESC_WIDTH = 40


def _descriptors(an: ClipAnalysis) -> np.ndarray:
    """Recorte del personaje centrado en su centroide: invariante a la deriva de cámara."""
    f = an.factor
    w = np.nanmax(an.bbox[:, 2] - an.bbox[:, 0]) / f * 1.15
    h = np.nanmax(an.bbox[:, 3] - an.bbox[:, 1]) / f * 1.15
    bw, bh = max(4, int(w)), max(4, int(h))
    dh = max(4, round(DESC_WIDTH * bh / bw))
    out = []
    for g, c in zip(an.gray, an.centroid):
        cx, cy = (c / f) if not np.isnan(c[0]) else (g.shape[1] / 2, g.shape[0] / 2)
        crop = cv2.getRectSubPix(g, (bw, bh), (float(cx), float(cy)))
        out.append(cv2.resize(crop, (DESC_WIDTH, dh), interpolation=cv2.INTER_AREA).ravel())
    return np.stack(out) * 255


def _distance_matrix(desc: np.ndarray) -> np.ndarray:
    n = len(desc)
    D = np.zeros((n, n), np.float32)
    for i in range(n):
        D[i] = np.abs(desc - desc[i]).mean(axis=1)
    return D


def find_loop(an: ClipAnalysis, fps: float, K: int, loop_seconds: tuple[float, float],
              skip_seconds: float) -> dict:
    D = _distance_matrix(_descriptors(an))
    n = an.n
    step = np.array([D[i, i + 1] for i in range(n - 1)])
    lmin = max(K * 2, int(np.ceil(loop_seconds[0] * fps / K)) * K)
    lmax = int(loop_seconds[1] * fps // K) * K
    s_min = max(1, int(round(skip_seconds * fps)))

    cands = []
    for L in range(lmin, lmax + 1, K):
        for s in range(s_min, n - L - 1):
            seam = (D[s - 1, s + L - 1] + D[s, s + L] + D[s + 1, s + L + 1]) / 3
            motion = step[s:s + L].mean()
            cands.append((float(seam / (motion + 1e-6)), s, L, float(seam), float(motion)))
    if not cands:
        raise ValueError(f"el clip ({n} frames) es corto para buscar loops de {lmin}-{lmax} frames; "
                         "bajá loop_seconds o pasá loop_start/loop_length a mano")
    cands.sort()
    best = cands[0][0]
    # Entre los casi empatados (15%), el más corto: menos frames, menos memoria.
    near = [c for c in cands if c[0] <= best * 1.15 + 1e-6]
    chosen = min(near, key=lambda c: (c[2], c[0]))

    top, seen = [], set()
    for c in cands:
        if (c[1], c[2]) not in seen:
            seen.add((c[1], c[2]))
            top.append({"start": c[1], "length": c[2], "score": round(c[0], 3)})
        if len(top) == 5:
            break
    score, s, L, seam, motion = chosen
    return {
        "start": s, "length": L, "score": round(score, 3), "seam": round(seam, 2),
        "motion": round(motion, 2), "seconds": round(L / fps, 3), "candidates": top,
        "quality": "buena" if score <= 0.6 else "aceptable" if score <= 1.0 else "costura visible",
    }


def periodic_drift(an: ClipAnalysis, L: int, skip: int) -> tuple[float, float]:
    """Deriva de cámara en px por frame nativo: compara cada frame con el de la misma fase un
    ciclo después (i contra i+L) en todo el clip. El bob y el balanceo se cancelan solos."""
    i = np.arange(skip, an.n - L)
    if not len(i):
        i = np.arange(0, an.n - L)
    if not len(i):
        return 0.0, 0.0
    cx, gy = an.centroid[:, 0], an.bbox[:, 3]
    return float(np.nanmean((cx[i + L] - cx[i]) / L)), float(np.nanmean((gy[i + L] - gy[i]) / L))


def trim_oneshot(an: ClipAnalysis, trim: tuple[int, int] | None, static_tail: bool, reverse: bool = False) -> dict:
    """Con reverse, el tramo se reproduce al revés: la cola quieta es el principio del tramo."""
    start, end = trim if trim else (0, an.n)
    end = min(end, an.n)
    cut = 0
    if static_tail and end - start > 2:
        motion = an.diff_char[start:end - 1]
        if reverse:
            motion = motion[::-1]
        thr = 0.15 * float(np.median(motion))
        last_moving = max((i for i, d in enumerate(motion) if d >= thr), default=len(motion) - 1)
        cut = end - start - (last_moving + 2)  # se queda el frame donde termina el movimiento
        if reverse:
            start += cut
        else:
            end -= cut
    return {"start": start, "length": end - start, "static_tail_trimmed": cut}
