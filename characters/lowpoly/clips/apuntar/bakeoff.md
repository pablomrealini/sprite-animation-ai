# Bake-off (2026-10-17)

Modelos: kling-o3-std. Animaciones: apuntar (pose `perfil_apagada_dullmagenta_16x9.png`, prompt `apuntar.txt`), salto_apuntando (pose `salto_apagada_dullmagenta_16x9.png`, prompt `salto_apuntando.txt`), apuntar_sin_arma (pose `sin_arma_dullmagenta_16x9.png`, prompt `apuntar_sin_arma.txt`), salto_apuntando_sin_arma (pose `sin_arma_salto_dullmagenta_16x9.png`, prompt `salto_apuntando_sin_arma.txt`). 2 clips por modelo y animación, 720p 16:9, sin audio.

| clip | estado | QA | deriva % | zoom % | borde | pose MAD | loop | US$ | notas |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| kling-o3-std_apuntar_1.mp4 | ok | warn | 6.7 | 0.0 | 2 | 1.7 | - | 0,42 | el personaje toca el borde del cuadro en 2 frames (arma o capa cortada); fondo poco plano (desvío 8.24): el key va a necesitar más tolerancia; casi sin movimiento (mediana 0.24): típico de first==last |
| kling-o3-std_apuntar_2.mp4 | ok | warn | 7.4 | 0.4 | 2 | 1.7 | - | 0,42 | el personaje toca el borde del cuadro en 2 frames (arma o capa cortada); fondo poco plano (desvío 8.15): el key va a necesitar más tolerancia; casi sin movimiento (mediana 0.98): típico de first==last |
| kling-o3-std_salto_apuntando_1.mp4 | ok | warn | 17.9 | 0.3 | 2 | 1.74 | - | 0,42 | el personaje toca el borde del cuadro en 2 frames (arma o capa cortada); fondo poco plano (desvío 8.15): el key va a necesitar más tolerancia |
| kling-o3-std_salto_apuntando_2.mp4 | ok | warn | 2.3 | 0.5 | 13 | 1.72 | - | 0,42 | el personaje toca el borde del cuadro en 13 frames (arma o capa cortada); fondo poco plano (desvío 8.18): el key va a necesitar más tolerancia |
| kling-o3-std_apuntar_sin_arma_1.mp4 | ok | warn | 0.1 | 0.3 | 0 | 1.61 | - | 0,42 | fondo poco plano (desvío 8.63): el key va a necesitar más tolerancia |
| kling-o3-std_apuntar_sin_arma_2.mp4 | ok | warn | 1.4 | 1.1 | 0 | 1.58 | - | 0,42 | fondo poco plano (desvío 7.98): el key va a necesitar más tolerancia; casi sin movimiento (mediana 0.52): típico de first==last |
| kling-o3-std_salto_apuntando_sin_arma_1.mp4 | ok | warn | 7.7 | 0.5 | 0 | 1.63 | - | 0,42 | fondo poco plano (desvío 8.93): el key va a necesitar más tolerancia |
| kling-o3-std_salto_apuntando_sin_arma_2.mp4 | ok | warn | 11.7 | 0.0 | 0 | 1.55 | - | 0,42 | fondo poco plano (desvío 8.65): el key va a necesitar más tolerancia |

| modelo | bajados | bloqueados | errores | QA ok/warn/fail | pose MAD (mediana) | mejor loop | US$ |
|---|---:|---:|---:|---|---:|---:|---:|
| kling-o3-std | 8 | 0 | 0 | 0/8/0 | 1.7 | - | 3,36 |

Gastado (estimado, a precio de lista): US$ 3,36.
