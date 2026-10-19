# Bake-off (2026-10-18)

Modelos: kling-o3-std. Animaciones: slide (pose `correr_apagada_dullmagenta_16x9.png`, prompt `slide.txt`), throw (pose `con_granada_dullmagenta_16x9.png`, prompt `tirar_granada.txt`), double_jump (pose `salto_apagada_dullmagenta_16x9.png`, prompt `doble_salto_bolita.txt`). 2 clips por modelo y animación, 720p 16:9, sin audio.

| clip | estado | QA | deriva % | zoom % | borde | pose MAD | loop | US$ | notas |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| kling-o3-std_slide_1.mp4 | ok | warn | 47.3 | 20.8 | 0 | 1.94 | - | 0,42 | fondo poco plano (desvío 8.78): el key va a necesitar más tolerancia |
| kling-o3-std_slide_2.mp4 | ok | warn | 5.7 | 0.6 | 0 | 1.97 | - | 0,42 | fondo poco plano (desvío 9.24): el key va a necesitar más tolerancia |
| kling-o3-std_throw_1.mp4 | ok | warn | 24.8 | 3.6 | 2 | 1.79 | - | 0,42 | el personaje toca el borde del cuadro en 2 frames (arma o capa cortada); fondo poco plano (desvío 9.11): el key va a necesitar más tolerancia |
| kling-o3-std_throw_2.mp4 | ok | warn | 15.7 | 0.4 | 2 | 1.73 | - | 0,42 | el personaje toca el borde del cuadro en 2 frames (arma o capa cortada); fondo poco plano (desvío 9.16): el key va a necesitar más tolerancia |
| kling-o3-std_double_jump_1.mp4 | ok | warn | 9.5 | 8.3 | 0 | 1.71 | - | 0,42 | fondo poco plano (desvío 8.76): el key va a necesitar más tolerancia |
| kling-o3-std_double_jump_2.mp4 | ok | warn | 12.4 | 1.5 | 0 | 1.73 | - | 0,42 | fondo poco plano (desvío 8.1): el key va a necesitar más tolerancia |

| modelo | bajados | bloqueados | errores | QA ok/warn/fail | pose MAD (mediana) | mejor loop | US$ |
|---|---:|---:|---:|---|---:|---:|---:|
| kling-o3-std | 6 | 0 | 0 | 0/6/0 | 1.79 | - | 2,52 |

Gastado (estimado, a precio de lista): US$ 2,52.
