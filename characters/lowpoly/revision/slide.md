# slide: el deslizamiento nuevo (Limpieza, 2026-10-18)

Aprobado por Pablo: "Sí, aprobado así como está. Que Limpieza lo limpie y Programación lo meta en el juego". Toma
`clips/tanda5/kling-o3-std_slide_3.mp4`, retocada por `characters/lowpoly/retocar_slide.py` en
`clips/retocado/slide_3.mp4` (correrlo antes del run). Reemplaza a `slide_in`, `slide` y `slide_out` de la tanda 3 (no
aprobados): mismos nombres, así el código de Programación sigue sirviendo. Los ojos cerrados del sostenido no se tocaron.

| Hoja | Qué muestra |
|---|---|
| `slide.png` | La secuencia como la jugaría la arena: run_gun → slide_in → slide → slide_out → run_gun, a 12 fps y a tamaño de juego |
| `slide_retoque.png` | Antes y después del retoque: el piso (verde: el de correr; amarillo: donde apoyaba) y el casco (cian) |
| `slide_in_cuadros.png`, `slide_cuadros.png`, `slide_out_cuadros.png` (+ `_juego`) | Cuadro por cuadro sobre verde, oscuro y rosa |
| `slide_nativos_44-76.png`, `slide_nativos_74-86.png` (+ `_juego`) | Los nativos del sostenido y de la subida, para la elección |

## El retoque: al piso de correr y al lugar

Mientras se tira, se desliza y se levanta, Kling baja el apoyo hasta 46 px (518 → 564) y lleva al personaje para atrás
(el casco, de 624 a 403: hasta 221 px). En 42–83 se corre el cuadro entero para que lo más bajo quede en el piso de
correr (518) y el casco donde está corriendo (x 624); lo que se destapa se pinta del fondo. La cabeza queda sobre el
jugador y las piernas salen para adelante, como en un deslizamiento: el movimiento lo pone el juego. 0–41 y 84–96
quedan como están (ahí el rebote es el de run_gun). En el atlas, las tres animaciones van con el piso del frame 0 del
clip (`ground_from_clip`): todos sus cuadros apoyan en el piso (pies a 0,3 px del pivot en 0,5×).

## Fases, para Programación (12 fps)

- **`slide_in`** (4): 0 n41 corriendo (la zancada de run_gun), 1 n43 se junta para tirarse, 2 n46 aterriza sentado,
  3 n47 se acomoda. Se saltean el 42, 44 y 45 (movidos).
- **`slide`** (1, en loop): n63, sentado con las piernas estiradas, las dos manos en la pistola al pecho y los ojos
  cerrados. Es el más nítido del sostenido: 49–72 casi no se mueve (la cabeza ±1 px de 1x), un loop sólo temblaría.
- **`slide_out`** (8): 0 n75 se incorpora, 1 n76, 2 n77, 3 n78 (se levanta), 4 n79 parado, 5 n80 primer paso, 6 n82,
  7 n84 la zancada del arranque (≈ run_gun 0: sigue corriendo).

**Caja de golpe del sostenido** (px de juego desde los pies, 0,5× × 0,8): **69 de alto** (el idle, 102: el 67 %),
de **x −26 a +70** (las piernas adelante; parado, −27 a +41). En la entrada: el 2 (aterriza) mide 74 y el 3, 71; en la
salida, 78 → 85 → 89 → 90 → 94 → 100.

## Detalles que quedan

- slide_out 1 y 2 (n76, n77) salen algo borrosos (nitidez 0,74 y 0,88): son cuadros de transición de 83 ms.
- slide_out 0 y 3 (n75, n78) tienen un borde rosa fino en el casco (rosa 99 y 100 px en 1x), a tamaño de juego 1 px.
