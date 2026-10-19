# Revisión del throw y el double_jump (Limpieza, 2026-10-18)

Revisados cuadro por cuadro sobre verde y sobre oscuro, a 1x y a tamaño de juego (0,5× × 1,6). Las hojas:

| Hoja | Qué muestra |
|---|---|
| `throw_cuadros_hoy.png`, `double_jump_cuadros_hoy.png` | Cada cuadro de hoy (antes del cambio del key), con el nativo, nitidez, rosa, corrimiento, para qué lo usa la arena y lo que se vio |
| `throw_juego_hoy.png`, `double_jump_juego_hoy.png` | Lo mismo a tamaño de juego |
| `throw_nativos_60-80.png`, `double_jump_nativos_22-44.png` (+ `_juego`) | Todos los nativos del tramo, para elegir cuadros |
| `borde_rosa.png` | El contorno rosa de 1 px, antes y ahora (`[key] edge_unmix`) |
| `throw_fix.png` | El tiro y el golpe como los juega la arena: hoy y con `throw_fix` |
| `double_jump_fix.png` | El mortal como lo dibuja la arena (ángulo con easing + giro por código): hoy y con `double_jump_fix` |
| `throw_fix_cuadros.png`, `double_jump_fix_cuadros.png` | Las dos animaciones nuevas cuadro por cuadro |

Todo se rehace con `characters/lowpoly/revisar.py` (ver su docstring); las notas de las hojas están en
`notas_throw_double_jump.json` y las secuencias, en `throw_fix.json` y `double_jump_fix.json`.

## Problemas

### Arreglado sin gastar

- **Contorno rosa en todas las animaciones** (se ve sobre fondo oscuro: el arma, las botas, el puño). Es el halo claro
  que deja el render por fuera del contorno más el borde mezclado con el fondo; el key por distancia los deja opacos y
  no tiene despill. Nuevo `[key] edge_unmix = true` en el pipeline: tinte del borde (azul − verde del anillo contra el de
  adentro) de 23–33 a 9–16 en las 18 animaciones. Los reflejos rosas del casco quedan (no es `clean = true`).
- **throw (la granada)**: el cuadro que se sostiene mientras carga (19, n68) tiene el puño hecho una mancha naranja; la
  vuelta (22–24, n75–77) da un paso adelante y gira de perfil (la cabeza avanza 26 + 7 + 6 px de 1x, ~32 px de juego)
  y el 24 sale borroso con el arma manchada; después vuelve de golpe al idle. **`throw_fix`**: nativos en el lugar y sin manchas.
- **double_jump (el mortal)**: el cuadro de 95° (3, n29) está de espaldas a cámara (sólo se ve el casco) con las piernas
  hechas humo. **`double_jump_fix`**: el n28 (44°) en su lugar, el n35 en vez del n33 deshecho y el n36 (256°) de más.
- **La boca de los tiros** (`boca_disparos.py`, `out/fx/`): seguía 4–26 px rojos de la franja del arma y en los cuadros
  con el cañón prendido quedaba atrás y abajo de la boca (crouch_shoot: 9 px de 0,5× abajo). Ahora sigue el arma por
  template matching: la boca cae en la punta del cañón en los 12 cuadros.

### Pide toma nueva (Animación ya las está haciendo)

- **throw**: todo el clip está agachado y girado a 3/4 (230–243 px de alto contra 256 del idle, de perfil): entrar y
  salir del idle salta igual con cualquier cuadro. El brazo pega una trompada, no tira por arriba, y no hay granada en
  la mano. Los primeros 28 cuadros del video está quieto y al final camina y dispara un rayo.
- **double_jump**: de 11 nativos del giro (n28–n38), 6 salen deformados (n29, n30, n32, n33, n34 y las piernas del
  n31). El de 180° (n31) se queda porque no hay otro: la cara se lee, las piernas no. Plan: la bolita girada por código.

## Para Programación (no cambié src.html)

`throw` y `double_jump` siguen iguales en el atlas (los cuadros que usa RIG.lowpoly no cambiaron). Para usar los nuevos:

- **Tiro**: `THROW_ANIM = "throw_fix"`, `throw: [[0, .07], [1, .05], [2, .05], [3, .06], [3, .05], [4, .03], [5, .03],
  [5, .03]]` (`releaseFrame` 2 igual). Fases: 0 n64 lleva el puño atrás, 1 n67 puño atrás de la cabeza (el que se
  sostiene al cargar), 2 n71 brazo estirado (sale la granada), 3 n72 estirado, 4 n73 empieza a bajarlo, 5 n63 el puño
  contra el pecho, antes del idle.
- **Golpe**: `melee: [["throw_fix", 1, .06, -4], ["throw_fix", 2, .1, 10], ["throw_fix", 3, .05, 7],
  ["throw_fix", 4, .04, 4], ["throw_fix", 5, .04, 1]]`.
- **Mortal**: `double_jump_fix` tiene 9 cuadros, como el que se usa (el `> 8` de `FLIP_ANG` sigue andando), en el
  mismo orden: `flip: [[1, 0], [2, 30], [3, 50], [4, 180], [5, 235], [6, 262], [7, 295], [8, 360]], flipFall: 8`.
  Ángulos medidos (casco contra el centro del cuerpo): 3°, 24°, 44°, 181°, 226°, 256°, 292°, 347°; los de la tabla
  siguen el mismo corrimiento que ya tenía RIG (+6° más o menos, y el último a 360). Hay que cambiar el nombre
  `"double_jump"` en `useChar` (FLIP, FLIP_ANG) y en los dos `name = "double_jump"` del dibujo del mortal.
- **Boca y bots**: con la boca nueva, `MUZZLE_H` pasa de ~51,3 a 55,2 y `CROUCH_MUZZLE` de ~34,4 a 42,0 px de juego
  (la del cuadro 0 de shoot y crouch_shoot). Ya está en el build; si los bots o el fogonazo se habían ajustado a ojo
  contra la medida vieja, revisarlos.
- El canvas del atlas creció 1 px (0,5×: 250 × 312, pivot y 292,29; antes 311 y 291,7): se lee del JSON.
