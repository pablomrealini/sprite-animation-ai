# Bake-off (2026-10-17)

Modelos: kling-o3-std. Animaciones: correr_a (pose `correr_dullmagenta_16x9.png`, prompt `correr_a.txt`). 2 clips por modelo y animación, 720p 16:9, sin audio.

| clip | estado | QA | deriva % | zoom % | borde | pose MAD | loop | US$ | notas |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| kling-o3-std_correr_a_1.mp4 | ok | warn | 0.5 | 0.0 | 0 | 2.06 | 0.307 (buena) | 0,42 | fondo poco plano (desvío 9.08): el key va a necesitar más tolerancia |
| kling-o3-std_correr_a_2.mp4 | ok | warn | 0.5 | 0.0 | 0 | 2.03 | 0.147 (buena) | 0,42 | fondo poco plano (desvío 9.1): el key va a necesitar más tolerancia |

| modelo | bajados | bloqueados | errores | QA ok/warn/fail | pose MAD (mediana) | mejor loop | US$ |
|---|---:|---:|---:|---|---:|---:|---:|
| kling-o3-std | 2 | 0 | 0 | 0/2/0 | 2.06 | 0.147 | 0,84 |

Gastado (estimado, a precio de lista): US$ 0,84.
