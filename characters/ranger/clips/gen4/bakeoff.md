# Bake-off (2026-10-16)

Modelos: seedance-2.0. Animaciones: run_legs (pose `ranger_run_chest_dullmagenta_16x9.png`, prompt `run_legs_chest.txt`). 2 clips por modelo y animación, 720p 16:9, sin audio.

| clip | estado | QA | deriva % | zoom % | borde | pose MAD | loop | US$ | notas |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| seedance-2.0_run_legs_1.mp4 | ok | fail | 0.2 | 0.0 | 0 | 64.44 | 0.271 (buena) | 1,52 | el frame 0 no respeta la pose (MAD 64.44): el modelo re-renderizó; fondo poco plano (desvío 8.25): el key va a necesitar más tolerancia |
| seedance-2.0_run_legs_2.mp4 | ok | fail | 0.6 | 0.8 | 0 | 55.73 | 0.335 (buena) | 1,52 | el frame 0 no respeta la pose (MAD 55.73): el modelo re-renderizó; fondo poco plano (desvío 8.24): el key va a necesitar más tolerancia |

| modelo | bajados | bloqueados | errores | QA ok/warn/fail | pose MAD (mediana) | mejor loop | US$ |
|---|---:|---:|---:|---|---:|---:|---:|
| seedance-2.0 | 2 | 0 | 0 | 0/0/2 | 64.44 | 0.271 | 3,03 |

Gastado (estimado, a precio de lista): US$ 3,03.
