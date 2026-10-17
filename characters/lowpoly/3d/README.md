# Vía 3D del personaje low-poly (prueba del 2026-10-17)

Modelo 3D desde la hoja de vistas por API, auto-rig, animaciones de biblioteca y render de costado con el encuadre
de `poses/perfil_dullmagenta_16x9.png`, para comparar con los clips de video del bake-off del idle. Gastado:
**US$2,045** (Meshy 1,52 + Hunyuan 0,525, precios de lista de fal).

## Veredicto (Pablo, 2026-10-17): este workflow no dio

Pablo vio los clips y el modelo y no le convencen: las animaciones se ven mal y el modelo 3D tampoco está a la altura
del concept. Lo que falla es el workflow automático (generador de modelos por IA + auto-rig + mocap de biblioteca o
ciclos por script), no la idea de pasar por 3D:

- **El modelo**: Meshy rehace la malla con triángulos parejos (remesh a 10k) y pinta los colores encima; el concept es
  low-poly de superficies duras, con pocos planos grandes y aristas marcadas. El casco queda redondeado, las hombreras
  blandas y los bordes de color dependen de la textura, no de la geometría. El arma (Hunyuan, un objeto simple) salió
  mucho mejor que el personaje.
- **Las animaciones**: el mocap de la biblioteca es de proporciones humanas y en un chibi se rompe (giros, patadas,
  pesos); los ciclos "a mano" son curvas por script, sin poses clave ni timing de animador.

Lo que queda como dato: la consistencia por construcción funciona (0 % de colores inventados), y el arma 3D de Hunyuan
es usable. Si se vuelve a la vía 3D, sería con el modelo y el rig hechos a mano (el personaje es simple) y los ciclos
animados por una persona; la IA, a lo sumo, como referencia de volumen.

## Qué hay

| | |
|---|---|
| `gen3d.py` | Los dos pedidos pagos (con `--dry-run`). Congela las vistas que usa en `entradas/` |
| `out/personaje/` | Meshy 7.1 multi-image-to-3d (4 vistas en T-pose con cinturón rojo, 10k triángulos): `model_glb.glb` (sin rig), `rigged_character_glb.glb` (T-pose riggeada, 24 huesos), `animation_glb.glb` (Idle de la biblioteca, id 0), `basic_animations__{walking,running}_glb.glb`, la textura (2048², albedo plano) y los FBX |
| `out/arma/` | Hunyuan 3D 3.1 Pro (el lateral de frente y su espejo de espalda): `model_glb.glb` (500k caras, textura 4096²) |
| `render.py` | Blender sin ventana: rehace los pesos del auto-rig (en memoria, el GLB no se toca), arma la escena, emparenta el arma al pecho, los brazos la agarran por IK y renderiza cada ciclo a PNG con alfa (`render/<clip>/`). Clips: `idle` y `caminar` (biblioteca), `correr` (biblioteca con la patada achicada), `idle_mano` y `correr_mano` (hechos en el script) |
| `post.py` | `clips/<clip>.mp4` (1920×1080, 24 fps, sobre #C42D7D, el ciclo repetido hasta pasar 5 s), `clips/<clip>_ciclo.mp4` y `tiras/<clip>_verde.png` (cuadro por cuadro a 12 fps) |
| `encuadre.json` | Escala y posición de la cámara (sale del cuadro 0 del idle; todos los clips usan el mismo) |
| `torso/` | `medir_torso.py` sobre los cinco clips |
| `inspeccionar.py` | Qué trae un GLB (huesos, acciones, caras) |

## Rearmar (no gasta)

Desde la raíz, con Blender 5.2 (`brew install --cask blender`):

```bash
blender -b --factory-startup -P characters/lowpoly/3d/render.py -- idle idle_mano correr correr_mano caminar
uv run --project pipeline python characters/lowpoly/3d/post.py idle idle_mano correr correr_mano caminar
uv run --project pipeline python characters/lowpoly/medir_torso.py --pose characters/lowpoly/poses/perfil_dullmagenta_16x9.png --box 820,478,985,645 --hoja characters/lowpoly/3d/entradas/vistas_tpose_cinturon_rojo_C0C3CC.png --out characters/lowpoly/3d/torso characters/lowpoly/3d/clips/{idle,idle_mano,correr,correr_mano,caminar}.mp4
```

El render de los cinco tarda ~6 min en esta Mac (EEVEE). `render.py -- idle --cuadros 0` renderiza un solo cuadro,
`--sufijo _prueba` escribe en `render/<clip>_prueba/` para comparar y `--crudo` usa los pesos de Meshy y la carrera
sin achicar (lo de antes). `post.py idle --contra-pose` pone el cuadro 0 al lado de la pose. Para rehacer el encuadre,
borrar `encuadre.json`.

## Cómo salió

- **El modelo**: muy fiel a la hoja (casco con la M, orejeras, hombreras, cinturón rojo, botas, cara). La textura es
  albedo sin luz horneada, con los mismos colores que el concept iluminado (traje 40 contra 44, rojo 216–232 contra
  231), así que la luz la pone Blender. El arma de Hunyuan sale casi idéntica a la hoja.
- **El rig con proporciones chibi**: el esqueleto es correcto (24 huesos, articulaciones en su lugar), pero:
  - El **Idle (id 0)** de la biblioteca es uno que mira a un costado: gira el cuerpo ~90° y vuelve, y en el chibi el
    giro llega a ±130°. No es la importación: el FBX da lo mismo. Se le sacó el giro alrededor de la vertical a cadera,
    columna, cuello y cabeza (`sin_giro`) y quedó de perfil con el peso que pasa de un pie al otro; los pies se abren
    un poco (el giro de las piernas venía compensando el de la cadera).
  - Los huesos vienen con **colas absurdas** (el antebrazo termina a 20 m): para el IK se rehacen las del brazo.
  - Los **brazos no llegan** a la pose del concept: el hombro del rig queda ~10 cm más alto y ~9 cm más atrás que en el
    dibujo, y del hombro a la muñeca hay 0,44 m en 1,70. El arma queda ~40 px más alta y más atrás que en la pose.
    Estirar el IK no sirve (Blender escala el hueso entero y las manos salen gordas).
  - Los **pesos del auto-rig** no sirven para el chibi: el pecho pesa 0,4–0,8 a `Head` (el casco es enorme y su
    influencia baja hasta el cinturón), la panza y el cinturón ~0,5 al muslo, y las hombreras mezclan cabeza, hombro y
    brazo: **se rompían** al llevar el brazo adelante y el muslo arrastraba la panza al correr.
  - **Correr** (el básico) patea muy atrás para unas piernas tan cortas (muslo ±43° y rodilla ±80° de su media): la
    bota sube hasta la cadera. **Caminar** (también gratis con el rig) se lee mejor: pasos cortos, sin torceduras.

## Arreglos del rig y las animaciones (2026-10-17, en Blender, sin gastar)

Todo en `render.py`, sobre lo importado: el GLB de Meshy no se toca.

- **Pesos por zona** (`repesar`), sobre la posición de reposo: casco y cara rígidos a `Head` (todo vértice que toca una
  cara blanca o de piel, más lo de arriba de z 0,99); tronco y cinturón a la columna por altura (`Hips` → `Spine`, cada
  hueso en la mitad de su tramo); debajo del cinturón, los pesos de la pierna de Meshy sin la cabeza ni el brazo;
  brazos, los de Meshy sin la cabeza, y la axila mezclada con el tronco. Las copias de un vértice que el glTF parte en
  las costuras de UV reciben los mismos pesos (se sueldan por posición), así que no se abren grietas.
- **Hombreras rígidas**: se encuentran solas (caras rojas de la textura conectadas desde arriba del hombro: 374 y 456
  caras) y van 100 % a un hueso nuevo por lado (`RightHombrera`/`LeftHombrera`), hijo del hombro y con el reposo del
  brazo, que copia el 60 % de la rotación del brazo (`HOMBRERA_SIGUE`). Con 0 quedaba como un arco hueco sobre el
  brazo; con 0,6 es un bloque arriba del brazo, como en el concept. Meshy fundió el borde de abajo del casco con la
  hombrera: esa costura va con el casco.
- **`correr`**: la básica con la amplitud achicada alrededor de la rotación media de cada hueso (`ACHICAR`: piernas
  ×0,55, pies ×0,5, cadera y columna ×0,6, rebote ×0,7). La bota ya no sube a la cadera; la de atrás todavía muestra la
  suela en 3 de los 8 cuadros de la tira y el arma cabecea con la columna.
- **`correr_mano`**: 16 cuadros a 24 fps (8 a 12 fps) desde el reposo (`CORRER_MANO`): cada tobillo sigue una
  trayectoria (34 % del ciclo en el piso, de 21 cm adelante a 20 cm atrás de la cadera; en el aire sube 19 cm, primero
  el talón atrás y después la rodilla adelante) y la rodilla sale de un IK de dos huesos hecho en el script; los pies
  quedan planos en el apoyo, la cadera rebota 3,5 cm, el pecho se inclina 10°. El arma no cabecea (va al hueso de
  abajo de la columna, que no gira) y la cabeza queda a la altura del idle.
- **`idle_mano`**: 48 cuadros (2 s) sobre el cuadro 0 del idle de la biblioteca (`IDLE_MANO`): la cadera baja 1,6 cm
  con las rodillas dobladas y los pies quietos, el pecho respira 1,6°, los hombros suben 6 mm y la cabeza cabecea 2°
  con retraso.
- **Al piso**: correr, correr_mano y caminar se suben o bajan para que lo más bajo del ciclo, visto por la cámara, caiga
  en y = 778 como el idle (antes caminar se hundía hasta 795 y correr hasta 787). Se apoya en la imagen y no por la z:
  con la cámara 6° desde arriba, el pie del lado de la cámara se ve ~12 px más abajo que el de atrás a la misma altura.

Cómo quedó cada clip (silueta en px del 1920 × 1080; la pose: arriba 260, pies 778):

| clip | cuadros | arriba | piso | pies (borde de atrás) |
|---|---|---|---|---|
| idle | 96 (4 s) | 255–265 | 774–781 | 737–784 (da pasitos) |
| idle_mano | 48 (2 s) | 258–265 | 777–778 | 759–761 (quietos) |
| correr | 15 (0,62 s) | 218–233 | 749–778 | 760–813 |
| correr_mano | 16 (0,67 s) | 257–268 | 760–778 | 756–823 |
| caminar | 25 (1,04 s) | 210–228 | 745–778 | 749–815 |

Ojo: el idle de la biblioteca está agachado, así que correr y caminar (de la misma biblioteca) quedan 30–37 px más
altos que él; correr_mano queda a la altura del idle.

Lo que queda:
- Arriba de la hombrera, pegado al casco, se ven unas rayas rosadas finas (~7 px a esta escala): la hombrera, al
  girar con el brazo, muestra una parte que en reposo queda bajo el casco y que Meshy pintó con el borde blanco. Mezclar
  esa zona con la cabeza no cambió nada; habría que repintar esa parte de la textura o bajar `HOMBRERA_SIGUE`.
- El idle de la biblioteca sigue mirando de reojo y dando pasitos (los pies se corren 47 px); `idle_mano` no.
- El arma sigue ~40 px más alta y más atrás que en la pose (los brazos del rig no llegan, ver arriba).

## Consistencia

Total, por construcción. `medir_torso.py` sobre los cinco clips (`torso/`; la pose misma da 16–18 % de *ajeno* contra
la hoja con cinturón rojo):

| clip | mov p95 | ΔE med / p95 | cambio med / p95 | ajeno | antes de los arreglos |
|---|---|---|---|---|---|
| idle | 13,3 px | 8,6 / 13,0 | 13,5 % / 20,5 % | 0,0 % | ΔE 9,6 / 14,3, cambio 14,9 % / 24,1 % |
| idle_mano | 5,1 px | 2,9 / 4,4 | 2,7 % / 5,7 % | 0,0 % | |
| correr | 19,7 px | 13,3 / 25,9 | 18,1 % / 36,9 % | 0,0 % | ΔE 15,1 / 29,3, cambio 21,5 % / 43,6 %, mov 25,5 px |
| correr_mano | 9,1 px | 5,8 / 8,8 | 7,5 % / 12,6 % | 0,0 % | |
| caminar | 16,6 px | 14,5 / 18,4 | 22,3 % / 29,9 % | 0,0 % | |

La *deriva* (ΔE y cambio) es movimiento real (el hombro, el brazo y el arma que suben, bajan y giran), no invención:
la métrica no los separa. Las tiras del torso muestran los mismos polígonos en todos los cuadros, ahora con la
hombrera entera.
