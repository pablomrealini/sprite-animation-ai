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

`method = "shape"` es para personajes sin contorno (el low-poly): la boca es una tapa con un disco
cian y, cuando el rayo sale pegado al disco, el contorno oscuro termina antes de la boca y el corte
se lleva la tapa. Ahí la boca se sigue con la forma del arma: el cuerpo del arma del frame 0 (sin la
punta, donde pega el brillo del rayo) se busca en cada frame alrededor de donde estaba en el anterior,
y la boca está siempre a la misma distancia de ese cuerpo. Se pinta con el color de fondo lo que
queda delante de la boca, en una franja alta alrededor de la altura del arma (la estrella del
fogonazo), y el anillo arriba y abajo del tramo del cañón junto a la boca. El frame 0 tiene que tener
el arma entera y sin rayo, con el disco cian a la vista.
"""

from __future__ import annotations

from pathlib import Path

import cv2
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
# method = "shape", en fracciones del alto del personaje en el frame 0 (calibrada con el low-poly de Kling O3)
SHAPE_GUN = 0.28  # largo del arma, de la empuñadura a la boca
SHAPE_STEP = 0.12  # cuánto puede moverse el arma de un frame al siguiente
SHAPE_REACH = 0.40  # media altura de la zona que se limpia delante de la boca (la estrella del fogonazo es alta)
SHAPE_HALO = 2  # el anillo alrededor de la boca: se limpia arriba y abajo del cañón, hasta tantos discos atrás
SHAPE_LOST = 25.0  # ΔE medio por píxel (Lab) a partir del cual el arma se da por perdida (bien: 2–18; perdida: 30+)


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


def _lab(rgb: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(np.ascontiguousarray(rgb, np.float32) / 255.0, cv2.COLOR_RGB2LAB)


def shape_geometry(img: np.ndarray) -> dict:
    """method = "shape": la boca en el frame 0 (el disco cian más a la derecha) y el cuerpo del arma que se sigue."""
    a = img[..., :3].astype(np.int16)
    solid = np.abs(a - bg_color(img).astype(np.int16)).sum(2) > SOLID_DIFF
    ys = np.nonzero(solid.any(1))[0]
    cyan = (a[..., 1] > 140) & (a[..., 2] > 140) & (a[..., 0] < 140)
    n, _, st, _ = cv2.connectedComponentsWithStats(cyan.astype(np.uint8))
    if not len(ys) or n < 2:
        raise ValueError("method shape: no encontré el disco cian de la boca en el frame 0")
    i = 1 + max(range(n - 1), key=lambda k: st[k + 1, 0] + st[k + 1, 2])
    x, y, w, dh = (int(v) for v in st[i, :4])
    front = max(int(np.nonzero(r)[0].max()) for r in solid[y:y + dh] if r.any())
    h = int(ys.max() - ys.min() + 1)
    gun = round(SHAPE_GUN * h)
    hx0 = front - SHAPE_HALO * dh  # el tramo del cañón junto a la boca: arriba y abajo sólo puede haber halo
    near = np.nonzero(solid[max(0, y - 3 * dh):y + 4 * dh, hx0:front + 1].any(1))[0] + max(0, y - 3 * dh)
    return {"front": front, "disk_y": [y, y + dh], "template": [front - gun, y - 2 * dh, front - 2 * dh, y + 2 * dh],
            "band": round(SHAPE_REACH * h), "halo": [hx0, int(near.min()), int(near.max())],
            "step": max(4, round(SHAPE_STEP * h))}


def _run_shape(paths: list[Path], out_dir: Path) -> dict:
    first = imgio.load(paths[0])
    geo = shape_geometry(first)
    tx0, ty0, tx1, ty1 = geo["template"]
    tmpl = _lab(first[ty0:ty1, tx0:tx1, :3])
    H, W = first.shape[:2]
    step, band, (y0, y1) = geo["step"], geo["band"], geo["disk_y"]
    px, py, muzzle = tx0, ty0, []
    n_tmpl = tmpl.shape[0] * tmpl.shape[1]
    for i, p in enumerate(paths):
        a = imgio.load(p)[..., :3].copy()
        sx0, sy0 = max(0, px - step), max(0, py - step)
        sx1, sy1 = min(W, px + (tx1 - tx0) + step), min(H, py + (ty1 - ty0) + step)
        v, _, (mx, my), _ = cv2.minMaxLoc(cv2.matchTemplate(_lab(a[sy0:sy1, sx0:sx1]), tmpl, cv2.TM_SQDIFF))
        cand, held = (sx0 + mx, sy0 + my), False
        # el fogonazo ilumina el arma, o el arma gira, y la coincidencia empeora: si el error medio por píxel pasa
        # SHAPE_LOST (ΔE), se busca en todo el cuadro, y si tampoco aparece, el arma queda donde estaba (no se va a la
        # deriva hacia las botas)
        if (v / n_tmpl) ** 0.5 > SHAPE_LOST:
            vg, _, (gx, gy), _ = cv2.minMaxLoc(cv2.matchTemplate(_lab(a), tmpl, cv2.TM_SQDIFF))
            if (vg / n_tmpl) ** 0.5 <= SHAPE_LOST:
                cand = (gx, gy)
            else:
                cand, held = (px, py), True
        px, py = cand
        dx, dy = px - tx0, py - ty0
        tip, yc = geo["front"] + dx, (y0 + y1) / 2 + dy
        r0, r1 = max(0, round(yc - band)), min(H, round(yc + band))
        bg = bg_color(a)
        a[r0:r1, tip + 1:] = bg  # lo que está delante de la boca
        hx0, gtop, gbot = geo["halo"]
        a[r0:max(r0, gtop + dy - 1), hx0 + dx:tip + 1] = bg  # el halo arriba del cañón, junto a la boca
        a[min(r1, gbot + dy + 2):r1, hx0 + dx:tip + 1] = bg  # y abajo
        imgio.save(out_dir / p.name, a)
        muzzle.append({"frame": i, "x": int(tip), "y": round(float(yc), 1), **({"held": True} if held else {})})
    xs, ys = [m["x"] for m in muzzle], [m["y"] for m in muzzle]
    return {"geometry": {"method": "shape", **geo}, "measured": ["shape"],
            "held_frames": [m["frame"] for m in muzzle if m.get("held")], "missed_frames": [],
            "muzzle_x": [min(xs), max(xs)], "muzzle_y": [min(ys), max(ys)], "muzzle": muzzle}


def run(in_dir: Path, out_dir: Path, params: FlashRemoval) -> dict:
    """Saca el fogonazo de todos los frames de in_dir y guarda muzzle.json junto a los frames."""
    paths = imgio.frames(in_dir)
    imgio.reset_dir(out_dir)
    if params.method == "shape":
        res = _run_shape(paths, out_dir)
        imgio.write_json(out_dir / "muzzle.json", {**{k: v for k, v in res.items() if k != "muzzle"},
                                                   "note": "boca del cañón por frame nativo, en px del video",
                                                   "muzzle": res["muzzle"]})
        return res
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
