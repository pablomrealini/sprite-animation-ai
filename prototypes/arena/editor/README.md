# Editor de arenas

Arma y retoca las arenas del VS de 4 (`prototypes/arena/arenas/*.json`, el formato en `../arenas/FORMATO.md`). Es del
rol Editor de niveles desde el 2026-10-18. La propuesta de mejoras y lo que falta: `propuesta.md`; las medidas del kit
de piezas para Arte: `kit_medidas.md`.

## Arrancar

Desde la raíz del repo:

```bash
uv run --project pipeline python prototypes/arena/editor/build.py
```

```bash
python3 prototypes/arena/editor/serve.py
```

y abrir http://localhost:8772/ (o `#<arena>` al final: http://localhost:8772/editor/dist/index.html#prueba_2496).
Después de tocar `editor.html`, alcanza con `build.py --page` y recargar. Si Programación cambia la física, el colgado,
la caída o el HUD en `src.html`, volver a armar el editor: los lee de ahí.

## Qué hace

- **Elegir**: clic; ⇧ + clic suma o saca; arrastrar en vacío hace un recuadro (con ⇧, suma); doble clic elige todo ese
  piso (lo que se pisa a esa altura, de los dos lados, y sus spawns); ⌘A, todo; Esc, nada. Lo elegido se arrastra
  junto (⇧ arrastrando: un solo eje) y las flechas lo mueven (⇧: de a grilla). En el eje que casi no se movió no hay
  imán: subir algo derecho no le corre la x.
- **Mover la vista**: espacio + arrastrar, la rueda, el botón del medio o el derecho. Zoom: ⌘ + rueda o pellizco; 0
  ajusta.
- **Espejo** (E, o "⇋ Espejo"): mover, estirar, borrar, duplicar o cambiar algo hace lo mismo con su pareja del otro
  lado. La pareja es lo que está espejado contra el medio (±6 px), de la misma pieza (o la `_izq` ↔ `_der`) o el
  mismo tipo de sólido; lo que está en el eje es su propia pareja y queda centrado. No cambia el formato. En el panel
  de la arena, "Simetría" lista lo que no tiene pareja (con Espejo, se marca en violeta en el lienzo).
- **Los spawns siguen a lo que pisan**: si se mueve la pasarela, su spawn va con ella.
- **Piezas**: la paleta muestra las pintadas de esta arena, el **Kit low-poly** (abajo), las de las otras arenas (al
  ponerla, su definición se copia a esta, con la misma imagen) y, plegado, el kit 2D del ranger. Las patas se estiran
  solas hasta lo de abajo (L). Una pieza pintada que se acerca al borde de otra a la misma altura se pega a su lado
  (encimada 2 px) con la misma línea de los pies.
- **Kit low-poly** (`arenas/kit_lowpoly/`, de Arte): pasarelas por tramos, flotantes de 200/300/450, el ascensor,
  columnas, bloque, pared, la guía del ascensor y decorado. "+ Pasarela" arma punta + N medios + punta (226 + 254 por
  medio, encimados 2 px para que no se vea la unión) y "+ Caño horizontal", N tramos; cada tira se elige y se mueve
  junta (⌥ + clic: una pieza sola). Se estiran a lo alto las patas de las pasarelas y las columnas, la guía y el caño
  vertical. El bloque y la pared no se estiran: el juego no le suma el estirado al alto de su colisión. Las piezas
  simétricas no se espejan en la copia simétrica (la luz sigue viniendo de la izquierda) y las puntas se cambian por la
  del otro lado. El decorado va detrás de todo. "＋ Nueva…" propone el fondo del kit (2496 × 1404, piso en 1264).
  Cuando Arte entrega de nuevo: `uv run --project pipeline python prototypes/arena/editor/kit.py`. Las arenas que ya
  usan una pieza guardan su copia de la definición: en el panel de la arena aparece "Actualizar del kit", que copia la
  de ahora, corre la pieza si cambió la línea de los pies y vuelve a apoyar las patas que estaban apoyadas.
- **Pies a la vista** (panel de la arena): las patas apoyadas cuyo pie no tapa lo de abajo (una pata que cae en la
  punta de una pasarela o afuera), con dónde; clic para elegirla.
- **Guías** (en "Ver"): pisos cada 200 px desde el piso (se cambia en el panel del alcance), lo que tapa el HUD con 4
  jugadores, el margen de 90 px de los power-ups y, en rojo, las caídas que sacan vida (560 px o más).
- **Alcance**: desde el piso, con la física del juego integrada igual que el juego (trapecio): simple 192, doble 348, a
  cualquier frecuencia de pantalla. Con `HANG_ON` apagado no aparece nada del colgado.
- **Probar** (P): el juego encima del lienzo (con las láminas y piezas de `arenas/`, aunque el juego no se haya vuelto a armar), en "probar arena solo", desde el spawn elegido; Esc vuelve. ⇧ + clic, en
  otra pestaña (con bots).
- **Lo no guardado** queda en este navegador, un borrador por arena: cambiar de arena o recargar no lo pierde (la lista
  marca con • las que tienen cambios). "Descartar cambios", en el panel de la arena, vuelve a lo de disco.
- **Guardar** (⌘S) escribe `arenas/<nombre>.json`; si ya había uno distinto, antes lo copia a
  `arenas/.respaldo/<nombre>-<fecha>.json` (los últimos 30 de cada arena; git la ignora). "Guardar como…": con otro
  nombre (`carpeta/nombre` para un borrador que no va al menú del juego).

## Los otros scripts

- `kit.py`: pasa la entrega de Arte (`backgrounds/lowpoly_kit/entrega` y el fondo) a `arenas/kit_lowpoly/` con su
  `kit.json`: la colisión, la franja que se estira (medida en el alfa) y cómo se espeja cada pieza. Como las de la
  Refinería low-poly, las patas bajan por detrás: del pie (donde se ensancha) asoman sólo 14 px sobre el contorno de lo
  de abajo, como un remate chico (`PIE_VISIBLE`), y el resto lo tapa la capa de adelante del juego (`front` de las piezas y "frente" del piso del fondo, que va a
  `plate.solid`). El editor dibuja esa capa igual que el juego.

- `capas.py`: pasa una arena de lámina entera a lámina en capas (fondo + cada pasarela como pieza). Las zonas de cada
  pieza están escritas a mano por arena (`LEFT`); ver la propuesta (E11).
- `flotante.py`: recorta la flotante de la Refinería low-poly como pieza que se mueve.
