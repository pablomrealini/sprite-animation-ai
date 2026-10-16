# Meter los props de ranger_props en el prototipo del ranger

El 2026-10-16 se eligieron 17 props, que son 22 piezas. Las opciones de cada uno están en `PICKED`, en `build_page.py`. Lo que necesita el juego quedó en `picked.json`: por pieza, el PNG de `post/`, su `k` (px del juego por px de la hoja), el tamaño en px del juego, el papel en el nivel y los puntos medidos (lo opaco sin el halo, el hueco del ventilador, el vano de la puerta, la pantalla del monitor y la chispa). Están en px de la hoja; multiplicados por `k` dan px del juego. `props.html` muestra el nivel de hoy con todo ubicado como propone este plan.

**La fase 1 ya está aplicada** (2026-10-16, sin commitear) en `prototypes/build.py`, `prototypes/ranger/src.html` y `prototypes/README.md`, con el código de las secciones 1 y 2. Las fases 2 y 3 faltan. Dos ubicaciones cambiaron respecto del primer borrador, para no molestar en la chimenea ni en la plataforma nueva: la baliza del bloque alto pasó a x = 3722 (en 3618 quedaba justo donde termina de subir el ranger) y el cartel grande a x = 4370 (en 4330 rozaba la punta de la plataforma de 4125). Las coordenadas se tomaron de `prototypes/ranger/src.html` al 2026-10-16, con los cambios sin commitear: el mundo mide 5000 px, tiene la chimenea en 3300/3590 y la plataforma de 4125. Si el nivel cambia, hay que actualizar `LEVEL` y `PLAN` en `build_page.py` y volver a correrlo, así la vista sigue mostrando lo mismo que el juego.

## El criterio: qué va adelante y qué va al fondo

El commit `49de359` sacó las cajas porque "no hacían nada": estaban en el plano del ranger, parecían obstáculos y no chocaban. Por eso cada prop tiene un papel (`role` en `picked.json`):

| papel | props | cómo se dibuja | por qué |
|---|---|---|---|
| `back` | barrel, cable_coil, console, fuel_tank, turret_off, crate_stack, antenna, signboard | Detrás de todo lo jugable, a la velocidad del mundo, con un tinte violeta del 35% (`rgba(24,18,52,0.35)`, el color de `NEAR_TINT` con menos fuerza). No chocan ni frenan balas. | Son voluminosos y no hacen nada. Teñidos se leen como fondo y no como obstáculo. |
| `fixture` | beacon, monitor, panel_spark, drone | En el plano del juego, detrás del ranger, como los carteles. Se animan. | Son chicos y fijos (en un poste, en una base, arriba de un bloque), así que no se leen como obstáculo. Son lo que le da vida al nivel. |
| `face` | fan (marco y aspas) | En la cara de un bloque, después de dibujar los bloques. | Si no, el bloque lo tapa. |
| `target` | explosive_barrel, crate_breakable | Blancos nuevos del sistema de `targets`. | Tienen función: se rompen. |
| `gate` | switch, door (marco y hoja) | La hoja es un sólido que corta el paso; el interruptor es un blanco. | Mecánica nueva: cambia el recorrido. |

El barril común va al fondo, al lado del explosivo, a propósito: así se aprende que el rojo es el que se rompe.

## Fases

1. **Sólo arte, sin cambiar el juego**: `back`, `fixture` y `face`, con sus animaciones. Riesgo bajo, porque nada choca y nada se puede disparar.
2. **Blancos nuevos**: el barril explosivo y la caja rompible. Usan el mismo sistema que los tableros y las latas (hp, tinte al impacto, burst, vuelven a los 3 s).
3. **Puerta con interruptor**: cambia el recorrido. Hay que decidirla junto con el diseño del nivel.

## 1. `prototypes/build.py`

Una línea en `BACKGROUNDS` y un bloque en `export_backgrounds`. Las piezas se exportan a `dist/bg/<pieza>.png`, y ninguna se llama igual que las del kit o los props de la base.

```python
BACKGROUNDS = {
    "ranger": {
        ...
        "sheets": {...},
        "deco": "ranger_props",   # backgrounds/ranger_props/picked.json: los props elegidos, cada uno con su k
    },
}
```

```python
    # al final de export_backgrounds, antes del return
    if "deco" in cfg:   # props sueltos de otro set: cada pieza con su k, su papel y sus puntos (en px de la hoja)
        dset = ROOT / "backgrounds" / cfg["deco"]
        data["deco"] = {}
        for piece, p in json.loads((dset / "picked.json").read_text())["pieces"].items():
            export_image(dset / p["file"], bg / f"{piece}.png", p["k"] * EXPORT)
            data["deco"][piece] = {key: v for key, v in p.items() if key not in ("file", "sheet", "option")} | {"src": f"bg/{piece}.png"}
```

## 2. `prototypes/ranger/src.html`, fase 1

**Carga y bake.** Hay que sumar `BG.deco` a `bgFiles` y `deco: {}` a `baked`. En `bake()`, después de los props:

```js
const BACK_TINT = "rgba(24,18,52,0.35)";   // al lado de NEAR_TINT: el decorado de fondo, hacia el violeta del cielo
const bgFiles = [...new Set([BG.layers, BG.kit, BG.props, BG.deco || {}].flatMap(o => Object.values(o).map(p => p.src)))];
```

```js
  // utilería de ranger_props: cada pieza a su tamaño; la de fondo, teñida (las aspas ya vienen al hueco del marco)
  for (const [name, A] of Object.entries(BG.deco || {})) {
    const [c, g] = surface(px(A.w), px(A.h)); g.drawImage(IMG[A.src], 0, 0, c.width, c.height);
    baked.deco[name] = A.role === "back" ? tinted(c, BACK_TINT) : c;
  }
```

**Dónde va cada uno.** Va al lado de `props`, en "mundo". `x` es el centro y `y` la base. En los ventiladores, `y` es el tope del bloque en cuya cara van, y el marco arranca debajo del tope del kit:

```js
// utilería de backgrounds/ranger_props (BG.deco): sólo se dibuja. back va detrás de todo lo jugable y teñida
const deco = [];
const put = (name, x, y = GROUND) => deco.push({ name, x, y, i: deco.length });
put("antenna", 120); put("cable_coil", 232); put("console", 385); put("monitor", 548);
put("beacon", 1055, GROUND - 84); put("barrel", 1122); put("beacon", 1400, GROUND - 196); put("panel_spark", 1512);
put("fuel_tank", 1680); put("drone", 1885); put("fan", 2195, GROUND - 230); put("crate_stack", 2350);
put("turret_off", 2730); put("beacon", 3030, GROUND - 250); put("beacon", 3722, GROUND - 370);
put("fan", 3665, GROUND - 370); put("signboard", 4370);
const BACK = new Set(["antenna", "cable_coil", "console", "barrel", "fuel_tank", "crate_stack", "turret_off", "signboard"]);
```

**El dibujo.** Una pieza se apoya por lo opaco, para que el halo de la baliza no la levante:

```js
let clock = 0;   // en finishUpdate: clock += dt (con la cámara lenta, la utilería también va lenta)
// arriba a la izquierda de la pieza, en px del mundo, con lo opaco (sin el halo) centrado en x y apoyado en y
function decoPiece(name, x, y) {
  const A = BG.deco[name], X = x - (A.solid[0] + A.solid[2]) / 2 * A.k, Y = y - A.solid[3] * A.k;
  drawBaked(baked.deco[name], Math.round(X - camX), Math.round(Y)); return [X, Y, A];
}
function drawDeco(d) {
  if (d.x - camX < -160 || d.x - camX > VW() + 160) return;
  if (d.name === "beacon") decoPiece(Math.floor(clock * 2 + d.i) % 2 ? "beacon_off" : "beacon_on", d.x, d.y);
  else if (d.name === "monitor") {
    // estática: 2,8 s prendida, con la pantalla espejada al azar cada 80 ms, y 0,4 s apagada
    if ((clock + d.i) % 3.2 > 2.8) return decoPiece("monitor_off", d.x, d.y);
    const [X, Y, M] = decoPiece("monitor_static", d.x, d.y), [a, b, w, h] = M.screen.map(v => v * M.k), f = Math.floor(clock / 0.08);
    ctx.save(); ctx.translate(Math.round(X - camX) + a + w / 2, Math.round(Y) + b + h / 2); ctx.scale(f % 2 ? -1 : 1, (f >> 1) % 2 ? -1 : 1);
    ctx.drawImage(baked.deco.monitor_static, a * bakeDS, b * bakeDS, w * bakeDS, h * bakeDS, -w / 2, -h / 2, w, h); ctx.restore();
  } else if (d.name === "fan") {
    const H = BG.deco.fan_housing, B = BG.deco.fan_blades, top = d.y + KIT.topH * BG.kit.top.k + 8;
    const [X, Y] = decoPiece("fan_housing", d.x, top + (H.solid[3] - H.solid[1]) * H.k);
    ctx.save(); ctx.translate(Math.round(X - camX) + H.hole[0] * H.k, Math.round(Y) + H.hole[1] * H.k); ctx.rotate(clock * Math.PI * 1.8 + d.i);
    drawBaked(baked.deco.fan_blades, -B.w / 2, -B.h / 2); ctx.restore();
  } else decoPiece(d.name, d.x, d.y);
}
```

Las chispas del tablero se generan en `finishUpdate`, con el `burst()` que ya existe:

```js
  clock += dt;
  for (const d of deco) if (d.name === "panel_spark" && clock > (d.next || 0)) {
    const A = BG.deco.panel_spark, sx = d.x + (A.spark[0] - (A.solid[0] + A.solid[2]) / 2) * A.k, sy = d.y + (A.spark[1] - A.solid[3]) * A.k;
    burst(sx, sy, "#9ff5fa", 6, 160, 0.3, 3); burst(sx, sy, "#ffffff", 3, 120, 0.2, 2); d.next = clock + 0.6 + Math.random() * 1.4;
  }
```

**El orden en `render()`.** La utilería de fondo va antes que todo lo jugable, y el ventilador va después de los bloques:

```js
  if (bgState === "ok") drawGround();
  for (const d of deco) if (BACK.has(d.name)) drawDeco(d);                       // nuevo
  for (const p of props) drawProp(p);
  for (const d of deco) if (!BACK.has(d.name) && d.name !== "fan") drawDeco(d);   // nuevo
  const behind = ready && P.state === "hang";
  if (behind) drawSprite();
  for (const s of solids) if (!s.ground) drawSolid(s);
  for (const d of deco) if (d.name === "fan") drawDeco(d);                        // nuevo
  for (const T of targets) drawTarget(T);
```

## 3. Fase 2: blancos nuevos

```js
function xbarrel(x, y) { const A = BG.deco.explosive_barrel; targets.push({ kind: "xbarrel", x: x - A.w / 2, y: y - A.h, w: A.w, h: A.h, hp: 2, max: 2, hit: 0, dead: 0 }); }
function crate(x, y) { const A = BG.deco.crate_breakable; targets.push({ kind: "crate", x: x - A.w / 2, y: y - A.h, w: A.w, h: A.h, hp: 3, max: 3, hit: 0, dead: 0 }); }
if (BG.deco) { xbarrel(1168, GROUND); xbarrel(4060, GROUND); crate(2560, GROUND); crate(4745, GROUND); }
```

- En `bake()`, el arte de cada uno es su pieza con el tinte del impacto. `drawTarget` ya lo dibuja apoyado en la base:
  `for (const [kind, name] of [["xbarrel", "explosive_barrel"], ["crate", "crate_breakable"]]) if (BG.deco?.[name]) baked.targets[kind] = [baked.deco[name], tinted(baked.deco[name], HIT_TINT)];`
- Al morir, el color de los restos va por tipo: `{ can: "#e8392e", board: "#c79a5a", crate: "#8fa3c4", xbarrel: "#ff8a2a" }`. El barril, además, explota: `burst(cx, cy, "#ffd23f", 20, 420, 0.6, 9)`, `shake = Math.max(shake, 0.18)` y `rumble(140, 0.9, 0.6)`. El daño en área queda para cuando haya enemigos.
- La caja mide 43×28 px y es chica al lado del tablero. Si cuesta acertarle, conviene darle hitbox de más y no agrandar el arte.

## 4. Fase 3: la puerta

Va en x = 3890, con el interruptor en x = 3790. Así queda en el tramo de piso que sigue a la chimenea, antes de la plataforma de 4125. Al bajar del bloque alto se ve la puerta cerrada, y hay que dispararle al interruptor para pasar. La puerta frena las balas, así que el barril de 4060 queda protegido hasta que se abre.

- **La hoja es un sólido** del tamaño del vano: `opening` por `k`, con el marco centrado en x y apoyado en el piso. Tiene `kind: "door"`, y hay que excluirlo de `bake()` (no es un bloque), de `drawSolid` y de la búsqueda de cornisas (`findLedge` y el chequeo de las líneas 411 y 444), para que el ranger no se cuelgue de la puerta.
- **El interruptor es un blanco de un tiro que no vuelve.** Al morir pasa a `switch_on` y abre la puerta: la hoja sube en 0,6 s, recortada al vano y detrás del marco, como en `props.html`. Al terminar, se saca el sólido.
- **El orden:** primero la hoja (con clip al vano), después el marco y después el ranger. Así, al cruzar, el ranger queda delante del marco.

## Lo que hay que saber

- **Grosor del contorno.** Cada hoja tiene su escala, así que los props chicos quedan con una línea de 1 px en el juego (barriles, cable, caja rompible) y los altos con 2 a 2,6 px (puerta, antena), como el kit. Junto con la cámara al 75%, la caja rompible y el cable se ven finos. Si molesta, se regeneran los chicos más grandes en la hoja: `low_a` con dos objetos en lugar de cuatro.
- **El rollo de cable** al fondo y teñido casi no se ve. Si no aporta, se saca.
- **La torreta** mide 87×113, más que el ranger (102). Teñida y al fondo funciona; si se vuelve enemigo, pasa al plano del juego.
- **La baliza prendida** trae su halo rojo dentro del PNG (45×42 contra 30×30 apagada). Por eso se apoya por lo opaco (`solid`), no por el borde del PNG.
- **Animaciones que no están:** la luz de la antena y la del dron no se midieron. Si se quieren, se mide su punto como la chispa (`measure` en `build_page.py`) y se dibuja un halo encima.
