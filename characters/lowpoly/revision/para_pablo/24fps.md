# 24 fps en vez de 12: prueba y estimación (Limpieza, 2026-10-19)

Pablo: "12 fps es poco, las animaciones tienen que estar en 24 cuadros". Prueba sin tocar el atlas del juego: todo en
`characters/lowpoly/work_revisar/` (git lo ignora).

## La prueba: run_gun, idle_combat y jump a 24

`24fps.mp4` (y `24fps.png`, un cuadro): a la izquierda el atlas de hoy (12 fps), a la derecha la prueba (24 fps), sobre
verde y a tamaño de juego (0,5× × 1,6), 10 s. Ojo: en el juego el salto no se reproduce de corrido; va por fases según
la velocidad (RIG.lowpoly.jump). El video lo muestra de corrido, como el clip.

| Animación | 12 fps (hoy) | 24 fps (prueba) | Qué se sacó o se sostuvo |
|---|---|---|---|
| run_gun | 14 (nativos 14, 16 … 40) | 28 (14–41, todos) | Nada. El 33 tiene la bota movida, como el 18 y el 26, que ya están hoy |
| idle_combat | 60 (0, 2 … 118) | 120 (0–119, todos) | Nada: ninguno borroso ni corrido |
| jump | 10 (5, 7, 9, 11, 14, 15, 18, 19, 21, 23) | 19 (5–23) | 13, 17 y 22 rotos, sostenidos con el de antes (12, 16, 21): los mismos que se salteaban a 12 |

Hojas cuadro por cuadro de la prueba: `revision/run_gun_cuadros_24fps.png`, `revision/jump_cuadros_24fps.png` (y
`_juego_24fps`).

## Si todo pasara a 24

Corrida de estimación: todo el low-poly con `game_fps = 24` (`work_revisar/fps24_todo/`). Los ciclos y los recortes
pasan solos; los cuadros a mano se estiraron a todos los nativos de su tramo (cota de arriba); los tiros quedan igual
(ya son nativos seguidos, el juego los reproduce en un tiempo fijo).

**Cuadros por animación** (el juego usa la variante 0,5×):

| Animación | 12 | 24 | |
|---|---:|---:|---|
| idle_combat | 60 | 120 |  |
| idle | 3 | 4 |  |
| run_gun | 14 | 28 |  |
| jump | 10 | 19 |  |
| double_jump | 11 | 20 | apagada en el juego |
| double_jump_fix | 9 | 17 | apagada en el juego |
| hang_in | 9 | 18 | apagada en el juego |
| hang | 17 | 33 | apagada en el juego |
| climb | 38 | 75 | apagada en el juego |
| hang_two | 48 | 96 | apagada en el juego |
| throw | 25 | 48 | apagada en el juego |
| throw_fix | 6 | 11 |  |
| shoot_in | 8 | 16 |  |
| shoot | 4 | 4 |  |
| shoot2h_in | 12 | 24 | apagada en el juego |
| shoot2h | 4 | 4 | apagada en el juego |
| crouch_in | 10 | 20 |  |
| crouch_shoot | 4 | 4 |  |
| crouch_out | 11 | 20 |  |
| jump_shoot | 4 | 13 |  |
| slide_in | 4 | 7 |  |
| slide | 1 | 1 |  |
| slide_out | 8 | 10 |  |
| double_jump_in | 5 | 7 |  |
| double_jump_out | 4 | 5 |  |
| double_jump_ball | 1 | 1 |  |
| throw2 | 18 | 53 |  |
| **total** | **348** | **678** | |

**Atlas.** 1x: 348 → 678 cuadros, 5 → 10 páginas de 2048. 0,5×: 2 → 3 páginas; la hoja que mete el juego (las páginas
apiladas) pasa de 2048 × 3063 a 2048 × 5301. El canvas de la celda cambia un poco (500 × 624 → 509 × 615 en 1x: hay
cuadros nuevos más anchos), así que el pivot y lo que el juego mide en el sprite se corren unos px.

**Peso de la página del juego** (hoy 12,0 MB; el artifact admite 16). El low-poly es la hoja 0,5× en WebP sin pérdida,
en base64: hoy 6,5 MB, más de la mitad de la página.

| Caso | low-poly | página |
|---|---:|---:|
| hoy (12 fps) | 6,6 MB | 12,1 MB |
| todo a 24 | 12,9 MB | **18,4 MB** (no entra) |
| 24 sólo en correr e idle | 7,9 MB | 13,3 MB |
| todo a 24, sin exportar las apagadas | 6,0 MB | **11,4 MB** |
| 24 en correr e idle, sin las apagadas | 4,3 MB | 9,8 MB |
| hoy, sin las apagadas | 3,0 MB | 8,5 MB |

"Las apagadas" son las que el juego tiene desactivadas hoy y siguen en el atlas: colgarse y subir (hang_in, hang,
hang_two, climb: `HANG_ON = false`), dos manos (shoot2h_in, shoot2h: `TWO_HAND_ON = false`), el tiro viejo (throw), el
mortal viejo (double_jump) y el de prueba (double_jump_fix, sólo con `?mortal=1`). Son más de la mitad del atlas. Se
pueden dejar en `characters/lowpoly/out` y no mandarlas a la página (lo decide Programación en `build.py`); si se
vuelven a prender, entran.

**Cuadros a mano que habría que rehacer** (elegir entre todos los nativos del tramo, sacando o sosteniendo los rotos):
- jump: hecho en la prueba (19 cuadros; 13, 17 y 22 sostenidos).
- throw2: 24–76 son 53 nativos. La granada del juego está pegada sólo en los 8 que se usan hoy (`retocar_throw2.py`,
  por cuadro): en 24–45 se detecta sola; en 46–50, con el brazo borroso, va a ojo. Rotos conocidos: 29–30 (mancha
  roja arriba del casco), 33–34 (chispa), 48 (movido).
- slide_in (41–47; 42, 44 y 45 movidos), slide_out (75–84; 81 sale borroso), double_jump_in (16–22) y double_jump_out
  (43–47; 46 borroso). `retocar_slide.py` ya corrige todos los nativos de 42 a 83.
- throw_fix (el golpe): hoy es 64, 67, 71, 72, 73 y 63, no seguidos; a 24 se rearma.
- jump_shoot: hoy 4 cuadros (8, 12, 16, 20), y el juego usa uno (airShot).
- Igual que hoy: shoot, crouch_shoot, slide (1 cuadro), double_jump_ball, idle. `tapa_correr.py` y `bolita_clip.py` ya
  cubren todos los nativos.

**Números de RIG.lowpoly a remapear** (para Programación; no los toqué). Cada cuadro de hoy es un nativo del clip; a 24
es la posición de ese nativo en la animación nueva (con los cuadros a mano estirados al tramo entero; si se rehacen,
cambian):

| RIG.lowpoly | animación | hoy | nativos | a 24 |
|---|---|---|---|---|
| grab | hang_in | [5, 6, 7, 8] | [50, 53, 55, 57] | [10, 13, 15, 17] |
| airShot | jump_shoot | [1] | [12] | [4] |
| jump (takeoff, rise, rise, apex, turn, fall, land) | jump | [3, 4, 5, 6, 7, 8, 9] | [11, 14, 15, 18, 19, 21, 23] | [6, 9, 10, 13, 14, 16, 18] |
| climb | climb | [0, 6, 9, 12, 16, 20, 23, 25, 28, 31, 34, 37] | [15, 27, 32, 38, 47, 55, 61, 65, 71, 76, 83, 88] | [1, 13, 18, 24, 33, 41, 47, 51, 57, 62, 69, 74] |
| flip (+ flipFall 8) | double_jump_fix | [1, 2, 3, 4, 5, 6, 7, 8, 8] | [24, 27, 28, 31, 35, 36, 37, 39, 39] | [1, 4, 5, 8, 12, 13, 14, 16, 16] |
| throw (throw2) | throw2 | [0, 3, 4, 5, 6, 7, 8, 9, 11, 13, 15, 17] | [24, 44, 45, 47, 49, 50, 51, 52, 60, 64, 68, 76] | [0, 20, 21, 23, 25, 26, 27, 28, 36, 40, 44, 52] |
| melee (throw_fix) | throw_fix | [1, 2, 3, 4, 5] | [67, 71, 72, 73, 63] | [4, 8, 9, 10, 0] |
| slide.in | slide_in | [1, 2, 3] | [43, 46, 47] | [2, 5, 6] |
| slide.out | slide_out | [0, 1, 2, 3, 4, 5, 6, 7] | [75, 76, 77, 78, 79, 80, 82, 84] | [0, 1, 2, 3, 4, 5, 7, 9] |
| ball.in | double_jump_in | [0, 2, 3, 4] | [16, 20, 21, 22] | [0, 4, 5, 6] |
| ball.out | double_jump_out | [0, 1, 2, 3] | [43, 44, 45, 47] | [0, 1, 2, 4] |

Además, en `src.html` hay 12 fijo y tiempos por cuadro que a 24 irían al doble de lento:
- `* 12` en colgado (`H.t * 12`), correr (`P.t * 12`), idle (`P.idleT * 12 * IDLE_SPEED`) y la vista del fogonazo
  corriendo (`t * 12 * RUN_SPEED / 260`). Pasarlo a los fps de cada animación (`ms` en lo que exporta `build.py`).
- Tiempo fijo por cuadro: crouch_in 0,04 s, crouch_out 0,045 y 0,05 (al caer pesado), apuntar in/out 0,04 y 0,045,
  la salida de la subida 0,055 y el agarre 0,05. A 24, la mitad, o elegir cuadros salteados.
- Lo que va con secuencias de RIG (tiro, golpe, slide, bolita, subida, mortal) y por fases (salto) ya tiene sus tiempos:
  cambian sólo los números de cuadro.
- `build.py` reduce shoot_in, shoot2h_in, crouch_in y crouch_out a 4 cuadros para el low-poly: sigue andando.

**El pipeline** hoy tiene un solo fps por personaje (`[character] game_fps`). Para mezclar (24 en unas, 12 en otras)
hace falta un `fps` por animación: es un cambio chico en `pipeline/` (Limpieza), sin costo.

## Recomendación

1. **Sacar de la página las animaciones apagadas** (Programación, en `build.py`): la página baja de 12,0 a 8,5 MB y deja
   lugar para todo lo demás.
2. **24 ya en correr e idle**: es donde más se nota (la corrida pasa de 14 a 28 cuadros, el idle de 60 a 120),
   salen solas del clip (no hay cuadros a mano ni rotos) y en el juego sólo cambian los `* 12` de correr e idle. Página:
   9,8 MB. Necesita el `fps` por animación en el pipeline (lo hago yo, sin costo).
3. **24 en las de acción de a una**, con los cuadros a mano rehechos y revisados sobre verde, y los números de RIG
   remapeados: el salto (ya está la prueba), después el slide, la bolita y throw2 (el más largo: la granada pegada en
   ~27 cuadros). Con todo a 24 y sin las apagadas, la página queda en ~11,4 MB.

Todo a 24 de una sola vez no entra en la página (18,4 MB) si no se sacan las apagadas. Nada de esto cuesta plata: los
clips de Kling ya están a 24 fps.

