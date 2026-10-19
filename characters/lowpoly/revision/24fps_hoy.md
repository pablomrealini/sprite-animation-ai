# Todo el low-poly a 24 fps (Limpieza, 2026-10-19)

Pablo: "Pasá todo a 24 de una, sacando de la página las animaciones apagadas". `characters/lowpoly/character.toml` con
`game_fps = 24`; el atlas de antes quedó en `work_revisar/out_12` (git lo ignora). No quedó ninguna a 12: ninguna tiembla
a 24 (al contrario: el casco de correr se aparta de su curva 0,6 px de media contra 1,9 a 12; el idle, 0,1 contra 0,3),
así que no hizo falta el fps por animación en el pipeline.

## Cuadros por animación (las que usa el juego)

| Animación | 12 | 24 | Nativos (los que faltan del tramo, salteados) |
|---|---:|---:|---|
| idle_combat | 60 | 120 | 0–119, todos |
| idle | 3 | 4 | el retrato |
| run_gun | 14 | 28 | 14–41, todos (con la tapa del arma arreglada en todos: `tapa_correr.py`) |
| jump | 10 | 16 | 5–23 sin 13 (sube borroso), 17 (mancha en la pierna) y 22 (cara y brazo movidos) |
| throw2 | 18 | 48 | 24–76 sin 29–30 (mancha roja sobre el casco), 33–34 (chispa) y 48 (movido); la granada del juego, pegada en los 26 que la tienen en la mano |
| throw_fix (golpe) | 6 | 8 | 64, 65, 66, 67, 71, 72, 73, 63: sin 68 (puño naranja) ni 69–70 (estela rosa) |
| shoot_in | 8 | 16 | 14–29 |
| crouch_in | 10 | 20 | 10–29 |
| crouch_out | 11 | 20 | 98–117 |
| shoot, crouch_shoot | 4 | 4 | iguales (un tiro de nativos seguidos) |
| jump_shoot | 4 | 4 | igual (8, 12, 16, 20; el juego usa el 12) |
| slide_in | 4 | 6 | 41, 43, 44, 45, 46, 47: sin 42 (el cuerpo hecho una mancha) |
| slide | 1 | 1 | 63 |
| slide_out | 8 | 9 | 75–84 sin 81 (borroso) |
| double_jump_in | 5 | 7 | 16–22, todos |
| double_jump_ball | 1 | 1 | bolita.png |
| double_jump_out | 4 | 4 | 43, 44, 45, 47: sin 46 (borroso) |
| **usadas** | **196** | **320** | |

Las apagadas quedaron como estaban, pasadas a 24 solas (hang_in 18, hang 33, hang_two 96, climb 75, shoot2h_in 24,
shoot2h 4, throw 48, double_jump 20, double_jump_fix 9): 327 cuadros más. **Total del atlas: 348 → 647.**

## Atlas

- 1x: celda 509 × 615 (antes 500 × 624), 9 páginas de 2048.
- 0,5×: celda 255 × 308 (antes 250 × 312), 3 páginas (2048 × 2048, 2044 × 2027, 1101 × 1108). La hoja apilada que mete el
  juego: 2048 × 5183, 9,3 MB en WebP sin pérdida, **12,4 MB en base64** (antes 6,5).
- Página del juego: con todo, ~17,9 MB (no entra en los 16 del artifact). Sin las apagadas (son el 55 % del área), como
  ya la arma `build.py`: **10,5 MB** (medido, `prototypes/arena/dist/index.html`; antes 12,0).
- El pivot cambió (0,5×: 125, 292,29 → 127,5, 292,73) y la celda también, pero cada cuadro con el mismo nativo quedó a
  ≤ 0,6 px de donde estaba respecto de los pies (salvo el mortal viejo, apagado). Las bocas de los tiros, rehechas
  (`boca_disparos.py`).

## Para Programación: RIG.lowpoly

RIG.lowpoly ya está en nativos (`natives: true` + `natRig` con el `nat` que exporta `build.py`): **no hay que cambiar
números**, salvo los dos que faltan. Así se resuelve cada uno en el atlas nuevo:

| RIG | animación | nativos | cuadro a 24 |
|---|---|---|---|
| jump (takeoff, rise, rise, apex, turn, fall, land) | jump | 11, 14, 15, 18, 19, 21, 23 | 6, 8, 9, 11, 12, 14, 15 |
| airShot | jump_shoot | 12 | 1 |
| throw (throw2) | throw2 | 24, 44, 45, 47, 49, 50, **51 (sale)**, 52, 60, 64, 68, 76 | 0, 16, 17, 19, 20, 21, **22**, 23, 31, 35, 39, 47 |
| melee | throw_fix | 67, 71, 72, 73, 63 | 3, 4, 5, 6, 7 |
| slide.in | slide_in | 43, 46, 47 | 1, 4, 5 |
| slide.out | slide_out | 75, 76, 77, 78, 79, 80, 82, 84 | 0, 1, 2, 3, 4, 5, 6, 8 |
| ball.in | double_jump_in | 16, 20, 21, 22 | 0, 4, 5, 6 |
| ball.out | double_jump_out | 43, 44, 45, 47 | 0, 1, 2, 3 |
| grab (apagado) | hang_in | 50, 53, 55, 57 | 10, 13, 15, 17 |
| climb (apagado) | climb | 15, 27 … 88 | 1, 13, 18, 24, 33, 41, 47, 51, 57, 62, 69, 74 |
| flip, flipFall (con ?mortal=1) | double_jump_fix | 24, 27, 28, 31, 35, 36, 37, 39 | 1–8 |

Todos los nativos de RIG están en el atlas. La granada sale en el n51 (`releaseFrame` 6 = el 7.º paso de `throw`) desde
(57, 74), como antes: el n50, el último con la granada en la mano, no se movió.

Lo nuevo que se puede aprovechar a 24 (los cuadros que había entre los de RIG):
- **Salto**: n12 (despega, entre el empujón y la subida), n16 (sube), n20 (cae, entre el turn y el fall).
- **Tiro de granada**: la anticipación tiene 16 cuadros (n24–44) y el tiro, 25–50 sin el 48; la vuelta, 52–76 de corrido.
- **Golpe**: n64–66 (lleva el puño atrás) antes del n67.
- **Slide**: n44 y n45 (cae sentado) entre el 43 y el 46; n83 (paso) entre el 82 y el 84.
- **Bolita**: n17–19 (sube) entre el 16 y el 20.

Lo que sí hay que ajustar en `src.html`: los `* 12` fijos (correr `P.t * 12`, idle `P.idleT * 12 * IDLE_SPEED`, la vista
del fogonazo corriendo `t * 12 * RUN_SPEED / 260`) y los tiempos fijos por cuadro de crouch_in (0,04 s), crouch_out
(0,045 y 0,05) y apuntar (0,04 y 0,045): con el doble de cuadros, a esos tiempos irían al doble de lento.

## Hojas

| Hoja | Qué muestra |
|---|---|
| `para_pablo/24fps_todo.mp4` (+ `.png`) | 12 contra 24, sobre verde, a tamaño de juego: correr, idle, salto, granada, golpe, slide y bolita |
| `<anim>_cuadros.png`, `<anim>_juego.png` | Cada animación usada, cuadro por cuadro sobre verde, oscuro y rosa, y a tamaño de juego |
| `throw2_retoque.png` | La granada del juego pegada en los 26 nativos con la granada en la mano |
