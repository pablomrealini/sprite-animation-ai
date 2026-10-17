# spritepipe

Convierte clips de image-to-video (Veo, Seedance, Kling, Omni, etc.) en sprite sheets listos para el engine. Implementa los pasos 4 a 12 del reporte [Animación 2D con IA para sprites](../reports/Animación%202D%20con%20IA%20para%20sprites.md), salvo la limpieza humana (paso 11), que se hace a mano y se enchufa por la carpeta `cleanup/`. Generar el clip (paso 3) queda afuera: `pad-pose` prepara la imagen que se le pasa al modelo y el pipeline arranca en el `.mp4`. La excepción es el bake-off (paso 0): `bakeoff` manda la misma pose a varios modelos por API y compara los clips con el QA. Los fondos del escenario salen de `gen-images`, que los genera por API de imagen y les hace el post.

Todo es local y determinístico: la misma config sobre el mismo clip da los mismos PNG. Cambiar tamaño, fps o paleta nunca obliga a regenerar video.

## Uso

Requiere `ffmpeg` y `uv` (los dos por Homebrew). Desde la raíz del repo:

```bash
uv run --project pipeline spritepipe run characters/synthetic/character.toml
```

Para armar la pose que se le pasa al modelo de video desde el concept de ChatGPT (PNG o WebP con transparencia): canvas 1920×1080 magenta, personaje al 48% del alto, pies al 72% y sin la sombra de piso. Para saltos, `--feet 0.92` deja aire arriba:

```bash
uv run --project pipeline spritepipe pad-pose poses/comando_concept.webp poses/comando_master_magenta_16x9.png
```

Si los concepts vienen aplanados sobre blanco (sin transparencia, con la línea de sombra debajo de las botas), `clean-concepts` arma el plantel: saca fondo, sombra y basura suelta, y deja todos los personajes en un canvas común de 512×512 a escala nativa, con los pies en la misma fila y las botas centradas (el pivot). Además arma en `magenta/` la pose 16:9 de cada uno con una sola escala para todo el plantel, lista para el modelo de video:

```bash
uv run --project pipeline spritepipe clean-concepts poses/roster/src/*.png --out poses/roster
```

Para mirar la limpieza previa de un clip suelto, sin config (ver [Limpieza previa](#limpieza-previa)). En un personaje no hace falta: alcanza con `clean` en la config.

```bash
uv run --project pipeline spritepipe clean characters/ranger/clips/raw/r04.mp4 /tmp/r04_limpio.mp4 --cut-muzzle --color-matrix bt601
```

Para sacar el fogonazo de un clip suelto, sin config. Escribe un H.264 sin pérdida y la boca del cañón por frame en `shoot_noflash.muzzle.json`. En un personaje no hace falta: alcanza con `remove_flash` en la config (ver abajo).

```bash
uv run --project pipeline spritepipe remove-flash clips/shoot.mp4 clips/shoot_noflash.mp4
```

Para comparar clips sueltos (QA y búsqueda de loop, sin config):

```bash
uv run --project pipeline spritepipe check clips/veo_walk.mp4 clips/kling_walk.mp4 --pose poses/walk.png
```

Para el bake-off de modelos por API (ver [Bake-off](#bake-off)). Sin keys en el entorno sólo muestra los pedidos y el costo:

```bash
uv run --project pipeline spritepipe bakeoff characters/comando/bakeoff.toml --dry-run
```

Para generar fondos por API de imagen (style frame, capas de parallax, kit de plataformas y props) con el estilo del personaje, en varios modelos a la vez (ver [Fondos por API de imagen](#fondos-por-api-de-imagen)). Sin keys sólo muestra los pedidos, los prompts y el costo:

```bash
uv run --project pipeline spritepipe gen-images backgrounds/ranger_base/gen.toml --dry-run
```

Para regenerar los clips sintéticos de prueba:

```bash
uv run --project pipeline spritepipe synth characters/synthetic
```

Los tests:

```bash
uv run --project pipeline pytest pipeline/tests
```

El resultado se revisa en `characters/<personaje>/out/preview.html`: todas las animaciones en loop con su timing real, pivot, línea de piso, flipX, onion skin y fondos. Con doble clic se abre desde el disco.

## Un personaje nuevo

```text
characters/soldado/
  character.toml     copia de characters/TEMPLATE.toml
  bakeoff.toml       opcional: bake-off de modelos por API (ver Bake-off)
  clips/             los .mp4 tal como salen del modelo (el ranger los tiene en clips/raw/)
  poses/             el concept y la imagen que se le pasó como primer frame (pad-pose; la usa el QA)
  prompts/           el prompt de cada clip (va al registro de procedencia)
  cleanup/<anim>/    frames limpiados a mano que reemplazan a los de 1x (opcional)
```

## Qué hace cada etapa

| Paso del reporte | Módulo | Qué hace |
|---|---|---|
| 1. Plantel | `concept.py` (`clean-concepts`) | Concept sobre blanco a RGBA: fondo = lo casi blanco y neutro conectado al borde (los blancos del personaje quedan encerrados por el contorno), borde desmezclado contra el blanco suponiendo contorno negro, línea de sombra = rachas de tinta de 8 px o menos en la franja del piso, basura = todo lo que no es la componente más grande. Canvas común a escala nativa, pies en la misma fila, botas centradas. |
| 1-2. Pose | `pose.py` (`pad-pose`) | Concept RGBA a un canvas 16:9 de color plano para el modelo de video: bbox sobre el alfa opaco, sin ruido de alfa ni sombra de piso (lo semitransparente en la franja de los pies), personaje al 48% del alto, centrado, con la línea de pies configurable. |
| 5a. Limpieza | `clean.py` (`clean`) | Opcional, antes de todo lo demás. Fondo por fila (aguanta degradés y barras), sombra de piso como fondo, sólo el componente más grande más el cian que lo toca, corte en la boca del arma, utilería que cruza el cuadro. Un color de fondo único. El clip limpio se cachea en `work/00_clean/`. Ver [Limpieza previa](#limpieza-previa). |
| 5. Extraer | `imgio.extract` | Todos los frames nativos a PNG, con la matriz de color explícita: la del tag del video, `color_matrix` si la config la declara, o BT.709. |
| 5b. Fogonazo | `flash.py` (`remove_flash`) | Opcional, en clips de disparo. Por frame, la boca es el contorno oscuro más a la derecha en la franja del arma; pinta con el color de fondo todo lo que está delante y el halo de arriba y de abajo del cañón, y guarda la boca por frame. La geometría del arma va en la config en px del clip, o se mide en el frame 0. Después de alinear, la boca pasa a px de celda: `out/fx/<anim>_muzzle.json`. |
| 4. QA | `qa.py` | Frame 0 contra la pose, deriva y zoom de cámara, personaje que toca el borde, cortes de escena, fondo sucio, clip casi quieto. Veredicto `ok`/`warn`/`fail`; con `--strict` corta en `fail`. |
| 6. Loop | `select.py` | En ciclos, busca el inicio y el largo con la costura más chica relativa al movimiento, comparando ventanas de tres frames para no confundir poses que van en sentido contrario. El largo es múltiplo de K. En oneshots recorta la cola quieta. |
| 9. fps | `decimate.py` | Decimación por factor entero (24→12 es K=2, 24→8 es K=3); en oneshots, el frame más nítido de cada grupo. Holds como duración por frame. Corre antes del key para no procesar frames que se tiran. |
| 7. Fondo | `key.py` | Verde o magenta: keyer por diferencia de color, unmix del borde y despill en una banda. Fondo blanco, gris o crema: distancia ΔE en Lab en modo connected. |
| 8. Alinear | `align.py` | Primero lleva cada clip a los px de video de la animación de referencia (ver [Escala por clip](#escala-por-clip)). Después, piso = fila opaca más baja, ancla = centroide del alfa. En ciclos saca la deriva de cámara medida entre ciclos consecutivos del clip; en oneshots fija el frame 0. Un canvas simétrico y un pivot abajo al centro para todas las animaciones. |
| 10. Reducir | `reduce.py` | HD: una sola reducción, en alfa premultiplicado, más variantes (0,5×). Pixel: factor entero, una paleta k-means común a todo el personaje, sin dithering, alfa binario. |
| 12. Empaquetar | `pack.py` | Atlas MaxRects con trim, extrude 1, padding 2, frames duplicados fusionados y multipack. También una grilla sin trim por animación y previews APNG. |

## Salidas

En `out/`:

- `<personaje>_<escala>-N.png` y `.json`: el atlas en formato JSON (Hash) de TexturePacker, con `spriteSourceSize`, `sourceSize`, `pivot` y `duration` por frame, más `animations` con los nombres de frame por animación.
- `<personaje>.json`: índice con fps, canvas, pivot y, por animación, frames, duraciones y loop.
- `sheets/<escala>/<anim>.png` y `.json`: grilla sin trim (celda = canvas). Es lo más fácil de importar sin plugins.
- `previews/<escala>/<anim>.png`: APNG en loop con el timing real.
- `preview.html`: el visor.
- `fx/<anim>_muzzle.json` (sólo con `remove_flash`): la boca del cañón por frame y por escala, en px de la celda (origen arriba a la izquierda) y relativa al pivot (`dx`, `dy`, y hacia abajo), para anclar el fogonazo que dibuja el engine. Con flipX, invertí `dx`. El índice lo lista en `fx`.
- `provenance.json`: clip y su hash, modelo, prompt, pose, resultado del QA, loop elegido, escala del clip (`scale`), limpieza previa (`clean`: el clip limpio, sus parámetros y lo medido), geometría del fogonazo, parámetros y versiones. Es el registro de autoría que pide la sección legal del reporte.
- `palette.png` (sólo pixel art).

## Importar en el engine

El pivot del JSON está normalizado con origen arriba a la izquierda (convención de TexturePacker).

- **Unity**: importá `sheets/1x/<anim>.png` como Sprite (Multiple), Slice → Grid By Cell Size con la celda del JSON, pivot Custom `(0.5, 1 - pivot.y)` porque Unity mide desde abajo, filtro Bilinear sin mipmaps (Point sin compresión en pixel art).
- **Godot 4**: AnimatedSprite2D, SpriteFrames → "Add frames from a Sprite Sheet" con `cols`×`rows` del JSON y `offset.y = alto_celda/2 - pivot_px.y` para que el nodo quede en los pies. En HD, activá Fix Alpha Border en el import.
- **Phaser**: `this.load.atlas(key, 'soldado_1x-0.png', 'soldado_1x-0.json')` y armá las animaciones con los nombres de `<personaje>.json` (`walk/0000`, ...) y `frameRate` igual al fps del índice; `setOrigin(0.5, pivot.y)`.

Nada de esto se probó todavía dentro de los engines: se probó que el atlas reconstruye cada frame bit a bit.

## Sacar el fogonazo

Los modelos de video dibujan el fogonazo aunque el prompt diga que no. Dentro del sprite trae dos problemas: el brillo se mezcla con el fondo y queda con borde rosado al keyear, y agranda la celda de todo el personaje. Con `remove_flash` el pipeline lo borra antes del key, a resolución de video, y exporta dónde está la boca para que el engine dibuje su propio efecto:

```toml
[[animation]]
name = "shoot"
clip = "clips/shoot.mp4"   # el clip tal como salió, con fogonazo
remove_flash = true        # la geometría del arma se mide en el frame 0

# o, si la detección falla, la geometría a mano en px del clip (lo que falte se mide):
# [animation.remove_flash]
# band_y = [235, 275]      # filas donde se busca el contorno oscuro del cañón
# search_x = [500, 620]    # columnas donde puede estar la boca
# flash_y = [195, 320]     # filas que puede ocupar el fogonazo
# halo_x0 = 538            # desde acá hasta la boca sólo hay cañón: ni mano ni mira
```

Para personajes **sin contorno** (el low-poly), el contorno oscuro no marca la boca: la boca es una tapa con un disco cian y el rayo sale pegado al disco. Ahí va `remove_flash = { method = "shape" }`, que sigue el arma con su forma del frame 0 (sin la punta) y borra lo que está delante de la boca (±40% del alto del cuerpo, por la estrella del fogonazo) y el halo arriba y abajo del cañón. Si la coincidencia se pierde (el destello tapa el arma: más de ΔE 25 de error medio), busca el arma en todo el cuadro y, si tampoco aparece, la deja donde estaba; esos frames salen en el log. Con un personaje que gira o da vueltas no sirve: ahí conviene recortar los frames con rayo. Lo mejor, igual, es que el video no traiga fogonazo: ver "Prueba sin fogonazo" en `characters/lowpoly/reporte_idle.md` (con Kling, el video sólo apunta y el arma va apagada).

Los frames sin fogonazo quedan en `work/<anim>/01_noflash/`, con la boca por frame en px del video en `muzzle.json`. No se re-encodea: el resto del pipeline lee esos PNG. `characters/comando` es el ejemplo real.

## Limpieza previa

Davinci devuelve fondos magenta apagados, a veces en degradé, con sombra de piso, y con cosas que el prompt no pidió: rayos y chispas, humo, una barra o una cornisa dibujadas, a veces el personaje en otra escala. Nada de eso se keyea bien. Con `clean`, el pipeline limpia el clip frame por frame antes de todo lo demás:

1. **Fondo por fila.** Fila por fila, la mediana de la franja de 24 px del borde izquierdo o la del derecho, la que más se parezca al fondo típico del frame, así aguanta degradés y un rayo o una barra que llegan a un solo borde. Las filas donde las dos franjas se alejan del fondo típico en más de 70 (suma de RGB), como una barra que cruza todo el cuadro, se interpolan entre las de arriba y las de abajo.
2. **Sombra de piso.** Es fondo todo lo que tiene el croma del fondo de su fila con entre 0,15 y 1,2 veces su luminancia: la sombra es del mismo tono pero más oscura.
3. **Efectos.** Queda sólo el componente conexo más grande (el personaje) sin contar el cian, más el cian que lo toca (la punta de la pistola). Rayos sueltos, chispas, humo y restos se van. Todo lo que no queda se pinta de un solo color, la mediana de los bordes en todo el clip.
4. **`cut_muzzle`**: un rayo con centro blanco que sale de la boca toca el arma y cuenta como personaje. Por eso se corta todo lo que queda delante de la boca, medida como el percentil 30 del borde derecho del personaje en los frames con el brazo extendido (los que pasan en más de 15 px al de los primeros 5 frames). Los frames con el rayo pegado dan bordes más lejanos y no mueven el percentil. Antes del corte vuelve el cian a menos de 20 px del cuerpo: en los frames de disparo el arma brilla cian y, sin eso, queda con agujeros. **`cut_left`** corta además lo que cruza por detrás: todo lo que está 25 px a la izquierda del borde izquierdo típico del personaje.
5. **`prop_rows`**: utilería dibujada que cruza el cuadro, como la barra de la que se cuelga. En las filas con personaje en más del 35% del ancho (la barra del ranger arranca en la mano y ocupa del 43% al 64%; el cuerpo colgado, hasta 26%), se borra desde cada borde mientras sea gris oscuro o negro, frenando en el casco o el guante. Lo que queda en esas filas fuera de las columnas del cuerpo también es barra, y los restos finos lejos de las partes gruesas del cuerpo se van.

La limpieza no re-escala. Si un clip trae al personaje en otra escala, declará `body_height_px` (ver [Escala por clip](#escala-por-clip)). El clip limpio queda en `work/00_clean/<clip>-<hash>.mp4` (H.264 sin pérdida, yuv444p, BT.709), con un JSON al lado con lo medido. Se reusa mientras no cambien el video, los parámetros, `color_matrix` ni `CLEAN_VERSION` en `clean.py`, que hay que subir si cambia el algoritmo. El log muestra el color de fondo, la boca medida y cuántos px se sacaron, y `(del cache)` cuando no lo rehízo.

### Varias animaciones de un clip

Un `[[clip]]` describe un video del que salen varias animaciones: archivo, limpieza, matriz de color, pose, modelo, prompt y escala. La animación que lo nombra en `clip` hereda todo eso y puede pisar cualquier valor. El clip se limpia una sola vez por corrida. `clip` también puede seguir siendo la ruta de un video, con `clean` en la propia animación (`clean = true` o una tabla `[animation.clean]`).

```toml
[[clip]]
name = "shoot2h"              # r02: disparo a dos manos
file = "clips/raw/r02.mp4"
color_matrix = "bt601"        # Davinci: video sin tag, codificado en BT.601
clean = { cut_muzzle = true } # o clean = true, o [clip.clean] con cut_muzzle, cut_left y prop_rows
body_height_px = 606          # viene ~27% más grande que el run
model = "seedance-2.0"
prompt = "prompts/shoot2h.txt"

[[animation]]
name = "shoot2h_in"
clip = "shoot2h"
kind = "oneshot"
trim = [6, 14]

[[animation]]
name = "shoot2h_out"          # la vuelta a una mano: el mismo tramo, al revés
clip = "shoot2h"
kind = "oneshot"
trim = [6, 14]
reverse = true
```

Con **`frames = [30, 31, 32, 29]`** (sólo oneshot, con `loop = true` si va en loop), la animación sale de esos frames nativos, en ese orden y uno por frame de salida, sin decimar. Sirve para armar una animación con tramos de partes distintas del clip: en el low-poly, cada disparo es el tiro del video (cañón prendido, destello y retroceso) y termina en un frame de antes del tiro, apuntando con el cañón apagado, que es donde la arena se queda en reposo. No va junto con `trim`.

Con **`reverse = true`**, el tramo elegido (`trim` en oneshots, el loop en ciclos) se reproduce al revés. Los frames se numeran como en el clip original, así que el tramo es el mismo que se ve en el reproductor. En oneshots, la cola quieta que se recorta es la del final de la animación, o sea el principio del tramo. En ciclos, la deriva de cámara se invierte.

### La matriz de color

Los clips de Davinci vienen sin tag de color y, sin tag, el pipeline supone BT.709. Pero comparando el frame 0 de los clips del ranger con su concept, BT.601 queda más cerca en los cinco clips que respetan la pose (en los colores saturados, diferencia mediana de 5–8 contra 9–11 sobre 255): con BT.709 el rojo se corre hacia el naranja. Por eso los clips del ranger declaran `color_matrix = "bt601"`. Vale para `[[clip]]` y `[[animation]]`, con o sin limpieza, y sólo afecta cómo se decodifica el video.

## Escala por clip

`target_height` lleva el cuerpo de la animación de referencia (`scale_reference`) a ese alto en px finales. Si todos los clips traen al personaje al mismo tamaño en px, alcanza con una sola escala. Eso deja de cumplirse cuando los clips salen de poses distintas o el modelo los devuelve en otra resolución. En el ranger, el run viejo era de 560×752 con el cuerpo a ~505 px, y un clip desde la pose 16:9 vuelve a 864×496 con ~235 px. Con una sola escala, ese clip saldría a 60 px en vez de 128.

Por eso, antes de armar el canvas común, cada clip se re-escala a los px de video de la referencia. La escala es cuerpo de la referencia / cuerpo del clip, donde el cuerpo es el alto del personaje parado en px del video de cada clip. Hay tres formas de declararlo en la `[[animation]]`:

```toml
[[animation]]
name = "jump"
clip = "clips/jump.mp4"
pose = "../../poses/ranger_jump_magenta_16x9.png"   # alcanza si la pose es de cuerpo parado

[[animation]]
name = "climb"
clip = "clips/climb.mp4"
pose = "../../poses/ranger_climb_magenta_16x9.png"  # arranca colgado: el bbox de la pose no es el cuerpo parado
pose_body_height_px = 440   # cuánto mediría parado en px de la pose, a la escala en que se armó (ejemplo)
# o: scale_pose = "../../poses/ranger_parado_chico_16x9.png"   # una pose parada armada a la misma escala

[[animation]]
name = "crouch_shoot"
clip = "clips/crouch_shoot.mp4"
body_height_px = 603        # a mano: el alto parado en px del video de este clip
```

- **Con `pose`**, si el frame 0 coincide con la pose (el QA no da `fail` en el MAD), el cuerpo sale de comparar el alto del frame 0 con el de la pose: cuerpo = frame 0 × parado / pose. Parado es el alto de la misma pose, el de `scale_pose` o `pose_body_height_px`. La resolución que devuelva el modelo no importa. Si el frame 0 no coincide con la pose, el log lo avisa y el clip queda como si no declarara nada.
- **Si la pose no es de cuerpo parado** (colgado, agachado, en el aire) y no se declara `scale_pose` ni `pose_body_height_px`, el pipeline toma el alto de esa pose como si fuera el cuerpo parado, y el clip sale mal escalado. Para detectarlo, el log muestra la escala de cada clip y a cuántos px finales queda el cuerpo.
- **`body_height_px`** en la animación pisa todo lo demás y se aplica siempre.
- **Sin nada declarado**, el clip queda a la escala de la referencia (×1), como antes. Si su frame 0 mide más de un 10% distinto que el de la referencia, el log lo avisa con `!` y dice a cuántos px va a salir.
- **El cuerpo de la referencia** es el que declare la animación de referencia (con `pose` o `body_height_px`). Si no declara nada, es el alto de referencia que se lleva a `target_height` (`body_height_px` de `[character]` o la mediana medida en la animación). Si la referencia es un run, el cuerpo parado de los demás clips sale a la altura media del run. Para que salga a la altura parada, declarale al run su `body_height_px` parado.
- **Clips de la misma pose**: si las poses tienen el mismo tamaño y el mismo alto parado, y los clips vuelven en la misma resolución, comparten una sola escala (la de la referencia, si está entre ellos, o la mediana). La diferencia que se mida entre sus frames 0 es ruido del re-render del modelo. Además, una escala sacada de la pose a menos de un 2% de 1 se deja en 1. Por eso el comando, cuyos clips tienen todos `pose`, sigue saliendo igual.

Los frames re-escalados quedan en `work/<anim>/03_scaled/`, en alfa premultiplicado (Lanczos para agrandar, área para achicar). El canvas, el pivot y la línea de piso se calculan después, sobre ellos, y la deriva de cámara y la boca del fogonazo se pasan a la escala nueva. Un clip agrandado se re-muestrea dos veces (acá y al reducir), así que queda un poco más blando que uno que viene a la resolución de la referencia. En `provenance.json`, `animations.<anim>.scale` registra lo medido y la escala aplicada.

## Bake-off

El paso 0 del reporte: la misma pose y el mismo prompt en varios modelos image-to-video, para elegir con datos y no con el clip más lindo. `spritepipe bakeoff` lee una config (`characters/comando/bakeoff.toml` es el ejemplo), manda los pedidos por API, baja cada clip apenas termina y les corre el mismo QA que `check`.

### Las keys

Las keys se leen sólo de dos variables de entorno, `FAL_KEY` y `GEMINI_API_KEY`. No van en la config, en un `.env` ni en ningún archivo del repo, y el comando nunca las imprime ni las guarda. Si falta una, los modelos de ese proveedor se saltean; si faltan las dos, el comando corre en dry-run.

- **fal.ai**: la key sale de [fal.ai/dashboard/keys](https://fal.ai/dashboard/keys). Cubre Seedance, Kling, MiniMax, Wan y Veo vía fal.
- **Gemini API**: la key sale de [aistudio.google.com/apikey](https://aistudio.google.com/apikey). Cubre Veo y Omni. Ninguno de los dos tiene tier gratis, así que el proyecto necesita billing activado.

Para cargarlas en la sesión sin que queden en el historial de la shell (sintaxis de zsh):

```bash
read -rs "FAL_KEY?FAL_KEY: " && export FAL_KEY
read -rs "GEMINI_API_KEY?GEMINI_API_KEY: " && export GEMINI_API_KEY
```

O, para no pegarlas cada vez, se guardan una vez en el llavero de macOS (`-w` al final pide el valor sin mostrarlo):

```bash
security add-generic-password -a "$USER" -s FAL_KEY -w
```

```bash
export FAL_KEY="$(security find-generic-password -a "$USER" -s FAL_KEY -w)"
```

Lo mismo con `GEMINI_API_KEY`.

### Correrlo

```bash
uv run --project pipeline spritepipe bakeoff characters/comando/bakeoff.toml --dry-run
```

```bash
uv run --project pipeline spritepipe bakeoff characters/comando/bakeoff.toml
```

El dry-run muestra, por modelo, el endpoint, la duración que se va a pedir, el costo por clip y el total, más el cuerpo exacto de cada pedido (con la imagen y el prompt resumidos). Sin `--dry-run` y con keys, muestra lo mismo y pide confirmación antes de gastar (`--yes` la saltea). Si el total estimado pasa `max_usd` de la config, no manda nada. `--models seedance-2.0,minimax-h3` corre sólo esos.

Los clips quedan en `clips/bakeoff/<modelo>_<anim>_<n>.mp4`. Además:

- `bakeoff.md`: la tabla por clip (estado, veredicto del QA, deriva, zoom, frames que tocan el borde, MAD del frame 0 contra la pose, costura del loop, costo) y un resumen por modelo.
- `bakeoff.json`: cada pedido con su id en el proveedor, estado, motivo del bloqueo o del error y el QA. No guarda keys ni imágenes.

`--anims idle_a,idle_b` corre sólo esas animaciones de la config, como `--models` con los modelos.

Volver a correr el comando no regenera lo que ya está bajado: para regenerar un clip, borralo. Si el proceso se corta (Ctrl-C, la red), los pedidos ya enviados siguen en el proveedor y se retoman sin pagarlos de nuevo durante 48 h; Veo borra el video a los 2 días.

### Los modelos

Los IDs, parámetros y precios salen de la documentación de cada proveedor, leída el 2026-10-15. Viven en `MODELS`, en `spritepipe/videoapi.py`, con el link a la doc en cada uno. Los precios son de lista; lo que se cobra de verdad está en el dashboard de cada proveedor.

| Nombre en la config | Endpoint | Duración | US$/s a 720p sin audio | Notas |
|---|---|---|---|---|
| `seedance-2.0` | fal `bytedance/seedance-2.0/image-to-video` | 4–15 s | 0,3034 | Lo que se usa hoy en Davinci. Cobra por tokens. |
| `seedance-2.5` | fal `bytedance/seedance-2.5/image-to-video` | 4–30 s | ~0,473 | `aspect_ratio` siempre sigue a la imagen. |
| `kling-3.0-pro` | fal `fal-ai/kling-video/v3/pro/image-to-video` | 3–15 s | 0,112 (0,168 con audio) | La resolución no se elige. fal.ai/pricing dice 0,14/s. Trae `negative_prompt` por defecto. |
| `minimax-h3` | fal `minimax/h3/image-to-video` | 5–15 s | 0,06 (768P) | 720p se pide como 768P. Por defecto expande el prompt (`prompt_expansion_mode = "balanced"`) y devuelve el expandido. El audio no se apaga. |
| `wan-2.2` | fal `fal-ai/wan/v2.2-a14b/image-to-video` | 1–10 s (`num_frames` a 16 fps) | 0,08 | fal interpola a 32 fps por defecto. Sin audio. |
| `veo-3.1-fast-fal` | fal `fal-ai/veo3.1/fast/image-to-video` | 4, 6, 8 s | 0,10 (0,15 con audio) | Con último frame usa `.../first-last-frame-to-video`. fal no expone `personGeneration`. |
| `veo-3.1-fast-gemini` | Gemini API `veo-3.1-fast-generate-preview` | 4, 6, 8 s | 0,10 (con audio, que no se apaga) | `personGeneration = "allow_adult"`, el único valor que acepta image-to-video. 1080p sólo en 8 s. **Se apaga el 2026-10-22**. |
| `minimax-h3-max` | fal `minimax/h3-max/image-to-video`; con referencias, `.../reference-to-video` | 1–15 s | 0,052 (promoción hasta el 2026-10-31, después 0,08); con referencias 0,08 | 720p se pide como 768P (sale 1344×768). Con referencias: primer frame (`image_url`, "opens exactly on this image"), último frame y hasta 9 referencias ("Image 1"…); 4.096 tokens de referencia incluidos por pedido (1.024 por imagen cuadrada), el excedente a US$0,02 cada 1.000. El audio no se apaga. |
| `kling-o3-std` | fal `fal-ai/kling-video/o3/standard/image-to-video`; con referencias, `.../reference-to-video` | 3–15 s | 0,084 (0,112 con audio) | Con referencias: `start_image_url`, `end_image_url` y las referencias como *elements*: cada 4 imágenes en orden son uno (la frontal y 1–3 vistas; `@Element1`… en el prompt). Con primer frame acepta hasta 3 elements. Sin seed. |
| `gemini-omni-1.1-flash` | Gemini API (Interactions API) `gemini-omni-1.1-flash` | 3–10 s | ~0,1014 (con audio, que no se apaga) | La pose va como primer frame con `task = "image_to_video"`; el último frame es la segunda imagen. Cobra por tokens: 5.792 tokens de video por segundo a 720p, más centavos de entrada y razonamiento. Sin `negative_prompt`. Sólo 720p tiene precio documentado. |

Con la config del comando (8 modelos, idle y shoot, 2 clips de 5 s cada uno) el total estimado da US$27,42. Veo redondea a 6 s.

### Referencias y una config con varias estrategias

Una `[[animation]]` puede llevar `refs`: imágenes de referencia (hoja de vistas, el arma) que van además del primer y el último frame, sólo a los modelos que las aceptan (`max_refs` en `MODELS`; hoy `minimax-h3-max` y `kling-o3-std`). A los demás les va la animación sin ellas, y el plan lo avisa. Con referencias, el pedido puede ir a otro endpoint y costar otra cosa: el plan muestra el rango por clip.

Para comparar estrategias en una sola config, cada animación puede elegir sus modelos (`models`) y llevar un prompt por modelo (`prompts`), porque cada uno nombra las referencias a su manera:

```toml
[[animation]]
name = "idle_b"
pose = "poses/perfil_dullmagenta_16x9.png"
prompt = "prompts/idle_b_h3max.txt"                       # "Image 1 to Image 4 show..."
prompts = { kling-o3-std = "prompts/idle_b_kling.txt" }   # "The character is @Element1..."
models = ["minimax-h3-max", "kling-o3-std"]
last_frame = true
refs = ["refs/vistas/tpose_frente.png", "refs/vistas/tpose_tres_cuartos.png"]
```

Lo que dio la prueba del 2026-10-17 (`characters/lowpoly/reporte_idle.md`): con referencias, los dos modelos empeoraron la consistencia de un idle de costado. H3 Max abre en el primer frame, corta a otra toma armada con las referencias y vuelve recién en el último. Kling no corta, pero gira al personaje hacia cámara para mostrar las vistas de frente. Kling O3 con sólo el primer y el último frame fue lo más consistente.

### Bloqueos de moderación

La columna de estado distingue `ok`, `bloqueado` y `error`. Un clip `bloqueado` es uno que el proveedor rechazó por moderación. En fal, eso es un 422 `content_policy_violation`; si el que rechaza es el dueño del modelo y no el filtro de fal, `categories` trae `model_moderated`. En Veo por la Gemini API, es una operación con `raiMediaFilteredCount` o un error con "Support codes". En Omni, es un error con uno de los códigos de bloqueo de la Interactions API (`safety`, `prohibited_content`, `content_blocked`, etc.). El motivo queda en las notas.

Para el comando hay una pregunta abierta: ¿Davinci devolvía "blocked by provider" con Veo por el filtro de Google o por un `personGeneration` más restrictivo de la plataforma? `veo-3.1-fast-gemini` manda `allow_adult` directo a Google, así que la respuesta sale de comparar:

- **También bloquea por la Gemini API**: es el filtro de Google, no la plataforma.
- **Pasa por la Gemini API**: era la plataforma.

La doc de Vertex lista dos códigos de soporte para la categoría de menores (58061214, 17301594), que rechazan si `personGeneration` no es `allow_all`. Image-to-video sólo acepta `allow_adult`, así que un personaje que el filtro lea como chico puede bloquearse aunque el arma no tenga nada que ver.

Veo por la Gemini API no cobra lo bloqueado. fal no lo aclara: su página de precios dice que se paga sólo lo exitoso y su FAQ, que un 422 puede cobrarse. Omni tampoco lo aclara: cobra por tokens de salida, incluido el razonamiento. Por las dudas, la tabla cuenta lo bloqueado de fal y de Omni como cobrado.

### Lo que hay que saber

- **Veo por la Gemini API tiene los días contados.** `veo-3.1-fast-generate-preview` se apaga el 2026-10-22, y Google recomienda pasar a `gemini-omni-1.1-flash`, que ya está en el bake-off. Si la prueba con `allow_adult` importa, hay que correrla antes de esa fecha. La fecha es la de la Gemini API: `veo-3.1-fast-fal` es otro servicio.
- **Omni va por otra API.** El pedido es un `POST /v1beta/interactions` con `background: true`; el bake-off consulta `GET /v1beta/interactions/{id}` hasta que sale de `in_progress` o `queued`, y el GET trae el video en base64. Sin `task = "image_to_video"`, Omni decide solo si la imagen es el primer frame o una referencia. Para un idle en loop, `last_frame = true` le manda la misma pose como segunda imagen.
- **Hay puntos de Omni que la doc de la Gemini API no cierra.** No da el formato de `duration`: se manda `"5s"`, el que documenta Vertex para el mismo modelo. Tampoco dice si respeta `seed`, cómo se ve un bloqueo en una interacción en background ni si cobra lo bloqueado. Si Google rechaza el formato, el pedido vuelve con error (`invalid_request`), no con bloqueo. La doc evalúa sólo prompts en inglés, y los del comando lo están.
- **La pose de fal se sube al CDN de fal**, con expiración de 24 h (`X-Fal-Object-Lifecycle-Preference`), porque fal desaconseja data URIs de más de unos KB. A la Gemini API (Veo y Omni) la imagen va en base64 dentro del pedido.
- **Hay dos puntos dudosos en la doc de Veo de la Gemini API.** El ejemplo REST manda la imagen como `inlineData`, mientras que el SDK de Python usa `bytesBase64Encoded`. La doc escribe `durationSeconds` como texto y el SDK, como número. El bake-off sigue el ejemplo REST para la imagen y el SDK para la duración. Si Google rechaza el formato, el pedido vuelve con error (no con bloqueo) y no se cobra.
- **El seed no siempre aplica.** `seed` sólo llega a los modelos que lo aceptan: MiniMax, Wan y Veo en fal, y Omni (en `generation_config`, sin garantía de que lo respete). Seedance y Kling no tienen seed, y Veo por la Gemini API lo rechaza.
- **fal entrega los videos en BT.601 sin tag.** Pasa con Kling, MiniMax H3 y Seedance: decodificados como BT.709 (lo que se supone sin tag), el rojo se corre a naranja y el MAD del frame 0 contra la pose sube (en Kling O3, de 0,5 a 10,6 en los colores saturados). En `character.toml`, los clips de fal llevan `color_matrix = "bt601"`, como los de Davinci. El QA del bake-off lee con BT.709: su MAD de la pose vale para comparar modelos, no como medida absoluta.
- **Hay que calibrar los umbrales del QA con estos clips.** Un modelo con más `warn` no es necesariamente peor: mirá los clips.

## Fondos por API de imagen

`spritepipe gen-images` arma los gráficos de fondo de un escenario con un modelo de imagen y la misma dirección de arte que el personaje: un style frame de pantalla completa, las capas de parallax, el kit de plataformas y los props. Lee una config por set (`backgrounds/ranger_base/gen.toml` es el ejemplo), manda un pedido por asset, modelo e imagen, y a cada imagen bajada le corre un post sin IA: key del fondo plano, transparencia, piezas sueltas, costura y recorte. Con varios modelos en la config, la salida es la comparación para elegir uno, como el bake-off de video.

```bash
uv run --project pipeline spritepipe gen-images backgrounds/ranger_base/gen.toml --dry-run
```

```bash
uv run --project pipeline spritepipe gen-images backgrounds/ranger_base/gen.toml --assets style_frame,mid,platform_kit,props
```

Las keys son las del bake-off: `FAL_KEY` y, para OpenAI directo, `OPENAI_API_KEY`, sólo desde el entorno (ver [Las keys](#las-keys)). Sin ninguna es siempre un dry-run, y no escribe nada: muestra por modelo y asset el tamaño que se va a pedir, si el fondo sale con alfa nativo, sobre el color de key u opaco, el costo y el total, más el prompt completo de cada asset y el cuerpo exacto de un pedido por modelo. Con keys muestra lo mismo y pide confirmación antes de gastar (`--yes` la saltea); si el total pasa `max_usd`, no manda nada. `--models` y `--assets` eligen un subconjunto. Lo ya bajado no se vuelve a pedir: para regenerar una imagen, borrala. `--post-only` rehace el post de lo bajado sin llamar a ninguna API (por ejemplo, después de cambiar `seam` o `height`).

### La config

```toml
[gen]
models = ["gpt-image-2.5-sunburst-fal", "nano-banana-2.1", "seedream-5-pro", "flux-3"]
images_per_asset = 1     # imágenes por asset y modelo (n en un [[asset]] lo pisa)
max_usd = 8
key_color = "#00FF00"    # fondo plano para los modelos sin alfa
quality = "high"         # GPT Image: low | medium | high | xhigh | max
resolution = "2K"        # 1K | 2K | 4K, en los modelos que la eligen
seed = 7                 # en los que lo aceptan (Nano Banana, Kontext)
ref_bg = "#FFFFFF"       # las referencias con transparencia se aplanan sobre este color

[styles]                 # bloques de prompt que los assets combinan
game = "..."             # contorno negro grueso y colores planos: la capa de juego
far = "..."              # desaturado y con menos contraste: las capas lejanas

[[asset]]
name = "mid"
style = ["game", "mid"]
prompt = "..."
refs = ["../../poses/ranger_concept.png"]
ref_role = "style"       # "style": sólo como guía de estilo; "character": el personaje va en la imagen;
                         # "level": el personaje y el style frame del nivel, para que la capa se le parezca
models = ["nano-banana-2.1"]  # opcional: sólo estos modelos de [gen] generan este asset
aspect = "3:1"           # cada modelo usa el tamaño permitido más parecido
alpha = "layer"          # opaque (cielo, style frame) | layer (aire arriba) | cutout (prop, pieza)
tile = "x"               # se repite en x: se revisa y arregla la costura
seam = "cut"             # cut | crossfade | clear | mask | none
```

La comparación del 2026-10-16 (los 4 modelos en `style_frame`, `mid`, `platform_kit` y `props`, US$1,13) quedó en `backgrounds/ranger_base/compare.html`. `compare.html` y `compare.md` muestran siempre todo lo que se generó en el set, aunque la corrida haya sido con `--models` o `--assets`, o un asset ya no elija ese modelo.

Una hoja con varias piezas lleva `split` con sus nombres en orden de lectura (filas de arriba abajo, cada una de izquierda a derecha), y `tile` puede ser una tabla por pieza: `tile = { top = "x", body = "x" }`. Las piezas de una hoja quedan todas a una misma escala; con `same_height = true` (el kit), además, a una misma altura (ver el paso 3 del post). `height` lleva la imagen a ese alto en px; en una hoja, la altura común o la de la pieza más alta, con la misma escala para todas. El prompt final es: los `style`, el `prompt` del asset, cómo usar la referencia y cómo tiene que ser el fondo. Esto último cambia por modelo: a GPT Image se le pide "Transparent background" y `background = "transparent"`; a los demás, un fondo plano de `key_color` sin degradé ni sombra.

### Salida

En la carpeta del set (`backgrounds/<set>/`):

- `raw/<asset>/<modelo>_<n>.png`: lo que devolvió el modelo, tal cual.
- `raw/<asset>/<modelo>_<n>.json`: la procedencia. Incluye set, asset, modelo, endpoint y link a la doc, el prompt completo, las referencias (la original y la aplanada, con sha256), el tamaño pedido y el devuelto, seed, calidad, costo estimado y nota de precio, uso que informa el proveedor (tokens de OpenAI), id del pedido, sha256 de la imagen y el reporte del post.
- `post/<asset>/<modelo>_<n>.png`: después del post. Con `split`: `post/<asset>/<modelo>_<n>/<pieza>.png`. Con `seam = "mask"`, además `<…>.seam_x.png` y `<…>.seam_x_mask.png`.
- `refs/`: las referencias aplanadas que se mandaron.
- `gen.json`: cada pedido con su estado, el id en el proveedor y el motivo de un bloqueo o error. No guarda keys ni imágenes. Un pedido de fal cortado a la mitad (Ctrl-C, la red) se retoma durante 24 h sin pagarlo de nuevo; uno de OpenAI no, porque es sincrónico.
- `compare.html`: la grilla asset × modelo, con cada imagen sobre damero (o sobre el violeta de la base), el veredicto del post y el costo. `compare.md` es la misma tabla en texto.

### El post, sin IA (`bgpost.py`)

1. **Key.** Los modelos sin alfa dibujan sobre `key_color`. El color real es la mediana de lo que se le parece mucho (ningún modelo devuelve `#00FF00` exacto) y se saca con el mismo keyer de los personajes, en modo global: un hueco verde entre dos edificios también es fondo. Verde porque no aparece en la base (violeta, naranja, gris acero, amarillo, cian, rojo).
2. **Transparencia.** El reporte dice qué fracción es transparente y por qué borde, y falla si no hay transparencia donde tiene que haber. Distingue cuando el modelo pintó el damero gris y blanco de "transparente" en lugar de devolver alfa. Además avisa si una capa tapa el borde de arriba, si un prop toca el borde (puede estar cortado) y si quedó color de key en lo opaco.
3. **Piezas.** Una hoja se separa por componentes conexos del alfa, en orden de lectura; las manchas de menos del 2% del área de la pieza mayor se descartan. Si salen más o menos piezas que nombres, quedan numeradas y el reporte lo dice. Todas quedan a la escala en que las dibujó el modelo, así el contorno tiene el mismo grosor en todas (en los props, la caja más baja que el cartel). Con `same_height`, la altura común es la mediana: las piezas que difieren menos de un 15% se escalan a ella, porque tienen que empalmar y el modelo las dibujó apenas distintas. Las demás, como la plataforma flotante, quedan a su escala, con aire abajo para que el borde por donde se camina quede alineado, y el reporte lo dice.
4. **Costura.** En lo que se repite en x (o en y), la diferencia entre la última columna y la primera se compara con la típica entre columnas vecinas: cerca de 1 no se ve, hasta 2 está bien, entre 2 y 4 se nota apenas, más de 4 es un corte. Calibrado a ojo con las capas `mid` de `ranger_base`: GPT 23,6 (corte claro), Seedream 5,3 (se nota), FLUX 3,4 (apenas) y Nano Banana 1,9 (no se ve). El reporte trae también el peor de 16 tramos (`peak`) como dato. No decide nada, porque un contorno vertical que cae justo en la vuelta lo dispara sin que haya costura. Si no está bien, una franja del final (`seam_px`, por defecto el 12% del ancho) se superpone al principio y la capa pierde ese ancho. Si el resultado no mejora, se descarta y queda en el reporte como `fix_discarded`:
   - `cut`: corte de error mínimo (image quilting, Efros y Freeman 2001). Es un camino de arriba abajo por donde las dos franjas más se parecen, con 2 px de fundido. No duplica contornos y, en una capa con transparencia, pasa por el aire entre las siluetas.
   - `crossfade`: fundido lineal en toda la franja. Va para cielos y degradés; en dibujo de línea deja contornos dobles.
   - `clear`: para cielos con cosas sueltas, como nubes. Una nube cortada por el borde no empalma con ningún corte ni fundido, porque del otro lado no sigue. Entonces se borra lo que toca el primer o el último borde y ahí queda el fondo de cada fila (la mediana de lo que no es una cosa). Lo demás no cambia y la capa conserva el ancho, salvo que el degradé mismo no cierre: en ese caso, además, va un `crossfade`. Lo usa el cielo de `ranger_industrial`.
   - `mask`: no toca la capa. Escribe la capa corrida medio ancho, con la costura en el centro, y una máscara de la franja (transparente = lo que se edita, la convención de OpenAI). Sirve para retocarla a mano o con un modelo de edición con máscara.
5. **Recorte.** Al bbox del alfa con 2 px de aire, salvo en los ejes que se repiten. A una capa se le recorta el aire de arriba y conserva el ancho; el recorte queda en el reporte (`trim`) para alinearla en el engine.

`spritepipe bg-post imagen.png salida.png` hace lo mismo con una imagen suelta, por ejemplo después de retocarla a mano: `--alpha`, `--key`, `--tile`, `--seam`, `--seam-px`, `--split`, `--same-height`, `--height` y `--no-trim`.

### Los modelos

Los IDs, parámetros, tamaños y precios salen de la documentación de cada proveedor leída el 2026-10-16 (los schemas OpenAPI de fal y la referencia de la Image API). Viven en `MODELS`, en `spritepipe/imageapi.py`, con el link a la doc en cada uno. Los precios son de lista y estimados; lo que se cobra de verdad está en el dashboard de cada proveedor.

| Nombre en la config | Endpoint (con referencias) | Fondo | US$ por imagen | Notas |
|---|---|---|---|---|
| `gpt-image-2.5-sunburst` | OpenAI `POST /v1/images/edits` (JSON, referencias como data URL) | alfa nativo | ~0,11 a 2560×1440 `high` | Por tokens: US$30/M de imagen de salida, con la fórmula de la calculadora de la guía; más texto (US$5/M) y referencias (US$8/M). Lo de las referencias es una estimación: la doc no da cuántos tokens usan en 2.5. Tamaño libre (lados múltiplos de 16, hasta 3:1); con `2K` se queda dentro de 2560×1440, el límite de lo no experimental. Sin seed. |
| `gpt-image-2.5-flare`, `gpt-image-2` | ídem | alfa nativo (en 2, "in preview") | ídem | Flare es el rápido de la 2.5. |
| `gpt-image-2.5-sunburst-fal`, `…-flare-fal` | fal `openai/gpt-image-2.5/sunburst/edit` | alfa nativo | ídem | El mismo modelo y los mismos tokens, pagados con `FAL_KEY`. |
| `nano-banana-2.1` | fal `google/nano-banana-2.1/edit` | key | ~0,059 a 2K (0,040 a 1K, 0,134 a 4K), más ~0,002 por referencia | Gemini por tokens. Proporciones fijas, incluidas 21:9 y 4:1. Hasta 14 referencias. |
| `nano-banana-pro` | fal `fal-ai/nano-banana-pro/edit` | key | 0,15 (el doble a 4K) | Gemini 3 Pro Image. |
| `seedream-5-pro` | fal `bytedance/seedream/v5/pro/edit` | key | 0,0675 hasta 1536² px, 0,135 hasta 2048², más 0,0045 por referencia desde la segunda | Precio "tentativo". Tamaño libre: con `2K` se queda en el escalón barato. Sin seed. |
| `flux-3` | fal `blackforestlabs/flux-3/edit-image` | key | 0,048 a 1k | fal no publica el precio de 2k ni de 4k, así que se pide siempre 1k. Hasta 10 referencias. Sin seed. |
| `flux-kontext-pro` | fal `fal-ai/flux-pro/kontext` (una referencia) o `…/kontext/multi` | key | 0,04 | El FLUX anterior; lo reemplazaron FLUX.2 y FLUX 3. |

Con la config de `ranger_base`, los 7 assets en los 4 modelos dan US$1,94 estimados; la comparación chica (`--assets style_frame,mid,platform_kit,props`) da US$1,13.

### Lo que hay que saber

- **Sólo GPT Image devuelve alfa.** Ni Nano Banana ni Seedream ni FLUX tienen opción de fondo. Por eso dibujan sobre verde y el post lo keyea. fal tiene modelos que separan una imagen en capas transparentes (Seedream 5 `layerize`, Qwen-Image-Layered) y removedores de fondo, pero son otro pedido pago y no están integrados.
- **OpenAI directo puede pedir verificar la organización.** La guía de generación de imágenes avisa que puede hacer falta la [verificación de la organización](https://help.openai.com/en/articles/10910291-api-organization-verification) para usar GPT Image, pero ninguna doc oficial dice para qué modelos ni qué error devuelve. Si la API responde 403 hablando de verificación, el error lo dice. Por fal no hace falta.
- **Los GPT Image viejos se apagan.** `gpt-image-1` se apaga el 2026-10-23; `gpt-image-1.5`, `gpt-image-1-mini` y `chatgpt-image-latest`, el 2026-12-01. Por eso no están en `MODELS`.
- **Moderación.** En OpenAI, un bloqueo es un 400 con `code = "moderation_blocked"` y la etapa (input u output). En fal es un 422 `content_policy_violation`, o `has_nsfw_concepts` en la salida de Kontext, que devuelve la imagen en negro. Las dos aparecen como `bloqueado` en la tabla. Ninguno de los dos aclara si cobra lo bloqueado, así que se cuenta como cobrado.
- **Las referencias se aplanan.** El concept del ranger es RGBA con el fondo en negro transparente, y varios modelos lo ven negro. Se manda aplanado sobre `ref_bg` (blanco), como quedó en `refs/`. A fal se sube al CDN con expiración de 24 h, como la pose del bake-off; a OpenAI va en base64 dentro del pedido.
- **El costo de GPT Image es una estimación.** La calculadora de la guía modela la 2.5, pero la página del modelo dice que no la estima. El uso real (tokens de entrada y salida) queda en el `.json` de cada imagen.
- **La costura se arregla, pero el modelo tiene que ayudar.** El prompt pide que la capa se repita en x y continúe por los dos bordes. `cut` encuentra el mejor corte dentro de la franja, pero si el principio y el final no se parecen en nada, el corte se nota igual. Ahí conviene `mask` y retocarla.

## Piloto

El número que decide si la ruta de IA conviene es el tiempo de limpieza por animación. Registralo en [`pilot/cleanup_log.csv`](../pilot/cleanup_log.csv), junto con los clips generados y los usables, para reemplazar los supuestos del reporte (5 intentos por clip, 1–4 h por animación) por datos propios.

## Limitaciones conocidas

- Probado con clips sintéticos (`characters/synthetic`), con el comando (`characters/comando`, cuatro clips de Seedance 2.0 a 864×496) y con el ranger (`characters/ranger`). La escala por clip se probó con clips sintéticos de dos resoluciones y con clips armados desde las poses 16:9 del ranger contra su run viejo de 560×752; todavía no con un clip real de otra resolución.
- Los umbrales del QA son heurísticos. Hay que calibrarlos en el bake-off.
- En idles muy sutiles (respiración de 1%), el movimiento entre frames se parece al ruido y la búsqueda de loop puede errarle por unos frames. El salto queda en menos de medio píxel, pero si molesta, fijá `loop_start`/`loop_length` a mano o generá el idle con primer y último frame iguales (ahí el clip entero es el loop).
- El zoom de cámara se detecta pero no se corrige: esos clips se regeneran.
- La limpieza previa supone un personaje que mira a la derecha y efectos cian (los del ranger); las constantes están calibradas con sus clips de 1280×720, y las distancias en px se escalan con el alto del clip. Una fila tapada en los dos bordes por algo que no cruza el cuadro entero (dos rayos, uno de cada lado) se interpola igual que una barra. `cut_muzzle` necesita que los primeros 5 frames tengan el brazo bajo.
- `remove_flash` supone un personaje que mira y dispara a la derecha, con el cañón como lo más a la derecha del frame 0 y el frame 0 sin fogonazo; si no, fijá la geometría en la config. El halo tiene que ser suave (sobre magenta lo es): si es opaco y toca el cañón, cuenta como cañón y sobrevive. Si el arma avanza más de 3 px respecto del frame 0, la mira entra en la zona del halo y se borra.
- No hay matting por IA (BiRefNet o ToonOut) para fondos que no son planos; tampoco frames puente con RIFE.
- `gen-images` se probó con clientes falsos y el dry-run real; el key, las piezas y la costura, con imágenes sintéticas. Las piezas suponen que el modelo las dejó separadas por fondo: si se tocan, salen juntas.
- `clean-concepts` supone personajes con contorno negro, de pie y con las dos botas en el piso. El blanco entre las piernas sólo se borra si toca el piso, cae en el centro de las botas y es del color del fondo; otros huecos de fondo encerrados (un brazo contra el torso) quedan blancos. Lo que el original corta en el borde de la imagen (la katana del ninja) queda cortado.
- El key por distancia (fondos blancos) puede dejar un hilo claro de 1 px a resolución de video, que desaparece al reducir.
- En pixel art, la grilla se alinea entre frames pero no se detecta la grilla original del clip; si el video trae "falso pixel art", pasalo antes por Proper Pixel Art.
