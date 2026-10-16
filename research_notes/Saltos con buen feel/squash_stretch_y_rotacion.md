# Squash & stretch por código y rotación/lean por velocidad en plataformas de acción

Convenciones: H = altura del personaje parado en su propio juego. Frames a 60 Hz salvo aclaración. **cálculo propio** = cuenta mía sobre datos citados; **conteo propio** = conteo mío sobre código/archivos; s/d = sin datos. "Desvío" = |1 − escala|. Todo el código citado lo leí directamente en GitHub (raw); no bajé ejecutables ni videos.

Nota previa: la nota `celeste_jump_feel.md` ya listaba salto (0.6, 1.4), aterrizaje → (1.6, 0.4) por vy/240, duck (1.4, 0.6), unduck (0.8, 1.2), fast fall (0.5, 1.5) y recuperación 1.75/s. Acá completo el resto de los `Sprite.Scale` de Player.cs (super jump, wall jumps, bounces, side bounce, cassette, temple fall, respawn), la ausencia de rotación y escala en el dash, y paso todo a frames.

---

## 1. Celeste (Player.cs): todos los `Sprite.Scale`, valores exactos y vuelta a (1,1)

### Takeaway
Celeste deforma a Madeline **solo por escala**, nunca por rotación. Usa cuatro "golpes" fijos: (0.6, 1.4) para todo despegue normal, (0.5, 1.5) / (1.5, 0.5) para resortes, aterrizaje proporcional a vy hasta (1.6, 0.4), y (1.4, 0.6) para agacharse. Todos vuelven a 1 de forma **lineal** a 1.75 unidades/s: 7 a 21 frames según el golpe, ≈14 frames (0.23 s) para el salto. Son deformaciones enormes (±40–60 %), pensadas para un sprite de ≈16 px.

### Cited Findings
**Recuperación (única para todos los casos):**
- Cada frame, en `UpdateSprite()`, cada eje se acerca a 1 con `Calc.Approach(Sprite.Scale.X, 1f, 1.75f * Engine.DeltaTime)`. Es una aproximación **lineal** a velocidad constante, sin spring ni easing — [Player.cs L1162–1166](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1162-L1166).
- La escala se aplica en `Render()`: `Sprite.Scale.X *= (int)Facing` antes de dibujar y se revierte después, así el flip por dirección reutiliza el mismo campo de escala — [L553](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L553), [L576](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L576).

**Tabla de asignaciones (conteo propio sobre Player.cs; duraciones = cálculo propio con desvío / 1.75 s, a 60 Hz):**

| Evento (método) | Línea | Scale (x, y) | Área sx·sy | Desvío máx | Vuelta a 1 |
|---|---|---|---|---|---|
| Salto normal `Jump()` | [L1688](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1688) | (0.6, 1.4) | 0.84 | 0.4 | 0.229 s ≈ 14 f |
| Super jump / hyper `SuperJump()` | [L1724](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1724) | (0.6, 1.4) | 0.84 | 0.4 | ≈ 14 f |
| Wall jump `WallJump()` | [L1774](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1774) | (0.6, 1.4) | 0.84 | 0.4 | ≈ 14 f |
| Wall bounce `SuperWallJump()` | [L1803](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1803) | (0.6, 1.4) | 0.84 | 0.4 | ≈ 14 f |
| Rebote en enemigo/objeto `Bounce()` (vy = −140) | [L1873](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1873) | (0.6, 1.4) | 0.84 | 0.4 | ≈ 14 f |
| Resorte `SuperBounce()` (vy = −185) | [L1910](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1910) | (0.5, 1.5) | 0.75 | 0.5 | 0.286 s ≈ 17–18 f |
| Resorte lateral `SideBounce()` (vx = 240) | [L1950](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1950) | (1.5, 0.5) | 0.75 | 0.5 | ≈ 17–18 f |
| Aterrizaje (en `OnCollideV`) | [L2557–2559](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2557-L2559) | lerp (1,1)→(1.6, 0.4) con `squish = min(vy/240, 1)` | 0.64 a tope | hasta 0.6 | hasta 0.343 s ≈ 21 f |
| Fast fall (abajo sostenido, vy ≥ 200) | [L2915–2920](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2915-L2920) | lerp (1,1)→(0.5, 1.5) entre vy = 200 y 240 | 0.75 a tope | 0.5 | se reasigna cada frame mientras dure |
| Agacharse | [L2861](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2861), [L2875](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2875) | (1.4, 0.6) | 0.84 | 0.4 | ≈ 14 f |
| Pararse (unduck) | [L2838](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2838) | (0.8, 1.2) | 0.96 | 0.2 | 0.114 s ≈ 7 f |
| Girarse estando agachada | [L792](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L792) | (0.8, 1.2) | 0.96 | 0.2 | ≈ 7 f |
| Cassette (entra/sale de la burbuja) | [L4650](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L4650), [L4666](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L4666) | 1.25 uniforme | 1.56 | 0.25 | 0.143 s ≈ 9 f |
| Caída del templo (cutscene) | [L4941](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L4941) | solo Y = 0.7 | 0.7 | 0.3 | 0.171 s ≈ 10–11 f |
| Fin del respawn de intro | [L5231](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L5231) | (1.5, 0.5) | 0.75 | 0.5 | ≈ 17–18 f |

- Constantes relevantes: `MaxFall = 160`, `FastMaxFall = 240`, `MaxRun = 90`, `JumpSpeed = −105`, `BounceSpeed = −140`, `SuperBounceSpeed = −185`, `DashSpeed = 240`, `Gravity = 900` — [Player.cs L23–75](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L23-L75).
- El aterrizaje solo deforma si el estado no es `StClimb`. Además tira polvo si `Speed.Y >= MaxFall / 2` (80 px/s) y pasa a `RunStumble` si cayó más de 50 px con vy ≥ 160 y |vx| ≥ 90 — [L2555–2565](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2555-L2565).
- **Dash: no toca la escala.** Lo que hace es congelar el juego 0.05 s (`Celeste.Freeze(.05f)`), sacudir la cámara en la dirección del dash con intensidad .2 y dejar una estela cada 0.08 s — [L3449](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3449), [L3565](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3565), [L3589](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3589).
- **Rotación: ninguna.** Player.cs nunca asigna `Sprite.Rotation`; solo lo lee una vez, para dibujar el overlay blanco de "star fly" — [L572](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L572) (conteo propio: grep de `Rotation` en todo el archivo).
- La animación `Flip` es el giro en el piso (input opuesto a vx con |vx| ≤ MaxRun); con |vx| > MaxRun usa `Skid`. No es un mortal — [L1278–1283](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1278-L1283).
- Pelo: el código ajusta su física (`StepPerSegment`, `StepApproach` 64–128) y su color (destello de 0.12 s al recargar el dash), pero no le aplica squash — [L832–860](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L832-L860), [L1139](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1139).
- Ejemplos de aterrizaje (cálculo propio con la fórmula de L2557–2559):
  - A la caída máxima normal (vy = 160): squish 0.667 → (1.40, 0.60).
  - A la velocidad de un salto chico (vy ≈ 105): squish 0.44 → (1.26, 0.74).
  - Con fast fall (vy = 240): squish 1 → (1.60, 0.40).
- Regla de reparto: Celeste no conserva el área. Usa **sx + sy = 2** (suma constante): el área baja a 0.84 en (0.6, 1.4) y a 0.64 en (1.6, 0.4) (cálculo propio con los valores de la tabla).
- Tamaño en píxeles (cálculo propio): con H_vis ≈ 16 px (medición de la nota previa, [celeste_jump_feel.md](../Movimiento%20y%20disparo%20en%20run-and-guns/celeste_jump_feel.md)), el salto suma ≈ 6.4 px de alto y el aterrizaje a fondo quita ≈ 9.6 px.

### Inferencias
- El pivot de Madeline casi seguro está en los pies. El código escala sin compensar posición y aun así los pies quedan apoyados al aterrizar. No pude ver la definición del sprite (ver Gaps).
- Celeste dibuja el gameplay a 320×180 y después lo amplía. El sprite escalado se re-muestrea a baja resolución, así que el contorno de 1 px sigue midiendo más o menos 1 px y el ±40 % no "deforma la línea" como lo haría en un sprite HD.
- Patrón de diseño: todos los despegues comparten un mismo golpe (0.6, 1.4) y los resortes uno más fuerte (0.5, 1.5). Un impulso "más fuerte que el salto normal", como un doble salto, lleva más deformación y dura más (con recuperación lineal fija, más desvío = más frames).
- Que la recuperación sea lineal hace que el golpe se lea como "pop + vuelta pareja". Al ser lineal, la duración crece con la amplitud: un golpe chico dura poco.

### Gaps
- Pivot/origen exacto de Madeline: `PlayerSprite.cs` no está en el repo público (el repo solo tiene `Player.cs` y `Readme.md`, [listado](https://github.com/NoelFB/Celeste/tree/master/Source/Player)). El `justify` del player en `Sprites.xml` no aparece en la wiki de Everest ([Adding Sprites](https://github-wiki-see.page/m/EverestAPI/Resources/wiki/Adding-Sprites)).
- Celeste no tiene doble salto, así que no hay un valor "de doble salto". Lo más parecido es `Bounce` (0.6, 1.4) y `SuperBounce` (0.5, 1.5).

---

## 2. Otras fuentes de código con números (toolkits, templates, juegos)

### Takeaway
Las fuentes abiertas que encontré se reparten en dos familias:
- **Golpe fijo + vuelta.** Celeste y el template de Sébastien Bénard (deepnight) usan (0.6, 1.4) al saltar y (1.5, 0.5) al aterrizar, con vuelta lineal o exponencial de ≈10–14 frames. Dawnosaur usa curvas keyframeadas: (0.8, 1.38) relativo en 8 frames al saltar y (1.3, 0.75) relativo en 12 frames al aterrizar.
- **Deformación por velocidad.** Juicy Breakout estira proporcional a la velocidad con clamp 0.85–1.35, y Celeste hace lo mismo en el fast fall.

Los toolkits genéricos (GDevelop, Feel) usan defaults de 0.2 s y fuerzas de 0.2 a 0.6. Para Cuphead, Hollow Knight, Ori, Dead Cells (el juego), TowerFall, Super Meat Boy y Nuclear Throne no encontré evidencia de squash por código.

### Cited Findings
**deepnight / gameBase (template Haxe de Sébastien Bénard):**
- `setSquashX(s)` pone (s, 2−s) y `setSquashY(s)` pone (2−s, s). Es la misma regla sx + sy = 2 de Celeste — [Entity.hx L668–677](https://github.com/deepnight/gameBase/blob/master/src/game/Entity.hx#L668-L677).
- Recuperación **exponencial**: `sprSquashX += (1-sprSquashX) * M.fmin(1, 0.2*tmod)`. Cada frame se recorre el 20 % de lo que falta hasta 1 — [Entity.hx L717–722](https://github.com/deepnight/gameBase/blob/master/src/game/Entity.hx#L717-L722).
- La escala final es `spr.scaleX = dir*sprScaleX*sprSquashX`, o sea que el flip va en la misma escala, igual que en Celeste — [Entity.hx L717–718](https://github.com/deepnight/gameBase/blob/master/src/game/Entity.hx#L717-L718).
- Pivot por defecto `pivotX = 0.5`, `pivotY = 1`: centro de los pies — [Entity.hx L152–154](https://github.com/deepnight/gameBase/blob/master/src/game/Entity.hx#L152-L154).
- En el jugador de ejemplo: al saltar `setSquashX(0.6)`, es decir (0.6, 1.4); al aterrizar `setSquashY(0.5)`, es decir (1.5, 0.5). Un comentario lo justifica como "some squash animations, because it's cheap and they do the job" — [SamplePlayer.hx L8, L71, L97–100](https://github.com/deepnight/gameBase/blob/master/src/game/sample/SamplePlayer.hx#L71).
- La física corre en `fixedUpdate` a **30 fps** (`FIXED_UPDATE_FPS = 30`) y el squash se actualiza en `postUpdate` con `tmod`, a la tasa de pantalla — [Const.hx](https://github.com/deepnight/gameBase/blob/master/src/game/Const.hx), [Entity.hx L54](https://github.com/deepnight/gameBase/blob/master/src/game/Entity.hx#L54).
- Duraciones (cálculo propio, con tmod = 1 a 60 Hz; la deformación que queda tras n frames es desvío·0.8ⁿ; vida media 3.1 frames = 0.052 s):
  - Salto (desvío 0.4): baja de 0.05 en 10 frames (0.17 s) y de 0.01 en 17 frames.
  - Aterrizaje (desvío 0.5): baja de 0.05 en 11 frames y de 0.01 en 18 frames.

**Dawnosaur platformer-movement (demo Unity):**
- Es un rectángulo con escala de reposo (1, 1.3) (primer key de `Idle.anim`). Todas las animaciones de squash son keyframes de escala del Animator, sin código. Archivos: [JumpLaunch.anim](https://github.com/DawnosaurDev/platformer-movement/blob/main/Platformer%20Demo%20-%20Unity%20Project/Assets/Visuals/Animation/JumpLaunch.anim), [Land.anim](https://github.com/DawnosaurDev/platformer-movement/blob/main/Platformer%20Demo%20-%20Unity%20Project/Assets/Visuals/Animation/Land.anim), [Fall.anim](https://github.com/DawnosaurDev/platformer-movement/blob/main/Platformer%20Demo%20-%20Unity%20Project/Assets/Visuals/Animation/Fall.anim), [JumoEnd.anim](https://github.com/DawnosaurDev/platformer-movement/blob/main/Platformer%20Demo%20-%20Unity%20Project/Assets/Visuals/Animation/JumoEnd.anim), [Idle.anim](https://github.com/DawnosaurDev/platformer-movement/blob/main/Platformer%20Demo%20-%20Unity%20Project/Assets/Visuals/Animation/Idle.anim) (sample rate 60).
- Valores relativos al reposo (conteo propio de keys + cálculo propio):
  - **Despegue** `JumpLaunch`: de (1.00, 1.154) a (0.80, 1.385) en 0.133 s = **8 frames**. El área crece hasta 1.11.
  - **Subida/caída** `JumpEnd`/`Fall`: estáticos en (1.00, 1.154) y (0.90, 1.154).
  - **Aterrizaje** `Land`: (1.30, 0.752) en t = 0 → (1.20, 0.785) a 0.05 s → (1.25, 0.790) a 0.083 s → (1, 1) a 0.2 s = **12 frames**. Hay un rebote chico en X a los 5 frames.
  - **Idle** (respiración): loop de 1 s, X 1 → 1.08, Y 1 → 0.952.
- Pivot: está en el centro, pero `Land` baja la posición −0.1609 en el frame 0, que es exactamente (1.3 − 0.978)/2. Así los pies quedan en el piso: equivale a escalar desde los pies (cálculo propio) — [Land.anim](https://github.com/DawnosaurDev/platformer-movement/blob/main/Platformer%20Demo%20-%20Unity%20Project/Assets/Visuals/Animation/Land.anim).
- El controlador de movimiento (`PlayerMovement.cs`) no toca la escala salvo para la gravedad. El "juice" está todo en `PlayerAnimator.cs` y en los clips — [PlayerMovement.cs](https://github.com/DawnosaurDev/platformer-movement/blob/main/Platformer%20Demo%20-%20Unity%20Project/Assets/Scripts/PlayerMovement.cs).

**Tarodev Ultimate 2D Controller** (Tarodev figura como "Additional Code" en el toolkit de GMTK, según el resumen del buscador de la [página de itch.io](https://gmtk.itch.io/platformer-toolkit)):
- El `PlayerAnimator` no hace squash por código: dispara triggers del Animator. El polvo de aterrizaje se escala con `InverseLerp(0, 40, impact)` — [PlayerAnimator.cs](https://github.com/Matthew-J-Spencer/Ultimate-2D-Controller/blob/main/Scripts/PlayerAnimator.cs).

**GDevelop "Character game feel" (extensión comunitaria):**
- Defaults: Idle fuerza 0.1 / velocidad 500; Jump 0.2 / 200; Fall 0.3 / 200; Land 0.6 / 100.
- La página marca la unidad de "Scaling speed" como duración. Lo más probable es que sea en ms; la página dice segundos en el caso de idle, lo cual es ambiguo.
- Requiere un Tween behavior — [GDevelop wiki](https://wiki.gdevelop.io/gdevelop5/extensions/character-game-feel/). Según el resumen del buscador, la misma página pide el origen del sprite abajo al centro (no lo vi en el texto devuelto).

**Feel (More Mountains), `MMF_SquashAndStretch`:**
- Defaults: `AnimateScaleDuration = 0.2` s; curva con keys (0, 0) → (0.3, 1.5) → (1, 0); `RemapCurveZero = 1`, `RemapCurveOne = 2`; `Axis = YtoXZ`; `Mode = Absolute` — [Feel API](https://feel-docs.moremountains.com/API/class_more_mountains_1_1_feedbacks_1_1_m_m_f___squash_and_stretch.html).
- Cálculo propio: si el remap es lineal sin clamp, el pico por defecto sería 2.5 en Y, a los 0.06 s (≈ 4 frames). Es un default exagerado que se espera ajustar.

**GMTK Platformer Toolkit (Mark Brown, 2022):**
- La UI de "juice" tiene "Squash & Stretch: Jump / Land" y "Lean: Angle / Speed". Valores que publicaron usuarios:
  - Jump 1.5 / Land 1.8 con Lean Angle 10 / Speed 47.
  - Jump 1.1 / Land 1.5.
  - Fuente: [comentarios en itch.io](https://gmtk.itch.io/platformer-toolkit/comments?before=270).
- Los defaults no están publicados en esa página. El devlog "Behind the Code" solo muestra el código de movimiento y adjunta un zip de scripts (10 kB, MIT) que no bajé — [devlog](https://gmtk.itch.io/platformer-toolkit/devlog/395523/behind-the-code).

**Super Meat Boy:**
- El artículo "Making Meat Boy Move" no menciona squash, escala ni rotación. Habla de input y diseño de niveles — [Game Developer](https://www.gamedeveloper.com/design/making-meat-boy-move).

**Squash escalado por la caída (cualitativo):**
- Un devlog de Unity con Feel escala el squash de aterrizaje según la caída ("subtle for short falls, larger for high falls") con un umbral de "hard fall", sin números — [Vaults and Vampires devlog](https://rcxa.itch.io/vaults-and-vampires/devlog/662233/jumping-and-landing-feedback).

### Inferencias
- Consenso numérico de las fuentes con código:
  - Despegue: Y +38 a +40 % (Celeste, deepnight, Dawnosaur).
  - Aterrizaje: X +30 a +60 %, Y −25 a −60 %.
  - Vuelta: 8 a 21 frames. La mediana está cerca de 12 frames (0.2 s), que coincide con el default de Feel (0.2 s) y con el `Land` de Dawnosaur.
- Todos esos valores son para sprites chicos o primitivos (Madeline ≈16 px, un rectángulo, pixel art de deepnight). Ver la sección 6 para escalarlos a HD.
- Como el template de deepnight hace squash a la tasa de pantalla con física a 30 fps, es un precedente directo de "deformación a 60 Hz sobre algo que avanza más lento". Es análogo al ranger: dibujos a 12 fps sobre un juego a 60 Hz.
- Bénard fue diseñador/programador líder de Dead Cells en Motion Twin (dato conocido, no verificado con fuente en esta sesión). Que su template use (0.6, 1.4) / (1.5, 0.5) no prueba que Dead Cells haga lo mismo: Dead Cells usa sprites renderizados desde 3D.

### Gaps
- **Cuphead** (squash por código o solo dibujado), **Hollow Knight**, **Ori**, **Dead Cells**, **TowerFall** (mismo autor y motor Monocle que Celeste, pero no verificado), **Super Meat Boy** y **Nuclear Throne**: no encontré fuentes primarias ni decomps legibles con valores de escala. s/d. Lo más prudente es asumir que en Cuphead y Hollow Knight el squash es dibujado.
- No pude leer el `characterJuice` del GMTK Toolkit (defaults, curvas, duración). Una búsqueda por nombres de variables no devolvió ningún mirror en GitHub.

---

## 3. Charlas y textos: reglas y números concretos

### Takeaway
"Juice it or lose it" no deja números en la charla en sí, pero sí en su demo (Juicy Breakout, código de Martin Jonasson). Ahí está la regla más limpia: estirar proporcional a la velocidad con **área exacta** (sx = r, sy = 1/r), con clamp final a **0.85–1.35**. Para golpes de impacto usa un "jelly" de 0.05 s de ida y **0.6 s de vuelta con Elastic.easeOut**. Nijman (Vlambeer) se enfoca en armas, cámara y hit pause, no en deformar al personaje. De Swink y Eiserloh no encontré números de squash.

### Cited Findings
- Juicy Breakout es "an example that we made for a talk at Nordic Game Indie Night". El README enlaza las ecuaciones de easing de Robert Penner, game-feel.com (Swink) y la charla de interpolación de Casey Muratori — [README.rst](https://github.com/grapefrukt/juicy-breakout/blob/master/README.rst). El usuario grapefrukt es Martin Jonasson ([perfil](https://github.com/grapefrukt)).
- Pelota, estiramiento animado: `relative = 1 + v/(2·vmax)`, clamp [1, 2.5], `scaleX = relative`, `scaleY = 1/relative` (área constante). Le suma un resorte de "shakiness" (k = 0.25, amortiguación 0.10 por timeDelta) y al final clampa ambos ejes a **[0.85, 1.35]** — [Ball.as L83–111](https://github.com/grapefrukt/juicy-breakout/blob/master/src/com/grapefrukt/games/juicy/gameobjects/Ball.as#L83-L111).
- Pelota, versión no animada: `scaleX = 1 + 0.3·k`, `scaleY = 1 − 0.2·k`, con k ∈ [0, 1] según la velocidad entre min y max. Es asimétrica: estira 30 % y afina 20 % — [Ball.as L93–96](https://github.com/grapefrukt/juicy-breakout/blob/master/src/com/grapefrukt/games/juicy/gameobjects/Ball.as#L93-L96).
- Pelota, rotación: se orienta hacia la dirección de la velocidad (`atan2`) con lerp de 0.5·timeDelta por frame — [Ball.as L72–78](https://github.com/grapefrukt/juicy-breakout/blob/master/src/com/grapefrukt/games/juicy/gameobjects/Ball.as#L72-L78).
- Bloque, jelly: X va a 1 + 0.2 en **0.05 s** con `Quadratic.easeInOut` y vuelve a 1 en **0.6 s** con `Elastic.easeOut`. Y hace lo mismo con 0.05 s de retraso. Se llama con fuerza .2 y un retraso aleatorio de hasta 0.02 s — [Block.as L119–127](https://github.com/grapefrukt/juicy-breakout/blob/master/src/com/grapefrukt/games/juicy/gameobjects/Block.as#L119-L127), [Main.as L320–325](https://github.com/grapefrukt/juicy-breakout/blob/master/src/com/grapefrukt/games/juicy/Main.as#L320-L325).
- Paleta: `scaleX = 1 + |dx|/100`, `scaleY = 1.5 − 0.5·scaleX`, es decir, estira según el desplazamiento por frame del mouse — [Main.as L217–222](https://github.com/grapefrukt/juicy-breakout/blob/master/src/com/grapefrukt/games/juicy/Main.as#L217-L222).
- "The art of screenshake" (Nijman, INDIGO 2013): una recreación de fans lista menos time-to-kill, más cadencia, balas más grandes, muzzle flash, balas más rápidas, knockback, lerp de cámara, screenshake, knockback del jugador, hit pause y recoil. **No incluye squash del personaje** — [recreación de DK Liao](https://dkliao.itch.io/the-art-of-screenshake-recreation/devlog/451576/quick-breakdown-of-all-the-effects) (fuente secundaria).
- En una cita secundaria de Nijman sobre la pistola de Nuclear Throne: la cámara patea 6 px y el screenshake sube 4 — [infovore](https://infovore.org/?p=5275).
- Principio de animación: el squash & stretch clásico mantiene el volumen constante — [Wikipedia: Squash and stretch](https://en.wikipedia.org/wiki/Squash_and_stretch).

### Inferencias
- Hay dos reglas de reparto en uso:
  - **Área exacta** (sx = 1/sy): Juicy Breakout.
  - **Suma constante** (sx = 2 − sy): Celeste y deepnight.
  
  Para desvíos de ±10–15 % dan casi lo mismo. Por ejemplo, sy = 1.12 → sx = 0.893 con área exacta o 0.88 con suma (área 0.986). Solo se separan en deformaciones grandes (cálculo propio).
- El clamp de Jonasson (0.85–1.35) es un buen techo para objetos "con dibujo", aunque él lo aplicó a una pelota.
- Elastic de 0.6 s funciona para bloques, pero en un personaje que tiene que estar listo para saltar de nuevo es largo. Las fuentes de personajes (Celeste, deepnight, Dawnosaur) vuelven en 8–21 frames sin rebote elástico; solo Dawnosaur tiene un rebote chico.

### Gaps
- Steve Swink, *Game Feel*: no encontré números de squash citables.
- Eiserloh: la sesión "Math for Game Programmers: Fast and Funky 1D Nonlinear Transformations" (GDC 2015) existe ([GDC Vault](https://gdcvault.com/play/1022142/Math-for-Game-Programmers-Fast)), pero la búsqueda no confirmó el orador ni su contenido.
- No encontré transcripción de "Juice it or lose it" con reglas verbales.
- Videos de GMTK sobre Celeste: no verificados.

---

## 4. Duración y easing; visibilidad con animación a 12 fps sobre un juego a 60 Hz

### Takeaway
Rango de duraciones en código: 7–21 frames. Golpes chicos: ≈7 frames. Despegue: 8–14 frames. Aterrizaje: 12–21 frames. Hay tres formas de volver a 1:
- **Lineal** (Celeste, 1.75/s).
- **Exponencial** (deepnight, 20 %/frame).
- **Curva keyframeada** (Dawnosaur, Feel), con algún rebote.

Ninguna fuente de personaje usa elástico largo. Como la escala se actualiza a 60 Hz aparte de los dibujos, el squash se ve aunque el sprite cambie de dibujo solo cada 5 frames, y suaviza lo entrecortado.

### Cited Findings
- Celeste: vuelta lineal a 1.75/s, ≈0.029 por frame. Despegue ≈14 frames, resorte ≈17–18, aterrizaje a fondo ≈21, unduck ≈7 — [Player.cs L1165–1166](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1165-L1166) (frames: cálculo propio).
- deepnight: exponencial, factor 0.2 por frame (`tmod`). Vida media ≈3 frames; menos de 5 % del desvío a los 10–11 frames — [Entity.hx L721–722](https://github.com/deepnight/gameBase/blob/master/src/game/Entity.hx#L721-L722) (frames: cálculo propio).
- Dawnosaur: despegue 8 frames; aterrizaje 12 frames con un rebote chico en X (1.3 → 1.2 → 1.25 → 1) — [Land.anim](https://github.com/DawnosaurDev/platformer-movement/blob/main/Platformer%20Demo%20-%20Unity%20Project/Assets/Visuals/Animation/Land.anim) (conteo propio).
- Feel: 0.2 s por defecto, con el pico al 30 % del tiempo — [Feel API](https://feel-docs.moremountains.com/API/class_more_mountains_1_1_feedbacks_1_1_m_m_f___squash_and_stretch.html).
- Juicy Breakout (objetos, no personaje): ida en 0.05 s y vuelta elástica en 0.6 s — [Block.as L119–127](https://github.com/grapefrukt/juicy-breakout/blob/master/src/com/grapefrukt/games/juicy/gameobjects/Block.as#L119-L127).
- deepnight anima el squash en `postUpdate` (tasa de pantalla) aunque la física corra a 30 fps fijos — [Const.hx](https://github.com/deepnight/gameBase/blob/master/src/game/Const.hx), [Entity.hx L54, L717–722](https://github.com/deepnight/gameBase/blob/master/src/game/Entity.hx#L717-L722).

### Inferencias
- Tiempos del ranger (cálculo propio): subida 0.36 s ≈ 22 frames, caída 0.28 s ≈ 17 frames, aire total ≈38 frames.
  - Un stretch de despegue de 8–10 frames ocupa el primer 40–45 % de la subida y ya se fue antes del ápice.
  - Un squash de aterrizaje de 8–12 frames dura 1.6–2.4 dibujos a 12 fps (5 frames de juego por dibujo).
- A 12 fps cada dibujo se sostiene 5 frames. Si la escala avanza cada frame, se ven 5 tamaños distintos por dibujo. Eso funciona como "in-between" barato. Es la misma situación que en Celeste, donde la escala anda a 60 Hz y las animaciones de Madeline a tasas mucho menores (sus delays por frame no están confirmados, ver la nota previa).
- Con desvíos chicos (≈0.15), la vuelta lineal estilo Celeste dura poco (0.15/1.75 = 0.086 s ≈ 5 frames; cálculo propio). Para un golpe chico conviene fijar la **duración** (8–12 frames) y no la velocidad, o usar la exponencial de deepnight. Con la exponencial, el 20 %/frame da ≈10 frames a cualquier amplitud.
- Ease-out (exponencial o cuadrática) es lo que más se parece al "pop y vuelve": el cambio más grande queda en el primer frame. Se puede agregar un rebote de 1 a 2 frames como en Dawnosaur. Evitar elástico largo, porque compite con el siguiente salto.

### Gaps
- No hay fuente que mida a partir de cuántos frames o porcentaje un jugador deja de percibir el squash. El umbral de 1 px se discute en la sección 6 como cálculo propio.

---

## 5. Rotación y lean por velocidad; mortales rotados por código vs dibujados

### Takeaway
Los ejemplos con código usan inclinaciones chicas:
- **Dawnosaur:** ±10°, lineal con vx, suavizado 0.08 por frame, también en el aire.
- **Tarodev:** 5°, solo en el piso, según el input y prácticamente instantáneo.
- **GMTK Toolkit:** tiene una opción "Lean" (un usuario la puso en 10°).

**Celeste no rota nunca.** Para mortales por código, la práctica comunitaria es rotar un hijo visual separado del collider, a una velocidad angular con dt, y volver a 0° al aterrizar. No conseguí conteos de dibujos de mortales dibujados (Metroid, Hollow Knight, Zero).

### Cited Findings
**Dawnosaur `PlayerAnimator`:**
- Ángulo objetivo: `newRot = tiltProgress·2·maxTilt − maxTilt`, con `tiltProgress = InverseLerp(−runMaxSpeed, +runMaxSpeed, vx)`. Es lineal en vx, de −maxTilt a +maxTilt.
- Se aplica con `LerpAngle(actual, objetivo, tiltSpeed)` en `LateUpdate`, por frame y sin dt. No mira si está en el piso, así que también inclina en el aire. En wall slide fija `tiltProgress = 0.25` (−5°) — [PlayerAnimator.cs](https://github.com/DawnosaurDev/platformer-movement/blob/main/Platformer%20Demo%20-%20Unity%20Project/Assets/Scripts/PlayerAnimator.cs).
- Valores de la escena: `maxTilt: 10`, `tiltSpeed: 0.08` — [Demo.unity L25075–25076](https://github.com/DawnosaurDev/platformer-movement/blob/main/Platformer%20Demo%20-%20Unity%20Project/Assets/Scenes/Demo.unity#L25075-L25076).
- Cálculo propio a 60 fps: vida media ln 0.5 / ln 0.92 ≈ 8.3 frames (0.14 s); llega al 90 % del ángulo en ≈28 frames (0.46 s).

**Tarodev `PlayerAnimator`:**
- `_maxTilt = 5` (grados) y `_tiltSpeed = 20`. La inclinación es `Euler(0, 0, 5·inputX)` solo si está en el piso; en el aire vuelve a vertical. Se aplica con `Vector3.RotateTowards(..., _tiltSpeed·dt)` — [PlayerAnimator.cs](https://github.com/Matthew-J-Spencer/Ultimate-2D-Controller/blob/main/Scripts/PlayerAnimator.cs).
- Cálculo propio: en `RotateTowards` el límite va en radianes, así que 20 rad/s ≈ 1146°/s y los 5° se alcanzan en ≈0.004 s. En la práctica es instantáneo, y depende del input, no de la velocidad.

**Otros:**
- GMTK Toolkit: opción "Lean: Angle / Speed"; un usuario publicó Angle 10, Speed 47. Defaults y unidades s/d — [comentarios itch.io](https://gmtk.itch.io/platformer-toolkit/comments?before=270).
- Celeste: no asigna `Sprite.Rotation` en ningún lugar de Player.cs — [Player.cs](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs) (conteo propio por grep).
- Juicy Breakout orienta la pelota según su vector de velocidad — [Ball.as L72–78](https://github.com/grapefrukt/juicy-breakout/blob/master/src/com/grapefrukt/games/juicy/gameobjects/Ball.as#L72-L78).
- Un prototipo de "game feel" lista "Acceleration Tilt" como efecto, sin valores — [Karl Fayeton, itch.io](https://karlfayeton.itch.io/test-3d-platformer).
- Un tutorial de animación procedural (3D) dice que una inclinación chica derivada de la aceleración da sensación de masa. Recomienda capa de rotación sobre la animación base, según el resumen del buscador — [Vulkan docs, physics-driven lean](https://docs.vulkan.org/tutorial/latest/Advanced_glTF/Procedural_Animation_IK/06_physics_driven_lean.html).

**Mortal por código:**
- Foro de Construct: separar el sprite visual que rota del objeto de colisión, porque con 15° de rotación una esquina toca el piso. Rotar en grados/s con dt y resetear al aterrizar — [Construct forum](https://construct.net/en/forum/construct-2/how-do-i-18/rotate-sprite-jumping-51127) (según el resumen del buscador).
- Foro de Scratch: al aterrizar antes o después de completar el giro, ajustar el ángulo a un múltiplo de 90° — [Scratch](https://scratch.mit.edu/discuss/post/7532406) (resumen del buscador).
- Godot: hay una pregunta sobre rotar 360° en el doble salto hasta que vy llegue a 0. Las respuestas sugieren animación o máquina de estados; no hay valores — [Godot forum](https://forum.godotengine.org/t/doublejump-how-to-rotate-2d-character-360deg-during-2nd-jump-until-velocity-y-reaches-0/13677).

### Inferencias
- Rango práctico de lean: **3–10°** como máximo a velocidad de carrera tope. El juego de referencia de precisión (Celeste) usa 0°. Los templates usan 5° (solo piso) o 10° (piso y aire).
- Las dos implementaciones abiertas difieren en el disparador:
  - Tarodev, por **input**: snap.
  - Dawnosaur, por **velocidad**: lerp lento, vida media ≈8 frames.
  
  Por velocidad es más físico y no tiembla al tocar el stick.
- Pivot para lean: los pies, así el personaje no "patina". Pivot para mortal: el centro de masa, ≈50 % de la altura. Rotar 360° alrededor de los pies hace que el cuerpo orbite (inferencia geométrica).
- Para el ranger, que dispara desde la boca del arma: cualquier rotación o escala por código mueve visualmente la boca. El punto de spawn de la bala tiene que pasar por la misma transformación (translate/rotate/scale), o hay que anular el lean mientras dispara. Si no, la bala sale "desde el aire".

### Gaps
- No encontré conteos de dibujos ni duraciones de mortales dibujados con fuente: spin jump de Super Metroid/Fusion/Dread, doble salto de Hollow Knight (Monarch Wings), doble salto de Zero en Mega Man X5/X6, Ori.
  - Super Metroid tiene tablas de delay por animación documentadas en un desensamblado ([metroidconstruction](https://metroidconstruction.com/resource.php?id=333)), pero no lo descargué.
  - El spin jump es un loop ([TASVideos](https://tasvideos.org/8214S)).
  - The Spriters Resource devolvió bot-protection en sesiones previas.
- Juegos comerciales con lean por velocidad y grados medidos (Rayman Legends, Spelunky, Ori, Sonic, Dead Cells): s/d.

---

## 6. Riesgos para un sprite HD cartoon con contorno grueso

### Takeaway
En HD la escala no uniforme deforma visiblemente el grosor del contorno: con sx = 0.6, las líneas verticales quedan 2.3 veces más finas que las horizontales. Además, en HD alcanza mucho menos porcentaje para que se vea, porque 1 px es ≈1 % de la altura (contra ≈6 % en Madeline). Igualar la deformación de Celeste **en proporción a la pantalla** da ≈+19 % para el ranger. Con ±12–20 %, el contorno se deforma menos de 1 px de diferencia entre ejes y el efecto se sigue viendo.

### Cited Findings
- Celeste usa ±40–60 % sobre un sprite de ≈16 px con contorno de 1 px, en una vista de 320×180 ampliada 6× — [Player.cs](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1688), [celeste_jump_feel.md](../Movimiento%20y%20disparo%20en%20run-and-guns/celeste_jump_feel.md).
- Jonasson clampa su estiramiento a 0.85–1.35 — [Ball.as L110–111](https://github.com/grapefrukt/juicy-breakout/blob/master/src/com/grapefrukt/games/juicy/gameobjects/Ball.as#L110-L111).
- deepnight y GDevelop escalan desde los pies (pivot 0.5, 1 / origen abajo al centro). Dawnosaur compensa la posición para mantener los pies apoyados — [Entity.hx L152–154](https://github.com/deepnight/gameBase/blob/master/src/game/Entity.hx#L152-L154), [GDevelop](https://wiki.gdevelop.io/gdevelop5/extensions/character-game-feel/), [Land.anim](https://github.com/DawnosaurDev/platformer-movement/blob/main/Platformer%20Demo%20-%20Unity%20Project/Assets/Visuals/Animation/Land.anim).

### Inferencias
**Umbral de 1 px (cálculo propio):**
- Madeline: 1 px = 1/16 ≈ 6 % de H, así que un squash de 5 % ni se ve.
- Ranger (102 px en pantalla): 1 px ≈ 1 % de H.
- Los juegos pixel art necesitan factores grandes para que se note; un sprite HD no.

**Equivalencia por fracción de pantalla (cálculo propio):**
- Madeline ocupa 16/180 = 8.9 % de la altura de la vista. Su +40 % son 6.4 px, o sea 3.6 % de la vista.
- El ranger ocupa 102/540 = 18.9 % de la vista (2.1 veces más). El mismo 3.6 % de la vista son 19.4 px, o sea **+19 %** de su altura.
- A ±15 % el ranger se mueve 15 px (2.8 % de la vista); a +40 % serían 41 px (7.6 %), el doble de "violento" que Celeste en pantalla.

**Grosor de línea (cálculo propio, contorno t en px de pantalla):**
- Las líneas verticales pasan a t·sx y las horizontales a t·sy. La anisotropía es sy/sx.
- Celeste (0.6, 1.4): 2.33×. Con t = 3 px quedan 1.8 px contra 4.2 px, un "dibujo aplastado" evidente en HD.
- (0.87, 1.15): 1.32×, 2.6 contra 3.45 px. Diferencia < 1 px, aceptable.
- (1.20, 0.83): 1.45×, 3.6 contra 2.5 px. En el límite.
- No medí el grosor real del contorno del ranger, así que t = 3 px es un supuesto. El ranger se dibuja al 80 % del atlas: un contorno de 4 px en el atlas da 3.2 px en pantalla.

**Rangos tentativos para HD con contorno grueso (inferencia):**
- ±8–15 % se lee claro y no rompe la línea.
- 15–20 % solo en picos de 1–3 frames (aterrizaje fuerte).
- Más de 25 % se empieza a leer como "goma" y rompe el contorno: no recomendado salvo gags.
- Ninguna fuente fija un máximo para HD; esto es criterio propio basado en los cálculos de arriba.

**Doble squash:**
- Si el clip ya tiene squash dibujado en el prep y en el aterrizaje, sumar el squash por código multiplica (por ejemplo, un dibujo a 0.85 de alto × 0.83 por código = 0.71).
- Opciones:
  - (a) No aplicar código en los dibujos que ya tienen squash, y aplicarlo solo donde el dibujo es neutro.
  - (b) Reducir el de código a la mitad cuando coincide.
  - (c) Sacar el squash dibujado del clip y dejarlo todo al código, como hace Celeste, que reemplaza la anticipación dibujada por squash de código (ver la nota previa).

**Orden de transformaciones en canvas (inferencia técnica):**
- `translate(pies) → rotate(lean) → scale(facing·sx, sy) → drawImage(-pivotX, -pivotY)`. Así el squash sigue el eje del cuerpo inclinado y el flip no invierte el ángulo de lean.
- Usar `imageSmoothingEnabled = true` (HD), para que la escala fraccional no genere dientes.
- Nunca escalar ni rotar el collider.

### Gaps
- No encontré fuentes específicas (posts de artistas o devs HD) sobre el máximo de deformación aceptable con contorno grueso. Todo lo de arriba es cálculo e inferencia.
- No medí el grosor real del contorno del ranger en el atlas.

---

## 7. Recomendación concreta para el prototipo (ranger HD, 60 Hz, dibujos a 12 fps)

### Takeaway
Arrancar con despegue (0.87, 1.15), doble salto (0.84, 1.19) y aterrizaje hasta (1.18, 0.85) proporcional a vy/1400, todos desde los pies y con vuelta exponencial de 20 %/frame (≈10 frames). Opcionalmente, un estiramiento continuo ≤8 % según |vy| (que se anula en el ápice) y lean de 3–5° según vx en el piso. Para el mortal de 3 dibujos, completar con rotación por código alrededor del centro. Todos los valores son una inferencia sobre las fuentes de arriba y hay que validarlos en el juego.

### Cited Findings
**Física del ranger (datos de contexto; cálculos propios con v0 = 1067, g↑ = 2963, g↓ = 4898, terminal 1400):**
- Altura de salto completo: 1067²/(2·2963) = **192 px** (1.9 H con H = 102).
- vy al aterrizar desde salto completo en el mismo nivel: √(2·4898·192) ≈ **1372 px/s** (98 % del terminal).
- Doble salto (vy = 960): sube 960²/(2·2963) = **156 px** en 0.32 s.
- Mortal: 3 dibujos en 0.42 s = 0.14 s por dibujo (8.4 frames). Un giro continuo de 360° en 0.42 s serían 857°/s = **14.3°/frame**.

**Referencias numéricas en las que se apoya la recomendación (resumen de las secciones 1–5):**
- Despegue: Celeste (0.6, 1.4) / 14 f; deepnight (0.6, 1.4) / ≈10 f; Dawnosaur (0.8, 1.385) / 8 f — [Player.cs L1688](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1688), [SamplePlayer.hx](https://github.com/deepnight/gameBase/blob/master/src/game/sample/SamplePlayer.hx#L97-L100), [JumpLaunch.anim](https://github.com/DawnosaurDev/platformer-movement/blob/main/Platformer%20Demo%20-%20Unity%20Project/Assets/Visuals/Animation/JumpLaunch.anim).
- Aterrizaje: Celeste lerp a (1.6, 0.4) por vy/240; deepnight (1.5, 0.5); Dawnosaur (1.3, 0.75) / 12 f — [Player.cs L2557–2559](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2557-L2559), [SamplePlayer.hx L71](https://github.com/deepnight/gameBase/blob/master/src/game/sample/SamplePlayer.hx#L71), [Land.anim](https://github.com/DawnosaurDev/platformer-movement/blob/main/Platformer%20Demo%20-%20Unity%20Project/Assets/Visuals/Animation/Land.anim).
- Impulsos más fuertes que el salto llevan más deformación: SuperBounce (0.5, 1.5) contra Jump (0.6, 1.4) — [Player.cs L1910](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1910).
- Estirar por velocidad: Celeste en fast fall; Juicy Breakout con clamp 0.85–1.35 — [Player.cs L2915–2920](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2915-L2920), [Ball.as](https://github.com/grapefrukt/juicy-breakout/blob/master/src/com/grapefrukt/games/juicy/gameobjects/Ball.as#L98-L111).
- Lean: Dawnosaur 10° lineal con vx, lerp 0.08; Tarodev 5° solo en el piso; Celeste 0° — [Dawnosaur](https://github.com/DawnosaurDev/platformer-movement/blob/main/Platformer%20Demo%20-%20Unity%20Project/Assets/Scripts/PlayerAnimator.cs), [Tarodev](https://github.com/Matthew-J-Spencer/Ultimate-2D-Controller/blob/main/Scripts/PlayerAnimator.cs).

### Inferencias
**Valores propuestos (inferencia; todo en escala relativa al dibujo, pivot en los pies salvo el mortal):**

| Evento | Escala objetivo (sx, sy) | Cómo se aplica | Vuelta | Por qué |
|---|---|---|---|---|
| Despegue (salto 1) | **(0.87, 1.15)** (área ≈ 1.0) | Golpe instantáneo en el frame en que se aplica v0. Si el clip tiene prep dibujado, al **terminar** el prep, no durante | Exponencial 0.2/frame → ≈10 f (0.17 s) | ≈⅓ del desvío de Celeste/deepnight; equivale en pantalla a ≈80 % del de Celeste (sección 6) |
| Subida/caída (opcional) | sy = 1 + 0.08·min(\|vy\|/1400, 1); sx = 1/sy | Objetivo continuo, se suaviza con lerp 0.25/frame. No acumula con el golpe: usar el máximo de ambos desvíos | — | Vuelve a 1 en el ápice (vy ≈ 0), el "momento redondo" del arco. Mismo principio que el fast fall de Celeste y la pelota de Jonasson |
| Ápice | (1, 1) | Sin golpe propio; ninguna fuente revisada lo hace | — | Con la fila anterior ya se lee |
| Aterrizaje | squish = clamp((vy − 300)/(1400 − 300), 0, 1); **sx = 1 + 0.18·squish, sy = 1 − 0.15·squish** | Golpe instantáneo al tocar el piso. Salto completo (1372 px/s) ≈ **(1.18, 0.85)**; caída de 50 px (≈700 px/s) ≈ (1.07, 0.95); menos de ≈300 px/s, nada | Exponencial 0.2/frame → ≈11 f; opcional rebote de 2 f a sx 1.03 como Dawnosaur | Escala con vy como Celeste, con umbral para no "temblar" en escalones. Techo ≈ 18 %, la equivalencia en pantalla de Celeste a vy normal |
| Aterrizaje con squash dibujado en el clip | La mitad: (1.09, 0.93) a tope | Aplicar sobre el dibujo neutro siguiente, o reducir mientras se ve el dibujo aplastado | ≈8 f | Evita el doble squash (0.85 × 0.85 ≈ 0.72) |
| Doble salto | **(0.84, 1.19)** | Golpe al resetear vy = 960 | 0.2/frame → ≈11–12 f | Un poco más fuerte que el salto 1, como SuperBounce frente a Jump en Celeste |
| Lean en el piso | θ = **4°·(vx / vmax_run)**, máximo 4–5° | Objetivo con lerp 0.15/frame (vida media ≈4 f) y pivot en los pies; 0° quieto; volver a 0° al disparar, o transformar el spawn de la bala | — | Entre Tarodev (5°) y Dawnosaur (10°); bajo porque el ranger dispara y un sprite HD grande hace muy visible cada grado |
| Lean en el aire | 0–3° (opcional) | Mismo lerp; a 0° durante el mortal | — | Dawnosaur inclina en el aire; Tarodev y Celeste no |

**Mortal del doble salto (3 dibujos en 0.42 s ≈ 7 fps):**
- **Opción A, recomendada para probar primero: rotación continua por código alrededor del centro del cuerpo** (≈50–55 % de H), entre 360° y −360° según el facing, con ease-out. Por ejemplo, ángulo = 360°·(1 − (1 − t)²) sobre 0.36–0.42 s.
  - Si los 3 dibujos ya muestran el cuerpo girado (≈0°, 120°, 240°), rotarlos además por código **duplica** el giro.
  - En ese caso, aplicar a cada dibujo un **offset de rotación** que barra de −60° a +60° durante sus 8.4 frames. La orientación aparente queda continua a 14.3°/frame mientras el dibujo cambia de forma cada 0.14 s.
  - Si los dibujos son "bolita" sin orientación clara, usar uno solo y rotarlo 360° entero.
- **Opción B: acortar el mortal.** Los 3 dibujos a 12 fps (0.25 s), después la pose de caída, más un offset de rotación chico (±30°) para tapar los saltos.
- Siempre:
  - Terminar la rotación en 0° (o ajustarla a 0° con un ease rápido de 3–4 frames) antes de aterrizar o al tocar el piso, como en el consejo de Scratch.
  - Rotar solo el visual, nunca el collider (Construct).
  - Volver al pivot en los pies para el squash de aterrizaje.
- Opcional: una estela/after-image cada ≈0.08 s durante el mortal (Celeste lo hace en el dash) ayuda a "rellenar" los 7 fps.

**Implementación en el canvas actual:**
- Ya hay `ctx.scale` alrededor de los pies. Guardar `sqX`, `sqY` y `lean` por entidad, aplicar `sq += (1 − sq)·(1 − 0.8^(dt·60))` por frame (exponencial independiente del frame rate) y componer `translate(pies) → rotate(lean) → scale(facing·0.8·sqX, 0.8·sqY)`.
- El punto de la boca del arma tiene que pasar por la misma matriz.

**Cómo validar:**
- Grabar a 60 fps y comparar tres niveles (½, 1× y 1.5× los valores de arriba).
- Mirar el contorno en el pico del aterrizaje: si la diferencia de grosor entre líneas verticales y horizontales supera ≈1 px en pantalla, bajar.

### Gaps
- Ningún valor de la tabla está probado en el prototipo; son puntos de partida derivados de las fuentes.
- No sé si los 3 dibujos del mortal son orientaciones espaciadas del cuerpo o poses distintas (agruparse/estirarse). De eso depende si conviene la opción A con offset o rotar un solo dibujo.
- Tampoco sé si el prep dibujado del salto retrasa el despegue o se reproduce en paralelo al impulso. Eso define en qué frame aplicar el stretch de despegue.
- Nota de seguridad de fuentes: tcrf.net apareció en los resultados de búsqueda pero no lo abrí. En las páginas que sí abrí no vi texto con instrucciones dirigidas al agente.
