# Efectos de feel alrededor del salto: polvo, estelas, shake, hit stop, sonido y landing lag

Convenciones: **H** = altura de pie del personaje en su propio juego. Frames a 60 Hz salvo aclaración. **medición propia / conteo propio / cálculo propio** = trabajo nuestro; s/d = sin dato. Lo que dice "lectura de código" es lectura directa de la fuente citada.

Referencias de escala usadas en las conversiones:
- Celeste: vista de 320×180 px de juego. Madeline mide ≈16 px visibles (H_vis), hitbox 11 px. Fuente: medición propia previa sobre capturas de Steam, en `research_notes/Movimiento y disparo en run-and-guns/celeste_jump_feel.md` (línea 119) y [Player.cs L263–266](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L263-L266). Madeline ocupa 16/180 = 8,9 % del alto de pantalla (cálculo propio).
- Demo *gamefeel* de deepnight: héroe `hei = 22` px, grilla de 16 px ([Hero.hx L12](https://github.com/deepnight/gamefeel/blob/HEAD/src/game/en/Hero.hx), [Const.hx L17](https://github.com/deepnight/gamefeel/blob/HEAD/src/game/Const.hx)). Física fija a 30 fps (`FIXED_UPDATE_FPS = 30`) ([Const.hx L14](https://github.com/deepnight/gamefeel/blob/HEAD/src/game/Const.hx)).
- Prototipo (contexto del encargo): ranger ≈102 px en una vista de 960×540, o sea 18,9 % del alto de pantalla, **2,1 veces más grande en pantalla que Madeline** (cálculo propio). Por eso convierto los efectos de cámara por **% de pantalla** (1 px de Celeste = 3 px a 540) y los de partículas por **H** (1 px de Celeste ≈ 102/16 = 6,4 px del ranger).
- Fuente nueva y muy pertinente: el repo [deepnight/gamefeel](https://github.com/deepnight/gamefeel). Es una demo de plataformas y disparos hecha para una charla de "game feel" en ENJMIN, 2019, actualizada en 2024 (descripción del repo). Cada efecto se prende y se apaga desde un menú ([README](https://github.com/deepnight/gamefeel/blob/HEAD/README.md)). deepnight es Sébastien Bénard, diseñador líder de Dead Cells en Motion Twin ([Nintendo Life](https://ds.nintendolife.com/news/2024/02/dead-cells-lead-designer-isnt-happy-with-abrupt-decision-to-end-development), [80.lv](https://80.lv/articles/dead-cells-hidden-tricks-that-make-the-game-feel-fair)). Ojo: el vínculo entre el usuario de GitHub "deepnight" y Bénard lo infiero por el nombre del estudio, Deepnight Games. No encontré los valores reales de Dead Cells, solo los de esta demo.
- Seguridad: no visité tcrf.net y no vi texto de inyección en ninguna de las páginas consultadas.

---

## 1. Polvo: forma, cantidad, dirección, velocidad, vida y escalado (despegue, aterrizaje, wall jump, doble salto)

### Takeaway
Las fuentes con código abierto usan **poco polvo, lento, que sube** y que **aparece solo pasado un umbral de caída**. Celeste tira 4 partículas al saltar y 8 al aterrizar, a 5–15 px/s (0,3–0,9 H/s), con vida de 0,3–0,5 s, y nada si cae a menos de la mitad de su velocidad máxima de caída. La demo de deepnight tira 20 bocanadas muy transparentes (alfa 0,1–0,2), y solo en caídas de 3 celdas o más, que equivalen a ≈2,2 H y superan su propio salto. Comparado con eso, el polvo del prototipo es abundante, rápido y horizontal. Además, el umbral "duro" (900 px/s) salta en cada salto completo, que aterriza a 1067 px/s.

### Cited Findings

**Celeste (2018). Llamadas en Player.cs y definición del tipo de partícula (código descompilado)**
- Salto normal: `Dust.Burst(BottomCenter, Calc.Up, 4)`, **4 partículas hacia arriba desde los pies** — [Player.cs L1690](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1690). Lo mismo en el super jump — [L1726](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1726).
- Aterrizaje: `if (Speed.Y >= MaxFall / 2) Dust.Burst(Position, Calc.Angle(new Vector2(0, -1)), 8)` — [L2561–2562](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2561-L2562). Son **8 partículas hacia arriba, solo si vy ≥ 80 px/s**, porque `MaxFall = 160f` ([L23](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L23)). La cantidad no escala con la velocidad: es todo o nada.
- Wall jump: 4 partículas en `Center ± 2 px` del lado de la pared, en dirección `Calc.UpLeft` o `Calc.UpRight`, es decir **diagonal a 45° hacia arriba y alejándose de la pared** — [L1776–1779](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1776-L1779). Las constantes `UpLeft = −2,356` y `UpRight = −0,785` rad están en [Calc.cs descompilado L2422–2425](https://github.com/TheCyndaquilDecompilers/Celeste_Decompiled/blob/HEAD/Celeste/Monocle/Calc.cs). Idem en super wall jump ([L1806–1808](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1806-L1808)) y en climb jump ([L1835–1840](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1835-L1840)).
- Dash derrapando en el piso: 1 partícula cada 0,02 s — [L1212–1213](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1212-L1213). Animación de empujar: 1 partícula en primer plano — [L396](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L396). Celeste no tiene doble salto.
- Cómo se reparte `Dust.Burst`: el desvío de posición es `AngleToVector(dirección − π/2, 4)` en valor absoluto. Para "arriba" queda **±4 px en X y 0 en Y**, o sea una línea de 8 px a la altura de los pies. Cada partícula sale con la dirección pedida — [Dust.cs descompilado](https://github.com/TheCyndaquilDecompilers/Celeste_Decompiled/blob/HEAD/Celeste/Dust.cs).
- `ParticleTypes.Dust`: texturas `particles/smoke0`–`smoke3` elegidas al azar, color blanco, `Acceleration = (0, 4)`, `LifeMin 0,3 / LifeMax 0,5` s, `Size 0,7 ± 0,1` (×textura), `DirectionRange 0,5` rad (±14°), `SpeedMin 5 / SpeedMax 15` px/s, rotación aleatoria, `ScaleOut = true` — [ParticleTypes.cs L14–44](https://github.com/TheCyndaquilDecompilers/Celeste_Decompiled/blob/HEAD/Celeste/ParticleTypes.cs). El tamaño se achica con `StartSize × Ease.CubeOut(vida restante)` — [Particle.cs L122–124](https://github.com/TheCyndaquilDecompilers/Celeste_Decompiled/blob/HEAD/Celeste/Monocle/Particle.cs). El ángulo se sortea en `dirección ± DirectionRange/2` y la rapidez entre Min y Max — [ParticleType.cs L119–121](https://github.com/TheCyndaquilDecompilers/Celeste_Decompiled/blob/HEAD/Celeste/Monocle/ParticleType.cs).
- **Cálculo propio en H (H_vis = 16 px):** franja de aparición ±0,25 H; rapidez 0,31–0,94 H/s; vida 18–30 f; gravedad 0,25 H/s², o sea casi nada. En el ranger (H = 102) equivale a ±26 px, **32–96 px/s**, 0,3–0,5 s, partículas que suben despacio y se achican.
- Escalado con la caída: el polvo no escala, pero el squash sí. Al aterrizar la escala va a `Lerp(1→1,6)` en X y `Lerp(1→0,4)` en Y, en proporción `min(vy / 240, 1)` — [L2557–2559](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2557-L2559).
- Aterrizajes guionados ("hero landing"): la caída del Templo Espejo emite `P_SummitLandA` ×12 hacia arriba, más `P_SummitLandB` ×8 a cada lado, a 15° del horizontal (izquierda y derecha) — [L4947–4949](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L4947-L4949). El aterrizaje del summit jump suma 30 partículas de fondo `P_SummitLandC` — [L5172–5175](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L5172-L5175). Esta forma es **pluma lateral más columna**, y se usa solo en momentos especiales.

**Celeste Classic (PICO-8), en el mismo repo**
- Usa **una bocanada animada por sprite**, no partículas. El objeto `smoke` arranca en el sprite 29 y avanza 0,2 por update hasta el 32: 3 dibujos de 5 updates cada uno. Se mueve `spd.X = 0,3–0,5` (siempre a la derecha) y `spd.Y = −0,1`, con un desvío de ±1 px y flip X/Y aleatorio — [Classic.cs L720–741](https://github.com/NoelFB/Celeste/blob/master/Source/PICO-8/Classic.cs#L720-L741).
- Se crea en **cada** aterrizaje, sin umbral ([L219–221](https://github.com/NoelFB/Celeste/blob/master/Source/PICO-8/Classic.cs#L219-L221)), al saltar en (x, y+4) ([L306](https://github.com/NoelFB/Celeste/blob/master/Source/PICO-8/Classic.cs#L306)), en el wall jump del lado de la pared ([L319](https://github.com/NoelFB/Celeste/blob/master/Source/PICO-8/Classic.cs#L319)), con 20 % de chance por frame durante el wall slide ([L289–290](https://github.com/NoelFB/Celeste/blob/master/Source/PICO-8/Classic.cs#L289-L290)) y en el dash ([L248](https://github.com/NoelFB/Celeste/blob/master/Source/PICO-8/Classic.cs#L248), [L373](https://github.com/NoelFB/Celeste/blob/master/Source/PICO-8/Classic.cs#L373)).
- Cálculo propio: si el cart actualiza a 30 Hz, que es lo estándar en PICO-8 aunque no lo verifiqué en el emulador, la bocanada dura 15 updates = 0,5 s.

**deepnight/gamefeel (Bénard, Dead Cells)**
- Aterrizaje, `Fx.landSmoke`: **20 partículas** que alternan lado (`i%2`) y nacen a 0–6 px del pie hacia su lado. Color 0xb78662 (marrón), **alfa objetivo 0,1–0,2**, escala 0,3–0,5 de la textura de humo. `dx = 0,1–1` px/frame hacia afuera, `dy = −0,1 a −0,4`, fricción 0,92–0,94 por frame, rotación aleatoria, vida 0,3–0,9 s y fade-out de 0,3–1,5 s — [Fx.hx L363–382](https://github.com/deepnight/gamefeel/blob/HEAD/src/game/Fx.hx#L363-L382).
- Disparo del efecto: `if (options.jumpFx && cHei >= 3)`, donde `cHei` es la altura de caída en celdas de 16 px medida desde la cima: `fallStartPxY` se reinicia mientras dy ≤ 0 — [Hero.hx L109–113](https://github.com/deepnight/gamefeel/blob/HEAD/src/game/en/Hero.hx#L109-L113), [Entity.hx L835–866](https://github.com/deepnight/gamefeel/blob/HEAD/src/game/Entity.hx#L835-L866). El código prevé una rama suave con alfa 0,25, pero queda inalcanzable porque está anidada dentro del mismo `if cHei >= 3`. En la práctica **las caídas de menos de 3 celdas no levantan polvo** (lectura de código).
- Doble salto, `Fx.doubleJump`: **15 líneas aditivas** que suben (`dy −0,5 a −1`, fricción ≈0,8, vida 0,1–0,2 s, ±8 px a los lados) **más 10 bocanadas** de humo azul grisáceo 0x616986 (`dy −0,2 a −2`, vida 0,3–0,9 s, escala 0,3–0,6) — [Fx.hx L436–470](https://github.com/deepnight/gamefeel/blob/HEAD/src/game/Fx.hx#L436). En el fragmento leído del salto normal no hay llamada a `fx`, solo squash X 0,55 ([Hero.hx L358–368](https://github.com/deepnight/gamefeel/blob/HEAD/src/game/en/Hero.hx#L358-L368)), aunque la opción dice "smoke puff when the player jumps, double-jumps or lands" ([Options.hx](https://github.com/deepnight/gamefeel/blob/HEAD/src/game/Options.hx)).
- **Cálculo propio en H (H = 22 px), suponiendo partículas a 60 fps (inferencia sobre `tmod`):** el umbral de 3 celdas son 48 px = **2,2 H**; la rapidez lateral, 6–60 px/s = 0,27–2,7 H/s, con fricción ≈ e^(−4,4/s); la franja de aparición, ±0,27 H. En el ranger: umbral ≈ 222 px de caída; 28–278 px/s; ±28 px.

**Hollow Knight**
- El Knight tiene un prefab propio de aterrizaje duro (`hardLandingEffectPrefab`) y un clip propio (`HeroAudioController.hardLanding`), según el código de HKMP, que replica los efectos — [HKMP HardLand.cs](https://github.com/Extremelyd1/HKMP/blob/master/HKMP/Animation/Effects/HardLand.cs). Que el aterrizaje duro tenga un efecto separado del normal es dato; cantidades y forma, s/d.

### Inferences
- La regla común es **umbral más todo o nada**. El polvo marca "caíste de verdad", no "tocaste el piso". Celeste corta en 0,5 × MaxFall. deepnight corta en una caída mayor que su propio salto: su salto llega a ≈2 celdas, cálculo propio aproximado con `dy = −0,45` y gravedad 0,05 por paso a 30 Hz, ignorando `reduceGravity` y posibles fricciones, o sea confianza baja. Si es así, un salto completo al mismo nivel no levanta polvo.
- **Bug del prototipo (cálculo propio con datos del encargo):** el tier duro dispara con vy > 900 px/s y un salto completo aterriza a ≈1067 px/s, así que todo salto completo cuenta como duro. El tier pierde su función de señal.
- Dirección: las tres fuentes mandan el polvo **hacia arriba o en diagonal hacia afuera, lento y achicándose**. El prototipo lo manda sobre todo a ras del piso a 60–170 px/s (0,6–1,7 H/s), rápido para la escala de Celeste (0,3–0,9 H/s). Queda dentro del rango de deepnight, pero allá el alfa es 0,1–0,2.
- El wall jump de Celeste orienta el polvo diagonal y lejos de la pared. Es la versión de "empuje" que sirve como modelo para el doble salto: el polvo sale **en contra** del impulso.
- Hay dos formas de hacerlo: partículas (Celeste, deepnight) o un sprite animado de 3 dibujos (Celeste PICO-8). Con un pipeline de sprites a 12 fps, una bocanada de 3–4 dibujos a 12 fps (0,25–0,33 s) es barata y coherente con el estilo del personaje.

### Gaps
- Tamaño en px de las texturas `smoke0`–`smoke3` de Celeste: s/d (no se pueden sacar del repo).
- Hollow Knight: cantidad, forma y dirección del polvo normal y duro: s/d. Los valores están en prefabs de Unity, no en código, y la búsqueda no los encontró.
- Dead Cells (el juego), Ori, Shovel Knight: sin fuentes con números.
- GMTK Platformer Toolkit: el devlog [Behind the Code](https://gmtk.itch.io/platformer-toolkit/devlog/395523/behind-the-code) solo cubre movimiento (verificado), y el código del toolkit no es público.
- Tutoriales de polvo de Pedro Medeiros (saint11): no los encontré; saint11.org redirige a saint11.art y no los indexé.

---

## 2. Estelas y afterimages (sobre todo en el doble salto)

### Takeaway
Celeste pone **3 fantasmas por dash**, uno al salir, otro a 0,08 s y otro al terminar a 0,15 s. Cada uno arranca con alfa 0,75, se tiñe con el color del pelo y se apaga en ≈0,5 s visibles, aunque su duración nominal es 1 s. Lo usa en el dash, que es un movimiento rápido, corto y con dirección elegida, y nunca en el salto. Para el doble salto, Hollow Knight (Monarch Wings) y la demo de deepnight usan **un efecto puntual** (alas o flash, más partículas y un sonido propio), **no una estela**.

### Cited Findings
- Celeste, cuándo se crean: `CreateTrail()` al iniciar el dash ([L3588](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3588)), `dashTrailTimer = .08f` ([L3589](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3589), [L3479–3483](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3479-L3483)) y otro al terminar `DashTime = .15f` ([L3619–3621](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3619-L3621), [L78](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L78)). **Conteo propio: 3 fantasmas, a 0, ≈5 y 9 frames.** Las variantes de dash de Badeline también hacen 3 (0, 0,08 s y `DashTime`) — [L5265–5267](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L5265-L5267).
- Color: `TrailManager.Add(this, wasDashB ? NormalHairColor : UsedHairColor)` ([L1087](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1087)), con `NormalHairColor = AC3232` (rojo) y `UsedHairColor = 44B7FF` (celeste) ([L276–278](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L276-L278)). El fantasma comunica el estado del recurso (dash disponible o gastado), no solo la velocidad.
- Duración y fade: `Add(..., float duration = 1f)` ([TrailManager.cs L107](https://github.com/TheCyndaquilDecompilers/Celeste_Decompiled/blob/HEAD/Celeste/TrailManager.cs); la misma firma aparece en el parche de Everest, [TrailManager.cs](https://github.com/EverestAPI/Everest/blob/dev/Celeste.Mod.mm/Patches/TrailManager.cs)). El alfa sigue `0,75 × (1 − Ease.CubeOut(percent))` ([TrailManager.cs L260](https://github.com/TheCyndaquilDecompilers/Celeste_Decompiled/blob/HEAD/Celeste/TrailManager.cs)). **Cálculo propio:** α = 0,55 a 0,1 s; 0,32 a 0,25 s; 0,09 a 0,5 s; 0,01 a 0,75 s. A la vista dura ≈0,4–0,5 s. El buffer original reserva 64 instantáneas de 64×64 px.
- Además del fantasma, el dash de Celeste emite 1 partícula `P_DashA/B` cada 0,02 s ([L3543–3544](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3543-L3544)), un `SlashFx` ([L3587](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3587)) y una onda de distorsión ([L3456](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3456)).
- Hollow Knight, Monarch Wings (doble salto): instancia `dJumpWingsPrefab` (alas), `dJumpFlashPrefab` (flash), un sistema de partículas `dJumpFeathers` (plumas) y `doubleJumpClip` (sonido). HKMP los destruye a los 2 s, "when every effect should be done" — [HKMP MonarchWings.cs](https://github.com/Extremelyd1/HKMP/blob/master/HKMP/Animation/Effects/MonarchWings.cs). No hay estela ni afterimage.
- deepnight: el doble salto usa líneas verticales que suben más humo azul (sección 1) y squash X 0,66, contra 0,55 en el salto normal — [Hero.hx L345–356](https://github.com/deepnight/gamefeel/blob/HEAD/src/game/en/Hero.hx#L345-L356). Para el dash usa **30 líneas aditivas** a 4–8 px/frame con vida ≈0,06 s, color #2f3caf, más un bump de cámara de 6 px y un bump de zoom de 0,03 — [Fx.hx L418–434](https://github.com/deepnight/gamefeel/blob/HEAD/src/game/Fx.hx#L418-L434), [Hero.hx L371–382](https://github.com/deepnight/gamefeel/blob/HEAD/src/game/en/Hero.hx#L371-L382). Tampoco hay fantasmas del sprite.

### Inferences
- Patrón: la **estela de fantasmas va en los movimientos rápidos de trayectoria recta** que el ojo puede perder (dash en 0,15 s, 240 px/s en Celeste). El **doble salto lleva un "golpe" puntual en el punto de impulso** (alas o flash, partículas que salen hacia abajo o arriba, sonido propio), porque la trayectoria es lenta y ya se lee sola.
- Cuándo la estela es ruido: si el movimiento se repite seguido o dura mucho. En un run-and-gun con balas en pantalla, los fantasmas compiten con proyectiles y enemigos. Celeste la limita a 3 instancias por acción y la tiñe con información (el color del dash).
- Con la voltereta del ranger a 12 fps, 2–3 fantasmas del frame actual de la voltereta, a ~0,05–0,08 s, ayudarían a leer el giro. Es opcional; lo mínimo es el golpe puntual.

### Gaps
- Mega Man X (dash ghosts en X4/X5), Metroid Dread (Spin Boost, Space Jump), Shovel Knight: no encontré fuentes con cantidad de fantasmas, frames de separación ni fade.
- Duración real visible del flash y de las alas de Monarch Wings: s/d. HKMP destruye todo a 2 s, que es el tiempo de limpieza, no el de la animación.

---

## 3. Screen shake y hit stop en aterrizajes fuertes

### Takeaway
**Celeste no sacude la pantalla al aterrizar normal**: solo vibra el pad (Light, Short). Reserva el shake vertical para dos aterrizajes guionados (5 px decrecientes en 0,5 s y 3 px en 0,3 s). La demo de deepnight sí sacude, pero escalado por la altura de caída: nada debajo de 2 celdas (≈1,5 H), máximo a las 8 (≈5,8 H), con un "bump" vertical de la cámara de hasta 10 px que se amortigua al 85 % por frame. **Ninguna fuente aplica hit stop al aterrizar**; los freezes van en el dash (Celeste 0,05 s = 3 f) y en los golpes (Nijman, 10–20 ms). El shake del prototipo (±1,5 px a 540) es la mitad del escalón mínimo de Celeste medido en pantalla.

### Cited Findings

**Celeste, implementación del shake (código descompilado de Level.cs)**
- `Shake(float time = 0.3f)` y `DirectionalShake(Vector2 dir, float time = 0.3f)` toman el máximo con el timer vigente, no suman — [Level.cs L4304–4326](https://github.com/TheCyndaquilDecompilers/Celeste_Decompiled/blob/HEAD/Celeste/Level.cs).
- Cada `OnRawInterval(0.04f)`, o sea cada 2,4 frames y no en cada frame, calcula `n = ceil(shakeTimer × 10)` px. Si el shake no es direccional, el offset es un entero aleatorio en [−n, n] en X e Y. Si es direccional, `−dir × n` con signo alternado en cada tick — [Level.cs L3530–3549](https://github.com/TheCyndaquilDecompilers/Celeste_Decompiled/blob/HEAD/Celeste/Level.cs). **Cálculo propio:** 0,3 s da 3 px durante 0,1 s, después 2 px y después 1 px. Va en escalones lineales.
- Accesibilidad: con el ajuste **Half**, el offset se reduce a su signo (±1 px) y el timer cae 1,5 veces más rápido. Con **Off**, no se aplica — [Level.cs L3551–3559](https://github.com/TheCyndaquilDecompilers/Celeste_Decompiled/blob/HEAD/Celeste/Level.cs), [L4306](https://github.com/TheCyndaquilDecompilers/Celeste_Decompiled/blob/HEAD/Celeste/Level.cs). El cart de PICO-8 también respeta `DisableScreenShake` ([Classic.cs L1498](https://github.com/NoelFB/Celeste/blob/master/Source/PICO-8/Classic.cs#L1498)).
- Aterrizaje normal: squash, polvo, `Input.Rumble(RumbleStrength.Light, RumbleLength.Short)` y SFX; **no hay `Shake` ni `Freeze`** — [Player.cs L2554–2581](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2554-L2581).
- Aterrizaje "fuerte" normal: si cayó más de 50 px (`highestAirY < Y − 50`, ≈3,1 H_vis) a vy ≥ MaxFall y con |vx| ≥ MaxRun, reproduce la animación `RunStumble`. Es una reacción solo visual — [L2564–2565](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2564-L2565).
- Aterrizajes guionados: la caída del Templo hace `DirectionalShake((0,1), 0.5f)`, un shake vertical de 5→1 px en 0,5 s (cálculo propio), con Rumble Strong y `Sprite.Scale.Y = 0.7` — [L4936–4944](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L4936-L4944). El summit hace `DirectionalShake(Vector2.UnitY)`, 3→1 px en 0,3 s — [L5165–5166](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L5165-L5166).
- Dash: `Celeste.Freeze(.05f)`, 3 f de freeze ([L3448–3449](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3448-L3449)), más `DirectionalShake(DashDir, .2f)`, 2→1 px en 0,2 s ([L3565](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3565)). Otros freezes: 0,05 s en [L3839](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3839), 0,1 s en [L3985](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3985) y 0,01 s al romper un cristal ([L5000](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L5000)). Ninguno está en un aterrizaje.
- **Cálculo propio en % de pantalla (alto de 180):** 1 px = 0,56 %, 3 px = 1,7 %, 5 px = 2,8 %. A 540 equivalen a 3, 9 y 15 px. El prototipo usa ±1,5 px = 0,28 %.

**Celeste Classic (PICO-8)**
- Dash: `freeze = 2` (frames) y `shake = 6` (frames). Durante el shake la cámara se mueve `−2 + rnd(5)`, de −2 a +2 px sobre 128 — [Classic.cs L355–357](https://github.com/NoelFB/Celeste/blob/master/Source/PICO-8/Classic.cs#L355-L357), [L1490–1504](https://github.com/NoelFB/Celeste/blob/master/Source/PICO-8/Classic.cs#L1490-L1504). Al aterrizar solo aparece la bocanada; no hay shake.

**deepnight/gamefeel (run-and-gun de demostración)**
- `onLand(cHei)`: `pow = clamp((cHei − 2)/6, 0, 1)`. Aplica `camera.bump(0, 10·pow)`, `camera.shakeS(0.6·pow, 0.8·pow)` y `bumpZoom(0.03·pow)` — [Hero.hx L67–90](https://github.com/deepnight/gamefeel/blob/HEAD/src/game/en/Hero.hx#L67-L90). La opción se describe como "Y shake" al caer desde lo alto y "X shake" al disparar ([Options.hx](https://github.com/deepnight/gamefeel/blob/HEAD/src/game/Options.hx)).
- Cámara: el bump se amortigua `×0,85` por frame. El shake es `cos(ftime·1,1)·2,5·pow·ratio` en X y `sin(0,3 + ftime·1,7)·2,5·pow·ratio` en Y: una oscilación suave, no aleatoria, que decae lineal con el tiempo restante. El zoom-bump se amortigua `×0,9` por frame — [Camera.hx L181–222, L315](https://github.com/deepnight/gamefeel/blob/HEAD/src/game/Camera.hx#L181-L222).
- Disparo: `bump(−dir·3, 0)`, `shakeS(0.1, 0.2)` (0,5 px), un flash de 0,04 s y `lockControlS(0.1)` — [Hero.hx L158–187](https://github.com/deepnight/gamefeel/blob/HEAD/src/game/en/Hero.hx#L158-L187). Cada paso de la carrera: `bump(0, 0.5)` y `shakeS(0.3, 0.2)` — [Hero.hx L304–317](https://github.com/deepnight/gamefeel/blob/HEAD/src/game/en/Hero.hx#L304-L317).
- **Cálculo propio en H (22 px, celda de 16):** el efecto empieza a 2 celdas (1,45 H) y llega al máximo a 8 celdas (5,8 H). En el máximo: bump de 10 px = 0,45 H, con semivida de ln 0,5 / ln 0,85 ≈ 4,3 frames; shake de 2 px = 0,09 H durante 0,6 s.

**Hit stop: referencias**
- Nijman (Nuclear Throne): el juego "freezes for about 10–20 milliseconds" cuando algo recibe un golpe. Son 0,6–1,2 frames. El mismo resumen da camera kick de 6 px y shake +4 que decae rápido, a 320×240 y 30 fps — [resumen de Tom Armitage, infovore](https://infovore.org/?p=5275).
- Smash: hitlag `⌊(d·0,65 + 6)·…⌋` en Ultimate. Un golpe de 15 % da 8 f (Melee), 10 f (Brawl y 4) o 15 f (Ultimate); el tope es 20 f (Melee) o 30 f (Brawl en adelante) — [SmashWiki Hitlag](https://www.ssbwiki.com/Hitlag).
- Sakurai describe el hitstop como recurso sobre todo de los fighters 2D (resumen de búsqueda de la columna de Famitsu, sin leer el texto completo) — [Source Gaming](https://sourcegaming.info/2015/11/11/thoughts-on-hitstop-sakurais-famitsu-column-vol-490-1/).

**Shake por trauma (Eiserloh)**
- La charla existe: "Math for Game Programmers: Juicing Your Cameras With Math", Squirrel Eiserloh, GDC 2016. Cubre "camera shake" y "smoothed motion" — [GDC Vault](https://www.gdcvault.com/play/1023557/Math-for-Game-Programmers-Juicing). No conseguí las diapositivas: mathforgameprogrammers.com dio error de SSL.
- Implementaciones que la citan: Bevy usa `TRAUMA_DECAY_PER_SECOND = 0.5`, `MAX_ANGLE = 10°`, `MAX_TRANSLATION = 20` px, `TRAUMA_EXPONENT = 2`, `NOISE_SPEED = 20`, y declara seguir esa charla — [Bevy 2D screen shake](https://bevy.org/examples/camera/2d-screen-shake/). KidsCanCode (Godot) usa `decay = 0.8`/s, `max_offset = (100, 75)` px, `max_roll = 0.1` rad, `trauma_power = 2` (sugiere 2 o 3), con ruido OpenSimplex de período 4 — [KidsCanCode](https://kidscancode.org/godot_recipes/3.x/2d/screen_shake/). Estos números son de los tutoriales, no de Eiserloh.

**Accesibilidad**
- Las Game Accessibility Guidelines no nombran el screen shake explícitamente. Lo más cercano: "Provide an option to turn off / hide background movement" (intermedio) y "Avoid any sudden unexpected movement or events" (avanzado) — [GAG full list](https://gameaccessibilityguidelines.com/full-list/). Celeste ofrece Off/Half/On (arriba). Bevy aclara que su shake afecta solo la vista renderizada, no la lógica ([Bevy](https://bevy.org/examples/camera/2d-screen-shake/)).

### Inferences
- **Shake en cada aterrizaje: no.** Celeste no lo hace, y deepnight lo anula por debajo de ≈1,5 H de caída. En un run-and-gun donde cada disparo ya sacude, sumar shake a cada aterrizaje borra la diferencia entre "disparé" y "caí fuerte".
- **Shake direccional vertical** para caídas: lo usan los dos aterrizajes guionados de Celeste y la demo de deepnight (bump en Y). El aleatorio queda para explosiones y daño.
- El escalón mínimo de Celeste equivale a ≈3 px a 540. Por debajo de eso el shake apenas se percibe. Es una inferencia; el ±1,5 px actual puede estar bajo el umbral perceptible.
- **Hit stop al aterrizar: no encontré a nadie que lo use** en las fuentes leídas. Congelar también congela el control de vuelo y de disparo, justo cuando el jugador quiere seguir. Lo dejaría para impactos de bala fuertes o kills (1–3 f, en la línea de Nijman y del dash de Celeste).
- Trauma: sirve para combinar disparos y aterrizajes sin que se pisen. Celeste no suma: toma el máximo del timer. Con disparos continuos, un decay lento como el de Bevy (0,5/s) satura; hace falta un decay de ≥1,5–2/s. Esto es inferencia, sin fuente.

### Gaps
- Hollow Knight: no encontré si el aterrizaje duro sacude la pantalla ni con qué amplitud, ni el umbral `BIG_FALL_TIME`. Los valores están en prefabs; las búsquedas y los repos de decomp no los tenían (el repo "Hollow-Knight-Decompiled" está vacío).
- Metroid (Dread, Samus Returns): sin datos.
- Valores originales de Eiserloh (exponente, decay, máximos): solo hay implementaciones secundarias.

---

## 4. Sonido de salto, doble salto y aterrizaje

### Takeaway
Celeste usa **eventos distintos para cada tipo de salto**: normal, asistido, wall jump izquierda y derecha, super, super wall, climb jump izquierda y derecha. El aterrizaje es un evento `land` con **parámetro de superficie**, sin escalado por velocidad en la llamada. Si el aterrizaje llega dentro de los 0,5 s posteriores a un climb hop, suena el **footstep** en lugar del `land`. Hollow Knight tiene **un clip separado para el aterrizaje duro** y otro para el doble salto. Para variación, la práctica habitual es 3–5 variantes con ±5 % de pitch; son reglas de práctica, no estándares.

### Cited Findings
- Salto: `char_mad_jump`, más `char_mad_jump_assisted` o `char_mad_jump_dreamblock` según el caso — [Player.cs L1680–1685](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1680-L1685). Super y superslide: `char_mad_jump_super` y `char_mad_jump_superslide` ([L1716–1719](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1716-L1719)).
- Wall jump: suenan **dos eventos**, `char_mad_land` con el índice de sonido **de la pared** (el pie golpea la pared) y `char_mad_jump_wall_right` o `char_mad_jump_wall_left` según el lado — [L1770–1773](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1770-L1773). Super wall jump suma `char_mad_jump_superwall` ([L1801–1802](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1801-L1802)). El climb jump tiene variantes de izquierda y derecha ([L1834–1839](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1834-L1839)).
- Aterrizaje: `Play(playFootstepOnLand > 0f ? Sfxs.char_mad_footstep : Sfxs.char_mad_land, SurfaceIndex.Param, surface)`, con la superficie tomada de la plataforma — [L2569–2580](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2569-L2580). `playFootstepOnLand = 0.5f` se fija en el climb hop ([L3291–3294](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3291-L3294)) y descuenta con el tiempo ([L669](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L669)). Los pasos de la carrera suenan en los frames 0 y 6 de la animación ([L363–392](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L363-L392); ya documentado en `celeste_jump_feel.md`).
- Dash: eventos separados por color (rojo o rosa) y por lado (izquierda o derecha) — [L3412–3421](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3412-L3421). La caída guionada del Templo usa un evento propio, `char_mad_mirrortemple_landing` ([L4936](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L4936)).
- La configuración interna de los eventos FMOD de Celeste (variantes, pitch, volumen) no se pudo leer. FMOD publicó el proyecto completo con notas de Kevin Regamey (resumen de búsqueda: [FMOD, apéndice Celeste](https://www.fmod.com/docs/studio/appendix-a-celeste.html)), pero la página no devolvió contenido legible.
- Hollow Knight: `HeroAudioController.hardLanding` es un clip separado ([HKMP HardLand.cs](https://github.com/Extremelyd1/HKMP/blob/master/HKMP/Animation/Effects/HardLand.cs)). `HeroController.doubleJumpClip` va con las alas ([HKMP MonarchWings.cs](https://github.com/Extremelyd1/HKMP/blob/master/HKMP/Animation/Effects/MonarchWings.cs)). El salto llama `audioCtrl.PlaySound(HeroSounds.JUMP)` ([hk-modding api HeroController.cs L377](https://github.com/hk-modding/api/blob/master/Assembly-CSharp/Patches/HeroController.cs#L377)).
- Nuclear Throne (Nijman): un sonido en cada acción. Los impactos mezclan un sonido de material (carne, planta, roca, metal) con el del enemigo — [infovore](https://infovore.org/?p=5275).
- Variación (prácticos, no estándar): 3–5 variantes de footstep y pitch aleatorio de ≈±5 % (≈±0,85 semitonos) — [bugnet](https://bugnet.io/blog/how-to-implement-footstep-variation-to-avoid-repetition). Un ejemplo de Sound Cue en UE usa pitch máximo de 1,08 — [uhiyama-lab](https://uhiyama-lab.com/en/notes/ue/sound-cue-vs-sound-wave-best-practices/).
- Escalado por altura: un dev en el foro de UE arma tiers de sonido por velocidad vertical (caída corta, media o muy alta) y nota que "bajar de un escalón" disparaba el land por error — [UE AnswerHub](https://answers.unrealengine.com/questions/101962/view.html). CRIWARE propone un impulso corto más un sonido de movimiento cuyo pitch sigue la altura del salto — [CRIWARE blog](https://blog.criware.com/index.php/2023/09/06/platformer-jump/).

### Inferences
- Separar **land suave** (casi un footstep) de **land duro** (clip propio, como Hollow Knight) es más legible que escalar el volumen de un solo sample. Celeste además baja a footstep las micro-caídas. Usar el mismo umbral para el sonido, el polvo duro y el shake mantiene la señal coherente.
- El wall jump de Celeste sugiere superponer un "golpe" con un "whoosh" en el doble salto: un impulso corto más un aire o aleteo.
- El prototipo no tiene sonido. Por lo leído, la lista mínima sería salto, doble salto, land suave, land duro y paso de carrera, más disparo e impacto.

### Gaps
- No encontré una charla de GDC de audio específica sobre salto y aterrizaje en plataformas, ni los parámetros reales de pitch y variantes de Celeste o Hollow Knight.
- GMTK: sin datos de sonido.

---

## 5. Landing lag y recuperación

### Takeaway
Los plataformeros de precisión y los run-and-guns medidos **no bloquean el control al aterrizar**. Mario y Mega Man aceptan el salto en el mismo frame del aterrizaje. Celeste solo reproduce un stumble visual tras caídas largas y rápidas. Ray (Hard Corps) tiene un asentamiento visual de ≈4 f. El lag aparece donde se quiere **peso o castigo**: en Smash, 2–8 f según juego y dureza; en la demo de deepnight, 0,06 s en todo aterrizaje y hasta 0,3 s de bloqueo más 0,75 s sin caminar tras caídas de ≥6 celdas (≈4,4 H); en Hollow Knight, con un estado de aterrizaje duro propio que el dash evita al reiniciar el timer.

### Cited Findings
- Celeste: al aterrizar no hay cambio de estado ni bloqueo; solo squash, polvo, rumble y SFX ([L2554–2581](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2554-L2581)). Tras caídas de más de 50 px a MaxFall y con |vx| ≥ MaxRun suena `RunStumble`, una animación sin bloqueo en el código citado ([L2564–2565](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2564-L2565)). El buffer de salto de Celeste dispara el salto en el frame de aterrizaje ([Celeste & Forgiveness](https://maddymakesgames.com/articles/celeste_and_forgiveness/)).
- Super Mario Bros. y Mega Man aceptan el salto desde el primer frame en el piso (lectura de código en notas previas: [smbdis.asm](https://gist.github.com/1wErt3r/4048722), [Bisqwit MM1](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt); ver `mario_megaman.md` L236–242).
- Contra: Hard Corps (Ray): tras la voltereta, el sprite de pie aparece 4 px alto y baja 1 px por frame durante ≈4 f. Es un asentamiento sin dibujos de aterrizaje (medición propia previa, `hardcorps_blazingchrome_measured.md` L352, sobre [este video](https://www.youtube.com/watch?v=rGz3VpVhUlk&t=75s)). En las hojas de sprites no hay frames de caída ni de aterrizaje (`hardcorps_blazingchrome_sheets.md` L238).
- Smash: aterrizaje liviano de 4 f en 64; en Melee "most characters have a 4 frame landing animation, regardless of how fast they are falling"; liviano de 2 f desde Brawl. El pesado es de 8 f en 64 y de 2–6 f desde Brawl, y ocurre cuando el personaje lleva un tiempo propio de cada personaje cayendo a velocidad máxima. Por eso aterrizar cerca de la cima del salto es más rápido — [SmashWiki Landing lag](https://www.ssbwiki.com/Landing_lag).
- deepnight/gamefeel, con la opción `controlLocks`:
  - si `cHei > 4` celdas: `pow2 = clamp((cHei − 4)/2)`, `lockControlS(0.3·pow2)`, `walkLock 0.75·pow2` s y la velocidad X multiplicada por `0,5·pow2`;
  - si no: `lockControlS(0.06)` y velocidad X ×0,7.

  La animación de aterrizaje dura `0.5·pow` s ([Hero.hx L71–102](https://github.com/deepnight/gamefeel/blob/HEAD/src/game/en/Hero.hx#L71-L102)). **Cálculo propio:** 0,06 s ≈ 3,6 f en cada aterrizaje; el bloqueo duro empieza a 2,9 H de caída y llega al máximo a 4,4 H (18 f de bloqueo total y 45 f sin caminar). Ojo con la línea de velocidad: con pow2 bajo, X queda casi en 0. Parece intencional o un error, y no lo puedo distinguir.
- Hollow Knight: hay un estado de aterrizaje duro con efecto y sonido propios (HKMP). El dash llama `ResetHardLandingTimer()` en cada frame, así que **un dash en el aire cancela la acumulación que lleva al aterrizaje duro** — [hk-modding api HeroController.cs L869–872](https://github.com/hk-modding/api/blob/master/Assembly-CSharp/Patches/HeroController.cs#L869-L872). Duración del bloqueo y umbral: s/d.
- Demo deepnight, disparo: cada disparo bloquea 0,1 s el control (`lockControlS(0.1)`, [Hero.hx L186](https://github.com/deepnight/gamefeel/blob/HEAD/src/game/en/Hero.hx#L186)). Esa demo acepta bloqueos cortos como parte del peso.

### Inferences
- El landing lag ayuda cuando el juego **quiere castigar** caídas o ataques aéreos (Smash) o **dar peso** a un personaje lento (Hollow Knight, demo deepnight). Molesta en juegos donde el aterrizaje es parte del flujo continuo (Celeste, Mario, Mega Man, Hard Corps). Un run-and-gun rápido está en este segundo grupo.
- Si se agrega, conviene: (a) solo por encima del umbral de caída dura; (b) que el salto, el disparo y el dash lo cancelen, como el dash de Hollow Knight que reinicia el timer o el buffer de Celeste; (c) que sea visual: squash, una pose de 0,15–0,2 s que cualquier input interrumpe y un stumble a velocidad.
- La pose de aterrizaje de 0,2 s del prototipo, solo estando quieto y sin bloqueo, ya coincide con el patrón "visual sin lag".

### Gaps
- Hollow Knight: duración del estado de aterrizaje duro, umbral de tiempo o velocidad de caída y qué inputs lo cancelan: s/d.
- Castlevania, Mega Man X: no encontré datos de recuperación al aterrizar.
- "Celeste & Forgiveness" (Thorson) no menciona landing lag (ya resumido en las notas previas).

---

## 6. Recomendación concreta para el prototipo (run-and-gun rápido, sprite de 102 px, vista de 960×540)

### Takeaway
Bajar el polvo de despegue a un toque mínimo, separar aterrizaje suave y duro **por altura de caída y no por la velocidad actual**, dar al doble salto un golpe propio (anillo o puff hacia abajo, squash y sonido) en lugar de estela, sacudir solo en el aterrizaje duro con un shake vertical de 6–9 px decreciente, **no** poner hit stop al aterrizar ni landing lag, y sumar 6 sonidos básicos. Todos los valores de esta sección son **cálculo propio** a partir de los hallazgos 1–5. Son puntos de partida para probar, no datos.

### Cited Findings
- Bases: polvo de Celeste a 0,3–0,9 H/s, con 4 partículas al saltar y 8 al aterrizar, umbral 0,5 × MaxFall ([L1690](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1690), [L2561–2562](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2561-L2562), [ParticleTypes.cs](https://github.com/TheCyndaquilDecompilers/Celeste_Decompiled/blob/HEAD/Celeste/ParticleTypes.cs)). Umbrales de deepnight por celdas de caída de 2, 3, 4 y 8 ([Hero.hx L67–114](https://github.com/deepnight/gamefeel/blob/HEAD/src/game/en/Hero.hx#L67-L114)). Shake de Celeste en escalones de 1 px cada 0,1 s, con Half y Off ([Level.cs](https://github.com/TheCyndaquilDecompilers/Celeste_Decompiled/blob/HEAD/Celeste/Level.cs)). Hit stop solo en dash o golpes ([Player.cs L3449](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3449), [infovore](https://infovore.org/?p=5275)). Fantasmas: 3 por dash, alfa 0,75 con fade CubeOut ([TrailManager.cs](https://github.com/TheCyndaquilDecompilers/Celeste_Decompiled/blob/HEAD/Celeste/TrailManager.cs)).
- Física del prototipo (contexto del encargo y reporte previo): un salto completo de 192 px aterriza a ≈1067 px/s; la terminal es 1400 px/s. Si la gravedad de caída es la de subida, 2963 px/s² ([reporte](../../reports/Movimiento%20y%20disparo%20en%20run-and-guns.md)), la terminal se alcanza tras 1400²/(2·2963) ≈ 331 px = 3,2 H de caída. vy = 900 equivale a 137 px de caída (1,3 H) y vy = 1300 a 285 px (2,8 H). Todo es cálculo propio.

### Inferences

**Umbral de caída (base de todo).** Medir `fallHeight = yAterrizaje − yCima` (en px), como deepnight, en vez de mirar vy. Así el umbral no se rompe si después se cambia la gravedad de caída: con la g de caída de 4898 px/s² propuesta en el reporte, un salto completo aterrizaría a ≈1370 px/s, prácticamente en la terminal. Tiers sugeridos en H = 102 px:
- **micro** (< 0,3 H ≈ 30 px: escalones, saltitos): sin polvo y sonido de paso (como el footstep de Celeste).
- **suave** (0,3 H a ≈2,5 H; incluye el salto completo de 1,9 H): polvo chico y land suave.
- **duro** (≥ 2,5–2,8 H ≈ 260–285 px; caídas más largas que el propio salto, en la línea de los 2,2–2,9 H de deepnight y los ≈3 H del stumble de Celeste): polvo grande, shake vertical, land duro y squash más fuerte.

**Polvo, cálculo propio escalando Celeste a H = 102 y mezclando con deepnight.**
- *Despegue*: **4–6 partículas**, nacidas en ±25 px de los pies, dirección arriba ±15° y **sesgadas hacia atrás** del movimiento si corre. Rapidez 30–100 px/s (0,3–1 H/s), vida 0,3–0,45 s, tamaño 10–12 px achicándose a 0 (no creciendo), alfa 0,5–0,7. Alternativa: una bocanada de sprite de 3 dibujos a 12 fps (0,25 s), como el PICO-8.
- *Aterrizaje suave*: **6–8 partículas**, mitad a cada lado, salida a 10–20° sobre el piso. 60–150 px/s con drag ≈4/s (que ya coincide con la fricción de deepnight, ≈e^(−4,4 t)), vida 0,3–0,5 s, tamaño 12 px que se achica.
- *Aterrizaje duro*: **14–20 partículas** con forma de **pluma lateral**: dos abanicos a ≈15° del piso, como el `P_SummitLandB` de Celeste, más 4–6 que suben. 150–260 px/s, vida 0,4–0,6 s, tamaño 14–17 px; alfa más bajo (0,4–0,6) si son muchas, como hace deepnight.
- *Doble salto*: un **anillo o puff hacia abajo**: 8–12 partículas en semicírculo inferior a 80–150 px/s, vida 0,2–0,3 s, más 2–4 líneas verticales rápidas (vida 0,1–0,2 s) como el `doubleJump` de deepnight. Color distinto del polvo del piso, porque nace en el aire (deepnight usa azul grisáceo).

**Doble salto.** El golpe puntual de arriba, más squash X ≈0,65 al impulsar (deepnight usa 0,66 en el doble y 0,55 en el normal) y un sonido propio. La estela es opcional: si se usa, **2–3 fantasmas** del frame de voltereta a 0,05–0,08 s, alfa inicial 0,5–0,6 y fade CubeOut de 0,3–0,4 s, tintados con un color de UI (no blanco puro) para no confundirlos con balas. No usar estela en el salto normal.

**Screen shake.**
- Disparos: mantener chico. Si la pistola dispara seguido, ±1–2 px y 0,04 s está bien. Que no use el mismo patrón que el aterrizaje.
- Aterrizaje suave: **sin shake**. Hoy tiene 0,04 s; sacarlo deja el shake como señal de "duro".
- Aterrizaje duro: **vertical direccional**: offset inicial hacia abajo, alternando signo cada 2–3 frames (0,04 s, como Celeste), amplitud **9 → 6 → 3 px** en escalones de 0,05–0,07 s (total ≈0,15–0,2 s). Es el escalón de Celeste a 540 (3 px por px de juego), recortado en duración por la cadencia del run-and-gun. Alternativa estilo deepnight: bump de cámara de 8–12 px hacia abajo con amortiguación ×0,85 por frame (semivida ≈4 f).
- Si se pasa a trauma: disparo +0,05–0,1, aterrizaje duro +0,35–0,45, `shake = trauma²`, offset máximo ≈12–15 px (2–3 % de 540), sin rotación o ≤1–2°, decay 1,5–2/s. Inferencia; los ejemplos publicados usan decay de 0,5–0,8/s, pensados para eventos sueltos.
- Accesibilidad: opción **Off / Half / Full**. Half puede copiar a Celeste: offset ±1 px de signo y decay ×1,5. El shake se aplica solo al render, nunca a la posición de las balas ni de la mira.

**Hit stop.** **No en aterrizajes.** Si se quiere peso extra en el duro, mejor un squash fuerte (1,4 × 0,6) más el shake. El hit stop se reserva para matar enemigos o recibir daño: 2–3 f (33–50 ms), en la línea de los 10–20 ms de Nijman y los 3 f del dash de Celeste. Hay que evitarlo en cada impacto de bala de la pistola.

**Landing lag.** **No agregar bloqueo de control** en aterrizajes suaves. En el duro, como mucho 0,08–0,12 s (5–7 f) **solo de la velocidad horizontal**: frenar a ×0,5–0,7, como hace deepnight con ×0,7. Salto, disparo y dash lo cancelan siempre. La pose de aterrizaje queda visual: 0,15–0,2 s en duro, 0,1 s en suave, interrumpible por cualquier input, también cuando corre (hoy solo aparece quieto).

**Sonido (lista mínima).**
1. salto: 3 variantes, ±5 % de pitch;
2. doble salto: distinto, impulso más aire o aleteo, 2 variantes;
3. land suave: 3 variantes, volumen 0,6–1,0 según la altura dentro del tier;
4. land duro: clip propio con graves, 2 variantes;
5. paso de carrera: 4–5 variantes, ±5 %, sincronizado con los frames de pisada (Celeste usa 2 por ciclo);
6. aterrizaje micro: el mismo paso.

Mismos umbrales que el polvo. Más disparo, casquillo e impacto según material, como Nijman.

**Orden de prueba sugerido.**
1. Arreglar el umbral (altura de caída).
2. Sacar el shake del aterrizaje suave.
3. Bajar el polvo de despegue.
4. Agregar el golpe del doble salto.
5. Agregar sonido.
6. Recién ahí evaluar fantasmas y trauma.

### Gaps
- Ningún número de esta sección se probó en el prototipo. Son extrapolaciones de Celeste (personaje 2,1 veces más chico en pantalla y sin disparos) y de una demo de enseñanza (deepnight), no de un run-and-gun comercial con fuente abierta.
- Faltan referencias de run-and-guns comerciales para el polvo y el shake de aterrizaje (Metal Slug, Contra, Blazing Chrome, Cuphead), además del asentamiento de ≈4 f de Hard Corps ya medido.
