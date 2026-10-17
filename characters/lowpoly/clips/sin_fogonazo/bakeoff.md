# Bake-off (2026-10-17)

Modelos: kling-o3-std. Animaciones: shoot_p (pose `perfil_dullmagenta_16x9.png`, prompt `shoot_sin_fogonazo.txt`), shoot_pd (pose `perfil_apagada_dullmagenta_16x9.png`, prompt `shoot_sin_fogonazo.txt`), jump_shoot_p (pose `salto_dullmagenta_16x9.png`, prompt `jump_shoot_sin_fogonazo.txt`), jump_shoot_pd (pose `salto_apagada_dullmagenta_16x9.png`, prompt `jump_shoot_sin_fogonazo.txt`). 2 clips por modelo y animación, 720p 16:9, sin audio.

| clip | estado | QA | deriva % | zoom % | borde | pose MAD | loop | US$ | notas |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| kling-o3-std_shoot_p_1.mp4 | ok | warn | 20.1 | 0.2 | 0 | 1.8 | - | 0,42 | fondo poco plano (desvío 8.2): el key va a necesitar más tolerancia |
| kling-o3-std_shoot_p_2.mp4 | ok | warn | 11.6 | 0.0 | 0 | 1.8 | - | 0,42 | fondo poco plano (desvío 9.33): el key va a necesitar más tolerancia |
| kling-o3-std_shoot_pd_1.mp4 | ok | warn | 2.7 | 0.2 | 0 | 1.69 | - | 0,42 | fondo poco plano (desvío 8.47): el key va a necesitar más tolerancia |
| kling-o3-std_shoot_pd_2.mp4 | ok | warn | 15.2 | 3.0 | 0 | 1.68 | - | 0,42 | fondo poco plano (desvío 9.31): el key va a necesitar más tolerancia |
| kling-o3-std_jump_shoot_p_1.mp4 | ok | warn | 17.8 | 0.8 | 29 | 1.85 | - | 0,42 | el personaje toca el borde del cuadro en 29 frames (arma o capa cortada); fondo poco plano (desvío 8.46): el key va a necesitar más tolerancia |
| kling-o3-std_jump_shoot_p_2.mp4 | ok | warn | 32.7 | 4.2 | 28 | 1.91 | - | 0,42 | el personaje toca el borde del cuadro en 28 frames (arma o capa cortada); fondo poco plano (desvío 9.16): el key va a necesitar más tolerancia |
| kling-o3-std_jump_shoot_pd_1.mp4 | ok | warn | 15.8 | 3.6 | 0 | 1.79 | - | 0,42 | fondo poco plano (desvío 8.36): el key va a necesitar más tolerancia |
| kling-o3-std_jump_shoot_pd_2.mp4 | ok | warn | 18.2 | 0.4 | 0 | 1.72 | - | 0,42 | fondo poco plano (desvío 9.03): el key va a necesitar más tolerancia |

| modelo | bajados | bloqueados | errores | QA ok/warn/fail | pose MAD (mediana) | mejor loop | US$ |
|---|---:|---:|---:|---|---:|---:|---:|
| kling-o3-std | 8 | 0 | 0 | 0/8/0 | 1.8 | - | 3,36 |

Gastado (estimado, a precio de lista): US$ 3,36.
