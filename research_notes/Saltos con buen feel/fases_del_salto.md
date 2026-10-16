# Fases del salto: anticipación, despegue, subida, ápice, caída y aterrizaje

Alcance: cómo animan el salto los plataformeros de acción, por fase: cuántos dibujos hay, cuánto dura cada uno y cómo se elige el cuadro según vy. No repito la física (altura, tiempos, gravedades, coyote, buffer), que ya está en `reports/Movimiento y disparo en run-and-guns.md` y en `research_notes/Movimiento y disparo en run-and-guns/`. Cuando uso datos de esas notas lo aclaro ("nota previa").

Convenciones:
- H = altura de pie del personaje en su propio juego.
- Tick = un cuadro de juego a 60 Hz (16,7 ms). "fr12" = un cuadro de animación a 12 fps (83 ms = 5 ticks).
- **conteo propio**, **medición propia** y **cálculo propio** marcan trabajo mío. s/d = sin dato.

Metodología y seguridad:
- Leí código en GitHub (Celeste oficial; descompilados de Hollow Knight y Cuphead; desensamblado de Super Mario World) y la documentación generada de Broforce.
- Vi las láminas de sprites a través de Wayback Machine. Spriters Resource devuelve 403 directo, así que no lo forcé. Bajé solo imágenes a la carpeta temporal de la sesión, nunca al repo.
- grep.app mostró un "Vercel Security Checkpoint", así que no lo usé. No abrí tcrf.net. No vi texto de prompt-injection en ninguna página.

---

## 1. Anticipación: ¿se demora el despegue?

### Takeaway
Ningún plataformero de acción revisado demora el despegue. Celeste, Hollow Knight, Cuphead, Super Mario World, Mega Man y Broforce aplican la velocidad de salto en el mismo tick del botón, o en el siguiente paso fijo. El "agacharse" o no existe o es puramente visual. El contraejemplo es Smash Bros, con un jumpsquat real de 3 ticks (0,05 s) en Ultimate y de 3 a 9 en juegos anteriores, y es una mecánica de juego de pelea. Los animadores de juegos (Pedro Medeiros, Jonathan Cooper) recomiendan evitar la anticipación en el personaje que controla el jugador.

### Cited Findings
- **Celeste.** `NormalUpdate` llama a `Jump()` en cuanto `Input.Jump.Pressed` y hay suelo o coyote ([Player.cs L2970](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2970)). `Jump()` fija `Speed.Y = JumpSpeed` (−105 px/s) en ese mismo tick y además **estira** el sprite a escala (0,6, 1,4), es decir más angosto y más alto. No hay squash previo ([Player.cs L1660–1693](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1660-L1693), escala en L1688). La escala vuelve a 1 a razón de 1,75 por segundo ([L1165–1166](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1165-L1166)). Eso da 0,4/1,75 = **0,23 s ≈ 14 ticks** de recuperación del estirón (cálculo propio, ya en nota previa).
- **Hollow Knight** (código descompilado por terceros con hooks del Modding API; no es fuente oficial):
  - `HeroJump()` pone `cState.jumping = true`, crea el efecto de polvo y el sonido.
  - `Jump()` aplica `rb2d.velocity.y = JUMP_SPEED` en cada paso de física mientras `jump_steps <= JUMP_STEPS`. Ninguno de los dos tiene espera ni pose previa ([HeroController.cs L628–646, L2879–2889](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L2879-L2889)).
  - La animación de aire arranca en el cuadro 0 del clip "Airborne" en cuanto `cState.jumping` es verdadero ([HeroAnimationController.cs L340–345](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroAnimationController.cs#L326-L357)).
- **Cuphead.** En el Animator, la transición `Idle → Jump` y `Run → Jump` es la condición `Grounded == false`, sin exit time ([animator_player.controller](https://github.com/jmxamongusmodder/cuphead-decomp/blob/HEAD/Assets/AnimatorController/animator_player.controller); parseo propio de transiciones). No hay estado de preparación: el salto es directamente la bola en loop. Ms. Chalice (DLC) tampoco tiene preparación: `Idle_Chalice → Jump_Launch` también salta con `Grounded == false` (mismo archivo).
- **Super Mario World.** Al apretar salto, el mismo bloque de código fija `PlayerYSpeed` desde la tabla de salto y pone la pose de aire (`PlayerInAir = $0B`) ([SMWDisX bank_00.asm L9979–9993](https://github.com/IsoFrieze/SMWDisX/blob/HEAD/bank_00.asm#L9979-L9993)). No hay pose previa.
- **Mario NES y Mega Man NES:** el salto sale en el tick en que se detecta la pulsación sobre suelo (nota previa `mario_megaman.md`, a partir de [smbdis.asm](https://gist.github.com/1wErt3r/4048722) y [Bisqwit maincode](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt)).
- **Smash Bros (contraejemplo):**
  - "Jump squat" es el tiempo entre el input y el momento en que el personaje deja el suelo.
  - **Ultimate:** casi todos tardan **3 ticks** (0,05 s). Kazuya tarda 7 y Giga Bowser 15.
  - **Melee:** de 3 ticks (Fox, Sheik, Pikachu…) a 8 (Bowser).
  - **Brawl:** de 4 a 9 (Snake).
  - **Smash 4:** de 4 a 8.
  - Durante el jumpsquat se decide short hop o full hop según si se suelta el botón — [SmashWiki, Jump](https://www.ssbwiki.com/Jump).
- **Pedro Medeiros (saint11, artista de Celeste y TowerFall)**, lámina "Jump" (texto leído del GIF; **conteo propio** de dibujos):
  - El paso "1. ANTICIPATION?" dice textual: "Avoid on player controlled characters". Muestra 4 dibujos de anticipación, como ejemplo de lo que hay que evitar.
  - El resto del salto se arma sin anticipación: going up, invert, fall y contact.
  - Fuentes: [índice de tutoriales](https://saint11.art/blog/pixel-art-tutorials/), [Jump.gif](https://saint11.art/img/pixel-tutorials/Jump.gif). El GIF tiene 24 cuadros a 0,08 s, porque el ejemplo animado corre a 12,5 fps (medición propia con ffprobe).
- **Pedro Medeiros**, lámina "Squash and Stretch":
  - "Stretching is a good and cheap way of smoothing fast animations".
  - "Add squash and stretch tweens to your game code for more dynamism".
  - Regla principal: al cambiar el ancho, cambiar también el alto, para conservar la masa.
  - Fuente: [Squash.gif](https://saint11.art/img/pixel-tutorials/Squash.gif).
- **Jonathan Cooper** (*Game Anim*, extracto en Game Developer):
  - Sobre la anticipación, los diseñadores piden "as little as possible" y los animadores "as many frames as possible". Si es muy larga, "the move will feel unresponsive, removing agency from the player".
  - En NPCs el telegraphing "is desirably longer".
  - Ejemplo de anticipación: "a crouch before a jump". La recuperación del aterrizaje es follow-through. Se puede marcar "a frame where the player regains control before the end".
  - Fuente: [The 12 principles of animation in video games](https://www.gamedeveloper.com/production/the-12-principles-of-animation-in-video-games).

### Inferences
- La práctica dominante es **0 ticks de demora**. El "squash de preparación" se reemplaza por un **estirón en el despegue**, hecho por código (Celeste) o por el primer dibujo de subida (saint11). Incluso el jumpsquat más corto de Smash (3 ticks = 0,05 s) equivale a 0,6 fr12. A 12 fps no da ni para mostrar un dibujo entero, así que una anticipación dibujada a 12 fps implicaría ≥ 1 fr12 = 83 ms de demora. Eso es más que cualquier Smash moderno, para un run-and-gun.
- Si se quiere "leer" un agache sin demora, se puede mostrar el dibujo agachado **durante el primer tick o los dos primeros (16–33 ms) mientras el cuerpo ya sube**. Pedro lo desaconseja igual, así que lo marco como opcional.

### Gaps
- No encontré declaraciones de los animadores de Cuphead (Studio MDHR) ni de Hollow Knight (Ari Gibson) sobre anticipación de salto.
- No encontré datos de anticipación de Ori ni de Dead Cells. El artículo de pipeline de Dead Cells habla de un personaje de 50 px de alto y de animar "with the least amount of frames possible", pero no menciona saltos ([Game Developer, Dead Cells deep dive](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)).
- No verifiqué con datos duros Mega Man X, Metal Slug, Shovel Knight ni Ori. Mega Man X tiene un dibujo de patas flexionadas al inicio de la serie (ver §2), pero sin código no sé si se muestra con el cuerpo ya en el aire.

---

## 2. Fases: dibujos y tiempos por fase en juegos de referencia

### Takeaway
Hay dos familias:
- **Salto de pocos dibujos elegidos por estado o vy.** SMW tiene 1 de subida y 1 de caída. Mario NES y Mega Man tienen 1 sostenido. Broforce tiene 6 por capa, indexados por velocidad.
- **Un clip en el tiempo que arranca en un cuadro u otro según el estado.** Hollow Knight usa un único clip "Airborne". Cuphead usa una bola en loop de 8 dibujos a 30 fps. Ms. Chalice usa launch de 8 a 30 fps, descend de 8 en loop y hold de 4.

Las láminas más ricas (Mega Man X, Metal Slug, el tutorial de saint11) tienen entre 7 y 13 dibujos de salto en total. La mayoría de los juegos de acción **no tienen clip de aterrizaje** o lo tienen muy corto y cancelable.

### Cited Findings
**Tabla resumen** (dibujos por fase; los "conteo propio" son lectura mía de láminas sin etiquetas):

| Juego | Despegue | Subida | Ápice | Caída | Aterrizaje | Fuente |
|---|---|---|---|---|---|---|
| Celeste | 0 (estirón por código 0,6×1,4) | jumpSlow / jumpFast (s/d de cuadros) | — (por física: media gravedad si \|vy\|<40) | fallSlow / fallFast (s/d) | sin clip; squash por código; `runStumble` en caída dura corriendo | [Player.cs L1300–1331](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1300-L1331), [L2554–2566](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2554-L2566) |
| Hollow Knight | 0 | clip "Airborne" desde el cuadro 0 | entrada en el cuadro 3 si no sube ni cae | entrada en el cuadro 5 si cae sin haber saltado; cuadro 7 al entrar a una escena por arriba | "Land" (solo si queda quieto), "HardLand" (con bloqueo) | [HeroAnimationController.cs L326–366](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroAnimationController.cs#L326-L366) |
| Cuphead / Mugman | 0 | bola 8 dibujos @30 fps en loop (0,267 s = 16 ticks) durante todo el salto | — | (misma bola) | sin clip: Jump→Idle al tocar suelo, más polvo y sonido | [anim_player_jump.anim](https://github.com/jmxamongusmodder/cuphead-decomp/blob/HEAD/Assets/AnimationClip/anim_player_jump.anim), [LevelPlayerAnimationController.cs L923–931](https://github.com/jmxamongusmodder/cuphead-decomp/blob/HEAD/Assets/Scripts/Assembly-CSharp/LevelPlayerAnimationController.cs#L923-L931) |
| Ms. Chalice (Cuphead DLC) | 0 | `Jump_Launch` 8 @30, sin loop (0,267 s) | — | `Jump_Descend` 8 @30 en loop, luego `Descend_Hold` 4 @30 en loop (0,133 s) | sin clip | [anim_player_jump_chalice_launch.anim](https://github.com/jmxamongusmodder/cuphead-decomp/blob/HEAD/Assets/AnimationClip/anim_player_jump_chalice_launch.anim), [..._descend.anim](https://github.com/jmxamongusmodder/cuphead-decomp/blob/HEAD/Assets/AnimationClip/anim_player_jump_chalice_descend.anim), [..._descend_hold.anim](https://github.com/jmxamongusmodder/cuphead-decomp/blob/HEAD/Assets/AnimationClip/anim_player_jump_chalice_descend_hold.anim) (conteo propio de keyframes) |
| Super Mario World | 0 | 1 pose ($0B) | — | 1 pose ($24) | (no revisado) | [bank_00.asm L10446–10456](https://github.com/IsoFrieze/SMWDisX/blob/HEAD/bank_00.asm#L10446-L10456) |
| Mario NES / Mega Man NES | 0 | 1 dibujo sostenido todo el salto | — | (el mismo) | Mega Man: sprite $0F de "hitting the ground", ≈4 ticks (tentativo) | nota previa `mario_megaman.md` y `gaps_metalslug_celeste_megaman.md` ([Bisqwit](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt)) |
| Broforce | s/d | 6 dibujos de cuerpo + 6 de arma, indexados por velocidad (3 estados: sube rápido, normal, cae rápido) | (estado "normal") | (estado "cae rápido") | rodada de 0,133 s si cae rápido | [Broforce-Docs](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/TestVanDammeAnim-Documentation.xml); nota previa `cuphead_broforce.md` |
| Mega Man X | 1 (patas flexionadas) | 2 | 1 (recogido, brazo arriba) | 2 | 1 (agachado) | **conteo propio**, lámina [X, SR 1225 vía Wayback](https://web.archive.org/web/20240223052140/https://www.spriters-resource.com/snes/mmx/sheet/1225/): 7 dibujos sin buster y otros 7 con buster |
| Metal Slug (Marco) | s/d | salto parado: 6 piernas + 6 torso; salto corriendo: 6 + 6 | — | (dentro de las 6) | 4 dibujos de aterrizaje / agachado a parado (rip compuesto) | nota previa `metal_slug_sheets.md` ([SR 11225 vía Wayback](https://web.archive.org/web/20230512095229/https://www.spriters-resource.com/resources/sheets/11/11225.png)) y `metal_slug_carl27_rip.md` (conteo propio) |
| Shovel Knight | s/d | 1 (piernas recogidas, pala arriba) | — | 1 (piernas abiertas) | ¿1? (pose agachada; rol no confirmado) | **conteo propio**, lámina sin etiquetas [SR 67117 vía Wayback](https://web.archive.org/web/20230814211012/https://www.spriters-resource.com/pc_computer/shovelknight/sheet/67117/): 3 filas de 1 dibujo justo después de la carrera de 6 |
| saint11 (tutorial) | anticipación 4 ("evitar") | "Going up" 2 ("simple animation, doesn't loop") | "Invert" 3 ("bridge between up and fall") | "Fall" 2 (brazos arriba, cabeza mira abajo, pelo y ropa flamean) | "Contact" 4 ("squash as much as you can"; "can be a long animation that's interrupted if necessary") | [Jump.gif](https://saint11.art/img/pixel-tutorials/Jump.gif) (conteo propio) |

**Detalles con números:**
- **Hollow Knight.** `PlayFromFrame("Airborne", 0)` si está saltando, `("Airborne", 5)` si está cayendo y `("Airborne", 3)` en otro caso. Las tres llamadas son solo `if (!IsPlaying("Airborne"))`: una vez que el clip arrancó, **sigue por tiempo** y el estado no lo reinicia ([L340–357](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroAnimationController.cs#L326-L357)). El cuadro 7 se usa al entrar a una escena por arriba o al esperar para entrar ([L193–213](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroAnimationController.cs#L190-L215)).
- **Cuphead.** Las tres curvas del clip (Cuphead, Mugman y un tercer path) tienen 8 keyframes cada una, con `m_SampleRate: 30`, `m_LoopTime: 1` y `m_StopTime: 0.2666667` ([anim_player_jump.anim](https://github.com/jmxamongusmodder/cuphead-decomp/blob/HEAD/Assets/AnimationClip/anim_player_jump.anim); conteo propio). Coincide con la nota previa ("Jump ball 8 @30").
- **Ms. Chalice:**
  - `Jump_Launch` pasa a `Jump_Descend` cuando el clip termina (exit time 1 = 0,267 s = 16 ticks) o cuando `MoveY < 0` ([animator_player.controller](https://github.com/jmxamongusmodder/cuphead-decomp/blob/HEAD/Assets/AnimatorController/animator_player.controller); parseo propio).
  - `MoveY` es el signo del desplazamiento entero por paso de física (`v.y = (int)v.y`), así que vale −1 solo cuando baja ≥ 1 unidad por paso ([LevelPlayerMotor.cs L252–257](https://github.com/jmxamongusmodder/cuphead-decomp/blob/HEAD/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs#L252-L257)).
  - `Descend` pasa a `Descend_Hold_No_Lines` y de ahí a `Descend_Hold` cuando el contador de loops llega a 2 (mismo controller).
- **Metal Slug** (nota previa `metal_slug.md`, **medición propia** sobre video): arco ≈22 ticks de subida, ≈8 de ápice (0,14 s) y ≈22 de caída. El salto parado sube más rápido, cuelga más y cae más rápido, pero aterriza en el mismo cuadro que el salto en movimiento ([TASVideos 9399S](https://tasvideos.org/9399S)).

### Inferences
- **Hollow Knight, cálculo propio por los índices de entrada:**
  - El clip "Airborne" tiene **≥ 8 cuadros**.
  - Cuadros 0–2: subida. 3–4: zona del ápice. 5–6: inicio de caída. 7 en adelante: caída sostenida.
  - Usar un único clip temporal funciona porque la subida tiene duración casi fija (pasos de `JUMP_STEPS`). El clip se dibuja "a medida" del arco.
  - Para caer de un borde sin saltar se entra directo en la caída (cuadro 5), no en la subida.
- **Promedio de las láminas con fases dibujadas** (Mega Man X, saint11, Metal Slug):
  - Subida: 2 dibujos.
  - Ápice o inversión: 1 a 3.
  - Caída: 2, el último en loop.
  - Aterrizaje: 1 a 4.
  - Despegue: 0 a 1, y cuando existe se muestra con el cuerpo ya moviéndose (inferencia).
- El prototipo tiene 2 de prep, 5 de aire y 3 de aterrizaje. En cantidad está en rango. El problema está en el reparto: 2 de prep que no se deberían mostrar como demora, 1 solo de ápice y un segundo dibujo de caída que nunca aparece (ver §3 y §7).

### Gaps
- **Celeste:** frames y `delay` de jumpSlow, jumpFast, fallSlow, fallFast, fallPose y land en `Sprites.xml`. El archivo vanilla está solo en la instalación del juego (`Content/Graphics/Sprites.xml`). No encontré espejo público, y el wiki de Everest solo muestra el ejemplo de Theo Crystal (`delay="0.08"`) ([Reskinning Entities](https://github.com/EverestAPI/Resources/wiki/Reskinning-Entities)). Si alguien del equipo tiene Celeste en PC, se resuelve en un minuto.
- **Hollow Knight:** cantidad de cuadros y fps de los clips tk2d "Airborne", "Land", "HardLand" y "Double Jump". No están en el código; están en los assets.
- **Mega Man X y Shovel Knight:** duraciones por dibujo (necesitan ROM o emulador, fuera de alcance). En Shovel Knight la asignación de roles es tentativa.
- **Dead Cells y Ori:** sin datos de dibujos por fase.

---

## 3. Umbrales de vy para elegir subida, ápice y caída

### Takeaway
Los umbrales publicados son pocos y bajos:
- **Celeste y SMW** cortan subida/caída en **vy = 0**. Celeste además pasa a fallFast solo al llegar a la terminal (160 px/s = 1,0 × terminal).
- **Broforce** usa una banda de ápice asimétrica, de +20 u/s subiendo a −55 u/s cayendo: 0,08 v0 subiendo y 0,21 v0 cayendo. A su gravedad, la banda dura ≈ 0,07 s.
- **Hollow Knight y Cuphead** no usan vy. Usan el estado (saltando / cayendo) más un clip temporal.

El prototipo tiene el problema contrario: su banda de ápice es angosta (0,053 s) y el primer dibujo de subida queda congelado 0,28 s.

### Cited Findings
- **Celeste:**
  - En el aire, si `Speed.Y < 0` reproduce jumpFast (si `|vx| > MaxRun` o ya venía latcheado `fastJump`) o jumpSlow.
  - Si no, reproduce fallFast cuando `fastJump || Speed.Y >= MaxFall`, y fallSlow en otro caso ([Player.cs L1300–1331](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1300-L1331)).
  - `MaxFall = 160`, `FastMaxFall = 240`, `JumpSpeed = −105` ([L23–49](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L23-L49)).
  - Fracciones (cálculo propio): fallFast arranca a 160/105 = **1,52 v0 = 1,0 × terminal normal**. Antes de eso, toda la caída es fallSlow.
  - `fastJump` se resetea al tocar suelo ([L1243](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1243)).
- **Super Mario World:** cada tick que `PlayerYSpeed` es ≥ 0 y `PlayerInAir == $0B` (salto normal), cambia a `$24` (pose de caída). Si era `$0C` (salto con P-meter lleno), no cambia y la pose se sostiene todo el salto ([bank_00.asm L10446–10456](https://github.com/IsoFrieze/SMWDisX/blob/HEAD/bank_00.asm#L10446-L10456)). Umbral: **vy = 0**.
- **Broforce:**
  - `AnimateActualJumpingFrames` maneja tres estados: "fast rising (yI > 20f), fast falling (yI < −55f), and normal jumping" ([Broforce-Docs](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/TestVanDammeAnim-Documentation.xml)).
  - Contexto, de la misma fuente: `_jumpForce` 260 u/s, `maxFallSpeed` −400 u/s y gravedad 1100 u/s² (nota previa).
  - Fracciones (cálculo propio): +20 = **0,077 v0**; −55 = **0,21 v0 = 0,14 × terminal**. Banda "normal": 20/1100 + 55/1100 = 0,018 + 0,050 = **0,068 s ≈ 4 ticks**, cargada hacia la caída.
- **Hollow Knight:** selecciona por `cState.jumping` / `cState.falling`. `falling` se activa con `rb2d.velocity.y <= −1e−6` sin tocar suelo, o sea a vy apenas negativa en sus ejes ([HeroController.cs L3330–3357](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L3330-L3357)). Una vez que el clip corre, ese cambio no lo reinicia (ver §2).
- **Cuphead:** la bola no depende de vy. Chalice pasa de launch a descend al terminar el clip (0,267 s) o al bajar ≥ 1 unidad por paso (ver §2).
- **saint11:** en "3. INVERT", "When changing the Y speed, use this as a bridge between up and fall" ([Jump.gif](https://saint11.art/img/pixel-tutorials/Jump.gif)). No da un umbral numérico.
- **Umbrales actuales del prototipo como fracción** (cálculo propio, con v0 = 1067 y terminal 1400):
  - −240 = −0,225 v0.
  - −60 = −0,056 v0.
  - +160 = 0,114 × terminal = 0,15 v0.
- **Tiempos del salto completo del prototipo con esos umbrales** (cálculo propio: subida vy = −1067 + 2963·t, caída vy = 4898·(t − 0,360), aterriza a 0,640 s con vy = 1372 px/s):

  | Dibujo actual | Condición | Intervalo | Duración | ticks | fr12 |
  |---|---|---|---|---|---|
  | rise 0 | vy < −240 | 0–0,279 s | 0,279 s | 16,7 | 3,4 |
  | rise 1 | −240 ≤ vy < −60 | 0,279–0,340 | 0,061 s | 3,6 | 0,7 |
  | apex | −60 ≤ vy < +160 | 0,340–0,393 | 0,053 s | 3,2 | 0,6 |
  | fall 0 | vy ≥ +160 | 0,393–0,640 | 0,247 s | 14,8 | 3,0 |
  | fall 1 | nunca | — | 0 | 0 | 0 |

### Inferences
- Los umbrales del prototipo están **muy pegados al ápice**. rise 0 se congela 3,4 fr12, y rise 1 y apex duran menos de 1 fr12 cada uno, así que se ven como un parpadeo. fall 0 se congela 3 fr12.
- Referencias para traducir umbrales:
  - Celeste y SMW cortan en 0.
  - Broforce usa una banda de ≈0,07 s cargada a la caída.
  - En Metal Slug el ápice "cuelga" ≈0,14 s (medición previa).
- Una regla práctica que sale de esto (inferencia): definir la banda del ápice **por tiempo** (±0,05–0,07 s alrededor de vy = 0) y convertirla a vy con la gravedad de cada lado: umbral de subida = g_sube·Δt y umbral de bajada = g_baja·Δt. Con gravedades asimétricas como las del prototipo (4898/2963 = 1,65×), el umbral de bajada tiene que ser ≈1,65 veces el de subida para que el ápice quede centrado en el tiempo.
- Celeste reserva fallFast para la terminal. En el prototipo eso es vy ≥ 1400, que un salto completo no alcanza (aterriza a 1372 = 98 %). Si se copia tal cual, fall 1 seguiría sin verse en saltos sobre plano. Por eso en §7 propongo un umbral de 0,6 × terminal para el segundo dibujo de caída.

### Gaps
- Cuphead no publica umbrales de vy, y Hollow Knight no usa vy para elegir cuadro. No encontré otros juegos con umbrales numéricos en código abierto (GMTK Platformer Toolkit: el devlog "Behind the code" no cubre animación — [itch.io](https://gmtk.itch.io/platformer-toolkit/devlog/395523/behind-the-code)).

---

## 4. Ápice: ¿dibujo dedicado o pose recogida sostenida?

### Takeaway
Cuando hay un dibujo de ápice, es una pose "recogida" o de "inversión" entre subida y caída: Mega Man X tiene 1, saint11 3, y en Hollow Knight los índices sugieren 2 cuadros (3–4). Dura del orden de **0,07–0,14 s**: Broforce ≈0,07 s por banda de vy y Metal Slug ≈0,14 s medido. Celeste no tiene dibujo de ápice. Lo resuelve con física: media gravedad mientras |vy| < 40 con el botón apretado.

### Cited Findings
- **saint11:** "Invert" con 3 dibujos como puente entre subida y caída ([Jump.gif](https://saint11.art/img/pixel-tutorials/Jump.gif); conteo propio).
- **Mega Man X:** 1 dibujo recogido, brazo arriba y piernas flexionadas, entre los 2 de subida y los 2 de caída (**conteo propio**, [lámina vía Wayback](https://web.archive.org/web/20240223052140/https://www.spriters-resource.com/snes/mmx/sheet/1225/)).
- **Hollow Knight:** si el personaje no está ni subiendo ni cayendo, el clip "Airborne" entra por el cuadro 3 ([L354–357](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroAnimationController.cs#L326-L357)).
- **Broforce:** estado "normal jumping" entre yI +20 y −55 ([Broforce-Docs](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/TestVanDammeAnim-Documentation.xml)). Duración ≈0,068 s (cálculo propio, §3).
- **Metal Slug:** ≈8 ticks (0,14 s) de "colgado" en el ápice (nota previa `metal_slug.md`, medición propia).
- **Celeste:** apex hang físico con media gravedad si |vy| < 40 px/s (0,38 v0) y el botón apretado. Agrega ≈0,09 s de colgado (nota previa `celeste_jump_feel.md`, [Player.cs L2952–2957](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2952-L2957)).
- **Cooper:** se usa squash en el ápice y estirón en la parte rápida del salto ([Game Developer](https://www.gamedeveloper.com/production/the-12-principles-of-animation-in-video-games), según el resumen de la página).

### Inferences
- Para el prototipo, ≈0,12 s de ápice (1,5 fr12) lo hace legible sin "flotar". El apex actual dura 0,053 s (0,6 fr12), por debajo de un cuadro de animación.
- Con 1 solo dibujo de ápice alcanza. Con 2 (subiendo→recogido, recogido→abriéndose) queda el "invert" de saint11 en versión mínima.

### Gaps
- Sin datos de duración del ápice en Hollow Knight, Cuphead (no tiene: bola), Ori ni Dead Cells.

---

## 5. Aterrizaje: dibujos, duración, suave vs duro y cancelación

### Takeaway
- Los juegos de acción más ágiles **no bloquean al jugador al aterrizar**:
  - Celeste no tiene clip de aterrizaje: aplica squash por código según la velocidad de caída.
  - Cuphead pasa de Jump a Idle directo, con polvo y sonido.
  - Hollow Knight muestra "Land" solo si el personaje queda quieto, y cualquier carrera o ataque la pisa.
- El aterrizaje "duro" es una variante aparte, que se dispara por tiempo o distancia de caída:
  - Hollow Knight tiene `HardLand`, que bloquea la entrada por `HARD_LANDING_TIME`.
  - Celeste tiene `runStumble` si cayó más de 50 px a velocidad terminal mientras corre.
  - Broforce rueda 0,133 s.
  - En Smash el aterrizaje cuesta 2 a 8 ticks.
- Pedro Medeiros: aplastar al máximo en el contacto, con una animación que puede ser larga pero interrumpible.

### Cited Findings
- **Celeste, aterrizaje** ([Player.cs L2554–2566](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2554-L2566)):
  - `squish = min(Speed.Y / FastMaxFall, 1)` con FastMaxFall = 240. Escala X = lerp(1, 1,6, squish) y escala Y = lerp(1, 0,4, squish).
  - Polvo si `Speed.Y >= MaxFall/2` (≥ 80 px/s = 0,5 × terminal).
  - `Sprite.Play(RunStumble)` si `highestAirY < Y − 50` (cayó más de 50 px) y `Speed.Y >= MaxFall` y `|Speed.X| >= MaxRun`.
  - Aterrizando a la terminal (160 px/s) da squish 0,667, es decir escala (1,4, 0,6). La recuperación a 1,75/s tarda 0,4/1,75 = **0,23 s ≈ 14 ticks**. Con fastfall (240) da (1,6, 0,4) y tarda **0,34 s ≈ 21 ticks** (cálculo propio; recuperación en [L1165–1166](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1165-L1166)).
  - El squash es visual: no hay estado de aterrizaje que bloquee.
  - 50 px ≈ 3,1 H visibles de Madeline (16 px) (cálculo propio con la H visible de la nota previa).
- **Hollow Knight** (descompilado):
  - **Land:**
    - `UpdateState` marca `playLanding` solo en la transición `airborne → idle` ([HeroAnimationController.cs L90–105](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroAnimationController.cs#L90-L105)). Si aterriza corriendo, el estado pasa a `running` y se reproduce Run, sin Land.
    - Mientras corre "Land", `CanPlayIdle()` devuelve falso. Al terminar el clip, `AnimationCompleteDelegate` vuelve a Idle ([L395–417](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroAnimationController.cs#L395-L417)).
    - Correr, girar, atacar o saltar entran por otras ramas, así que Land es interrumpible (inferencia de la estructura de `UpdateAnimation`).
  - **Aterrizaje suave:** `BackOnGround()` crea `softLandingEffectPrefab` (polvo) y vibración, como mucho una vez cada `LANDING_BUFFER_STEPS = 5` pasos de física ([HeroController.cs L3673–3700, L4606–4627](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L3673-L3700)).
  - **Aterrizaje duro:**
    - Mientras cae (vy < 0, sin wall slide), suma `fallTimer`. Si `fallTimer > BIG_FALL_TIME`, activa `willHardLand` y un rumble de caída ([L3330–3357](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L3330-L3357)). Agarrarse a una pared lo cancela.
    - Al aterrizar así, `DoHardLanding()` resetea el input, cancela el ataque, pone el estado `hard_landing`, suena HARD_LANDING y crea el efecto ([L2952–2961](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L2952-L2961)).
    - La animación es "HardLand" ([HeroAnimationController.cs L363–366](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroAnimationController.cs#L363-L366)). Termina cuando `hardLandingTimer > HARD_LANDING_TIME` ([L4697–4704](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L4697-L4704)).
- **Cuphead:** `Jump → Idle` con `Grounded == true`, sin exit time ([animator_player.controller](https://github.com/jmxamongusmodder/cuphead-decomp/blob/HEAD/Assets/AnimatorController/animator_player.controller)). `OnGrounded()` reproduce el sonido "player_grounded" y crea `groundedEffect` ([LevelPlayerAnimationController.cs L923–931](https://github.com/jmxamongusmodder/cuphead-decomp/blob/HEAD/Assets/Scripts/Assembly-CSharp/LevelPlayerAnimationController.cs#L923-L931)). No hay clip de aterrizaje del personaje.
- **Broforce:**
  - `doRollOnLand`: rueda al aterrizar si yI < −300 (0,75 × terminal). Otra entrada de la misma doc (`CanDoRollOnLand`) dice −350 (0,875 × terminal): las dos entradas se contradicen.
  - "The roll lasts 0.133 seconds and prevents other actions" (≈8 ticks). `RollOnLand` dice "13 frames", que tampoco cuadra con 0,133 s ([Broforce-Docs](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/TestVanDammeAnim-Documentation.xml)).
- **Metal Slug:**
  - 4 dibujos de aterrizaje / agachado a parado (nota previa `metal_slug_carl27_rip.md`, conteo propio).
  - Al aterrizar disparando se suma una demora de 2 ticks que restaura la cadencia normal ([TASVideos 9815S](https://tasvideos.org/9815S), vía nota previa).
- **Mega Man NES:** sprite $0F "hitting the ground" ≈ 4 ticks (tentativo, nota previa `gaps_metalslug_celeste_megaman.md`, [Bisqwit](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt)).
- **Mega Man X:** 1 dibujo de aterrizaje agachado por serie (conteo propio, §2).
- **Smash** ([SmashWiki, Landing lag / Lag](https://www.ssbwiki.com/Landing_lag)):
  - Smash 64: aterrizaje liviano 4 ticks y pesado 8.
  - Melee: casi todos 4 ticks. La misma página también menciona 2 ticks para aterrizajes livianos, así que la fuente es ambigua.
  - Brawl: el aterrizaje pesado va de 2 a 6 ticks según el personaje.
  - Desde Brawl, el aterrizaje "pesado" ocurre tras caer a velocidad máxima durante un tiempo propio de cada personaje. Aterrizar cerca del ápice es más rápido.
- **saint11:** "5. CONTACT", con 4 dibujos: "Squash as much as you can on contact" y "This can be a long animation that's interrupted if necessary" ([Jump.gif](https://saint11.art/img/pixel-tutorials/Jump.gif)).
- **Cooper:** la recuperación del aterrizaje es follow-through. Hay que definir un cuadro en el que el jugador recupera el control antes del final ([Game Developer](https://www.gamedeveloper.com/production/the-12-principles-of-animation-in-video-games)).

### Inferences
- El patrón común tiene dos piezas. Primero, un **impacto siempre visible pero no bloqueante**: squash por código como Celeste o polvo y sonido como Cuphead y Hollow Knight. Segundo, **dibujos de recuperación solo si el jugador no hace nada**, como el Land de Hollow Knight o el "interrumpible" de saint11. El prototipo ya hace lo segundo (salta los 3 cuadros si hay movimiento). Le falta lo primero: hoy, si aterrizás corriendo, el impacto no se ve.
- **Variante dura:** en los ejemplos se decide por **tiempo o distancia de caída**, no solo por velocidad:
  - Hollow Knight usa `BIG_FALL_TIME`.
  - Celeste pide > 50 px de caída y vy en la terminal.
  - Smash pide tiempo a velocidad máxima.
  - En el prototipo un salto completo ya aterriza al 98 % de la terminal, así que un umbral solo por velocidad marcaría todos los saltos como "duros".
- En un run-and-gun conviene que **ni el aterrizaje duro bloquee el disparo ni el salto** (inferencia). El bloqueo de Hollow Knight es de un metroidvania, y Broforce lo limita a 0,133 s.

### Gaps
- Valores de `BIG_FALL_TIME` y `HARD_LANDING_TIME` de Hollow Knight: son campos públicos que se cargan desde el prefab de Unity y no aparecen en el código. No los encontré publicados.
- Cantidad de cuadros y fps de "Land" y "HardLand" en Hollow Knight: s/d.
- Duración por dibujo del aterrizaje de Metal Slug y de Mega Man X: s/d (sin emulador).

---

## 6. Salto corriendo vs parado, y giro en el aire

### Takeaway
- **Variantes según la velocidad horizontal al despegar:**
  - Hay variantes en Metal Slug (6+6 dibujos por variante), en Super Mario World (pose propia, pero solo con el P-meter lleno) y en Celeste (jumpFast, solo por encima de la velocidad máxima de carrera, latcheado hasta aterrizar). Pedro Medeiros recomienda dos: UP con x_speed = 0 y FORWARD con x_speed > 0.
  - Hollow Knight, Cuphead, Mega Man y Mega Man X usan una sola.
- **Giro en el aire:** es instantáneo en todos los casos revisados. La animación de giro existe solo en el suelo.

### Cited Findings
- **saint11:** "I like having 2 animations for jumping. UP is when starting X_SPEED=0. FORWARD is when starting X_SPEED>0" ([Jump.gif](https://saint11.art/img/pixel-tutorials/Jump.gif)).
- **Celeste:** jumpFast si `|Speed.X| > MaxRun` (90 px/s), con `fastJump` latcheado hasta el suelo ([L1308–1311, L1243](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1300-L1331)). Correr normal (≤ 90) da jumpSlow, así que la variante "rápida" es para dash o impulsos.
- **Super Mario World:** al saltar, si `PlayerPMeter ≥ $70` (carrera a tope), la pose es `$0C` en vez de `$0B` ([bank_00.asm L9979–9993](https://github.com/IsoFrieze/SMWDisX/blob/HEAD/bank_00.asm#L9979-L9993)). Esa pose no se cambia a la de caída ([L10446–10456](https://github.com/IsoFrieze/SMWDisX/blob/HEAD/bank_00.asm#L10446-L10456)).
- **Metal Slug:** salto parado 6 + 6 y salto corriendo 6 + 6 en piernas y torso. Las piernas del salto corriendo son más recogidas: 14 px de alto contra 18–24 del parado (nota previa `metal_slug_sheets.md`, conteo y medición propios; [SR 11225 vía Wayback](https://web.archive.org/web/20230512095229/https://www.spriters-resource.com/resources/sheets/11/11225.png)).
- **Hollow Knight:** un único clip "Airborne", sin variante por velocidad ([L326–357](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroAnimationController.cs#L326-L357)). Cuphead usa la misma bola para todo, y Mega Man y Mega Man X una sola serie (§2).
- **Giro:**
  - **Celeste:** `Facing = moveX` cada tick con input horizontal, en cualquier estado salvo trepar, levantar o dash rojo, incluido el aire ([L786–794](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L786-L794)). La animación `flip` solo se reproduce dentro de la rama `onGround` ([L1277–1283](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1272-L1286)).
  - **Hollow Knight:** "Turn" solo si `cState.onGround` ([HeroAnimationController.cs L367–381](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroAnimationController.cs#L367-L381)).
  - **Cuphead:** `Turn_Run` solo sale del estado Run ([animator_player.controller](https://github.com/jmxamongusmodder/cuphead-decomp/blob/HEAD/Assets/AnimatorController/animator_player.controller)).

### Inferences
- Para el prototipo alcanza con **un solo set de aire**. Si se agrega una variante corriendo, el criterio de referencia es mirar |vx| al despegar y **latchearla hasta aterrizar**, como Celeste y SMW. Según saint11, el umbral es "> 0". Según SMW y Celeste, es "carrera a tope".
- **Flip instantáneo en el aire**, sin dibujo de giro.

### Gaps
- No verifiqué si Mega Man X o Shovel Knight tienen variante corriendo (no aparece en las láminas vistas).

---

## 7. Recomendación concreta para el prototipo (12 fps de dibujo, 60 Hz de juego, v0 = 1067, terminal 1400)

### Takeaway
1. Despegue instantáneo, **sin mostrar los 2 cuadros de prep como demora**.
2. **5 dibujos de aire elegidos por vy**, con umbrales que dan a cada fase ≥ 0,1 s en un salto completo:
   - subida A si vy < −590 (−0,55 v0);
   - subida B hasta −180 (−0,17 v0);
   - ápice hasta +300 (0,21 × terminal);
   - caída A hasta +840 (0,6 × terminal);
   - caída B por encima.
3. Aterrizaje con un **contacto de 1 fr12 siempre visible**, por código si hay movimiento, y la recuperación completa solo si queda quieto.

### Cited Findings
Esta sección es **cálculo propio** sobre la física del prototipo dada en el encargo:
- Subida: vy = −1067 + 2963·t. Ápice a 0,360 s y 192 px.
- Caída: vy = 4898·(t − 0,360). Aterriza a 0,640 s con vy = 1372 px/s.
- Salto corto: corte a −480 px/s. Aproximo el tap como vy = −480 desde el tick 0: sube 39 px en 0,162 s, cae en 0,126 s y aterriza a 617 px/s.

Bases citadas para cada decisión:
- Despegue sin demora: §1 (Celeste, Hollow Knight, Cuphead, SMW; saint11 "Avoid on player controlled characters").
- Ápice de ≈0,07–0,14 s: §4 (Broforce, Metal Slug).
- Segundo dibujo de caída como loop o caída rápida: §3 (Celeste fallFast; Hollow Knight entra a la caída por el cuadro 5 al caer de un borde).
- Squash por código en el aterrizaje, proporcional a vy: §5 ([Celeste L2557–2559](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2554-L2566)).
- Dibujos de recuperación solo si quieto: §5 (Hollow Knight "Land" solo a idle; saint11 "interrupted if necessary").

**Tabla propuesta, salto completo** (cálculo propio):

| Fase | Dibujo | Condición en vy (px/s) | Fracción | Intervalo | Duración | ticks | fr12 |
|---|---|---|---|---|---|---|---|
| Despegue + subida rápida | rise A (estirado) | vy < −590 | −0,55 v0 | 0–0,161 s | 0,161 s | 9,7 | 1,9 |
| Subida lenta | rise B | −590 ≤ vy < −180 | −0,17 v0 (= 2963 × 0,06 s) | 0,161–0,299 | 0,138 s | 8,3 | 1,7 |
| Ápice | apex (recogido / invert) | −180 ≤ vy < +300 | +0,21 × terminal (= 4898 × 0,06 s) | 0,299–0,421 | 0,122 s | 7,3 | 1,5 |
| Caída | fall A | +300 ≤ vy < +840 | 0,6 × terminal | 0,421–0,532 | 0,110 s | 6,6 | 1,3 |
| Caída rápida / larga | fall B (o loop de 2) | vy ≥ +840 | ≥ 0,6 × terminal | 0,532–0,640 | 0,109 s | 6,5 | 1,3 |

**Salto corto (tap)** con los mismos umbrales: rise B 0,101 s (6 ticks) → ápice 0,122 s (7 ticks) → fall A 0,065 s (4 ticks) → aterriza a 617 px/s. Con los umbrales actuales, el mismo tap da rise 0 0,081 s → rise 1 0,061 → apex 0,053 → fall 0 0,093.

**Caída desde un borde sin saltar** (inferencia, por la entrada por el cuadro 5 de Hollow Knight): arrancar directamente en fall A en vez de pasar por el ápice. Con el umbral de vy, el ápice duraría 300/4898 = 0,061 s al caer de un borde.

**Aterrizaje** (cálculo propio; cada fr12 = 0,083 s):
- **Contacto, siempre.** 1 dibujo de squash por 0,083 s si queda quieto. Si hay movimiento, disparo o salto, no se cambia el dibujo, pero se aplica squash por código sobre el que siga (run, idle-shoot): escalaY = 1 − k·min(vy/1400, 1) y escalaX = 1 + k·min(vy/1400, 1), recuperando en ≈0,1–0,15 s.
  - Para una figura HD de 128 px, k ≈ 0,12–0,2. Es mi inferencia: Celeste usa k = 0,6 en pixel art de 16 px.
  - Hoy el cuadro de prep aplasta solo 4 % (125 vs 130 px).
- **Recuperación, solo si quieto.** 1–2 dibujos más (0,083–0,167 s). Total 0,17–0,25 s, similar a los 0,2 s actuales. Cualquier input la cancela en el tick.
- **Suave vs normal vs duro:**
  - Suave si vy < 840 (0,6 × terminal; taps y caídas cortas): solo contacto y squash por código, sin recuperación.
  - Normal: el salto completo.
  - Duro: caída > ~3 H (≥ 384 px), equivalente a los 50 px ≈ 3 H visibles de Celeste. Con esta física, 384 px son ≈0,42 s de caída (llega a la terminal a 0,286 s y 200 px). Squash más profundo y 3 dibujos si queda quieto, igual cancelable. No conviene bloquear como Hollow Knight en un run-and-gun.
- **Polvo:** al aterrizar con vy ≥ 700 (0,5 × terminal, regla de Celeste `MaxFall/2`) y al despegar (Hollow Knight crea `jumpEffectPrefab` en cada salto).

**Dibujos que faltan o sobran en el clip actual de 10** (inferencia):
1. **Los 2 de prep** no se deberían mostrar antes del despegue. El cuadro 1 (aplastado, 125 px) puede reciclarse como **contacto** del aterrizaje, o para un agache visual de 1–2 ticks con el cuerpo ya subiendo (opcional).
2. **Falta un estirón de despegue claro** (rise A). Celeste lo hace por código (0,6 × 1,4), saint11 con "going up". Si el primer dibujo de aire no está estirado, sumar stretch por código (≈0,85 × 1,15 que decae en ≈0,15–0,2 s, inferencia para HD).
3. **El ápice tiene 1 solo dibujo.** saint11 usa 3 para el "invert". Con 1 bien recogido alcanza si dura ≈0,12 s. Ideal: 2 (cerrándose / abriéndose).
4. **fall 1 nunca se usa.** Pasa a ser caída rápida o larga, y si hay 2 dibujos, loop de 2 a 12 fps con pelo y ropa flameando ("Fall: arms go up, head looks down; hair, cloth… flap in the wind", saint11).
5. **Falta una variante de aterrizaje duro** (squash más profundo) si se quiere distinguir caídas largas.
6. **Opcional:** set de salto corriendo (Metal Slug, saint11). No es necesario para la prueba.

**Problema de pipeline** (inferencia): los 5 cuadros de aire traen el cuerpo **ya desplazado hacia arriba dentro de la celda** (24, 30, 31, 30 y 26 px). Si la física mueve al personaje y el dibujo también tiene la subida "horneada", el sprite queda hasta 31 px (≈0,24 H) por encima del cuerpo físico. Además, al cambiar de dibujo por vy hay saltos de hasta 6 px entre cuadros. Conviene re-anclar los cuadros de aire a un pivote común (cadera o centro de masa) para que la altura la ponga solo la física, como los juegos revisados, donde el clip de aire es una pose y no una trayectoria.

### Inferences
- Los umbrales propuestos ponen el ápice centrado en el tiempo (±0,06 s): sube 0,061 s y baja 0,061 s. Para eso el umbral de bajada es 1,65 veces el de subida, por la gravedad asimétrica. Con eso cada dibujo dura entre 1,3 y 1,9 fr12 en un salto completo y ninguno parpadea por debajo de 1 fr12. El tap se ve como rise B → ápice → fall A.
- Si se prefiere copiar Broforce (banda de ápice de ≈0,07 s cargada a la caída), los umbrales serían ≈ −0,077 v0 (−82 px/s) y +0,14 × terminal (+196 px/s). Eso da un ápice de ≈0,07 s ≈ 0,8 fr12, demasiado breve para 12 fps.
- Alternativa más simple, estilo Hollow Knight: al despegar, reproducir un clip temporal de 5 dibujos a 12 fps que dure ≈0,42 s (subida + ápice) y después loop de caída. Es menos robusta con el salto variable, porque el tap dura 0,29 s y cortaría el clip a la mitad. Por eso recomiendo selección por vy.

### Gaps
- No pude validar los umbrales en juego (solo investigación; no toqué `prototypes/`). Hay que probarlos a ojo, sobre todo k del squash, el umbral de aterrizaje duro (3 H) y si el ápice de 0,12 s se siente "flotante" con la gravedad de caída de 4898.
- Sin delays de Celeste ni fps de Hollow Knight, las duraciones de referencia por dibujo se apoyan en Cuphead (30 fps), Broforce (≈15 fps), saint11 (12,5 fps en el GIF) y mediciones previas de Metal Slug.
