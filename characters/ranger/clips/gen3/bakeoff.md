# Bake-off (2026-10-16)

Modelos: seedance-2.0. Animaciones: idle_combat (pose `ranger_master_dullmagenta_16x9.png`, prompt `idle_combat.txt`). 2 clips por modelo y animación, 720p 16:9, sin audio.

| clip | estado | QA | deriva % | zoom % | borde | pose MAD | loop | US$ | notas |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| seedance-2.0_idle_combat_1.mp4 | ok | fail | 0.1 | 0.0 | 0 | 55.98 | 0.445 (buena) | 1,52 | el frame 0 no respeta la pose (MAD 55.98): el modelo re-renderizó; fondo poco plano (desvío 7.72): el key va a necesitar más tolerancia |
| seedance-2.0_idle_combat_2.mp4 | ok | fail | 0.2 | 0.1 | 0 | 53.76 | 0.285 (buena) | 1,52 | el frame 0 no respeta la pose (MAD 53.76): el modelo re-renderizó; fondo poco plano (desvío 7.67): el key va a necesitar más tolerancia |

| modelo | bajados | bloqueados | errores | QA ok/warn/fail | pose MAD (mediana) | mejor loop | US$ |
|---|---:|---:|---:|---|---:|---:|---:|
| seedance-2.0 | 2 | 0 | 0 | 0/0/2 | 55.98 | 0.285 | 3,03 |

Gastado (estimado, a precio de lista): US$ 3,03.
