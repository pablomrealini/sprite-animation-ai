# Bake-off (2026-10-17)

Modelos: kling-o3-std. Animaciones: climb (pose `climb_first_dullmagenta_16x9.png`, prompt `climb.txt`), hang_two (pose `climb_first_dullmagenta_16x9.png`, prompt `hang_two.txt`). 2 clips por modelo y animación, 720p 16:9, sin audio.

| clip | estado | QA | deriva % | zoom % | borde | pose MAD | loop | US$ | notas |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| kling-o3-std_climb_1.mp4 | ok | ok | 163.4 | 61.1 | 0 | 2.44 | - | 0,34 |  |
| kling-o3-std_climb_2.mp4 | ok | ok | 231.3 | 53.6 | 0 | 2.37 | - | 0,34 |  |
| kling-o3-std_hang_two_1.mp4 | ok | warn | 5.5 | 2.6 | 0 | 2.4 | 0.278 (buena) | 0,34 | deriva/paneo o el personaje se traslada: 5.5% del alto (la alineación saca la deriva lineal) |
| kling-o3-std_hang_two_2.mp4 | ok | ok | 0.2 | 0.0 | 0 | 2.43 | 1.136 (costura visible) | 0,34 |  |

| modelo | bajados | bloqueados | errores | QA ok/warn/fail | pose MAD (mediana) | mejor loop | US$ |
|---|---:|---:|---:|---|---:|---:|---:|
| kling-o3-std | 4 | 0 | 0 | 3/1/0 | 2.43 | 0.278 | 1,34 |

Gastado (estimado, a precio de lista): US$ 1,34.
