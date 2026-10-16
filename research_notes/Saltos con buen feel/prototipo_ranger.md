# Línea de base: el salto del ranger en el prototipo (2026-10-16)

Qué hay hoy en `prototypes/ranger/src.html` y en los sprites del ranger, para que las recomendaciones partan de ahí. Los números del código salen de leer el archivo (con cambios sin commitear de otra sesión al momento de leerlo). Los de los dibujos son **conteo propio** o **medición propia** sobre `characters/ranger/out/sheets/1x/*.png` y `characters/ranger/out/ranger_1x-0.json` (altura de cada frame y subida de los pies sobre el pivot).

## Física y estados (código)

- Personaje: 128 px en el atlas, dibujado al 80% (`CHAR_DEFAULT = 0.8`, ~102 px). Collider 40 × 112 px a escala de atlas (×0,8 en pantalla). Animaciones a 12 fps; juego a 60 Hz. Vista 960 × 540.
- Feel "reporte": carrera 300 px/s, v0 1067 px/s, gravedad 2963 subiendo y 4898 cayendo, recorte a 480 px/s al soltar, terminal 1400 px/s, coyote y buffer 0,10 s, corrección de esquina 12 px. Salto completo ≈192 px (1,5 H) en 0,36 s de subida y 0,28 s de bajada.
- Despegue instantáneo: `P.vy = -FEEL.v0` en el tick del input. Los 2 frames de preparación del clip no se muestran en el modo físico.
- Selección del dibujo en el aire por vy: vy < −240 → `rise[0]`; < −60 → `rise[1]`; < +160 → ápice; si no → `fall[0]`. `fall[1]` nunca se usa. Disparando en el aire, un único frame (`AIR_SHOT`) del clip `jump_shoot`.
- Aterrizaje: `landT = 0,2 s`, muestra los frames de aterrizaje del clip (0,07 s cada uno) sólo si el jugador está quieto; moverse o saltar los saltea. Sin bloqueo de control.
- Doble salto: una vez por estadía en el aire (se recarga al pisar o al colgarse), en cualquier momento del vuelo. `P.vy = -0,9·v0 = −960 px/s` sin importar la vy previa (reseteo). Suma ≈156 px sobre el punto donde se activa (cálculo propio: 960² / (2·2963)). El recorte del salto variable también lo afecta. Durante el mortal (`FLIP_DUR = 0,42 s`) no se puede disparar. Sin efecto visual ni sonido. Control horizontal sin cambios.
- Squash/stretch, rotación o inclinación por código: no hay. El sprite se dibuja con `ctx.scale(±0,8, 0,8)` alrededor del pivot de los pies.
- Polvo (`dust()`): bolitas redondas que salen la mitad a cada lado, por el piso, con un poco de velocidad hacia arriba; vida 0,45–0,6 s, gravedad 120, arrastre 4, crecen ×1,6. Despegue: 12 partículas, 170 px/s, 13 px. Aterrizaje suave: 14, 190 px/s, 14 px. Duro (vy > 900 px/s): 22, 260 px/s, 17 px.
- Sacudida de cámara: 0,04 s (aterrizaje suave, y también cada disparo) u 0,08 s (aterrizaje duro), con ±1,5 px al azar por frame. Sin hit stop. Vibración del pad sólo en el disparo a dos manos.
- Sonido: no hay ninguno.
- Cornisa: agarre automático con vy > −220 px/s; la mano del primer frame del colgado tiene que quedar a ≤22 px en horizontal de la esquina del bloque y entre 20 px arriba y 26 px abajo del tope; afuera del bloque y con lugar arriba. Agarre: frames 6–9 de `hang_in` a 0,05 s (0,2 s), después el loop `hang` a 12 fps. El sprite se dibuja detrás del bloque y sólo asoman los dedos. Desde el colgado: salto o arriba → sube; abajo → suelta (vy 60 px/s, 6 px hacia afuera, 0,35 s sin re-agarre). No hay salto desde el colgado. La subida es provisoria: 0,14 s de interpolación hacia arriba y después `crouch_out` (4 frames a 0,055 s), ≈0,36 s en total, y termina con vx = 0.

## Los dibujos (conteo propio sobre los sheets)

**`jump` (10 frames, del clip r08 de Davinci).** Frame 0 parado (130 px de alto). Frame 1 apenas agachado (125 px). Frames 2–6: **la misma pose recogida repetida**, piernas encogidas y pistola al frente, con variaciones mínimas; los pies suben 24, 30, 31, 30 y 26 px dentro de la celda. Frames 7–9 parado (126–128 px). No hay estirón de despegue, ni ápice distinto de la subida, ni caída con las piernas buscando el piso, ni squash de aterrizaje que se lea. **Elegir el dibujo por vy hoy cambia poco lo que se ve**, porque los cinco dibujos del aire son casi iguales.

**`double_jump` (11 frames, toma g06 por API).** Ángulos del cuerpo a ojo, ±20° (medición propia): 0 parado; 1 despegue recogido, vertical; 2 inclinado ≈35° hacia adelante; 3 ≈80–90° (horizontal); 4 ≈150°; 5 ≈200° (cabeza abajo); 6 ≈290°; 7 y 8 casi verticales, cayendo; 9 y 10 aterrizaje agachado (126 px). Es un mortal hacia adelante con **5 dibujos de giro (2–6)**, cada uno el mismo bollo recogido girado unos 45–90°. El prototipo filtra los frames "girados" por proporción (ancho/alto > 0,95 o alto < 100 px) y se queda con **3, 4 y 5 (≈90° → 200°) durante 0,42 s** (≈7 fps). Muestra poco más de media vuelta y vuelve de golpe al dibujo vertical del salto: le faltan la entrada (frame 2) y la salida (frame 6).

**`hang_in` (10 frames, r07) y `hang` (9 frames).** 0–4: parado y agachándose para el salto vertical; 5: despega estirando el brazo; 6–9: colgado de **una sola mano** cerrada sobre una barra invisible (con un hueco donde estaba la barra), la otra mano con la pistola abajo. `hang` es el loop colgado (154–155 px de alto).

**`poses/ranger_climb_magenta_16x9.png`.** El ranger colgado de una mano, sobre magenta puro (#FF00FF). Para generar por API hay que pasarlo a magenta apagado (`pad-pose --bg C42D7D`): con magenta puro Seedance pinta reflejos en el casco blanco (ver `characters/ranger/generate.toml`).

## Trabajo en curso de otras sesiones (2026-10-16, sin commitear)

- `characters/ranger/generate_climb.toml` prepara dos clips por API desde la misma pose, colgado **con las dos manos**: `climb` (colgado → sube → parado sobre el canto; primer y último frame fijos, 4 s, 2 tomas) y `hang_two` (loop colgado). Prompts en `characters/ranger/prompts/climb.txt` y `hang_two.txt`. Las poses (`ranger_climb_first_…` y `ranger_climb_last_…`) salen de `poses_gen` con `climb_frames.py`. Al momento de leerlo, los clips todavía no estaban en `clips/`.
- `backgrounds/ranger_fx/gen.toml` y `prototypes/fx_lab/` generan fogonazos e impactos con la API de imagen (GPT Image 2.5 Sunburst por fal, alfa nativo) para compararlos con los de código. Hay una investigación hermana en `research_notes/Fogonazos y efectos de disparo/` que cubre los efectos del disparo, incluida la sacudida por disparo.
- Costo de referencia que dio Pablo: ~US$1,50 por toma de Seedance 2.0. Las tandas por API (`spritepipe bakeoff`) generan 2 tomas por animación de 4–5 s a 720p.
