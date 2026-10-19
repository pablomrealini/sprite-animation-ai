# Bake-off (2026-10-18)

Modelos: kling-o3-std. Animaciones: throw_cerca (pose `con_granada_cerca_dullmagenta_16x9.png`, prompt `tirar_granada_cerca.txt`). 2 clips por modelo y animación, 720p 16:9, sin audio.

| clip | estado | QA | deriva % | zoom % | borde | pose MAD | loop | US$ | notas |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| kling-o3-std_throw_cerca_1.mp4 | ok | warn | 16.3 | 0.7 | 0 | 1.88 | - | 0,34 | fondo poco plano (desvío 9.28): el key va a necesitar más tolerancia |
| kling-o3-std_throw_cerca_2.mp4 | ok | warn | 14.9 | 1.4 | 3 | 1.86 | - | 0,34 | el personaje toca el borde del cuadro en 3 frames (arma o capa cortada); fondo poco plano (desvío 9.43): el key va a necesitar más tolerancia |

| modelo | bajados | bloqueados | errores | QA ok/warn/fail | pose MAD (mediana) | mejor loop | US$ |
|---|---:|---:|---:|---|---:|---:|---:|
| kling-o3-std | 2 | 0 | 0 | 0/2/0 | 1.88 | - | 0,67 |

Gastado (estimado, a precio de lista): US$ 0,67.
