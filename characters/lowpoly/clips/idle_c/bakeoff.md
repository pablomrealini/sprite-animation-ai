# Bake-off (2026-10-17)

Modelos: minimax-h3-max, kling-o3-std. Animaciones: idle_c (pose `sin_arma_dullmagenta_16x9.png`, prompt `idle_c_h3max.txt`). 2 clips por modelo y animación, 720p 16:9, sin audio.

| clip | estado | QA | deriva % | zoom % | borde | pose MAD | loop | US$ | notas |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| minimax-h3-max_idle_c_1.mp4 | ok | fail | 0.5 | 0.5 | 0 | 9.0 | 0.765 (aceptable) | 0,40 | el fondo #ACB1BD no es verde ni magenta: uso key por distancia en modo connected; funciona si el personaje tiene contorno y el fondo es plano; el color del fondo cambia durante el clip (124.0/255); posible corte de escena en los frames [2, 3, 4, 5, 120, 121, 122] |
| minimax-h3-max_idle_c_2.mp4 | ok | fail | 1.8 | 3.8 | 57 | 7.98 | 1.29 (costura visible) | 0,40 | el fondo #3D3B49 no es verde ni magenta: uso key por distancia en modo connected; funciona si el personaje tiene contorno y el fondo es plano; el personaje toca el borde del cuadro en 57 frames (arma o capa cortada); el color del fondo cambia durante el clip (140.0/255); posible corte de escena en los frames [9, 114, 115, 116] |
| kling-o3-std_idle_c_1.mp4 | ok | warn | 4.5 | 0.2 | 0 | 1.69 | 1.096 (costura visible) | 0,42 | deriva/paneo o el personaje se traslada: 4.5% del alto (la alineación saca la deriva lineal); fondo poco plano (desvío 7.77): el key va a necesitar más tolerancia; el color del fondo cambia durante el clip (10.0/255) |
| kling-o3-std_idle_c_2.mp4 | ok | warn | 3.0 | 4.2 | 0 | 1.7 | 0.765 (aceptable) | 0,42 | fondo poco plano (desvío 7.71): el key va a necesitar más tolerancia; el color del fondo cambia durante el clip (10.0/255) |

| modelo | bajados | bloqueados | errores | QA ok/warn/fail | pose MAD (mediana) | mejor loop | US$ |
|---|---:|---:|---:|---|---:|---:|---:|
| minimax-h3-max | 2 | 0 | 0 | 0/0/2 | 9.0 | 0.765 | 0,80 |
| kling-o3-std | 2 | 0 | 0 | 0/2/0 | 1.7 | 0.765 | 0,84 |

Gastado (estimado, a precio de lista): US$ 1,64.
