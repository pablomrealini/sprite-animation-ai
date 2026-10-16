# Bake-off (2026-10-16)

Modelos: seedance-2.0. Animaciones: throw (pose `ranger_master_dullmagenta_16x9.png`, prompt `throw.txt`). 2 clips por modelo y animación, 720p 16:9, sin audio.

| clip | estado | QA | deriva % | zoom % | borde | pose MAD | loop | US$ | notas |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| seedance-2.0_throw_1.mp4 | ok | fail | 3.2 | 0.5 | 2 | 56.42 | - | 1,52 | el frame 0 no respeta la pose (MAD 56.42): el modelo re-renderizó; el personaje toca el borde del cuadro en 2 frames (arma o capa cortada); fondo poco plano (desvío 8.32): el key va a necesitar más tolerancia; el color del fondo cambia durante el clip (9.0/255); casi sin movimiento (mediana 0.19): típico de first==last |
| seedance-2.0_throw_2.mp4 | ok | fail | 5.9 | 2.4 | 1 | 56.31 | - | 1,52 | el frame 0 no respeta la pose (MAD 56.31): el modelo re-renderizó; el personaje toca el borde del cuadro en 1 frames (arma o capa cortada); fondo poco plano (desvío 8.71): el key va a necesitar más tolerancia; el color del fondo cambia durante el clip (10.0/255); posible corte de escena en los frames [49]; casi sin movimiento (mediana 0.23): típico de first==last |

| modelo | bajados | bloqueados | errores | QA ok/warn/fail | pose MAD (mediana) | mejor loop | US$ |
|---|---:|---:|---:|---|---:|---:|---:|
| seedance-2.0 | 2 | 0 | 0 | 0/0/2 | 56.42 | - | 3,03 |

Gastado (estimado, a precio de lista): US$ 3,03.
