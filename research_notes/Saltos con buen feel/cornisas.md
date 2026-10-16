# Cornisas: agarre (ledge grab) y trepada (ledge climb) en Celeste, Hollow Knight/Silksong, Prince of Persia, Strider, Shinobi y referencias modernas

Convenciones de estas notas:
- **H** = altura parado del personaje en su propio juego. Conversión "a 128 px" = el mismo valor para un personaje de 128 px de alto (escala del atlas del ranger). Para pasar a pantalla del prototipo (dibujado al 80 %, ≈102 px), multiplicá por 0,8.
- Tiempos en segundos y en frames a 60 Hz ("f"). Prince of Persia corre a 12 fps de juego (1 frame PoP = 5 f a 60 Hz) y Spelunky Classic a 30 fps (1 frame = 2 f).
- Etiquetas: **[código]** = leído en código fuente público; **[dev]** = declaración de desarrolladores; **[comunidad]** = wiki, foro o guía de fans; **[resumen de búsqueda]** = solo vi el fragmento del buscador porque la página devolvió 403/402. Trabajo propio: **medición propia**, **conteo propio**, **cálculo propio**. s/d = sin datos.
- Alturas de referencia: Celeste H = 16 px visibles (medición propia de la sesión anterior) y hitbox de 11 px ([Player.cs L263–266](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L263-L266)). Prince of Persia (DOS) H = **41 px**: es el alto del PNG del frame `frame_15_stand` (res415.png) en [SDLPoP/data/KID](https://github.com/NagyD/SDLPoP/tree/master/data/KID) (**medición propia**; mapeo imagen→recurso verificado en [seg009.c L567–585](https://github.com/NagyD/SDLPoP/blob/master/src/seg009.c#L567-L585) y [seg000.c L2136](https://github.com/NagyD/SDLPoP/blob/master/src/seg000.c#L2136)). Spelunky Classic H = 16 px (caja de colisión de −8 a +8 en y, [characterStepEvent.gml L1037](https://github.com/yancharkin/SpelunkyClassicHD/blob/main/scripts/characterStepEvent/characterStepEvent.gml#L1037)).
- Archivos leídos en master el 2026-10-16: Celeste `Player.cs` (5.471 líneas), SDLPoP `src/` y `data/KID`, la fuente Apple II de Mechner (`CTRL.S`) y el fork SpelunkyClassicHD (GML). Las líneas citadas valen para esas versiones.
- No visité tcrf.net. No encontré texto de prompt injection en ninguna página consultada. Devolvieron 403/402: hollowknight.wiki, psnprofiles.com, strider.fandom.com, spriters-resource.com, metroidwiki.org y gamespot.com.
- Material ya cubierto en la sesión anterior y que no repito: física de salto, coyote, buffer, corner correction y teetering de Celeste ([celeste_jump_feel.md](../Movimiento%20y%20disparo%20en%20run-and-guns/celeste_jump_feel.md)). Ese archivo solo trae las cuatro constantes del climb hop. `aiming_ledges_ai_pipeline.md` habla de teetering (estar parado al borde), no de agarre de cornisa.

## 1. Celeste: agarre de pared con stamina, "climb hop" automático y asistencias cerca de cornisas

### Takeaway
Celeste no tiene agarre de cornisa propiamente dicho. Tiene un agarre de pared con botón (Grab) que funciona como agarre de cornisa: (a) si quedás con la mano por encima del borde, el juego te desliza hacia abajo a 30 px/s hasta que la mano toca la pared; ahí descansás "colgado del borde". (b) Si subís y la mano pasa el borde, el juego dispara un **climb hop** automático: un saltito de 8 px (0,5 H) hacia arriba y ≈8 px hacia adelante, con el control horizontal bloqueado 0,2 s. No hay animación de trepada: el pop reemplaza la trepada. El feel sale de ventanas chicas pero continuas (2 px para agarrar, 2 px de subida automática), de que la velocidad se amortigua en lugar de cortarse en seco (×0,2), y de que la salida es inmediata e interrumpible.

### Cited Findings
**Constantes de trepada** [código] — [Player.cs L102–119](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L102-L119)

| Constante | Valor | En H (H = 16 px) | A 128 px | Frames a 60 Hz |
|---|---|---|---|---|
| ClimbMaxStamina | 110 | — | — | — |
| ClimbUpCost | 100/2,2 = 45,45 por s | — | — | — |
| ClimbStillCost | 100/10 = 10 por s | — | — | — |
| ClimbJumpCost | 110/4 = 27,5 por salto | — | — | — |
| ClimbTiredThreshold | 20 | — | — | — |
| ClimbCheckDist | 2 px | 0,125 H | 16 px | — |
| ClimbUpCheckDist | 2 px | 0,125 H | 16 px | — |
| ClimbNoMoveTime | 0,1 s | — | — | 6 f |
| ClimbUpSpeed | −45 px/s | 2,8 H/s | 360 px/s | 0,75 px/f |
| ClimbDownSpeed | 80 px/s | 5 H/s | 640 px/s | — |
| ClimbSlipSpeed | 30 px/s | 1,9 H/s | 240 px/s | — |
| ClimbAccel | 900 px/s² | 56 H/s² | 7.200 px/s² | — |
| ClimbGrabYMult | 0,2 | — | — | — |
| ClimbHopY / ClimbHopX | −120 / 100 px/s | 7,5 / 6,25 H/s | 960 / 800 px/s | — |
| ClimbHopForceTime | 0,2 s | — | — | 12 f |
| ClimbJumpBoostTime | 0,2 s | — | — | 12 f |
| ClimbHopNoWindTime | 0,3 s | — | — | 18 f |

Las conversiones a H y a 128 px son **cálculo propio**.

**Cuándo agarra** [código]
- Agarra solo con Grab apretado, sin estar cansado, sin estar agachado, con `Speed.Y >= 0` (cayendo o en el ápice, nunca subiendo) y sin moverse en dirección opuesta a la pared — [L2790–2818](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2790-L2818).
- `ClimbCheck` prueba si la hitbox, corrida 2 px hacia donde mira, toca un Solid — [L2777–2780](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2777-L2780).
- Si no hay pared a tu altura pero sí 1–2 px más arriba, el juego te sube esos píxeles y agarra (`ClimbUpCheckDist`). No lo hace si estás apretando abajo ni con viento hacia abajo — [L2808–2816](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2808-L2816).
- Al agarrar (`ClimbBegin`): Speed.X = 0, Speed.Y × 0,2, bloqueo de movimiento por 0,1 s, rumble y snap de hasta 2 px hacia la pared — [L3056–3078](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3056-L3078).

**"Colgarse del borde" y el climb hop** [código]
- `SlipCheck` mira dos puntos justo afuera del borde frontal de la hitbox: la fila superior y 4 px más abajo. Si los dos están libres, el código lo interpreta como "manos por encima del borde" — [L3316–3325](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3316-L3325).
- Sin input vertical, con las manos por encima del borde, el personaje resbala a ClimbSlipSpeed (30 px/s). El comentario del código dice "Slip down if hands above the ledge and no vertical input" — [L3225–3231](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3225-L3231).
- Apretando arriba: si hay techo encima, o si el hop está bloqueado (sólido a 6 px arriba, o un `LedgeBlocker`), se frena. Si no, y `SlipCheck()` da verdadero, ejecuta `ClimbHop()` — [L3186–3203](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3186-L3203), [L3327–3345](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3327-L3345).
- Si la pared desaparece mientras subís (Speed.Y < 0), también hace `ClimbHop()` ("Climbed over ledge?") — [L3136–3150](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3136-L3150).
- `ClimbHop()`: Speed.Y = min(Speed.Y, −120) y Speed.X = 100 hacia donde mira. Si todavía hay pared adelante, guarda `hopWaitX` y aplica los 100 px/s recién cuando el frente queda libre, para no engancharse en el borde. Fuerza `moveX = 0` durante 0,2 s (input horizontal bloqueado) y suena `char_mad_climb_ledge` — [L3291–3313](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3291-L3313), [L814–823](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L814-L823), [L760–764](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L760-L764).
- Si el bloque se mueve durante el hop, el personaje lo acompaña (`climbHopSolid`; el comentario de L218 dice "snap to beside it until you get above it") — [L218](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L218), [L771–780](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L771-L780).

**Salidas desde la pared** [código]
- Salto: con la dirección contraria apretada hace `WallJump`. Si no, hace `ClimbJump`: un salto normal que cuesta 27,5 de stamina — [L3110–3118](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3110-L3118), [L1813–1830](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1813-L1830).
- Si el ClimbJump fue sin dirección y en los 0,2 s siguientes apretás la dirección contraria, se convierte en wall jump (130 px/s horizontal) y devuelve la stamina — [L688–699](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L688-L699), [L58](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L58).
- Soltar Grab te pasa a estado normal: caída libre — [L3127–3133](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3127-L3133).
- El dash también sale del agarre — [L3120–3125](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3120-L3125).

**Selección de dibujo** [código]
- En el estado de trepada, el dibujo depende del input y de la geometría: subiendo → `ClimbUp`; bajando → `WallSlide`; quieto y sin pared 6 px por debajo → `Dangling` (piernas colgando, porque la pared termina por encima de los pies); mirando para atrás → `ClimbLookBack`; si no → `WallSlide` — [L1218–1233](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1218-L1233).
- Hay SFX de mano en el frame 5 de climbUp y climbDown — [L384–385](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L384-L385).

**Asistencias relacionadas con cornisas** [código] (detalle en las notas anteriores)
- `UpwardCornerCorrection = 4` px (0,25 H, 32 px a 128) — [L53](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L53), [L2585–2612](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2585-L2612).
- `DashCornerCorrection = 4` — [L82](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L82).
- `JumpThruAssistSpeed = −40` px/s empuja hacia arriba dentro de una plataforma de un sentido. No actúa durante la trepada salvo que estés subiendo (`lastClimbMove == −1`) — [L127](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L127), [L917–918](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L917-L918).
- Maddy Thorson lista estas asistencias como "forgiveness" para "fudge" el juego a favor del jugador — [Celeste & Forgiveness](https://maddymakesgames.com/articles/celeste_and_forgiveness/) [dev].

**Geometría derivada** (**cálculo propio**, H = 16 px, hitbox de 11 px, pies = Position)
- Punto de mano del SlipCheck: 4 px por debajo del tope de la hitbox, o sea 7 px sobre los pies = 0,44 H (56 px a 128).
- En reposo colgado del borde, el borde queda a 7 px sobre los pies. Asoman por encima ≈9 px de sprite (0,56 H; 72 px a 128), si el sprite mide 16 px.
- Hop sin mantener salto, con g = 900 px/s² ([L24](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L24)): sube 120²/(2·900) = **8 px = 0,5 H** (64 px a 128) en **0,133 s = 8 f**.
- Horizontal: con moveX forzado a 0, frena a RunAccel×AirMult = 650 px/s² ([L30–33](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L30-L33)). Recorre 100²/(2·650) ≈ **7,7 px ≈ 0,48 H** (62 px a 128) en 0,154 s (≈9 f). A los 0,2 s (12 f) vuelve el control.
- Bloqueo del hop: sólido a ≤ 6 px sobre los pies = 0,375 H (48 px a 128). `Dangling`: la pared termina ≥ 5 px por encima de los pies = 0,31 H (40 px a 128).
- Stamina: subir sin parar dura 110/45,45 = **2,42 s** (≈109 px ≈ 6,8 H). Colgado quieto dura **11 s** (9 s hasta el umbral de cansancio). Alcanza para 4 climb jumps seguidos.

### Inferences
- El "colgarse del borde" de Celeste es un estado emergente: mano al borde, resbalón suave hasta ahí y dibujo `Dangling` si los pies quedan en el aire. No hay snap duro a la esquina. Para un juego con sprites grandes generados por IA, el equivalente es fijar un punto de mano y dejar que el personaje se asiente (lerp o velocidad) en vez de teletransportarlo.
- El climb hop demuestra que una trepada puede durar ≈0,13–0,2 s y no necesitar dibujos propios: usa los dibujos de salto y caída. El "costo" es un bloqueo horizontal de 0,2 s para que el hop no se deshaga.
- `hopWaitX` es un detalle de feel que conviene copiar: el empuje horizontal se aplica recién cuando el frente del collider pasó el borde, así el personaje no "rasca" la esquina.
- El agarre exige `Speed.Y >= 0`, así que nunca engancha subiendo. Es más estricto que el umbral actual del prototipo (vy > −220 px/s).

### Gaps
- Frames y delays de climbUp, climbDown, dangling y climbLookBack: el Sprites.xml no es público. Solo se sabe que climbUp/climbDown tienen al menos 6 dibujos, porque hay un evento en el frame 5 ([L384–385](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L384-L385)).
- Monocle no es público. Asumo rectángulos con borde derecho e inferior exclusivo, igual que en las notas anteriores.

## 2. Hollow Knight (el Caballero) y Hollow Knight: Silksong (Hornet)

### Takeaway
El Caballero de Hollow Knight **no** tiene agarre de cornisa. Su única herramienta de pared es Mantis Claw: se pega a la pared, resbala y hace wall jump. Hornet en Silksong agarra cornisas **desde el comienzo, sin habilidad**, y se sube sola. Si apretás salto en el momento justo del agarre, sale un salto más alto (el "ledge jump" que mencionan las previews). No encontré números (ventana, duración) en ninguna fuente. Los jugadores reportan una ventana vertical acotada ("muy bajo o muy alto y rebotás") y que planear con el capote impide el agarre.

### Cited Findings
- [comunidad] Sobre el Caballero: "your original lead character could not climb up ledges"; en Silksong "Hornet can just climb up ledges" — [Gfinity](https://www.gfinityesports.com/article/hollow-knight-silksong-qol-improvements-that-make-it-easier-than-its-predecessor).
- [comunidad, resumen de búsqueda] Mantis Claw: en el aire, cerca de una pared, apretar hacia ella hace que el Caballero se pegue y resbale. Saltar lo lanza en diagonal y alejándose. Solo funciona en superficies completamente verticales. La wiki no describe ningún agarre de cornisa — [hollowknight.wiki: Mantis Claw](https://hollowknight.wiki/w/Mantis_Claw) (403 al abrirla).
- [comunidad] Hornet: "When you jump and press forward, Hornet will proceed to hang onto the ledge and get herself up" — [Gfinity](https://www.gfinityesports.com/article/hollow-knight-silksong-qol-improvements-that-make-it-easier-than-its-predecessor). Otra guía dice que lo hace sin habilidad extra y sin el equivalente de Mantis Claw — [Deltia's Gaming](https://deltiasgaming.com/?p=338237) (resumen de búsqueda).
- [prensa, preview] "Her biggest change is the ability to grab onto a ledge and jump off it to gain more height" — [Nintendo World Report](https://www.nintendoworldreport.com/hands-on-preview/50845/hollow-knight-silksong-switch-preview).
- [prensa, Edge 2020] Hornet "can mantle or clamber onto ledges" — [KeenGamer resumiendo Edge](https://www.keengamer.com/articles/news/new-hollow-knight-silksong-details-revealed-in-edge-magazine-exclusive/).
- [comunidad] "Pressing the jump button at the right time whenever Hornet grabs a ledge makes her jump higher than usual" — [Gfinity, 5 tips](https://www.gfinityesports.com/article/struggling-with-hollow-knight-silksong-here-are-5-tips-you-need-to-know).
- [comunidad, hilo de Steam]
  - "too low OR too high and you just bounce off" (Viking ZX).
  - "Float messes with grabbing corners" (Dark). Otro usuario parafrasea el motivo así: con el botón de planear apretado, los brazos de Hornet no llegan al borde.
  - "I find dashing into them lands better" (Aetemes).
  - Agarres no deseados al bajar por una pared, "sometimes pulling up straight into an enemy" (Seal).
  - Fuente: [Steam: "grabbing ledges weirdly unreliable"](https://steamcommunity.com/app/1030300/discussions/0/595159120097973357/).
- [comunidad, resumen de búsqueda] Cling Grip es otra cosa: Hornet se pega a una pared vertical, resbala despacio, salta desde ahí y con sprint trepa en vertical — [hollowknight.wiki: Cling Grip](https://hollowknight.wiki/w/Cling_Grip) (403 al abrirla).
- [comunidad] Un usuario de Linux reportó un "ledge sprint" que se disparaba tras cada agarre. Era un problema del controlador o Proton, no una mecánica — [Steam](https://steamcommunity.com/app/1030300/discussions/0/596286707636147581/).

### Inferences
- Por las descripciones ("hang onto the ledge and get herself up", "pulling up straight into an enemy"), el agarre de Hornet parece un **mantle automático sin estado de colgado prolongado**: agarra y sube enseguida, y el salto durante esa ventana da altura extra. Es una inferencia, no está documentado.
- La queja "too low OR too high" confirma que hay una ventana vertical finita. Que el planeo lo impida sugiere que el chequeo depende de la pose o estado (brazos), no solo de la caja.
- Para un run-and-gun, el riesgo que señalan los jugadores (subirse solo a un enemigo) sirve como argumento para exigir dirección hacia la cornisa, o al menos no agarrar con dirección contraria o abajo.

### Gaps
- Ventana en px, duración del mantle, cancelabilidad y frames de animación de Hornet: no encontré datos ni rip contable (spriters-resource 403).
- Silksong es Unity como HK, pero no encontré un decompilado público de su `HeroController` con lógica de cornisa.

## 3. Prince of Persia (1989): tolerancias y secuencias desde el código; The Lost Crown (2024)

### Takeaway
En PoP 1989 el agarre **exige mantener Shift** (el botón en Apple II) para agarrar y para seguir colgado. Al soltar, se suelta. Desde la caída agarra el borde de la fila de arriba si se cumplen tres cosas:
- caés a menos de 32 px/frame (`grabspeed`);
- tus pies están dentro de los últimos **25 px** sobre la línea de piso de tu fila (`grablead`, 0,61 H);
- el borde está en la columna de adelante después de correrte 8 unidades hacia atrás (`grabreach`, ≈18 px, 0,45 H).

Después hace snap: x al borde del tile, y a la línea de piso, velocidad 0.

La mano está anclada al píxel: en los 13 dibujos de colgado, el píxel más alto queda **1 px sobre la línea del piso** (2–3 px en dos de ellos; cálculo propio). El cuerpo se balancea debajo con offsets por frame. Hay un **stun de 12 frames (1,0 s)** en el que no podés trepar. La trepada dura **17 frames = 1,42 s** (85 f a 60 Hz) y sube exactamente una fila (63 px = 1,54 H) más 6 unidades (≈14 px, 0,33 H) hacia adelante. No hay salto desde el colgado. Colgado libre, se suelta solo a los 43 frames (3,6 s). The Lost Crown: sin datos de cornisa. Sí hay dos principios de diseño citados: cualquier animación es cancelable por salto, esquive o parry, y la duración de cada animación se ajustó "de a un frame".

### Cited Findings
**Parámetros originales (Apple II, Mechner)** [código]
- `grabreach = -8`, `grabspeed = 32 ;max Y-vel to grab ledge`, `grablead = 25 ;increase to grab ledge earlier`, `stuntime = 12` — [CTRL.S L45–48](https://github.com/jmechner/Prince-of-Persia-Apple-II/blob/master/01%20POP%20Source/Source/CTRL.S#L45-L48).
- La rutina `fallon` ("Hasn't hit floor yet -- can he grab edge above?") verifica, en orden: botón apretado y vivo; `CharYVel < grabspeed`; `CharY + grablead >= FloorY` de la fila; "Is there a ledge within reach?" (suma `grabreach` a X y relee bloques). Si hay borde: "Align char with block": X al borde, Y = FloorY, YVel = 0, secuencia `fallhang` y `stunned = stuntime` — [CTRL.S L243–300](https://github.com/jmechner/Prince-of-Persia-Apple-II/blob/master/01%20POP%20Source/Source/CTRL.S#L243-L300).
- `hanging`: si `stunned` es distinto de 0, no podés trepar. Joystick arriba → `climbup`. Botón suelto → `:drop` (`hangdrop` si hay piso debajo o detrás, `hangfall` si no). Si debajo hay un bloque o panel → `hangstraight`. Si la cornisa se derrumba → caés. Si no, "just keep swinging" — [CTRL.S L1408–1530](https://github.com/jmechner/Prince-of-Persia-Apple-II/blob/master/01%20POP%20Source/Source/CTRL.S#L1408-L1530).

**Port C (SDLPoP), mismo comportamiento con nombres legibles** [código]
- `check_grab()`: `control_shift == CONTROL_HELD` ("press Shift to grab"), `Char.fall_y < 32` ("you can't grab if you're falling too fast"), vivo, y `y_land[curr_row+1] <= Char.y + 25`. Corre x en −8 (`char_dx_forward(-8)`) y prueba `can_grab_front_above()`. Si puede: `Char.x = char_dx_forward(distance_to_edge_weight())`, `Char.y = y_land[curr_row+1]`, `fall_y = 0`, `seq_15_grab_ledge_midair`, `grab_timer = 12` y sonido de agarre — [seg006.c L1177–1226](https://github.com/NagyD/SDLPoP/blob/master/src/seg006.c#L1177-L1226).
- Se llama durante el inicio de caída (frames 102–105) y en caída libre mientras no tocaste piso — [seg006.c L909–948](https://github.com/NagyD/SDLPoP/blob/master/src/seg006.c#L909-L948), [seg005.c L37–43](https://github.com/NagyD/SDLPoP/blob/master/src/seg005.c#L37-L43).
- El grito de caída arranca con `fall_y >= 31` — [seg005.c L38–41](https://github.com/NagyD/SDLPoP/blob/master/src/seg005.c#L38-L41).
- `can_grab()` rechaza:
  - agarrar a través de pared o piso;
  - un loose floor temblando;
  - un doortop desde el lado equivocado;
  - un tile sin piso.
  - Fuente: [seg006.c L1606–1622](https://github.com/NagyD/SDLPoP/blob/master/src/seg006.c#L1606-L1622).
- `grab_timer` baja 1 por frame — [seg006.c L1405–1407](https://github.com/NagyD/SDLPoP/blob/master/src/seg006.c#L1405-L1407).
- `control_hanging()`:
  - Con `grab_timer == 0` y arriba → `can_climb_up()`.
  - Con Shift mantenido sigue colgado: pasa a `hang_against_wall` si debajo hay pared, y suelta si la cornisa desapareció.
  - Sin Shift → `hang_fall()`.
  - Fuente: [seg005.c L791–824](https://github.com/NagyD/SDLPoP/blob/master/src/seg005.c#L791-L824).
- `hang_fall()`: `seq_23_release_ledge_and_fall` si no hay piso detrás ni debajo. Si no, `seq_11_release_ledge_and_land`, y antes corre x −7 si está contra una pared — [seg005.c L846–869](https://github.com/NagyD/SDLPoP/blob/master/src/seg005.c#L846-L869).
- Parado debajo de una cornisa, arriba → `check_jump_up()`: elige "jump up and grab" (recto, adelante o hacia atrás) según la distancia al borde (<4 o <6 unidades) y si hay piso detrás — [seg005.c L693–760](https://github.com/NagyD/SDLPoP/blob/master/src/seg005.c#L693-L760), [L871–895](https://github.com/NagyD/SDLPoP/blob/master/src/seg005.c#L871-L895).
- Escalas del motor:
  - Tile = 14 unidades internas en x = 32 px de pantalla; alto de fila 63 px — [types.h L1427–1430](https://github.com/NagyD/SDLPoP/blob/master/src/types.h#L1427-L1430).
  - Caída: aceleración 3 px/frame, máximo 33 — [types.h L1435–1436](https://github.com/NagyD/SDLPoP/blob/master/src/types.h#L1435-L1436).
  - Pisos en `y_land = {-8, 55, 118, 181, 244}` — [data.h L506](https://github.com/NagyD/SDLPoP/blob/master/src/data.h#L506).
  - Timer a 60 Hz con 5 ticks por frame fuera de combate (12 fps) y 6 en combate (10 fps) — [types.h L1373](https://github.com/NagyD/SDLPoP/blob/master/src/types.h#L1373), [data.h L869–870](https://github.com/NagyD/SDLPoP/blob/master/src/data.h#L869-L870), [seg003.c L362–368](https://github.com/NagyD/SDLPoP/blob/master/src/seg003.c#L362-L368).
- Opciones de SDLPoP, que no son del original:
  - `fix_grab_falling_speed` (32 → 30): "By jumping and bumping into a wall, you can sometimes grab a ledge two stories down".
  - `enable_jump_grab`: Shift + arriba durante un salto agarra la fila de arriba, con alcance de "a little over 1 full tile" parado y "about 2.5 tiles or less" corriendo.
  - Fuente: [SDLPoP.ini L147–149, L186–187](https://github.com/NagyD/SDLPoP/blob/master/SDLPoP.ini), [seg006.c L1228–1283](https://github.com/NagyD/SDLPoP/blob/master/src/seg006.c#L1228-L1283).
- Manual de C64 [comunidad, resumen de búsqueda]: "To hang from a ledge: Press a joystick button and hold it down. To pull yourself up onto the ledge, push the joystick up" — [princeop.txt](https://papperlan.duckdns.org/textfiles.com/piracy/SOFTDOCS/princeop.txt).

**Secuencias (seqtbl.c) y duraciones** (conteo propio de frames en el código; 12 fps; ×5 para frames a 60 Hz)

| Secuencia | Frames PoP | Segundos | f a 60 Hz | Notas |
|---|---|---|---|---|
| `fallhang` (agarre desde caída) | 1 (frame 80) → `hang` | 0,08 | 5 | [L687–689](https://github.com/NagyD/SDLPoP/blob/master/src/seqtbl.c#L687-L689) |
| `jumphangMed` (salto vertical y agarre) | 14 | 1,17 | 70 | [L526–532](https://github.com/NagyD/SDLPoP/blob/master/src/seqtbl.c#L526-L532) |
| `hang` (balanceo) | 43, después `hangdrop` | 3,58 | 215 | [L554–567](https://github.com/NagyD/SDLPoP/blob/master/src/seqtbl.c#L554-L567): suelta sola al terminar |
| `hangstraight` (contra pared) | 5 + loop infinito | — | — | [L569–573](https://github.com/NagyD/SDLPoP/blob/master/src/seqtbl.c#L569-L573) |
| `climbup` | **17** | **1,42** | **85** | [L590–600](https://github.com/NagyD/SDLPoP/blob/master/src/seqtbl.c#L590-L600) |
| `climbfail` (espejo, guillotina, reja cerrada) | 11 | 0,92 | 55 | [L575–579](https://github.com/NagyD/SDLPoP/blob/master/src/seqtbl.c#L575-L579) |
| `climbdown` (bajar al colgado desde arriba) | 10 | 0,83 | 50 | [L581–588](https://github.com/NagyD/SDLPoP/blob/master/src/seqtbl.c#L581-L588) |
| `hangdrop` (soltar y aterrizar) | 5 | 0,42 | 25 | [L602–607](https://github.com/NagyD/SDLPoP/blob/master/src/seqtbl.c#L602-L607) |
| `hangfall` (soltar al vacío) | 3, después freefall con fall_y 12 | 0,25 | 15 | [L609–613](https://github.com/NagyD/SDLPoP/blob/master/src/seqtbl.c#L609-L613) |
| stun posterior al agarre en caída | 12 | 1,0 | 60 | `grab_timer`/`stuntime` |

- `climbup`, detalle: frames 135–140 (6) → `dx(5), dy(-63), SEQ_UP` → 141–148 (8) → 149 (1) → 118–119 "stand up from crouch" (2) → `dx(1)` → stand. Sube exactamente una fila (63 px) y avanza 5+1 = 6 unidades — [seqtbl.c L590–600](https://github.com/NagyD/SDLPoP/blob/master/src/seqtbl.c#L590-L600).

**Cómo se dibuja la mano en el borde** (**cálculo propio** con alto del PNG + `dy` de `frame_table_kid`; el sprite se dibuja con la base en `Char.y + dy`, [seg008.c L1733–1737](https://github.com/NagyD/SDLPoP/blob/master/src/seg008.c#L1733-L1737); tabla en [seg006.c L127](https://github.com/NagyD/SDLPoP/blob/master/src/seg006.c#L127); PNGs en [data/KID](https://github.com/NagyD/SDLPoP/tree/master/data/KID))
- Colgado, el ancla `Char.y` queda en la línea de piso de la fila de abajo, 63 px bajo el borde.
- En los 13 dibujos de colgado (frames 87–99) el píxel superior queda **1 px por encima de la línea de piso de la cornisa**. Las excepciones son el 91 (3 px) y el 94 (2 px). Cada dibujo compensa su alto distinto (50–57 px) con un `dy` propio (−10 a −15), así que **la mano queda clavada y el cuerpo se balancea** (dx por frame de −1 a +7 unidades).
- Los dos primeros dibujos de trepada (135–136) también tienen el tope a 1 px sobre el borde.
- Dibujo 91 (colgado en reposo): 57 px de alto = **1,39 H** de mano a punta de pie. La base queda 10 px sobre el piso de abajo (0,24 H), por eso `hangdrop` es una caída corta y segura.
- Trepada (posición del píxel más bajo respecto al borde):
  - Frames 135–140 ("tirón"): los pies suben de 51 a 22 px bajo el borde (0,71 H en 0,5 s) y la cabeza asoma hasta 13 px.
  - Frames 141–144 ("pasar el borde"): ancla ya arriba. El punto más bajo pasa de 17 a 4 px bajo el borde y el dibujo mide 20–28 px (agachado).
  - Frames 145–149 ("agachado arriba"): 22 → 34 px de alto.
  - Frames 118–119 (pararse): 38 → 39 px. Stand: 41 px.
- Reparto de la trepada (conteo propio): tirón 6/17 (35 %), pasar el borde 4/17 (24 %), agachado arriba 5/17 (29 %), pararse 2/17 (12 %).

**Conversión de tolerancias** (**cálculo propio**, H = 41 px; a 128 px = ×3,12)
- `grablead` 25 px = 0,61 H → 78 px a 128.
- `grabreach` 8 unidades ≈ 18,3 px = 0,45 H → 57 px a 128. La columna probada mide 14 unidades = 32 px = 0,78 H.
- Velocidad máxima para agarrar: 32 px/frame = 384 px/s = 9,4 H/s (1.200 px/s a 128).
- Desde quieto, fall_y llega a 32 en ≈11 frames. Se puede agarrar durante los primeros ≈0,85 s de caída (≈2,5 filas). Desde ese momento suena el grito: el sonido avisa que ya no hay agarre.
- En términos de la mano: el dibujo de caída (frame 106) mide 36 px. Al disparar el agarre, su tope está entre 3 y 28 px por debajo del borde y pasa a 1 px por encima. El agarre "estira los brazos" hasta 0,7 H hacia arriba. El ancla se corre 0–25 px hacia abajo, pero lo visible sube.
- Trepada: +63 px (1,54 H → 197 px a 128) en vertical y +13,7 px (0,33 H → 43 px a 128) hacia adelante.

**The Lost Crown (2024)** [dev]
- "Before having Sargon and his animation, we worked with just a capsule… Sargon was, for one year, a capsule".
- Sobre el peso: "The weight, for me, is the whole thing". Ajustaron largos de animación "just about one frame".
- "if a player uses a defensive mechanic like a parry, dodge, or even a jump, it could cancel any animation".
- Rayman como referencia "For the platforming aspect".
- Fuente: [Xbox Wire, 2024-01-17](https://news.xbox.com/en-us/2024/01/17/prince-of-persia-the-lost-crown-builds-on-raymans-platforming-legacy/).
- [prensa] Una preview lista saltos largos, slides, wall jumps, barras y "grabbing and jumping off handholds" — [Acer blog](https://blog.acer.com/en/discussion/1200/preview-of-prince-of-persia-the-lost-crown) (resumen de búsqueda).

### Inferences
- PoP es el extremo "simulación": ventana generosa (0,6 H, compensa 12 fps y caídas de hasta 32 px por frame), botón obligatorio, stun de 1 s y trepada de 1,42 s. Funciona porque el juego es lento y de puzzle. Para un run-and-gun a 60 Hz solo vale copiar **la técnica de anclaje**: un punto de mano fijo por dibujo y offsets por frame para que la mano no patine. Los tiempos no.
- La estructura de la trepada (≈35 % tirón, ≈25 % pasar el borde, ≈40 % reincorporarse) sirve como guion de fases para el clip. En acción se comprime la última parte, o se sale corriendo.
- La auto-suelta a 3,6 s y el stun eran presión de diseño de PoP (el reloj de 60 minutos). No aplican al prototipo.

### Gaps
- Si la mano se dibuja por delante o por detrás del frente del piso (capas de PoP): no lo verifiqué.
- Altura del Kid en Apple II: medí la versión DOS de SDLPoP.
- The Lost Crown: ventana, automatismo y duración del agarre de cornisa son s/d. GameSpot (que menciona "mantle") devolvió 403.

## 4. Strider (arcade 1989) y Strider (2014)

### Takeaway
Hiryu no "agarra cornisas" como PoP. Se pega con el gancho o cypher a paredes y techos al saltar contra ellos, se desplaza colgado y, apretando arriba debajo de una plataforma, hace un **flip** que lo deja arriba. En 2014 la trepada es casi universal (paredes y techos a cualquier ángulo) y la forma rápida de subir es el **climb jump** (arriba + salto). No encontré velocidades ni frames.

### Cited Findings
- [enciclopedia] Arcade: joystick de 8 direcciones y dos botones. Hiryu puede "latch onto certain platforms, and climb across walls and ceilings using a metallic hook" — [Wikipedia: Strider (1989 arcade)](https://en.wikipedia.org/wiki/Strider_(1989_arcade_game)).
- [comunidad, resumen de búsqueda] "pressing up while clinging below a platform will flip Hiryu up onto its top" — [Strider Wiki: Strider (CPS-1)](https://strider.fandom.com/wiki/Strider_(CPS-1)) (402 al abrirla).
- [comunidad, TAS] Strider 2 (PSX; el autor dice que "was not changed from the arcade"):
  - la trepada se activa al "run into a wall or ceiling in the air";
  - "The fastest way to climb a wall is to jump three frames before you touch it";
  - desde la pared, apretar en contra hace un "hassou jump";
  - "There is no quick way to move along a ceiling".
  - Fuente: [TASVideos foro](https://tasvideos.org/Forum/Posts/192645).
- [comunidad, speedrun] Strider 2014:
  - "Climbing is possible on almost all walls and ceilings, regardless of angle";
  - "Pressing Up+Jump while climbing walls will give you a boost of speed with a climb jump", que no funciona en paredes inclinadas;
  - después de un Plasma Catapult hay que mantener arriba para re-agarrar la superficie.
  - Fuente: [SDA KB: Movement Techniques](https://kb.speeddemosarchive.com/Strider_(2014)/Movement_Techniques).

### Inferences
- Strider resuelve la cornisa con un **flip** (acrobacia corta y rápida) en vez de una trepada realista. Para un personaje cartoon de run-and-gun, un "flip-up" de 2–3 dibujos es una alternativa legítima a la trepada de 4 fases. Además, el clip de IA sería más fácil de generar: un giro rápido tolera más deformación que un mantle lento.

### Gaps
- Velocidad de trepada, duración del flip, ventana de enganche y conteo de dibujos: s/d (spriters-resource 403, sin datos de RAM ni frame data).

## 5. Shinobi III: Return of the Ninja Master (1993) y Shinobi: Art of Vengeance (2025)

### Takeaway
Shinobi III **no tiene agarre de cornisa**. Tiene "Spiderwalk", que es colgarse de techos, cuerdas o vigas con Salto + Arriba (se baja con Salto + Abajo), y "Wall Kick" con Salto + hacia la pared. Todo es explícito, con botón. Art of Vengeance (2025) tiene pegado automático y breve a paredes, colgado de techos y cuerdas, garras para trepar superficies marcadas, y un **auto-mantle**: si llegás cerca del tope de una plataforma, Joe se sube solo. Los jugadores se quejan de que no se puede evitar.

### Cited Findings
- [manual oficial] Spiderwalk: "simultaneously press Jump and the D-button up to grab the ceiling, rope or cross beam, then move left or right. To get back on the ground, simultaneously press Jump and the D-button down". Wall Kick: "Jump toward a wall, then simultaneously press Jump and the D-button towards the wall". El manual no menciona cornisas — [Manual Shinobi III (SEGA Mega Drive Classics, Steam)](https://www.segaretro.org/images/d/d4/ShinobiIII_Steam_manual.pdf).
- [comunidad] Art of Vengeance:
  - al saltar contra una pared "Joe will automatically cling to it for a brief moment" y A lo lanza;
  - se puede encadenar wall jumps entre paredes cercanas;
  - techos aptos: se agarra al saltar hacia ellos y se suelta con Abajo;
  - cuerdas y cadenas: se agarran saltando, arriba/abajo trepa, izquierda/derecha balancea.
  - Fuente: [Ludo.guide: movement techniques](https://www.ludo.guide/guide/shinobi-art-of-vengeance/getting-started/basic-controls-movement/movement-techniques).
- [comunidad, Steam] "he will auto mantle onto platforms… if you get too close to the top of that platform he will leap on top if it", y eso arruina puzzles donde hay que quedarse colgado al costado. Además, soltarse de la pared es "a combination of pressing down and jump" y "sometimes when you need to drop… you let go and he still hangs" — [Steam: "These controls need to be fixed"](https://steamcommunity.com/app/2361770/discussions/0/673972930560169236/).
- [comunidad, resumen de búsqueda] "Musashi will automatically climb up ledges. This can be a boon but also a curse on some sections" — [PSNProfiles trophy guide](https://psnprofiles.com/guide/23945-shinobi-art-of-vengeance-trophy-guide) (403 al abrirla).
- [comunidad, resumen de búsqueda] Las Ninja Claws permiten colgarse y trepar paredes y techos marcados con una superficie amarilla agrietada, y resetean las habilidades de movimiento — misma guía de PSNProfiles.

### Inferences
- La serie pasó de "todo con botón" (1993) a "auto-mantle cerca del tope" (2025). La queja típica del auto-mantle aparece cuando el diseño de nivel pide quedarse colgado al costado (esquivar algo arriba). En un run-and-gun, donde a veces convenga quedarse colgado para que pase una bala, conviene que el mantle requiera dirección hacia la cornisa o arriba.

### Gaps
- Distancias de activación del auto-mantle, duración y cancelabilidad en Art of Vengeance: s/d.

## 6. Referencias modernas: Metroid Dread / Samus Returns, Dead Cells, Spelunky (código), GDevelop (código)

### Takeaway
Hay dos escuelas:
- **Con dirección**: Metroid Dread (inclinar hacia la cornisa mientras saltás o caés) y Spelunky (apretar hacia la pared). Dread además deja disparar, apuntar libre y contraatacar colgado.
- **Automático**: Dead Cells, Hornet y Shinobi AoV. Es fluido, pero genera quejas por agarres no deseados ("edge waffling", agarres que cortan ataques).

Spelunky es la referencia de código más limpia:
- ventana vertical de **4 px (0,25 H)**;
- hay que estar tocando la pared y apretar hacia ella;
- snap a grilla de 8 px que deja el tope de la caja al ras del borde;
- **sin trepada**: para subir se salta con el salto normal desde el colgado;
- cooldowns de re-agarre de **0,1–0,17 s**.

### Cited Findings
**Metroid Dread** [oficial + guía]
- "Samus can also grab onto ledges by tilting the Left Stick toward them while jumping or falling". Free Aim (L + stick) funciona "hanging from a ledge or crouching" — [Nintendo, Metroid Dread Report Vol. 9](https://www.nintendo.com/au/news-and-articles/metroid-dread-report-vol-9-handy-tips-for-newcomers).
- Colgada, Samus "can fire her arm cannon, use free aim, and perform melee counters"; se sube "moving from ledge to ledge" — [Samurai Gamers: Ledge Grab](https://samurai-gamers.com/metroid-dread/how-to-use-ledge-grab/). Misma guía: "While on Ledge Grab, eliminate enemies by using her Power Beam or Missile attacks… you can use Melee Counter" — [Samurai Gamers: Standard Abilities](https://samurai-gamers.com/metroid-dread/standard-abilities/).
- Duración de la subida y transición cornisa→correr: no las encontré documentadas (ver Gaps).

**Dead Cells** [comunidad; no encontré declaraciones de Motion Twin]
- Agarre automático: el personaje "grabs onto any ledge that offers itself". Mantener arriba no cambia nada. Un jugador perdió puertas con tiempo y murió por "auto-grabbing a ledge" al intentar bajar, y pidió un botón de trepar — [GOG: "A climb button"](https://www.gog.com/forum/dead_cells/a_climb_button).
- "'Edge waffling' drives me, and a lot of other players, nuts". Otro jugador dice que los agarres "cancel out attack animations for no reason" y que "it shouldn't have priority over other actions" — [Steam: Ledge Grabbing](https://steamcommunity.com/app/588650/discussions/0/1457328392110395509/).

**Spelunky Classic** [código: fork HD en GML, presumiblemente fiel a la lógica original de Derek Yu; 30 fps según `option_game_speed: 30` en [options_main.yy](https://github.com/yancharkin/SpelunkyClassicHD/blob/main/options/main/options_main.yy)]
- Detección: no tocar techo, `hangCount == 0`, no estar en el suelo, apretar hacia la pared (`kRight and colRight`). Además, sólido en (x+9, y−5) o (x+9, y−6), libre en (x+9, y−9) y sin suelo en (x, y+9). Después: `state = HANGING; move_snap(1, 8); yVel = 0; grav = 0`. No hay condición de vy (con guantes se puede agarrar cualquier pared, pero cayendo) — [characterStepEvent.gml L410–504](https://github.com/yancharkin/SpelunkyClassicHD/blob/main/scripts/characterStepEvent/characterStepEvent.gml#L410-L504).
- Colgado:
  - abajo + salto → caer, `hangCount = 5` (10 con guantes);
  - salto con dirección contraria → caer, `hangCount = 3`;
  - salto solo → salto normal (`yAcc += initialJumpAcc * 2`, el mismo impulso del salto desde el suelo), 2 px alejándose de la pared, `hangCount = 3`;
  - si la pared desaparece → caer, `hangCount = 4`.
  - Fuente: [L506–549](https://github.com/yancharkin/SpelunkyClassicHD/blob/main/scripts/characterStepEvent/characterStepEvent.gml#L506-L549), salto de suelo en [L351–362](https://github.com/yancharkin/SpelunkyClassicHD/blob/main/scripts/characterStepEvent/characterStepEvent.gml#L351-L362), `initialJumpAcc = -2` en [characterCreateEvent.gml L68](https://github.com/yancharkin/SpelunkyClassicHD/blob/main/scripts/characterCreateEvent/characterCreateEvent.gml#L68).
- "Ledge flip": agachado en el borde, mirando al vacío y apretando hacia él → `DUCKTOHANG`, que pasa a colgado. La animación va a `image_speed = 0.8` — [L816–870](https://github.com/yancharkin/SpelunkyClassicHD/blob/main/scripts/characterStepEvent/characterStepEvent.gml#L816-L870), [L1039–1043](https://github.com/yancharkin/SpelunkyClassicHD/blob/main/scripts/characterStepEvent/characterStepEvent.gml#L1039-L1043).
- Conteo propio en el repo ([sprites/](https://github.com/yancharkin/SpelunkyClassicHD/tree/main/sprites)): `sHangLeft` tiene **1 dibujo** (colgado estático) y `sDuckToHangL` **9 dibujos**.
- **Cálculo propio** (H = 16 px; caja de −8 a +8 alrededor del origen; pies en y+8):
  - el borde tiene que estar entre 13 y 16 px sobre los pies (0,81–1,0 H), una **ventana de 4 px = 0,25 H** (32 px a 128);
  - en horizontal hay que estar en contacto (0 px);
  - el snap a 8 px deja y = borde + 8, con el tope de la caja al ras del borde y las manos dibujadas por encima;
  - cooldowns: 3 frames = 0,1 s (6 f a 60 Hz) tras salto o soltada con dirección contraria; 5 = 0,167 s (10 f) tras abajo + salto (10 = 0,33 s con guantes); 4 = 0,133 s si se va la pared;
  - ledge flip: 9 dibujos / 0,8 = 11,25 frames ≈ **0,375 s**.

**GDevelop (motor open source, comportamiento "Platformer character")** [código]
- `xGrabTolerance` por defecto **10 px**; `yGrabOffset` por defecto 0, más un `yGrabOffset` propio de cada plataforma — [platformerobjectruntimebehavior.ts L201–204](https://github.com/4ian/GDevelop/blob/master/Extensions/PlatformBehavior/platformerobjectruntimebehavior.ts#L201-L204).
- `_checkGrabPlatform`: corre el objeto `xGrabTolerance` hacia donde se mueve (o hacia donde miró por última vez), busca plataformas que crucen, hace snap de y a `plataforma.y + plataforma.yGrabOffset − yGrabOffset` y agarra solo si en esa posición no choca con nada — [L792–835](https://github.com/4ian/GDevelop/blob/master/Extensions/PlatformBehavior/platformerobjectruntimebehavior.ts#L792-L835).
- `_canGrab` es un test **barrido**: agarra si la línea de agarre del personaje cruzó la de la plataforma entre el frame anterior y el actual, subiendo o bajando ("This must be inclusive for at least one position…") — [L902–921](https://github.com/4ian/GDevelop/blob/master/Extensions/PlatformBehavior/platformerobjectruntimebehavior.ts#L902-L921).
- Colgado: tecla de soltar o salto — [L2443–2480](https://github.com/4ian/GDevelop/blob/master/Extensions/PlatformBehavior/platformerobjectruntimebehavior.ts#L2443-L2480).
- [docs, resumen de búsqueda] La opción de agarrar sin moverse viene activada por defecto: "when moving toward a wall, a character automatically grabs a nearby ledge" — [GDevelop wiki](https://wiki.gdevelop.io/gdevelop5/behaviors/platformer/).

### Inferences
- El "salto desde el colgado = salto normal" de Spelunky elimina la animación de trepada entera. El jugador sube saltando y cae parado arriba. Para un pipeline donde cada clip cuesta generación y limpieza, es la opción más barata, y se puede ofrecer **además** de la trepada (arriba = trepar, salto = saltar).
- El test barrido de GDevelop resuelve el problema de las caídas rápidas a 60 Hz: con una ventana chica no se saltea el borde entre frames.
- Dread muestra que en un juego de disparos colgarse puede ser una postura de combate (apuntar, disparar, contraatacar), no solo un paso de plataforma.

### Gaps
- Metroid Dread y Samus Returns: duración del pull-up, si se cancela y si conserva velocidad al correr. No encontré frame data (ni speedrun, ni datos del motor), y Samus es 3D, así que no hay rip contable.
- Dead Cells: tolerancias y duración s/d. No encontré charla ni post de Motion Twin o Deepnight sobre el agarre.
- Ori y Blasphemous: solo encontré menciones anecdóticas. Blasphemous: un jugador dice que mantener dirección sin saltar o un espadazo de más impiden el agarre ([Steam](https://steamcommunity.com/app/774361/discussions/0/3484123669089692742)). Sin números.

## 7. Comparativa transversal

### Takeaway
Las tolerancias van de 4 px (Spelunky, 0,25 H) a 25 px (PoP, 0,61 H). El agarre de pared de Celeste usa 2 px horizontales (0,125 H). Todos hacen **snap** a una posición canónica: borde del tile en PoP, grilla de 8 px en Spelunky, línea de agarre más offset en GDevelop, resbalón hasta la mano en Celeste. Las trepadas van de 0 s (Spelunky salta), ≈0,13–0,2 s (climb hop de Celeste) a 1,42 s (PoP). Los juegos de acción modernos (Hornet, Shinobi AoV, Dead Cells) tienden al mantle automático y rápido, y su crítica recurrente son los agarres no deseados.

### Cited Findings
| Juego | Activación | Ventana vertical | Horizontal | Condición vy | Snap / dibujo de la mano | Trepada | Desde el colgado | Soltar / re-agarre | Disparo / inv. |
|---|---|---|---|---|---|---|---|---|---|
| Celeste ([Player.cs](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2790-L2818)) | Botón Grab | +2 px de subida automática; resbala hasta que la mano toca la pared | 2 px (0,125 H) | vy ≥ 0 | Sin snap a la esquina: resbala a 30 px/s; dibujo `Dangling` si los pies quedan al aire | Climb hop 8 px arriba / ≈8 px adelante, 0,13 s a ápice, 0,2 s de bloqueo (cálculo propio) | Climb jump; wall jump con dirección contraria | Soltar Grab; stamina 11 s quieto | No dispara (no es shooter) |
| PoP 1989 ([CTRL.S](https://github.com/jmechner/Prince-of-Persia-Apple-II/blob/master/01%20POP%20Source/Source/CTRL.S#L45-L48)) | Shift o botón mantenido | 25 px (0,61 H) | Columna de 32 px tras correrse 18 px (0,45 H) | fall < 32 px/f (9,4 H/s) | x al borde del tile, y a la línea de piso; mano clavada 1–3 px sobre el borde en los 13 dibujos (cálculo propio) | 17 f = 1,42 s, después de 1 s de stun | Nada (solo arriba = trepar) | Soltar Shift → hangdrop 0,42 s o hangfall; auto-suelta a 3,6 s | s/d |
| Spelunky ([GML](https://github.com/yancharkin/SpelunkyClassicHD/blob/main/scripts/characterStepEvent/characterStepEvent.gml#L410-L549)) | Dirección hacia la pared | 4 px (0,25 H) | Contacto (0 px) | Ninguna | Snap a 8 px: tope de la caja = borde; 1 dibujo de colgado | No hay: se salta | Salto normal; contrario + salto = caer | Abajo + salto; cooldown 0,1–0,17 s | s/d |
| GDevelop ([TS](https://github.com/4ian/GDevelop/blob/master/Extensions/PlatformBehavior/platformerobjectruntimebehavior.ts#L792-L921)) | Automático (configurable) | Cruce barrido de la línea de agarre | 10 px por defecto | Sube o baja | y = línea de plataforma + offsets configurables | No incluida | Salto | Tecla de soltar | — |
| Metroid Dread ([Nintendo](https://www.nintendo.com/au/news-and-articles/metroid-dread-report-vol-9-handy-tips-for-newcomers)) | Stick hacia la cornisa | s/d | s/d | Saltando o cayendo | s/d | s/d | s/d | s/d | Dispara, apunta libre y contraataca ([guía](https://samurai-gamers.com/metroid-dread/how-to-use-ledge-grab/)) |
| Silksong ([Gfinity](https://www.gfinityesports.com/article/hollow-knight-silksong-qol-improvements-that-make-it-easier-than-its-predecessor), [Steam](https://steamcommunity.com/app/1030300/discussions/0/595159120097973357/)) | Automático o con adelante (las fuentes no coinciden) | Finita ("too low OR too high") | s/d | Subiendo y cayendo (inferencia) | s/d | Sube sola (inferencia) | Salto con timing = más altura | s/d | s/d |
| Shinobi AoV ([Steam](https://steamcommunity.com/app/2361770/discussions/0/673972930560169236/)) | Auto-mantle cerca del tope | s/d | s/d | s/d | s/d | s/d | — | Abajo + salto para soltarse de la pared | s/d |
| Dead Cells ([GOG](https://www.gog.com/forum/dead_cells/a_climb_button)) | Automático | s/d | s/d | s/d | s/d | s/d | s/d | s/d | Los jugadores dicen que el agarre corta ataques |
| Shinobi III ([manual](https://www.segaretro.org/images/d/d4/ShinobiIII_Steam_manual.pdf)) | Sin cornisa; techo con Salto + Arriba | — | — | — | — | — | — | Salto + Abajo | — |
| Strider arcade ([Wikipedia](https://en.wikipedia.org/wiki/Strider_(1989_arcade_game))) | Gancho al chocar pared o techo | s/d | s/d | s/d | s/d | Flip con arriba bajo plataforma ([resumen de búsqueda](https://strider.fandom.com/wiki/Strider_(CPS-1))) | Hassou jump (contrario) | s/d | s/d |

Prototipo actual (dato del encargo; **cálculo propio** en H suponiendo px de mundo a escala de pantalla, H = 102 px; entre paréntesis, si fueran px de atlas, H = 128):

| Parámetro | Valor | En H |
|---|---|---|
| Ventana vertical | +20 / −26 px = 46 px | 0,45 H (0,36 H) |
| Ventana horizontal | 22 px | 0,22 H (0,17 H) |
| Condición vy | vy > −220 px/s | 2,2 H/s |
| Agarre | 0,2 s | — |
| Trepada | ≈0,36 s, termina con vx = 0 | — |
| Re-agarre tras soltar | 0,35 s | — |

### Inferences
- Ventana: el prototipo (≈0,36–0,45 H) está entre Spelunky (0,25 H, 30 fps) y PoP (0,61 H, 12 fps). A 60 Hz y con test barrido no hace falta más. Lo que sí conviene es medir la distancia horizontal **desde la cara del collider**, no desde la mano de un clip.
- Trepada: 0,36 s es razonable frente a PoP (1,42 s). Igual es más larga que el hop de Celeste (≈0,2 s hasta recuperar control) y que la opción Spelunky (0 s). El problema real es la salida con vx = 0.
- Re-agarre: 0,35 s es 2–3,5 veces más que Spelunky (0,1–0,17 s).
- Automático vs dirección: en todos los juegos automáticos con documentación de jugadores hay quejas por agarres no deseados (Dead Cells, Shinobi AoV, Silksong). Los que piden dirección (Dread, Spelunky) no muestran esas quejas en lo que encontré. No es evidencia fuerte: no busqué quejas del caso contrario.

### Gaps
- No hay datos duros (frames, px) de ningún juego comercial moderno. Todo lo numérico viene de PoP, Celeste, Spelunky y GDevelop (código).

## 8. Recomendación concreta para el prototipo (ranger de 128 px de atlas, ≈102 px en pantalla, collider 40×112 de atlas, 60 Hz, clips a 12 fps)

### Takeaway
Agarre **automático sin botón, pero no con dirección contraria ni con abajo**, con test barrido. Ventana vertical asimétrica de ≈0,40 H. Snap con la mano clavada por frame (técnica PoP). Hang con el cuerpo **delante** del bloque (nuevo clip). Trepada de **0,28 s** (4 dibujos) cancelable por salto apenas los pies pasan el borde. Salida a **correr con velocidad** si se mantiene adelante. Salto desde el colgado (vertical, y hacia atrás con dirección contraria). Re-agarre geométrico más 0,15 s. Todas las cifras de abajo son **cálculo propio** sobre las referencias citadas en las secciones 1–7. Valores en px de atlas (128) y, entre paréntesis, de pantalla (×0,8).

### Cited Findings
Esta sección no agrega fuentes nuevas. Cada número se apoya en: ventanas de Spelunky y PoP ([GML](https://github.com/yancharkin/SpelunkyClassicHD/blob/main/scripts/characterStepEvent/characterStepEvent.gml#L410-L504), [CTRL.S](https://github.com/jmechner/Prince-of-Persia-Apple-II/blob/master/01%20POP%20Source/Source/CTRL.S#L45-L48)); asentamiento y amortiguación de Celeste ([L3056–3078](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3056-L3078)); hop y `hopWaitX` ([L3291–3313](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3291-L3313)); test barrido de GDevelop ([L902–921](https://github.com/4ian/GDevelop/blob/master/Extensions/PlatformBehavior/platformerobjectruntimebehavior.ts#L902-L921)); anclaje de mano por frame de PoP ([seg008.c L1737](https://github.com/NagyD/SDLPoP/blob/master/src/seg008.c#L1737)); "jump cancels any animation" de The Lost Crown ([Xbox Wire](https://news.xbox.com/en-us/2024/01/17/prince-of-persia-the-lost-crown-builds-on-raymans-platforming-legacy/)); disparo colgado de Dread ([guía](https://samurai-gamers.com/metroid-dread/how-to-use-ledge-grab/)).

### Inferences
**A. Detección**
1. **Activación:** automática, sin botón. Se bloquea si hay dirección **contraria** a la pared, si se aprieta **abajo**, o durante el cooldown de soltada. Con dirección hacia la pared o neutro, agarra. Es un término medio entre la dirección obligatoria de Dread y Spelunky y el automático de Dead Cells y Hornet, que es el que genera quejas.
2. **vy:** mantener vy > −220 px/s (cerca del ápice o cayendo). Celeste es más estricto (vy ≥ 0) y Spelunky más laxo (cualquiera). Sin límite superior de caída: con test barrido no hace falta el `grabspeed` de PoP.
3. **Test barrido:** comparar el punto de mano del frame anterior con el actual contra la línea del borde, como `_canGrab` de GDevelop. Si cruzó o está dentro de la ventana, agarra. Así una caída de 15–20 px por frame no se saltea la ventana.
4. **Ventana vertical** (mano respecto del borde): desde **0,10 H por encima** (≈13 px atlas, 10 px pantalla) hasta **0,30 H por debajo** (≈38 px, 31 px). Total ≈0,40 H (51 px, 41 px). Agarrar un poco tarde y "estirar los brazos" es lo que hace PoP (hasta ≈0,7 H). El tope de 0,30 H evita teletransportes visibles.
5. **Ventana horizontal**, medida **desde la cara del collider** hasta la cara de la pared: **0–12 px** atlas (0–10 px pantalla, ≈0,1 H). Referencias: Celeste 2 px = 0,125 H; GDevelop 10 px; Spelunky contacto. Dejá de medir desde la mano del clip.
6. **Zona de auto-mantle (opcional):** si la mano ya pasó la ventana por arriba (más de 0,10 H) y los pies están a ≤ **0,30 H** por debajo del borde (≈38 px, 31 px), con dirección hacia la pared, hacé un **mantle corto** de 0,12–0,15 s directo a parado o corriendo, en lugar de colgarse. Es el equivalente al climb hop de Celeste (salta cuando la mano pasa el borde; sube 0,5 H). Exigí dirección hacia la pared por las quejas de Shinobi AoV.

**B. Snap y dibujo de la mano**
7. Collider: cara frontal al ras de la cara de la pared.
8. Vertical: el **punto de mano** del dibujo actual (tabla por frame, medida sobre el clip nuevo) va 2–3 px de atlas por debajo de la línea del borde, así los dedos asoman 1–3 px por encima (PoP: 1 px).
9. Durante el loop de colgado, mantené la mano clavada con **offsets por frame** (dx, dy por dibujo, como `frame_table_kid` de PoP), no con el pivote de pies.
10. Entrada: amortiguá en vez de cortar. Lerp de 0,08–0,12 s a la posición de snap (Celeste: ClimbNoMoveTime 0,1 s y vy × 0,2). El agarre de 0,2 s actual puede bajar a **3 dibujos × 0,04 s = 0,12 s**.
11. Con el clip nuevo (cuerpo contra la cara de la pared, manos sobre la superficie superior), dibujá el sprite **delante** del bloque. El truco de dibujarlo detrás solo hace falta con el clip viejo de "barra invisible", porque la barra queda sobre el centro del cuerpo y obliga a superponer cuerpo y bloque.

**C. Desde el colgado (sin límite de tiempo; PoP se suelta a los 3,6 s y Celeste a los 11 s por stamina, en un run-and-gun no hace falta)**
12. **Arriba o hacia la pared → trepar**, buffereado desde el agarre y ejecutado a partir de 0,1 s. Nada del stun de 1 s de PoP.
13. **Salto (neutro o arriba) → salto vertical** con la velocidad del salto de suelo, como Spelunky. Hornet incluso gana altura. Saca al personaje por encima del borde sin animación de trepada.
14. **Salto + dirección contraria → salto hacia atrás:** vx ≈ velocidad de correr alejándose, vy ≈ 80–100 % del salto. Es el wall jump de Celeste: 130 px/s horizontal con 0,16 s de dirección forzada.
15. **Abajo (o abajo + salto) → soltar:** vy 0–60 px/s (Spelunky arranca en 0). El empuje de 6 px deja de hacer falta con el clip nuevo.
16. **Re-agarre:** bloquear **el mismo borde** hasta que la mano baje más que la ventana (0,30 H bajo el borde), más un timer de **0,15 s** (Spelunky 0,1–0,17 s; hoy 0,35 s). Otro borde se puede agarrar enseguida.
17. **Daño colgado:** no encontré i-frames documentados en ninguna referencia. Propuesta de diseño: sin invulnerabilidad; un golpe suelta la cornisa con knockback.
18. **Disparo colgado:** Dread lo permite (incluso apuntar libre). Para v1, no dispares colgado: necesitaría 1–3 dibujos extra (colgado con un brazo apuntando hacia atrás o abajo). Sí permití disparo buffereado a la salida de la trepada.

**D. Trepada (reemplaza el lerp de 0,14 s + crouch_out de ≈0,36 s)**
19. **Duración: 0,28 s = 17 f** (rango aceptable 0,25–0,32 s). Con **4 dibujos** a ~0,07 s (12 fps nominal), o 5 a 0,055 s.
20. **Movimiento por código, no por el clip:**
    - Fase 1 (0–0,12 s): subida con ease-out hasta que los pies queden ≈0,1 H bajo el borde.
    - Fase 2 (0,12–0,22 s): avance de **0,35 H** (≈45 px atlas, 36 px pantalla; PoP avanza 0,33 H) más el resto de la subida.
    - Fase 3 (0,22–0,28 s): asentar.
    - El desplazamiento vertical total es el largo de colgado (mano a pies). En PoP es 1,39 H. Medilo sobre el clip nuevo.
21. **Empuje horizontal estilo `hopWaitX`:** el avance horizontal arranca recién cuando el frente del collider pasa el borde.
22. **Cancelación:** desde que los pies pasan la línea del borde (≈fase 2), un salto cancela el resto, pone el collider arriba y salta desde el suelo (The Lost Crown: "a jump… could cancel any animation"). Antes de eso, un salto se convierte en el salto vertical del punto 13.
23. **Salida con inercia:** si se mantiene adelante al final (o en los últimos 0,1 s), entrá directo a **correr con vx = 60–80 % de la velocidad máxima** y saltá el crouch_out. Neutro → idle (o crouch_out si querés peso). Hoy termina con vx = 0. El hop de Celeste lanza a 100 px/s, ≈1,1 veces su MaxRun, aunque después frena por el bloqueo de 0,2 s.
24. **Buffer:** guardá salto o disparo apretados en los últimos 0,1 s de la trepada y ejecutalos en el primer frame de salida, con el mismo buffer que el resto del juego.

**E. Clips a generar (Seedance, image-to-video, cámara lateral fija)**
25. **Hang nuevo** (reemplaza la "barra invisible"):
    - Encuadre: perfil mirando a la derecha. Un bloque de color plano a la derecha (escena de referencia que después se recorta) y el personaje colgado de su esquina superior izquierda.
    - Pose: brazos estirados, palmas sobre la superficie superior, dedos curvados sobre el filo, pecho y rodillas cerca de la cara de la pared, pies colgando sin tocar el piso.
    - Loop sutil de respiración o balanceo, 2–4 dibujos. PoP balancea el cuerpo y deja la mano fija.
    - Largo de mano a pies esperado ≈1,3–1,4 H (PoP 1,39 H).
26. **Climb** (arranca en el primer frame del hang nuevo y termina en el primer frame de run o en idle). Fases según el reparto de PoP, comprimidas para acción:
    1. **Tirón (≈35 %):** codos se flexionan, el pecho sube hasta el borde, las rodillas se recogen.
    2. **Pasar el borde (≈25 %):** las manos empujan hacia abajo sobre la superficie, los codos quedan por encima del borde, el torso se inclina sobre la superficie, una rodilla o pie sube al borde.
    3. **Incorporarse (≈40 %):** el pie de atrás sube, el cuerpo se endereza hacia adelante y termina en el primer paso de carrera, no parado.
    - Generá ≈1–1,5 s de clip, porque los clips de IA suelen salir lentos. Elegí **4 dibujos clave**: brazos flexionados con el pecho al borde; codos arriba con rodilla subiendo; rodilla o pie sobre el borde con torso bajo; impulso al primer frame de run.
    - Medí en cada uno el punto de mano (fases 1–2) y el pivote de pies (fases 2–3) para la tabla de anclas por frame.
27. **Alternativa barata:** un "flip-up" estilo Strider de 2–3 dibujos (voltereta corta desde el colgado). Tolera más deformación del video que un mantle realista, porque la pose en giro es menos legible y los errores se notan menos.

### Gaps
- Falta el largo real de mano a pies del ranger en un hang con el cuerpo contra la pared. Define el desplazamiento vertical de la trepada y conviene medirlo sobre el clip nuevo.
- No hay datos de referencia para la duración de mantles de Hornet, Samus o Joe Musashi. El rango de 0,25–0,32 s es inferencia, apoyada en el climb hop de Celeste (≈0,13–0,2 s) y en la trepada actual (0,36 s).
- Daño colgado e i-frames: s/d en todas las referencias. La propuesta del punto 17 es de diseño, no citada.
