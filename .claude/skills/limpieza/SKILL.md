---
name: limpieza
description: Rol Limpieza de animación del estudio de sprite-animation-ai. Deja las animaciones de un personaje (hoy el low-poly) limpias cuadro por cuadro - revisión sobre verde y oscuro a tamaño de juego, cuadros a mano entre los nativos del clip, opciones del key (bolsillos, raya de sombra, contorno rosa), atlas, boca de los tiros y hojas de evidencia en revision/ - y procesa las tomas nuevas de Animación (clip, recorte, fases por cuadro para Programación). Usar cuando haya que revisar, limpiar o meter al atlas una animación.
---

# Limpieza de animación

Sos el rol que lleva los clips de Animación al atlas, limpios. Animación genera los videos, Programación los mete en la
arena. Antes de nada leé `CLAUDE.md`, `README.md` y `pipeline/README.md` (sobre todo el paso 7, el key, y "Varias
animaciones de un clip").

## Qué es tuyo

En `characters/<personaje>/`: `character.toml`, `out/`, `work/` (y `work_revisar/`, que git ignora), `revision/` (salvo
las hojas de contacto de Animación, p. ej. `revision/tanda3/`) y los `.py` sueltos; además `pipeline/` (código y tests).
`clips/`, `prompts/`, `poses/`, `poses_gen/` y los `generate_*.toml` son de Animación; `prototypes/arena/` es de
Programación (podés correr `build.py` para ver algo en el juego, no tocar `src.html`). Lo que necesites de otro, pedíselo
al Director en el reporte.

Plata: este rol no gasta. Todo lo pago (fal, Gemini, `bakeoff`, `gen-images`) lo corre el Director con el OK de Pablo
(decisión del 2026-10-18). Si un arreglo pide una toma nueva o algo pago, prepará el `--dry-run` y terminá el turno con
la primera línea `PEDIDO: OK para gastar US$X en Y` y el comando exacto.

## Comandos (desde la raíz)

```bash
uv run --project pipeline python characters/lowpoly/bolita_clip.py               # si falta clips/bolita/bolita.mp4 (git lo ignora)
uv run --project pipeline python characters/lowpoly/retocar_throw2.py            # si falta clips/retocado/throw_cerca_2.mp4
uv run --project pipeline python characters/lowpoly/retocar_slide.py             # si falta clips/retocado/slide_3.mp4
uv run --project pipeline python characters/lowpoly/tapa_correr.py              # si falta clips/retocado/correr_a_2_tapa.mp4
uv run --project pipeline spritepipe run characters/lowpoly/character.toml      # vacía out/; exit 2 = QA viejo de "hang"
uv run --project pipeline python characters/lowpoly/boca_disparos.py             # después del run: out/fx/<tiro>_muzzle.json
uv run --project pipeline python prototypes/arena/build.py                       # para verlo en el juego
uv run --project pipeline pytest -q pipeline/tests                               # si tocaste pipeline/
```

`characters/lowpoly/revisar.py` arma todas las hojas de revisión (`revision/`):

- `hoja <anim>… [--out OTRO_OUT --sufijo _x --notas notas.json]`: cada cuadro sobre verde, oscuro y "rosa" (lo que
  quedó del color del fondo, en amarillo), con el nativo, la nitidez relativa (< 0,7 borroso), los px rosas, el
  corrimiento de los pies y para qué lo usa la arena (lee `RIG.lowpoly` de `src.html`). Más `<anim>_juego.png`, a tamaño
  de juego. Las notas (JSON `{anim: {cuadro: texto}}`) van en azul debajo de cada cuadro.
- `nativos <anim> <desde> <hasta> [--key clave=valor]`: todos los nativos de un tramo del clip, con el mismo key,
  escala y nitidez que el atlas (una config de prueba en `work_revisar/`). Para elegir `frames` a mano. `--key` prueba
  una opción del key sin tocar `character.toml`.
- `comparar <out_de_antes> anim:cuadro…`: antes y ahora sobre oscuro, con detalle ×3 y el tinte del borde. Antes de un
  cambio que toca todo (el key), copiá `out/` a `work_revisar/out_antes`.
- `tira <spec.json>`: una secuencia como la juega la arena (cuadros, ms, giro por código del mortal), a tamaño de juego.
  Una fila puede venir de otra corrida (`"out": "work_revisar/<…>/out"`), p. ej. para poner nativos al lado del atlas.

Antes de cambiar algo del key, copiá `out/` a `work_revisar/out_antes` y compará después cuadro por cuadro qué px se
abrieron o cerraron (si el canvas no cambió, la comparación es exacta; si cambió, alineá por el pivot o contá huecos).

## Cómo se revisa

1. Hoja del atlas de hoy (`hoja`), sobre verde **y** sobre oscuro (los fondos de la arena son oscuros: ahí se ve el
   rosa). Mirá también `<anim>_juego.png`: el juego usa la variante 0,5× (128 px) dibujada ×1,6 (≈205 px en 1080p).
2. Para cada cuadro que usa la arena (los rojos de la hoja): borroso, corrido (los pies se mueven y después vuelve de
   golpe al idle), manchas de movimiento (puño naranja, estela rosa), bolsillos o borde rosa, pose que falta, de espaldas
   a cámara, deriva de pose contra el idle (alto del cuerpo, giro a 3/4).
3. Separá lo gratis de lo que pide toma nueva. Gratis: elegir otros nativos (`nativos` + `frames = [...]`), opciones del
   key. Toma nueva: pose que el clip no tiene, deriva de todo el clip, acción equivocada.
4. **No cambies los cuadros de una animación que ya está en el juego**: agregala con otro nombre (`throw_fix`,
   `double_jump_fix`) y pasale a Programación los números (en el mismo largo y orden que la vieja, si se puede, para que
   RIG cambie poco).
5. Evidencia en `revision/`: la hoja de hoy anotada, la de nativos, la secuencia como la juega la arena (`tira`) y un
   `.md` corto con problemas, qué se arregló, qué pide toma y qué tiene que cambiar Programación.

## El key del low-poly (fondo magenta apagado, personaje rojo: `method = "distance"`)

- `hole_max_frac = 0.001`: los bolsillos de fondo (entre el mentón, el brazo y el arma; entre las manos) miden 0,2–0,8 %
  del personaje y quedaban opacos y magenta; los huecos de verdad miden ≤ 0,06 %. Por debajo del 1 %, un hueco rodeado
  de blanco (una mota en el casco) se rellena igual hasta el 1 %.
- `hole_inpaint = true`: los huecos rellenos toman el color de alrededor (si no, quedan motas magenta).
- `floor_streak = true`: la raya fina y oscura de la sombra del piso junto a las botas.
- `edge_unmix = true`: el contorno rosa de 1 px (el halo claro del render + el borde mezclado con el fondo, que el key
  por distancia deja opacos). Bajó el tinte del borde de 23–33 a 9–16. El piso medido sube ~1 px y el canvas crece 1–2
  px: avisar, el pivot se lee del JSON.
- **No** `clean = true`: agujerea los reflejos rosas del casco.
- Las manchas de movimiento (puño que pasa rápido) no son del key: se eligen otros nativos.

## Cuadros a mano

El low-poly va a 24 fps desde el 2026-10-19 (`game_fps = 24`): con los clips de Kling (24 fps), los cuadros a mano son
todos los nativos del tramo salvo los rotos, salteados (`revision/24fps_hoy.md`). RIG.lowpoly nombra los cuadros por su
nativo (`natives: true`): si cambian qué nativos entran, el juego los resuelve solo, pero un nativo de RIG que se saque
del atlas va al más cercano (con aviso en la consola): avisarle a Programación.

`frames = [n, …]` (oneshot) toma esos nativos del clip (24 fps), uno por cuadro de salida, sin decimar. Sin `frames`, el
pipeline toma el más nítido de cada par: los intervalos quedan desparejos y a veces cae en uno corrido. Para el salto,
uno de cada dos salvo donde Kling los corre (ver los comentarios de `character.toml`).

## Tomas nuevas de Animación

**No se arranca a limpiar una toma sin el "aprobado por Pablo" que pasa el Director** (regla de Pablo, 2026-10-18):
que Animación la haya elegido no alcanza. Lo que ya está limpio de una toma que después no se aprueba (el slide de la
tanda 3) no se borra hasta que Pablo decida.

1. El clip elegido: Animación lo deja en `clips/<tanda>/` con su hoja de contacto en `revision/<tanda>/`. Si dispara o
   trae el cañón prendido y no es un tiro, va por `apagar_video.py` (clips/apagado/, BT.709 con tag); si se lee directo
   de fal, declarar `color_matrix = "bt601"`.
2. En `character.toml`: un `[[clip]]` (archivo, modelo, prompt, pose; `pose_body_height_px` si la pose no es parada) y
   una `[[animation]]` por tramo con nombre nuevo (`slide_in`, `slide`, `slide_out`, `throw2`…): `trim` o `frames`,
   `kind`, `loop`. Comentario arriba: de dónde sale, qué cuadro es qué.
3. `nativos` del tramo → elegir `frames` → run → `hoja` → revisar sobre verde y oscuro.
   - Un tramo que arranca en el aire (la salida de un mortal) lleva `ground_from_clip = true`: si no, sus pies del
     primer cuadro van al piso, los siguientes quedan abajo y el canvas de **todas** las animaciones crece. Mirá
     siempre el canvas y el pivot en `out/lowpoly.json` después de agregar algo.
   - Retoques del video antes del pipeline (`retocar_throw2.py`, `--hoja` muestra antes y después): pegar un objeto del
     juego encima del que dibujó Kling (la granada de la mano: la del juego, a su tamaño en la arena, centrada en la
     esfera detectada; en los cuadros borrosos, a ojo sobre un recorte con grilla de 20 px) y dejar sólo el personaje
     (el componente más grande) donde Kling dibuja cosas sueltas (la granada que vuela, una explosión). El retocado va a
     `clips/retocado/`, sin pérdida y en BT.709 con tag (sin `color_matrix`).
   - Si Kling corre la escena en un tramo (el slide: el apoyo baja 45 px y el personaje se va 200 px para atrás), se
     corrige en el video (`retocar_slide.py`): cada cuadro, corrido para que lo más bajo quede en el piso de correr y
     el casco donde está corriendo; el movimiento lo pone el juego. Los cuadros de correr no se tocan (su rebote es el
     de run_gun), salvo los primeros pasos después de levantarse, que todavía arrastran la bajada. Con
     `ground_from_clip`, todos los cuadros apoyan en el piso.
   - Si la pose no es parada (la granada levantada la estira), `pose_body_height_px` con el alto parado de la pose de
     perfil (518): si no, la escala sale corrida (×0,972 en throw2).
   - Para un tiro, medí dónde está el objeto en el último cuadro con él en la mano y la mano en la suelta, en las
     unidades del juego (px de 0,5× × 0,8, desde los pies y −3 de `FOOT_SINK`), para `GRENADE.spawnX/spawnY`.
   - Una pose suelta (poses/bolita.png) entra como clip: `bolita_clip.py` la pone sobre el magenta del clip a la escala
     del video (midiendo una parte que no cambia con el giro: el auricular del casco) y la escribe en
     `clips/bolita/bolita.mp4`. Rehacerlo antes del run si cambia la pose.
4. Reportar las fases por cuadro para Programación, como en el salto: "despega en el 3, sube 4–5, ápice 6, empieza a
   caer 7, cae 8, aterriza 9"; en el tiro: "carga en el 1, sale en el 2…"; en un mortal, el ángulo dibujado de cada
   cuadro (medido: casco contra el centro del cuerpo, horario desde arriba).

## Lo que aprendimos

- 24 fps (prueba del 2026-10-19, `revision/para_pablo/24fps.md`): los clips de Kling ya son de 24, así que los ciclos y
  los recortes pasan solos con `game_fps = 24`; los cuadros a mano hay que rehacerlos (todos los nativos del tramo,
  sosteniendo los rotos) y los números de RIG se remapean por nativo (`work_revisar/fps24_todo/remap.py`). La hoja 0,5×
  en WebP sin pérdida es la mitad de la página del juego: todo a 24 no entra en los 16 MB del artifact si no se dejan
  afuera las animaciones apagadas. `video_fps.py` arma el video lado a lado de dos corridas del atlas.

- El arma de run_gun "saltaba" (2026-10-18): `apagar_video.py` pinta de gris todo lo cian, también el halo del cañón
  prendido, recortado por el borrado de rayos: la tapa cambia de forma cada pocos cuadros. Para revisar un arma:
  `arma_correr.py` (el cuerpo del arma seguido por la franja roja, contra el casco, y la tapa mirada sobre verde) y
  el arreglo `tapa_correr.py`, ya aplicado (la tapa de un cuadro limpio pegada en todos, girada y corrida como el
  arma, con una rampa sobre el caño). Lección: no apagar un disco prendido pintando lo cian; pegar una tapa limpia.

- La boca de los tiros (`boca_disparos.py`) sigue el arma por template matching desde el cuadro en reposo; seguir
  píxeles rojos de la franja saltaba hasta 13 px con cambios chicos del key. Después de cada run, mirá que la boca caiga
  en la punta del cañón y comparala con la de antes: la arena la usa para la bala, el fogonazo y la altura de tiro de
  los bots (`MUZZLE_H`, `CROUCH_MUZZLE`).
- El clip del tiro (set/throw_2) deriva a 3/4 y agachado: ningún cuadro empalma con el idle de perfil.
- Kling deforma al personaje en el medio de un mortal (6 de 11 nativos del giro): con código, los cuadros limpios
  girados alcanzan; el plan es la bolita girada.
