---
name: animacion
description: Rol Animación del estudio de sprite-animation-ai. Tomas nuevas de un personaje (hoy el low-poly) con Kling O3 standard por el bakeoff del pipeline - pose de arranque, prompt, generate_*.toml, dry-run y pedido de gasto, generación, hojas de contacto sobre verde y elección de toma y cuadros para Limpieza. Usar cuando haya que generar o rehacer una animación con video IA.
---

# Animación: tomas nuevas con Kling O3

Sos el rol que genera los videos. Limpieza los procesa (`character.toml`, `out/`), Programación los mete en la arena.
Antes de nada leé `CLAUDE.md`, `README.md` y la parte del bakeoff de `pipeline/README.md`.

## Qué es tuyo

En `characters/<personaje>/`: `clips/`, `prompts/`, `poses/`, `poses_gen/` y los `generate_*.toml`. Más esta skill.
`character.toml`, `out/`, `work/`, `revision/` (salvo tus hojas de contacto), los `.py` sueltos y `pipeline/` son de
Limpieza: se leen, no se tocan. Si necesitás un cambio de otro, pedíselo al Director en el reporte.

## Plata

Todo lo que llama a fal o Gemini se corre primero con `--dry-run`. Con el costo, terminá el turno con la primera línea
`PEDIDO: OK para gastar US$X en …` (un solo pedido por tanda) y, abajo, el comando exacto a correr desde la raíz.
**Los comandos pagos no los corre Animación**: los corre el Director en su sesión, con el OK de Pablo (Pablo,
2026-10-18). Si el pedido tiene un paso gratis en el medio (elegir una pose y pasarla por pad-pose antes del video),
van dos comandos y se avisa que entre uno y otro sigue Animación. La clave se carga sin mostrarla:

```bash
eval "$(grep '^export FAL_KEY=' ~/.zshrc | tail -1)"
```

## La receta (lo que anduvo)

- **Modelo**: `kling-o3-std`, 5 s, 720p, sin audio, 2 tomas por animación (US$0,42 por toma). Sólo primer y último
  cuadro: con referencias (hojas de vistas) Kling gira al personaje hacia cámara (`reporte_idle.md`).
- **Pose de arranque**: 1920×1080, magenta apagado `#C42D7D`, personaje al 48% del alto y pies al 72%
  (`spritepipe pad-pose concept.png salida.png --bg C42D7D`; `--feet 0.92` deja aire arriba para saltos). Siempre a la
  escala del idle: si la pose no es parada, medí el casco (ver `subida_frames.py`, `colgarse_frames.py`).
- **Arma apagada**: con el disco cian prendido, Kling dispara aunque el prompt lo prohíba. Apagala en la pose:
  `uv run --project pipeline python characters/lowpoly/apagar_arma.py entrada.png salida.png`.
- **Último cuadro**: `last_frame = true` (igual al primero) cierra loops y deja entrada y salida empalmadas; una ruta
  a otra pose sirve para transiciones (colgado → parado, con granada → mano vacía).
- **Poses nuevas**: `poses_gen/gen.toml` (gen-images, GPT Image 2.5 y Nano Banana, 2 de cada uno, US$0,36–0,47 por
  asset). Elegí una y pasala a 16:9. Si es parada, con pad-pose. Si es baja o rara (deslizarse, agachado, bolita), con
  `pose_16x9.py` de esta skill, que escala por el casco y apoya en el piso de otra pose:

  ```bash
  uv run --project pipeline python .claude/skills/animacion/pose_16x9.py characters/lowpoly/poses_gen/post/<asset>/<img>.png \
      --ref characters/lowpoly/poses/correr_apagada_dullmagenta_16x9.png --out characters/lowpoly/poses/<asset>_dullmagenta_16x9.png
  ```

- **Proporciones**: los modelos de imagen alargan piernas y brazos cuando la pose los estira (tanda4, el slide: la
  pierna estirada medía 1,5 cascos). Las medidas del low-poly, en anchos de casco (perfil_apagada): pantalón, de la
  cadera a la bota, 0,23; bota 0,5 de largo y 0,34 de alto; parado, de la cadera a la suela 0,56. Una pierna estirada
  en el piso con la bota acostada mide ~0,75 (pantalón + bota). Pidiéndolo con números en una edición bajó a ~1,0
  (deslizarse_b), pero no llegó. Antes de pasar una pose a video, y siempre que Pablo la tenga que aprobar, armá la
  hoja de comparación con la de perfil a la misma escala de casco y medí a ojo contra la marca (la medición
  automática por colores no sirve: el traje es del mismo gris que el pantalón):

  ```bash
  uv run --project pipeline python .claude/skills/animacion/hoja_poses.py characters/lowpoly/poses_gen/post/<asset>/*.png \
      --ref characters/lowpoly/poses/perfil_apagada_concept.png --out characters/lowpoly/revision/para_pablo/<asset>.png \
      --pierna 0.75 --leyenda "pierna estirada con las proporciones de parado" --notas "nota 1" "nota 2" ...
  ```

  Las poses nuevas las aprueba Pablo como imagen (`PARA APROBAR: pose de …`) antes de gastar en video.
  Si con palabras no respeta las proporciones (en el slide, dos rondas), no repitas el pedido: armá la pose con partes
  reales del personaje (la pierna de perfil girada mide justo, `revision/para_pablo/pierna_real_prueba.png`) o con
  una guía dibujada encima, y una sola edición para unir.
- **Pose fija**: si la pose de la acción importa (el slide), no la describas sólo con palabras: Kling hace lo que le
  sale (tanda3: sentado con las piernas abiertas). Generala quieta en poses_gen y usala de último cuadro de la entrada
  y de primer cuadro de la salida, en dos clips cortos (3 s), como subir (generate_tanda4.toml). El sostenido es la
  pose misma y las dos mitades empalman. Pero el slide así no salió: la pose generada traía piernas largas y manos
  raras, y Pablo prefirió volver a una toma directa con un prompt que nombra cada error de las tomas anteriores
  (generate_tanda5.toml, prompts/slide_directo.txt). De 4 tomas, 1 salió con los pies adelante y sin disparar
  (slide_3); 2 se tiraron de panza igual. "Feet-first" sigue saliendo de panza la mitad de las veces: pedí 4 tomas,
  no 2. Las piernas salieron del largo justo con "short and thick ... the same length as in the running pose". Ojo: un clip que **arranca** quieto con el arma adelante dispara al empezar
  (tanda4 slide_out 1 y 2, del cuadro 1 al 15–25) y Kling puede correr al personaje mientras tanto (46 px): se usa
  desde que deja de disparar y Limpieza alinea el empalme.

### El prompt

Copiá la estructura de `prompts/` (en inglés): estilo low-poly → cámara fija y de perfil → "Use the input image as the
first frame and the last frame" → la acción → prohibiciones → consistencia → fondo. Lo que aprendimos:

- **En el lugar**: "runs in place like on a treadmill, … no forward travel", y "the camera never follows the character".
- **Que arranque ya** ("Right away, …"). Si la acción es corta, Kling se queda quieto al principio y rellena el final
  inventando: en `set/throw_2` estuvo quieto 28 cuadros y al final disparó un rayo.
- **No disparar**: "The pistol is a dark, unlit prop: it never lights up and nothing ever comes out of it, no beam, no
  laser, no flash, no spark, no glow and no smoke." Estirar el brazo de golpe lo lee como disparo: si no hace falta,
  el arma queda baja o al pecho.
- **Repetir la acción** ("twice in a row", "three jumps") da más cuadros para elegir en saltos.
- **Mortales**: Kling deforma al personaje en el medio del giro. Pedí la bolita sin girar y que el juego la rote. Aun
  sin girar, mientras sostiene la bolita el casco crece ~30% y pierde la franja roja (tanda3 double_jump_1, 24–41): la
  bolita sostenida conviene que sea `poses/bolita.png` y del video sólo el encogerse y el abrirse.
- **Brazo de atrás**: una acción grande con la mano de atrás (de perfil a la derecha, la izquierda) hace que Kling gire
  al personaje hacia cámara para mostrarla (tanda3 throw_1 y _2: anticipación de frente, vuelta de espaldas y
  disparo al final). La acción va con el brazo de adelante: con la granada en la mano de adelante y la pistola en la
  de atrás (tanda3b throw_cerca_2) tira bien, no gira de espaldas ni dispara y vuelve a agarrar la pistola. Al cargar
  abre el torso a tres cuartos hacia cámara, que es lo natural, y la cara sigue de perfil. Kling igual agrega cosas
  sueltas (una explosión fuera de cuadro, chispas en la granada): se saltean o las borra Limpieza.
- **Duración**: 4 s alcanza para un tiro con vuelta; con 5 s rellena con quietud al principio y disparos al final.
- **Deslizarse**: "feet-first slide" salió una vez sentado con la pierna de atrás estirada, quieto y bien (tanda3
  slide_2) y otra de panza, corrido 47% del cuadro y disparando (slide_1). Una deriva alta en `bakeoff.md` avisa que
  el personaje se fue del lugar.
- Siempre: "The body stays in side view and never turns toward the camera", "Keep exactly the same design, proportions,
  colors and polygon facets in every frame", "Matte surfaces…", "Solid flat background, the same color as in the input
  image, unchanged, with no shadow and no floor".

## Pasos

1. Pose(s) de arranque y fin en `poses/` (apagadas, a escala). Si falta una, va en `poses_gen/gen.toml`.
2. Prompt en `prompts/<anim>.txt` y un `generate_<tanda>.toml` nuevo (copiá `generate_tanda3.toml`), con un
   comentario arriba que diga qué es cada toma y de dónde sale cada pose. Cada toml con su `out_dir` propio: hasta el
   dry-run reescribe el `bakeoff.md` de su carpeta con sólo sus animaciones.
3. Dry-run y pedido:

   ```bash
   uv run --project pipeline spritepipe bakeoff characters/lowpoly/generate_<tanda>.toml --dry-run
   ```

   Si una pose todavía no existe (sale de gen-images en la misma tanda), el bakeoff no carga: hacé el dry-run sobre
   una copia con esa pose cambiada por otra del mismo tamaño (el precio no depende de la imagen).
4. El Director corre `bakeoff … --yes` (sin `--dry-run`) y avisa. Los clips quedan en
   `clips/<tanda>/kling-o3-std_<anim>_<n>.mp4` con `bakeoff.md` (QA). `--anims a,b` corre sólo esas.
5. Hoja de contacto de cada toma sobre verde, con el número nativo (24 fps) de cada cuadro, el que usa Limpieza en
   `trim` y `frames`:

   ```bash
   uv run --project pipeline python .claude/skills/animacion/hoja_toma.py characters/lowpoly/clips/<tanda>/*.mp4 \
       --out characters/lowpoly/revision/<tanda>
   ```

   Mirala cuadro por cuadro (deformaciones, cara, arma que se prende, rayos, el personaje que se corre del lugar).
   Para ver de cerca un tramo: `--step 1 --desde 36 --hasta 60`, o cuadros sueltos con recorte fijo en px del video:
   `--cuadros 38,40,42 --recorte 430,180,880,560 --alto 320 --sufijo _entrada`. Los cuadros movidos (borrosos, manchas
   en las piernas) se saltean: Limpieza arma la animación con `frames` a mano.
6. **Pablo aprueba cada toma mirando el video** antes de que vaya a Limpieza o a Programación (Pablo, 2026-10-18).
   Elegí la mejor y dejale en `characters/lowpoly/revision/para_pablo/` el tramo útil sobre verde como `<anim>.mp4`
   (con el número de cada cuadro en la esquina) y su hoja de contacto `<anim>.png`:

   ```bash
   uv run --project pipeline python .claude/skills/animacion/video_verde.py characters/lowpoly/clips/<tanda>/<toma>.mp4 \
       --desde 12 --hasta 84 --out characters/lowpoly/revision/para_pablo/<anim>.mp4
   uv run --project pipeline python .claude/skills/animacion/hoja_toma.py characters/lowpoly/clips/<tanda>/<toma>.mp4 \
       --desde 12 --hasta 84 --out characters/lowpoly/revision/para_pablo --nombre <anim>
   ```

   El recorte sigue al personaje; si algo que tiene que verse sale de cuadro (la granada al soltarla), pasá
   `--recorte x0,y0,x1,y1` a los dos, dejando afuera lo que no va (la explosión que inventa Kling). Ojo: el recorte va
   en px del video (1280×720), no de la pose (1920×1080).

   Si la animación sale de dos clips (entrada y salida que empalman en una pose), van los dos tramos en un solo video,
   con la hoja de los mismos cuadros; `@dx` corre un tramo en x si Kling dejó al personaje en otro lugar:

   ```bash
   uv run --project pipeline python .claude/skills/animacion/video_verde.py clips/tanda4/kling-o3-std_slide_in_1.mp4:40-72 \
       "clips/tanda4/kling-o3-std_slide_out_1.mp4:18-35,38-46@-46" \
       --out characters/lowpoly/revision/para_pablo/slide.mp4 --hoja characters/lowpoly/revision/para_pablo/slide.png
   ```
7. Terminá el turno con la primera línea `PARA APROBAR: <anim>` y qué mirar (dónde están las fases y los defectos
   que conocés). El Director se lo lleva a Pablo y te reenvía la respuesta. Con el OK, los cuadros útiles de cada fase
   (entrada, sostenido, salida, el cuadro en que la granada sale de la mano, etc.) van a Limpieza en la nota de la
   tanda, para que arme `character.toml`.
