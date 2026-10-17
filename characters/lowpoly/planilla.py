"""Planilla del set de la arena: el ranger del juego y el low-poly lado a lado, clip por clip (planilla.html).

Lee planilla.toml (los clips, su estado y notas) y los índices de los dos atlas (out/<personaje>.json) para saber qué
animaciones existen y a qué escala. Cada preview (el APNG de out/previews/1x/) se muestra con el cuerpo al mismo alto
en pantalla, así se comparan diseño y movimiento, no resolución: el ranger sale a 128 px de cuerpo y el low-poly a 256.

Uso (desde la raíz del repo):

    uv run --project pipeline python characters/lowpoly/planilla.py
"""

from __future__ import annotations

import html
import json
import os
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHARS = ROOT.parent
BODY_PX = 150  # alto del cuerpo en pantalla, para los dos personajes
ESTADOS = {"hecho": "Hecho", "a rehacer": "A rehacer", "listo": "Listo para generar", "falta pose": "Falta la pose",
           "descartado": "Descartado"}


def atlas(name: str) -> dict:
    out = CHARS / name / "out"
    idx = json.loads((out / f"{name}.json").read_text(encoding="utf-8"))
    prov = json.loads((out / "provenance.json").read_text(encoding="utf-8"))
    v = idx["variants"]["1x"]
    target = tomllib.loads(prov["config"])["character"]["target_height"]  # la config va como texto en la procedencia
    return {"out": out, "canvas": v["canvas"], "anims": set(v["animations"]), "target": target}


def rel(p: Path) -> str:
    return html.escape(os.path.relpath(p, ROOT))


def preview(ch: dict, anim: str, k: float) -> str:
    p = ch["out"] / "previews" / "1x" / f"{anim}.png"
    if anim not in ch["anims"] or not p.exists():
        return f'<div class="pv empty" style="width:{round(ch["canvas"]["w"] * k)}px"><span>{html.escape(anim)}</span></div>'
    w, h = round(ch["canvas"]["w"] * k), round(ch["canvas"]["h"] * k)
    return (f'<figure class="pv"><img src="{rel(p)}" width="{w}" height="{h}" alt="{html.escape(anim)}">'
            f'<figcaption>{html.escape(anim)}</figcaption></figure>')


def main() -> None:
    cfg = tomllib.loads((ROOT / "planilla.toml").read_text(encoding="utf-8"))
    ranger, low = atlas("ranger"), atlas("lowpoly")
    kr, kl = BODY_PX / (ranger["target"] or 128), BODY_PX / (low["target"] or 256)
    clips = cfg["clip"]
    rows, total_usd = [], 0.0
    counts = {e: 0 for e in ESTADOS}
    for c in clips:
        counts[c["estado"]] = counts.get(c["estado"], 0) + 1
        total_usd += c.get("usd", 0)
        pose = (f'<img class="pose" src="{rel(ROOT / c["pose"])}" alt="pose">' if c.get("pose") and (ROOT / c["pose"]).exists()
                else '<div class="pose empty">sin pose todavía</div>')
        meta = [f'<b>Ranger:</b> {html.escape(c["ranger"])}', f'<b>Config:</b> <code>{html.escape(c["config"])}</code>']
        if c.get("tomas"):
            meta.append(f'<b>Tomas:</b> {c["tomas"]} · US$ {c.get("usd", 0):.2f}'.replace(".", ","))
        nota = f'<p class="nota">{html.escape(c["nota"])}</p>' if c.get("nota") else ""
        if c.get("revision"):
            nota += f'<p class="nota rev"><b>Revisión de Pablo:</b> {html.escape(c["revision"])}</p>'
        links = [f'<a href="{rel(ROOT / "cuadros" / f"{a}.png")}">{html.escape(a)}</a>' for a in c["anims"]
                 if (ROOT / "cuadros" / f"{a}.png").exists()]
        if links:
            meta.append("<b>Cuadro a cuadro:</b> " + " · ".join(links))
        rows.append(f'''<section class="clip {c["estado"].replace(" ", "-")}">
  <header><h2>{html.escape(c["name"])}</h2><span class="estado">{ESTADOS.get(c["estado"], c["estado"])}</span></header>
  <div class="cols">
    <div><h3>Ranger (juego actual)</h3><div class="strip">{"".join(preview(ranger, a, kr) for a in c["anims"])}</div></div>
    <div><h3>Low-poly</h3><div class="strip">{"".join(preview(low, a, kl) for a in c["anims"])}</div></div>
    <div class="side"><h3>Pose de arranque</h3>{pose}<p class="meta">{"<br>".join(meta)}</p>{nota}</div>
  </div>
</section>''')
    n_anims = sum(len(c["anims"]) for c in clips)
    done = sum(len(c["anims"]) for c in clips if c["estado"] == "hecho")
    resumen = " · ".join(f"{ESTADOS[e]}: {n}" for e, n in counts.items() if n)
    page = ROOT / "planilla.html"
    page.write_text(f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Planilla del set low-poly</title>
<style>
:root{{--bg:#f4f4f2;--fg:#1d1d1b;--mut:#6b6b66;--card:#fff;--line:#ddd;--ok:#2f7d4a;--go:#2d5fa8;--wait:#9a6a12;--off:#888;--stage:#c9ccd4}}
@media (prefers-color-scheme: dark){{:root{{--bg:#1b1b1a;--fg:#ecece8;--mut:#a0a09a;--card:#252524;--line:#3a3a38;--ok:#5fbf7f;--go:#7aa7e8;--wait:#d6a54a;--off:#999;--stage:#3a3d44}}}}
body{{margin:0;padding:16px;font:15px/1.45 system-ui,sans-serif;background:var(--bg);color:var(--fg)}}
h1{{font-size:22px;margin:0 0 4px}} .sub{{color:var(--mut);margin:0 0 16px}}
.clip{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px;margin:0 0 14px}}
.clip header{{display:flex;align-items:center;gap:10px;margin-bottom:8px}} h2{{font-size:17px;margin:0}} h3{{font-size:13px;color:var(--mut);margin:0 0 6px;font-weight:500}}
.estado{{font-size:12px;padding:2px 8px;border-radius:10px;border:1px solid currentColor}}
.hecho .estado{{color:var(--ok)}} .a-rehacer .estado{{color:#c0392b}} .listo .estado{{color:var(--go)}} .falta-pose .estado{{color:var(--wait)}} .descartado .estado{{color:var(--off)}}
.cols{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr) 260px;gap:14px}}
.strip{{display:flex;gap:8px;overflow-x:auto;background:var(--stage);border-radius:6px;padding:8px;min-height:{round(BODY_PX * 1.3)}px;align-items:flex-end}}
.pv{{margin:0;display:flex;flex-direction:column;align-items:center;flex:none}} .pv img{{display:block}}
.pv figcaption{{font-size:11px;color:var(--mut);margin-top:2px}}
.pv.empty{{height:{round(BODY_PX * 1.2)}px;border:1px dashed var(--line);border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:11px;color:var(--mut)}}
.pose{{width:100%;border-radius:4px;display:block}} div.pose.empty{{height:120px;border:1px dashed var(--line);display:flex;align-items:center;justify-content:center;color:var(--mut);font-size:12px}}
.meta,.nota{{font-size:12px;color:var(--mut);margin:6px 0 0}} .rev{{color:var(--fg)}} code{{font-size:11px}}
@media (max-width:900px){{.cols{{grid-template-columns:1fr}}}}
</style></head><body>
<h1>Planilla del set low-poly</h1>
<p class="sub">Los {len(clips)} clips de la arena ({n_anims} animaciones; {done} hechas en low-poly). {resumen}. Las tomas del set costaron US$ {total_usd:.2f} (aparte, el bake-off de estrategias del idle: US$ 9,00, en compare.html).
Los dos personajes se muestran con el cuerpo a {BODY_PX} px en pantalla: el ranger sale a {ranger["target"]} px y el low-poly a {low["target"]}.</p>
{"".join(rows)}
</body></html>
""".replace("US$ " + f"{total_usd:.2f}", "US$ " + f"{total_usd:.2f}".replace(".", ",")), encoding="utf-8")
    print(f"✓ {page}: {len(clips)} clips, {done}/{n_anims} animaciones hechas")


if __name__ == "__main__":
    main()
