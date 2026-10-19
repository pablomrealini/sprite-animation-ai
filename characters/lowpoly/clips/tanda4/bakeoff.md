# Bake-off (2026-10-18)

Modelos: kling-o3-std. Animaciones: slide_in (pose `correr_apagada_dullmagenta_16x9.png`, prompt `slide_in.txt`), slide_out (pose `deslizarse_dullmagenta_16x9.png`, prompt `slide_out.txt`). 2 clips por modelo y animación, 720p 16:9, sin audio.

| clip | estado | QA | deriva % | zoom % | borde | pose MAD | loop | US$ | notas |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| kling-o3-std_slide_in_1.mp4 | ok | warn | 30.5 | 17.0 | 0 | 2.03 | - | 0,25 | fondo poco plano (desvío 8.89): el key va a necesitar más tolerancia |
| kling-o3-std_slide_in_2.mp4 | ok | warn | 30.2 | 18.6 | 0 | 2.07 | - | 0,25 | fondo poco plano (desvío 8.7): el key va a necesitar más tolerancia |
| kling-o3-std_slide_out_1.mp4 | ok | warn | 25.4 | 23.7 | 0 | 1.83 | - | 0,25 | fondo poco plano (desvío 8.73): el key va a necesitar más tolerancia |
| kling-o3-std_slide_out_2.mp4 | ok | warn | 49.4 | 24.5 | 0 | 1.96 | - | 0,25 | fondo poco plano (desvío 9.0): el key va a necesitar más tolerancia |

| modelo | bajados | bloqueados | errores | QA ok/warn/fail | pose MAD (mediana) | mejor loop | US$ |
|---|---:|---:|---:|---|---:|---:|---:|
| kling-o3-std | 4 | 0 | 0 | 0/4/0 | 2.03 | - | 1,01 |

Gastado (estimado, a precio de lista): US$ 1,01.
