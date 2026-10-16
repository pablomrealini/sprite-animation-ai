"""Paso 5b (opcional): sacar el fogonazo de un clip de disparo y guardar dónde está la boca.

Los modelos de video dibujan el fogonazo aunque el prompt diga que no. Si queda en el sprite, el
brillo se mezcla con el fondo y sale con borde rosado al keyear, y agranda la celda de todo el
personaje. Acá se borra a resolución de video, antes del key, y la boca del cañón por frame se
exporta para que el engine dibuje su propio efecto anclado ahí.

Por frame:
  1. la boca es la columna más a la derecha con contorno oscuro dentro de la franja del arma;
  2. las filas del cañón son lo que no es fondo en la columna justo detrás de la boca;
  3. se pinta con el color de fondo todo lo que está delante de la boca, y el halo de arriba y de
     abajo del cañón entre `halo_x0` y la boca, dejando una fila a cada lado (el antialias).
El halo tiene que ser suave para no confundirse con el cañón en el paso 2, y lo es: sobre el
magenta suma 60-90 de diferencia, contra 120 del umbral. El contorno no sirve para eso porque el
fogonazo ilumina la boca por dentro y deja de ser oscuro.
La geometría del arma se fija en la config, en px del clip, o se mide en el frame 0, que es la pose
sin disparar: la boca es el contorno oscuro más a la derecha del personaje (que mira a la derecha),
las franjas salen del alto del personaje y `halo_x0` es donde empieza el tramo del cañón que no
tiene ni mano ni mira arriba o abajo. Supone que el arma no avanza más allá de donde está en el
frame 0; el retroceso la lleva para atrás, lejos del halo.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from . import imgio
from .config import FlashRemoval

DARK_LUM = 70  # luminancia media (0-255) por debajo de la cual un píxel es contorno
SOLID_DIFF = 120  # suma de |RGB - fondo| a partir de la cual un píxel es personaje
ROW_SLACK = 15  # cuánto pueden salirse de la franja las filas del cañón
TIP_GAP = 2  # se pinta desde este número de px delante de la boca
# Geometría automática, en fracciones del alto del personaje en el frame 0 (calibrada con el comando)
AUTO_BAND = 0.085  # media altura de la franja del arma
AUTO_SEARCH = (0.24, 0.27)  # cuánto se busca la boca hacia atrás y hacia adelante
AUTO_FLASH = 0.28  # media altura del fogonazo
HALO_MARGIN = 3  # px entre el inicio del tramo limpio del cañón y halo_x0

GEOMETRY = ("band_y", "search_x", "flash_y", "halo_x0")


def bg_color(img: np.ndarray) -> np.ndarray:
    """Promedio de un parche de 8×8 cerca de la esquina: el color con el que se pinta."""
    return img[4:12, 4:12, :3].reshape(-1, 3).mean(0).round().astype(np.uint8)


def detect_geometry(img: np.ndarray) -> dict:
    """Mide la geometría del arma en un frame sin fogonazo (el frame 0)."""
    a = img[..., :3].astype(np.int16)
    H = a.shape[0]
    solid = np.abs(a - bg_color(img).astype(np.int16)).sum(2) > SOLID_DIFF
    dark = (a.mean(2) < DARK_LUM) & solid
    ys = np.nonzero(solid.any(1))[0]
    cols = np.nonzero(dark.sum(0) >= 2)[0]
    if not len(ys) or not len(cols):
        raise ValueError("no encontré el arma en el frame 0: fijá la geometría de remove_flash en la config")
    h = int(ys.max() - ys.min() + 1)
    tip = int(cols.max())
    rows = np.nonzero(dark[:, max(0, tip - 2):tip + 1].any(1))[0]
    yc = (rows.min() + rows.max()) / 2
    band = (round(yc - AUTO_BAND * h), round(yc + AUTO_BAND * h))
    search = (max(0, tip - round(AUTO_SEARCH[0] * h)), tip + round(AUTO_SEARCH[1] * h))
    flash_y = (max(0, round(yc - AUTO_FLASH * h)), min(H, round(yc + AUTO_FLASH * h)))

    barrel = np.nonzero(solid[:, max(0, tip - 3)])[0]
    barrel = barrel[(barrel >= band[0] - ROW_SLACK) & (barrel <= band[1] + ROW_SLACK)]
    top, bot = (barrel.min(), barrel.max()) if len(barrel) else (rows.min(), rows.max())
    x = tip - 3  # hacia atrás, mientras arriba y abajo del cañón sólo haya fondo
    while x > search[0]:
        col = flash_y[0] + np.nonzero(solid[flash_y[0]:flash_y[1], x])[0]
        if ((col < top - 2) | (col > bot + 2)).any():
            break
        x -= 1
    return {"band_y": band, "search_x": search, "flash_y": flash_y, "halo_x0": min(tip - 3, x + 1 + HALO_MARGIN)}


def remove(img: np.ndarray, geo: dict) -> tuple[np.ndarray, dict | None]:
    """Devuelve el frame RGB sin fogonazo y la boca en px del video (None si no la encontró)."""
    a = img[..., :3].copy()
    bg = bg_color(a)
    lum = a.astype(np.int16).mean(2)
    (by0, by1), (sx0, sx1), (fy0, fy1), hx0 = (geo[k] for k in GEOMETRY)

    cols = np.nonzero((lum[by0:by1, sx0:sx1] < DARK_LUM).any(0))[0]
    if not len(cols):
        return a, None
    tip = sx0 + int(cols.max())
    behind = a[fy0:fy1, max(0, tip - 3)].astype(np.int16)
    rows = fy0 + np.nonzero(np.abs(behind - bg.astype(np.int16)).sum(1) > SOLID_DIFF)[0]
    rows = rows[(rows >= by0 - ROW_SLACK) & (rows <= by1 + ROW_SLACK)]
    if not len(rows):
        return a, None
    top, bot = int(rows.min()) - 1, int(rows.max()) + 1

    a[fy0:fy1, tip + TIP_GAP:] = bg  # todo lo que está delante de la boca
    a[fy0:top, hx0:tip + TIP_GAP] = bg  # halo arriba del cañón
    a[bot + 1:fy1, hx0:tip + TIP_GAP] = bg  # halo abajo del cañón
    return a, {"x": tip, "y": round((top + bot) / 2, 1)}


def run(in_dir: Path, out_dir: Path, params: FlashRemoval) -> dict:
    """Saca el fogonazo de todos los frames de in_dir y guarda muzzle.json junto a los frames."""
    paths = imgio.frames(in_dir)
    imgio.reset_dir(out_dir)
    fixed = {k: getattr(params, k) for k in GEOMETRY if getattr(params, k) is not None}
    auto = detect_geometry(imgio.load(paths[0])) if len(fixed) < len(GEOMETRY) else {}
    geo = {k: fixed.get(k, auto.get(k)) for k in GEOMETRY}

    muzzle = []
    for i, p in enumerate(paths):
        img, m = remove(imgio.load(p), geo)
        imgio.save(out_dir / p.name, img)
        muzzle.append({"frame": i, **(m or {"x": None, "y": None})})
    xs = [m["x"] for m in muzzle if m["x"] is not None]
    ys = [m["y"] for m in muzzle if m["y"] is not None]
    info = {
        "geometry": {k: list(v) if isinstance(v, tuple) else v for k, v in geo.items()},
        "measured": sorted(set(GEOMETRY) - set(fixed)),
        "missed_frames": [m["frame"] for m in muzzle if m["x"] is None],
        "muzzle_x": [min(xs), max(xs)] if xs else None,
        "muzzle_y": [min(ys), max(ys)] if ys else None,
    }
    imgio.write_json(out_dir / "muzzle.json", {**info, "note": "boca del cañón por frame nativo, en px del video",
                                               "muzzle": muzzle})
    return {**info, "muzzle": muzzle}


def anchors(name: str, muzzle: list[dict], native_indices: list[int], shifts: list[list[int]],
            canvas: dict, pivot_px: dict, variants: dict, pivot_norm_y: float,
            clip_scale: tuple[float, float] | None = None) -> dict:
    """Pasa la boca de px del video a px de la celda de cada variante, por frame de salida.

    El frame alineado pone el (0,0) del video en pivot + shift; la reducción escala por celda/canvas.
    Se usa el centro del píxel de la boca, en la misma convención que pivot_px (origen arriba a la
    izquierda, sin centrar en el píxel). clip_scale es la escala (x, y) con la que align llevó el clip
    a px de la referencia, si no es 1.
    """
    if clip_scale:
        kx, ky = clip_scale
        muzzle = [m if m["x"] is None else {**m, "x": (m["x"] + 0.5) * kx - 0.5, "y": (m["y"] + 0.5) * ky - 0.5}
                  for m in muzzle]
    out = {}
    for tag, v in variants.items():
        sx, sy = v["w"] / canvas["w"], v["h"] / canvas["h"]
        px, py = v["w"] * 0.5, round(v["h"] * pivot_norm_y, 2)
        frames = []
        for j, (n, (dx, dy)) in enumerate(zip(native_indices, shifts)):
            m = muzzle[n]
            f = {"frame": j, "name": f"{name}/{j:04d}", "native_frame": n}
            if m["x"] is None:
                frames.append({**f, "x": None, "y": None, "dx": None, "dy": None})
                continue
            x = (m["x"] + pivot_px["x"] + dx + 0.5) * sx
            y = (m["y"] + pivot_px["y"] + dy + 0.5) * sy
            frames.append({**f, "x": round(x, 2), "y": round(y, 2), "dx": round(x - px, 2), "dy": round(y - py, 2)})
        out[tag] = {"cell": {"w": v["w"], "h": v["h"]}, "pivot_px": {"x": px, "y": py}, "frames": frames}
    return {
        "note": (f"Boca del cañón por frame de {name}, para anclar el fogonazo. x,y en px de la celda "
                 "(origen arriba a la izquierda); dx,dy relativos al pivot (y hacia abajo). Con flipX, invertí dx."),
        "animation": name,
        "variants": out,
    }
