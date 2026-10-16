"""Paso 5a (opcional): limpiar el clip antes de todo lo demás.

Los clips de Davinci vuelven con fondos magenta apagados, a veces en degradé y con sombra de piso,
y con efectos que el prompt no pidió: rayos y chispas, humo, utilería dibujada (una barra, una
cornisa). Nada de eso se keyea bien, así que se limpia frame por frame, a resolución de video:

  1. El fondo se modela por fila, así aguanta degradés: la mediana de la franja izquierda o la de la
     derecha, la que más se parezca al fondo típico del frame (un rayo que llega a un borde ensucia
     sólo ese lado). Las filas donde ninguna se parece (una barra o un rayo que cruzan todo el
     cuadro) se interpolan entre las filas buenas.
  2. Es fondo lo que tiene el croma del fondo de su fila con una luminancia de 0,15 a 1,2 veces la
     del fondo: entra la sombra de piso, que es del mismo tono pero más oscura.
  3. Queda sólo el componente conexo más grande (el personaje) sin contar el cian de los efectos,
     más el cian que lo toca (la punta de la pistola). Todo lo demás se pinta de un color único,
     la mediana de los bordes en todo el clip.
  4. `cut_muzzle`: borra todo lo que queda delante de la boca del arma. La boca es un cuantil bajo
     del borde derecho del personaje en los frames con el brazo extendido: los frames con un rayo
     pegado dan bordes más lejanos. Como ese corte se lleva los rayos, antes se recupera el cian a
     menos de 20 px del cuerpo: en los frames de disparo el arma brilla cian y sin esto queda con
     agujeros. `cut_left` borra además los rayos que cruzan por detrás.
  5. `prop_rows`: utilería dibujada que cruza el cuadro (filas con personaje en más del 35% del
     ancho, como la barra de la que se cuelga, que arranca en la mano). Se borra desde cada borde mientras sea gris oscuro o
     negro, frenando en el casco o el guante; lo que queda en esas filas fuera de las columnas del
     cuerpo también es barra, y los restos finos lejos de las partes gruesas del cuerpo se van.
Las constantes están calibradas con los clips del ranger a 1280×720; las distancias en px se
escalan con el alto del clip. Supone un personaje que mira a la derecha.

El clip limpio se guarda en H.264 sin pérdida (yuv444p, BT.709) en work/00_clean/, con un JSON al
lado. Se reusa mientras no cambien el clip, los parámetros ni CLEAN_VERSION.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

import cv2
import numpy as np

from . import imgio
from .config import Clean

CLEAN_VERSION = 5  # subirla cuando cambie el resultado, para invalidar los clips cacheados
REF_HEIGHT = 720  # alto de video con el que se calibraron las distancias en px

STRIP = 24  # columnas de cada borde lateral donde se mide el fondo
ROW_SMOOTH = 15  # suavizado vertical del fondo por fila
ROW_FAR = 70  # fila cuyas dos franjas difieren del fondo típico en más que esto (suma RGB): se interpola
CHROMA_TOL = 0.11  # diferencia de croma (suma de |r,g,b normalizados|) contra el fondo de la fila
LUM_RANGE = (0.15, 1.2)  # luminancia relativa al fondo de la fila que sigue siendo fondo (sombra incluida)
FX_NEAR = 7  # el cian a menos de esto del personaje es suyo
FX_GUN = 41  # con cut_muzzle, el cian a menos de la mitad de esto del cuerpo vuelve (el arma que brilla)
MUZZLE_EXTENDED = 15  # brazo extendido: borde derecho más allá del de los primeros frames en esto
MUZZLE_QUANTILE = 30
MUZZLE_GAP = 6  # aire entre la boca medida y el corte
LEFT_GAP = 25  # aire entre el borde izquierdo típico y el corte de cut_left
PROP_ROW = 0.35  # fracción del ancho con personaje a partir de la cual una fila es utilería. En r07, el
# cuerpo colgado llega al 26% y la barra, desde la mano hasta un borde, ocupa del 43% al 64%
PROP_GRAY = (30, 130)  # utilería: |R-G| y |G-B| menores que el primero, luminancia menor que el segundo
PROP_PAD = (6, 9)  # filas de más arriba y abajo de la utilería (el antialias)
PROP_BELOW = (4, 120)  # filas debajo de la utilería donde se buscan las columnas del cuerpo
PROP_BODY_PAD = 9  # ancho del ensanche de esas columnas
PROP_ZONE = (4, 2)  # filas de más arriba y abajo donde se borra fuera de las columnas del cuerpo
THIN_OPEN, THIN_NEAR = 5, 9  # restos finos: no sobreviven a una apertura de 5×5 y quedan lejos de lo grueso


def _px(v: float, s: float) -> int:
    return max(1, round(v * s))


def _odd(v: float, s: float) -> int:
    return _px(v, s) | 1


def bg_rows(a: np.ndarray, strip: int = STRIP, smooth: int = ROW_SMOOTH) -> np.ndarray:
    """Color del fondo por fila (H×3, float): la mediana de la franja lateral que más se parece al fondo
    típico del frame, suavizada en vertical. Las filas donde las dos se alejan se interpolan."""
    left = np.median(a[:, :strip].astype(np.float32), axis=1)
    right = np.median(a[:, -strip:].astype(np.float32), axis=1)
    glob = np.median(np.concatenate([left, right]), axis=0)
    dl, dr = np.abs(left - glob).sum(1), np.abs(right - glob).sum(1)
    rows = np.where((dl <= dr)[:, None], left, right)
    ok = np.minimum(dl, dr) < ROW_FAR
    if ok.sum() >= 2 and not ok.all():
        y = np.arange(len(rows))
        rows = np.stack([np.interp(y, y[ok], rows[ok, c]) for c in range(3)], 1)
    ker = np.ones(smooth) / smooth
    pad = smooth // 2
    return np.stack([np.convolve(np.pad(rows[:, c], pad, mode="edge"), ker, "valid") for c in range(3)], 1)


def bg_mask(a: np.ndarray, rows: np.ndarray) -> np.ndarray:
    """Fondo: croma del fondo de su fila y luminancia en LUM_RANGE (la sombra de piso entra)."""
    f = a.astype(np.float32)
    c = f / (f.sum(2, keepdims=True) + 1e-3)
    cb = rows / (rows.sum(1, keepdims=True) + 1e-3)
    lum = f.mean(2) / (rows.mean(1)[:, None] + 1e-3)
    return (np.abs(c - cb[:, None, :]).sum(2) < CHROMA_TOL) & (lum > LUM_RANGE[0]) & (lum < LUM_RANGE[1])


def fx_mask(a: np.ndarray) -> np.ndarray:
    """Rayos y chispas cian (y lo azulado brillante del halo)."""
    f = a.astype(np.int16)
    R, G, B = f[..., 0], f[..., 1], f[..., 2]
    return ((G > 150) & (B > 170) & (R < 190)) | ((B > R + 25) & (G > R + 10) & (f.mean(2) > 170))


def _cut_props(fg: np.ndarray, fx: np.ndarray, a: np.ndarray, s: float) -> None:
    """Borra de fg la utilería que cruza el cuadro (in place)."""
    H, W = fg.shape
    rows = np.where((fg & ~fx).sum(1) > PROP_ROW * W)[0]
    if not len(rows):
        return
    f = a.astype(np.int16)
    y0, y1 = max(0, rows.min() - _px(PROP_PAD[0], s)), min(H, rows.max() + _px(PROP_PAD[1], s))
    sub = f[y0:y1]
    barlike = ((np.abs(sub[..., 0] - sub[..., 1]) < PROP_GRAY[0]) & (np.abs(sub[..., 1] - sub[..., 2]) < PROP_GRAY[0])
               & (sub.mean(2) < PROP_GRAY[1]))
    barlike |= ~fg[y0:y1]
    from_left = np.cumprod(barlike, axis=1).astype(bool)
    from_right = np.cumprod(barlike[:, ::-1], axis=1)[:, ::-1].astype(bool)
    fg[y0:y1] &= ~(from_left | from_right)
    # lo que quede en esas filas fuera de las columnas del cuerpo (lo que hay debajo de la barra, más
    # el guante) también es barra: bordes de 1-3 px en tonos que no son grises
    below = fg[min(H, y1 + _px(PROP_BELOW[0], s)):min(H, y1 + _px(PROP_BELOW[1], s))].astype(np.uint8)
    nb, lb, sb, _ = cv2.connectedComponentsWithStats(below, connectivity=8)
    cols = (lb == 1 + int(np.argmax(sb[1:, cv2.CC_STAT_AREA]))).any(0) if nb > 1 else below.any(0)
    red = ((f[y0:y1, :, 0] > 150) & (f[y0:y1, :, 1] < 100)).any(0)
    body = cv2.dilate((cols | red).astype(np.uint8)[None, :], np.ones((1, _odd(PROP_BODY_PAD, s)), np.uint8))[0]
    z0, z1 = max(0, y0 - _px(PROP_ZONE[0], s)), min(H, y1 + _px(PROP_ZONE[1], s))
    fg[z0:z1, ~body.astype(bool)] = False


def keep_mask(a: np.ndarray, params: Clean) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    """Lo que queda del frame (el personaje), lo mismo sin el cian (para medir sus bordes), el cian
    cercano al cuerpo que vuelve con cut_muzzle y cuántos px no eran fondo."""
    s = a.shape[0] / REF_HEIGHT
    fg0 = ~bg_mask(a, bg_rows(a, _px(STRIP, s), _odd(ROW_SMOOTH, s)))
    fx = fx_mask(a)
    fg = fg0.copy()
    if params.prop_rows:
        _cut_props(fg, fx, a, s)
    core = (fg & ~fx).astype(np.uint8)
    cnt, lab, st, _ = cv2.connectedComponentsWithStats(core, connectivity=8)
    if cnt > 1:
        main = lab == (1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])))
        k = _odd(FX_NEAR, s)
        near = cv2.dilate(main.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
        keep = main | (fx & fg & near)
        k = _odd(FX_GUN, s)
        gun = fx & fg & cv2.dilate(main.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    else:
        keep = fg
        gun = np.zeros_like(fg)
    if params.prop_rows:
        k8 = keep.astype(np.uint8)
        ko, kn = _odd(THIN_OPEN, s), _odd(THIN_NEAR, s)
        thick = cv2.morphologyEx(k8, cv2.MORPH_OPEN, np.ones((ko, ko), np.uint8))
        keep &= cv2.dilate(thick, np.ones((kn, kn), np.uint8)).astype(bool)
    return keep, keep & ~fx, gun, int(fg0.sum())


def muzzle_limit(rights: list[int], s: float = 1.0, steady: bool = False) -> int | None:
    """Columna de la boca del arma: cuantil bajo del borde derecho con el brazo extendido.

    El brazo está extendido donde el borde derecho pasa por más de MUZZLE_EXTENDED px al de los
    primeros 5 frames (la pose de arranque)."""
    r = np.array(rights)
    ext = r[r > np.median(r[:5]) + _px(MUZZLE_EXTENDED, s)]
    if len(ext) and not steady:
        return int(np.percentile(ext, MUZZLE_QUANTILE)) + _px(MUZZLE_GAP, s)
    # el brazo no se mueve (un idle con el arma siempre al frente): la boca es el borde derecho típico, y lo que
    # pase de ahí es un destello
    return int(np.median(r)) + _px(MUZZLE_GAP, s) if len(r) else None


def run(frames: np.ndarray, params: Clean) -> tuple[list[np.ndarray], dict]:
    """frames: N×H×W×3 RGB. Devuelve los frames limpios y lo medido."""
    H, W = frames.shape[1:3]
    s = H / REF_HEIGHT
    strip = _px(STRIP, s)
    bg = np.median(np.concatenate([frames[:, :, :strip].reshape(-1, 3), frames[:, :, -strip:].reshape(-1, 3)]),
                   axis=0).astype(np.uint8)
    keeps, guns, rights, lefts, removed = [], [], [], [], 0
    for a in frames:
        keep, body, gun, n_fg = keep_mask(a, params)
        removed += n_fg  # menos lo que queda, al final: lo que queda es siempre parte de fg
        keeps.append(keep)
        guns.append(gun if params.cut_muzzle else None)
        cols = np.where(body.any(0))[0]
        rights.append(int(cols.max()) if len(cols) else -1)
        lefts.append(int(cols.min()) if len(cols) else W)

    limit = muzzle_limit(rights, s, params.muzzle_steady) if params.cut_muzzle else None
    left = int(np.percentile(lefts, 50)) - _px(LEFT_GAP, s) if params.cut_left else None
    left = left if left is None or left > 0 else None  # el cuerpo ya está pegado al borde
    out = []
    for a, keep, gun in zip(frames, keeps, guns):
        if limit is not None:
            keep |= gun
            keep[:, limit + 1:] = False
        if left is not None:
            keep[:, :left] = False
        removed -= int(keep.sum())
        a = a.copy()
        a[~keep] = bg
        out.append(a)
    return out, {"bg": "#" + "".join(f"{c:02X}" for c in bg), "muzzle_x": limit, "cut_left_x": left,
                 "removed_px": removed}


def _key(clip: Path, params: Clean, matrix: str | None) -> str:
    h = hashlib.sha256(clip.read_bytes())
    h.update(json.dumps({"params": asdict(params), "matrix": matrix, "version": CLEAN_VERSION},
                        sort_keys=True).encode())
    return h.hexdigest()


def ensure(clip: Path, params: Clean, out_dir: Path, label: str, matrix: str | None = None) -> dict:
    """Clip limpio en out_dir/<label>-<hash>.mp4: lo arma si no está o si cambió algo."""
    key = _key(clip, params, matrix)
    out = out_dir / f"{label}-{key[:8]}.mp4"
    meta = out.with_suffix(".json")
    if out.exists() and meta.exists():
        info = imgio.read_json(meta)
        if info.get("key") == key:
            return {**info, "path": out, "cached": True}
    info = clean_clip(clip, out, params, matrix)
    info = {"key": key, "source": str(clip), "params": asdict(params), "color_matrix": matrix, **info}
    imgio.write_json(meta, info)
    return {**info, "path": out, "cached": False}


def clean_clip(clip: Path, out: Path, params: Clean, matrix: str | None = None) -> dict:
    """Limpia un clip entero y lo escribe sin pérdida. matrix pisa la matriz de color del video."""
    vinfo = imgio.probe(clip)
    frames, stats = run(imgio.read_video(clip, vinfo, matrix), params)
    imgio.encode_rgb_video(frames, out, vinfo["fps"], crf=0, pix_fmt="yuv444p")
    return {"frames": len(frames), **stats}
