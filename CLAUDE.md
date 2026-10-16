# Para Claude

Proyecto de Pablo Realini y su socio (los dos devs de juegos, ex-Ironhide / Kingdom Rush): un pipeline de animación 2D de personajes con IA y juegos chicos para probarla. Leé primero `README.md` (qué hay y cómo se arranca); el manual del pipeline es `pipeline/README.md` y el de los juegos, `prototypes/README.md`.

## Cómo trabajar acá

- **Idioma**: español rioplatense, en las respuestas, los comentarios del código y los docs. Reportes técnicos, directos, con números cuando los hay.
- **Plata**: todo lo que llama a una API paga (`spritepipe bakeoff`, `spritepipe gen-images`, cualquier pedido a fal o Gemini) se corre primero con `--dry-run`, se muestra el costo y se espera un OK explícito antes de gastar. Nunca gastar "para probar".
- **Claves**: nunca pedirlas, recibirlas en el chat ni escribirlas en archivos o en el repo. Viven en el entorno de cada uno (llavero de macOS o `~/.zshrc`); si no están cargadas, decir cómo cargarlas y que lo haga la persona.
- **Git**: commitear o pushear sólo cuando lo piden. Las imágenes elegidas de `post/` están ignoradas y van con `git add -f` (ver "Convenciones del repo" en el README).
- **Animaciones nuevas**: revisarlas cuadro por cuadro sobre verde antes de meterlas en un juego.
- **Referencias de terceros**: sólo para analizar, nunca como asset ni al repo.
- **Si te rechazan una herramienta**: parar y esperar indicaciones, no reintentar.

## Comandos de siempre (desde la raíz)

- Tests del pipeline: `uv run --project pipeline pytest -q pipeline/tests`
- Atlas de un personaje: `uv run --project pipeline spritepipe run characters/<personaje>/character.toml`
- Arena (VS de 4): `uv run --project pipeline python prototypes/arena/build.py` → `prototypes/arena/dist/index.html`, servido con `python3 -m http.server 8767 --bind 127.0.0.1` desde la raíz
- Editor de arenas: `uv run --project pipeline python prototypes/arena/editor/build.py` y `python3 prototypes/arena/editor/serve.py` (puerto 8772)
- Los otros prototipos: `uv run --project pipeline python prototypes/build.py <personaje>`

## La arena, en corto

- Todo el juego es `prototypes/arena/src.html`; `build.py` le mete el atlas del ranger (en base64), el kit, la granada, el LUT de color y las arenas de `prototypes/arena/arenas/*.json`.
- Las arenas son JSON escritos por el editor (o a mano con el mismo formato): una lámina pintada de 1920 × 1080 (`plate`), piezas pintadas encima (`pieces` + `objects`), sólidos con `ledge`, lugares de salida y un bloque `color` (fondo y plataformas). La `y` de cada pasarela es la línea de los pies: el borde de atrás de la cara de arriba pintada.
- Para probar en el navegador sin mirar: las funciones del juego son globales (`loadArena`, `startTest`, `startMatch`, `step(dt)`, `render()`, `SLOTS`, `SET`, `players`, `solids`, `G`). Con el panel oculto no corre `requestAnimationFrame`: avanzar con `step(1/60)` y llamar `render()` antes de capturar.
- Se publica como artifact privado "Arena del Ranger" (link en `prototypes/README.md`), que declara la capacidad `db`: al republicar, no mandar `capabilities` para conservarla. El panel de la granada guarda sus ajustes en el doc `tuning/grenade` de esa base.
