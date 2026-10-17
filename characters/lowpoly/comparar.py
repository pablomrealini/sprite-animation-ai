"""Página para comparar las estrategias del bake-off del idle (y del run): compare.html en la carpeta del personaje.

Por clip: el clip tal cual (sobre magenta), el clip recortado sobre verde, la hoja de cuadros a 12 fps sobre verde
(para revisarlo cuadro por cuadro), la tira de torsos y los números de `medir_torso.py`. Lee la lista de clips de
`comparar.toml`.

Uso (desde la raíz del repo):

    uv run --project pipeline python characters/lowpoly/comparar.py characters/lowpoly/comparar.toml
"""

from __future__ import annotations

import html
import json
import os
import sys
import tomllib
from pathlib import Path

import cv2
import numpy as np

from spritepipe import chroma, imgio

GREEN = np.array([0, 255, 0], np.float32)



def fal_matrix(info: dict) -> str | None:
    """fal entrega los videos en BT.601 sin tag (con BT.709 el rojo se corre a naranja); si el video trae tag, se usa."""
    return None if info.get("color_space") else "bt601"

def keyed_green(frames: np.ndarray) -> list[np.ndarray]:
    """El personaje sobre verde: alfa por distancia al color del borde (ΔE 12 → 0, ΔE 32 → 1)."""
    key = chroma.border_color(frames[0].astype(np.float32)) / 255.0
    out = []
    for f in frames:
        x = f.astype(np.float32) / 255.0
        d = chroma.estimate_alpha(x, key, method="distance") * chroma.DISTANCE_SCALE
        a = np.clip((d - 12) / 20, 0, 1)[..., None]
        out.append((f * a + GREEN * (1 - a)).round().astype(np.uint8))
    return out


def bbox(frames: list[np.ndarray], pad: int = 16) -> tuple[int, int, int, int]:
    """Unión de los bbox del componente más grande de cada cuadro (el ruido del fondo no cuenta)."""
    m = np.zeros(frames[0].shape[:2], bool)
    for f in frames[::3]:
        fg = (np.abs(f.astype(int) - GREEN.astype(int)).sum(-1) > 120).astype(np.uint8)
        n, lab, st, _ = cv2.connectedComponentsWithStats(fg, connectivity=8)
        if n > 1:
            big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
            x, y, w, h = st[big, :4]
            m[y:y + h, x:x + w] = True
    ys, xs = np.nonzero(m)
    h, w = m.shape
    return max(0, xs.min() - pad), max(0, ys.min() - pad), min(w, xs.max() + pad), min(h, ys.max() + pad)


def contact_sheet(frames: list[np.ndarray], step: int, cols: int = 12) -> np.ndarray:
    picked = frames[::step]
    h, w = picked[0].shape[:2]
    rows = -(-len(picked) // cols)
    sheet = np.full((rows * (h + 18), cols * w, 3), 255, np.uint8)
    for i, f in enumerate(picked):
        r, c = divmod(i, cols)
        sheet[r * (h + 18) + 18:r * (h + 18) + 18 + h, c * w:(c + 1) * w] = f
        cv2.putText(sheet, str(i * step), (c * w + 3, r * (h + 18) + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                    (0, 0, 0), 1, cv2.LINE_AA)
    return sheet


def process(clip: Path, out: Path, name: str) -> dict:
    info = imgio.probe(clip)
    vid, sheet = out / f"{name}_verde.mp4", out / f"{name}_cuadros.png"
    if all(p.exists() and p.stat().st_mtime > clip.stat().st_mtime for p in (vid, sheet)):  # ya armado
        return {"verde": vid, "cuadros": sheet, "frames": info["nb_frames"] or round(info["duration"] * info["fps"]),
                "fps": info["fps"], "size": f"{info['width']}×{info['height']}"}
    frames = imgio.read_video(clip, info, fal_matrix(info))
    green = keyed_green(frames)
    x0, y0, x1, y1 = bbox(green)
    crop = [g[y0:y1, x0:x1] for g in green]
    imgio.encode_rgb_video([np.ascontiguousarray(c[: c.shape[0] // 2 * 2, : c.shape[1] // 2 * 2]) for c in crop],
                           vid, info["fps"], crf=16)
    step = max(1, round(info["fps"] / 12))
    small = [cv2.resize(c, (c.shape[1] // 2, c.shape[0] // 2), interpolation=cv2.INTER_AREA) for c in crop]
    imgio.save(sheet, contact_sheet(small, step))
    return {"verde": vid, "cuadros": sheet, "frames": len(frames), "fps": info["fps"],
            "size": f"{info['width']}×{info['height']}"}


def main(cfg_path: Path) -> None:
    cfg = tomllib.loads(cfg_path.read_text(encoding="utf-8"))
    root = cfg_path.parent
    out = root / cfg.get("out_dir", "compare")
    out.mkdir(parents=True, exist_ok=True)
    page = root / cfg.get("page", "compare.html")
    torso = {}
    for tj in cfg.get("torso", []):
        data = json.loads((root / tj).read_text(encoding="utf-8"))
        for c in data["clips"]:
            clip = Path(c["clip"])  # relativa a donde se corrió medir_torso: la raíz del repo o la del personaje
            clip = next((q for q in (clip, root / clip, Path.cwd() / clip) if q.exists()), clip)
            torso[clip.resolve()] = (c, data["between"].get(c.get("name") or clip.stem, {}))

    def rel(p: Path) -> str:
        return html.escape(os.path.relpath(Path(p).resolve(), page.parent.resolve()))

    sections = []
    for grp in cfg["group"]:
        cards = []
        for c in grp["clips"]:
            clip = (root / c["file"]).resolve()
            name = c.get("name") or clip.stem
            if not clip.exists():
                cards.append(f'<div class="card missing"><h3>{html.escape(name)}</h3><p>sin clip</p></div>')
                continue
            p = process(clip, out, name)
            # los clips de C con el arma pegada se miden sin arma: los números son los del clip original
            t, btw = torso.get(clip) or torso.get(
                clip.with_name(clip.name.replace("_arma", "").replace("_sin_rayos", "")), (None, {}))
            nums = ""
            if t:
                # la otra toma de la misma estrategia y modelo (_1 ↔ _2): ¿inventan lo mismo?
                me = t.get("name") or Path(t["clip"]).stem
                sib = me[:-1] + {"1": "2", "2": "1"}.get(me[-1], me[-1])
                btw_mean = f"{btw[sib]:.1f}" if sib in btw else "–"
                nums = (f"<table><tr><th>cuadro 0 vs pose</th><td>{t['frame0_mad']}</td></tr>"
                        f"<tr><th>torso ΔE mediana / p95</th><td>{t['de_median']} / {t['de_p95']}</td></tr>"
                        f"<tr><th>torso cambiado mediana / p95</th><td>{t['changed_median']:.1%} / {t['changed_p95']:.1%}</td></tr>"
                        f"<tr><th>movimiento del torso p95</th><td>{t['move_p95']} px de la pose</td></tr>"
                        + (f"<tr><th>colores ajenos a la hoja</th><td>{t['alien_median']:.1%} (pose {t['alien_pose']:.1%})</td></tr>"
                           if "alien_median" in t else "")
                        + f"<tr><th>contra la otra toma (ΔE torso medio)</th><td>{btw_mean}</td></tr></table>")
                if t.get("strip"):
                    strip = Path(t["strip"])
                    strip = next((q for q in (strip, root / strip, Path.cwd() / strip) if q.exists()), strip)
                    nums += f'<img class="strip" src="{rel(strip)}" alt="torsos">'
            note = f'<p class="note">{html.escape(c["note"])}</p>' if c.get("note") else ""
            cards.append(
                f'<div class="card"><h3>{html.escape(name)}</h3>'
                f'<div class="vids"><video src="{rel(clip)}#t=0.05" preload="auto" controls loop muted playsinline></video>'
                f'<video src="{rel(p["verde"])}" controls loop muted autoplay playsinline></video></div>'
                f'<p class="meta">{p["size"]}, {p["frames"]} cuadros a {p["fps"]:g} fps · '
                f'<a href="{rel(p["cuadros"])}">cuadro por cuadro (12 fps, verde)</a></p>{note}{nums}</div>')
        desc = f'<p>{html.escape(grp.get("desc", ""))}</p>' if grp.get("desc") else ""
        sections.append(f'<section><h2>{html.escape(grp["title"])}</h2>{desc}<div class="grid">{"".join(cards)}</div></section>')

    intro = "".join(f"<p>{html.escape(x)}</p>" for x in cfg.get("intro", []))
    page.write_text(f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(cfg.get("title", "Comparación"))}</title>
<style>
:root{{--bg:#f4f4f2;--fg:#1d1d1b;--mut:#6b6b66;--card:#fff;--line:#ddd}}
@media (prefers-color-scheme: dark){{:root{{--bg:#1b1b1a;--fg:#ecece8;--mut:#a0a09a;--card:#252524;--line:#3a3a38}}}}
body{{margin:0;padding:16px;font:15px/1.45 system-ui,sans-serif;background:var(--bg);color:var(--fg)}}
h1{{font-size:22px}} h2{{font-size:18px;margin-top:28px}} h3{{margin:0 0 6px;font-size:15px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:14px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px;min-width:0}}
.vids{{display:grid;grid-template-columns:1fr 1fr;gap:6px}} video{{width:100%;background:#000;border-radius:4px}}
.meta,.note{{color:var(--mut);font-size:13px;margin:6px 0}}
table{{border-collapse:collapse;font-size:13px;margin:6px 0}} th{{text-align:left;font-weight:500;color:var(--mut);padding:2px 10px 2px 0}}
td{{font-variant-numeric:tabular-nums}} .strip{{width:100%;image-rendering:auto;margin-top:4px}}
.refs img{{height:180px;margin-right:8px;background:#c0c3cc;border-radius:4px}}
@media (max-width:480px){{.grid{{grid-template-columns:1fr}}}}
</style></head><body>
<h1>{html.escape(cfg.get("title", "Comparación"))}</h1>{intro}
<div class="refs">{"".join(f'<img src="{rel(root / r)}" alt="ref">' for r in cfg.get("refs", []))}</div>
{"".join(sections)}
</body></html>
""", encoding="utf-8")
    print(f"✓ {page}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
