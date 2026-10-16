# Bake-off (2026-10-16)

Modelos: seedance-2.0. Animaciones: run_legs (pose `ranger_master_magenta_16x9.png`, prompt `run_legs.txt`). 1 clips por modelo y animación, 720p 16:9, sin audio.

| clip | estado | QA | deriva % | zoom % | borde | pose MAD | loop | US$ | notas |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| seedance-2.0_run_legs_1.mp4 | ok | fail | 0.5 | 0.6 | 0 | 90.18 | 0.09 (buena) | 1,52 | el frame 0 no respeta la pose (MAD 90.18): el modelo re-renderizó |

| modelo | bajados | bloqueados | errores | QA ok/warn/fail | pose MAD (mediana) | mejor loop | US$ |
|---|---:|---:|---:|---|---:|---:|---:|
| seedance-2.0 | 1 | 0 | 0 | 0/0/1 | 90.18 | 0.09 | 1,52 |

Gastado (estimado, a precio de lista): US$ 1,52.
