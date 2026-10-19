# throw2: el tiro de granada nuevo (Limpieza, 2026-10-18)

Aprobado por Pablo: "la granada ok, pero en el juego quizás tiene que ser más rápida". Toma
`clips/tanda3b/kling-o3-std_throw_cerca_2.mp4`, retocada por `characters/lowpoly/retocar_throw2.py` en
`clips/retocado/throw_cerca_2.mp4` (correrlo antes del run). `throw` y `throw_fix` no se tocaron.

| Hoja | Qué muestra |
|---|---|
| `throw2.png` | Arriba, la propuesta rápida como la jugaría la arena (idle → tiro → idle); abajo, los 18 cuadros a 12 fps |
| `throw2_retoque.png` | El retoque, antes y después: la granada del juego en la mano (24–50) y sin la que vuela ni la explosión (51–56) |
| `throw2_cuadros.png`, `throw2_juego.png` | Cuadro por cuadro sobre verde, oscuro y rosa; a tamaño de juego |
| `throw2_nativos_20-80.png` (+ `_juego`) | Todos los nativos del tramo |

## El retoque

- **Una sola granada.** La de la mano de Kling (gris oscura con franja roja) se tapa con la del juego
  (`backgrounds/lowpoly_grenade/.../off.png`, la del power-up y el HUD) a su tamaño en la arena (24 px de juego =
  81 px del video; su cuerpo mide 45 px de ancho y la esfera de Kling, ~47), centrada en la esfera, espejada (la
  argolla para atrás, como la de Kling) y girada como va la mano: −15° a −5° en la anticipación (24–45), −40° en el 47,
  15° y 25° en el 49–50. En 24–45 el centro sale de detectar la esfera; en 47–50 el brazo va borroso y el centro va a
  ojo sobre un recorte con grilla.
- **Sólo el personaje en 51–56**: la granada que vuela en 51–52 (la pone el juego) y la explosión que dibuja Kling a la
  derecha en 53–55 se pintan del fondo.

## Fases, para Programación

18 cuadros (nativos): 0 n24, 1 n28, 2 n36, 3 n44 · 4 n45, 5 n47, 6 n49, 7 n50 · 8 n51 · 9 n52, 10 n56, 11 n60, 12 n62 ·
13 n64, 14 n66, 15 n68, 16 n72, 17 n76.

- **Anticipación** (0–3): la granada levantada atrás de la cabeza, a la vista. Del 0 al 2 casi no se mueve; el 3 ya
  baja un poco el brazo. Para la carga sostenida: el 3.
- **Tiro** (4–7): el brazo pasa por arriba; 5 (n47) con el brazo bien atrás; 7 (n50) es el último con la granada en la
  mano.
- **Suelta** (8, n51): la mano abierta adelante, sin granada.
- **Seguimiento** (9–12): el brazo estirado adelante, quieto.
- **Vuelta** (13–17): baja el brazo y vuelve a la pose de perfil (17 = la de perfil, empalma con el idle).

**Dónde larga el juego su granada** (px de juego desde los pies, como `GRENADE.spawnX/spawnY`: 0,5× × 0,8 y −3 del
hundimiento de los pies): la granada de la mano en el cuadro 7 está en **(57, 74)**; la punta del puño en la suelta
(cuadro 8) en **(51, 57)**. Para que sea la misma granada, que salga en el 8 desde donde estaba en el 7: ~(57, 74). Hoy
el juego usa (54, 114), que era para el tiro viejo.

**Más rápida** (lo que pidió Pablo), una propuesta: `throw: [[0, .05], [3, .05], [4, .03], [5, .03], [6, .03],
[7, .03], [8, .05], [9, .04], [11, .04], [13, .04], [15, .04], [17, .04]]` con `releaseFrame` 6 (el cuadro 8): sale a
los 220 ms y todo dura 470 ms (el viejo: sale a los 120, 390 en total). La carga sostiene el 3.

**El golpe** (melee) conviene que siga con `throw_fix`: en throw2 todos los cuadros de antes de la suelta tienen la
granada en la mano.

## Detalles que quedan

- 4, 6 y 7 (n45, n49, n50): el arma de la otra mano sale borrosa, con una estela rosada (se mueve rápido); un cuadro
  cada uno.
- En 47–50 la granada del juego queda nítida sobre el brazo borroso.
