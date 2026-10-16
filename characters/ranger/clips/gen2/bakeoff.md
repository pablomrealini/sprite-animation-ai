# Bake-off (2026-10-16)

Modelos: seedance-2.0. Animaciones: idle_breath (pose `ranger_master_dullmagenta_16x9.png`, prompt `idle_breath.txt`), double_jump (pose `ranger_jump_dullmagenta_16x9.png`, prompt `double_jump.txt`). 2 clips por modelo y animación, 720p 16:9, sin audio.

| clip | estado | QA | deriva % | zoom % | borde | pose MAD | loop | US$ | notas |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| seedance-2.0_idle_breath_1.mp4 | ok | warn | 0.1 | 0.0 | 0 | 19.85 | 0.433 (buena) | 1,52 | el frame 0 se aparta de la pose (MAD 19.85); fondo poco plano (desvío 7.56): el key va a necesitar más tolerancia |
| seedance-2.0_idle_breath_2.mp4 | ok | warn | 0.5 | 0.5 | 0 | 20.76 | 1.286 (costura visible) | 1,52 | el frame 0 se aparta de la pose (MAD 20.76); fondo poco plano (desvío 7.91): el key va a necesitar más tolerancia |
| seedance-2.0_double_jump_1.mp4 | ok | warn | 18.6 | 2.5 | 0 | 24.18 | - | 1,52 | el frame 0 se aparta de la pose (MAD 24.18); fondo poco plano (desvío 8.08): el key va a necesitar más tolerancia |
| seedance-2.0_double_jump_2.mp4 | ok | warn | 22.6 | 8.9 | 0 | 24.07 | - | 1,52 | el frame 0 se aparta de la pose (MAD 24.07); fondo poco plano (desvío 8.04): el key va a necesitar más tolerancia |

| modelo | bajados | bloqueados | errores | QA ok/warn/fail | pose MAD (mediana) | mejor loop | US$ |
|---|---:|---:|---:|---|---:|---:|---:|
| seedance-2.0 | 4 | 0 | 0 | 0/4/0 | 24.07 | 0.433 | 6,07 |

Gastado (estimado, a precio de lista): US$ 6,07.
