# El arma de run_gun: "como que salta raro" (Limpieza, 2026-10-18)

> **Aplicado** (aprobado por Pablo, 2026-10-18): `run_gun` sale de `clips/retocado/correr_a_2_tapa.mp4` (de
> `tapa_correr.py`), con el loop fijo en 14–41 como antes. En el atlas sólo cambió run_gun (las otras 28 animaciones,
> el canvas, el pivot y las bocas de los tiros, idénticos). La boca que mide el juego al correr se corrió hasta 3 px
> del sprite (2,4 px de juego: x en el cuadro 10, y en el 3), más que el ~1,6 que estimé: son los cuadros que tenían
> la tapa corrida, y ahora la boca está en la punta del caño y no en el gris de más. Hojas: `arma_correr_antes_despues.png`,
> `arma_correr_*_aplicado.png` y `arma_correr_en_el_juego_aplicado.png`.

**Qué salta:** la tapa de la boca del arma. En 8 de los 14 cuadros del loop (2, 3, 5, 6, 9, 10, 12 y 13) no es la tapa
del arma: un gris pegado de más, corrido abajo y adelante con un escalón (3, 10), cortado en recto o cuadrado con un
borde lila (2, 5, 9, 12), o con una esquina lila (6, 13). Como alterna con los cuadros buenos (0, 1, 4, 7, 8, 11), cada
~250 ms la punta cambia de forma y de largo: se lee como un salto. El cuerpo del arma se mueve bien: contra el casco va y
viene ±2 px de juego, suave, con el brazo al correr.

**Por qué** (`arma_correr_causa.png`): en el clip de correr (Kling, set toma 2 de correr) el disco cian de la boca está
prendido y Kling dispara un rayo cada ~7 cuadros. Para el atlas, `apagar_video.py --sin-rayos`:
1. borra los rayos (pinta del fondo un rectángulo delante de la boca y franjas arriba y abajo del caño);
2. pinta del gris del arma todo lo cian. Eso es el disco, pero también el halo de luz que deja el cañón prendido
   alrededor de la boca.

El halo gris queda como parte del arma, recortado en rectángulo donde terminaba el borrado del rayo. Pasa en los cuadros
de los rayos y en los de alrededor, donde el halo es más grande. No es el arma pegada aparte (`pegar_arma.py` no se usa
en el atlas), ni la alineación, ni la costura del loop (13 → 0 empalma), ni `boca_disparos.py` (sólo mide los tiros
parados, dos manos y agachado).

**En el juego** (`arma_correr_en_el_juego.png`, corriendo y corriendo con disparo, cada 1/12 s): a tamaño de juego la
tapa cambia de forma de un cuadro a otro. La boca que mide el juego para la bala y el fogonazo va de 49 a 54 px adelante
y de 58 a 69 arriba de los pies; eso es sobre todo el brazo y el rebote al correr, que están bien.

## Propuesta: gratis, sin toma nueva

`characters/lowpoly/tapa_correr.py`: en cada cuadro del clip sin rayos sigue el cuerpo del arma (la franja roja, que la
luz no cambia) con giro y corrimiento contra el cuadro 0 de run_gun (n14, que está bien). Después pinta del fondo la
tapa y el halo alrededor de la boca y pega ahí la tapa apagada del n14, girada y corrida como el arma de ese cuadro, con
una rampa de 14 px sobre el caño para que no se vea la unión. Resultado: la misma tapa en los 14 cuadros, con el arma
moviéndose igual que hoy (`arma_correr_*_aplicado.png`). (Antes de aplicarlo, se probó aparte en `work_revisar/`.)

Para aplicarlo (con el OK): el clip de `run_gun` pasa a `clips/retocado/correr_a_2_tapa.mp4` (sale de
`tapa_correr.py`), se rehace el atlas y se mira cuadro por cuadro sobre verde. Los cuadros del loop y el resto de las animaciones no cambian;
la boca que mide el juego se corre a lo sumo 1,6 px de juego. US$0.

Otra opción, también gratis: correr con los cuadros de carrera del slide nuevo (tanda 5, 0–41), que salió con el arma
apagada y sin rayos. Ese clip ya está aprobado como slide, pero es otra corrida (otra toma), así que Pablo la tendría que
ver primero.

## Hojas

| Hoja | Qué muestra |
|---|---|
| `arma_correr_tabla.png` | Los gráficos (el cuerpo del arma contra el casco; la punta contra el cuerpo) y la tabla por cuadro |
| `arma_correr_detalle.png` | El arma agrandada ×3 sobre verde, en orden de loop (13 → 0 al final); en rojo, los cuadros con la tapa mal |
| `arma_correr_juego.png` | El personaje entero a tamaño de juego ×1,5, sobre verde y oscuro, en orden de loop |
| `arma_correr_causa.png` | El mismo cuadro en el video de Kling, sin rayos y apagado |
| `arma_correr_en_el_juego.png` | Capturas del juego a 4K, corriendo (arriba) y corriendo con disparo (abajo) |
| `*_aplicado.png`, `arma_correr_antes_despues.png` | Lo mismo con la tapa arreglada, ya en el atlas |

Las hojas de ahora se rehacen con `uv run --project pipeline python characters/lowpoly/arma_correr.py --sufijo _aplicado
--tapas-bien` (sin opciones marca en rojo los cuadros de la lista TAPA, que eran los del atlas de antes).
