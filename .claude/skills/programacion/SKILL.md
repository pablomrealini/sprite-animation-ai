---
name: programacion
description: Rol Programación del estudio de sprite-animation-ai. Cambios de juego en la arena (prototypes/arena/src.html, build.py, color.js, dist/ y las arenas que ya existen) - reglas, feel, bots, efectos, HUD y animaciones aprobadas - probados sin mirar en el navegador integrado con step(1/60)/render() y bots simulados, y recompilados para que Pablo los pruebe. Usar cuando haya que tocar el código del VS de 4 (el editor de arenas es del rol Editor de niveles).
---

# Programación: la arena y el editor

Sos el rol que toca el juego. Animación genera los clips, Limpieza los deja en `characters/<personaje>/out/`, Arte hace
los dibujos en carpetas nuevas de `backgrounds/`; vos los metés en la arena. Antes de nada leé `CLAUDE.md`, `README.md`
y `prototypes/README.md` (la parte de la arena).

## Qué es tuyo

`prototypes/arena/src.html`, `prototypes/arena/build.py` (el del juego), `prototypes/arena/color.js`,
`prototypes/arena/dist/`, `prototypes/README.md` y las arenas que ya existen en `prototypes/arena/arenas/` (con
`prueba_2496`). Más esta skill. Desde el 2026-10-18 (Pablo), `prototypes/arena/editor/` (editor.html, serve.py, build.py,
capas.py, flotante.py, dist/) y las arenas nuevas son del rol Editor de niveles: no se tocan. Si un cambio del juego
afecta al editor (la física, el formato del JSON de las arenas, `export_kit` o `color_lut` de build.py), avisarle al
Director en el reporte para que se lo pase; el contrato del JSON va a estar en `arenas/FORMATO.md`. Lo demás se lee, no se toca; si necesitás algo de otro, pedíselo al Director en
el reporte. Todos trabajan en la misma carpeta sin worktree: nada de commit, stash, checkout, reset ni cambiar de rama.
En `src.html` puede haber trabajo de otros sin commitear (p. ej. el salto por fases): `git diff` antes de empezar y
editá sólo lo tuyo.

## Cómo está armado `src.html`

Un solo `<script>` clásico: todo es global (`loadArena`, `startTest`, `startMatch`, `step(dt)`, `render()`, `SLOTS`,
`SET`, `players`, `solids`, `G`, `FEEL`, `HEAT`, `PICKUP`…). Las reglas son constantes arriba, cada una con su comentario
y la fecha de lo que pidió Pablo. Lo que se apaga y se puede volver va detrás de un interruptor `const` con comentario:
`CAMERA_FX`, `HANG_ON` (colgarse de cornisas), `HEAD_TAG` (el número sobre la cabeza). Si un interruptor cambia lo que
se puede alcanzar, el editor tiene que decir lo mismo (`HANG_ON` y `PHYS` en `editor/editor.html`). Las notas de
"Reglas de la prueba" en el HTML se actualizan con cada cambio de reglas.

## Ciclo

1. Editar `src.html` (o `build.py`).
2. Recompilar (~17 s):
   ```bash
   uv run --project pipeline python prototypes/arena/build.py
   ```
   El editor, si lo tocaste: `uv run --project pipeline python prototypes/arena/editor/build.py --page`.
3. Probar en el navegador integrado (`preview_start` con `url` http://localhost:8772/dist/index.html si el servidor del
   editor está andando; si no, `python3 -m http.server 8767 --bind 127.0.0.1` desde la raíz). Pegar
   `.claude/skills/programacion/pruebas.js` en `javascript_tool` y llamar `await listo()`: apaga el bucle de
   `requestAnimationFrame` (si no, el juego sigue corriendo entre llamadas). Después, todo en tiempo de juego:
   - `cadencia()`: tiros por segundo reales a 60/120/144 Hz y en qué tiro se traba el arma.
   - `llegar(arena)`: un bot desde el piso hasta cada superficie (cuántas veces llega en 10 s).
   - `partidas(arena, segs)`: 4 bots con vidas de sobra; subidas y bajas por minuto, trabados, % por altura, errores.
   - Casos puntuales: armar el estado a mano (`players[0].hp = 2`, `pickups.push({...})`), `step(1/60)` y mirar.
   - `caer(y0, x)`: una caída desde y0 (el daño por caída, `FALL`).
4. Mirar: con el panel a la vista, `render()` y `computer` screenshot (sale a ~800 px; `zoom` no agranda). Lo que anda
   siempre, también con el panel oculto (ahí las capturas salen viejas): levantar el receptor en segundo plano,
   ```bash
   python3 .claude/skills/programacion/recibir.py <scratchpad>/caps
   ```
   y en la página `alto()` (lienzo a 1920 × 1080), `hoja(escena, tomas, acciones, gx, gy, gw)` (4 momentos de una
   región chica, agrandados) y `await guardar("x.png")`; después `Read` del PNG. Las capturas para el reporte van a la
   carpeta de notas compartida.
5. Recargar la pestaña (`location.reload()`) cuando termines: las pruebas cambian `SLOTS`, `SET` y la arena.

## Trampas conocidas

- La gravedad va con trapecio (`y += (vy_antes + vy_después) / 2 · dt`): con Euler el salto dependía de los Hz de la
  pantalla. Todo lo nuevo que caiga con gravedad (y lo que lo dibuje de antemano, como `arc`), igual. Medir a 60, 120 y
  144 Hz con `step(1/hz)` cuando se toque la física; el editor tiene que integrar igual que el juego.
- El JSON de las arenas: `arenas/FORMATO.md` es el contrato con el editor. Un campo nuevo entra primero en el juego con
  un valor por defecto que deja igual lo que existe; comparar los `solids` de todas las arenas antes y después.
- La cadencia por cuadro: restar `dt` a `fireCD` redondea hacia arriba (a 60 fps, 1/6 s caía en 11 cuadros). Ya está
  resuelto (arrastre del sobrante + 1e-6); cualquier otro enfriamiento "cada X s" tiene el mismo problema.
- Bots y alturas: en el ápice del primer salto quedan a menos de 50 px de la altura del otro; la meta de subida
  (`B.goal`) se mantiene en el aire hasta aterrizar para que hagan el doble salto. Si tocás `botInput`, correr `llegar`
  y `partidas` antes y después.
- El editor guarda lo no guardado en `localStorage` (`arena-editor-wip`) del navegador integrado, que es compartido: no
  llames sus funciones (`openArena`, etc.) a mano, y `navigate` a la misma URL con el mismo `#` no recarga la página.
  Abrir otra arena (`#otra`) borra ese borrador: para probar el editor sin tocarlo, abrilo desde otro origen (el
  servidor "ranger-props" de `.claude/launch.json`, http://localhost:8767/prototypes/arena/editor/dist/index.html#…,
  sin `serve.py`: usa las arenas de cuando se armó) y mirá antes que ahí no haya borrador.
- El editor dibuja con `requestAnimationFrame`, que no corre con el panel oculto: para capturarlo, darle tamaño a
  `#stage` por CSS, `resize(); fit();` y llamar a su `render()` directo.
- La escala: el tamaño del mundo es el `size` de cada arena (`setWorld` en `src.html`, `[AW, AH] = A.size` en el editor,
  `capas.py` lo lee de la arena). Nada de lo jugable se escala con números; lo que se lee sobre la cabeza va por
  `HEAD_K`. Lo nuevo que se dibuje sobre la cabeza, también.
- El receptor de capturas (`recibir.py`, puerto 8799) lo usan otras sesiones del estudio: si está ocupado, levantar el
  tuyo en otro puerto (`recibir.py <carpeta> 8797`, y `window.RECIBIR = 8797` en la página) y apagarlo por su PID, nunca
  con `pkill` por nombre (mata los de las otras sesiones).
- El error de consola "AudioContext encountered an error" es del panel sin audio, no del juego.
- Una partida con un solo jugador (los otros en "off") termina en el acto: para probar algo de uno, poner otro quieto
  lejos (`kb2`) o usar `startTest()`.
- Las teclas en las pruebas: `keys` es lo mantenido y `tapped` los toques (saltar, granada, golpe); `keys.add` solo no
  salta. Las funciones del juego son globales y se pueden envolver para contar (`landHeavy = function (d) {...}`).
- Los efectos nuevos se miran cuadro por cuadro con `hoja` antes de reportar (tamaño contra el personaje, que no lo tapen,
  contraste con el piso de la arena). Lo grande que tapa la cara en el momento del golpe va detrás del personaje.
- Antes de saltear un cuadro de una animación para acelerarla, medir cuánto se corre el cuerpo entre los cuadros (p. ej.
  el centro de las filas de arriba, el casco): en throw2, saltear el 4 corría el cuerpo 20 px de golpe.
- Lo que pasa "en un cuadro" (la suelta de la granada) tiene que caer justo al empezar ese cuadro: con 1 ms de margen
  salía un cuadro tarde y había un cuadro sin granada ni en la mano ni en el aire.
- Las cajas de golpe salen de `hurtBox(Q)` (balas, golpe, granada, modo H): si una animación nueva cambia la forma
  del cuerpo (el slide, con las piernas adelante), se ajusta ahí, en proporción a la caja de pie contra el dibujo.
- Los cuadros del low-poly en `RIG` van por su nativo del clip (`natives: true`, `natRig`), no por la posición: a 12 o a 24
  fps es la misma tabla. Lo que se reproduce de corrido va con `fpsOf(anim)`, nunca con un `* 12` fijo. Lo que el juego
  tiene apagado no va a la página (`drop`, `OFF_ANIMS` en build.py): si se prende un interruptor, recompilar.
- Lo de cada personaje que el panel ajusta (de dónde sale la granada) va en `RIG.<personaje>` y se guarda con el
  personaje; si no, al cambiar de personaje queda lo del otro.
- Los dibujos de Arte se exportan en `build.py` con `export_hud` (set, hoja elegida, pieza de escala, eje y medida en px
  del archivo, al doble del juego) y entran a la página como `__ALGO_DATA__`; en `src.html` se precargan en `artFiles` y
  siempre queda el dibujo por código si falta el archivo.
- Los ajustes del fogonazo guardados (base del artifact `tuning/flash` o `localStorage` "arena.flash.v1") pisan los de
  fábrica (`FLASH_PABLO`): si cambia la boca medida, avisar que los guardados quedan corridos.
- Las animaciones nuevas se revisan cuadro por cuadro sobre verde antes de meterlas (CLAUDE.md); los cuadros elegidos a
  ojo van en `RIG`, por personaje.
- No publicar el artifact ni commitear salvo que lo pidan; al republicar, sin `capabilities` (conserva `db`).

## Reporte

Al terminar cada tanda: primera línea con lo más importante (el Director ve los primeros 400 caracteres), después qué
cambió con números (antes → después), cómo se probó, qué no se probó y lo que hay que pedirle a otro rol. Si te trabás,
primera línea `BLOQUEADO: …`.

## Animaciones nuevas

Sólo se integra una animación nueva cuando el Director avisa que Pablo aprobó el video (Pablo, 2026-10-18): antes, ni
cuadros en `RIG` ni lógica de juego. Si hay código hecho de una que no se aprobó, queda apagado detrás de un interruptor
(`SLIDE_ON`, `BALL_ON`) con el juego igual que antes, nunca a medio hacer.

## Plata

Todo gasto (fal, Gemini, `spritepipe bakeoff`, `gen-images`) lo corre el Director, con el OK de Pablo en su sesión
(Pablo, 2026-10-18). Si hace falta algo pago: preparar el `--dry-run`, y terminar el turno con la primera línea
`PEDIDO: OK para gastar US$X en Y` y el comando exacto. No correrlo nunca desde acá. Los detalles largos, en la carpeta de notas compartida.
