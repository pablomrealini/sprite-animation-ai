"""Revisión cuadro por cuadro de las animaciones del low-poly, como la del salto (2026-10-18).

Dos comandos (desde la raíz del repo, después de `spritepipe run characters/lowpoly/character.toml`):

    uv run --project pipeline python characters/lowpoly/revisar.py hoja throw double_jump
    uv run --project pipeline python characters/lowpoly/revisar.py nativos throw 30 78

`hoja` arma revision/<anim>_cuadros.png desde el atlas: cada cuadro sobre verde, sobre oscuro y "rosa" (gris, con lo
que queda del color del fondo en amarillo), con su número, el nativo del clip del que sale, lo medido y para qué lo usa
la arena (RIG.lowpoly de prototypes/arena/src.html). Además, revision/<anim>_juego.png: la variante 0,5× a tamaño de
juego en retina (128 px × 0,8 × 2 ≈ 205 px), que es como se ve.

Lo medido, por cuadro:
  nit   nitidez: varianza del laplaciano adentro del personaje, relativa a la mediana de la animación (< 0,7 es borroso)
  rosa  px opacos del color del fondo (a menos de ΔRGB 60 del key): bolsillos de magenta y bordes sin limpiar
  dx dy cuánto se mueve el centro de los pies y la cabeza contra el cuadro anterior, en px de 1x (corridos)

`comparar` pone lado a lado, sobre oscuro, cuadros de dos corridas del atlas (p. ej. una copia de out/ de antes de un
cambio del key y la de ahora), con el detalle ampliado y el tinte del borde de cada uno: revision/<nombre>.png.

    uv run --project pipeline python characters/lowpoly/revisar.py comparar work_revisar/out_antes idle_combat:0 throw:20

`tira` arma una secuencia como la juega la arena, a tamaño de juego sobre oscuro, desde un JSON (revision/<nombre>.json):
{"titulo": ..., "filas": [{"titulo": ..., "out": ..., "cuadros": [[anim, cuadro, ms, etiqueta, grados], ...]}]}; los grados
(opcional) giran el cuadro alrededor del centro de su caja, como el mortal del juego (horario, como drawRot); "out"
(opcional, relativo a characters/lowpoly) toma esa fila de otra corrida, p. ej. la de `nativos`.

    uv run --project pipeline python characters/lowpoly/revisar.py tira characters/lowpoly/revision/throw_fix.json

`nativos` arma todos los cuadros nativos de un tramo del clip (con el mismo key, escala y nitidez del atlas, en
work_revisar/, que git ignora) y su hoja en revision/<anim>_nativos_<a>-<b>.png, para elegir a mano los `frames`.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import textwrap
import tomllib
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SRC = REPO / "prototypes" / "arena" / "src.html"
GREEN = (0, 177, 64)          # el verde de las hojas del salto
DARK = (24, 26, 34)           # el fondo oscuro de la arena
YELLOW = (255, 230, 0)
H = 230                       # alto de cada cuadro en la hoja, px
COLS = 9
GAME_K = 1.6                  # 0,5× (128 px) × 0,8 × 2 = 205 px: retina en 1080p
PATH_KEYS = ("clip", "file", "pose", "prompt", "scale_pose", "palette")


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    for name in (("Arial Bold.ttf",) if bold else ()) + ("Arial.ttf",):
        p = Path("/System/Library/Fonts/Supplemental") / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default(size=size)


# --- datos del atlas -----------------------------------------------------------------------------------------------

def cells(out: Path, variant: str, anim: str) -> list[np.ndarray]:
    meta = json.loads((out / "sheets" / variant / f"{anim}.json").read_text(encoding="utf-8"))
    im = np.array(Image.open(out / "sheets" / variant / f"{anim}.png").convert("RGBA"))
    w, h, cols = meta["cell"]["w"], meta["cell"]["h"], meta["cols"]
    return [im[(i // cols) * h:(i // cols + 1) * h, (i % cols) * w:(i % cols + 1) * w] for i in range(meta["count"])]


def provenance(out: Path, anim: str) -> dict:
    p = json.loads((out / "provenance.json").read_text(encoding="utf-8"))
    return p["animations"].get(anim, {})


def usos(anim: str) -> dict[int, list[str]]:
    """Para qué usa la arena cada cuadro de `anim`, leído de RIG.lowpoly en src.html."""
    if not SRC.exists():
        return {}
    txt = SRC.read_text(encoding="utf-8")
    m = re.search(r"\n  lowpoly: \{\n(.*?)\n  \},", txt, re.S)
    if not m:
        return {}
    rig = m.group(1)
    u: dict[int, list[str]] = {}
    add = lambda i, s: u.setdefault(int(i), []).append(s)  # noqa: E731
    if anim == "throw":
        if t := re.search(r"throw: \[(.*?)\],\n", rig):
            seq = [int(a) for a, _ in re.findall(r"\[(\d+), ([\d.]+)\]", t.group(1))]
            for k, i in enumerate(dict.fromkeys(seq)):
                add(i, f"tiro {k}")
            if len(seq) > 1:
                add(seq[1], "carga")
            rel = re.search(r"releaseFrame: (\d+)", txt)
            if rel and int(rel.group(1)) < len(seq):
                add(seq[int(rel.group(1))], "sale")
        if t := re.search(r"melee: \[(.*?)\],\n", rig):
            for k, i in enumerate(re.findall(r'\["throw", (\d+),', t.group(1))):
                add(i, f"golpe {k}")
    if anim == "double_jump":
        if t := re.search(r"flip: \[(.*?)\], flipFall: (\d+)", rig):
            for i, ang in re.findall(r"\[(\d+), (\d+)\]", t.group(1)):
                add(i, f"mortal {ang}°")
            add(t.group(2), "caída")
    if anim == "jump" and (t := re.search(r"jump: \{(.*?)\}", rig)):
        for k, v in re.findall(r"(\w+): (\[[\d, ]*\]|\d+)", t.group(1)):
            for i in re.findall(r"\d+", v):
                add(i, k)
    if anim == "hang_in" and (t := re.search(r"grab: \[([\d, ]+)\]", rig)):
        for i in re.findall(r"\d+", t.group(1)):
            add(i, "agarre")
    if anim == "climb" and (t := re.search(r"climb: \[(.*?)\],\n", rig)):
        for i in re.findall(r"\[(\d+), \d+, [\d.]+\]", t.group(1)):
            add(i, "subida")
    if anim == "jump_shoot" and (t := re.search(r"airShot: (\d+)", rig)):
        add(t.group(1), "tiro en el aire")
    return u


# --- lo medido -----------------------------------------------------------------------------------------------------

def medir(cs: list[np.ndarray], key: tuple[int, int, int]) -> list[dict]:
    res = []
    for c in cs:
        a = c[..., 3] > 128
        rgb = c[..., :3].astype(np.float32)
        lum = cv2.cvtColor(c[..., :3], cv2.COLOR_RGB2GRAY).astype(np.float32)
        inner = cv2.erode(a.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        lap = cv2.Laplacian(lum, cv2.CV_32F)
        sharp = float(lap[inner].var()) if inner.any() else 0.0
        pink = a & (np.linalg.norm(rgb - np.array(key, np.float32), axis=2) < 60)
        ys, xs = np.nonzero(a)
        if len(ys):
            y1 = ys.max()
            feet = xs[ys >= y1 - 6].mean()
            y0 = ys.min()
            head = xs[ys <= y0 + 30].mean()
        else:
            y0 = y1 = feet = head = 0
        res.append({"sharp": sharp, "pink": int(pink.sum()), "pink_mask": pink, "feet": (float(feet), int(y1)),
                    "head": (float(head), int(y0)), "box": (xs.min(), ys.min(), xs.max(), ys.max()) if len(ys) else None})
    med = float(np.median([r["sharp"] for r in res])) or 1.0
    for i, r in enumerate(res):
        r["nit"] = r["sharp"] / med
        p = res[i - 1] if i else r
        r["dx"] = r["feet"][0] - p["feet"][0]
        r["dy"] = r["feet"][1] - p["feet"][1]
        r["dhead"] = r["head"][0] - p["head"][0]
    return res


# --- hojas ---------------------------------------------------------------------------------------------------------

def tile(c: np.ndarray, box: tuple[int, int, int, int], bg, h: int, pink: np.ndarray | None = None) -> Image.Image:
    im = Image.fromarray(c, "RGBA")
    if pink is not None:   # gris, con el color del fondo en amarillo
        g = np.array(im.convert("LA").convert("RGBA"))
        g[..., :3] = (g[..., :3] * 0.55 + 60).astype(np.uint8)
        g[..., 3] = c[..., 3]
        big = cv2.dilate(pink.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
        g[big] = (*YELLOW, 255)
        im = Image.fromarray(g, "RGBA")
    base = Image.new("RGBA", im.size, (*bg, 255))
    base.alpha_composite(im)
    t = base.crop(box)
    return t.resize((round(t.width * h / t.height), h), Image.LANCZOS).convert("RGB")


def union_box(cs: list[np.ndarray], pad: int = 6) -> tuple[int, int, int, int]:
    m = np.zeros(cs[0].shape[:2], bool)
    for c in cs:
        m |= c[..., 3] > 20
    ys, xs = np.nonzero(m)
    h, w = m.shape
    return max(0, xs.min() - pad), max(0, ys.min() - pad), min(w, xs.max() + pad + 1), min(h, ys.max() + pad + 1)


def hoja(out: Path, anim: str, dest: Path, titulo: str, natives: list[int] | None = None, rosa: bool = True,
         nota: dict[int, str] | None = None, con_usos: bool = True) -> list[dict]:
    cs = cells(out, "1x", anim)
    prov = provenance(out, anim)
    natives = natives or prov.get("timing", {}).get("native_indices") or list(range(len(cs)))
    kc = prov.get("key", {}).get("key_color", "#C22E7E")
    key = tuple(int(kc[i:i + 2], 16) for i in (1, 3, 5))
    ms = medir(cs, key)
    u = usos(anim) if con_usos else {}
    box = union_box(cs)
    tw = round((box[2] - box[0]) * H / (box[3] - box[1]))
    cw = max(tw, 236)            # la columna: el cuadro centrado y lugar para los textos
    rows = 3 if rosa else 2
    wrap = {i: textwrap.wrap(t, max(20, cw // 8)) for i, t in (nota or {}).items()}
    lab = 66 + 18 * max([len(w) for w in wrap.values()] + [1])
    n = len(cs)
    nr = -(-n // COLS)
    f1, f2, ft = font(17, True), font(15), font(24, True)
    W = min(n, COLS) * (cw + 12) + 12
    blockh = rows * (H + 4) + lab
    s = Image.new("RGB", (W, 70 + nr * blockh), (245, 245, 245))
    d = ImageDraw.Draw(s)
    d.text((12, 10), titulo, fill=(0, 0, 0), font=ft)
    d.text((12, 42), "arriba verde, al medio oscuro" + (", abajo el color del fondo que quedó, en amarillo" if rosa else "")
           + ".  nit: nitidez relativa (< 0,7 borroso)  rosa: px del fondo  dx: corrimiento de los pies, px de 1x",
           fill=(60, 60, 60), font=f2)
    for i, c in enumerate(cs):
        x, y = 12 + (i % COLS) * (cw + 12), 70 + (i // COLS) * blockh
        tx = x + (cw - tw) // 2
        s.paste(tile(c, box, GREEN, H), (tx, y))
        s.paste(tile(c, box, DARK, H), (tx, y + H + 4))
        if rosa:
            s.paste(tile(c, box, (245, 245, 245), H, ms[i]["pink_mask"]), (tx, y + 2 * (H + 4)))
        m = ms[i]
        ty = y + rows * (H + 4) + 2
        d.text((x, ty), f"cuadro {i} · nativo {natives[i] if i < len(natives) else '?'}", fill=(0, 0, 0), font=f1)
        bad = m["nit"] < 0.7
        d.text((x, ty + 20), f"nit {m['nit']:.2f}", fill=(200, 0, 0) if bad else (40, 40, 40), font=f2)
        d.text((x + 70, ty + 20), f"rosa {m['pink']}", fill=(200, 0, 0) if m["pink"] > 25 else (40, 40, 40), font=f2)
        d.text((x + 150, ty + 20), f"dx {m['dx']:+.0f}", fill=(200, 0, 0) if abs(m["dx"]) > 12 else (40, 40, 40), font=f2)
        if i in u:
            d.text((x, ty + 40), "juego: " + ", ".join(u[i]), fill=(170, 0, 0), font=f2)
        for k, line in enumerate(wrap.get(i, [])):
            d.text((x, ty + 60 + 18 * k), line, fill=(0, 90, 170), font=f2)
    dest.parent.mkdir(parents=True, exist_ok=True)
    s.save(dest)
    return ms


def hoja_juego(out: Path, anim: str, dest: Path, titulo: str, natives: list[int] | None = None) -> None:
    cs = cells(out, "0.5x", anim)
    natives = natives or provenance(out, anim).get("timing", {}).get("native_indices") or list(range(len(cs)))
    box = union_box(cs, 3)
    h = round((box[3] - box[1]) * GAME_K)
    tw = round((box[2] - box[0]) * GAME_K)
    n = len(cs)
    cols = min(n, 13)
    nr = -(-n // cols)
    f1, ft = font(15, True), font(20, True)
    s = Image.new("RGB", (12 + cols * (tw + 8), 44 + nr * (2 * h + 30)), DARK)
    d = ImageDraw.Draw(s)
    d.text((12, 10), titulo, fill=(240, 240, 240), font=ft)
    for i, c in enumerate(cs):
        x, y = 12 + (i % cols) * (tw + 8), 44 + (i // cols) * (2 * h + 30)
        for k, bg in enumerate((GREEN, DARK)):
            im = Image.new("RGBA", (c.shape[1], c.shape[0]), (*bg, 255))
            im.alpha_composite(Image.fromarray(c, "RGBA"))
            s.paste(im.crop(box).resize((tw, h), Image.BILINEAR).convert("RGB"), (x, y + k * h))
        d.text((x, y + 2 * h + 4), f"{i} · n{natives[i] if i < len(natives) else '?'}", fill=(240, 240, 240), font=f1)
    s.save(dest)


def tinte(c: np.ndarray) -> float:
    """Azul − verde del anillo de afuera de lo opaco menos el de adentro: cuánto fondo magenta quedó en el contorno."""
    op = (c[..., 3] > 128).astype(np.uint8)
    if op.sum() < 100:
        return float("nan")
    ring = (op == 1) & (cv2.erode(op, np.ones((3, 3), np.uint8)) == 0)
    inner = cv2.erode(op, np.ones((9, 9), np.uint8)) > 0
    rgb = c[..., :3].astype(np.float32)
    bg = lambda m: float((rgb[m][:, 2] - rgb[m][:, 1]).mean())  # noqa: E731
    return bg(ring) - bg(inner)


def comparar(antes: Path, ahora: Path, picks: list[tuple[str, int]], dest: Path, titulo: str) -> None:
    th, zk = 300, 3
    f1, f2, ft = font(17, True), font(15), font(22, True)
    rows = []
    piv = lambda o: json.loads((o / "lowpoly.json").read_text(encoding="utf-8"))["variants"]["1x"]["pivot_px"]  # noqa: E731
    pa, pb = piv(antes), piv(ahora)
    for anim, i in picks:
        ca, cb = cells(antes, "1x", anim)[i], cells(ahora, "1x", anim)[i]
        if ca.shape != cb.shape:   # canvas distintos: el de antes, corrido para que los pies (el pivot) coincidan
            full = np.zeros_like(cb)
            oy, ox = round(pb["y"] - pa["y"]), round(pb["x"] - pa["x"])
            h, w = min(ca.shape[0], cb.shape[0] - oy), min(ca.shape[1], cb.shape[1] - ox)
            full[oy:oy + h, ox:ox + w] = ca[:h, :w]
            ca = full
        box = union_box([ca, cb])
        ys, xs = np.nonzero(cb[..., 3] > 128)
        # el detalle: el cuarto de abajo a la derecha del personaje (el arma y las botas, donde más se veía el borde)
        cx, cy = int(xs.mean()), int(ys.mean())
        det = (cx - 10, cy - 10, cx + 90, cy + 90)
        tiles = [tile(ca, box, DARK, th), tile(cb, box, DARK, th)]
        for c in (ca, cb):
            im = Image.new("RGBA", (c.shape[1], c.shape[0]), (*DARK, 255))
            im.alpha_composite(Image.fromarray(c, "RGBA"))
            tiles.append(im.crop(det).resize((100 * zk, 100 * zk), Image.NEAREST).convert("RGB"))
        rows.append((anim, i, tiles, tinte(ca), tinte(cb)))
    W = 12 + max(sum(t.width + 10 for t in r[2]) for r in rows) + 10
    s = Image.new("RGB", (W, 60 + len(rows) * (th + 34)), (245, 245, 245))
    d = ImageDraw.Draw(s)
    d.text((12, 10), titulo, fill=(0, 0, 0), font=ft)
    d.text((12, 38), "antes · ahora · detalle antes · detalle ahora (×3, px de 1x). tinte: azul − verde del contorno contra"
           " el de adentro", fill=(60, 60, 60), font=f2)
    for k, (anim, i, tiles, ta, tb) in enumerate(rows):
        x, y = 12, 60 + k * (th + 34)
        for t in tiles:
            s.paste(t, (x, y + (th - t.height) // 2))
            x += t.width + 10
        d.text((12, y + th + 6), f"{anim} {i}", fill=(0, 0, 0), font=f1)
        d.text((200, y + th + 8), f"tinte {ta:.0f} → {tb:.0f}", fill=(40, 40, 40), font=f2)
    dest.parent.mkdir(parents=True, exist_ok=True)
    s.save(dest)


def tira(spec: dict, dest: Path, out: Path = HERE / "out") -> None:
    cache: dict[tuple[Path, str], list[np.ndarray]] = {}

    def get(a: str, o: Path = out) -> list[np.ndarray]:
        return cache.setdefault((o, a), cells(o, "0.5x", a))

    outs = [HERE / f["out"] if f.get("out") else out for f in spec["filas"]]
    boxes = {o: union_box([get(q[0], o)[q[1]] for f, fo in zip(spec["filas"], outs) if fo == o for q in f["cuadros"]], 6)
             for o in set(outs)}   # una caja por corrida (los canvas pueden ser distintos); la escala es la misma (0,5×)
    side = max(max(b[2] - b[0], b[3] - b[1]) for b in boxes.values())   # cuadrado: lo girado entra
    k = GAME_K
    tw = round(side * k)
    f1, f2, ft = font(15, True), font(13), font(22, True)
    n = max(len(f["cuadros"]) for f in spec["filas"])
    rowh = tw + 70
    s = Image.new("RGB", (12 + n * (tw + 6), 50 + len(spec["filas"]) * rowh), (245, 245, 245))
    d = ImageDraw.Draw(s)
    d.text((12, 10), spec["titulo"], fill=(0, 0, 0), font=ft)
    for r, (fila, fo) in enumerate(zip(spec["filas"], outs)):
        y = 50 + r * rowh
        d.text((12, y), fila["titulo"], fill=(0, 0, 0), font=f1)
        t_ms = 0
        for j, q in enumerate(fila["cuadros"]):
            anim, i, ms = q[0], q[1], q[2]
            lab = q[3] if len(q) > 3 else ""
            rot = q[4] if len(q) > 4 else 0
            c = get(anim, fo)[i]
            im = Image.new("RGBA", (c.shape[1], c.shape[0]), (0, 0, 0, 0))
            im.alpha_composite(Image.fromarray(c, "RGBA"))
            box = boxes[fo]
            cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
            sq = im.crop((round(cx - side / 2), round(cy - side / 2), round(cx + side / 2), round(cy + side / 2)))
            if rot:
                ys, xs = np.nonzero(np.array(sq)[..., 3] > 20)
                sq = sq.rotate(-rot, resample=Image.BICUBIC, center=((xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2))
            bg = Image.new("RGBA", sq.size, (*DARK, 255))
            bg.alpha_composite(sq)
            x = 12 + j * (tw + 6)
            s.paste(bg.resize((tw, tw), Image.BILINEAR).convert("RGB"), (x, y + 20))
            short = {"idle_combat": "idle", "double_jump": "dj", "double_jump_fix": "djf", "throw_fix": "tf",
                     "double_jump_in": "dj_in", "double_jump_ball": "ball", "double_jump_out": "dj_out"}.get(anim, anim)
            d.text((x, y + 22 + tw), f"{short} {i}" + (f"  {rot:+.0f}°" if rot else ""), fill=(0, 0, 0), font=f1)
            d.text((x, y + 40 + tw), f"{t_ms} ms {lab}", fill=(150, 0, 0) if lab else (60, 60, 60), font=f2)
            t_ms += ms
    dest.parent.mkdir(parents=True, exist_ok=True)
    s.save(dest)


# --- nativos: una config de prueba con todos los cuadros de un tramo ------------------------------------------------

def _val(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        return "[" + ", ".join(_val(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{k} = {_val(x)}" for k, x in v.items()) + " }"
    raise TypeError(v)


def _abs(d: dict, root: Path) -> dict:
    o = {}
    for k, v in d.items():
        if k in PATH_KEYS and isinstance(v, str) and (root / v).exists():
            v = str((root / v).resolve())
        o[k] = v
    return o


def nativos(config: Path, anim: str, a: int, b: int, work: Path, key: dict | None = None) -> Path:
    cfg = tomllib.loads(config.read_text(encoding="utf-8"))
    cfg.setdefault("key", {}).update(key or {})
    root = config.parent
    anims = {x["name"]: x for x in cfg["animation"]}
    clips = {x["name"]: x for x in cfg.get("clip", [])}
    src = dict(anims[anim])
    ref = cfg["character"].get("scale_reference")
    lines = []
    for sec in ("character", "key", "output"):
        if sec in cfg:
            t = _abs(cfg[sec], root)
            if sec == "output":
                t["work_dir"], t["out_dir"] = str(work / "work"), str(work / "out")
            lines += [f"[{sec}]"] + [f"{k} = {_val(v)}" for k, v in t.items()] + [""]
    if "output" not in cfg:
        lines += ["[output]", f"work_dir = {_val(str(work / 'work'))}", f"out_dir = {_val(str(work / 'out'))}", ""]
    need = {src["clip"]} | ({anims[ref]["clip"]} if ref in anims else set())
    for name in need & clips.keys():
        lines += ["[[clip]]"] + [f"{k} = {_val(v)}" for k, v in _abs(clips[name], root).items()] + [""]
    if ref in anims and ref != anim:
        lines += ["[[animation]]"] + [f"{k} = {_val(v)}" for k, v in _abs(anims[ref], root).items()] + [""]
    for k in ("trim", "frames", "loop", "trim_static_tail", "pick", "loop_start", "loop_length", "loop_seconds",
              "skip_seconds", "reverse"):
        src.pop(k, None)
    src.update(name=anim, kind="oneshot", frames=list(range(a, b + 1)))
    lines += ["[[animation]]"] + [f"{k} = {_val(v)}" for k, v in _abs(src, root).items()] + [""]
    work.mkdir(parents=True, exist_ok=True)
    p = work / f"{anim}_{a}-{b}.toml"
    p.write_text("\n".join(lines), encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "spritepipe.cli", "run", str(p)], cwd=REPO, capture_output=True, text=True)
    if not (work / "out" / "sheets" / "1x" / f"{anim}.json").exists():
        print(r.stdout[-3000:], r.stderr[-3000:])
        raise SystemExit(f"spritepipe no armó {anim} (exit {r.returncode})")
    return work / "out"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("hoja", help="hoja cuadro por cuadro de animaciones del atlas")
    h.add_argument("anims", nargs="+")
    h.add_argument("--out", type=Path, default=HERE / "out")
    h.add_argument("--sufijo", default="", help="agregado al nombre del archivo (p. ej. _antes)")
    h.add_argument("--notas", type=Path, help="JSON {anim: {cuadro: nota}}: lo que se vio en cada cuadro, en azul")
    c = sub.add_parser("comparar", help="cuadros de dos corridas del atlas, lado a lado sobre oscuro")
    c.add_argument("antes", type=Path, help="el out/ de antes (una copia)")
    c.add_argument("cuadros", nargs="+", metavar="ANIM:CUADRO")
    c.add_argument("--ahora", type=Path, default=HERE / "out")
    c.add_argument("--nombre", default="comparar")
    c.add_argument("--titulo", default="antes y ahora, sobre oscuro")
    t = sub.add_parser("tira", help="una secuencia como la juega la arena, desde un JSON")
    t.add_argument("spec", type=Path)
    n = sub.add_parser("nativos", help="todos los nativos de un tramo del clip de una animación")
    n.add_argument("anim")
    n.add_argument("desde", type=int)
    n.add_argument("hasta", type=int)
    n.add_argument("--config", type=Path, default=HERE / "character.toml")
    n.add_argument("--work", type=Path, default=HERE / "work_revisar")
    n.add_argument("--key", action="append", default=[], metavar="CLAVE=VALOR",
                   help="pisar un valor de [key] para probarlo (p. ej. --key edge_unmix=true)")
    args = ap.parse_args()
    rev = HERE / "revision"
    if args.cmd == "tira":
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        tira(spec, args.spec.with_suffix(".png"))
        print(args.spec.with_suffix(".png"))
    elif args.cmd == "comparar":
        picks = [(a, int(i)) for a, i in (x.rsplit(":", 1) for x in args.cuadros)]
        comparar(args.antes, args.ahora, picks, rev / f"{args.nombre}.png", args.titulo)
        print(rev / f"{args.nombre}.png")
    elif args.cmd == "hoja":
        notas = json.loads(args.notas.read_text(encoding="utf-8")) if args.notas else {}
        for anim in args.anims:
            nota = {int(k): v for k, v in notas.get(anim, {}).items()}
            ms = hoja(args.out, anim, rev / f"{anim}_cuadros{args.sufijo}.png", f"{anim}: cuadro por cuadro (atlas 1x)",
                      nota=nota, con_usos=args.out.resolve() == (HERE / "out").resolve())   # RIG es del atlas del juego
            hoja_juego(args.out, anim, rev / f"{anim}_juego{args.sufijo}.png", f"{anim} a tamaño de juego (0,5× × 1,6)")
            for i, m in enumerate(ms):
                print(f"{anim:12s} {i:3d}  nit {m['nit']:.2f}  rosa {m['pink']:4d}  dx {m['dx']:+5.1f}  "
                      f"dy {m['dy']:+4d}  cabeza {m['dhead']:+5.1f}")
    else:
        key = {k: tomllib.loads(f"v = {v}")["v"] for k, v in (kv.split("=", 1) for kv in args.key)}
        tag = "".join(f"_{k}" for k in key)
        out = nativos(args.config, args.anim, args.desde, args.hasta,
                      args.work / f"{args.anim}_{args.desde}-{args.hasta}{tag}", key)
        nat = list(range(args.desde, args.hasta + 1))
        dest = rev / f"{args.anim}_nativos_{args.desde}-{args.hasta}{tag}.png"
        ms = hoja(out, args.anim, dest, f"{args.anim}: nativos {args.desde}–{args.hasta} (para elegir frames)", nat,
                  con_usos=False)
        hoja_juego(out, args.anim, dest.with_name(dest.stem + "_juego.png"), f"{args.anim}: nativos a tamaño de juego", nat)
        for i, m in enumerate(ms):
            print(f"nativo {nat[i]:3d}  nit {m['nit']:.2f}  rosa {m['pink']:4d}  dx {m['dx']:+5.1f}  cabeza {m['dhead']:+5.1f}")
        print(dest)


if __name__ == "__main__":
    main()
