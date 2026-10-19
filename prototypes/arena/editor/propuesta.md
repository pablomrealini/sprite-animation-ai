# Propuesta: el editor de arenas para escenarios grandes (2496 × 1404)

Editor de niveles, 2026-10-18.

**Lo que decidió Pablo (2026-10-18):** la tanda 1 va como está, con el clic en vacío como recuadro de selección; `editor/`
y las arenas nuevas pasan a Editor de niveles (las que existen siguen de quien las hizo; `prueba_2496` es de
Programación), con `arenas/FORMATO.md` como contrato; las arenas grandes se arman con un kit de piezas (medidas en
`kit_medidas.md`); los power-ups siguen al azar (J2 afuera).

**Estado:** la tanda 1 (E1–E6) está hecha el mismo día; cómo se usa, en `README.md`. Al hacer E6 apareció que el salto
del juego depende de los Hz de la pantalla (medido: simple 183 / doble 331 a 60 Hz, 188 / 340 a 120–144 Hz; la cuenta
exacta da 192 / 348): Programación lo pasó a trapecio y desde entonces da 192 / 348 en cualquier pantalla; el editor
integra igual. Lo que sigue de acá abajo es la propuesta tal como se escribió, antes de eso.

## En corto

El editor de hoy alcanza para retocar una arena hecha: abre el mismo JSON que el juego, prueba sin guardar en 3 s,
estira las patas solas y calcula el alcance del salto en vivo. Para **armar** una arena grande le faltan tres cosas:

1. **Trabajar de a muchos y en espejo.** Todas las arenas son simétricas, pero la copia simétrica (M) es de una sola
   vez: después cada mitad va por su lado. No hay selección múltiple, y los spawns no siguen a lo que pisan.
2. **Piezas para armar.** Una arena nueva arranca sin piezas low-poly: la paleta trae sólo el kit 2D del ranger. Para
   reusar las pasarelas de la Refinería low-poly hay que copiar sus definiciones a mano en el JSON (así se hizo
   `prueba_2496`), y no hay pasarelas que se alarguen a lo ancho.
3. **Un alcance que sirva para el juego.** El editor dice "se llega a todo" en `prueba_2496`, pero los bots no pasan
   del 2.º piso (0% del tiempo en el de 430). El grafo que arma el editor no lo usa nadie.

**Tanda 1 recomendada** (sólo el editor, ~1 a 2 sesiones, no toca nada de Programación): borrador por arena y
respaldo al guardar, piezas de todas las arenas en la paleta, simetría viva, selección múltiple con spawns que siguen
a su superficie, guías de la escala (pisos, HUD, caídas que duelen) y la física leída del juego. Detalle y criterios
de aceptación en "Primera tanda".

## Cómo lo probé

- Leí entero `editor/` (`editor.html`, 1355 líneas; `serve.py`, `build.py`, `capas.py`, `flotante.py`) y del juego
  `setWorld`, `addSolid`, `loadArena`, `loadObjects`, `moveObjects`, `pieceArt`, `pickupSpot`, `climbGoal`,
  `pickRoam` y `botInput`, más las notas de Programación sobre la escala.
- Abrí `http://localhost:8772/editor/dist/index.html#prueba_2496` en el navegador integrado, a 1440 × 900, y armé
  encima sin guardar: agregué una flotante, la llevé arriba, hice su copia simétrica, subí una pasarela con patas,
  puse una plataforma del kit, probé en el juego, deshice y medí el dibujo. Al final borré mi borrador del navegador:
  `arenas/prueba_2496.json` quedó como estaba (17:51:59) y no había borradores de otros en ese origen.

## Cómo se arma hoy una arena desde una lámina

1. Una imagen (de Pablo o del modelo) → edición con IA para limpiarla (Nano Banana 2.1, ~US$0,12) → recorte al tamaño
   de la arena.
2. En el editor, "+ Sólido" y calcar cada pasarela sobre la lámina (la `y` en el borde de atrás de la cara de arriba).
3. Para pasarla a capas: otra edición "sin pasarelas" y `capas.py`, que recorta cada pasarela como pieza con alfa.
   Las zonas de cada pieza están **escritas a mano en Python** (`LEFT` en `capas.py`, sólo para `refineria` y
   `refineria_lowpoly`), y la flotante sale de un polígono medido a mano (`flotante.py`). Una lámina nueva = alguien
   escribe código.
4. En el editor: mover piezas, patas, spawns, color y alcance; Probar; Guardar.

Funciona (salió la Refinería low-poly), pero cada arena nueva repite los pasos 2 y 3 a mano.

## Qué anda bien hoy

- **Mismo formato y mismas reglas que el juego.** El editor arma los sólidos como `loadArena` (`baseSolid`,
  `objSolids`), gradúa con la misma `color.js` y toma el tamaño del mundo de `size`. Lo que se ve es lo que se juega.
- **Probar en el acto.** ▶ Probar (P) abre el juego encima del lienzo, sin guardar, en "probar arena solo" y desde el
  spawn elegido; Esc vuelve a editar donde estaba. En la prueba tardó ~3 s.
- **Patas que siguen.** Subí `pasarela_medio_izq` de 798 a 704 y las patas se estiraron solas (+93) hasta la pasarela
  de abajo. "Que llegue abajo" (L) hace lo mismo a mano.
- **Alcance en vivo.** Dijkstra sobre las superficies con la curva del salto simple (192) y doble, flechas S/D,
  plataformas que se mueven muestreadas cada 24 px, y la lista "Se llega a todo desde el piso" / "N superficies sin
  llegar, M spawns mal parados". Al elegir algo se ve su envolvente de salto y la distancia (↕) a lo de arriba y abajo.
- **Rápido.** Dibujar el cuadro entero tarda 0,36 ms con las 27 superficies de `prueba_2496` y 3,4 ms con 275 (le
  sumé 60 flotantes y 4 que se mueven): una arena grande no lo complica.
- **Lo básico está**: duplicar (⌘D), espejar (F), copia simétrica (M), flechas de a 1 px (⇧ de a grilla), grilla de
  16/8, imán contra las paredes, deshacer de 300 pasos (incluye la colisión de las piezas), recorridos con puntos,
  velocidad y pausa, y "▶ Animar" para verlos moverse.
- **Arena nueva de 2496.** "＋ Nueva…" pregunta el tamaño (2496 × 1404 por defecto), pone el piso a 140 del borde y
  dos spawns.

## Qué no anda o falta (con ejemplos)

### Simetría y pisos
- **La simetría se rompe sola.** Al subir `pasarela_medio_izq` arrastrándola con la grilla en 16, la `x` pasó de 370 a
  368: el imán busca el borde más cerca de una línea de la grilla aunque el arrastre sea vertical. Su pareja
  (`pasarela_medio_der` en 1691, espejo exacto de 370) no se entera. Hay que corregir a mano las dos.
- **No hay selección múltiple.** Subir un piso entero de `prueba_2496` (dos pasarelas espejadas y sus dos spawns) hoy
  son 4 arrastres más 2 correcciones de `x`, o 4 elecciones y 4 números en el panel. Con un piso más arriba, el
  doble.
- **Los spawns no siguen.** Después de subir la pasarela, el spawn 5 quedó en el aire en 814 ("1 spawns mal
  parados"). Pasa lo mismo con cualquier cosa apoyada.

### Piezas y reuso
- **Arena nueva sin piezas low-poly.** Las pintadas son de cada arena (`pieces` en su JSON) y la paleta muestra sólo
  las de la abierta. Para usar las pasarelas de la Refinería low-poly en `prueba_2496`, Programación copió las 7
  definiciones a mano (~150 renglones). El juego ya las comparte por la ruta (`src` es relativo a `arenas/`): falta
  el atajo en el editor.
- **El kit de la paleta es el 2D del ranger** (13 piezas: plataformas, cajas y decorado). Puse `platforms/float_m`
  al lado de la flotante low-poly: otro estilo (plano, contorno grueso). No hay kit low-poly.
- **Nada se alarga a lo ancho.** Las patas se estiran a lo alto, pero una pasarela más larga es otra imagen.

### Navegación y orden
- A 1440 × 900 la arena entera entra al 43% (el lienzo mide 1110 px) y los rótulos quedan de 10–11 px; en el panel
  chico de la app, al 27%. Al 105% se ve el 42% del ancho. No hay minimapa ni "ir a la selección".
- **No hay lista de objetos.** La única lista es la del alcance, y en la de `prueba_2496` tres renglones dicen
  "flotante" sin forma de distinguirlos. El orden de dibujo es el del JSON, con "Atrás/Adelante" de a un paso. No se puede bloquear la lámina
  ni ocultar una capa para no agarrarla sin querer.
- **El clic en vacío mueve la vista.** Un clic entre las patas de una pasarela (alfa vacío) no la elige y arrastra
  toda la vista.
- **El panel lateral es una sola columna** (selección, color con 10 controles, alcance, piezas, atajos): al hacer
  clic en una pieza de la paleta, abajo, el panel de la selección se actualiza arriba, fuera de la vista.

### Alcance y caminos
- **Dice "se llega a todo" y los bots no llegan.** En `prueba_2496` (medido por Programación): los bots llegan en
  22 de 54 pruebas, nunca al tope de la columna (0 de 6) y pasan 52% del tiempo en el piso, 31% en 1006, 15% en 814,
  2% en 622 y **0% en 430**. Los bots buscan una subida de a un piso (`climbGoal`, hasta 330 px) y suben a una
  plataforma al azar (`pickRoam`); el grafo del editor no lo usan.
- **Muestra sólo la mejor flecha que llega a cada superficie.** No muestra las bajadas, ni cuántos saltos hay desde el
  piso (a las flotantes de 430 son 4: doble, simple, simple y doble), ni lo que depende de un solo camino: el tope de
  la columna (554) se alcanza sólo desde la flotante que se mueve; ninguna pasarela ni flotante quieta llega.
- **La física está copiada.** `PHYS` en `editor.html` repite `FEEL` del juego, y `HANG_ON` está en los dos. El doble
  del editor es 333 ("medido"); las notas dicen 347, y la cuenta con `v0` 1067, `gUp` 2963 y `dbl` 0,9 da 347,6. Con
  14 px de diferencia, un hueco de 340 sale rojo o verde según a quién le creas.

### Cosas del juego que el editor no muestra
- **El HUD.** Con 4 jugadores ocupa ~240 × 75 px arriba a la derecha de la vista de 960 (`HUD2` en `src.html`): en
  una arena de 2496 son ~620 × 195 px del mundo (en las de 1920, ~480 × 150). La flotante que puse en y 176 a la
  derecha quedaría debajo.
- **Las caídas que sacan vida** (560 px o más): en `prueba_2496`, de 430 al piso son 792.
- **Los power-ups.** Salen al azar en cualquier cara de arriba de 60 px o más, a 90 px de las paredes (30% de las
  veces en un spawn). No se puede elegir dónde: ni ponerlos arriba para que la gente suba.
- **Las plataformas que se mueven arrancan todas juntas** (en el punto 0 con su pausa): no hay forma de desfasarlas.

### Probar
- Probar es sólo "arena sola": Esc vuelve al editor, así que no se pueden ver bots ahí. Con bots hay que abrir el juego
  en otra pestaña (⇧ + clic) y mirar a ojo; las métricas (`llegar`, `partidas`) son scripts de Programación.

### Guardar
- **El borrador se borra al abrir otra arena.** Lo no guardado vive en un solo lugar del navegador
  (`arena-editor-wip`). `openArena` lo borra al abrir cualquier otra arena (con `#otra` en la dirección o con el
  menú): si había un borrador de la Refinería y se abre `#prueba_2496`, se pierde sin aviso. Además es por origen:
  `localhost:8772` y `127.0.0.1:8772` tienen borradores distintos.
- **Guardar pisa el archivo** sin dejar la versión anterior, y el deshacer se pierde al recargar.

### Ruido
- Con `HANG_ON` apagado, el panel sigue mostrando "cuelga", "Colgarse de" y "Recorte delante del colgado" en cada
  pieza y sólido. En el juego, ese recorte sólo tapa a los que están colgados (`baked.solid` se dibuja después de
  ellos), así que hoy no hace nada.

## Mejoras, por impacto y esfuerzo

Esfuerzo: **chico** = horas; **mediano** = una sesión; **grande** = varias o con otro rol. "Juego" dice si hace falta
tocar `src.html` (Programación).

| # | Mejora | Impacto | Esfuerzo | Juego |
|---|---|---|---|---|
| E1 | Borrador por arena (`arena-editor-wip:<arena>`) que no se borra al abrir otra, aviso de borradores al abrir, y respaldo al guardar (`serve.py` deja la versión anterior en `arenas/.respaldo/`, ignorada por git) | alto | chico | no |
| E2 | Paleta con las piezas pintadas de todas las arenas: agregar una copia su definición con el mismo `src`. El kit 2D, plegado | alto | chico | no |
| E3 | Simetría viva: modo Espejo (tecla E) donde mover, estirar, borrar o cambiar algo hace lo mismo con su pareja (misma pieza, `flip` opuesto, `x` espejada ±4 px, misma `y`), sin cambiar el formato. Arrastre con eje trabado (⇧) y el imán sin correr la `x` en arrastres verticales. "Revisar simetría" lista lo que no tiene pareja | alto | mediano | no |
| E4 | Selección múltiple (⇧ + clic, recuadro, "todo lo de este piso"); mover, duplicar, espejar y borrar en grupo; los spawns se pegan a su superficie y viajan con ella | alto | mediano | no |
| E5 | Capa "Guías": renglones de pisos desde el piso (192 y 333/347, o a elección), la zona del HUD con 4 jugadores, los márgenes (30 px paredes, 90 px power-ups) y, debajo de cada superficie, la línea de los 560 px que sacan vida | medio-alto | chico | no |
| E6 | Física de un solo lado: el build del editor lee `FEEL` y `HANG_ON` de `src.html` (sólo lee). Sin colgado, se oculta todo lo del colgado | medio | chico | no |
| E7 | Orden y navegación: panel "Objetos" con nombres únicos (`pasarela_medio_izq · 814`), ocultar y bloquear por objeto y por capa (lámina, sólidos, piezas, spawns), reordenar arrastrando, ir a la selección (Z), minimapa, panel lateral en pestañas con la selección siempre a la vista | medio | mediano | no |
| E8 | Alcance 2.0: saltos desde el piso en cada superficie, aviso de "un solo camino", bajadas (y si duelen), "desde acá" (todo lo que se alcanza en 1 y 2 saltos desde lo elegido) y el grafo exportado: cada arista con cómo se hace (salto, doble, viaja, cae) y desde qué `x` despega | alto | mediano | no |
| E9 | Lámina desde el editor: soltar la imagen (la copia `serve.py`), aviso si no mide el `size` | medio | chico | no |
| E10 | Bloqueo y maqueta: piezas grises de cualquier ancho para diseñar sin arte, y "Exportar maqueta" (PNG del tamaño de la arena + máscara de cada pieza) para que Arte la pinte | alto | mediano | no |
| E11 | Recortar piezas desde el editor: la zona de cada pieza dibujada sobre la lámina (o tomada del bloqueo), y `serve.py` corre `capas.py` con esas zonas en vez de `LEFT` escrito a mano | alto si seguimos con "lámina primero" | grande | no |
| J1 | Bots que siguen el grafo: el cálculo del alcance pasa a `alcance.js`, compartido como `color.js` (el build lo mete en el juego y en el editor); el bot arma el camino entero y lo sigue arista por arista | alto | mediano-grande | sí |
| J2 | Lugares de power-ups en el JSON (opcionales, con peso; sin ellos, al azar como hoy) y en el editor como los spawns | medio-alto | chico + chico | sí |
| J3 | Tramos: piezas pintadas que se alargan a lo ancho (la franja del medio se repite), como las patas a lo alto | medio-alto | mediano + Arte | sí |
| J4 | Fase de las que se mueven (`move.phase`), para ascensores alternados | medio | chico | sí |
| J5 | Probar con bots desde el editor y mapa de uso: partidas aceleradas en el iframe y el % de tiempo por superficie pintado sobre el lienzo | alto para afinar | mediano | sí (expone lo que hoy hace `pruebas.js`) |

## Primera tanda recomendada

**E1, E2, E3, E4, E5 y E6.** Todo en `editor.html`, `serve.py` y `editor/build.py`; no cambia el formato de las
arenas ni toca el juego. Criterios para darla por buena, probados en `prueba_2496` sin guardar:

- Subir el piso del medio 96 px con las dos pasarelas y sus dos spawns: **un recuadro y un arrastre** (hoy 4 arrastres
  y 2 correcciones). "Revisar simetría" da 0 sin pareja antes y después.
- Arena nueva de 2496 con las pasarelas y la flotante de la Refinería low-poly **desde la paleta**, sin tocar el JSON.
- Abrir `#refineria_lowpoly` con un borrador de `prueba_2496` sin guardar: el borrador sigue ahí. Guardar deja la
  versión anterior en `arenas/.respaldo/`.
- Con las guías prendidas se ven los renglones de pisos, el rectángulo del HUD y, bajo cada superficie, dónde una
  caída saca vida. El doble salto del editor es el del juego (el número sale de `FEEL`).
- Sin `HANG_ON`, ningún control del colgado en el panel.

**Tanda 2:** E8 (alcance 2.0 y el grafo exportado) para que Programación haga J1 (bots), más E7 (navegación) y J2
(power-ups). Mientras, Arte hace el kit low-poly. **Tanda 3:** J3 (tramos), E10 (bloqueo y maqueta) o E11 (recortar),
según la ruta de arte que elija Pablo, y J5.

## Una decisión de fondo: con qué se pintan las arenas grandes

Hoy el orden es **lámina primero**: imagen → limpieza → colisión calcada → recorte en capas. Da el look de la imagen
de Pablo, pero el diseño de juego queda atado a lo que pintó el modelo, y mover una pasarela en la pintura salió caro
(pedirle "subilas" no anduvo; se hizo a mano, con un relleno de US$0,12). Para arenas grandes propongo invertirlo:

- **Kit de piezas (recomendado para iterar).** Fondo sin pasarelas + piezas low-poly con alfa (pasarelas en tramos,
  patas, flotantes, plataforma que se mueve, bloques). Se arma y se cambia en el editor sin gastar; las piezas sirven
  para todas las arenas. Necesita A1 y A2 de Arte, y J3 para los tramos.
- **Bloqueo y maqueta pintada (para una arena "de vidriera").** Se diseña con piezas grises (E10), se prueba con bots,
  y recién entonces Arte pinta la maqueta. Las zonas de cada pieza salen del bloqueo, así que el recorte (E11) no
  necesita código a mano.
- **Lámina primero (como hoy).** Sirve si Pablo trae una imagen que quiere tal cual; necesita E11 para no escribir
  `LEFT` a mano cada vez.

## Qué necesito de Arte

- **A1. Kit low-poly de escenario** con alfa (GPT Image 2.5 Sunburst, US$0,17 la hoja, 2 hojas por pedido), del mismo
  estilo que la Refinería low-poly (vista 3/4, luz de arriba a la izquierda), a 1 px = 1 px del juego:
  pasarela en tramos (punta izquierda, medio que se repite sin costura, punta derecha) con su franja de patas;
  columnas o patas sueltas que se estiran; flotantes de ~200, ~300 y ~450 px; una plataforma de ascensor; un bloque o
  pared; barandas y decorado suelto de fondo (tanques, chimeneas, caños). Las medidas exactas (losa, línea de los
  pies, franja de patas) las paso yo cuando Pablo elija la ruta. Estimado: 4 asset × 2 hojas = ~US$1,36, siempre con
  dry-run y PEDIDO por el Director.
- **A2. Fondos de 2496 × 1404 sin pasarelas** (lo lejano y el piso), 2 o 3 opciones. A 2K 16:9 el modelo devuelve
  2752 × 1536: alcanza sin agrandar.
- **A3. (Sólo con "bloqueo y maqueta")** pintar la maqueta que exporte el editor (edición, ~US$0,12 por pedido con
  Nano Banana 2.1, como `plate_bare`).

## Qué necesito de Programación

- **J1, los bots con el grafo** (lo más importante para las arenas grandes). Propuesta: `prototypes/arena/alcance.js`
  con `buildEnv`, `link` y `reach` sacados del editor (lo escribo yo en la tanda 2), que `build.py` mete en el juego y
  en el editor como hoy `color.js`. En el juego: al cargar la arena se arma el grafo; el bot pide el camino a la
  superficie de su objetivo y lo sigue arista por arista (caminar hasta la `x` de despegue, saltar, doble en la altura
  que diga la arista, atravesar hacia abajo). Meta en `prueba_2496`: `llegar` ≥ 45 de 54 (hoy 22) y más de 5% del
  tiempo en 430 (hoy 0%), sin trabados.
- **J2, J3 y J4**: los campos nuevos del JSON (`pickups`, tramos, `move.phase`), primero en el juego con un valor por
  defecto que deja las arenas de hoy iguales; después los pongo en el editor.
- **J5**: exponer en el juego (no sólo en `pruebas.js`) una corrida de bots acelerada que devuelva el % de tiempo por
  superficie, para pintarla en el editor.
- Confirmar el doble salto medido (333 o 347) y si el recorte "delante del colgado" sirve para algo sin `HANG_ON`.

## Cómo repartir el trabajo sin pisarse

Hoy Programación es dueña de `editor/` y de `arenas/`. Propongo:

- **Editor de niveles** toma `prototypes/arena/editor/` entero (`editor.html`, `serve.py`, `build.py`, `capas.py`,
  `flotante.py`, `dist/`) y las arenas nuevas de `prototypes/arena/arenas/` (las que ya existen siguen de quien las
  hizo hasta que se reemplacen; `prueba_2496` es de Programación).
- **Programación** sigue con `src.html`, el `build.py` del juego, `dist/`, `color.js` y el juego en general.
- **El contrato es el formato del JSON**, escrito en `prototypes/arena/arenas/FORMATO.md` (lo escribo yo, lo revisa
  Programación). Un campo nuevo entra primero en el juego, con un valor por defecto que no cambia las arenas de hoy, y
  después en el editor.
- **Los módulos compartidos** (`color.js` hoy; `alcance.js` mañana) los toca uno solo por vez: `alcance.js` lo escribo
  yo; si Programación cambia la física, me avisa y el build del editor la lee del juego (E6).
- `editor/build.py` importa `export_kit` y `color_lut` del `build.py` del juego: si Programación los cambia, me avisa.
- La tanda 1 no toca ningún archivo de Programación, así que puede ir en paralelo con lo que esté haciendo.

Si Pablo prefiere que Programación siga dueña de `editor/`, la alternativa es que yo escriba el detalle de cada
mejora y las pruebas, y Programación las haga; es más lento porque el editor pasa a competir con el juego.

## Para que decida Pablo

1. ¿La tanda 1 va como está?
2. ¿`editor/` pasa a Editor de niveles?
3. ¿Con qué se pintan las arenas grandes: kit de piezas (recomendado), bloqueo y maqueta pintada, o lámina primero?
4. ¿El clic en vacío pasa a ser recuadro de selección (y la vista se mueve con espacio, la rueda o el botón derecho),
   o queda como hoy?
5. ¿Power-ups en lugares elegidos (J2) o al azar como hoy?
