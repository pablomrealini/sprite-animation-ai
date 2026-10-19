# Medidas del kit low-poly de escenario (A1) y de los fondos de 2496 × 1404 (A2)

Editor de niveles para Arte, 2026-10-18. Pablo decidió que las arenas grandes se arman con un kit de piezas: un fondo
sin pasarelas y piezas sueltas con alfa que se ponen, se espejan y se estiran en el editor. Todo en **px del juego**.

## Lo que vale para todas las piezas

- **Escala: 1 px del archivo final = 1 px del juego.** Se pueden dibujar más grandes en la hoja (a 2K entran ~3×) y
  achicar a la medida; en la entrega va la medida de cada pieza en px del juego (ancho o alto, como los `*_ART`).
- **Contra qué se miden.** El personaje parado mide ~105 px de alto y ~32 de ancho (su caja). El salto simple sube
  192 px y el doble ~333–347; los pisos van cada ~200 px. Una pasarela de 400 px son ~12 personajes de ancho.
- **Estilo**: el de la Refinería low-poly. Referencias: `prototypes/arena/arenas/refineria_lowpoly/*.png` (las
  pasarelas y la flotante) y `refineria_lowpoly/fondo.webp`. Vista 3/4 de frente: se ve la cara de arriba (clara) y la
  de adelante (media); los costados sólo en las puntas. Luz de arriba a la izquierda, contorno oscuro, gris acero con
  tacos rojos, franjas amarillas y negras y luces cian.
- **La línea de los pies** es el borde de atrás de la cara de arriba: la primera fila clara bajo el contorno oscuro.
  Ahí se para el personaje. Tiene que ser **una fila recta y horizontal** a lo ancho de toda la pieza, y la misma fila
  en todas las piezas de un mismo juego de tramos.
- **Cara de arriba: 18 px de profundidad** (de la línea de los pies hacia abajo), clara y plana. Por encima de la
  línea de los pies puede haber hasta 16 px de cosas de atrás (los tacos rojos, el contorno, un borde de baranda),
  nada que tape los pies ni que parezca otro piso.
- **Las patas se estiran a lo alto**: el editor alarga una franja de filas (no la repite). En esa franja, **sólo
  cosas verticales** (pilares, caños, cables, luces largas): las diagonales y las cruces se deforman al estirar, así
  que van arriba de la franja (pegadas a la losa) o en los pies.
- Fondo transparente (alfa nativo) y **una sola mancha por pieza**. Sin sombra en el piso.
- Las medidas de abajo son las que busco; ±4 px no importa: al recibirlas mido cada pieza y escribo su definición
  (línea de los pies, franja de patas, colisión) en el JSON de la arena.

## A1. Las piezas

Cuatro hojas, cada una con sus piezas a la misma escala (en orden de lectura, separadas, sin tocarse ni tocar el
borde).

### Hoja 1: pasarela en tramos

Una pasarela se arma con **punta izquierda + uno o más medios + punta derecha**. Las cuatro piezas miden **200 px de
alto** y tienen las mismas filas:

| Filas (desde arriba) | Qué es |
|---|---|
| 0 – 16 | lo de atrás que asoma (tacos rojos, contorno) |
| **16** | **línea de los pies** |
| 16 – 34 | cara de arriba (18 px), clara |
| 34 – 64 | cara de adelante de la losa (30 px): rebajes, franjas, luces |
| 64 – 72 | sombra de abajo de la losa |
| **72 – 172** | **franja de patas** (100 px, se estira): sólo pilares verticales |
| 172 – 200 | pies (28 px): zapatas que apoyan, no se estiran |

| Pieza | Ancho | Qué lleva |
|---|---|---|
| `pasarela_punta_izq` | 80 | el remate de la losa con un taco rojo y un pilar debajo del taco |
| `pasarela_medio_a` | 256 | taco rojo en el centro y un pilar debajo |
| `pasarela_medio_b` | 256 | sin pilar: una franja amarilla y negra o una luz cian en la losa |
| `pasarela_punta_der` | 80 | como la izquierda, del otro lado (si sale igual a la izquierda espejada, sirve espejarla) |

- **Los medios se repiten sin costura**: el borde izquierdo de cada medio empalma con el derecho de cualquier medio y
  con las puntas (misma losa, mismo contorno, mismas filas). No recortar en x: cada medio mide exactamente 256. Es el
  mismo caso que el `platform_kit` de `backgrounds/ranger_base` (`same_height`).
- Con esto salen pasarelas de 416 (80 + 256 + 80), 672, 928… Mientras el juego no repita tramos solo, las armo yo en
  PNG de ese ancho.

### Hoja 2: columnas, bloques y la guía del ascensor

Mismas filas que la pasarela donde aplica: línea de los pies en 16, franja que se estira y pies abajo.

| Pieza | Ancho × alto | Qué es | Franja que se estira |
|---|---|---|---|
| `columna_angosta` | 48 × 200 | pilar suelto para poner debajo de una flotante; arriba un capitel (sin cara pisable) | 24 – 176 |
| `columna_ancha` | 96 × 200 | pilar con **tope pisable** (como la columna del medio de la Refinería): línea de los pies en 16 | 72 – 176 |
| `bloque` | 128 × 200 | bloque macizo que frena balas y se sube saltando: cara de arriba con los pies en 16, frente de chapa | 72 – 176 |
| `pared` | 64 × 200 | lo mismo, angosto | 72 – 176 |
| `guia_ascensor` | 40 × 200 | riel vertical de fondo, sin colisión: muestra por dónde viaja el ascensor | 20 – 180 |

### Hoja 3: flotantes y ascensor

Sin patas: se ponen en el aire o se mueven. **80 px de alto**, línea de los pies en **8**, cara de arriba de 18
(8 – 26), cara de adelante de 28 (26 – 54) y abajo, hasta 80, lo que cuelga (propulsores, luces, refuerzos).

| Pieza | Ancho | Qué es |
|---|---|---|
| `flotante_200` | 200 | como la flotante de la Refinería, con tacos rojos en las puntas |
| `flotante_300` | 300 | la misma familia |
| `flotante_450` | 450 | la misma familia, con un taco al medio |
| `ascensor` | 200 | plataforma que sube y baja: franjas amarillas y negras en el frente, tacos rojos, un muñón de pistón abajo (nada que llegue al piso) |

### Hoja 4: decorado de fondo

Sin colisión: va detrás de todo lo jugable. Que se lea como fondo: **más azulado y con menos contraste** que lo
jugable, como el fondo de la Refinería low-poly. **Nada de caras de arriba claras y planas**, ni escaleras: que nada
parezca pisable.

| Pieza | Ancho × alto (aprox.) |
|---|---|
| `deco_tanque` | 240 × 360 |
| `deco_chimenea` | 100 × 520 |
| `deco_torre` (torre de refinería con luces cian) | 200 × 600 |
| `deco_cano_h` (tramo recto que se repite a lo ancho) | 256 × 48 |
| `deco_cano_v` (tramo recto que se repite a lo alto) | 48 × 256 |
| `deco_codo` | 96 × 96 |

## A2. Fondos de 2496 × 1404 sin pasarelas

- **Medida final exacta: 2496 × 1404.** A 2K 16:9 el modelo devuelve ~2752 × 1536 (1,79:1, no 16:9 justo): se lleva
  a 1404 de alto (~2516 de ancho) y se recortan ~10 px por lado. Que nada importante quede pegado a los costados.
- **Los detalles a la misma medida en px del juego que el fondo de la Refinería low-poly**: es una toma más abierta
  (se ve más refinería), no la misma agrandada. La lámina de `prueba_2496` es la de 1920 agrandada × 1,3 y por eso sus
  detalles se ven más grandes que las piezas.
- **El piso**, de lado a lado: línea de los pies en **y 1264** (140 px sobre el borde de abajo, como el 940 de la de
  1080), cara de arriba de ~36 px (1264 – 1300) y cara de adelante hasta abajo, con caños rojos y luces cian como el
  de la Refinería.
- **Nada pisable fuera del piso**: sin pasarelas, plataformas ni columnas con tope en la zona de juego. Las torres de
  los costados (hasta ~300 px de cada borde) pueden estar, como en la Refinería, sin caras de arriba claras.
- Entre el piso y y ~300 van las pasarelas del kit: ahí el fondo con contraste medio-bajo y bruma, para que las piezas
  se lean adelante.
- **Arriba a la derecha** (x > 1876, y < 195) va el HUD con 4 jugadores: cielo o algo liso.
- **Casi simétrico** (las arenas son simétricas).
- Sin personajes, HUD ni texto. Dos o tres opciones. En WebP, ~150–300 KB (la de `prueba_2496` pesa 159 KB).

## La entrega

Para cada pieza elegida: la ruta (`backgrounds/<set>/post/<asset>/<modelo>_<n>/<pieza>.png`) y su medida en px del
juego. Yo las paso a `prototypes/arena/arenas/`, mido la línea de los pies y la franja de las patas de cada una, y
las pongo en la paleta del editor. Si alguna medida de acá no le sirve al modelo, decímelo antes del dry-run y la
ajustamos.
