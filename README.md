# sprite-animation-ai

Pipeline para hacer animación 2D de personajes con IA y probarla en juegos chicos. La idea: un concept del personaje → pose preparada → clip de un modelo de video (Seedance, Veo, Kling…) → limpieza y recorte → sprite sheet listo para el engine. Los fondos, props y efectos salen de modelos de imagen con la misma dirección de arte. Todo lo que no es IA es local y determinístico: la misma config sobre el mismo clip da los mismos PNG.

## Qué hay

| Carpeta | Qué es |
|---|---|
| `reports/` | Los reportes de investigación: el principal es [Animación 2D con IA para sprites](reports/Animación%202D%20con%20IA%20para%20sprites.md) (el método de punta a punta); además fogonazos, movimiento y disparo en run-and-guns y saltos con buen feel |
| `pipeline/` | `spritepipe`, la herramienta de línea de comandos: preparar poses, bake-off de modelos de video por API, limpieza de clips, sprite sheets y fondos por API de imagen. Su [README](pipeline/README.md) es el manual |
| `characters/` | Un personaje por carpeta: `character.toml` (clips, animaciones, escala), `generate*.toml` (pedidos a los modelos de video), `prompts/`, `clips/raw/` (los elegidos) y `out/` (el atlas y los sheets) |
| `poses/` | Concepts y poses 16:9 sobre magenta que se le pasan a los modelos; `roster/` es el plantel de 8 |
| `backgrounds/` | Sets de gráficos por API de imagen (`gen.toml` + la comparación `compare.html` + las opciones elegidas en `post/`) |
| `prototypes/` | Los juegos de prueba, una página HTML cada uno: polígono del comando, polígono del ranger y la **arena**, un VS local de hasta 4. Su [README](prototypes/README.md) explica cada uno |
| `prototypes/arena/editor/` | Editor de arenas (local): mover piezas, espejar, lugares de salida, alcance del salto, color del fondo y de las plataformas, y probar jugando |
| `research_notes/` | Notas y material de las investigaciones (las referencias de terceros quedan fuera del repo) |

## Arrancar

Hace falta macOS o Linux con `uv` y `ffmpeg` (en Mac, por Homebrew: `brew install uv ffmpeg`). Desde la raíz del repo:

```bash
uv run --project pipeline pytest -q pipeline/tests
```

Armar el atlas de un personaje desde sus clips (no gasta nada):

```bash
uv run --project pipeline spritepipe run characters/ranger/character.toml
```

Armar y abrir la arena (el VS de 4):

```bash
uv run --project pipeline python prototypes/arena/build.py
```

```bash
python3 -m http.server 8767 --bind 127.0.0.1
```

y abrir http://127.0.0.1:8767/prototypes/arena/dist/index.html. Controles y joysticks: ver la ayuda en la misma página y `prototypes/README.md`.

El editor de arenas:

```bash
uv run --project pipeline python prototypes/arena/editor/build.py
```

```bash
python3 prototypes/arena/editor/serve.py
```

y abrir http://127.0.0.1:8772/. "Guardar" escribe `prototypes/arena/arenas/<nombre>.json`; "▶ Probar" abre el juego con la arena del editor.

## Lo que cuesta plata

Generar clips de video y gráficos usa APIs pagas (fal.ai para Seedance y los modelos de imagen; Gemini para Veo y Omni). Cada comando que gasta tiene `--dry-run`, que muestra qué manda y cuánto sale: siempre correrlo primero. Las claves (`FAL_KEY`, `GEMINI_API_KEY`) van en el entorno de cada uno (el llavero de macOS o el `~/.zshrc`), **nunca** en el repo. Ver "Bake-off" en `pipeline/README.md`.

## Convenciones del repo

- Los PNG alternativos de cada comparación quedan en disco (`raw/` y `post/` están en `.gitignore`); al repo van la config, la comparación, los `.json` de procedencia y **la opción elegida**, que se agrega con `git add -f`. Si un build se queja de que falta una imagen de `post/`, es una elegida que no se subió.
- Los `dist/` de los prototipos no van al repo: se rearman con su `build.py`.
- Las referencias de terceros (sprite rips de otros juegos) son sólo para analizar y nunca van al repo.
- Toda animación nueva se revisa cuadro por cuadro sobre verde antes de usarla en un juego.
- Los juegos se publican como artifacts privados de Claude (los links están en `prototypes/README.md`): para que los vea otro, se comparten desde el menú Share de la página.
