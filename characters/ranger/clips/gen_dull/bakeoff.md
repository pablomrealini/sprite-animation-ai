# Bake-off (2026-10-16)

Modelos: seedance-2.0. Animaciones: idle_breath (pose `ranger_master_dullmagenta_16x9.png`, prompt `idle_breath.txt`). 1 clips por modelo y animación, 720p 16:9, sin audio.

| clip | estado | QA | deriva % | zoom % | borde | pose MAD | loop | US$ | notas |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| seedance-2.0_idle_breath_1.mp4 | ok | warn | 0.2 | 0.3 | 0 | 20.66 | 1.318 (costura visible) | 1,52 | el frame 0 se aparta de la pose (MAD 20.66); fondo poco plano (desvío 7.96): el key va a necesitar más tolerancia; casi sin movimiento (mediana 0.83): típico de first==last |

| modelo | bajados | bloqueados | errores | QA ok/warn/fail | pose MAD (mediana) | mejor loop | US$ |
|---|---:|---:|---:|---|---:|---:|---:|
| seedance-2.0 | 1 | 0 | 0 | 0/1/0 | 20.66 | 1.318 | 1,52 |

Gastado (estimado, a precio de lista): US$ 1,52.
