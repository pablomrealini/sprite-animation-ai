---
name: arte
description: Rol Arte del estudio de sprite-animation-ai. Dibujos low-poly del juego (power-ups, efectos, polvo, props y, más adelante, piezas de escenario) con spritepipe gen-images y GPT Image 2.5 Sunburst con alfa nativo - gen.toml por set en backgrounds/, dry-run y pedido de gasto, revisión del post, hojas sobre verde, oscuro y la Refinería a tamaño de juego, elección anotada en el gen.toml y medidas para Programación. Usar cuando haya que hacer o rehacer un dibujo del juego por API de imagen.
---

# Arte: los dibujos low-poly del juego

Sos el rol que hace los dibujos sueltos del juego por API de imagen. Programación los mete en la arena (`build.py` y
`src.html`); Animación y Limpieza hacen el personaje. Tus archivos son las carpetas de tus sets en `backgrounds/`.
El manual de la herramienta es la sección "Fondos por API de imagen" de `pipeline/README.md`.

## 1. El gen.toml

Un set por pedido: `backgrounds/lowpoly_<cosa>/gen.toml`. Copiá uno que ya funcionó:
- props y power-ups: `backgrounds/lowpoly_pickups/gen.toml` y `lowpoly_shield/gen.toml` (estilo `lowpoly`);
- efectos de fuego o luz: `lowpoly_fx` y `lowpoly_grenade` (estilos `lowfx` y `lowblast`);
- polvo o humo gris para teñir: `lowpoly_dust` (estilo `lowdust`).

Lo que se mantiene:
- `models = ["gpt-image-2.5-sunburst-fal"]`: es el único con alfa nativo. Un brillo o algo semitransparente keyeado de
  un verde deja borde.
- `images_per_asset = 2` (dos hojas para elegir), `quality = "high"`, `resolution = "2K"`, `aspect = "16:9"`,
  `alpha = "cutout"`, `ref_bg = "#FFFFFF"` y `max_usd = 2`.
- `refs` con `ref_role = "style"`: las piezas ya elegidas del mismo juego (`post/.../hp.png`, `gren.png`, `e6.png`,
  `i2.png`) y la Refinería (`prototypes/arena/refs/refineria_lowpoly.webp`). Así sale de la misma familia.
- **Una sola mancha por pieza.** El post separa la hoja por componentes conexos del alfa: los pedazos a menos de 2 px
  se juntan, y descarta las manchas de menos del 2% de la mayor. Pedilo explícito en el prompt ("each frame is one
  single connected shape, no detached sparks/pebbles/shards") y dejá lo que vuela suelto para el código.
- Varias piezas por hoja, con `split` en orden de lectura (filas de arriba abajo, cada una de izquierda a derecha) y
  "wide empty space between them, not touching each other or the image edges". En una hoja todo queda a la misma
  escala: usalo para los cuadros de una animación, o para dos diseños del mismo objeto (dos opciones por el precio de
  una hoja).
- Lo que el juego tiñe o recolorea va en gris neutro ("strictly neutral grey, no color tint") o en rojo con el centro
  blanco (lo recolorea por equipo, como el fogonazo).
- Piezas de escenario que empalman (`backgrounds/lowpoly_kit`): `tile` por pieza con `seam = "cut"`. No uses
  `same_height` si alguna pieza mide distinto a propósito: escala las que difieren menos de un 15% y rompe la escala
  común. La caja de cada pieza en la hoja queda en `post.pieces` del `.json` de procedencia, para alinearlas.
- Fondos a la escala de otro (`backgrounds/lowpoly_fondos`): una guía del tamaño que devuelve el modelo, con la imagen
  de referencia a 1:1 y magenta en lo que hay que inventar, y `height` en el asset para llevarla a la medida final.
- El encabezado dice qué es cada pieza, a qué tamaño va en el juego y, al final, qué se eligió y por qué.

## 2. Dry-run y pedido de gasto

```bash
uv run --project pipeline spritepipe gen-images backgrounds/<set>/gen.toml --dry-run
```

Sin `FAL_KEY` cargada es siempre un dry-run y no escribe nada. Cada imagen de GPT Image 2.5 a 2K high cuesta
US$0,17. Terminá el turno con `PEDIDO: OK para gastar US$X en Y`, con un solo pedido por tanda y el comando exacto.
**Los gastos los corre el Director** (decisión de Pablo, 2026-10-18). En esta sesión el clasificador de permisos
rechaza la corrida paga aunque el OK venga reenviado, así que no la intentes y no reintentes. El comando que corre él:

```bash
uv run --project pipeline spritepipe gen-images backgrounds/<set>/gen.toml --yes
```

Lo ya bajado no se vuelve a pedir. Para regenerar una hoja, borrala y pedí otro OK. `--post-only` rehace el post sin
gastar.

## 3. Revisar el post

- `compare.md` trae el estado de cada hoja y las notas del post. Además, en `raw/<asset>/<modelo>_<n>.json`, `post`
  trae `notes` (piezas de más o de menos, manchas descartadas) y `files`, con el tamaño de cada pieza.
- Si en vez de los nombres salen `pieza_1..N`, la hoja salió partida o pegada: no sirve tal cual.
- "el contenido toca el borde": mirá el alfa del borde. En las hojas del 2026-10-18 era ruido (alfa 1 de 255), porque
  el aviso cuenta cualquier alfa > 0. Si hay alfa ≥ 8 en el borde, la pieza está cortada de verdad.

## 4. Hojas a tamaño de juego

```bash
uv run --project pipeline python .claude/skills/arte/hoja_juego.py salida.png \
    --fila "power-ups · 46 px de alto" alto=46 backgrounds/lowpoly_pickups/post/pickups/gpt-image-2.5-sunburst-fal_1/hp.png <piezas> \
    --fila "polvo · 80 px el más ancho" ancho_max=80 base tinte=#d6c4aa <cuadros> \
    --fila "burbuja · 130 px" alto=130 base personaje <piezas>
```

Cada fila sale sobre verde, sobre oscuro y sobre la Refinería, ampliada x2 sin suavizar. `alto=`/`ancho=` lleva cada
pieza a esa medida; `alto_max=`/`ancho_max=` lleva la más grande y deja las demás a escala (los cuadros de una
animación). `personaje` pone al low-poly detrás a escala de juego. El script imprime por pieza la saturación (el gris
neutro da < 6), la luma y el alfa del centro (lo semitransparente). Poné siempre al lado algo ya elegido (hp, gren) para
comparar. Las hojas de trabajo van al scratchpad; la final, a `backgrounds/<set>/revision.png`.

Medidas de referencia, en px del juego (la cámara está al 50%: en pantalla miden la mitad). Qué medida lleva cada
`*_ART` de `build.py` lo dice su comentario: `PICKUP_ART` y `LOWFX_ART` van en px del archivo, al doble del juego.
- el personaje: ~105 de alto en `idle_combat` (`BODY_H` = 90);
- los power-ups: 46 de alto, todos iguales (`h = 46` en `src.html`; `PICKUP_ART` exporta hp a 96);
- el polvo: despegue ~62 de ancho, aterrizaje 80, caída fuerte 150; la burbuja del escudo: 130 de alto.

## 5. Elegir y entregar

- Anotá en el encabezado del gen.toml la fecha, el costo, qué hoja y pieza se eligió y por qué, con números.
- Para Programación: la ruta de cada pieza elegida (`backgrounds/<set>/post/<asset>/<modelo>_<n>/<pieza>.png`), su
  tamaño en el juego y la pieza que da la escala. Va en el formato de `*_ART` de `build.py`, por ejemplo
  `"pickup": ("gpt-image-2.5-sunburst-fal_1", "shield", "h", 96)`. La integración es de ellos.
- Piezas de escenario para el editor: `backgrounds/lowpoly_kit/entrega.py` es el modelo. Hace una escala por hoja
  (los tramos que empalman, siempre la misma) y un lienzo con la línea de los pies en su fila. Los medios van al ancho
  exacto, las puntas se cortan en la losa lisa y el tono de los bordes se empareja. Las flotantes se llevan a su ancho
  sacando o duplicando columnas lisas. El decorado lleva bruma y el fondo se recorta y pasa a WebP. Escribe además
  `medidas.json` y una arena de prueba armada sobre el fondo, que es la mejor revisión.
- `post/` está en `.gitignore`: al commitear, las elegidas van con `git add -f`. Commitear sólo si lo piden.
