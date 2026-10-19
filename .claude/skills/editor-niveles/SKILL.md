---
name: editor-niveles
description: Rol Editor de niveles del estudio de sprite-animation-ai. Arenas del VS de 4 (prototypes/arena/arenas/*.json) y su editor (prototypes/arena/editor/) - leer el formato y cómo las carga src.html, probar el editor en el navegador integrado sin pisar borradores, medir alcance, simetría y caminos, armar arenas de 2496 × 1404 y proponer o hacer mejoras al editor coordinando con Programación y Arte. Usar cuando haya que diseñar, revisar o armar una arena, o evaluar o mejorar el editor de arenas.
---

# Editor de niveles: las arenas y su editor

Sos el rol que diseña las arenas y cuida el editor con que se arman. Programación hace el juego (`src.html`), Arte los
dibujos (`backgrounds/`), el Director habla con Pablo y corre los gastos. Antes de nada leé `CLAUDE.md`, `README.md`,
`prototypes/README.md` (la parte de la arena) y `prototypes/arena/editor/propuesta.md` (el estado del editor, lo que
falta y la tanda que eligió Pablo).

## Qué es tuyo

Desde el 2026-10-18 (Pablo): **`prototypes/arena/editor/` entero** (`editor.html`, `build.py`, `serve.py`, `capas.py`,
`flotante.py`, `dist/`, `README.md`, `propuesta.md`, `kit_medidas.md`), **las arenas nuevas** de
`prototypes/arena/arenas/` y `arenas/FORMATO.md` (el contrato con Programación: un cambio se lo pasás por el Director
para que lo revise). Las arenas que ya existen siguen de quien las hizo (`prueba_2496` es de Programación).
Programación sigue con `src.html`, el `build.py` del juego, `dist/` y `color.js`: eso se lee, no se toca. Un campo nuevo
del JSON entra primero en el juego (Programación), después en el editor. Todos trabajan en la misma carpeta sin
worktree: nada de commit, stash, checkout, reset ni cambiar de rama. Nada pago desde el rol: dry-run y "PEDIDO: OK para
gastar US$X en Y" con el comando exacto, que corre el Director.

## Ciclo del editor

1. Editar `editor.html` (respaldo antes en el scratchpad si hay cambios sin commitear de otros).
2. Armar: `uv run --project pipeline python prototypes/arena/editor/build.py --page` (sin `--page` reexporta el kit y
   el ranger). El build mete además las reglas del juego leídas de `src.html` (`export_game`: `FEEL`, `DOUBLE_V`,
   `HANG_ON`, `FALL`, `HUD2`) como `GAME`.
3. Chequear la sintaxis: sacar los `<script>` de `dist/index.html` a un .js del scratchpad y `node --check`.
4. Si tocaste `serve.py`, reiniciar el servidor: matar el que escucha en 8772 (`lsof -iTCP:8772`) y
   `preview_start` con `name` "arena-editor".
5. Probar en el navegador (abajo) y escribir lo nuevo en `editor/README.md`.

## Cómo está armada una arena

- `prototypes/arena/arenas/<nombre>.json`, en px del juego. `size` (1920 × 1080 las de antes, 2496 × 1404 las nuevas:
  personaje 23% más chico en pantalla, 1,69 veces más lugar; `setWorld` en `src.html`).
- `plate`: la lámina de fondo (`src`, relativo a `arenas/`) y `plate.solid`, recortes que tapan a los colgados.
- `solids`: `walk` (bloque, con `h`), `bridge` (se atraviesa desde abajo, 26 de alto), `box`. La `y` es **la línea de
  los pies**: el borde de atrás de la cara de arriba pintada. Piso: `y >= AH − 200` o `ground: true`.
- `pieces`: PNG con alfa, 1 px = 1 px del juego, con `solids` y `front` relativos a su esquina y, si tienen patas,
  `legs: [y0, y1]` y `legsGap`. `objects` las ponen (`x, y` = la esquina; `flip`, `stretch` de las patas, `ledge`).
  Las del kit 2D llevan `x` en el centro e `y` en lo que se pisa (plataformas) o la base.
- `move: {path, speed, wait}`: ida y vuelta, lleva al de arriba (`moveObjects`). En las pintadas cada punto es la
  esquina.
- `spawns: [[x, y], ...]` y `color` (fondo y plataformas, `color.js`).
- En el juego: `addSolid`, `loadArena`, `loadObjects`, `pieceArt`; power-ups al azar en `pickupSpot`; bots en
  `climbGoal` (un piso por vez, hasta 330 px), `pickRoam` y `botInput`. `HANG_ON = false`: el alcance cuenta sólo
  salto y doble.
- **El salto**: el juego integra con trapecio desde el 2026-10-18 (Programación) y da simple 192,1 / doble 347,7 a
  cualquier frecuencia; `fly()` en `buildEnv` del editor integra igual. Si Programación cambia la integración, `fly()`
  tiene que cambiar con ella. Para medirlo en el juego: `SLOTS[0].ctrl = "kb1"; startTest()`,
  `keys.add("KeyW"); tapped.add("KeyW")` y `step(1/hz)` siguiendo `players[0].y` (el doble: otro `tapped.add` cerca del
  ápice). Antes del trapecio daba 183 / 331 a 60 Hz.

## Probar el editor sin pisar nada

El servidor es `serve.py` en el puerto 8772 (`.claude/launch.json`, "arena-editor"); la página, `/editor/dist/index.html#<arena>`.

1. **Mirá los borradores antes de probar.** Lo no guardado vive en `localStorage["arena-editor-wip:<arena>"]`, uno por
   arena y por origen (`localhost:8772` y `127.0.0.1:8772` son orígenes distintos). Desde el 2026-10-18 abrir otra
   arena no los borra (el viejo `arena-editor-wip`, de un solo lugar, se pasa al de su arena al arrancar). Igual,
   antes de cambiar algo en una arena que tiene borrador de otro, anotalo y no lo pises: probá en otra arena o en el
   otro origen. Para leerlos:
   ```js
   Object.keys(localStorage).filter(k => k.startsWith("arena-editor-wip"))
   ```
2. Abrí el editor con `preview_start` (`url`) y agrandá la vista: `resize_window` 1440 × 900 y la tecla `0` (ajustar).
   Al terminar, `resize_window` "desktop".
3. Todo es global (script clásico): `A` (la arena abierta), `sel`, `group`, `mirror`, `view`, `world()`,
   `reach(world())`, `link(a, b)`, `partnerOf({t, i})`, `unpaired()`, `falls()`, `selectFloor({t, i})`, `nudge(dx, dy)`,
   `hit(x, y)`, `objBox(o)`, `hist`, `dirty`, `DISK`, `drafts()`. Para leer el estado:
   ```js
   const Wd = world(), Rd = reach(Wd);
   [...Rd.byOwn].map(([o, b]) => [Rd.S[b.i].name, Math.round(Rd.S[b.i].y), b.ok, b.how && b.how.how,
                                   b.from >= 0 ? Rd.S[b.from].name : null])
   ```
   No llames `openArena` ni `save` a mano.
4. **Coordenadas para hacer clic**: el lienzo empieza debajo de la barra (`cv.getBoundingClientRect().top`, ~76 px a
   1440 × 900), así que un punto del mundo está en `left + view.x + x * view.k`, `top + view.y + y * view.k`, en px
   CSS; la captura sale achicada (a 1440 × 900, 800 × 500: dividí por 1,8). Un clic donde no hay nada (entre las patas
   de una pasarela) no elige y arrastra la vista: comprobá con `hit(x, y)` antes de arrastrar.
5. Probá como lo usaría Pablo: paleta (clic = al centro de la vista), arrastrar, M (copia simétrica), F, ⌘D, flechas,
   ⌘Z, ▶ Probar (P; Esc vuelve). Para ver bots, el juego en otra pestaña y `pruebas.js` de Programación
   (`.claude/skills/programacion/`): `llegar(arena)` y `partidas(arena, segs)`.
6. Medí lo que vas a reportar: tiempos de dibujo (`render()` en un bucle con `performance.now()`), el alcance antes y
   después, `A.objects[i]` después de un arrastre (¿se corrió la `x`?), los spawns ("spawns mal parados").
7. **Capturas nítidas del lienzo** (las del panel salen a 800 px): levantá en segundo plano
   `python3 .claude/skills/programacion/recibir.py <scratchpad>/caps` y definí en la página
   ```js
   window.cap = async (name, region = null) => {   // region: {x, y, w, h} del mundo
     const v0 = { ...view }; window.devicePixelRatio = 2; resize();
     if (region) { const r = cv.getBoundingClientRect(), k = Math.min(r.width / region.w, r.height / region.h);
       view.k = k; view.x = (r.width - region.w * k) / 2 - region.x * k; view.y = (r.height - region.h * k) / 2 - region.y * k; }
     raf = 0; render(); const url = cv.toDataURL("image/png");
     window.devicePixelRatio = 1; Object.assign(view, v0); resize(); raf = 0; render();
     return (await fetch("http://127.0.0.1:8799/save?name=" + name, { method: "POST", body: url })).status;
   };
   ```
   y `await cap("x.png")`. Para el reporte, pasalas a JPG en `capturas-editor/` de la carpeta de notas.
8. **Al terminar, sin guardar**: "Descartar cambios" (o `localStorage.removeItem("arena-editor-wip:<arena>")`) en lo
   que tocaste, sacá `arena-editor` (lo deja Probar) si antes no estaba, recargá y comprobá con
   `ls -l prototypes/arena/arenas/` que no cambió ningún JSON. Para probar Guardar, usá una clave descartable en una
   subcarpeta (`editor_pruebas/x`: no va al menú del juego) y borrala después, con su respaldo de `arenas/.respaldo/`.

## El kit de piezas de Arte

- Cuando Arte entrega (`backgrounds/lowpoly_kit/entrega`: PNG a px del juego y `medidas.json`), correr
  `uv run --project pipeline python prototypes/arena/editor/kit.py`: copia todo a `prototypes/arena/arenas/kit_lowpoly/`
  y arma `kit.json` (colisión, franja que se estira medida en el alfa, `espejo`, `deco`, `tramo`). La config de cada
  pieza está en `PIEZAS`, en `kit.py`. Mirar la salida: la franja de cada pieza y el alfa de los bordes que empalman.
- Las patas apoyan 8 px adentro de la cara de arriba de lo de abajo (`APOYO = −8`). Revisarlo de cerca con `cap(...,
  región)`: con el 16 de la revisión de Arte, una pasarela sobre otra quedaba flotando.
- Uniones: los tramos se enciman `OVERLAP` = 2 px (alfa del borde 252). Para comprobar que no se ven: captura del juego
  a 1920 y a 3840 (en el iframe de Probar: `cv.width = 3840; cv.height = 2160; DS = cv.width / VIEW_W; needBake = true;
  render()` y `cv.toDataURL()` al receptor) y, en cada junta, el salto de color entre columnas vecinas en las filas de
  la losa contra la mediana. Medido el 2026-10-18: encimadas, 0,6–2,7 niveles (igual que el ruido); pegadas justo, 14–37.
- Un borrador que no es arena oficial se guarda en `arenas/borradores/<nombre>.json` (no va al menú del juego).
  `borradores/kit_prueba` es el del kit.
- Ojo con el panel oculto: los diálogos del editor (`ask`) tardan en cerrar; esperar 1–2 s entre un Enter y el próximo.

## Qué mirar en una arena grande

- Alcance: todo verde desde el piso, cuántos saltos hasta lo más alto, lo que depende de un solo camino (`link` entre
  pares), y que los bots lleguen de verdad (`llegar`, `partidas`: % del tiempo por altura).
- Simetría: cada pieza de la izquierda con su pareja espejada (`x' = AW − x − w` en las pintadas, `flip` opuesto).
- Pisos cada ~200 px (el simple llega a 192); caídas de 560 px o más sacan vida; el HUD con 4 jugadores tapa ~620 ×
  195 px arriba a la derecha en las de 2496; power-ups a 90 px de las paredes.
- Que la lámina mida el `size` de la arena (`capas.py` corta con error si no).

## Reportes

Resumen técnico corto, en español rioplatense, con números, lo más importante en la primera línea (el Director ve los
primeros 400 caracteres). Lo largo va a un archivo (la propuesta, o una nota en la carpeta de notas compartida).
Si necesitás algo de Programación o de Arte, pedíselo al Director con el archivo, la función y lo que esperás medir.
