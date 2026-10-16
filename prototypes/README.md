# Juegos de prueba

Dos prototipos jugables para probar los sprites en movimiento, con teclado y mouse. Son una página HTML con un canvas, sin dependencias.

| Personaje | Artifact publicado | Qué prueba |
|---|---|---|
| comando | [Polígono del Comando](https://claude.ai/artifact/VUQhrtgp2HH4SRbuV68Yvm) | correr, saltar (como está o físico) y disparar |
| ranger | [Polígono del Ranger](https://claude.ai/artifact/NwSY6oEUuDF6DYJxpgXByF) | correr, saltar, colgarse de cornisas, saltar de una cornisa a otra y subir, disparar con una o dos manos, agachado y en el aire. Selector de feel: el del reporte de run-and-guns o el anterior |
| ranger, 4 jugadores | [Arena del Ranger](https://claude.ai/artifact/BGwyTTUFaUPVsNQCsQKg5s) | VS local de hasta 4 (dos en el teclado, joysticks y bots) en una arena de una pantalla con el kit de `backgrounds/ranger_industrial`: golpes con empujón, golpe de cerca, granadas con carga, power-ups de granadas y salud, 3 vidas por partida con reaparición e invulnerabilidad (parpadea) y un arma que se calienta y se traba. Los otros colores salen del atlas del ranger |

Los artifacts son privados: para que los vea alguien más, hay que compartirlos desde el menú Share de la página.

## Armar

```bash
uv run --project pipeline python prototypes/build.py ranger
```

Lee `characters/<personaje>/out/` (el atlas 1x y su JSON), mide por frame la boca del arma, la subida del salto y la mano del colgado, y deja `prototypes/<personaje>/dist/index.html` con el atlas al lado. Si cambiaron las animaciones, primero corré `spritepipe run` del personaje.

El ranger además lleva el fondo generado con `spritepipe gen-images` (ver "Fondos por API de imagen" en `pipeline/README.md`). Qué opción de cada asset se usa está en `BACKGROUNDS`, en `build.py`: el build las achica a 2 px por px del juego en `dist/bg/` (las capas en WebP, el kit y los props en PNG) y mete sus medidas en la página. Las capas de parallax llevan el lienzo del modelo al alto de la pantalla, alineadas abajo, con la posición que sale del recorte del post (`post.trim` en el `.json` de `raw/`). En la página, cada bloque se arma con las puntas del kit en los bordes, el tope repetido arriba y el cuerpo repetido abajo; las plataformas flotantes repiten un tramo del medio; el piso es el cuerpo repetido; los blancos son el `target` (chico en las latas) y la caja y el cartel son utilería sin colisión. La utilería de `backgrounds/ranger_props` (`deco` en `BACKGROUNDS`) sale de su `picked.json`: el decorado voluminoso va detrás de todo lo jugable y teñido hacia el violeta, y lo chico y fijo (balizas en el tope de los bloques, monitor con estática, tablero con chispas, dron) y los ventiladores en la cara de los bloques se animan por código (ver `backgrounds/ranger_props/integrar.md`). Las colisiones son las de siempre.

Los efectos del disparo del ranger salen de `FX`, en `build.py`: la hoja elegida de cada efecto y su tamaño en px del juego. El build achica las piezas de `backgrounds/ranger_fx/post/` a `dist/fx/` y mete en la página su tamaño y su ancla (la boca en el fogonazo, el contacto en el impacto). Esas carpetas están en `.gitignore`: las dos elegidas van al repo con `git add -f`.

`src.html` no tiene `<!doctype>` ni `<head>`, porque el publicador de artifacts los agrega. Para abrirlo local hace falta un navegador común (doble clic sobre `dist/index.html`), no el panel de archivos de la app de Claude, que no carga el PNG del atlas.

## La arena

```bash
uv run --project pipeline python prototypes/arena/build.py
```

Usa el mismo atlas y las mismas medidas que el polígono del ranger (`measure` de `prototypes/build.py`), las piezas del kit industrial que se eligieron en `backgrounds/ranger_industrial/kit.html` (`KIT` en `prototypes/arena/build.py`) y los efectos del polígono. Deja `prototypes/arena/dist/` con el atlas adentro de `index.html` (en base64), porque la página le lee los píxeles para sacar los colores de los otros tres jugadores y, abierta desde el disco, un PNG de al lado no lo permite.

Las reglas están arriba de `src.html`: `COMBAT` (empujón y golpe), `RESPAWN` (cuánto tarda en volver, cuánto dura la invulnerabilidad, que corta al disparar, y el haz que avisa dónde), `HEAT` (cuánto calienta cada disparo y cuánto tarda en enfriarse, normal y trabada), `GRENADE`, `MELEE` y `PICKUP`.

- **Golpe de cerca** (`MELEE`): Q o U en el teclado izquierdo, M o Num 4 en el derecho, LT (L2, ZL) en el joystick. Un puñetazo adelante que llega 72 px más allá del cuerpo, a la altura del cuerpo, en el piso o en el aire: saca 1, empuja 780 px/s (el disparo de dos manos, 560), levanta 420, aturde 0,4 s y congela el juego 0,07 s al conectar. Hay uno cada 0,5 s. Cubre el hueco del tiro a quemarropa, porque la bala sale ~100 px delante del cuerpo. No hay clip de melee: usa los cuadros 1 (el puño atrás), 3 (el brazo adelante, que es cuando pega) y 16 a 18 de `throw` (`MELEE_SEQ`), con un envión del cuerpo, un barrido y una estrella dibujados por código. Los bots pegan cuando tienen al otro encima, a la misma altura, y en vez de alejarse se quedan.
- **Power-ups** (`PICKUP`): el primero sale a los 9 s (en la prueba, a los 3) y después uno cada 12 a 18 s. Hay como mucho 2 a la vez, o 1 con dos jugadores o en la prueba. Cada uno aparece en la cara de arriba de algo que se pisa o en un lugar de salida, sin las plataformas que se mueven, a 90 px de las paredes, con lugar arriba y lejos de los jugadores. Antes de aparecer lo avisa un haz angosto de su color durante 0,75 s. Flota, late y, si nadie lo agarra, los últimos 3 de sus 12 s parpadea y se va. El amarillo con la granada recarga las 5; el blanco con la cruz suma un tercio de la salud, al menos 1 (+1 con 3 golpes, +2 con 5; con 1 golpe no sale). Se agarra tocándolo, y si al que lo toca no le sirve, queda ahí; en la prueba se agarra siempre. Se dibujan por código. Los bots que lo necesitan a veces van a buscarlo (`wantedPickup`): más seguido cuanto más cerca está, y casi siempre si les queda un golpe.
- **Color de la arena** (`color` en el JSON de la arena): `{fondo: {paleta, saturacion, contraste, brillo, bruma}, plataformas: {...}, bruma_color}`. El juego gradúa al prearmar, píxel a píxel, con `gradePixels` de `prototypes/arena/color.js`, que es la misma función que usa el editor y que `build.py` mete en la página. El orden es: la paleta de Pablo (un LUT de 17³ que `paleta.py` saca de `refs/refineria.webp` → `refs/refineria_paleta_pablo.webp` en cada build), después saturación, contraste y brillo (1 es neutro) y por último la mezcla hacia la bruma. Sin `bruma_color`, la bruma es el promedio del sexto de arriba de la lámina, achicada a 96 × 54; sin lámina, `[143, 179, 224]`. Es la misma cuenta que hace el editor. Fondo es la lámina; con el kit, el cielo, las capas y el decorado de atrás. Plataformas son los recortes de `plate.solid`, las piezas pintadas y los objetos del kit (su imagen graduada queda guardada); con el kit, además, el relleno, las caras, los puentes, las flotantes y los caños. Sin `color` no se gradúa nada. Graduar tarda ~0,2 s y pasa sólo al prearmar. `setArenaColor(c)` lo cambia en vivo desde la consola.
- **HUD**: las tarjetas de arriba van al 70% de su tamaño original (`HUD_K`), con todo escalado y centradas. Las granadas que quedan se ven debajo de la barra de cada uno, con el dibujo de la granada. `build.py` la exporta a 3 px por px del juego (`kit/grenade-grenade-hud.png`) para que no se vea borrosa, y las gastadas van en sombra. En la prueba se ve una sola con ∞.

Cada `prototypes/arena/arenas/<nombre>.json` aparece en el menú para elegir (todas de 1920 × 1080). Una arena puede ser de dos maneras. Con el kit, como Fundición, el juego arma cada pasarela con las piezas. Pintada, como Refinería, `plate` es una lámina de 1920 × 1080 que va de fondo, y `plate.solid` son los recortes que van delante del colgado. Encima de las dos van los `objects`, piezas del kit con su propia colisión:

- Las cajas y las demás piezas llevan `x` en el centro e `y` en la base. Con `solid: false` no chocan y van detrás, oscurecidas.
- Las plataformas (`platforms/*`) llevan en `y` lo que se pisa. Con `move: {path, speed, wait}` van y vuelven por esos puntos y llevan a quien esté encima.

En `solids`, `ledge` (`both`, `left`, `right` o `none`) dice de qué bordes uno se puede colgar. En el menú, "Probar arena solo" entra sin bots y sin final de partida: R cambia de lugar de salida y H muestra lo que se pisa. La de hoy es `fundicion.json`, en px del juego. `solids` es lo que se pisa: pasarelas con relleno de vigas y el puente. `platforms` son las flotantes y las repisas, que se atraviesan desde abajo y con abajo + saltar. Además están los lugares de salida, el decorado y los caños. El tope de las pasarelas, el relleno y las patas se eligen solos con la semilla, así que para cambiar la arena alcanza con mover rectángulos en el JSON y volver a armar.

Los bots están en `botInput`, en `prototypes/arena/src.html`: persiguen al más cercano, suben por donde pueden, disparan cuando lo tienen en la línea de la boca, golpean si lo tienen encima, a veces esquivan o van por un power-up que les sirve y cada tanto van a buscar altura. El nivel se elige en el menú, y `BOT_LEVELS` tiene los tiempos de reacción, las ráfagas y la probabilidad de esquivar de cada uno.

Para jugar con joysticks, abrí el juego local en Chrome: la página publicada no deja leer controles.

```bash
open -a "Google Chrome" prototypes/arena/dist/index.html
```

## Jugar con un control

El ranger acepta control (Gamepad API, mapping estándar: Xbox, PlayStation y la mayoría de los genéricos). Stick izquierdo o cruceta para correr y agacharse, A para saltar (otra vez en el aire, doble salto), X o RT para disparar, B o RB para disparar con las dos manos y Vista para las guías. El estado del control aparece abajo de los controles.

Para probarlo, abrí el juego local en Chrome, no la página publicada: la vista de artifacts puede no dejar leer controles.

```bash
open -a "Google Chrome" prototypes/ranger/dist/index.html
```

Con el control conectado, apretá cualquier botón: el navegador no lo muestra hasta que lo usás, y ese primer botón arranca el juego.

## Qué es provisorio

- Ranger: con el run "Anterior", al correr dispara desde la mano que balancea. La subida a la cornisa usa 10 de los 22 frames del clip (`CLIMB_SEQ` en `src.html`), con un avance por frame para que las rodillas apoyen en el canto.
- Los efectos (rayos, chispas, vainas, sombra) son de código. En el ranger, el fogonazo y el impacto son dibujos de GPT Image (`backgrounds/ranger_fx`, elegidos en [`fx_lab`](fx_lab/README.md)) con el halo, el destello y las chispas por código. El fogonazo va pegado a la boca del frame en pantalla. El frame de disparo que trae el destello del clip se cambia por el anterior (`noBaked` en `src.html`), hasta que `remove_flash` corra sobre los clips de disparo del ranger.
- Ranger: la capa `near` va oscurecida y corrida al violeta por código (`NEAR_TINT`) para que no compita con la capa de juego, y el impacto en los blancos es la misma imagen teñida. Las franjas de las puntas del kit no empalman con las del tope: la junta se tapa con una línea de contorno.
