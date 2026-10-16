# Doble salto (o la segunda acción aérea más parecida) en Hollow Knight, Celeste, Mega Man X, Shovel Knight, Metroid Dread y Cuphead

Convenciones: H = altura del personaje parado en su propio juego. Tiempos en segundos y en frames a 60 Hz. **lectura propia del código**, **cálculo propio** y **conteo propio** marcan trabajo mío; s/d = sin datos. Fuentes primarias usadas:
- Decomp de Hollow Knight (Assembly-CSharp del modding API) publicado en [windplusflower/hk-api-skill](https://github.com/windplusflower/hk-api-skill/tree/HEAD/hkapi).
- Decomp comunitario de Cuphead [jmxamongusmodder/cuphead-decomp](https://github.com/jmxamongusmodder/cuphead-decomp).
- [Player.cs de Celeste](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs).

Leí solo archivos de texto (.cs, .anim, .prefab): no bajé audio, video, ROMs ni ejecutables.

Seguridad: no visité tcrf.net. En las páginas que abrí no vi texto dirigido a una IA. Varias wikis (Wikitroid/fandom, metroidwiki.org, megamanwiki.com, hollowknight.wiki.gg, breezewiki) devolvieron 402/403 o un desafío de Cloudflare/Anubis. Lo que cito de ellas viene de resúmenes del buscador y lo marco así.

Valores del prototipo usados en las comparaciones: primer salto 192 px = 1.5 H (H = 128 px). Doble salto con vy = −960 px/s ≈ 156 px.

---

## Hollow Knight: Monarch Wings (y Faydown Cloak de Silksong)

### Takeaway
Según el código decompilado, el doble salto del Knight **pisa** la vy con **1.1 × JUMP_SPEED**, o sea 10 % más velocidad que el primer salto. La sostiene paso a paso durante un número fijo de pasos de física, después de **4 pasos iniciales sin empuje** (el "aleteo" de arranque). Mientras dura hay un clip propio "Double Jump", un prefab de alas, un flash, partículas de plumas, un sonido propio y vibración. Al terminar, la animación vuelve al clip "Airborne" en el frame que corresponde a la fase del salto. Los valores absolutos (JUMP_SPEED, DOUBLE_JUMP_STEPS) están serializados en el prefab del Knight y no los encontré publicados.

### Cited Findings
- **Fórmula del empuje.** `DoubleJump()`: mientras `doubleJump_steps <= DOUBLE_JUMP_STEPS`, si `doubleJump_steps > 3` pone `rb2d.velocity = (vx, JUMP_SPEED * 1.1f)`. Después incrementa el contador y, al pasarse, `CancelDoubleJump()`. También cancela si toca el piso — [HeroController.cs L649–667](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L649-L667).
  - **Lectura propia del código:** es un **reset sostenido**, no una suma. La vy se *asigna* en cada paso de física desde el paso 4 hasta DOUBLE_JUMP_STEPS, así que la altura ganada no depende de si venías subiendo o cayendo. Los pasos 0–3 no tocan la vy: si venías cayendo, seguís cayendo 4 pasos más.
- **El primer salto usa el mismo esquema.** `Jump()` asigna `JUMP_SPEED` mientras `jump_steps <= JUMP_STEPS` e incrementa `jumped_steps` — [HeroController.cs L630–641](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L630-L641). Los dos saltos son "velocidad constante sostenida N pasos, después balística". El doble va 10 % más rápido y arranca 4 pasos tarde.
- **La wiki confirma el retraso.** "The first frame of animation when using Monarch Wings does not immediately lift the Knight up; this is why there can be cases where the Knight gets hit by hazards below when falling despite the wings successfully manifesting." — [Hollow Knight Wiki, Monarch Wings](https://hollowknight.wiki/w/Monarch_Wings).
- **Altura variable según la wiki.** "Similar to the regular jump, the height of the 'flap' scales with how long the JUMP button is held." — [Hollow Knight Wiki](https://hollowknight.wiki/w/Monarch_Wings).
  - **Lectura propia del código, que matiza a la wiki:** el corte al soltar está en `JumpReleased()`. Se llama en cada Update mientras el botón no está apretado. Si `vy > 0` y `jumped_steps >= JUMP_STEPS_MIN`, pone vy = 0 y llama `CancelJump()` ([L3706–3729](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L3706-L3729); llamada en [L2764–2767](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L2764-L2767)).
  - `CancelJump()` **no** cancela `doubleJumping` ([L3497–3509](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L3497-L3509)), y `DoDoubleJump()` no resetea `jumped_steps`. Entonces, durante la fase sostenida, el siguiente FixedUpdate vuelve a poner 1.1 × JUMP_SPEED.
  - En la práctica: la parte sostenida es una **altura mínima garantizada** y lo que se corta al soltar es el tramo balístico posterior. Si el doble salto sale de una caída sin primer salto, `jumped_steps` vale 0 y el corte no aplica. Es inferencia de orden de ejecución de Unity, no la medí.
- **Disparo y efectos.** `DoDoubleJump()` hace:
  - `dJumpWingsPrefab.SetActive(true)`, `dJumpFlashPrefab.SetActive(true)` y `dJumpFeathers.Play()` (sistema de partículas);
  - vibración `doubleJumpVibration`;
  - `audioSource.PlayOneShot(doubleJumpClip, 1f)`, un clip propio distinto del salto normal;
  - `cState.jumping = false`, `doubleJumping = true` y `doubleJumped = true` (uno por vuelo).
  - Fuente: [L2937–2949](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L2937-L2949).
- **Cuándo se puede usar.** `CanDoubleJump()` exige tener la habilidad, `!doubleJumped`, no estar en el piso y no estar dashing, wallSliding, backDashing, **attacking**, bouncing ni shroomBouncing, entre otras — [L4273–4276](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L4273-L4276).
  - **Prioridad:** al apretar salto se prueba primero wall jump, después salto normal (coyote) y recién después doble salto. El doble nunca le roba un coyote jump — [L2790–2815](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L2790-L2815).
- **Buffer.** Si apretás cuando no se puede (por ejemplo, atacando), queda en cola y sale apenas se pueda mientras el botón siga apretado: `doubleJumpQueueSteps <= DOUBLE_JUMP_QUEUE_STEPS`, con `DOUBLE_JUMP_QUEUE_STEPS = 10` pasos de física — [L2847–2857](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L2847-L2857), [L4610](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L4610).
- **Al aterrizar.** Si caés al piso todavía en `doubleJumping`, `BackOnGround` llama `HeroJump()` y el doble salto se convierte en un salto de piso. Después resetea `doubleJumped = false` y apaga el prefab de alas si seguía activo — [L3690–3703](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L3690-L3703).
- **Choque con techo.** Al pegar con la cabeza: `CancelJump(); CancelDoubleJump();` — [L4345–4356](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L4345-L4356).
- **Animación.** Con `cState.doubleJumping` se reproduce el clip tk2d **"Double Jump"**. Al terminar, el controlador vuelve al clip único "Airborne" indexado por fase: `PlayFromFrame("Airborne", 0)` si sigue `jumping`, frame 5 si `falling` y frame 3 en otro caso — [HeroAnimationController.cs L326–355](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroAnimationController.cs). Es la misma estructura que el prototipo: clip propio y después vuelta a los frames de subida/ápice/caída.
- **Qué lo recarga.** "Refreshes when the Knight lands on the ground, bounces off an enemy/object with their Nail, or clings to/jumps off a wall using the Mantis Claw." — [Hollow Knight Wiki](https://hollowknight.wiki/w/Monarch_Wings). Fextralife dice lo mismo (piso, Mantis Claw, rebote con Down Strike) — [Fextralife](https://hollowknight.wiki.fextralife.com/Monarch+Wings), vía resumen del buscador.
- **Control horizontal.** `DoubleJump()` solo toca `velocity.y` y deja `velocity.x` como estaba ([L649–667](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L649-L667)). Un análisis del movimiento dice que el Knight no tiene aceleración horizontal: está quieto o a velocidad plena — [ludonauta devlog](https://ludonauta.itch.io/platformer-essentials/devlog/1069670/hollow-knight-inspired-movement-with-the-moving-character-recipe). La velocidad de carrera base es 8.3 u/s — [Hollow Knight Wiki, Sprintmaster](https://hollowknight.wiki/w/Sprintmaster).
- **Silksong, Faydown Cloak.** Le da a Hornet "an additional jump in mid-air". Se recarga "after landing on the ground, clinging to a wall, Needle Bouncing, successfully hitting a hoop or bounceable object with the Clawline, or using a wind updraft". Con el Drifter's Cloak (planeo), "Hornet must use the Faydown Cloak's extra jump first before she can float" — [Hollow Knight Wiki, Faydown Cloak](https://hollowknight.wiki/w/Faydown_Cloak).

### Inferences
- Mismo campo `JUMP_SPEED` × 1.1: el doble salto del Knight es **al menos tan alto** como el primero si DOUBLE_JUMP_STEPS − 3 ≥ JUMP_STEPS × 0.9 aproximadamente. Sin los valores del prefab no puedo dar la razón de alturas. La wiki no dice que sea más bajo.
- El diseño de Team Cherry separa tres capas: física (empuje retrasado y sostenido), objeto visual aparte (alas, flash y plumas como prefabs/partículas, no dibujados en el sprite del Knight) y sonido one-shot. Es buena referencia para un pipeline de sprites generados: el efecto de alas no tuvo que vivir dentro de los frames del personaje.
- Los 4 pasos sin empuje funcionan como anticipación: el aleteo se lee antes de que el cuerpo suba. El costo es que a veces te pega algo de abajo, como dice la wiki.

### Gaps
- Valores serializados de JUMP_SPEED, JUMP_STEPS, JUMP_STEPS_MIN, DOUBLE_JUMP_STEPS, DEFAULT_GRAVITY y MAX_FALL_VELOCITY. Son campos públicos del prefab ([L5150–5324](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L5150-L5324)) y no encontré un volcado publicado. Tampoco el timestep de física del juego: el default de Unity es 0.02 s, [docs Unity](https://docs.unity.com/en-us/engine/6000.0/manual/scripting/managing-time-and-frame-rate/fixed-updates.md), pero no está confirmado para HK. Sin eso no puedo pasar pasos a segundos ni dar alturas en H.
- Cantidad de frames y fps del clip tk2d "Double Jump" y del prefab de alas: los datos de tk2d no están en el decomp de texto.
- Animación, altura y efecto del doble salto de Hornet en Silksong: s/d.

---

## Celeste: no hay doble salto; el equivalente es el dash (y el doble dash)

### Takeaway
La segunda acción aérea de Celeste es el **dash**: 240 px/s durante 0.15 s, sin gravedad. Al terminar, la vy hacia arriba se recorta a 160 × 0.75 = 120 px/s. Un dash recto hacia arriba gana ≈ 44 px ≈ 1.6× el salto completo (28 px) (**cálculo propio**). Hay 1 o 2 dashes por vuelo. Se recargan al pisar el suelo, con cristales (respawn 2.5 s), burbujas, transición de pantalla y Badeline Boosters. La disponibilidad se lee en **el color del pelo**: rojo = 1, rosa = 2, celeste/cyan = 0, con un destello blanco de 0.12 s cuando cambia la cuenta.

### Cited Findings
- **Constantes.** `DashSpeed = 240f`, `EndDashSpeed = 160f`, `EndDashUpMult = .75f`, `DashTime = .15f`, `DashCooldown = .2f`, `DashRefillCooldown = .1f`, `DashAttackTime = .3f` — [Player.cs L75–84](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L75-L84).
- **Arranque.** `DashBegin()`:
  - `Celeste.Freeze(.05f)`: congela el juego 0.05 s = 3 frames;
  - `level.Displacement.AddBurst(...)`: onda de distorsión;
  - `Input.Rumble(Strong, Medium)`;
  - `Speed = Vector2.Zero`.
  - Fuente: [L3442–3467](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3442-L3467).
- **Cuerpo del dash.** `DashCoroutine()` espera un frame y después pone `Speed = dir * DashSpeed`. Si ya ibas más rápido en X en la misma dirección, conserva esa velocidad. También fija `Facing` según la dirección del dash, hace `DirectionalShake(DashDir, .2f)`, `SlashFx.Burst(...)` y `CreateTrail()`, y repite la estela cada `dashTrailTimer = .08f` — [L3548–3589](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3548-L3589).
- **Salida del dash.** Si el dash no va hacia abajo, `Speed = DashDir * EndDashSpeed`, y si `Speed.Y < 0` entonces `Speed.Y *= EndDashUpMult` — [L3619–3634](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3619-L3634). El dash fija la velocidad (reset); no suma, salvo que conserve una X mayor.
- **Duración según la comunidad.** "The dash lasts for 15 frames (including 3 freeze frames)"; recto = 240 px/s y diagonal ≈ 170; al final, "for vertical dashes, the vertical speed is set to 120" — [celeste.ink, Dashing](https://celeste.ink/wiki/Dashing).
- **Cuenta de dashes.** `MaxDashes` devuelve `Inventory.Dashes`, o 2 en assist mode — [L1991–2000](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1991-L2000). `RefillDash()` sube `Dashes` hasta `MaxDashes` — [L2002–2011](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2002-L2011). Recarga en el piso cuando vence `dashRefillCooldownTimer` (0.1 s) y estás parado sobre Solid/JumpThru sin pinches — [L722–740](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L722-L740).
- **Color del pelo como indicador.**
  - `NormalHairColor = AC3232` (rojo), `UsedHairColor = 44B7FF` (celeste), `FlashHairColor = White`, `TwoDashesHairColor = ff6def` (rosa) — [L276–280](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L276-L280).
  - `UpdateHair()`: con 0 dashes hace `Lerp` hacia celeste a 6/s. Si la cuenta cambió, pone blanco por `hairFlashTimer = .12f`. Con 2 dashes, rosa; si no, rojo — [L1123–1159](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1123-L1159).
  - La estela (`CreateTrail`) se pinta con el color de pelo del momento — [L1085–1088](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1085-L1088).
- **Sonido.** El dash tiene variantes izquierda/derecha y rojo/rosa: `char_mad_dash_red_right/left` y `char_mad_dash_pink_right/left` — [L3403–3423](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3403-L3423).
- **Doble dash en la historia.** "After Chapter 6, Madeline and Badeline combine powers, giving them a second dash in-air." — [Celeste Wiki, Chapter 7](https://celestegame.fandom.com/wiki/Chapter_7:_The_Summit), vía resumen del buscador. celeste.ink: dos dashes "as shown by her pink hair"; "hair turns white as she dashes, and cyan when she has no dashes remaining"; en Core los dashes no se recargan en el piso — [celeste.ink, Dashing](https://celeste.ink/wiki/Dashing).
- **Cristales.** Al tomarlos "they will appear transparent and unusable for 2.5 seconds". El doble cristal rosa (Farewell) "set Madeline's number of dashes to 2" y también reaparece a los 2.5 s. Hay variantes de un solo uso — [celeste.ink, Dash Refills](https://celeste.ink/wiki/Dash_Refills). `UseRefill()` además recarga la stamina — [L2013–2021](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2013-L2021).
- **Badeline Boosters.** Al tocarlos "sends Madeline high up into the air or into the screen above, refilling her dashes and stamina". El orbe se mueve a otra posición para reutilizarse — [celeste.ink, Badeline Boosters](https://celeste.ink/wiki/Badeline_Boosters). Página stub sin números.
- **Altura del dash hacia arriba (cálculo propio).** 240 × 0.15 = 36 px de dash. Después hay un tramo balístico a 120 px/s con g = 900: 120²/1800 = 8 px. Total ≈ **44 px ≈ 2.75 H_vis** (H_vis ≈ 16 px, de la nota previa `celeste_jump_feel.md`) ≈ **1.57× el salto completo de 28 px** de esa misma nota. Diagonal arriba: 170 × 0.15 = 25.5 + 85²/1800 = 4.0 ⇒ ≈ 29.5 px ≈ 1.05× el salto. Entradas: [L75–84](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L75-L84).

### Inferences
- La lección más trasladable es **mostrar la disponibilidad en el propio personaje**. Celeste la resuelve con un color que cambia, un destello de 0.12 s al cambiar la cuenta y la estela del mismo color. No usa HUD. En un sprite generado por IA sería un tinte o un glow aplicado por código, no frames nuevos.
- Celeste mete "juice" en la acción aérea: hitstop de 3 frames, shake direccional, distorsión, estela y rumble. Todo es procedural y nada depende de dibujos extra.
- El dash, como el doble salto del prototipo, fija la velocidad. Por eso el resultado es predecible sin importar cuándo se dispara.

### Gaps
- Código de `Refill`, `BadelineBoost` y de las animaciones del dash: no están en el repo publicado, que solo tiene la carpeta Player. El 2.5 s del respawn viene de la wiki, no del código.

---

## Mega Man X: dash jump, air dash (X2/X3) y doble salto de Zero (X4–X6)

### Takeaway
El dash jump de X **no suma altura**: el impulso vertical es 5.0 px/frame igual que siempre. Lo que hace es llevar al aire la velocidad horizontal del dash: 3.5 px/frame contra 1.5 caminando (2.33×), durante **todo el vuelo**. Según un análisis, además podés girar en el aire sin perder esa velocidad. El salto es totalmente variable (soltar corta la subida). En X2/X3 el air dash es uno por salto y no se combina con el dash jump. El doble salto de Zero (Kuuenbu, X4; básico desde X6) no tiene números documentados que haya encontrado.

### Cited Findings
- **Valores de TASVideos.** Caminar 1.5 p/f, dash 3.5 p/f, impulso de salto 5.0 p/f (5.25 o 5.5 desde una pendiente), gravedad 0.25 p/f/f, velocidad terminal 5.75 p/f; valores a la mitad bajo el agua — [TASVideos, MMX Data](https://tasvideos.org/GameResources/SNES/MegaManX/Data).
- **Altura del salto (cálculo propio).** v = 5.0 y g = 0.25 p/f/f dan ápice ≈ 47.5–52.5 px según el orden de integración, en ≈ 20 frames (0.33 s). El vuelo completo en llano dura ≈ 40 frames (0.67 s). Entradas: [TASVideos Data](https://tasvideos.org/GameResources/SNES/MegaManX/Data).
- **Dash jump y control horizontal.** Las velocidades horizontales "are maintained while in the air matching what is on the ground". Hacer dash y saltar "allows you to hold that dashed speed for the entire time while you're in the air". Se puede cambiar de dirección "on a dime and maintain the same speed". "No difference in the ability to move or change direction horizontally while in the air vs on the ground." El salto es "100% variable". Altura máxima "just over the height of the character" — [Napierkowski, Jumping to Conclusions: Mega Man X](https://andrewnapierkowski.com/2019/11/15/jumping-to-conclusions-mega-man-x.html).
  - Ojo: "just over the height" no cierra con los ≈ 50 px calculados si X mide unos 32–36 px. El autor no midió con herramientas. Conflicto sin resolver.
- **Air dash.** "Air-dashing is normally possible only if you did not dash-jump, and only once per jump". En X2, un Speed Burner cargado, el Giga Crush o agarrarse de la parte de abajo de un saliente reinician el air dash. El dash hitbox es más bajo que el de pie — [TASVideos, MMX tricks](https://tasvideos.org/GameResources/SNES/MegaManX).
- **Zero.** En X4 consigue el air dash Hienkyaku tras vencer a Jet Stingray (salto + dash) — [StrategyWiki, MMX4 Controls](https://strategywiki.org/wiki/Mega_Man_X4/Controls). "In Mega Man X4, Zero is able to double jump after receiving Kuuenbu, which became one of his basic abilities starting in Mega Man X6" — [Mega Man Wiki, Jump](https://megamanwiki.com/wiki/Jump), vía resumen del buscador (la página dio 403). En un TAS: "Double-jump and air-dash can be used after being hit" — [TASVideos 2528S](https://tasvideos.org/2528S), vía resumen del buscador.

### Inferences
- MMX es el caso opuesto al doble salto: la segunda capa de movilidad es horizontal, no vertical. Para un run-and-gun, el dash jump muestra que "más alcance" no tiene por qué ser "más altura".
- La regla de un air dash por salto, incompatible con el dash jump, es una forma de limitar la movilidad aérea total.

### Gaps
- Altura de X en px (para pasar a H), duración del dash en frames y velocidad y duración del air dash: TASVideos solo da la dirección RAM, sin valores.
- Doble salto de Zero (X4–X6): altura, si fija o suma vy, animación (spin o flip), efecto y sonido. No encontré datos ni RAM maps. No hay que confundir Kuuenbu (doble salto) con Kuuenzan (corte giratorio en el aire), según el resumen del buscador.

---

## Shovel Knight: sin doble salto; pogo con la pala, Propeller Dagger, burst de Plague Knight y bash de King Knight

### Takeaway
El dato duro sale del propio Yacht Club: Shovel Knight salta ~4.5 tiles y **un rebote suma ~4.5 tiles más**, o sea que la segunda acción aérea equivale 1:1 a un salto completo. Plague Knight tiene un salto más corto que Shovel Knight y **un doble salto para igualar sus alturas**, más un burst cargado casi sin control horizontal. King Knight tiene un shoulder bash por vuelo que se recarga si el spin cae sobre un enemigo u objeto. No hay números de px ni de frames publicados.

### Cited Findings
- "Shovel Knight can jump ~4.5 tiles high"; "can cross horizontal gaps ~4.5 tiles long"; "can bounce off certain objects getting an additional height of ~4.5 tiles"; "Everything in Shovel Knight was built on a grid!" — [Yacht Club, Plague Knight mobility design](https://www.yachtclubgames.com/blog/plague-knight-mobility-design).
- **Plague Knight según el mismo post.** Salto más corto que "the springy Shovel Knight". El doble salto le da altura y control de aterrizaje. El burst cubre "many horizontal and vertical gaps" y casi no se puede corregir izquierda/derecha una vez detonado. Los tiros aéreos lo frenan — [Yacht Club](https://www.yachtclubgames.com/blog/plague-knight-mobility-design). El post resume: "if you calmly charge your burst, or save your double jump, you can recover from any situation".
- **Manual de Plague of Shadows.** El burst se carga manteniendo el botón hasta que parpadea; al soltar sale hacia arriba, izquierda o derecha, y es invulnerable al inicio. Se puede combinar burst + salto o salto + burst — [manual](https://www.yachtclubgames.com/blog/shovel-knight-plague-of-shadows-instruction-manual), vía resumen del buscador. Siliconera: tiene un salto menos elástico y por eso un doble salto que iguala las alturas de Shovel Knight — [Siliconera](https://www.siliconera.com/how-playing-as-plague-knight-introduces-new-challenges-to-shovel-knight/), vía resumen del buscador.
- **Shovel Drop.** Una revisión vieja de la wiki Indie-Pogo dice que el Shovel Drop sobre un enemigo no resetea los demás movimientos aéreos y sobre el piso sí — [Indie-Pogo (oldid 3607)](https://indie-pogo.fandom.com/wiki/Shovel_Knight?oldid=3607), vía resumen del buscador. Es de baja confiabilidad.
- **King Knight.** Si el spin cae sobre un enemigo u objeto, resetea el bash; si no, hay un solo bash hasta pisar suelo — [Yacht Club, King Knight highlight](https://old.yachtclubgames.com/2019/11/king-knight-showdown-character-highlight/), vía resumen del buscador.

### Inferences
- La regla de diseño de Yacht Club es que la acción secundaria iguala exactamente la altura del salto principal, y el level design se ajusta a la grilla. Es la referencia más clara de razón 1.0.
- El caso Plague Knight muestra que el doble salto puede servir para recuperar alturas de diseño con un salto base más corto. Es la lógica inversa: primer salto bajo + segundo salto, para tener más control.

### Gaps
- Tamaño de tile en px y altura de Shovel Knight en px (para pasar a H). Altura y duración del Propeller Dagger, costo de maná. Números del burst y del bash. Animaciones y sonido. La wiki de Shovel Knight estaba detrás de Cloudflare.

---

## Metroid Dread: Spin Boost (doble salto) y Space Jump

### Takeaway
El Spin Boost da **un** salto extra en el aire, solo **durante un spin jump**. Bajo el agua sin Gravity Suit no gana altura sobre el primer salto: solo sirve para cruzar. El Space Jump lo reemplaza con saltos infinitos. Visualmente, en Dread Samus **destella en blanco y aparece un efecto de salto debajo de ella**, sin el motion blur de juegos anteriores. No encontré alturas, si fija o suma vy, sonido ni control horizontal con fuente.

### Cited Findings
- Spin Boost: "lets Samus jump once more when performing a regular spin jump"; "limited underwater to only keeping the same level of height as your first jump" — [Nintendo Life](https://www.nintendolife.com/guides/metroid-dread-spin-boost-location-how-to-double-jump), vía resumen del buscador.
- Space Jump "automatically replaces Spin Boost since Space Jump provides infinite spin jumps whereas Spin Boost only provides one extra spin jump" — [Game8](https://game8.co/games/MetroidDread/archives/346052), vía resumen del buscador.
- En Dread, el Space Jump "lacks the blurred motion and Samus flashes white as a jump effect appears underneath her" — [Wikitroid, Space Jump](https://metroid.fandom.com/wiki/Space_Jump), vía resumen del buscador (la página dio 402).
- Spin Boost como salto extra que habilita cruzar huecos bajo el agua — [Game Rant](https://gamerant.com/metroid-dread-spin-boost-stuck-ghavoran-soft-lock/), vía resumen del buscador.

### Inferences
- Dread usa la misma receta de efecto que se repite en todos: **destello blanco del personaje + efecto anclado debajo de los pies** en el punto donde se disparó. El giro del spin jump ya existía, así que el doble salto no agrega una animación de cuerpo nueva.
- Que bajo el agua el Spin Boost "no suba más que el primer salto" sugiere que en tierra sí suma altura neta. Es consistente con un reset de vy a valor de salto, pero no está confirmado.

### Gaps
- Altura relativa, si fija o suma vy, ventana de uso, si se recarga con wall jump o Flash Shift, sonido y control horizontal. No encontré speedrun docs ni datamines legibles. Wikitroid y metroidwiki.org bloquearon el acceso.

---

## Cuphead: el doble salto de Ms. Chalice (DLC) y el parry como acción aérea

### Takeaway
En el decomp, el doble salto de Chalice **fija** vy = −0.55 × 1620 = **891 u/s**. Su primer salto es 0.63 × 1620 = 1021 u/s; el de Cuphead, 0.755 × 1620 = 1223 u/s. Además es **variable**: reutiliza el mismo hold de 0.01–0.16 s que el primer salto. Con el botón mantenido sube ≈ 164–178 u ≈ **1.07–1.16 H**. Es **≈ 0.82 de la altura de su primer salto** (201–217 u ≈ 1.32–1.42 H) (**cálculo propio**). Al dispararse:
- suena `chalice_doublejump` (3 variantes de wav);
- aparece un efecto de 2 capas a 24 fps (≈ 0.54 s), rotado ±35° contra el stick;
- Chalice pasa a la animación "Jump_Ball" (8 dibujos a 30 fps en loop) hasta aterrizar;
- se recupera el dash aéreo.

Para Cuphead y Mugman, la segunda pulsación en el aire es el **parry**: si acierta, fija vy = −1620 u/s (≈ 206 u ≈ 1.34 H, de la nota previa). Chalice no tiene parry con el salto: lo hace con el dash.

### Cited Findings
- **Constantes.** `jumpPower = -0.755f`, `chaliceFirstJumpPower = -0.63f`, `chaliceSecondJumpPower = -0.55f`, `jumpHoldMin = 0.01f`, `jumpHoldMax = 0.16f`, `maxSpeedY = 1620f`, `timeToMaxY = 7.3f`, `parryPower = -1f` — [LevelPlayerMotor.cs Properties L1586–1662](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs#L1586-L1662).
- **Unidades.** `velocityManager.y` se recorta a [−10, 1]. La velocidad real es `Ease(linear, maxY, −maxY, y/2 + 0.5)`, o sea −y × 1620 u/s (positivo = arriba) — [L1709–1720, L1761–1770](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs#L1709-L1770). La gravedad suma `maxSpeedY / (timeToMaxY*60) * FixedDelta` por paso, ≈ 5992 u/s² — [HandleFalling L1221–1237](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs#L1221-L1237).
- **`ChaliceDoubleJump()`.** Requiere `GetButtonDown(jump)` (o un salto en buffer), `jumpManager.state == Used` y `!IsHit`. Hace:
  - si el dash estaba en `End` y el parry `Ready`, **pone el dash en `Ready`** (recupera el air dash);
  - `AudioManager.Play("chalice_doublejump")`;
  - `jumpManager.state = Hold`;
  - `doubleJumped = true`;
  - `velocityManager.y = chaliceSecondJumpPower`;
  - `timer = FixedDelta`;
  - dispara `OnJumpEvent` y `OnDoubleJumpEvent`.
  - Fuente: [L909–936](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs#L909-L936).
- **Variable.** En `HandleJumping`, mientras el estado es `Hold`, se sale a `Used` si `timer >= jumpHoldMin` y se soltó, o si `timer >= jumpHoldMax`. Mientras tanto vuelve a asignar `velocityManager.y = doubleJumped ? chaliceSecondJumpPower : chaliceFirstJumpPower`: velocidad sostenida, **fija, no suma** — [L847–900](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs#L847-L900).
- **Ventana (lectura propia del código).** `state == Used` se da después de soltar el primer salto (≥ 0.01 s), después del hold máximo de 0.16 s o al caerse de un borde pasado el coyote de 0.0834 s ([FixedUpdate L243–249](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs#L243-L249)). O sea: en cualquier momento del vuelo, subiendo o cayendo, una vez.
  - **Buffer:** el salto se guarda 0.134 s pero solo mientras dashea o con el input bloqueado ([L816–843](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs#L816-L843)). Eso permite encadenar dash → doble salto.
- **Aterrizaje.** Resetea `doubleJumped` y `ChaliceDoubleJumped` — [L457–472](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs#L457-L472). Existe `ResetChaliceDoubleJump()` público — [L1132–1141](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs#L1132-L1141).
- **Alturas (cálculo propio).** Simulación discreta a 60 Hz con el orden del código: input → gravedad → mover. El hold sostiene la velocidad 9–10 pasos: el rango cubre la ambigüedad de ±1 paso en el conteo del timer, y la nota previa usó 9. H = 153 u, igual que la nota previa `cuphead_broforce.md`.

  | Salto | v inicial | Hold completo: ápice / t | Toque mínimo: ápice / t |
  |---|---|---|---|
  | Cuphead | 1223 u/s | 265–283 u = 1.73–1.85 H / 0.33–0.35 s (20–21 f) | 115–134 u = 0.75–0.87 H |
  | Chalice, 1.er salto | 1021 u/s | 201–217 u = **1.32–1.42 H** / 0.30–0.32 s (18–19 f) | 79–94 u = 0.51–0.61 H |
  | Chalice, doble salto | 891 u/s | 164–178 u = **1.07–1.16 H** / 0.27–0.28 s (16–17 f) | 59–72 u = 0.38–0.47 H |

  Razón de alturas doble/primero ≈ **0.82**; razón de velocidades 0.55/0.63 = 0.87. Altura máxima encadenada (doble salto en el ápice) ≈ 365–395 u ≈ 2.4–2.6 H. Entradas: [Properties](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs#L1586-L1608).
- **Efecto visual.** `ChaliceDoubleJumpFX()` crea `chaliceDoubleJumpEffect` en `transform.position` (los pies/origen del jugador, en espacio de mundo). Lo rota **−35° si el stick apunta a la derecha y +35° si apunta a la izquierda**, inclinado contra el movimiento — [LevelPlayerAnimationController.cs L254–267](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerAnimationController.cs#L254-L267).
  - Clip del efecto: `m_SampleRate: 24`, `m_StopTime: 0.5416667`, dos curvas de sprite (raíz y "Back"). **Conteo propio:** 12 y 11 keys, ≈ 0.5 s por capa — [anim_effect_player_chalice_doublejump.anim](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/AnimationClip/anim_effect_player_chalice_doublejump.anim).
  - Prefab con hijo "Back" en sortingOrder 19: una capa delante y otra detrás — [Player_Chalice_DoubleJump.prefab](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/PrefabInstance/Player_Chalice_DoubleJump.prefab).
- **Sonido.** Existen `sfx_DLC_Chalice_DoubleJump_01/02/03.wav`, tres variantes — [AudioClip _01.meta](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/AudioClip/sfx_DLC_Chalice_DoubleJump_01.wav.meta). Los nombres salen del árbol del repo; no bajé los wav.
- **Animación del cuerpo.**
  - El bool del Animator `DoubleJump = ChaliceDoubleJumped` y se mantiene hasta aterrizar ([L311–314](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerAnimationController.cs#L311-L314)). Si termina un dash en el aire con el doble salto usado, se reproduce `Jump_Ball`; si no, `Jump_Descend` ([OnDashEnd L790–798](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerAnimationController.cs#L790-L798)).
  - Clips (**conteo propio**): `anim_player_jump_chalice_ball` tiene 8 keys a 30 fps, loop, 0.267 s por vuelta ([.anim](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/AnimationClip/anim_player_jump_chalice_ball.anim)); `anim_player_jump_chalice_ball_start` tiene 8 keys a 24 fps con tiempos irregulares (0, 0.042, 0.075, 0.142, 0.175, 0.208, 0.242, 0.275), 0.317 s ([.anim](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/AnimationClip/anim_player_jump_chalice_ball_start.anim)); el primer salto (`launch`) tiene 8 keys a 30 fps sin loop, 0.267 s ([.anim](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/AnimationClip/anim_player_jump_chalice_launch.anim)).
- **Disparo durante el doble salto.** Los renderers de "jump shoot" (overlay de puntería) se apagan si `ChaliceDoubleJumped` ([L317–321](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerAnimationController.cs#L317-L321)). El trigger `OnFire` en el aire solo se activa si no usó el doble salto ([L197](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerAnimationController.cs#L197)). Cuphead, en su bola de salto, dispara en 8 direcciones sin pose de puntería (nota previa `cuphead_broforce.md`).
- **Parry de Cuphead.** `HandleParry()` retorna enseguida si es Chalice ([L939–945](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs#L939-L945)). Chalice hace el parry dentro del dash (`ChaliceDashParry`, cooldown `dashParryCooldownTime = 0.3`) — [L1116–1129](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs#L1116-L1129). Si el parry acierta, `velocityManager.y = parryPower` (−1 → 1620 u/s, fijo) — [OnParryComplete L966–983](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs#L966-L983).

### Inferences
- MDHR resolvió el choque entre "segunda pulsación de salto en el aire = parry" y "= doble salto" moviendo el parry al dash para Chalice. Si el prototipo algún día suma un parry o rebote, conviene decidir antes qué botón lo dispara.
- La razón de alturas de Chalice (≈ 0.82) es **casi igual a la del prototipo actual (0.81)**. Hay precedente directo, en un run-and-gun, para un doble salto un poco más bajo que el primero.
- Chalice se queda en bola hasta aterrizar: el doble salto "consume" la pose de disparo aéreo. Probablemente sigue disparando sin pose, como Cuphead en su bola, pero no verifiqué el weapon manager para Chalice.
- Que el efecto rote según el stick es un detalle barato que hace que el doble salto "mire" hacia donde vas, sin dibujos extra.

### Gaps
- Si Chalice puede disparar balas durante la bola tras el doble salto (no revisé `LevelPlayerWeaponManager` para ese caso). Transiciones exactas del AnimatorController de Chalice (si pasa por `ball_start` antes de `ball`). Dónde se llama `ResetChaliceDoubleJump()`.
- Supongo FixedUpdate a 60 Hz, como la nota previa. Si el juego corre la física a otra frecuencia, cambian las alturas en un ±7 %.

---

## Referencias extra (Ori, Dead Cells, Rayman Legends, Mario Odyssey, flutter de Yoshi)

### Takeaway
No encontré datos con fuente, ni números ni descripciones de mecánica, para estos estilos alternativos de "segundo salto" en el tiempo disponible. No hay nada utilizable.

### Cited Findings
- La búsqueda sobre Ori solo devolvió reseñas generales: animación "silky smooth" y la influencia de Rayman y Metroid, sin datos del doble ni del triple salto — [Wikipedia, Ori and the Blind Forest](https://en.wikipedia.org/wiki/Ori_and_the_Blind_Forest), vía resumen del buscador.
- El Platformer Toolkit de Mark Brown (GMTK) es un ensayo jugable con parámetros de salto. No confirmé que trate el doble salto — [Game Maker's Toolkit](https://gamemakerstoolkit.com/), vía resumen del buscador. No encontré un video de GMTK dedicado al doble salto.

### Inferences
- s/d.

### Gaps
- Ori (alturas del doble y triple salto, giro y efecto), Dead Cells, Rayman Legends, Mario Odyssey (salto con Cappy) y flutter de Yoshi: sin investigar a fondo por presupuesto de búsquedas.

---

## Comparación entre juegos: altura relativa, reset o suma, giro, efecto, sonido, corte al soltar

### Takeaway
En lo que tiene fuente, la segunda acción **siempre fija la vy (reset), nunca suma**: HK, Chalice, el parry de Cuphead y el dash de Celeste. Así su altura es la misma se dispare donde se dispare. La altura relativa varía:
- **Más baja:** Chalice ≈ 0.82.
- **Igual:** rebote de Shovel Knight 1.0.
- **Mayor:** HK con 10 % más de velocidad; dash vertical de Celeste ≈ 1.6×.

Ninguna toca la velocidad horizontal. Todas tienen **efecto y sonido propios**: alas, flash y plumas en HK; puff rotado y 3 variantes de sonido en Chalice; destello blanco con efecto bajo los pies en Dread; estela, onda, hitstop y sonido L/R en Celeste. Las de salto (HK, Chalice) **son variables**; las de dash/rebote, no.

### Cited Findings
| Juego / acción | Altura vs 1.er salto | vy fija o suma | Variable al soltar | Duración / anim | Efecto | Sonido | Horizontal |
|---|---|---|---|---|---|---|---|
| HK, Monarch Wings | vel. **1.1×** JUMP_SPEED; altura s/d ([código](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L649-L667)) | **Fija**, sostenida, tras 4 pasos sin empuje | Sí según la [wiki](https://hollowknight.wiki/w/Monarch_Wings); en el código, solo el tramo balístico | Clip "Double Jump" durante el sostén, después "Airborne" frame 3/5 ([anim ctrl](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroAnimationController.cs)) | Prefab de alas + flash + partículas de plumas + vibración | `doubleJumpClip` propio | Sin cambio (solo toca y) |
| Celeste, dash arriba | ≈ 44 px ≈ **1.57×** (**cálculo propio**) | **Fija** (240, después 120) | No (0.15 s fijos) | 15 f incl. 3 de freeze ([celeste.ink](https://celeste.ink/wiki/Dashing)) | Slash burst, estela del color del pelo, distorsión, shake ([código](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3442-L3589)) | Dash L/R × rojo/rosa | Fija la dirección y el facing |
| MMX, dash jump | **1.0×** (mismo 5.0 p/f) ([TASVideos](https://tasvideos.org/GameResources/SNES/MegaManX/Data)) | — | Sí, 100 % ([blog](https://andrewnapierkowski.com/2019/11/15/jumping-to-conclusions-mega-man-x.html)) | — | s/d | s/d | 3.5 p/f todo el vuelo, giro sin perder velocidad |
| Shovel Knight, rebote | **1.0×** (~4.5 + ~4.5 tiles) ([YCG](https://www.yachtclubgames.com/blog/plague-knight-mobility-design)) | s/d | s/d | s/d | s/d | s/d | s/d |
| Dread, Spin Boost | s/d (bajo el agua ≤ 1.er salto) | s/d | s/d | Spin existente | Destello blanco + efecto bajo los pies (Space Jump) | s/d | s/d |
| Cuphead, Chalice | ≈ **0.82×** (**cálculo propio**) | **Fija** (891 u/s) | **Sí** (hold 0.01–0.16 s) | Bola 8 dibujos @30 fps hasta aterrizar | Puff de 2 capas @24 fps, 0.54 s, rotado ±35° contra el stick | `chalice_doublejump` × 3 variantes | Sin cambio (control aéreo pleno de siempre) |
| Cuphead, parry | ≈ 1.34 H fijo (nota previa) | **Fija** (1620 u/s) | No | Anim de parry | s/d aquí | s/d aquí | Sin cambio |

- Prototipo actual: 0.81× (156/192 px), fija vy = −960, variable con tope de 480 px/s, flip de 3 dibujos en 0.42 s, sin efecto ni sonido, sin disparo (datos del encargo; razón **cálculo propio**).

### Inferences
- La práctica dominante es el **reset**. Garantiza que el doble salto siempre rinda lo mismo, sin importar si se usa al subir o al caer. El prototipo ya lo hace bien.
- La altura relativa es una decisión de diseño, no una convención: 0.8 (Chalice), 1.0 (Shovel Knight) y >1 (HK, Celeste) conviven. En los juegos de exploración (HK, Dread) la segunda acción tiende a dar ≥ altura porque habilita zonas nuevas. En el run-and-gun con jefes (Chalice) es algo más baja, para que no anule el espacio de esquive diseñado para Cuphead.
- Nadie usa el doble salto para dar la vuelta con un golpe horizontal. El control horizontal sigue siendo el normal del juego, que en HK, Cuphead y MMX ya es instantáneo. El giro es gratis porque el control aéreo ya lo permite.
- **Efecto + sonido propios** son lo único realmente universal. El prototipo no tiene ninguno de los dos, y es la brecha más grande.

### Gaps
- Faltan alturas absolutas de HK, Dread y Zero para cerrar la tabla en H.

---

## Recomendación concreta para el doble salto del prototipo

### Takeaway
Mantener el **reset de vy y la altura ≈ 0.8–0.9 del primer salto** (hoy 0.81, igual que Chalice), pero sin frenar si ya venías subiendo más rápido. Mantener el corte al soltar con un mínimo un poco mayor. Acortar el flip para que **termine cerca del ápice del doble salto (≈ 0.30–0.33 s)** y hacer el giro **por código** sobre la pose recogida. Agregar **efecto anclado en los pies + destello y sonido propio con variantes**. No mostrar disponibilidad salvo que se sumen recargas en el aire.

### Cited Findings
- Precedentes de cada decisión:
  - Reset de vy: HK [L649–667](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L649-L667), Chalice [L909–936](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs#L909-L936).
  - Razón ≈ 0.82: Chalice (**cálculo propio** de [Properties](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs#L1586-L1608)).
  - Variable: Chalice ([L847–900](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs#L847-L900)) y HK ([wiki](https://hollowknight.wiki/w/Monarch_Wings)).
  - Vuelta a los frames por fase: HK ([HeroAnimationController](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroAnimationController.cs)).
  - Efecto en el punto de disparo, rotado según el stick: Chalice ([L254–267](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerAnimationController.cs#L254-L267)).
  - Destello blanco: Dread ([Wikitroid](https://metroid.fandom.com/wiki/Space_Jump), vía resumen) y pelo de Celeste a 0.12 s ([L1123–1159](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1123-L1159)).
  - Sonido propio con variantes: Chalice ([AudioClip](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/AudioClip/sfx_DLC_Chalice_DoubleJump_01.wav.meta)) y HK `doubleJumpClip` ([L2943](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L2937-L2949)).
  - Indicador de disponibilidad: Celeste ([celeste.ink](https://celeste.ink/wiki/Dashing)).
  - Buffer: HK, 10 pasos ([L4610](https://github.com/windplusflower/hk-api-skill/blob/HEAD/hkapi/HeroController.cs#L4610)); Chalice, 0.134 s durante el dash ([L816–843](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs#L816-L843)).
- **Cálculo propio** con g_subida = 2963 px/s², H = 128 px y primer salto 192.1 px en 0.360 s (21.6 f):

  | vy del doble salto | Altura extra | En H | t al ápice | Razón vs 1.er salto |
  |---|---|---|---|---|
  | −928 (0.87·v0, como Chalice) | 145 px | 1.14 H | 0.313 s (18.8 f) | 0.76 |
  | **−960 (actual)** | **156 px** | **1.21 H** | **0.324 s (19.4 f)** | **0.81** |
  | −1012 (v0·√0.9) | 173 px | 1.35 H | 0.342 s (20.5 f) | 0.90 |
  | −1067 (= v0, como Shovel Knight) | 192 px | 1.50 H | 0.360 s (21.6 f) | 1.00 |

  Topes del corte al soltar: 480 px/s → 39 px (0.30 H); 550 → 51 px (0.40 H); 600 → 61 px (0.47 H). El toque mínimo de Chalice da 0.38–0.47 H.
- El flip actual (0.42 s) dura **≈ 0.10 s (≈ 6 f) más** que la subida del doble salto (0.324 s). La voltereta invade la caída (**cálculo propio**).

### Inferences
1. **Altura:** dejar **vy = −960** (0.81, igual que Chalice). Probar −1012 (0.90) si los niveles piden alcance; ir a −1067 (1.0) solo si querés la regla de Shovel Knight, "segundo salto = salto completo".
2. **Reset sin freno:** usar `vy = min(vy, −960)` en coordenadas con y hacia abajo. Si se presiona apenas después del primer salto, cuando vy ≈ −1000 o más, no lo frena. Chalice sí frena un poco en ese caso. Es inferencia de diseño.
3. **Corte al soltar:** mantenerlo, como hacen Chalice y HK. Subir el tope solo para el doble salto a **≈ 550–600 px/s**, para que un toque rinda 0.40–0.47 H como en Chalice; hoy da 0.30 H. Alternativa estilo HK: garantizar un tramo mínimo (por ejemplo 0.08–0.10 s sin corte) y cortar solo después.
4. **Flip:**
   - Duración ≈ **0.30–0.33 s** (18–20 f), para que termine en el ápice del doble salto. Después, devolver a los frames de ápice/caída por vy, como hace HK.
   - Los 3 dibujos de Seedance a 0.42 s quedan en ≈ 7 fps efectivos. Mejor usar 1–2 poses recogidas (tuck) y **rotarlas 360° por código** alrededor del centro del cuerpo, a 60 Hz o en pasos de 45° (8 pasos en 0.30 s ≈ 27 fps, equivalente a la bola de Chalice de 8 dibujos a 30 fps).
   - Con ease-out (rápido al principio) se lee mejor el impulso.
   - Si el sprite de 12 fps no aguanta rotación libre por el pixel art, usar 4 pasos de 90° más un smear.
5. **Disparo:** con un flip de 0.30 s, bloquear el disparo es tolerable. Mejor: guardar en buffer el disparo durante el flip y soltarlo al primer frame post-flip. Cuphead dispara en su bola sin pose de puntería, así que permitir disparar desde el centro del cuerpo durante el giro también tiene precedente en el género.
6. **Efecto visual:**
   - Puff o anillo de aire/energía **anclado en los pies en el punto de disparo**, en espacio de mundo (no sigue al personaje). Duración 0.3–0.5 s.
   - Rotado ±30–35° contra el input horizontal, como Chalice.
   - Más un **destello blanco de 2–3 frames** en el sprite, como Dread y Celeste.
   - Opcional: 4–8 partículas tipo "plumas/chispas", como las plumas de HK. Todo por código o con un clip de 6–12 dibujos a 24 fps; no hace falta un clip nuevo del personaje.
7. **Sonido:** un one-shot **distinto del primer salto** (un "fwump" más aéreo o mecánico, como un jet de bota para un ranger), con **2–3 variantes al azar** como Chalice.
8. **Disponibilidad:** si el doble salto solo se recarga al aterrizar, no hace falta mostrarlo. HK y Chalice no lo muestran; HK solo muestra las alas al usarlo. Si se agregan recargas en el aire (pisar enemigos, rebotes, pickups), ahí sí conviene un indicador en el cuerpo estilo Celeste (glow o tinte en botas/mochila, más un destello y un sonido al recargar).
9. **Horizontal:** no tocar vx, como HK y Chalice. Permitir que el giro de facing ocurra en el frame del doble salto según el stick. El control aéreo del prototipo ya lo permite.
10. **Buffer y bordes:**
    - Si se aprieta salto cuando el doble salto no está permitido (por ejemplo, en recoil), guardarlo ≈ 0.13–0.17 s como HK y Chalice.
    - El salto de coyote debe tener prioridad sobre el doble salto, como en HK.
    - Si toca piso durante el flip, cortar el flip y aterrizar normal. HK convierte ese caso en un salto de piso, cosa que no hace falta copiar.

### Gaps
- Nada de esto está probado en el juego. Las cifras de altura y tiempo son cálculos continuos con las gravedades del encargo, no mediciones en el canvas a 60 Hz.
- Para fijar la razón óptima (0.81 contra 0.9 o 1.0) hace falta saber qué alturas de plataforma y esquives va a usar el diseño de niveles.
