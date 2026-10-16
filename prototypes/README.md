# Juegos de prueba

Dos prototipos jugables para probar los sprites en movimiento, con teclado y mouse. Son una página HTML con un canvas, sin dependencias.

| Personaje | Artifact publicado | Qué prueba |
|---|---|---|
| comando | [Polígono del Comando](https://claude.ai/artifact/VUQhrtgp2HH4SRbuV68Yvm) | correr, saltar (como está o físico) y disparar |
| ranger | [Polígono del Ranger](https://claude.ai/artifact/NwSY6oEUuDF6DYJxpgXByF) | correr, saltar, colgarse de cornisas, saltar de una cornisa a otra y subir, disparar con una o dos manos, agachado y en el aire. Selector de feel: el del reporte de run-and-guns o el anterior |

Los artifacts son privados: para que los vea alguien más, hay que compartirlos desde el menú Share de la página.

## Armar

```bash
uv run --project pipeline python prototypes/build.py ranger
```

Lee `characters/<personaje>/out/` (el atlas 1x y su JSON), mide por frame la boca del arma, la subida del salto y la mano del colgado, y deja `prototypes/<personaje>/dist/index.html` con el atlas al lado. Si cambiaron las animaciones, primero corré `spritepipe run` del personaje.

El ranger además lleva el fondo generado con `spritepipe gen-images` (ver "Fondos por API de imagen" en `pipeline/README.md`). Qué opción de cada asset se usa está en `BACKGROUNDS`, en `build.py`: el build las achica a 2 px por px del juego en `dist/bg/` (las capas en WebP, el kit y los props en PNG) y mete sus medidas en la página. Las capas de parallax llevan el lienzo del modelo al alto de la pantalla, alineadas abajo, con la posición que sale del recorte del post (`post.trim` en el `.json` de `raw/`). En la página, cada bloque se arma con las puntas del kit en los bordes, el tope repetido arriba y el cuerpo repetido abajo; las plataformas flotantes repiten un tramo del medio; el piso es el cuerpo repetido; los blancos son el `target` (chico en las latas) y la caja y el cartel son utilería sin colisión. La utilería de `backgrounds/ranger_props` (`deco` en `BACKGROUNDS`) sale de su `picked.json`: el decorado voluminoso va detrás de todo lo jugable y teñido hacia el violeta, y lo chico y fijo (balizas en el tope de los bloques, monitor con estática, tablero con chispas, dron) y los ventiladores en la cara de los bloques se animan por código (ver `backgrounds/ranger_props/integrar.md`). Las colisiones son las de siempre.

Los efectos del disparo del ranger salen de `FX`, en `build.py`: la hoja elegida de cada efecto y su tamaño en px del juego. El build achica las piezas de `backgrounds/ranger_fx/post/` a `dist/fx/` y mete en la página su tamaño y su ancla (la boca en el fogonazo, el contacto en el impacto). Esas carpetas están en `.gitignore`: las dos elegidas van al repo con `git add -f`.

`src.html` no tiene `<!doctype>` ni `<head>`, porque el publicador de artifacts los agrega. Para abrirlo local hace falta un navegador común (doble clic sobre `dist/index.html`), no el panel de archivos de la app de Claude, que no carga el PNG del atlas.

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
