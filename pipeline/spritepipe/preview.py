"""Visor HTML local para revisar un personaje: todas las animaciones en loop con su timing real,
pivot, línea de piso, flipX, onion skin y fondos. Se abre con doble clic (file://); los datos
van embebidos y los PNG se cargan por ruta relativa."""

from __future__ import annotations

import json
from pathlib import Path

TEMPLATE = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
:root { --bg:#f4f4f2; --panel:#fff; --ink:#1c1c1c; --muted:#6b6b6b; --line:#dcdcd8; --accent:#d1495b; }
@media (prefers-color-scheme: dark) { :root { --bg:#151515; --panel:#1f1f1f; --ink:#ececec; --muted:#9a9a9a; --line:#333; --accent:#ff6b7d; } }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font:14px/1.4 system-ui, -apple-system, sans-serif; }
header { position:sticky; top:0; z-index:2; background:var(--panel); border-bottom:1px solid var(--line);
  padding:10px 16px; display:flex; flex-wrap:wrap; gap:8px 18px; align-items:center; }
h1 { font-size:16px; margin:0 12px 0 0; }
label { color:var(--muted); display:inline-flex; gap:6px; align-items:center; }
select, button { font:inherit; color:var(--ink); background:var(--bg); border:1px solid var(--line); border-radius:6px; padding:3px 8px; }
button { cursor:pointer; }
main { padding:16px; display:grid; gap:16px; grid-template-columns:repeat(auto-fill, minmax(260px, 1fr)); }
.card { background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:10px; }
.card h2 { font-size:14px; margin:0 0 6px; display:flex; justify-content:space-between; }
.card h2 span { color:var(--muted); font-weight:400; }
.stage { overflow:auto; border-radius:6px; }
canvas { display:block; margin:auto; image-rendering:pixelated; }
.meta { color:var(--muted); font-size:12px; margin-top:6px; font-variant-numeric:tabular-nums; }
</style>
</head>
<body>
<header>
  <h1>__TITLE__</h1>
  <label>Escala <select id="variant"></select></label>
  <label>Zoom <select id="zoom"><option>1</option><option selected>2</option><option>3</option><option>4</option><option>6</option></select></label>
  <label>Fondo <select id="bgsel"><option value="checker">damero</option><option value="#202020">oscuro</option><option value="#e8e8e8">claro</option><option value="#6a8f3c">pasto</option></select></label>
  <label><input type="checkbox" id="pivot" checked> pivot y piso</label>
  <label><input type="checkbox" id="flip"> flipX</label>
  <label><input type="checkbox" id="onion"> onion skin</label>
  <button id="play">Pausa</button>
  <button id="step">Paso</button>
</header>
<main id="grid"></main>
<script>
const DATA = __DATA__;
const $ = id => document.getElementById(id);
let playing = true, cards = [], images = [];
const variantSel = $('variant');
Object.keys(DATA.variants).forEach(v => variantSel.add(new Option(v, v)));

function checker(ctx, w, h, s) {
  for (let y = 0; y < h; y += s) for (let x = 0; x < w; x += s) {
    ctx.fillStyle = ((x / s + y / s) & 1) ? '#c9c9c9' : '#f0f0f0'; ctx.fillRect(x, y, s, s);
  }
}

function build() {
  const V = DATA.variants[variantSel.value];
  images = V.pages.map(src => { const im = new Image(); im.src = src; return im; });
  const grid = $('grid'); grid.innerHTML = ''; cards = [];
  for (const [name, anim] of Object.entries(V.animations)) {
    const card = document.createElement('div'); card.className = 'card';
    const total = anim.frames.reduce((a, f) => a + f.duration, 0);
    card.innerHTML = `<h2>${name}<span>${anim.frames.length} frames · ${anim.loop ? 'loop' : 'una pasada'}</span></h2>
      <div class="stage"><canvas></canvas></div><div class="meta"></div>`;
    grid.appendChild(card);
    cards.push({ anim, name, canvas: card.querySelector('canvas'), meta: card.querySelector('.meta'),
                 i: 0, t: 0, total, V });
  }
}

function draw(c) {
  const z = +$('zoom').value, V = c.V, cw = V.canvas.w, ch = V.canvas.h;
  const cv = c.canvas; if (cv.width !== cw * z) { cv.width = cw * z; cv.height = ch * z; }
  const ctx = cv.getContext('2d'); ctx.imageSmoothingEnabled = DATA.style !== 'pixel';
  const bg = $('bgsel').value;
  if (bg === 'checker') checker(ctx, cv.width, cv.height, 8 * z); else { ctx.fillStyle = bg; ctx.fillRect(0, 0, cv.width, cv.height); }
  const flip = $('flip').checked;
  const paint = (f, alpha) => {
    ctx.save(); ctx.globalAlpha = alpha;
    if (flip) { ctx.translate(cv.width, 0); ctx.scale(-1, 1); }
    ctx.drawImage(images[f.page], f.x, f.y, f.w, f.h, f.ox * z, f.oy * z, f.w * z, f.h * z);
    ctx.restore();
  };
  if ($('onion').checked && c.anim.frames.length > 1) {
    const prev = c.anim.frames[(c.i - 1 + c.anim.frames.length) % c.anim.frames.length];
    paint(prev, 0.3);
  }
  paint(c.anim.frames[c.i], 1);
  if ($('pivot').checked) {
    const px = V.pivot.x * z, py = V.pivot.y * z;
    ctx.strokeStyle = getComputedStyle(document.body).getPropertyValue('--accent');
    ctx.lineWidth = 1; ctx.beginPath();
    ctx.moveTo(0, py + 0.5); ctx.lineTo(cv.width, py + 0.5);
    ctx.moveTo(px + 0.5, py - 6 * z); ctx.lineTo(px + 0.5, py + 3 * z); ctx.stroke();
  }
  const f = c.anim.frames[c.i];
  c.meta.textContent = `frame ${c.i + 1}/${c.anim.frames.length} · ${f.duration} ms · ciclo ${Math.round(c.total)} ms · celda ${cw}×${ch}`;
}

let last = performance.now();
function tick(now) {
  const dt = now - last; last = now;
  for (const c of cards) {
    if (playing && c.hold > 0) {  // una pasada: se queda en el último frame y repite para revisar
      c.hold -= dt; if (c.hold <= 0) { c.i = 0; c.t = 0; }
    } else if (playing) {
      c.t += dt;
      while (c.t >= c.anim.frames[c.i].duration) {
        c.t -= c.anim.frames[c.i].duration;
        if (c.i < c.anim.frames.length - 1) c.i++;
        else if (c.anim.loop) c.i = 0;
        else { c.hold = 700; c.t = 0; break; }
      }
    }
    draw(c);
  }
  requestAnimationFrame(tick);
}
variantSel.onchange = build;
$('play').onclick = () => { playing = !playing; $('play').textContent = playing ? 'Pausa' : 'Play'; };
$('step').onclick = () => { playing = false; $('play').textContent = 'Play';
  cards.forEach(c => { c.i = (c.i + 1) % c.anim.frames.length; c.t = 0; }); };
build(); requestAnimationFrame(tick);
</script>
</body>
</html>
"""


def write(out: Path, title: str, data: dict) -> None:
    html = TEMPLATE.replace("__TITLE__", title).replace("__DATA__", json.dumps(data, ensure_ascii=False))
    out.write_text(html, encoding="utf-8")
