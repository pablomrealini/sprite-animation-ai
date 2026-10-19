"""Paso 7: sacar el fondo con un chroma key determinístico.

Verde o magenta usan diferencia de color; un fondo plano no cromático (blanco, gris, crema)
usa distancia ΔE en Lab, que anda bien si el personaje tiene contorno. Con un fondo plano, el key le gana a cualquier matting por IA: aplica la misma regla en
todos los frames, así que no parpadea. Por frame:
  1. color de fondo real (mediana del borde) o el que fija la config;
  2. alpha_raw por diferencia de color (ver chroma.py) y rampa entre las tolerancias;
  3. islas chicas fuera (ruido de compresión, motas);
  4. modo "connected" (por defecto con fondos no cromáticos): los huecos chicos del color de
     fondo que no tocan el borde se conservan (ojos, brillos); con `hole_inpaint`, pintados del
     color de alrededor (las motas de fondo adentro del personaje);
  4b. `floor_streak`: la sombra del piso que el key no saca queda como una raya fina y oscura
     pegada a los pies; se borra lo fino (más angosto que FLOOR_STREAK_PX a 720p) y oscuro de la
     franja de abajo del personaje (FLOOR_STREAK_BAND de su alto). Las botas son gruesas: quedan;
  5. unmix del borde: F = (C - (1-α)K) / α, que saca el halo verde en vez de taparlo;
  5b. `edge_unmix`: con el key por distancia, el borde con algo de fondo mezclado (10–30 %) queda
     opaco y sin despill: un contorno rosa de 1–2 px que se ve sobre fondos oscuros. En una banda
     de EDGE_UNMIX_PX (a 720p) desde el borde, cada px se toma como mezcla del fondo y del color de
     adentro más cercano: α = cuánto de ese color tiene, y el color, desmezclado. Los px que no
     están sobre esa recta (brillos, detalles de otro color) quedan como estaban;
  6. despill en una banda angosta alrededor del borde, por si quedó contaminación;
  7. RGB en 0 donde α = 0, para que ningún resize posterior arrastre el verde.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from . import chroma, imgio
from .config import Character


FLOOR_STREAK_PX = 9      # más angosto que esto (a 720p, se escala con el alto del video) es raya, no pie
FLOOR_STREAK_BAND = 0.1  # la franja de abajo del personaje donde se busca, en fracción de su alto
FLOOR_STREAK_LUM = 0.35  # y más oscuro que esto (el canal más alto, de 0 a 1), o
FLOOR_STREAK_BLUE = 0.2  # con más azul que esto en la mezcla (b / (r + g + b)): la sombra sobre magenta o gris; el rojo
                         # de una bota tiene ~0,12, así que el borde fino de una suela roja queda


def floor_streak(img: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    """La máscara de la raya de sombra junto a los pies: lo que la apertura morfológica saca (lo fino), oscuro o del tono
    de una sombra (magenta apagado o gris, no rojo), y en la franja de abajo del personaje."""
    rows = np.nonzero((alpha > 0.5).any(1))[0]
    if not len(rows):
        return np.zeros(alpha.shape, bool)
    y0, y1 = rows[0], rows[-1]
    k = max(3, round(FLOOR_STREAK_PX * alpha.shape[0] / 720)) | 1
    m = (alpha > 0.05).astype(np.uint8)
    opened = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    blue = img[..., 2] / np.maximum(img.sum(2), 1e-6)
    kill = (m == 1) & (opened == 0) & ((img.max(2) < FLOOR_STREAK_LUM) | (blue > FLOOR_STREAK_BLUE))
    kill[: y1 - max(4, int(FLOOR_STREAK_BAND * (y1 - y0)))] = False
    return kill


EDGE_UNMIX_PX = 2        # ancho de la banda del borde, a 720p (se escala con el alto del video)
EDGE_UNMIX_MIN = 0.15    # el color de adentro tiene que estar al menos así de lejos del fondo (RGB 0..1), o no se toca
EDGE_UNMIX_RESIDUAL = 0.12  # un px opaco es mezcla si está a menos de esto de la recta fondo–adentro (RGB 0..1)
EDGE_HALO_PX = 2         # el anillo de afuera de lo opaco donde se busca el halo, a 720p
EDGE_HALO_AB = 20        # halo: su croma (a*, b* de Lab) va del de adentro hacia el del fondo, a menos de esto de esa recta
EDGE_HALO_MIN_AB = 20    # y el croma de adentro tiene que distinguirse del del fondo al menos esto (si no, no se toca)


def edge_unmix(img: np.ndarray, alpha: np.ndarray, key: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """El borde contaminado de fondo: (máscara de los px corregidos, su alfa, su color). Ver 5b arriba.

    F es el color de adentro más cercano (lo opaco, achicado EDGE_UNMIX_PX) y K el fondo. Dos casos:
      - mezcla: C = t·F + (1 - t)·K, con t la proyección de C - K sobre F - K, si C cae cerca de esa recta: alfa t y
        el color desmezclado (o F, si t < 0,5: desmezclar poco de algo oscuro amplifica el ruido y da verde);
      - halo: el render deja por fuera del contorno un anillo más claro, del tono del fondo (lila sobre el arma gris,
        rosa sobre el rojo), que el key deja opaco. En el anillo de afuera, si el croma del px va de F hacia K (y no
        hacia otro lado: un detalle rojo sobre el arma gris queda), el px pasa a F con alfa 1 - s (s: cuánto se
        corrió hacia K).
    Lo que no es ni una cosa ni la otra (un detalle de otro color en el borde, como la mira roja del arma) queda."""
    h = alpha.shape[0] / 720
    px = max(1, round(EDGE_UNMIX_PX * h))
    solid = (alpha >= 1).astype(np.uint8)
    k = 2 * px + 1
    inner = cv2.erode(solid, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    none = np.zeros(alpha.shape, bool)
    if not inner.any():
        return none, alpha[none], img[none]
    dist, labels = cv2.distanceTransformWithLabels(1 - inner, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    seeds = np.flatnonzero(inner.ravel())                  # los labels van en el orden de barrido de los px de adentro
    out_d = cv2.distanceTransform(solid, cv2.DIST_L2, 5)   # en lo opaco: distancia al borde
    semi = (alpha > 0) & (alpha < 1) & (dist <= 2 * px + 2)
    opaque = (solid == 1) & (inner == 0) & (dist <= px + 1.5)   # lo fino sin "adentro" cerca (dedos, la punta) queda
    ys, xs = np.nonzero(semi | opaque)
    if not len(ys):
        return none, alpha[none], img[none]
    f = img.reshape(-1, 3)[seeds[labels[ys, xs] - 1]]
    c = img[ys, xs]
    a = alpha[ys, xs].copy()
    rgb = c.copy()
    is_semi = semi[ys, xs]

    d = f - key
    dd = (d * d).sum(1)
    t = np.clip(((c - key) * d).sum(1) / np.maximum(dd, 1e-6), 0.0, 1.0)
    resid = np.linalg.norm(c - key - t[:, None] * d, axis=1)
    mix = (dd > EDGE_UNMIX_MIN ** 2) & (resid < EDGE_UNMIX_RESIDUAL)
    a[mix] = np.minimum(a[mix], t[mix])
    unmixed = np.clip(key + (c - key) / np.maximum(t, 0.15)[:, None], 0.0, 1.0)
    rgb[mix] = np.where((t[mix] < 0.5)[:, None], f[mix], unmixed[mix])

    ring = ~mix & (is_semi | (out_d[ys, xs] <= max(1.0, EDGE_HALO_PX * h)))
    lab = lambda x: cv2.cvtColor(np.ascontiguousarray(x.reshape(-1, 1, 3), np.float32), cv2.COLOR_RGB2LAB)[:, 0, 1:]  # noqa: E731
    ab_c, ab_f, ab_k = lab(c), lab(f), lab(key[None])[0]
    v = ab_k - ab_f
    vv = (v * v).sum(1)
    sh = np.clip(((ab_c - ab_f) * v).sum(1) / np.maximum(vv, 1e-6), 0.0, 1.0)
    r = np.linalg.norm(ab_c - ab_f - sh[:, None] * v, axis=1)
    halo = ring & (vv > EDGE_HALO_MIN_AB ** 2) & (r < EDGE_HALO_AB) & (sh > 0.1)
    a[halo] = np.minimum(a[halo], 1.0 - sh[halo])
    rgb[halo] = f[halo]

    ok = mix | halo
    mask = np.zeros(alpha.shape, bool)
    mask[ys[ok], xs[ok]] = True
    return mask, a[ok], rgb[ok]


HOLE_WHITE_MAX_FRAC = 0.01  # hasta dónde se rellena un hueco rodeado de blanco (el 1% de siempre)
HOLE_WHITE_RING = 0.6       # rodeado de blanco: esa fracción de su contorno es blanca (saturación < 0,25, valor > 0,6)


def _white_ring(img: np.ndarray, labels: np.ndarray, st: np.ndarray, i: int) -> float:
    """La fracción blanca del contorno (2 px alrededor) del hueco `i`."""
    x, y, w, h = st[0], st[1], st[2], st[3]
    x0, y0, x1, y1 = max(0, x - 3), max(0, y - 3), min(img.shape[1], x + w + 3), min(img.shape[0], y + h + 3)
    m = (labels[y0:y1, x0:x1] == i).astype(np.uint8)
    ring = (cv2.dilate(m, np.ones((5, 5), np.uint8)) > 0) & (m == 0)
    c = img[y0:y1, x0:x1][ring]
    if not len(c):
        return 0.0
    mx, mn = c.max(1), c.min(1)
    white = (mx > 0.6) & ((mx - mn) / np.maximum(mx, 1e-6) < 0.25)
    return float(white.mean())


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
        # quedan opacos. Los grandes (brazo contra el torso) son fondo de verdad. Con hole_max_frac bajo (los bolsillos
        # entre el brazo y el pecho son del tamaño de una mota en el casco), los rodeados de blanco (la mota) se
        # rellenan igual hasta HOLE_WHITE_MAX_FRAC.
        bg = (alpha == 0).astype(np.uint8)
        count, labels, stats, _ = cv2.connectedComponentsWithStats(bg, connectivity=4)
        border_labels = np.unique(np.concatenate([labels[0], labels[-1], labels[:, 0], labels[:, -1]]))
        n_solid = max(1, int(solid.sum()))
        area = stats[:, cv2.CC_STAT_AREA]
        small = area < ch.hole_max_frac * n_solid
        fill = np.zeros(count, bool)
        fill[1:] = small[1:]
        fill[border_labels] = False
        if ch.hole_max_frac < HOLE_WHITE_MAX_FRAC:
            for i in np.nonzero((area < HOLE_WHITE_MAX_FRAC * n_solid) & ~fill)[0]:
                if i == 0 or i in border_labels:
                    continue
                if _white_ring(img, labels, stats[i], i) > HOLE_WHITE_RING:
                    fill[i] = True
        interior = fill[labels]
        alpha[interior] = 1.0
        a_true[interior] = 1.0
        if getattr(ch, "hole_inpaint", False) and interior.any():
            # el color de alrededor (antes del unmix y del borde: si no, el borde desmezcla el magenta y lo vuelve a abrir)
            u8 = (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)
            painted = cv2.inpaint(u8, interior.astype(np.uint8), 3, cv2.INPAINT_TELEA).astype(np.float32) / 255.0
            img = img.copy()
            img[interior] = painted[interior]

    if getattr(ch, "floor_streak", False):   # bgpost arma la config a mano, sin este campo
        kill = floor_streak(img, alpha)
        alpha[kill] = 0.0
        a_true[kill] = 0.0

    edge = (alpha > 0) & (alpha < 1)
    a = np.maximum(a_true, 0.15)[..., None]
    unmixed = np.clip((img - (1 - a) * key) / a, 0.0, 1.0)
    rgb = np.where(edge[..., None], unmixed, img)

    if getattr(ch, "edge_unmix", False):
        m, a_m, rgb_m = edge_unmix(img, alpha, key)
        alpha[m] = a_m
        rgb[m] = rgb_m

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
