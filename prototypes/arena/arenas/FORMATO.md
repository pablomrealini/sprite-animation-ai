# El formato de las arenas

Es el contrato entre el juego (`prototypes/arena/src.html`, de Programación) y el editor (`prototypes/arena/editor/`,
de Editor de niveles). Cada `arenas/<nombre>.json` es una arena del menú del juego; los `arenas/<carpeta>/*.json`
son borradores o fuentes (el editor los abre y el juego no). Lo escribió Editor de niveles el 2026-10-18 y lo revisa
Programación (2026-10-18: el juego quedó igual a este archivo, y las 5 arenas que existían, idénticas en colisión).

## Reglas

- Todo va en **px del juego**, con la y para abajo. La `y` de lo que se pisa es **la línea de los pies**: el borde de
  atrás de la cara de arriba pintada (la primera fila clara bajo el contorno oscuro); el juego hunde los pies 3 px.
- Un campo nuevo entra **primero en el juego**, con un valor por defecto que deja iguales las arenas que ya existen;
  después en el editor y en este archivo. Ninguno de los dos borra campos que no conoce: el editor los guarda como
  vinieron.
- El editor y `serve.py` escriben el JSON con una clave por renglón y cada sólido, objeto o spawn en el suyo.
- Las imágenes (`plate.src`, `pieces.*.src`) son rutas relativas a `arenas/`. Una arena puede usar las de otra
  (`prueba_2496` usa las de `refineria_lowpoly/`). `build.py` del juego las copia a `dist/arenas/`.

## Campos

| Campo | Qué es | Por defecto |
|---|---|---|
| `name` | el nombre del menú | la clave |
| `note` | notas libres | — |
| `size` | `[ancho, alto]` del mundo. La cámara muestra la arena entera: `ZOOM = 960 / ancho` (`setWorld`). 1920 × 1080 las de antes; 2496 × 1404 las nuevas (el personaje se ve 23% más chico y hay 1,69 veces más lugar) | `[1920, 1080]` |
| `seed` | la semilla de lo que el kit elige solo (topes, relleno, patas) | — |
| `plate` | la lámina: `{src, solid}`. `src`, la imagen de fondo, del tamaño de `size`. `solid`, rectángulos `[x, y, w, h]` de la lámina que se dibujan delante de los que están colgados | sin lámina: el kit |
| `pieces` | las piezas pintadas de esta arena, por nombre (ver abajo) | `{}` |
| `solids` | lo fijo que se pisa (ver abajo) | `[]` |
| `objects` | lo que se pone encima: piezas pintadas o del kit, quietas o con recorrido (ver abajo) | `[]` |
| `spawns` | lugares de salida `[[x, y], ...]`: `x` el centro del personaje, `y` la línea de los pies de lo que pisa | `[]` |
| `color` | la graduación: `{fondo: {...}, plataformas: {...}, bruma_color}`. Cada grupo: `paleta` (0–1, el LUT de Pablo), `saturacion`, `contraste`, `brillo` (1 es neutro) y `bruma` (0–1). `bruma_color` `"#rrggbb"`; sin él, el promedio del sexto de arriba de la lámina. La cuenta es `gradePixels` de `color.js`, la misma en el juego y en el editor | sin graduar |
| `platforms`, `decor`, `pipes` | sólo las arenas del kit (Fundición): flotantes y repisas del kit, decorado y caños que arma `bake()`. Con lámina no se dibujan | `[]` |

### `solids`

`{kind, x, y, w, ...}`. `x` es el borde izquierdo y `y` la línea de los pies.

| `kind` | Qué es |
|---|---|
| `bridge` | se atraviesa desde abajo y se baja con abajo + saltar. Mide 26 de alto |
| `walk` | bloque: no se atraviesa, frena balas. `h` su alto (60 si falta). En el kit, `fill: "full"` o `"row"` y `legs` eligen el dibujo |
| `box` | caja: como `walk` (`h` 60 si falta), sin cornisa |

- `ground`: es el piso. Si falta, es piso lo que está a 200 px del borde de abajo o menos (`y >= alto − 200`).
- `ledge`: de qué borde se cuelga (`both`, `left`, `right`, `none`). Con `HANG_ON = false` (hoy) no se usa.
- `noLedge`: sin cornisa (el piso y las cajas ya lo son).

### `pieces`

Por nombre: `{src, w, h, solids, front, legs, legsGap, cut}`. Un PNG con alfa; `w` y `h` en px del juego (el PNG
puede ser más grande: se dibuja a `w × h`). Todo lo de adentro es relativo a la esquina de arriba a la izquierda de
la pieza:

- `solids`: como los de arriba (`bridge` si falta `kind`), con `y` la línea de los pies dentro de la pieza.
- `front`: rectángulos de la pieza que van delante de los colgados.
- `legs: [y0, y1]`: la franja de las patas, que se estira con `stretch` del objeto (lo de arriba de `y0` queda igual
  y lo de abajo de `y1` baja). `legsGap`: cuántos px por encima de lo de abajo terminan las patas ("Que llegue abajo"
  del editor).
- `cut`: dónde estaba la pieza en la lámina original (lo usa `capas.py`).

### `objects`

`{piece, x, y, ...}`.

- **Pieza pintada** (`piece` es una de `pieces`): `x, y` es su esquina de arriba a la izquierda. `flip` la espeja
  dentro de su caja, `ledge` pisa el de sus sólidos y `stretch` (px) alarga las patas. Se dibujan en el orden del
  JSON.
- **Pieza del kit** (`platforms/*`, `small_props/*`, `landmarks/*`): `x` es el centro; `y`, lo que se pisa en las
  plataformas y la base en lo demás. `solid: false` no choca; `layer: "back"` la manda detrás, oscurecida, y tampoco
  choca.
- `move: {path: [[x, y], ...], speed, wait}`: ida y vuelta por los puntos, con `wait` s de pausa en las puntas, a
  `speed` px/s, y lleva al que está encima. En las pintadas cada punto es la esquina; en las del kit, el centro de lo
  que se pisa. El primer punto es su `x, y`. Si faltan, `speed` 120 y `wait` 0,5; `speed: 0` vale 0 (no se mueve).

## Campos que usa sólo el editor (el juego los ignora)

- En `objects`: `tira`, un id; las piezas con la misma tira son una pasarela (o un caño) armada por tramos, una al lado
  de la otra, y el editor las elige y las mueve juntas.
- En `pieces` (copiados del kit): `espejo` (con qué se hace la copia del otro lado: `"mismo"`, la misma pieza sin
  espejar; un nombre, la pieza del otro lado; sin él, se espeja con `flip`), `deco` (decorado sin colisión: va detrás
  de todo) y `tramo` (`"x"` se repite a lo ancho, `"y"` se estira a lo alto).

## Kits de piezas

`arenas/<kit>/kit.json` (hoy `kit_lowpoly`, lo arma `editor/kit.py` desde la entrega de Arte; no se edita a mano): las
piezas (con el mismo formato que `pieces`, más `grupo` para la paleta) y los fondos (`fondos: [{src, size, piso}]`).
No es una arena y el juego no lo lee: al poner una pieza en el editor, su definición se copia a la arena, con el `src`
del kit. Las imágenes viven en `arenas/kit_lowpoly/` para que `build.py` las copie con las arenas que las usan.
Una pasarela por tramos son piezas sueltas encimadas 2 px (los bordes tienen alfa 252; pegadas justo se ve la unión).

## Lo que el juego decide solo (no está en el JSON)

- Paredes a los costados (`x < 0` y `x > ancho`) y un techo, invisibles.
- Los power-ups: al azar sobre caras de arriba de 60 px o más, a 90 px de las paredes, o en un spawn (`pickupSpot`).
- El HUD: arriba a la derecha, en px de pantalla. Con 4 jugadores tapa ~620 × 195 px del mundo en las de 2496.
