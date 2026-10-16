# ranger_props: props de prueba

Tamaño en px del juego (vista de 960×540, piso en y = 474, el ranger al 80% mide 102 px). Cada hoja va a su propia escala: la pieza ancla al alto de `ANCHOR` en `build_page.py`. Capa: *fondo* es detrás de todo lo jugable, a la velocidad del mundo y con un tinte violeta; *juego* es el plano del ranger. **Elegida** es la opción que quedó (2026-10-16). Abrí `props.html` para verlos en la escena y en el nivel, y `integrar.md` para meterlos al prototipo.

| prop | hoja | tipo | capa | opción 1 (px) | opción 2 (px) | elegida | idea |
|---|---|---|---|---|---|---|---|
| `barrel` | low_a | decorado | fondo | 35×50 | 34×50 | 2 | Barril de acero. Al fondo, al lado de los explosivos: el rojo es el que se rompe. |
| `explosive_barrel` | low_a | función | juego · blanco | 35×50 | 33×50 | 2 | Blanco: con dos tiros revienta (burst naranja y rojo grande, shake). Más adelante, daño en área. |
| `crate_breakable` | low_a | función | juego · blanco | 38×32 | 43×28 | 2 | Blanco con hp, como el tablero; al romperse, astillas con burst(). |
| `cable_coil` | low_a | decorado | fondo | 48×17 | 46×18 | 1 | Rollo de cable al pie de la antena o de la consola. |
| `beacon_off` | low_b | vida | juego · tope de bloques | 31×30 | 30×30 | 2 | Baliza apagada: alterna con la prendida. |
| `beacon_on` | low_b | vida | juego · tope de bloques | 37×40 | 45×42 | 2 | Baliza prendida, con su halo: parpadeo cada ~0,5 s, desfasadas entre sí. |
| `switch_off` | low_b | función | juego · puerta | 29×72 | 35×74 | 1 | Interruptor: al dispararle pasa a on y abre la puerta. |
| `switch_on` | low_b | función | juego · puerta | 29×63 | 35×63 | 1 | El interruptor accionado. |
| `drone` | low_b | vida | juego | 53×34 | 76×41 | 1 | Dron estacionado en su base; más adelante puede despegar cuando el ranger se acerca. |
| `console` | mid_a | decorado | fondo | 96×70 | 107×70 | 2 | Consola con pantallas. |
| `fuel_tank` | mid_a | decorado | fondo | 107×74 | 108×75 | 2 | Tanque de combustible. |
| `turret_off` | mid_a | decorado | fondo | 74×78 | 87×112 | 2 | Torreta apagada; más adelante, un enemigo que se prende y pasa al juego. |
| `crate_stack` | mid_a | decorado | fondo | 74×90 | 74×82 | 1 | Cajas apiladas. Si se quieren en el juego, como sólido que se sube. |
| `monitor_off` | mid_b | vida | juego | 52×64 | 53×64 | 1 | Monitor apagado: alterna con la estática. |
| `monitor_static` | mid_b | vida | juego | 52×64 | 53×64 | 1 | Estática: se anima espejando la pantalla cada ~80 ms y a ratos se apaga. |
| `panel_spark` | mid_b | vida | juego | 60×66 | 54×79 | 2 | Tablero abierto: chispas cian con burst() cada 0,6–2 s. |
| `fan_housing` | mid_b | vida | juego · cara de un bloque | 59×57 | 50×49 | 2 | Marco del ventilador, pegado a la cara de un bloque. |
| `fan_blades` | mid_b | vida | juego · cara de un bloque | 53×53 | 43×41 | 2 | Aspas: giran por código dentro del marco (escaladas al hueco). |
| `antenna` | tall | decorado | fondo | 91×248 | 93×240 | 2 | Mástil de comunicaciones, detrás de la capa de juego. |
| `signboard` | tall | decorado | fondo | 124×131 | 125×141 | 2 | Cartel de la base con emblema. |
| `door_frame` | tall | función | juego · puerta | 147×140 | 150×140 | 1 | Marco de la puerta: detrás del ranger, adelante de la hoja. |
| `door_leaf` | tall | función | juego · puerta | 83×117 | 76×127 | 1 | Hoja: sólido que corta el paso; sube detrás del marco cuando se acciona el interruptor. |

Escala de cada hoja (px del juego por px de la hoja): low_a 0.07837 / 0.07429, low_b 0.10169 / 0.12712, mid_a 0.15184 / 0.16204, mid_b 0.13823 / 0.11636, tall 0.20057 / 0.2026.
