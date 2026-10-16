# Bake-off (2026-10-16)

Modelos: seedance-2.0. Animaciones: run_legs (pose `ranger_master_magenta_16x9.png`, prompt `run_legs.txt`), idle_breath (pose `ranger_master_magenta_16x9.png`, prompt `idle_breath.txt`), double_jump (pose `ranger_jump_magenta_16x9.png`, prompt `double_jump.txt`). 2 clips por modelo y animación, 720p 16:9, sin audio.

| clip | estado | QA | deriva % | zoom % | borde | pose MAD | loop | US$ | notas |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| seedance-2.0_run_legs_1.mp4 | ok | fail | 0.2 | 0.4 | 0 | 83.24 | 0.165 (buena) | 1,52 | el frame 0 no respeta la pose (MAD 83.24): el modelo re-renderizó |
| seedance-2.0_run_legs_2.mp4 | ok | fail | 0.3 | 0.2 | 0 | 87.5 | 0.094 (buena) | 1,52 | el frame 0 no respeta la pose (MAD 87.5): el modelo re-renderizó |
| seedance-2.0_idle_breath_1.mp4 | ok | warn | 0.3 | 0.2 | 0 | 25.82 | 0.383 (buena) | 1,52 | el frame 0 se aparta de la pose (MAD 25.82) |
| seedance-2.0_idle_breath_2.mp4 | ok | warn | 0.6 | 0.0 | 0 | 25.94 | 0.59 (buena) | 1,52 | el frame 0 se aparta de la pose (MAD 25.94) |
| seedance-2.0_double_jump_1.mp4 | ok | fail | 27.8 | 6.5 | 0 | 58.64 | - | 1,52 | el frame 0 no respeta la pose (MAD 58.64): el modelo re-renderizó |
| seedance-2.0_double_jump_2.mp4 | ok | warn | 17.4 | 1.6 | 0 | 29.14 | - | 1,52 | el frame 0 se aparta de la pose (MAD 29.14) |

| modelo | bajados | bloqueados | errores | QA ok/warn/fail | pose MAD (mediana) | mejor loop | US$ |
|---|---:|---:|---:|---|---:|---:|---:|
| seedance-2.0 | 6 | 0 | 0 | 0/3/3 | 58.64 | 0.094 | 9,10 |

Gastado (estimado, a precio de lista): US$ 9,10.
