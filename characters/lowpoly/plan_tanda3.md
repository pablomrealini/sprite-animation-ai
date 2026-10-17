# Plan del set low-poly después de probarlo en la arena (2026-10-17)

Lo que dijo Pablo al jugarlo:

- **Disparo.** Sin el retroceso del video se ve peor. Lo raro no es el cañón prendido, sino el cañón prendido sin disparar.
- **Colgarse.** Con video no va a andar bien.
- **Granada.** Tiene que tener la granada en la mano.

## La regla

**El cañón se prende sólo cuando dispara.**

- **Cuando no dispara** (idle, correr, saltar, agacharse, apuntar), el disco de la boca va apagado (gris).
- **Cuando dispara**, va el video de Kling tal cual: retroceso, cañón prendido, fogonazo y la cara iluminada. No se limpia nada.

Cada postura de disparo sale de **un solo clip** que encadena apuntar (apagado) → ráfaga (prendido) → apuntar. Se corta en entrada, disparo (en loop mientras se aprieta) y salida. Al salir del mismo clip, el empalme no salta.

## Por postura

| Postura | De dónde sale | Video nuevo |
|---|---|---|
| Idle | El que está, con el disco apagado en el post (probado: queda perfecto) | — |
| Correr | El que está: borrar los rayos que Kling dispara solo y apagar el disco. O rehacerlo desde la pose apagada | — (o US$0,84) |
| Agacharse y disparar agachado | `clips/tanda2/crouch_1`: se agacha y apunta apagado (12–44), dispara prendido (46–86) y se para (102–114) | — |
| Disparo a dos manos | `clips/tanda2/shoot2h_2`: junta las manos apagado (6–27), dispara (28–44) y vuelve a apuntar. La ráfaga es corta: hay que verla en loop | — (si no alcanza, US$0,84) |
| Salto disparando | `clips/tanda2/jump_shoot_2`: salta con el brazo estirado apagado y dispara arriba (24–33). Como salto común queda el limpio (`set/jump_1`) | — |
| Disparo parado | Probar gratis: entrada de `apuntar_1` (apagado) y disparo de `set/shoot_1` (prendido, con retroceso), que salen de la misma pose. Si el empalme salta, un clip nuevo "apunta, ráfaga, apunta" desde la pose apagada | — (o US$0,84) |
| Granada | Pose con la granada en la mano (US$0,47), y video de tirarla que termina con la mano vacía (US$0,84). El juego dibuja la granada desde el cuadro en que sale | US$1,31 |
| Doble salto | La bolita (`poses/bolita.png`) girada por el juego | — |
| Colgarse | Ver abajo | — |

**Colgarse.** Para el low-poly, se deja el colgado de una mano para después. Al agarrarse del canto, el personaje **sube solo** con el `climb` que ya tenemos, que arranca colgado de las dos manos y no dibuja el canto: anda en cualquier plataforma. Si hace falta un instante colgado, alcanza con los primeros cuadros del `climb`. Es un cambio de la arena, no de video.

## Qué toca al juego (arena, otra sesión)

- **Disparo:** en el low-poly, el juego no dibuja su fogonazo (ya viene en el video), pero sigue tirando la bala desde la boca.
- **Colgarse:** al agarrarse, el low-poly pasa directo a `climb`, sin el colgado de una mano.
- **Doble salto:** la bolita girando en lugar del mortal.
- **Granada:** se suelta en el cuadro en que sale de la mano.

## Costo

- **Mínimo:** US$1,31 (la granada).
- **Si el disparo parado o el de dos manos piden clip nuevo:** hasta US$3,83.
- **Lo demás:** post y recortes, sin gastar.

## Orden

1. Armar el atlas con lo que ya existe y verlo en la arena: idle y correr apagados, agacharse, dos manos y salto disparando encadenados, y el disparo parado de prueba.
2. Con lo que salga de verlo, decidir los clips nuevos (disparo parado, dos manos) y la granada.
3. Los cambios de la arena (fogonazo del low-poly, auto-subida, bolita), en la sesión del selector.

## Paso 1 hecho (2026-10-17, sin gastar)

- **Cañón apagado** en todo lo que no dispara: `apagar_video.py` (clips/apagado/). En correr, primero borra los rayos.
- **Disparos con cuadros a mano** (opción nueva `frames` del pipeline): cada uno es un tiro del video (cañón prendido, destello y retroceso) que termina apuntando con el cañón apagado. Así, agachado sin disparar no brilla.
  - Parado: `set/shoot_1` 30, 31, 32 → 29 (retroceso de 10 px; el disco apagado antes del primer tiro).
  - Dos manos: `tanda2/shoot2h_2` 28, 29, 30 → 27.
  - Agachado: `tanda2/crouch_1` 47, 48, 50 → 44 (sin retroceso: el destello pulsa).
- **La boca de los tiros** sale de `boca_disparos.py` (out/fx/): en los cuadros con rayo, la punta del personaje es la punta del rayo y la bala habría salido de ahí.
- **Salto disparando:** los cuadros de subida de `tanda2/jump_shoot_2` (apagado). La arena usa uno solo, con su fogonazo de código.
- **Fogonazo:** Pablo lo probó y el del video queda mal: se borra (apagar_video.py --sin-fogonazo, la boca seguida desde el cuadro de reposo) y lo dibuja el juego, como en el ranger. Quedan el cañón prendido y la luz sobre el personaje, que no le molestan.
