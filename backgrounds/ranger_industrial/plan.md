# Mundo industrial del ranger: análisis del concept y plan de props

El concept es `style_frame.png` (2026-10-16), que también es la referencia de estilo de `gen.toml`. En `concept_zonas.jpg` está marcado por zonas, y los números de este documento son los de esa imagen. Los enemigos, la torreta y el HUD quedan afuera por ahora.

## 1. Por qué el nivel de hoy se ve repetitivo y la imagen no

| | nivel de hoy (5000 px) | concept |
|---|---|---|
| Piso | Una sola franja gris a una altura, de punta a punta. | Dos pisos (1 y 7), un hueco con un puente de vigas (6) y un escalón de altura (20). |
| Obstáculos | Siempre la misma torre de bloques grises con franja amarilla, en distintas alturas. Son cajas sueltas apoyadas en el piso. | No hay cajas sueltas: todo es arquitectura. La pasarela sigue en una subestructura (3) que llega hasta abajo de la pantalla. |
| Profundidad | Un plano de juego plano delante del fondo. | La subestructura es calada: entre las vigas en X se ve el fondo. Los caños (4) cruzan delante y detrás, y el primer plano (19) enmarca abajo. |
| Orientación | Nada distingue un tramo de otro, salvo la antena y el cartel. | Hay hitos en los extremos: el edificio de entrada (12) y el portón blindado (13). |
| Color | Gris, violeta y franjas amarillas en todos los bloques. | La paleta es la del ranger (negro, blanco crema, rojo, cian). El amarillo queda para lo que se usa: escalera (5) y peligro (15). Los caños rojos guían la vista en horizontal. |
| Ritmo | Bloque, blanco, bloque, blanco, con la misma densidad en todo el nivel. | Alterna tramos densos (máquinas, caños) con tramos abiertos (puente y plataformas flotantes sobre el vacío). |

Lo que hace rica la imagen es un kit chico de piezas modulares combinadas de muchas maneras: pasarela, subestructura, viga y caño. No es una cantidad grande de props distintos, y eso es lo que conviene copiar.

## 2. La imagen pasada a nuestra escala

En el concept el ranger mide unos 73 px. En el juego, al 80%, mide unos 98, así que **las medidas de la imagen se multiplican por ~1,35**.

- **La imagen no es una pantalla nuestra.** Con la cámara al 75% vemos 1280 × 720 px del mundo, y la imagen, a nuestra escala, mide ~2260 × 1270. Lo que muestra entra en casi dos pantallas de ancho y en poco más de la mitad de su alto. Hay que leerla como un tramo de nivel.
- **Entre pisos hay ~320 px** (238 en la imagen). Colgándose se llega a una cornisa de unos 310 a 340 px (el salto de 192 más la mano), justo el límite: pasaría al ras, y depende de agarrar el borde en el punto más alto. Para pasar de un piso al otro conviene una escalera, un bloque intermedio, la chimenea, o bajar la distancia a ~280.
- **El hueco del medio mide ~400 px** (300 en la imagen). Corriendo, nuestro salto cubre unos 190 px a la misma altura. Hay que achicarlo a ~170 px, o cruzarlo con el doble salto o por el puente. La imagen no respeta nuestro salto, y es la primera cosa que hay que corregir al pasarla al juego.
- **Alto útil:** la cámara no se mueve en vertical y el piso queda al 88% de la pantalla, así que sobre el piso hay unos 630 px. Entran dos pisos y plataformas flotantes encima, pero no más. Un tercer piso o fosos pedirían cámara vertical.
- **Medidas aproximadas en px del juego:** pasarela de ~44 de grueso (placa más canto), abrazaderas rojas de ~40 cada ~190, caño grueso de Ø ~50, escalera de ~60 de ancho, plataforma flotante de ~230 × 65, caja de ~155 × 65.

**Riesgo de lectura.** El ranger es rojo, blanco y negro, igual que el mundo de la imagen. Ahí se lee porque detrás tiene el azul del cielo o metal oscuro. La regla: en la franja donde se mueve el personaje (del piso a ~110 px arriba), fondo frío y oscuro. Las masas grandes de rojo y blanco van debajo de la línea del piso y en los hitos.

## 3. Props necesarios, por kit

**Tileable** quiere decir que la pieza se repite sin costura: la pasarela se estira a cualquier ancho y la subestructura llena cualquier alto. **Capa** es dónde se dibuja respecto del ranger. `back` y `fixture` son los papeles de `ranger_props/integrar.md`.

### A. Pasarela, el piso nuevo (zonas 1, 2, 7)
| pieza | tamaño aprox. | tileable | capa / colisión |
|---|---|---|---|
| `top_a`: placa crema con canto negro y luces chicas, con una abrazadera roja en el centro | 190 × 44 | horizontal | juego, sólida |
| `top_b`: igual, con una franja amarilla y negra en vez de la abrazadera. Se alterna con `top_a` | 190 × 44 | horizontal | juego, sólida |
| `cap_left`, `cap_right`: puntas con la abrazadera de cierre | 48 × 44 | no | juego |

No hay calcos sueltos: el post descarta lo que mide menos del 2% de la pieza más grande de la hoja, así que las luces vienen dibujadas en el canto y la franja de peligro es una variante de la placa.

### B. Subestructura: el relleno debajo de cada pasarela (zona 3)
| pieza | tamaño aprox. | tileable | capa |
|---|---|---|---|
| `truss_a`, `truss_b`: paneles de vigas en X (una grande y dos chicas), calados: transparentes entre las vigas | 128 × 128 | horiz. y vert. | detrás del ranger |
| `column`: columna de perfil doble T | 32 × 128 | vertical | detrás |
| `machine_a/b/c`: paneles de máquina opacos, con tira cian, rejilla o tapa | 128 × 128 | horiz. y vert. | detrás |

La viga que va justo debajo de la placa es el canto negro de la pasarela.

Cada sólido se rellena eligiendo entre estos paneles con un azar con semilla. La misma semilla da siempre el mismo dibujo, y dos paneles iguales nunca quedan juntos. Esto es lo que más corta la repetición. El ventilador de `ranger_props` (`face`) se usa como un panel más.

### C. Caños (zonas 4 y 19)
| pieza | tamaño aprox. | tileable |
|---|---|---|
| grueso (Ø 50): `thick` (recto), `thick_elbow` (codo), `thick_tee` (T), `flange` (brida), `valve` (volante de válvula) | 150 de tramo | el recto |
| fino (Ø 22): `thin` (recto), `thin_elbow` (codo) | 70 de tramo | el recto |

Un caño se arma como una línea de puntos en el nivel, y el juego pone los rectos y los codos. Los verticales y los codos para otros lados son las mismas piezas rotadas y espejadas, con la luz del caño de costado. Va en tres planos: detrás de la subestructura (teñido), delante de ella y en primer plano (zona 19, sólo en el borde de abajo y más rápido que el mundo). El primer plano usa este mismo kit, más grande y más oscuro, sin hoja propia.

### D. Puente de vigas (zona 6)
| pieza | tamaño aprox. | tileable | colisión |
|---|---|---|---|
| `bridge_a`: un tramo entero, con la viga de arriba (la que se pisa), una X calada y la viga de abajo | 140 × 140 | horizontal | se pisa la viga de arriba |
| `bridge_b`: el mismo tramo con la luz naranja en el centro | 140 × 140 | horizontal | ídem |

En la imagen el puente queda ~95 px debajo de la pasarela alta, así que es una tercera altura que no cuesta nada.

### E. Escalera (zona 5)
`ladder_mid` (60 × 32, tileable vertical) y `ladder_top` (con pasamanos que asoman sobre el piso). **No conviene ponerla antes de que se pueda usar.** Una escalera que no se trepa le enseña al jugador que el decorado miente. Para usarla hace falta un clip nuevo del ranger trepando de espaldas (Seedance, dos intentos, ~US$3) y el estado en el juego.

### F. Plataformas (zonas 9 y 11)
| pieza | tamaño aprox. | notas |
|---|---|---|
| `float_s`, `float_m`: flotante de placa crema y puntas rojas, con la panza oscura en punta y un brillo de propulsor | 160 y 230 × 65 | reemplazan a las `slab` de hoy |
| `ledge`: repisa de pared con dos ménsulas en diagonal | 230 × 90 | se apoya en un muro o edificio |

### G. Hitos y muros (zonas 12, 13, 14)
| pieza | tamaño aprox. | uso |
|---|---|---|
| `entry_building`: edificio de entrada con marco blindado y puerta | 270 × 390 | el principio del nivel, como límite izquierdo |
| `blast_door`: portón blindado con chevrones | 180 × 570 | el final, como límite derecho. Más adelante puede abrirse con el interruptor de la fase 3 de props |
| `tank_tower`, `tank_pair`: un tanque cilíndrico alto con tira cian, y dos más bajos unidos por un caño | 150 × 400 y 250 × 300 | detrás de la pasarela, uno cada ~1500 px como referencia |
| `wall_a`, `wall_b`: paneles blindados, blanco con franja roja y rojo con franja blanca | 128 × 128, tileable en los dos sentidos | caras de los sólidos altos (la chimenea) y muros que cortan el paso. Van en la hoja `small_props`, por la altura |

### H. Utilería chica (zonas 8, 10, 15)
| pieza | tamaño aprox. | notas |
|---|---|---|
| `crate_x_s`, `crate_x_l`: cajas grises de acero con X | 95 × 75 y 155 × 65 | Detrás del ranger, sin chocar. Si se ponen en el plano de juego tienen que chocar: el commit `49de359` sacó las cajas que no hacían nada |
| `hazard_post`: poste amarillo y negro | 40 × 140 | marca bordes y peligros |
| `cell`: cápsula de energía cian, con el brillo animado | 30 × 45 | el futuro coleccionable. Por ahora, decorado sobre las flotantes |

### I. Fondo de día (zonas 16, 17, 18)
Son las mismas cuatro capas de parallax que hoy, con otro contenido: `sky` (azul con nubes planas), `far` (torres pálidas, casi del color del cielo), `mid` (refinería con tiras cian y puentes de caños) y `near` (estructuras azul oscuro). En la imagen se nota la perspectiva atmosférica: cuanto más lejos, más azul y menos contraste. Es lo que el prompt `far` de `ranger_base` ya pide, pero hacia el azul en vez del violeta.

## 4. Qué se reutiliza

- **De `ranger_props` sirven casi todos:** la caja rompible y el barril explosivo como blancos, `crate_stack`, `console`, `monitor`, `beacon`, `panel_spark`, el ventilador como panel de subestructura y la puerta y el interruptor para la fase 3. Son de metal gris con acentos rojos, cian y amarillo, que es la misma familia. Si el fondo pasa a de día, el tinte de fondo `BACK_TINT` tiene que pasar de violeta a azul.
- **Se reemplaza:** el kit de bloques y las flotantes de `ranger_base` (`platform_kit`), y las cuatro capas de noche si se elige el día.
- **El nivel de hoy se rearma.** Las pruebas que tiene (bloque para colgarse, chimenea, plataforma para atrás) siguen sirviendo, pero como tramos de la pasarela.

## 5. Generación

- Con `spritepipe gen-images`, un set nuevo `backgrounds/ranger_industrial/`. Las piezas del plano de juego van con GPT Image 2.5 Sunburst (alfa nativo, el modelo de `ranger_props`) y las capas, con Nano Banana 2.1 (el de las capas de `ranger_base`). Referencias: este concept y `poses/ranger_concept.png`.
- **Las hojas se agrupan por altura**, como en `ranger_props`, para que el post no desordene los nombres.
- **La costura ya la arregla el post.** `tile = "x"`, `"y"` o `"xy"` por pieza mide la costura de cada tileable y, si se nota, la corrige con un corte de error mínimo (es lo que se usó en el kit y las capas de `ranger_base`). No hace falta nada nuevo en `pipeline/`.
- **Costo, según el dry-run del 2026-10-16:** US$3,15 en total. Las 7 hojas de GPT Image, a US$0,17 cada imagen y con 2 opciones, dan US$2,38. Las 4 capas de Nano Banana, a US$0,06 y con 3 opciones, dan US$0,76.

## 6. Editor de niveles

**El problema de hoy.** El nivel son llamadas en el código con coordenadas a mano (`block(860, 84, 220)`, `put("fan", 2195, GROUND - 230)`). Para ubicar algo hay que adivinar un número, armar, recargar y mirar. Con un kit de ~40 piezas, eso es lo que deja los props "en cualquier lado".

**Paso 1: el nivel como datos, con el kit.** Pasa a `prototypes/ranger/levels/<nivel>.json`, y `prototypes/build.py` lo mete en la página como hace con el arte:

```json
{ "world": { "w": 5000, "seed": 7 }, "spawn": [300, 0],
  "solids":   [{ "kind": "walkway", "x": 0, "top": 0, "w": 840 }, { "kind": "bridge", "x": 840, "top": 95, "w": 300 },
               { "kind": "float", "size": "m", "x": 1000, "top": 330 }],
  "ladders":  [{ "x": 800, "from": 0, "to": 320 }],
  "pipes":    [{ "size": "thick", "layer": "front", "path": [[0, -60], [260, -60], [260, -140]] }],
  "landmarks":[{ "name": "entry_building", "x": 0 }, { "name": "blast_door", "x": 4820 }],
  "deco":     [{ "name": "crate_stack", "x": 500, "y": 0, "layer": "back", "flip": false }],
  "targets":  [{ "kind": "board", "x": 640, "y": 0 }] }
```

Las alturas se miden desde el piso de abajo. Lo que diseña la persona son rectángulos y unos pocos objetos. El **vestido es automático**: tope de pasarela, puntas, abrazaderas cada ~190 px, subestructura con variantes por semilla y luces del canto. Eso corta la repetición sin ubicar nada a mano. Este paso no gasta nada y hace falta igual para el kit nuevo.

**Paso 2: el editor, dentro de la misma página del juego** (tecla E). Así lo que se ve al editar es exactamente lo que se juega.
- Grilla de 16 px y paleta con miniaturas de las piezas.
- Los sólidos se dibujan arrastrando. Los props se ponen con clic y después se mueven, se espejan y se borran.
- Capas que se prenden y apagan (fondo, juego, frente) y deshacer.
- **Probar desde acá:** se juega desde donde está el cursor, y con E se vuelve al editor en el mismo lugar.
- **Alcance del salto:** marca en rojo las plataformas a las que no se llega, calculado con los números de `FEEL` (salto de 192 px, ~190 px de distancia corriendo, cornisa colgándose hasta ~310 a 340). Para ustedes es lo más útil del editor, porque la imagen ya mostró que es fácil dibujar huecos imposibles.
- **Guardado:** se baja y se sube el JSON. Otra opción es guardarlo en la base de datos del artifact, así los dos editan el mismo nivel desde el link y yo lo paso al repo.

**Recomendación.** Hacer el paso 1 junto con el kit, y el editor antes de armar el nivel largo. Armar dos pisos con caños y subestructura escribiendo coordenadas es justo lo que salió mal con los props.

## 7. Fases

| fase | qué | costo | archivos |
|---|---|---|---|
| 1 | Hojas de estructura: A, B, D, F (`walkway`, `substructure`, `bridge`, `platforms`) | US$1,36 | set nuevo |
| 2 | Hojas de caños, hitos y utilería: C, G, H (`pipes`, `landmarks`, `small_props`) | US$1,02 | set nuevo |
| 3 | Fondo de día: las 4 capas (I: `sky`, `far`, `mid`, `near`) | US$0,76 | set nuevo |
| 4 | Nivel como datos, vestido automático y nivel rearmado con dos pisos | sin costo | `src.html`, `build.py` |
| 5 | Editor | sin costo | `src.html` |
| 6 | Escalera jugable (clip de Seedance) y cápsulas como coleccionable | ~US$3 | personaje, `src.html` |
| después | Pasar a través de las plataformas desde abajo (puente y flotantes), fosos con reaparición y cámara vertical | sin costo | `src.html` |

Las fases 1, 2 y 3 están en `gen.toml` y salen en una sola corrida (o por fase, con `--assets`). La 4 y la 5 tocan el mismo archivo del juego y van una después de la otra, en esta sesión.

**Elegidas el 2026-10-16** en `kit.html`: opción 1 de `walkway`, `substructure`, `platforms` y `pipes`; opción 2 de `bridge`, `landmarks` y `small_props`; capas `sky` 1, `far` 1, `mid` 2 y `near` 1. La opción 1 del cielo es la única sin ciudad y empalma con `seam = "clear"` (queda una nube por vuelta).

## 8. Por decidir

- ~~¿De día o de noche?~~ Decidido el 2026-10-16: de día, como la imagen. `gen.toml` lleva el estilo `game` de día y regenera las 4 capas.
- **¿El hueco se cruza saltando?** Si es así, se achica a ~170 px. Si no, se cruza por el puente o por el piso de abajo.
- **¿Plataformas que se atraviesan desde abajo?** Hoy las `slab` son sólidas. En los run-and-guns las flotantes y los puentes suelen dejarse atravesar desde abajo, y eso cambia cómo se diseñan los dos pisos.
