# Bake-off (2026-10-17)

Modelos: kling-o3-std. Animaciones: shoot (pose `perfil_dullmagenta_16x9.png`, prompt `shoot.txt`), shoot2h (pose `perfil_dullmagenta_16x9.png`, prompt `shoot2h.txt`), crouch_shoot (pose `perfil_dullmagenta_16x9.png`, prompt `crouch_shoot.txt`), throw (pose `perfil_dullmagenta_16x9.png`, prompt `throw.txt`), jump (pose `salto_dullmagenta_16x9.png`, prompt `jump.txt`), jump_shoot (pose `salto_dullmagenta_16x9.png`, prompt `jump_shoot.txt`), double_jump (pose `salto_dullmagenta_16x9.png`, prompt `double_jump.txt`), hang (pose `salto_dullmagenta_16x9.png`, prompt `hang.txt`). 2 clips por modelo y animación, 720p 16:9, sin audio.

| clip | estado | QA | deriva % | zoom % | borde | pose MAD | loop | US$ | notas |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| kling-o3-std_shoot_1.mp4 | ok | warn | 5.3 | 0.2 | 61 | 1.81 | - | 0,42 | el personaje toca el borde del cuadro en 61 frames (arma o capa cortada); fondo poco plano (desvío 8.19): el key va a necesitar más tolerancia |
| kling-o3-std_shoot_2.mp4 | ok | warn | 3.8 | 0.1 | 0 | 1.82 | - | 0,42 | fondo poco plano (desvío 10.27): el key va a necesitar más tolerancia |
| kling-o3-std_shoot2h_1.mp4 | ok | warn | 25.5 | 0.3 | 0 | 1.8 | - | 0,42 | fondo poco plano (desvío 8.0): el key va a necesitar más tolerancia |
| kling-o3-std_shoot2h_2.mp4 | ok | warn | 7.3 | 0.0 | 35 | 1.77 | - | 0,42 | el personaje toca el borde del cuadro en 35 frames (arma o capa cortada); fondo poco plano (desvío 11.35): el key va a necesitar más tolerancia |
| kling-o3-std_crouch_shoot_1.mp4 | ok | warn | 6.9 | 0.2 | 0 | 1.82 | - | 0,42 | fondo poco plano (desvío 8.93): el key va a necesitar más tolerancia |
| kling-o3-std_crouch_shoot_2.mp4 | ok | warn | 9.4 | 1.2 | 65 | 1.8 | - | 0,42 | el personaje toca el borde del cuadro en 65 frames (arma o capa cortada); fondo poco plano (desvío 10.21): el key va a necesitar más tolerancia |
| kling-o3-std_throw_1.mp4 | ok | warn | 19.6 | 5.8 | 0 | 1.78 | - | 0,42 | fondo poco plano (desvío 9.49): el key va a necesitar más tolerancia |
| kling-o3-std_throw_2.mp4 | ok | warn | 17.3 | 2.9 | 2 | 1.82 | - | 0,42 | el personaje toca el borde del cuadro en 2 frames (arma o capa cortada); fondo poco plano (desvío 8.72): el key va a necesitar más tolerancia |
| kling-o3-std_jump_1.mp4 | ok | warn | 9.2 | 1.8 | 0 | 1.89 | - | 0,42 | fondo poco plano (desvío 8.14): el key va a necesitar más tolerancia |
| kling-o3-std_jump_2.mp4 | ok | warn | 50.7 | 1.1 | 5 | 1.84 | - | 0,42 | el personaje toca el borde del cuadro en 5 frames (arma o capa cortada); fondo poco plano (desvío 8.32): el key va a necesitar más tolerancia |
| kling-o3-std_jump_shoot_1.mp4 | ok | warn | 12.3 | 1.3 | 3 | 1.82 | - | 0,42 | el personaje toca el borde del cuadro en 3 frames (arma o capa cortada); fondo poco plano (desvío 8.24): el key va a necesitar más tolerancia |
| kling-o3-std_jump_shoot_2.mp4 | ok | warn | 11.4 | 0.1 | 10 | 1.9 | - | 0,42 | el personaje toca el borde del cuadro en 10 frames (arma o capa cortada); fondo poco plano (desvío 8.25): el key va a necesitar más tolerancia |
| kling-o3-std_double_jump_1.mp4 | ok | warn | 12.7 | 1.3 | 2 | 1.81 | - | 0,42 | el personaje toca el borde del cuadro en 2 frames (arma o capa cortada); fondo poco plano (desvío 7.91): el key va a necesitar más tolerancia |
| kling-o3-std_double_jump_2.mp4 | ok | warn | 27.5 | 5.2 | 10 | 1.8 | - | 0,42 | el personaje toca el borde del cuadro en 10 frames (arma o capa cortada); fondo poco plano (desvío 7.92): el key va a necesitar más tolerancia |
| kling-o3-std_hang_1.mp4 | ok | warn | 10.1 | 34.8 | 0 | 2.01 | - | 0,42 | fondo poco plano (desvío 8.89): el key va a necesitar más tolerancia |
| kling-o3-std_hang_2.mp4 | ok | warn | 21.4 | 21.0 | 0 | 1.94 | - | 0,42 | fondo poco plano (desvío 9.68): el key va a necesitar más tolerancia |

| modelo | bajados | bloqueados | errores | QA ok/warn/fail | pose MAD (mediana) | mejor loop | US$ |
|---|---:|---:|---:|---|---:|---:|---:|
| kling-o3-std | 16 | 0 | 0 | 0/16/0 | 1.82 | - | 6,72 |

Gastado (estimado, a precio de lista): US$ 6,72.
