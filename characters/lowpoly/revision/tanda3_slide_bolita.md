# Tanda 3: deslizamiento y doble salto en bolita (Limpieza, 2026-10-18)

> **El slide de esta nota quedó reemplazado** (2026-10-18): Pablo no aprobó la toma 2 de la tanda 3; el de ahora es la
> tanda 5 toma 3, con las fases en `slide.md`. Las hojas `slide*.png` de esta carpeta son las nuevas. La parte del doble
> salto en bolita sigue valiendo.

Clips de Animación: `clips/tanda3/kling-o3-std_slide_2.mp4` y `kling-o3-std_double_jump_1.mp4` (BT.601). En
`character.toml`, sección "tanda 3". Ninguna animación que ya usa el juego cambió de cuadros.

| Hoja | Qué muestra |
|---|---|
| `slide.png` | La secuencia como la jugaría la arena: run_gun → slide_in → slide → slide_out → run_gun, a 12 fps y a tamaño de juego |
| `double_jump_bolita.png` | El doble salto (ápice, se encoge, la bolita girada por código, se abre, cae); la bolita del video contra bolita.png |
| `slide_in_cuadros.png`, `slide_cuadros.png`, `slide_out_cuadros.png` (+ `_juego`) | Cuadro por cuadro sobre verde, oscuro y rosa |
| `double_jump_in_cuadros.png`, `double_jump_ball_cuadros.png`, `double_jump_out_cuadros.png` (+ `_juego`) | Ídem |
| `slide_in_nativos_30-96.png`, `double_jump_in_nativos_12-50.png` (+ `_juego`) | Todos los nativos de los tramos |

## Fases, para Programación (0,5×: el idle mide 127 px de alto)

**Deslizamiento** (`slide_in`, `slide`, `slide_out`; 12 fps). Entra y sale en la zancada de correr: run_gun 0 empalma con
slide_in 0 y slide_out 5 con run_gun 0.

- `slide_in` (6): 0 n36 corre, 1 n38 se tira, 2 n39 en el aire (25 px sobre el piso), 3 n40 baja, 4 n42 toca el piso,
  5 n44 deslizando.
- `slide` (1, en loop): n62, deslizando sentado con el arma al frente; se sostiene lo que dure el slide. Mide 100 px de
  alto (79 % del idle): para la caja de golpe.
- `slide_out` (6): 0 n86 empieza a levantarse, 1 n87, 2 n88 todavía bajo, 3 n91 parado, 4 n92 zancada, 5 n94 zancada
  (sigue run_gun).

**Doble salto en bolita** (`double_jump_in`, `double_jump_ball`, `double_jump_out`). Los dos tramos del video van a su
altura sobre el piso del clip (`ground_from_clip`); la bolita va sola, a la escala del resto.

- `double_jump_in` (5): 0 n16 sube estirado (46 px sobre el piso), 1 n18 sube (75), 2 n20 arriba (89), 3 n21 empieza a
  encogerse (89), 4 n22 rodillas arriba (94). Del 4 pasa a la bolita.
- `double_jump_ball` (1): bolita.png, para girar por código (una vuelta entera, como el mortal). Mide 91 px (72 % del
  idle); conserva la franja roja del casco.
- `double_jump_out` (4): 0 n43 se abre (99 px sobre el piso), 1 n44 estira las piernas (76), 2 n45 piernas abajo, con
  el balanceo corrido (46), 3 n47 cae parado (1): sirve de cuadro de caída hasta tocar el piso.

## Decisiones

- **La bolita es poses/bolita.png, no la del video.** En el video (nativos 23–41) el casco crece ~30 % y pierde la
  franja roja; a tamaño de juego se lee como un huevo blanco. bolita.png se pone a la escala del video con el auricular
  del casco (un disco: 297 px en la imagen, 59,5 px en los nativos 20–21 → ×0,2003) y pasa por el pipeline como un
  clip (`bolita_clip.py` → `clips/bolita/bolita.mp4`), así sale con el mismo key, nitidez y pivot que el resto.
- **El sostenido del slide es un cuadro (n62), no un loop.** 44–84 está muy quieto (la cabeza se mueve ±2 px de 1x):
  un loop sólo agrega temblor.

## Arreglos del key que salieron de esto (todo el personaje)

- **Bolsillos de magenta.** En el slide sostenido, el hueco entre el mentón, el brazo y el arma quedaba opaco y
  magenta en cuadros alternos (0,2–0,3 % del personaje, menos que el 0,4 % de `hole_max_frac`). Lo mismo entre las
  manos en hang_two (32 cuadros), entre las piernas en run_gun 6 y en shoot_in 5. `hole_max_frac` pasó a 0,001.
- **Motas en el casco.** Con el umbral bajo, una mota rosa en el casco blanco (hang_in 6, del tamaño de un bolsillo) se
  abría. Regla nueva en el key: un hueco rodeado de blanco se rellena igual hasta el 1 %; y con `hole_inpaint = true`
  los huecos rellenos toman el color de alrededor (blanco en el casco), no el magenta. En todo el atlas 1x, los px
  opacos del color del fondo bajaron de 11.226 a 6.966.
- **Canvas.** `double_jump_out` arranca en el aire: alineado como oneshot (pies del primer cuadro en el piso), el n47
  quedaba 197 px abajo y el canvas de todas las animaciones crecía de 624 a 788 px (1x). Con `ground_from_clip` (opción
  nueva del pipeline) quedó como estaba: 500 × 624 en 1x, 250 × 312 en 0,5×, pivot y 292,29.

## Detalles que quedan

- slide: el arma tiene un tinte violeta arriba (reflejo del fondo en el render, no del key) y hay motas sueltas entre
  el mentón y el arma en slide_in 3 (n40). A tamaño de juego son 1–2 px.
- double_jump_out 2 (n45): las piernas salen corridas (el balanceo); el 46 está más borroso.
