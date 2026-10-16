"""Post de los fondos generados, sin IA: key del fondo plano, transparencia, piezas sueltas, costura y recorte.

Todo se hace en alfa premultiplicado, así los bordes semitransparentes no arrastran el color del fondo.

- Key: los modelos sin transparencia nativa dibujan sobre un color plano (verde por defecto, que no
  aparece en la base), y se saca con el mismo keyer de los personajes (key.py) en modo global: un hueco
  del color de key encerrado entre dos edificios o dentro de un cartel también es fondo.
- Transparencia: qué fracción es transparente, si el borde lo es, si quedó color de key, y si el modelo
  pintó el damero de "transparente" en vez de devolver alfa.
- Piezas: una hoja (el kit de plataformas, los props) se separa por componentes del alfa, en orden de
  lectura, todas a una misma escala. Con same_height, las que tienen que empalmar quedan a la misma altura.
- Costura: una capa que se repite en x tiene que empalmar su última columna con la primera. `seam_score`
  compara esa diferencia con la típica entre columnas vecinas (cerca de 1, invisible). Si se nota, una
  franja del final se superpone al principio y la capa pierde ese ancho (si no mejora, se descarta):
    cut: corte de error mínimo (image quilting, Efros y Freeman 2001). Un camino de arriba abajo por donde
         las dos franjas más se parecen, con 2 px de fundido. No duplica contornos y, en una capa con
         transparencia, pasa por el aire entre las siluetas.
    crossfade: fundido lineal en toda la franja. Para cielos y degradés; en dibujo de línea deja contornos dobles.
    mask: no toca la capa. Escribe la capa corrida medio ancho (la costura queda en el centro) y la máscara
         de la franja (transparente = lo que se edita, la convención de OpenAI), para editarla a mano o con
         un modelo de edición con máscara.
- Recorte: al bbox del alfa, salvo en los ejes que se repiten.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace

import cv2
import numpy as np

from . import chroma, imgio, key

ALPHA_ON = 8  # alfa (0-255) que cuenta como contenido al recortar y al separar piezas
TRIM_PAD = 2  # px de aire alrededor del recorte, para no comerse el antialias
FEATHER = 2  # px de fundido a cada lado del corte de error mínimo
# Costura relativa a la diferencia típica entre columnas vecinas. En las capas mid de ranger_base, a ojo: GPT
# 23,6 (corte claro), Seedream 5,3 (se nota), FLUX 3,4 (apenas), Nano Banana 1,9 (no se ve).
SEAM_OK, SEAM_WARN = 2.0, 4.0
SEAM_BANDS = 16
PIECE_MIN_FRAC = 0.02  # una pieza más chica que esto (en área, respecto de la mayor) es basura
PIECE_GAP_PX = 2  # partes a menos de esto se juntan en una pieza (un tornillo suelto, una luz)
HEIGHT_SNAP = 0.15  # piezas que difieren menos que esto de la altura común se escalan a ella; las otras, no


@dataclass
class PostSpec:
    expect: str = "cutout"  # "opaque" (cielo, style frame) | "layer" (capa con aire arriba) | "cutout" (props, kit)
    key: str | None = None  # "#RRGGBB" si el modelo dibujó sobre un color plano; None si trae alfa o es opaco
    tile: dict[str, str] = field(default_factory=dict)  # pieza ("" = la imagen entera) -> "x" | "y" | "xy"
    seam: str = "cut"  # "cut" | "crossfade" | "mask" | "none"
    seam_px: float = 0.12  # ancho de la franja de la costura: px, o fracción del ancho si es < 1
    trim: bool = True
    split: list[str] = field(default_factory=list)  # nombres de las piezas de una hoja, en orden de lectura
    same_height: bool = False  # en una hoja: las piezas a una misma altura (las de un kit que empalman)
    height: int | None = None  # alto final en px; en una hoja, el de la altura común o el de la pieza más alta


# --- alfa premultiplicado ------------------------------------------------------------


def as_rgba(img: np.ndarray) -> np.ndarray:
    if img.shape[2] == 4:
        return img
    return np.dstack([img, np.full(img.shape[:2], 255, np.uint8)])


def premul(rgba: np.ndarray) -> np.ndarray:
    f = rgba.astype(np.float32) / 255.0
    f[..., :3] *= f[..., 3:4]
    return f


def unpremul(f: np.ndarray) -> np.ndarray:
    a = f[..., 3:4]
    rgb = np.where(a > 1e-6, f[..., :3] / np.maximum(a, 1e-6), 0.0)
    return (np.clip(np.dstack([rgb, a]), 0, 1) * 255 + 0.5).astype(np.uint8)


def resize(rgba: np.ndarray, w: int, h: int) -> np.ndarray:
    if (w, h) == (rgba.shape[1], rgba.shape[0]):
        return rgba
    shrink = w * h < rgba.shape[0] * rgba.shape[1]
    f = cv2.resize(premul(rgba), (w, h), interpolation=cv2.INTER_AREA if shrink else cv2.INTER_LANCZOS4)
    return unpremul(np.clip(f, 0, 1))


# --- key -----------------------------------------------------------------------------


def estimate_key(rgb: np.ndarray, wanted: np.ndarray) -> np.ndarray:
    """El color de fondo real: la mediana de lo que se parece mucho al color pedido. Los modelos nunca
    devuelven #00FF00 exacto, y en una capa que llega abajo y a los costados el borde no es todo fondo."""
    dom, opp = chroma.split_channels(wanted)
    s = chroma.screen(rgb, dom, opp)
    near = s > 0.5 * chroma.key_strength(wanted)
    if near.mean() < 0.005:
        return wanted
    return np.median(rgb[near], axis=0).astype(np.float32)


def key_out(img: np.ndarray, color: str) -> tuple[np.ndarray, dict]:
    rgb = img[..., :3].astype(np.float32) / 255.0
    wanted = chroma.parse_hex(color)
    k = estimate_key(rgb, wanted)
    # Los mismos valores por defecto que [key] de un personaje, en modo global
    params = SimpleNamespace(key_method="chroma", key_mode="global", key_tolerance=(0.12, 0.80), min_island_px=64,
                             hole_max_frac=0.0, despill=1.0, despill_band_px=3)
    rgba, k, method, _ = key.key_frame(img[..., :3], params, k)
    return rgba, {"key_color": "#" + "".join(f"{round(c * 255):02X}" for c in k), "method": method}


# --- transparencia -------------------------------------------------------------------


def looks_checker(rgb: np.ndarray, patch: int = 96) -> bool:
    """El damero gris y blanco que algunos modelos dibujan cuando se les pide fondo transparente: en una
    esquina, dos tonos claros y neutros, cada uno en al menos un cuarto de los píxeles."""
    for c in (rgb[:patch, :patch], rgb[:patch, -patch:], rgb[-patch:, :patch], rgb[-patch:, -patch:]):
        c = c.reshape(-1, 3).astype(np.int16)
        neutral = (c.max(1) - c.min(1) < 12) & (c.min(1) > 140)
        if neutral.mean() < 0.9:
            continue
        lum = c[neutral].mean(1)
        hi, lo = lum > lum.mean(), lum <= lum.mean()
        if hi.mean() > 0.25 and lo.mean() > 0.25 and lum[hi].mean() - lum[lo].mean() > 12:
            return True
    return False


def alpha_report(rgba: np.ndarray, expect: str, key_color: str | None = None) -> dict:
    a = rgba[..., 3]
    transparent, opaque = float((a == 0).mean()), float((a == 255).mean())
    edges = {"top": a[0], "bottom": a[-1], "left": a[:, 0], "right": a[:, -1]}
    border = {k: round(float((v == 0).mean()), 3) for k, v in edges.items()}
    flags = []
    if expect == "opaque":
        if opaque < 0.999:
            flags.append(("warn", f"{100 * (1 - opaque):.1f}% sin alfa pleno en una imagen que va opaca"))
    else:
        if transparent < 0.02:
            flags.append(("fail", "sin transparencia" + (": el modelo pintó el damero en vez de devolver alfa"
                                                          if looks_checker(rgba[..., :3]) else "")))
        elif expect == "layer" and border["top"] < 0.5:
            flags.append(("warn", f"el borde de arriba es transparente sólo en un {100 * border['top']:.0f}%: "
                                  "la capa tapa el cielo"))
        elif expect == "cutout":
            cut = [k for k, v in border.items() if v < 0.98]
            if cut:
                flags.append(("warn", f"el contenido toca el borde ({', '.join(cut)}): puede estar cortado"))
    if key_color and transparent >= 0.02:
        k = chroma.parse_hex(key_color)
        dom, opp = chroma.split_channels(k)
        rgb = rgba[..., :3].astype(np.float32) / 255.0
        left = (a > 128) & (chroma.screen(rgb, dom, opp) > 0.35 * chroma.key_strength(k))
        frac = float(left.sum() / max(1, (a > 128).sum()))
        if frac > 0.001:
            flags.append(("warn", f"quedó color de key en el {100 * frac:.2f}% de lo opaco"))
    verdict = "fail" if any(f[0] == "fail" for f in flags) else "warn" if flags else "ok"
    return {"verdict": verdict, "transparent": round(transparent, 4), "opaque": round(opaque, 4),
            "border_transparent": border, "flags": [m for _, m in flags]}


# --- piezas --------------------------------------------------------------------------


def split(rgba: np.ndarray, names: list[str]) -> tuple[list[tuple[str, np.ndarray, list[int]]], list[str]]:
    """Separa una hoja en piezas por componentes conexos del alfa, en orden de lectura (filas, después x).
    Cada pieza lleva sólo sus píxeles, aunque el bbox de una vecina se le meta."""
    solid = (rgba[..., 3] >= ALPHA_ON).astype(np.uint8)
    k = 2 * PIECE_GAP_PX + 1
    joined = cv2.dilate(solid, np.ones((k, k), np.uint8))
    n, labels, stats, cent = cv2.connectedComponentsWithStats(joined, connectivity=8)
    areas = np.bincount(labels[solid > 0], minlength=n)
    keep = [i for i in range(1, n) if areas[i] >= PIECE_MIN_FRAC * max(areas[1:].max(initial=0), 1)]
    notes = []
    if dropped := (n - 1) - len(keep):
        notes.append(f"{dropped} manchas chicas descartadas")
    hs = np.median([stats[i, cv2.CC_STAT_HEIGHT] for i in keep]) if keep else 0
    rows: list[list[int]] = []
    for i in sorted(keep, key=lambda i: cent[i][1]):
        if rows and cent[i][1] - np.mean([cent[j][1] for j in rows[-1]]) < 0.5 * hs:
            rows[-1].append(i)
        else:
            rows.append([i])
    order = [i for row in rows for i in sorted(row, key=lambda i: cent[i][0])]
    if names and len(order) != len(names):
        notes.append(f"salieron {len(order)} piezas y se esperaban {len(names)} ({', '.join(names)}): "
                     "quedan numeradas")
        names = []
    out = []
    for j, i in enumerate(order):
        mine = labels == i
        ys, xs = np.nonzero(mine & (solid > 0))  # el bbox de lo que hay, sin el margen de la dilatación
        x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
        piece = rgba[y0:y1, x0:x1].copy()
        piece[~mine[y0:y1, x0:x1]] = 0
        out.append((names[j] if names else f"pieza_{j + 1}", piece, [x0, y0, x1, y1]))
    return out, notes


def same_height(pieces: list[tuple[str, np.ndarray]]) -> tuple[list[np.ndarray], dict, list[str]]:
    """Las piezas a la altura mediana. Las que difieren menos de HEIGHT_SNAP se escalan a ella (el modelo
    las dibujó apenas distintas y tienen que empalmar); las demás quedan a su escala, con aire abajo si son
    más bajas (el borde de arriba, por donde se camina, queda alineado)."""
    target = int(round(float(np.median([p.shape[0] for _, p in pieces]))))
    out, scales, notes = [], {}, []
    for name, p in pieces:
        s = target / p.shape[0]
        if abs(s - 1) <= HEIGHT_SNAP:
            out.append(resize(p, max(1, round(p.shape[1] * s)), target))
            scales[name] = round(s, 4)
        elif p.shape[0] < target:
            pad = np.zeros((target - p.shape[0],) + p.shape[1:], np.uint8)
            out.append(np.concatenate([p, pad]))
            scales[name] = 1.0
            notes.append(f"{name} mide {p.shape[0]} px contra {target}: queda a su escala, con aire abajo")
        else:
            out.append(p)
            scales[name] = 1.0
            notes.append(f"{name} mide {p.shape[0]} px contra {target}: queda a su escala, más alta que las demás")
    return out, {"height": target, "scales": scales}, notes


def uniform(pieces: list[np.ndarray], height: int | None, ref: int) -> list[np.ndarray]:
    """Una sola escala para todas: la que lleva `ref` px a `height`."""
    if not height or height == ref:
        return pieces
    s = height / ref
    return [resize(p, max(1, round(p.shape[1] * s)), max(1, round(p.shape[0] * s))) for p in pieces]


# --- costura -------------------------------------------------------------------------


def _along(f: np.ndarray, axis: str) -> np.ndarray:
    return f if axis == "x" else f.transpose(1, 0, 2)


def seam_score(rgba: np.ndarray, axis: str = "x") -> dict:
    """Diferencia entre el último borde y el primero, relativa a la típica entre columnas vecinas: con 1, la
    vuelta es un paso como cualquier otro. `peak` es la peor de 16 franjas, sólo como dato: un contorno
    vertical que cae justo en la vuelta la dispara sin que haya costura (pasó con Nano Banana en ranger_base)."""
    f = _along(premul(rgba), axis)
    adj = np.abs(np.diff(f, axis=1)).sum(-1)
    wrap = np.abs(f[:, -1] - f[:, 0]).sum(-1)
    typical = max(float(adj.mean()), 1e-3)
    bands = [b for b in np.array_split(np.arange(f.shape[0]), SEAM_BANDS) if len(b)]
    score = float(wrap.mean()) / typical
    peak = max(float(wrap[b].mean()) for b in bands) / typical
    verdict = "ok" if score <= SEAM_OK else "warn" if score <= SEAM_WARN else "fail"
    return {"axis": axis, "score": round(score, 2), "peak": round(peak, 2), "verdict": verdict}


def _min_cut(err: np.ndarray, lo: int, hi: int) -> np.ndarray:
    """Camino vertical de costo mínimo por err (alto × ancho), una columna por fila, que se mueve a lo sumo
    un px entre filas y queda en [lo, hi]."""
    h, w = err.shape
    cost = np.full((h, w), np.inf)
    back = np.zeros((h, w), np.int8)
    band = np.zeros(w, bool)
    band[lo:hi + 1] = True
    cost[0, band] = err[0, band]
    for y in range(1, h):
        prev = cost[y - 1]
        cand = np.stack([np.r_[np.inf, prev[:-1]], prev, np.r_[prev[1:], np.inf]])
        k = cand.argmin(0)
        cost[y] = np.where(band, cand[k, np.arange(w)] + err[y], np.inf)
        back[y] = k - 1
    path = np.empty(h, int)
    path[-1] = int(cost[-1].argmin())
    for y in range(h - 1, 0, -1):
        path[y - 1] = path[y] + back[y, path[y]]
    return path


def fix_seam(rgba: np.ndarray, method: str, overlap: float, axis: str = "x") -> tuple[np.ndarray, dict]:
    """La franja final se superpone a la inicial y la capa pierde ese ancho. El nuevo último px es el que
    estaba justo antes de la franja, y el nuevo primero, el que le seguía: la vuelta empalma por
    construcción, y la unión queda adentro, donde el corte o el fundido la esconden."""
    f = _along(premul(rgba), axis)
    w_total = f.shape[1]
    w = int(round(overlap * w_total if overlap < 1 else overlap))
    w = max(2 * FEATHER + 4, min(w, w_total // 3))
    tail, head = f[:, w_total - w:], f[:, :w]
    x = np.arange(w)[None, :]
    if method == "crossfade":
        t = np.broadcast_to((x + 0.5) / w, tail.shape[:2])
        info = {}
    elif method == "cut":
        err = ((tail - head) ** 2).sum(-1)
        path = _min_cut(err, FEATHER, w - 1 - FEATHER)
        t = np.clip((x - path[:, None] + FEATHER) / (2 * FEATHER), 0, 1)
        info = {"cut_error": round(float(err[np.arange(len(path)), path].mean()), 5),
                "cut_x": [int(path.min()), int(path.max())]}
    else:
        raise ValueError(f"seam tiene que ser cut, crossfade, mask o none, no {method!r}")
    blend = tail * (1 - t)[..., None] + head * t[..., None]
    out = np.concatenate([blend, f[:, w:w_total - w]], axis=1)
    out = unpremul(_along(out, axis))
    return out, {"method": method, "overlap_px": w, **info}


def seam_mask(rgba: np.ndarray, overlap: float, axis: str = "x") -> tuple[np.ndarray, np.ndarray]:
    """La capa corrida medio ancho (la costura queda en el centro) y una máscara RGBA del mismo tamaño,
    opaca salvo la franja de la costura, que queda transparente (lo que un modelo de edición repinta)."""
    ax = 1 if axis == "x" else 0
    n = rgba.shape[ax]
    w = int(round(overlap * n if overlap < 1 else overlap))
    rolled = np.roll(rgba, n // 2, axis=ax)
    mask = np.zeros(rgba.shape[:2] + (4,), np.uint8)
    mask[..., 3] = 255
    sl = slice(max(0, n // 2 - w // 2), n // 2 + w // 2)
    if ax == 1:
        mask[:, sl, 3] = 0
    else:
        mask[sl, :, 3] = 0
    return rolled, mask


# --- recorte -------------------------------------------------------------------------


def trim(rgba: np.ndarray, keep: str = "") -> tuple[np.ndarray, list[int]]:
    """Recorta al contenido (alfa >= ALPHA_ON, más TRIM_PAD px), salvo en los ejes de `keep` ("x", "y")."""
    ys, xs = np.nonzero(rgba[..., 3] >= ALPHA_ON)
    h, w = rgba.shape[:2]
    if not len(ys):
        return rgba, [0, 0, w, h]
    x0, x1 = (0, w) if "x" in keep else (max(0, xs.min() - TRIM_PAD), min(w, xs.max() + 1 + TRIM_PAD))
    y0, y1 = (0, h) if "y" in keep else (max(0, ys.min() - TRIM_PAD), min(h, ys.max() + 1 + TRIM_PAD))
    return rgba[y0:y1, x0:x1], [int(x0), int(y0), int(x1), int(y1)]


# --- todo junto ----------------------------------------------------------------------


def _finish(name: str, img: np.ndarray, spec: PostSpec, tile: str, dest: Path, rep: dict, keep: str = "") -> None:
    """Costura, recorte y alto de una imagen o pieza; la escribe en dest y anota en rep."""
    for axis in tile:
        before = seam_score(img, axis)
        entry = {"before": before}
        if spec.seam in ("cut", "crossfade") and before["verdict"] != "ok":
            fixed, how = fix_seam(img, spec.seam, spec.seam_px, axis)
            after = seam_score(fixed, axis)
            if after["score"] < before["score"]:
                img = fixed
                entry.update(fix=how, after=after)
            else:
                entry["fix_discarded"] = {**how, "after": after}
        elif spec.seam == "mask" and before["verdict"] != "ok":
            rolled, mask = seam_mask(img, spec.seam_px, axis)
            imgio.save(dest.with_name(f"{dest.stem}.seam_{axis}.png"), rolled)
            imgio.save(dest.with_name(f"{dest.stem}.seam_{axis}_mask.png"), mask)
            entry["mask"] = [f"{dest.stem}.seam_{axis}.png", f"{dest.stem}.seam_{axis}_mask.png"]
        rep.setdefault("seam", {})[f"{name}:{axis}" if name else axis] = entry
    if spec.trim and spec.expect != "opaque":
        img, box = trim(img, keep=tile + keep)
        rep.setdefault("trim", {})[name or "image"] = box
    imgio.save(dest, img)
    rep.setdefault("files", {})[name or "image"] = {"file": dest.name, "w": img.shape[1], "h": img.shape[0]}


def process(src: Path, dest: Path, spec: PostSpec) -> dict:
    """Post de una imagen generada. Sin split escribe dest; con split, dest.parent/dest.stem/<pieza>.png."""
    img = as_rgba(imgio.load(src))
    rep: dict = {"source": {"w": img.shape[1], "h": img.shape[0]}, "notes": []}
    if spec.key and spec.expect != "opaque":
        img, rep["key"] = key_out(img, spec.key)
    rep["alpha"] = alpha_report(img, spec.expect, spec.key)
    if spec.height and not spec.split:
        img = resize(img, max(1, round(img.shape[1] * spec.height / img.shape[0])), spec.height)
    if not spec.split:
        _finish("", img, spec, spec.tile.get("", ""), dest, rep)
        return rep
    pieces, notes = split(img, spec.split)
    rep["notes"] += notes
    trimmed = [(name, trim(p)[0]) for name, p in (pc[:2] for pc in pieces)]
    if spec.same_height:
        sized, rep["height"], notes = same_height(trimmed)
        rep["notes"] += notes
        ref = rep["height"]["height"]
    else:
        sized, ref = [p for _, p in trimmed], max(p.shape[0] for _, p in trimmed)
    sized = uniform(sized, spec.height, ref)
    rep["pieces"] = {name: box for name, _, box in pieces}
    folder = dest.parent / dest.stem
    for (name, _), p in zip(trimmed, sized):
        _finish(name, p, spec, spec.tile.get(name, ""), folder / f"{name}.png", rep, "y" if spec.same_height else "")
    return rep
