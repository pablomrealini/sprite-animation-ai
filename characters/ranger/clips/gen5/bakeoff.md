# Bake-off (2026-10-16)

Modelos: seedance-2.0. Animaciones: climb (pose `ranger_climb_first_dullmagenta_16x9.png`, prompt `climb.txt`), hang_two (pose `ranger_climb_first_dullmagenta_16x9.png`, prompt `hang_two.txt`). 2 clips por modelo y animación, 720p 16:9, sin audio.

| clip | estado | QA | deriva % | zoom % | borde | pose MAD | loop | US$ | notas |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| seedance-2.0_climb_1.mp4 | ok | fail | 123.0 | 3.3 | 0 | 66.12 | - | 1,21 | el frame 0 no respeta la pose (MAD 66.12): el modelo re-renderizó; casi sin movimiento (mediana 0.26): típico de first==last |
| seedance-2.0_climb_2.mp4 | ok | fail | 146.2 | 5.8 | 0 | 65.65 | - | 1,21 | el frame 0 no respeta la pose (MAD 65.65): el modelo re-renderizó; el color del fondo cambia durante el clip (12.0/255); casi sin movimiento (mediana 0.30): típico de first==last |
| seedance-2.0_hang_two_1.mp4 | ok | fail | 0.1 | 1.1 | 0 | 65.43 | 1.614 (costura visible) | 1,21 | el frame 0 no respeta la pose (MAD 65.43): el modelo re-renderizó; el color del fondo cambia durante el clip (15.0/255); casi sin movimiento (mediana 0.29): típico de first==last |
| seedance-2.0_hang_two_2.mp4 | ok | fail | 1.2 | 1.1 | 0 | 65.69 | 0.912 (aceptable) | 1,21 | el frame 0 no respeta la pose (MAD 65.69): el modelo re-renderizó; casi sin movimiento (mediana 0.37): típico de first==last |

| modelo | bajados | bloqueados | errores | QA ok/warn/fail | pose MAD (mediana) | mejor loop | US$ |
|---|---:|---:|---:|---|---:|---:|---:|
| seedance-2.0 | 4 | 0 | 0 | 0/0/4 | 65.69 | 0.912 | 4,85 |

Gastado (estimado, a precio de lista): US$ 4,85.
