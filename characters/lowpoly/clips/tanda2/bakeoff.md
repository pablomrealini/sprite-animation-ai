# Bake-off (2026-10-17)

Modelos: kling-o3-std. Animaciones: shoot2h (pose `perfil_apagada_dullmagenta_16x9.png`, prompt `apuntar_dos_manos.txt`), crouch (pose `perfil_apagada_dullmagenta_16x9.png`, prompt `agacharse_apuntando.txt`), jump_shoot (pose `salto_apuntando_apagada_dullmagenta_16x9.png`, prompt `salto_apuntando_quieto.txt`). 2 clips por modelo y animación, 720p 16:9, sin audio.

| clip | estado | QA | deriva % | zoom % | borde | pose MAD | loop | US$ | notas |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| kling-o3-std_shoot2h_1.mp4 | ok | warn | 0.4 | 0.1 | 0 | 1.71 | - | 0,42 | fondo poco plano (desvío 8.65): el key va a necesitar más tolerancia; casi sin movimiento (mediana 0.55): típico de first==last |
| kling-o3-std_shoot2h_2.mp4 | ok | warn | 3.5 | 1.1 | 0 | 1.7 | - | 0,42 | fondo poco plano (desvío 8.75): el key va a necesitar más tolerancia |
| kling-o3-std_crouch_1.mp4 | ok | warn | 4.4 | 0.3 | 0 | 1.71 | - | 0,42 | fondo poco plano (desvío 8.74): el key va a necesitar más tolerancia |
| kling-o3-std_crouch_2.mp4 | ok | warn | 2.9 | 1.4 | 0 | 1.68 | - | 0,42 | fondo poco plano (desvío 8.4): el key va a necesitar más tolerancia |
| kling-o3-std_jump_shoot_1.mp4 | ok | warn | 17.3 | 1.0 | 0 | 1.85 | - | 0,42 | fondo poco plano (desvío 8.67): el key va a necesitar más tolerancia |
| kling-o3-std_jump_shoot_2.mp4 | ok | warn | 15.3 | 0.3 | 0 | 1.82 | - | 0,42 | fondo poco plano (desvío 8.64): el key va a necesitar más tolerancia |

| modelo | bajados | bloqueados | errores | QA ok/warn/fail | pose MAD (mediana) | mejor loop | US$ |
|---|---:|---:|---:|---|---:|---:|---:|
| kling-o3-std | 6 | 0 | 0 | 0/6/0 | 1.71 | - | 2,52 |

Gastado (estimado, a precio de lista): US$ 2,52.
