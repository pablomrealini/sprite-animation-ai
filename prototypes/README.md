# Juegos de prueba

Dos prototipos jugables para probar los sprites en movimiento, con teclado y mouse. Son una página HTML con un canvas, sin dependencias.

| Personaje | Artifact publicado | Qué prueba |
|---|---|---|
| comando | [Polígono del Comando](https://claude.ai/artifact/VUQhrtgp2HH4SRbuV68Yvm) | correr, saltar (como está o físico) y disparar |
| ranger | [Polígono del Ranger](https://claude.ai/artifact/NwSY6oEUuDF6DYJxpgXByF) | correr, saltar, colgarse de cornisas y subir, disparar con una o dos manos, agachado y en el aire. Selector de feel: el del reporte de run-and-guns o el anterior |

Los artifacts son privados: para que los vea alguien más, hay que compartirlos desde el menú Share de la página.

## Armar

```bash
uv run --project pipeline python prototypes/build.py ranger
```

Lee `characters/<personaje>/out/` (el atlas 1x y su JSON), mide por frame la boca del arma, la subida del salto y la mano del colgado, y deja `prototypes/<personaje>/dist/index.html` con el atlas al lado. Si cambiaron las animaciones, primero corré `spritepipe run` del personaje.

`src.html` no tiene `<!doctype>` ni `<head>`, porque el publicador de artifacts los agrega. Para abrirlo local hace falta un navegador común (doble clic sobre `dist/index.html`), no el panel de archivos de la app de Claude, que no carga el PNG del atlas.

## Qué es provisorio

- Ranger: el idle es un cuadro quieto, la subida a la cornisa salta de posición con la animación de pararse (falta el clip de trepar), y al correr dispara desde la mano que balancea.
- Los efectos (rayos, fogonazo, chispas, vainas, sombra) son de código.
