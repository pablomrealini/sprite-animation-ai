# Bake-off (2026-10-17)

Modelos: seedance-2.0, minimax-h3-max, kling-o3-std. Animaciones: idle_a (pose `perfil_dullmagenta_16x9.png`, prompt `idle_a.txt`), idle_b (pose `perfil_dullmagenta_16x9.png`, prompt `idle_b_h3max.txt`), idle_b_tq (pose `tq_dullmagenta_16x9.png`, prompt `idle_b_tq_h3max.txt`). 2 clips por modelo y animación, 720p 16:9, sin audio.

| clip | estado | QA | deriva % | zoom % | borde | pose MAD | loop | US$ | notas |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| seedance-2.0_idle_a_1.mp4 | ok | fail | 0.2 | 0.4 | 0 | 44.8 | 1.982 (costura visible) | 1,52 | el frame 0 no respeta la pose (MAD 44.8): el modelo re-renderizó; fondo poco plano (desvío 8.7): el key va a necesitar más tolerancia |
| seedance-2.0_idle_a_2.mp4 | ok | fail | 0.3 | 0.0 | 0 | 45.13 | 0.511 (buena) | 1,52 | el frame 0 no respeta la pose (MAD 45.13): el modelo re-renderizó; fondo poco plano (desvío 8.69): el key va a necesitar más tolerancia |
| minimax-h3-max_idle_a_1.mp4 | ok | fail | 36.5 | 57.3 | 30 | 8.19 | 0.172 (buena) | 0,26 | deriva/paneo o el personaje se traslada: 36.5% del alto; zoom o cambio de escala: 57.3% del alto; el personaje toca el borde del cuadro en 30 frames (arma o capa cortada); fondo poco plano (desvío 7.61): el key va a necesitar más tolerancia; el color del fondo cambia durante el clip (158.0/255); posible corte de escena en los frames [64, 94] |
| minimax-h3-max_idle_a_2.mp4 | ok | warn | 3.0 | 0.3 | 0 | 8.3 | 0.527 (buena) | 0,26 | fondo poco plano (desvío 7.65): el key va a necesitar más tolerancia |
| minimax-h3-max_idle_b_1.mp4 | ok | fail | 0.3 | 0.4 | 0 | 9.44 | 1.151 (costura visible) | 0,44 | el fondo #B0B4BF no es verde ni magenta: uso key por distancia en modo connected; funciona si el personaje tiene contorno y el fondo es plano; el color del fondo cambia durante el clip (129.0/255); posible corte de escena en los frames [1, 2, 3, 122] |
| minimax-h3-max_idle_b_2.mp4 | ok | fail | 16.8 | 19.0 | 79 | 9.89 | 0.798 (aceptable) | 0,44 | el fondo #B0B3BE no es verde ni magenta: uso key por distancia en modo connected; funciona si el personaje tiene contorno y el fondo es plano; deriva/paneo o el personaje se traslada: 16.8% del alto (la alineación saca la deriva lineal); zoom o cambio de escala: 19.0% del alto; el personaje toca el borde del cuadro en 79 frames (arma o capa cortada); el color del fondo cambia durante el clip (121.0/255); posible corte de escena en los frames [2, 3, 4, 5, 9, 37, 86, 116] |
| minimax-h3-max_idle_b_tq_1.mp4 | ok | fail | 0.9 | 1.1 | 0 | 9.5 | 0.924 (aceptable) | 0,44 | el fondo #B0B4BF no es verde ni magenta: uso key por distancia en modo connected; funciona si el personaje tiene contorno y el fondo es plano; el color del fondo cambia durante el clip (129.0/255); posible corte de escena en los frames [1, 2, 3, 122] |
| minimax-h3-max_idle_b_tq_2.mp4 | ok | fail | 15.2 | 15.8 | 77 | 9.28 | 0.428 (buena) | 0,44 | el fondo #AFB3BD no es verde ni magenta: uso key por distancia en modo connected; funciona si el personaje tiene contorno y el fondo es plano; deriva/paneo o el personaje se traslada: 15.2% del alto (la alineación saca la deriva lineal); zoom o cambio de escala: 15.8% del alto; el personaje toca el borde del cuadro en 77 frames (arma o capa cortada); el color del fondo cambia durante el clip (122.0/255); posible corte de escena en los frames [6, 37, 111, 112, 113, 114, 115, 116, 117] |
| kling-o3-std_idle_a_1.mp4 | ok | warn | 1.8 | 1.5 | 0 | 1.77 | 1.682 (costura visible) | 0,42 | fondo poco plano (desvío 7.69): el key va a necesitar más tolerancia; casi sin movimiento (mediana 0.76): típico de first==last |
| kling-o3-std_idle_a_2.mp4 | ok | warn | 0.0 | 0.6 | 0 | 1.8 | 0.949 (aceptable) | 0,42 | fondo poco plano (desvío 7.7): el key va a necesitar más tolerancia; casi sin movimiento (mediana 0.58): típico de first==last |
| kling-o3-std_idle_b_1.mp4 | ok | warn | 2.0 | 2.6 | 0 | 1.98 | 0.168 (buena) | 0,42 | el color del fondo cambia durante el clip (10.0/255) |
| kling-o3-std_idle_b_2.mp4 | ok | warn | 0.8 | 1.1 | 0 | 1.86 | 0.158 (buena) | 0,42 | fondo poco plano (desvío 8.15): el key va a necesitar más tolerancia; el color del fondo cambia durante el clip (10.0/255) |

| modelo | bajados | bloqueados | errores | QA ok/warn/fail | pose MAD (mediana) | mejor loop | US$ |
|---|---:|---:|---:|---|---:|---:|---:|
| seedance-2.0 | 2 | 0 | 0 | 0/0/2 | 45.13 | 0.511 | 3,03 |
| minimax-h3-max | 6 | 0 | 0 | 0/1/5 | 9.44 | 0.172 | 2,28 |
| kling-o3-std | 4 | 0 | 0 | 0/4/0 | 1.86 | 0.158 | 1,68 |

Gastado (estimado, a precio de lista): US$ 7,00.
