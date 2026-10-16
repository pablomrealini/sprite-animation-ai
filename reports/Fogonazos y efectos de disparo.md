# Dibujá el fogonazo, pegalo al cañón y dejá las chispas al código

Los seis juegos de referencia dibujan el fogonazo; ninguno lo arma con partículas. Metal Slug lo dibuja dentro del torso, y Hard Corps, Cuphead, Blazing Chrome, Broforce y Enter the Gungeon lo ponen como un objeto aparte en la boca. Todos usan de 1 a 4 dibujos que duran de 2 a 12 frames. Lo que va por código, en los que lo tienen, es lo que rodea al dibujo: las chispas con gravedad de Broforce, los puntos que se enfrían de Blazing Chrome, la nube de puntos que sigue a la bala en Hard Corps, el flash blanco del enemigo en Gungeon. Por eso, a la pregunta "partículas o sprites", la respuesta es la mezcla: **el núcleo del fogonazo y la forma del impacto, dibujados; el resto, código**. Pero el fogonazo del ranger no sale raro por ser código. **Sale raro por tres cosas que se arreglan sin cambiar de técnica.** El juego lo deja fijo en el mundo durante 0,06 s, así que corriendo queda 15 px atrás del cañón y cayendo se despega hasta 70 px. El frame de disparo del clip trae el destello del video cortado justo delante de la boca: una "V" cian con un halo lila que aparece en cada tiro. Y es chico: 0,12–0,16 alturas de largo, menos de lo que mide el arma, contra 0,39–0,40 en Metal Slug y Hard Corps, los más parecidos. La prueba con GPT Image 2.5 costó US$0,46 por dos hojas con dos opciones cada una. Los impactos salieron usables de entrada: dos animaciones de 4 frames que salpican hacia el tirador. Los fogonazos salieron con púas hacia atrás, que los hacen parecer dardos. Todo se compara en `prototypes/fx_lab/`, a velocidad real y en cámara lenta.

Cómo leer los números. **H** es la altura del personaje parado en su propio juego. El ranger mide 128 px en el atlas y el juego lo dibuja al 80%, así que H = 102 px del juego (77 px de pantalla, con la cámara al 75%). Su blaster mide 34 px del atlas, 0,27 H (medición propia). **f** es un frame a 60 Hz, 16,7 ms. Las marcas siguen la convención del equipo: **medición propia** es un valor medido sobre video cuadro a cuadro o sobre un rip; **conteo propio**, frames contados; **cálculo propio**, aritmética sobre valores citados; **s/d**, que no se encontró. Las notas completas, con la fuente de cada número, están en `research_notes/Fogonazos y efectos de disparo/`. Los sprite sheets se leyeron de The Spriters Resource a través de copias de Wayback Machine, porque el sitio les da 403 a los bots, y lo que no estaba ahí se midió en video a 60 fps. Quedaron en `refs/`, que no va al repo.

## El de hoy sale raro por dónde está, no por cómo está hecho

**El fogonazo queda en el mundo y el ranger se le va.** `fire()` crea el fogonazo en la boca del frame que está en pantalla, y `drawFlash` lo dibuja en ese punto del mundo durante 0,06 s, unos 3–4 frames. Parado no se nota: la boca del frame de disparo está a 1–2 px de la del frame de reposo. Moviéndose, sí. Con el feel "reporte" del prototipo (300 px/s, v0 = 1067, gravedad 2963 al subir y 4898 al bajar, terminal 1400), esto es lo que se corre el fogonazo respecto de la boca en cada frame (cálculo propio, en px del juego):

| Situación | Frame 1 | Frame 2 | Frame 3 | Frame 4 |
|---|---|---|---|---|
| Corriendo a 300 px/s | 0 | 5 atrás | 10 atrás | 15 atrás (0,15 H) |
| Despegando (sube a 1067 px/s) | 0 | 17 abajo | 33 abajo | 48 abajo (0,47 H) |
| Cayendo a 700 px/s | 0 | 13 arriba | 27 arriba | 43 arriba |
| Cayendo a la terminal | 0 | 23 arriba | 47 arriba | 70 arriba (0,68 H) |

Saltando y disparando, el fogonazo deja una estela vertical que se separa del arma. Ninguna de las referencias hace esto (ver "Pegado a la boca").

**El frame de disparo trae medio destello del video.** El modelo de video dibujó un destello en un frame de cada disparo. `build.py` lo detecta (el último valor de cada frame) y el juego arranca cada ciclo de disparo en ese frame, para que el destello coincida con el tiro. Pero la limpieza previa (`clean` con `cut_muzzle`) corta todo lo que está delante de la boca. Del destello quedan 2–3 px de una "V" cian pegada a la lente, más un halo lila semitransparente de 37 px de alto (0,29 H) por arriba y por abajo del cañón (medición propia sobre `shoot` 2/4). Aparece en `shoot` (2/4), `shoot2h` (2/5) y `crouch_shoot` (1/5). `jump_shoot` lo esquiva porque el juego elige un frame sin destello para el aire. Encima de eso, `drawFlash` suma su halo.

**Es chico y finito.** El halo de `drawFlash` mide 12–15 px hacia adelante y 11–14 px de alto, y la punta, 11–16 px de largo por 3–5 de ancho (cálculo propio sobre el código, a S.char 0,8). En total son **0,12–0,16 H, entre 0,4 y 0,6 veces el arma**. Es el único de la comparación más chico que el arma que lo dispara.

**Y sale 3 px arriba de la lente.** `drawSprite` dibuja al ranger `FOOT_SINK` px hundido en el piso (3 px, el contorno del kit de plataformas), pero `fire()` calcula la boca sin ese hundido. La bala y el fogonazo nacían 3 px por encima del centro de la lente (medición propia sobre el código). La sesión de saltos lo corrigió el mismo día con `muzzleAt`, que hace la misma cuenta que `drawSprite`.

## Los seis dibujan el fogonazo

| Juego | Cómo está hecho | Dibujos | Cuánto dura | Tamaño | Respecto del arma | ¿Varía? | Anclaje | Brillo |
|---|---|---|---|---|---|---|---|---|
| Metal Slug, pistola | Dentro del frame del torso | 3: rojo oscuro → núcleo blanco y amarillo → hilacha que se despega (conteo propio sobre el [sheet de Marco](https://web.archive.org/web/20230512095229im_/https://www.spriters-resource.com/resources/sheets/11/11225.png)) | 6 f, 2 por dibujo (medición propia, 4 tiros, [video](https://www.youtube.com/watch?v=_iOu1ozwk5s&t=9s)) | 0,39 H adelante; 0,55 H hacia arriba | 1,3–1,7× | No | Va con el torso | Colores al tope de la paleta; el Neo Geo no tiene semitransparencia por sprite ([NeoGeoDev](https://wiki.neogeodev.org/index.php/Sprites)) |
| Metal Slug, HMG | Dentro del torso | 2 formas: bola blanca y lengua naranja | Continuo mientras dispara: cambia cada 2 f ([video](https://www.youtube.com/watch?v=_iOu1ozwk5s&t=45s)) | 0,61 H | ≈1,15× | Alterna las dos | Con el torso | Ídem |
| Contra: Hard Corps | Objeto aparte, centrado en la boca (inferencia fuerte: el sheet de Fang los trae sueltos) | 4: cruz → estrella → anillo → chispas ([sheet de Fang](https://web.archive.org/web/20230802021249im_/https://www.spriters-resource.com/resources/sheets/25/27275.png?updated=1460955759)) | 4 f, 1 por dibujo; a una bala cada 4 f queda en loop ([video](https://www.youtube.com/watch?v=GCf_A9AXy_k&t=424s)) | 0,40 H (el anillo) | ≈0,5× el rifle | No: los mismos 4 dibujos en las 8 direcciones y para dos personajes | En la boca de cada pose | 3 colores planos de la paleta del jugador |
| Cuphead | Objeto aparte por tiro ([AbstractLevelWeapon.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/AbstractLevelWeapon.cs)) | 4: disco, anillo, salpicadura, estrella | 12 f (0,2 s, el clip va a 20 fps, [anim](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/AnimationClip/anim_weapon_peashot_basic_flash_a.anim)); a 7,5 tiros/s se encima 1–2 | 0,21–0,44 H | 1,1–2× el guante | Rotación 0–360° y espejo X/Y al azar ([Effect.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/Effect.cs)) | Colgado del personaje en el piso; suelto en el aire | Alfa normal con el halo pintado en la textura |
| Blazing Chrome | Un dibujo por tiro | 1, con al menos 2 variantes (estrella y asterisco) | 2 f (conteo propio, 21 tiros, [video](https://www.youtube.com/watch?v=yHNwfRtqPR4)) | 0,6–0,7 H | 1,3–1,6× | Al azar entre las variantes (inferencia, n = 9) | Sigue al arma (medición propia, en un salto) | Opaco; además el arma se pinta "iluminada" 3 f |
| Broforce | Puff aparte, más un flash dibujado en el sprite del arma ([docs](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/EffectsController-Documentation.xml), generadas por IA y cruzadas con mods) | Puff: disco y elipse; arma: 3 dibujos | Puff en 5 de cada 6 f a 10 tiros/s: 3 de disco, 2 de elipse ([video](https://www.youtube.com/watch?v=c4eSis4wXKc&t=61s)) | Puff 0,73 × 0,56 H; el del arma, 0,3 H | ≈0,9× (cálculo propio, arma de 16 px de arte) | Gira con la dispersión de la bala, ±3° | Puff colgado del personaje; glow fijo en el mundo | Opaco, más una distorsión de calor |
| Enter the Gungeon | Flipbook aparte por arma ([Alexandria](https://github.com/Nevernamed22/Alexandria/blob/main/VisualAPI/VFXBuilder.cs)) | ≈4 (inferencia por el ritmo 3-2-2-3) | 10 f: 3 de cono blanco, 4 de estallido naranja, 3 de brasas ([video](https://www.youtube.com/watch?v=XKjPjhZgqW4&t=217s)) | 0,75–0,9 H de largo | 1,6–1,9× | No vi variantes en 2 tiros; gira con el apuntado | Colgado del cañón (`barrelOffset`, `attached`) | Recorte opaco, con emisivo, bloom y luz (inferencia por los shaders de los mods) |
| **Ranger hoy** | Código: halo y cruz | — | 0,06 s ≈ 3–4 f | 0,12–0,16 H | 0,4–0,6× | Largo de la punta al azar | **Fijo en el mundo** | Suma de color (`lighter`) |

**Duración: un núcleo corto y blanco, y a veces una cola que se enfría.** Blazing Chrome muestra un solo dibujo 2 frames; Hard Corps cambia de dibujo cada frame durante 4; Broforce sostiene el disco 3. Metal Slug (6 f), Gungeon (10 f, 3 de núcleo blanco) y Cuphead (12 f) agregan una cola apagada después del núcleo. Vlambeer va al extremo: en Nuclear Throne, la bala es redonda en su primer frame y eso hace de fogonazo ([Rock Paper Shotgun](https://web.archive.org/web/2014/http://www.rockpapershotgun.com/2013/10/21/interview-jan-willem-nijman-on-nuclear-thrones-feel/)). Un fogonazo real dura 1–2 ms ([arXiv](https://arxiv.org/pdf/1410.6025)), así que un solo frame ya lo exagera 8–16 veces (cálculo propio): cuánto dura es una decisión de lectura, no de realismo. A la cadencia del ranger, 12 tiros/s, cae un tiro cada 5 frames. Un fogonazo de más de 5 frames se encima con el siguiente. Cuphead lo acepta (1–2 encimados). Metal Slug y Hard Corps lo convierten en un loop continuo mientras se mantiene el gatillo, y Broforce deja un solo frame apagado de cada 6.

**Tamaño: entre 1 y 2 veces el arma.** Los más parecidos al ranger son Metal Slug y Hard Corps, con 0,39–0,40 H para el arma chica y 0,61 H para la HMG. Broforce, Gungeon y Blazing Chrome van más grandes (0,6–0,9 H), pero sus personajes miden 19–52 px y el fogonazo tiene que leerse a esa escala. Medido contra el arma, casi todos están entre 1,1 y 2 veces su largo. Para el blaster del ranger (0,27 H), eso da 0,3–0,55 H; las 0,39 H de la pistola de Metal Slug son 40 px del juego.

**Variar por disparo no es la regla.** Metal Slug con la pistola, Hard Corps y Gungeon repiten siempre la misma secuencia. Los que varían lo hacen barato: Metal Slug alterna dos formas en la HMG, Blazing Chrome elige al azar entre dos dibujos, Cuphead gira y espeja un dibujo radial, y Broforce lo gira con la dispersión de la bala. Variar importa más cuanto más dura el fogonazo y cuanto más rápido dispara el arma. Para estirar pocos dibujos, alcanza con girarlos ±10–20°, escalarlos ×0,85–1,15 y espejarlos en vertical al azar ([notas, C.4](../research_notes/Fogonazos%20y%20efectos%20de%20disparo/broforce_gungeon_tecnica.md)).

## Pegado a la boca

**Ninguna referencia deja el fogonazo atrás cuando el personaje se mueve.** Metal Slug lo resuelve por construcción: el fogonazo es parte del dibujo del torso. Usa sus mismos 13–15 colores y cambia de color cuando Marco parpadea con la paleta de invencibilidad (medición propia). Gungeon lo cuelga del cañón y Broforce del personaje, aunque el glow de Broforce queda en el mundo. Blazing Chrome lo mueve con el arma: entre los dos frames de un fogonazo, con Mavra saltando, se desplazó lo mismo que ella (medición propia). Cuphead es el caso intermedio. El fogonazo nace en la boca de la pose y se cuelga del personaje si está en el piso, también corriendo. Se suelta en el aire o al darse vuelta ([WeaponSparkEffect.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/WeaponSparkEffect.cs)), y ahí 12 frames de desfase se notan poco porque el dibujo es radial.

Broforce y Gungeon hacen explícita una regla: **lo que es del arma sigue a la boca; lo que es del mundo se suelta**. Del mundo son el humo, las chispas, los casquillos y el glow. El ranger no tiene esqueleto, pero ya tiene lo necesario: un punto de boca por frame, que `build.py` mide en cada animación. Basta con leerlo cada vez que se dibuja el fogonazo, no sólo al disparar. Con un fogonazo de 1–2 frames, como el de Blazing Chrome, el anclaje casi no importa; con 4 o más, sí.

## Brillo sin suma de color

**Ninguna de las seis usa blending aditivo en el disparo común.** Neo Geo y Genesis no lo tienen. Metal Slug y Hard Corps sacan el brillo de un núcleo blanco con 1–2 colores saturados de la propia paleta, de formas que cambian cada frame y de un contraste en el tiempo: el primer dibujo del fogonazo de la pistola de Metal Slug es rojo oscuro, y recién el segundo es blanco. Blazing Chrome copia esa estética a propósito: su director de arte dice que mantuvo "limitations on colours and resolution" ([MCV/UK](https://mcvuk.com/?p=223533)). Cuphead usa alfa normal con un halo suave pintado en la textura: el 42–70% de los píxeles del fogonazo son semitransparentes (medición propia). Los modos de mezcla quedan para el EX (hard light) y el parry (screen). Gungeon dibuja recortes opacos con emisivo, bloom y luz puntual (inferencia por los shaders que usan los mods), y Broforce agrega una distorsión de calor, no luz.

En canvas, `lighter` suma los colores y nunca oscurece ([MDN](https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/globalCompositeOperation)). Sobre la noche violeta del ranger brilla, pero sobre un fondo claro se lava a blanco y pierde la forma; en el fx_lab se ve con "Fondo: claro". La salida estándar es un núcleo opaco con alfa normal, que se lee sobre cualquier fondo, y encima un halo aparte con `lighter` y alfa baja.

## Impactos: una forma corta, y a veces puntos por código

| Juego | Contra qué | Cómo está hecho | Duración | Tamaño | Dirección | Reacción del blanco |
|---|---|---|---|---|---|---|
| Metal Slug, pistola | Roca | Secuencia dibujada: domo → huevo blanco → llama vertical → chispas, dibujadas dentro de cada cuadro | ≈10 f (medición propia) | hasta 0,68 H | No apunta a la bala (1 caso) | — |
| Metal Slug, HMG | Blindado | Chispa redonda dibujada que se deshace en puntos | 12–14 f | 0,29 H | Radial | Tinte naranja de paleta, en bloques de 2 f |
| Hard Corps, Vulcan Laser | Enemigo | Sin chispa: la bala sigue de largo como una nube de puntos de 1 px ([video](https://www.youtube.com/watch?v=GCf_A9AXy_k&t=418s)) | 4–5 f | ≈0,37 H | Sigue la dirección de la bala | Ciclo de paleta cada frame |
| Cuphead | Enemigo o pared, igual (sólo cambia el sonido) | La bala pasa a su animación de muerte, dibujada ([anim](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/AnimationClip/anim_peashot_basic_die.anim)) | 15 f (0,25 s) | 0,26 → 1,1 H | Radial | Tinte cian de 0,04 s en pulsos ([HitFlash.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/HitFlash.cs)) |
| Blazing Chrome | Enemigo | Medialuna dibujada, más decenas de puntos de 1 px que se enfrían de blanco a rojo | 6 f la medialuna; 10–15 f los puntos | 0,35–0,4 H | La medialuna abre hacia el tirador y los puntos salen hacia atrás | Cambio de paleta de 3 f |
| Broforce | Pared | Pop dibujado: disco blanco sólido 2 f, después anillo amarillo que se abre 3–4 f. Más 10 chispas por código, con gravedad, a lo largo de la normal y de amarillo a rojo | ≈6 f el pop | 0,7 → 0,9 H | Las chispas, por la normal | — |
| Enter the Gungeon | Pared horizontal, pared vertical, enemigo, bala que se agota | Un efecto distinto para cada caso ([GungeonCraft](https://github.com/pcrain/GungeonCraft/blob/master/src/Extensions.cs)) | s/d | s/d | Orientado a la normal (inferencia) | 1 f de silueta blanca y 1 f al 50%, por código |
| **Ranger hoy** | Blanco y bloque | Código: un círculo con suma que se abre, más 11 cuadrados (16 a dos manos) hacia todos lados, con gravedad | 0,09 s el círculo; 0,38 s los cuadrados | 0,18–0,53 H de diámetro | Radial | Tinte cian de 0,08 s en los blancos |

**Hay tres ideas para robar.** La primera: que el primer frame del golpe sea blanco puro, como el disco de Broforce, la silueta de Gungeon o el golpe de Nuclear Throne, que "always starts with a frame white" ([Rock Paper Shotgun](https://web.archive.org/web/2014/http://www.rockpapershotgun.com/2013/10/21/interview-jan-willem-nijman-on-nuclear-thrones-feel/)). Para un blaster cian, la rampa sería blanco → cian → azul. La segunda es la dirección. Contra un enemigo, el impacto entra (Hard Corps; Capcom explica lo mismo para Street Fighter 6, [EventHubs](https://eventhubs.com/news/2023/jul/18/capcom-early-sf6-drive-parry)). Contra una pared, rebota hacia el tirador o por la normal (Blazing Chrome, Broforce). Los cuadrados del ranger hoy salen para todos lados. La tercera es que casi todos suman una reacción del blanco que no es un efecto aparte: un tinte o un cambio de paleta de 2–4 frames (Metal Slug, Hard Corps, Cuphead, Blazing Chrome) o una silueta blanca (Gungeon). El ranger ya la tiene en los blancos de tiro. El hit stop, el congelado de un instante al pegar, viene de los juegos de pelea ([critpoints](https://critpoints.net/2017/05/17/hitstophitfreezehitlaghitpausehitshit/)). Vlambeer lo usa en 10–20 ms por golpe, pero a 12 tiros/s congelaría el juego todo el tiempo.

## Cuándo conviene cada técnica

| | (a) Código | (b) Sprites (IA o a mano) | (c) Mezcla |
|---|---|---|---|
| Silueta y estilo | Formas genéricas: el estilo sale del color, el tamaño y el movimiento | Total: cada frame tiene la forma que se quiera, con el contorno y los colores planos del personaje | La forma la da el dibujo |
| Variedad | Gratis: cada tiro sale distinto | Cuesta arte; se estira con giro, escala y espejo | Gratis en la parte de código |
| Física | Gravedad, rebote, normal, color que se enfría | Ninguna: el flipbook es fijo | La que haga falta |
| Costo | Ajustar código | Una hoja por efecto (US$0,23 por dos opciones con GPT Image) y elegir | Una hoja más el código |
| Sobre fondo claro | Si suma color, se lava | Opaco: se lee siempre | Núcleo opaco, halo sumado |
| Quién lo usa | El ranger hoy; Hard Corps, sólo en los puntos del impacto | Metal Slug, Hard Corps y Cuphead, para todo | Blazing Chrome, Broforce, Gungeon |
| Va bien para | Chispas, polvo, casquillos, halos, el flash del blanco: lo que tiene física o cambia en cada tiro | El núcleo del fogonazo y la forma del impacto: lo que tiene que parecer del mismo mundo que el personaje | El caso general |

**Para este pipeline hay un argumento más a favor del dibujo.** El ranger sale de un video de IA con contorno negro grueso y colores planos, y los fondos de juego salen de GPT Image con el mismo estilo. Un fogonazo hecho de degradés radiales y sumas de color es de otro estilo, y se nota más cuanto más grande se lo haga. Una hoja dibujada con el concept del ranger como referencia sale con el mismo lenguaje: formas planas y un borde que las separa del fondo.

## La prueba: dos hojas de GPT Image y un banco de efectos

**Las hojas.** `spritepipe gen-images` con GPT Image 2.5 Sunburst por fal, el único modelo con alfa nativo, con `poses/ranger_concept.png` como guía de estilo. Se pidieron dos hojas con dos opciones cada una, por US$0,46 (`backgrounds/ranger_fx/gen.toml`; comparación en `compare.html`). Las cuatro imágenes salieron con alfa: el máximo es 254, no 255, y el build lo lleva a 255. El post separó las piezas bien y en orden, 6 en los fogonazos y 8 en los impactos. Para eso el prompt pide que cada pieza sea una sola mancha, sin chispas sueltas: el post separa las piezas por componentes conexos, y una chispa a más de 2 px quedaría como una pieza aparte.

- **Impactos: usables.** Las dos opciones traen dos animaciones de 4 frames, en escala y estilo coherentes: estrella, salpicadura de 6–8 púas hacia el tirador, medialuna y medialuna fina. Es casi la medialuna direccional de Blazing Chrome.
- **Fogonazos: a medias.** Salieron las 3 formas del primer frame y el segundo frame de cada una, pero el modelo hizo las púas laterales inclinadas hacia atrás, como las aletas de una flecha. A tamaño de juego (40 px) se lee como un estallido cian. En la lupa, en cambio, parece un dardo que sale volando. La opción 1 trae además un anillo en la base que cae sobre la lente del arma. Una segunda tanda (US$0,23 por dos opciones) tendría que pedir un abanico que se abra hacia adelante, con las púas hacia adelante y afuera, nunca hacia atrás, y el primer frame casi todo blanco. Otra posibilidad son formas radiales como las de Hard Corps y Cuphead: sirven para cualquier ángulo y se pueden girar al azar.

**El banco de efectos** (`prototypes/fx_lab/`) es una página aparte que no toca el juego:

```bash
uv run --project pipeline python prototypes/fx_lab/build.py
```

Usa el mismo atlas y la misma medición de boca que el juego, copia `drawFlash` sin cambios, y achica las piezas de `backgrounds/ranger_fx` a un tercio, con el ancla medida. El ranger dispara en loop contra un bloque con la cadencia del juego.

- **Técnica** (teclas 1, 2 y 3): código, sprites o mezcla.
- **Vista:** una técnica con lupa ×4 sobre la boca y el impacto, o las tres en fila.
- **Tiempo:** velocidad de 1× a ⅒×, pausa y paso de a un frame.
- **Pose:** una mano, dos manos, agachado, corriendo o saltando.
- **Juego:** ancla ("queda donde salió", como el juego, o "sigue al arma"), destello del clip (queda o sacado), fondo (noche, gris o claro) y sacudón.
- **Sprites:** hoja de cada efecto, color normal o sumado, variación (alterna, azar con giro y espejo, o fija), frames de cada dibujo y tamaños.
- **Mezcla:** las chispas del impacto salen hacia atrás, como en Blazing Chrome, o siguen la bala, como en Hard Corps.

Los valores por defecto reproducen el juego. Para verlo, abrí `prototypes/fx_lab/dist/index.html` con doble clic, o levantá `fx-lab` desde `.claude/launch.json`.

## Qué conviene para el ranger

Todo esto es una propuesta para probar en el fx_lab, no un resultado medido:

1. **Pegar el fogonazo a la boca**, con cualquier técnica: la posición se lee del frame que está en pantalla cada vez que se dibuja. Es el arreglo que más se nota corriendo y saltando.
2. **Sacar el destello del clip.** Lo más rápido es cambiar el frame marcado por el anterior del mismo clip, como hace el fx_lab con "Sacado". Lo prolijo es correr `remove_flash` sobre los clips de disparo del ranger, como en el comando, que además exporta la boca por frame. Falta probar que funcione después de la limpieza previa.
3. **Fogonazo (mezcla).** El núcleo dibujado y opaco, con 2 dibujos de 2 frames cada uno, 4 frames en total. A 12 tiros/s eso deja un frame apagado entre tiros, como Broforce. Tamaño: 0,35–0,4 H, unos 36–40 px del juego, casi 1,5 veces el arma. Tres formas que se turnen o salgan al azar, con giro de ±12° y escala ×0,9–1,1, y ×1,3 a dos manos. Encima, por código, un halo sumado de alfa baja que no pase de la boca hacia atrás, y 2–3 chispas finas hacia adelante.
4. **Impacto (mezcla).** La animación de 4 frames a 2 frames cada uno (0,13 s), de 0,43 H, alternando las dos filas. Encima, por código, un destello blanco sumado de 0,06 s y 6–10 puntos hacia el tirador; contra los blancos, el tinte que ya tiene.
5. **Antes de decidir el color**, probarlo con "Fondo: claro".

## La elegida

Pablo eligió la mezcla en el fx_lab (botón "La elegida"), con un fogonazo más chico y más largo que el propuesto:

- **Fogonazo:** la hoja 2, con las 3 formas turnándose 1-2-3. El primer dibujo dura 2 frames y el segundo 3: son 83 ms, el tiempo entre dos tiros a 12/s, así que mientras se dispara queda en loop, como la HMG de Metal Slug o el fogonazo de Hard Corps. Mide 26 px, 0,25 H, casi exactamente el largo del arma. Suma un halo con suma de color y tres chispas finas.
- **Impacto:** la hoja 1, con las dos filas turnándose. Son 4 dibujos de 2 frames (133 ms) de 50 px de alto (0,49 H), más un destello de 0,06 s y 6 chispas hacia el tirador (10 a dos manos).
- **Color normal** para los dibujos. La suma de color queda sólo para el halo, el destello y las chispas.
- **Pegado a la boca** del frame en pantalla, con los 3 px del hundido, y **sin el destello del clip.**

Cómo pasarlo al juego está en [`prototypes/fx_lab/README.md`](../prototypes/fx_lab/README.md): qué agregar a `prototypes/build.py` (la hoja elegida de cada efecto, su tamaño y el ancla de cada pieza) y qué cambiar en `fire()`, `impact()`, `drawFlash` y `render()`. Los cambios se probaron sobre una copia del juego del 2026-10-16, que quedó en `prototypes/fx_lab/dist/juego/` para verla andando.

## Conclusión

La investigación le saca peso a la pregunta. Que el fogonazo del ranger sea de código no es lo que lo hace raro: lo es que no siga al arma, que se le sume medio destello del video y que sea más chico que el arma. Arreglado eso, la técnica es una cuestión de estilo, y ahí las referencias coinciden más de lo esperable. El núcleo del efecto es un dibujo corto, de 1 a 4 dibujos, con un primer frame blanco. Lo que tiene física o cambia en cada tiro va por código. El brillo sale del contraste, no de sumar color. Para un pipeline que ya dibuja al personaje y los fondos con IA, la mezcla es la opción natural: la hoja de impactos salió buena en el primer intento por US$0,23. La de fogonazos sirve a 26 px, aunque en cámara lenta las púas hacia atrás la hacen parecer un dardo; otra tanda con las púas hacia adelante cuesta lo mismo.
