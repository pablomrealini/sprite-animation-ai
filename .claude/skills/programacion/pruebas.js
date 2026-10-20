// Pruebas de la arena sin mirar: pegar entero en el javascript_tool del navegador integrado, con la página del juego
// abierta (http://localhost:8772/dist/index.html, o la del http.server de 8767). Deja en window: listo(), cadencia(),
// llegar(arena), partidas(arena, segs), alto(), hoja(escena, tomas, acciones, gx, gy, gw), guardar(nombre) y caer(y0, x). Todo corre en tiempo de juego (step(1/60)), no en tiempo real.
// Ojo: cambia SLOTS, SET y la arena del menú de esa pestaña; recargar después para jugar normal.

// espera a que cargue, apaga el bucle de requestAnimationFrame (si no, el juego sigue andando entre una llamada y otra)
// y junta los errores de la página
window.listo = async () => {
  await new Promise(r => { const w = () => (typeof ready !== "undefined" && ready && artState === "ok") ? r() : setTimeout(w, 200); w(); });
  tick = () => {}; await new Promise(r => setTimeout(r, 100));
  window.__errs = []; window.addEventListener("error", e => window.__errs.push(e.message));
  // el panel cambia de tamaño al sacar una captura y resize() borra el lienzo: volver a dibujar
  window.addEventListener("resize", () => { resize(); render(); });
  return { char: CHAR_KEY, arena: ARENA.name };
};

// tiros por segundo reales y en qué tiro se traba el arma, a 60/120/144 Hz (teclado izquierdo: F una mano, G dos)
window.cadencia = () => {
  const out = [], origPush = Array.prototype.push; let shots = [], simT = 0;
  bullets.push = function (...a) { shots.push(simT); return origPush.apply(this, a); };
  const run = (key, hz, secs, noHeat) => {
    SLOTS[0].ctrl = "kb1"; startTest(); G.toast = null; G.pickT = 999;
    const Q = players[0]; for (let i = 0; i < 40; i++) step(1 / 60);
    const h = { ...HEAT }; if (noHeat) { HEAT.shot1 = 0; HEAT.shot2 = 0; }
    shots = []; keys.add(key); let over = null;
    for (let i = 0; i < secs * hz; i++) { simT = i / hz; step(1 / hz); if (Q.overheat && !over) over = [shots.length, shots[shots.length - 1] - shots[0]]; }
    keys.clear(); Object.assign(HEAT, h);
    const span = shots[shots.length - 1] - shots[0];
    return `${key} ${hz} Hz: ${((shots.length - 1) / span).toFixed(2)}/s` + (over ? `, se traba en el tiro ${over[0]} a los ${over[1].toFixed(2)} s` : "");
  };
  for (const hz of [60, 120, 144]) out.push(run("KeyF", hz, 4, true), run("KeyG", hz, 4, true));
  out.push(run("KeyF", 60, 1.5, false), run("KeyG", 60, 1.5, false));
  bullets.push = origPush;
  return out;
};

// ¿los bots llegan a cada superficie? Un bot sale del piso (6 lugares) y el otro jugador queda parado arriba,
// invulnerable; cuenta cuántas veces llega en 10 s
window.llegar = (arena, N = 6) => {
  loadArena(arena);
  const ground = solids.find(s => s.ground), rows = []; let ok = 0, n = 0;
  for (const s of solids.filter(s => !s.bound && !s.ground && !(s.obj && s.obj.path) && s.w >= 50)) {
    let k2 = 0;
    for (let k = 0; k < N; k++) {
      SLOTS[0].ctrl = "bot"; SLOTS[1].ctrl = "kb2"; SLOTS[2].ctrl = "off"; SLOTS[3].ctrl = "off"; SET.lives = 99; startMatch();
      for (let i = 0; i < 100; i++) step(1 / 60);
      const Q = players[0], T = players[1];
      resetPlayer(Q, [150 + (k / (N - 1)) * (AW - 300), ground.y]); resetPlayer(T, [s.x + s.w / 2, s.y], 999);
      Q.bot = newBot(); G.pickT = 999; pickups.length = 0;
      for (let t = 0; t < 10; t += 1 / 60) {
        T.x = s.x + s.w / 2; T.y = s.y; T.vx = T.vy = 0; T.onGround = true; T.invT = 999;
        step(1 / 60);
        if (Q.onGround && supportAt(Q.x, Q.y, Q) === s) { k2++; break; }
      }
    }
    ok += k2; n += N; rows.push(`${s.kind} y${s.y} x${Math.round(s.x)}-${Math.round(s.x + s.w)} (sube ${ground.y - s.y}): ${k2}/${N}`);
  }
  return { total: `${ok}/${n}`, rows };
};

// partidas de 4 bots con vidas de sobra: subidas por minuto, bajas por minuto, trabados (3 s en 40 px queriendo
// moverse), cuadros colgados y % del tiempo por altura
window.partidas = (arena, secs = 300) => {
  loadArena(arena); SLOTS.forEach(s => s.ctrl = "bot"); SET.count = 4; SET.lives = 99; SET.hp = 3; startMatch();
  const st = { hang: 0, ups: 0, lv: {}, stuck: 0 }, last = new Map(), still = new Map();
  for (let i = 0; i < secs * 60; i++) {
    step(1 / 60); if (G.state !== "play") continue;
    for (const Q of players) {
      if (!Q.alive) { last.delete(Q); still.delete(Q); continue; }
      if (Q.state === "hang" || Q.state === "climb") st.hang++;
      const k = still.get(Q) || { x: Q.x, y: Q.y, t: 0 };
      if (Math.abs(Q.x - k.x) < 40 && Math.abs(Q.y - k.y) < 40 && (Q.in.left || Q.in.right)) { if ((k.t += 1 / 60) > 3) { st.stuck++; k.t = -999; } } else { k.x = Q.x; k.y = Q.y; k.t = 0; }
      still.set(Q, k);
      const s = Q.onGround && supportAt(Q.x, Q.y, Q); if (!s) continue;
      const lv = s.ground ? "piso" : String(Math.round(s.y / 50) * 50); st.lv[lv] = (st.lv[lv] || 0) + 1;
      const p = last.get(Q); if (p && p.y - s.y > 30) st.ups++; last.set(Q, s);
    }
  }
  const tot = Object.values(st.lv).reduce((a, b) => a + b, 0), m = secs / 60;
  return `${arena}: ${(st.ups / m).toFixed(1)} subidas/min, ${(players.reduce((a, p) => a + p.kills, 0) / m).toFixed(1)} bajas/min, trabados ${st.stuck}, cuadros colgado ${st.hang}, % por altura ` +
    Object.entries(st.lv).sort().map(([k, v]) => `${k}:${Math.round(100 * v / tot)}`).join(" ") + `, errores ${window.__errs?.length ?? "?"}`;
};
// mirar un efecto: momentos (en s desde que arranca la escena) de una región del juego (gx, gy y gw de ancho, en px del
// juego, 16:9) en una grilla de 2 × 2 sobre el lienzo. tomas: [[t, rótulo], ...]; acciones: [[t, fn], ...] (apretar o
// soltar teclas: keys es lo mantenido, tapped los toques). alto() pone el lienzo a 1920 × 1080 (sin retina sale borroso)
// y guardar(nombre) manda la hoja a recibir.py (las capturas del panel oculto salen viejas y chicas)
window.alto = () => { cv.width = 1920; cv.height = 1080; DS = cv.width / VIEW_W; needBake = true; };
window.hoja = (escena, tomas, acciones, gx, gy, gw) => {
  const k = DS * W2S, gh = gw * 9 / 16, W = cv.width / 2, H = cv.height / 2, out = document.createElement("canvas"); out.width = cv.width; out.height = cv.height;
  const og = out.getContext("2d"); let t = 0, ai = 0; escena(); const acts = (acciones || []).slice().sort((a, b) => a[0] - b[0]);
  tomas.forEach(([tt, rot], i) => {
    while (t < tt - 1e-6) { while (ai < acts.length && acts[ai][0] <= t + 1e-6) acts[ai++][1](); step(1 / 60); t += 1 / 60; }
    render(); og.drawImage(cv, gx * k, gy * k, gw * k, gh * k, (i % 2) * W, Math.floor(i / 2) * H, W, H);
    og.fillStyle = "#000"; og.font = "bold 30px sans-serif"; og.fillText(rot, (i % 2) * W + 12, Math.floor(i / 2) * H + 36);
  });
  keys.clear(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.drawImage(out, 0, 0); window.__hoja = out;
};
window.addEventListener("resize", () => { if (window.__hoja) { alto(); ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.drawImage(window.__hoja, 0, 0, cv.width, cv.height); } });
window.guardar = async (nombre, c = window.__hoja || cv) =>
  (await fetch(`http://127.0.0.1:${window.RECIBIR || 8799}/save?name=${nombre}`, { method: "POST", headers: { "Content-Type": "text/plain" }, body: c.toDataURL("image/png") })).status;
// una caída: el jugador 4 suelto en el aire en (x, y0) como si viniera de pisar y0 (FALL se mide desde ahí). Devuelve la
// vida antes y después, el tipo de aterrizaje y el texto que sube. Ej.: caer(340) en la Refinería low-poly saca 1
window.caer = (y0, x = 1100, extra = {}) => {
  SLOTS[0].ctrl = "kb1"; SLOTS[1].ctrl = "off"; SLOTS[2].ctrl = "off"; SLOTS[3].ctrl = "kb2"; SET.hp = 3; startMatch();
  for (let i = 0; i < 110; i++) step(1 / 60); G.pickT = 999; labels.length = 0;
  const D = players[3]; Object.assign(D, { x, y: y0, onGround: false, vy: 0, vx: 0, fallY0: y0, state: "air", jump: { mode: "phys", fixed: true }, peakY: y0 }, extra);
  const hp0 = D.hp; for (let i = 0; i < 180 && !D.onGround; i++) step(1 / 60);
  return { cae: Math.round(D.y - y0), hp: `${hp0}→${D.hp}`, aterrizaje: D.landKind, texto: labels[0]?.text ?? null };
};
"listas: await listo(); cadencia(); llegar('refineria_lowpoly'); partidas('refineria_lowpoly', 300); caer(340); alto(); hoja(escena, [[0.1, 'a'], [0.2, 'b'], [0.4, 'c'], [0.7, 'd']], [], 940, 800, 320); await guardar('x.png')";
