# Bake-off (2026-10-18)

Modelos: kling-o3-std. Animaciones: slide (pose `correr_apagada_dullmagenta_16x9.png`, prompt `slide_directo.txt`). 4 clips por modelo y animación, 720p 16:9, sin audio.

| clip | estado | QA | deriva % | zoom % | borde | pose MAD | loop | US$ | notas |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| kling-o3-std_slide_1.mp4 | ok | warn | 8.6 | 2.4 | 0 | 1.95 | - | 0,34 | fondo poco plano (desvío 8.96): el key va a necesitar más tolerancia |
| kling-o3-std_slide_2.mp4 | ok | warn | 22.3 | 6.4 | 0 | 1.95 | - | 0,34 | fondo poco plano (desvío 8.92): el key va a necesitar más tolerancia |
| kling-o3-std_slide_3.mp4 | ok | warn | 34.6 | 12.7 | 0 | 2.04 | - | 0,34 | fondo poco plano (desvío 8.42): el key va a necesitar más tolerancia |
| kling-o3-std_slide_4.mp4 | ok | warn | 16.1 | 6.4 | 0 | 1.98 | - | 0,34 | fondo poco plano (desvío 8.81): el key va a necesitar más tolerancia |

| modelo | bajados | bloqueados | errores | QA ok/warn/fail | pose MAD (mediana) | mejor loop | US$ |
|---|---:|---:|---:|---|---:|---:|---:|
| kling-o3-std | 4 | 0 | 0 | 0/4/0 | 1.98 | - | 1,34 |

Gastado (estimado, a precio de lista): US$ 1,34.
