# Fogonazos e impactos: Broforce, Enter the Gungeon y teoría general

Notas para decidir cómo dibujar el fogonazo (muzzle flash) y los impactos (hit sparks) del blaster cian del ranger: (a) partículas/formas por código, (b) sprites animados dibujados con IA, (c) mezcla. Esta parte cubre **Broforce** (Free Lives, 2015), **Enter the Gungeon** (Dodge Roll, 2016) y la **teoría general**. Metal Slug, Hard Corps, Cuphead y Blazing Chrome los cubren otras notas.

**Convención de marcas.** **medición propia** = medido sobre video o rip; **conteo propio** = frames contados a mano; **cálculo propio** = aritmética nuestra; **s/d** = sin dato. Todo lo demás lleva link. **H** = altura del personaje en pantalla (de la cabeza a los pies, sin el arma).

**Fuentes y qué tan confiables son.**
- **Broforce, código:** [alexneargarder/Broforce-Docs](https://github.com/alexneargarder/Broforce-Docs) es **documentación generada por IA** a partir del código del juego. El README dice que fue "generated automatically by having an AI analyze the game's code" y pide no confiar del todo. La cruzo con código real de mods que llama a esas mismas funciones ([BroforceMods](https://github.com/alexneargarder/BroforceMods), [Bro-Maker](https://github.com/Gorzontrok/Bro-Maker)), que compila contra el juego. Cuando el mod confirma la firma o el uso, lo digo.
- **Gungeon, código:** no hay decompilado público ni documentación oficial del sistema de VFX. Uso el código de mods que compila contra `Assembly-CSharp` del juego: [Alexandria](https://github.com/Nevernamed22/Alexandria) (la API de modding actual), [GungeonCraft](https://github.com/pcrain/GungeonCraft), [Once More Into the Breach](https://github.com/Nevernamed22/OnceMoreIntoTheBreach) y [ExpandTheGungeon](https://github.com/ApacheThunder/ExpandTheGungeon). Los **nombres de campos** son del juego (si no, no compilan). Los **valores por defecto vanilla** no se ven ahí.
- **The Spriters Resource (copia de Wayback):** no tiene hojas de efectos de ninguno de los dos.
  - Broforce: sólo personajes y "Miscellaneous" ([índice, Wayback 2023](https://web.archive.org/web/2023/https://www.spriters-resource.com/pc_computer/broforce/)).
  - Gungeon: personajes, familiares, algunos enemigos y jefes, e ítems estáticos; ni fogonazos ni impactos ([índice, Wayback 2023](https://web.archive.org/web/2023/https://www.spriters-resource.com/pc_computer/enterthegungeon/); el listado CDX de 2025 muestra las mismas fichas).
  - Existe un rip completo de atlas de Gungeon en GitHub ([r2d2m/Enter-The-Gungeon-Assets](https://github.com/r2d2m/Enter-The-Gungeon-Assets)). No lo usé: son atlas sin nombres ni datos de animación, así que no sirve para contar frames ni fps.
- **Video:** las duraciones salen de gameplay de YouTube a 60 fps, que bajé con `yt-dlp` y recorrí cuadro a cuadro con `ffmpeg`. Un "frame" es 1/60 s **de la grabación**. Si el juego corre a otra tasa, la medición queda cuantizada a 16,7 ms. La compresión ensucia los bordes, así que los tamaños tienen ±10 % (medición propia).
  - Las tiras ampliadas quedaron en `refs/broforce/` y `refs/gungeon/` (gitignored).
  - Los timestamps son aproximados (±1 s), porque `--download-sections` corta en keyframe.

---

## Resumen

| | Broforce (Rambro) | Enter the Gungeon (Marine Sidearm) |
|---|---|---|
| **Fogonazo: duración** | 10 disparos/s. Por disparo: **3 frames** de disco blanco-amarillo + **2** de amarillo más chico + 1 sin nada (medición propia, período de 6 frames a 60 Hz) | **10 frames ≈ 0,167 s**: **3 frames** de cono blanco-amarillo, 4 de estallido amarillo-naranja y 3 de brasas sueltas (medición propia, 2 disparos) |
| **Fogonazo: dibujos** | 2 capas: (1) **dibujado dentro del sprite del arma** (frames 1–3 de la hoja del arma, conteo propio) y (2) un **puff animado aparte**, `muzzleFlashPrefab`, más un "glow" de distorsión ([docs IA](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/EffectsController-Documentation.xml)) | Animación tk2d dentro de un `VFXPool` por arma (`Gun.muzzleFlashEffects`). Cantidad de dibujos vanilla: s/d. Por el ritmo 3-2-2-3 parecen ≈ 4 dibujos a ≈ 24 fps (inferencia) |
| **Fogonazo: tamaño** | ≈ 55×42 px a 1080p con H ≈ 75 px, o sea **≈ 0,73 H × 0,56 H** ≈ 14×11 px de arte. El flash dibujado en el arma es de **6×5 px de arte ≈ 0,3 H** (medición propia) | Cono de ≈ 40–48 × 27 px a 720p con H ≈ 52 px, o sea **≈ 0,75–0,9 H de largo × 0,5 H de alto**, ≈ 1,6–1,9× el largo del arma (medición propia) |
| **Variación por disparo** | El puff se orienta con la velocidad de la bala, que trae dispersión aleatoria en Y (código de mods). No vi escala al azar | Se orienta al ángulo de apuntado. En 2 disparos no vi variantes (muestra chica) |
| **Anclaje** | Se crea en el punto de salida de la bala y se **emparenta al transform del bro** (lo sigue). El glow queda fijo en el mundo ([docs IA](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/EffectsController-Documentation.xml) + [código de mods](https://github.com/alexneargarder/BroforceMods/blob/master/Mission%20Impossibro/Mission%20Impossibro/MissionImpossibro.cs)) | Transform `barrelOffset` hijo del arma, con `VFXObject.attached` y `orphaned` para decidir si sigue al arma o queda en el mundo ([Alexandria](https://github.com/Nevernamed22/Alexandria/blob/main/VisualAPI/VFXBuilder.cs)) |
| **Blending** | s/d directo. El "glow" es un efecto de **distorsión** (heat haze), no una capa aditiva ([docs IA](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/EffectsController-Documentation.xml)). En video se ve pixel art opaco (inferencia) | Sprites **cutout** (alpha test) con parámetro **emisivo** que alimenta el bloom, más una luz puntual opcional. Lo deduzco de los shaders que usan los mods (`Brave/…TiltedCutoutEmissive`). No es aditivo (inferencia) |
| **Impacto en pared** | "Pop": **2 frames de disco blanco sólido** (≈ 0,7 H), después **3–4 frames amarillos** (anillo grueso o disco) con un anillo fino que se expande hasta ≈ 0,9 H. Total ≈ 6 frames ≈ 0,1 s (medición propia). Más chispas: cuadraditos de 1 px de arte con gravedad y rebote ([docs IA](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/Shrapnel-Documentation.xml)) | VFX separados para pared horizontal, pared vertical, enemigo, muerte de la bala en el aire, etc. ([campos de `ProjectileImpactVFXPool`](https://github.com/pcrain/GungeonCraft/blob/master/src/Extensions.cs)). Duración en pared: s/d |
| **Impacto en enemigo** | Sangre y gibs (fuera de alcance acá) | **1 frame de silueta blanca sólida + 1 frame ≈ 50 % blanco**. Medición propia: 3 golpes en el jefe y 1 en un Bullet Kin. Es un flag de código (`HealthHaver.flashesOnDamage`), no un dibujo |
| **Partículas por código** | Chispas (`sparkCount` 10 por defecto; ducha de 12 a 250+ u/s), color por "temperatura" de amarillo a rojo, esquirlas, humo, casquillos ([docs IA](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/Projectile-Documentation.xml)) | Casquillos y cargadores eyectados, screenshake por arma ([campos usados por mods](https://github.com/pcrain/GungeonCraft/blob/master/src/Extensions.cs)) |

**En una línea:** los dos son **(c) mezcla**. El núcleo del fogonazo y del impacto es **una animación dibujada corta** (flipbook de pocos frames). La variedad y la física vienen **de código**: orientación, chispas con gravedad, casquillos, glow o luz, y el flash blanco del enemigo.

---

## A. Broforce

### A.1 Fogonazo

**Dos capas superpuestas.**

1. **Flash dibujado en la hoja del arma.**
   - Conteo propio sobre [`rambroGun.png`](https://github.com/Gorzontrok/Bro-Maker/tree/main/images/Example%20Spritesheets) (hoja de ejemplo de BroMaker, celdas de 32×32; copia en `refs/broforce/rambroGun_fila0_x8.png`). La fila 0 tiene 4 celdas: celda 0 = arma en reposo (16×8 px) y celdas 1–3 = arma con retroceso **más un fogonazo dibujado**: un núcleo blanco-amarillo y una nubecita de humo gris.
   - La celda 3 es la más grande: bbox de 22×9 px (arma más flash) y ≈ **6×5 px** sólo el flash. Tiene 32 píxeles "claros" (luminancia > 180), contra 19–22 en las celdas 1–2 (medición propia).
   - BroMaker documenta que el 4.º frame del arma "is displayed first when the fire button is pressed, then it animates backwards towards the first frame" ([BroMaker wiki, Spritesheets](https://github.com/Gorzontrok/Bro-Maker/wiki/Spritesheets)).
   - El contador del arma avanza cada 0,0334 s y `gunFrame` se pone en 3 al disparar ([docs IA, TestVanDammeAnim](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/TestVanDammeAnim-Documentation.xml)). Entonces el flash dibujado dura **frames de arma 3 → 2 → 1 ≈ 0,1 s** (cálculo propio: 3 × 0,0334).
   - Cada frame del arma tiene **un dibujo distinto** de flash y humo, no es un solo dibujo que se apaga. El frame 3 es el más grande.
2. **Puff aparte, `EffectsController`.**
   - `CreateMuzzleFlashEffect(x, y, z, xI, yI, parent)` "Instantiates both the main flash animation oriented by velocity and a separate glow effect. The main flash is parented to the provided transform" ([docs IA, EffectsController](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/EffectsController-Documentation.xml)).
   - El base `TestVanDammeAnim.FireWeapon` "Sets gun animation frame, creates muzzle flash, spawns projectile" ([docs IA](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/TestVanDammeAnim-Documentation.xml)).
   - **Catálogo de variantes por tipo de arma** (docs IA, mismo archivo):

     | Variante | Uso | Comportamiento |
     |---|---|---|
     | `muzzleFlashPrefab` | "small firearms" | Se emparenta al bro |
     | `Medium` | Armas más grandes | Se emparenta al bro |
     | `Big` | Armas pesadas | "not parented… remains stationary", con `BigGlow` |
     | `Round` | — | Se emparenta al bro |
     | `RoundBlue` | "energy weapons" | Variante azul del redondo |
     | `TankCannon` | Cañón de tanque | Se espeja con el signo de `xI`, con `HugeGlow` |
     | `Vomit` | Ácido o bilis | Sin glow |
     | `TimeBro` | Bro del tiempo | Ignora el timescale (se ve en cámara lenta) |

   - Los glows (`muzzleFlashSmallGlowPrefab`, `GlowPrefab`, `BigGlow`, `HugeGlow`) se describen como "distortion glow effect… heat distortion visual".
   - **El tamaño del fogonazo va por categoría de arma, no por arma.** Hay 4 tamaños de glow y una variante azul para energía.

**Medición en video** ([Broforce, "Rambro's Covert Operation", 1080p60](https://www.youtube.com/watch?v=c4eSis4wXKc&t=61s), ≈ 1:01–1:02; tiras en `refs/broforce/bf_rambro_fogonazo_*.png`):
- **Período de disparo:** 6 frames → **10 disparos/s**, medido sobre 12 ciclos (medición propia). Coincide con el `fireRate` 0,1 del [template comunitario de Rambro](https://github.com/alexneargarder/Broforce-Templates/blob/master/Bro%20Template/Bro%20Template/_ModContent/Bro%20Template.json), no con el 0,0334 del default base.
- **Ciclo por disparo** (conteo propio, cuenta de píxeles blancos con min(RGB) > 225 en la zona del cañón):

  | Frames | Qué se ve | Píxeles |
  |---|---|---|
  | 3 | Disco blanco con borde amarillo grande | 600–950 blancos |
  | 2 | Elipse amarilla más chica | ≈ 150 blancos, 500 amarillos |
  | 1 | Nada | 0 |

  En fuego continuo el cañón casi nunca queda "apagado": 5 de cada 6 frames tienen flash.
- **Tamaño del disco:** ≈ 55×42 px a 1080p.
  - Rambro mide H ≈ 75 px en ese video, del pelo a los pies (medición propia). Son 19 px de arte según la [nota previa](../Movimiento%20y%20disparo%20en%20run-and-guns/cuphead_broforce.md), así que ≈ 3,9 px de pantalla por px de arte.
  - El flash queda en **≈ 0,73 H × 0,56 H ≈ 14×11 px de arte**, más del doble del flash dibujado en el arma (cálculo propio).
  - Inferencia: el disco grande es el puff de `EffectsController` y el chiquito es el del arma.

**Variación por disparo.** En el código de mods, el puff recibe la velocidad de la bala escalada: `CreateMuzzleFlashEffect(x, y, -25f, xSpeed * 0.15f, ySpeed * 0.15f, base.transform)` ([MissionImpossibro.cs, l. 654](https://github.com/alexneargarder/BroforceMods/blob/master/Mission%20Impossibro/Mission%20Impossibro/MissionImpossibro.cs)).
- La bala base sale con `ySpeed = Random.Range(0, 40) - 20` contra `xSpeed = 400`. Ese es el `UseFire` que copia BroMaker en [SwordHero.cs](https://github.com/Gorzontrok/Bro-Maker/blob/main/BroMakerLib/CustomObjects/Bros/SwordHero.cs), réplica del base (inferencia).
- Entonces el fogonazo **rota ±≈ 3°** con la dispersión de la bala (cálculo propio: atan(20/400)).
- El lanzallamas de un mod, que imita el patrón vanilla, usa `Random.value * 60f - 30f` en Y contra 60 en X: **±≈ 27°** al azar por flash, y re-emite el flash cada 0,1 s mientras dispara ([RJBrocready.cs, l. 439](https://github.com/alexneargarder/BroforceMods/blob/master/RJBrocready/RJBrocready/RJBrocready.cs)).
- No encontré escala ni flip al azar (s/d).

### A.2 Anclaje

- **Posición:** el puff se crea en el **mismo (x, y) donde nace la bala**, a z = −25 (delante de todo). Los mods usan offsets fijos desde el pivote del bro, por ejemplo `X + localScale.x * 14, Y + 13.5` ([CaptainAmeribro.cs, l. 664](https://github.com/alexneargarder/BroforceMods/blob/master/Captain%20Ameribro/Captain%20Ameribro/CaptainAmeribro.cs)) o `X + localScale.x * 10, Y + 6.5` ([SwordHero.cs](https://github.com/Gorzontrok/Bro-Maker/blob/main/BroMakerLib/CustomObjects/Bros/SwordHero.cs)). `localScale.x` es ±1 y hace de flip.
- **Seguimiento:** el flash se **emparenta** al transform del bro, así que si el bro se mueve en esos frames el flash va con él. El glow **no**: queda en el mundo ([docs IA](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/EffectsController-Documentation.xml); un mod reimplementa la versión Big con `CreateEffect(muzzleFlashBigPrefab, …, parent)` y `CreateEffect(muzzleFlashBigGlowPrefab, …)` sin parent, en [WarRig.cs, l. 3814](https://github.com/alexneargarder/BroforceMods/blob/master/Furibrosa/Furibrosa/WarRig.cs)).
- **El arma:** es una capa aparte con su propio contador ([BroMaker wiki](https://github.com/Gorzontrok/Bro-Maker/wiki/Spritesheets)). El flash dibujado dentro del arma viaja con ella por construcción.

### A.3 Blending

- s/d en fuentes. Lo único documentado es que el "glow" es **distorsión** (refracción tipo calor) y no luz sumada ([docs IA](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/EffectsController-Documentation.xml)).
- Hay materiales distintos para balas amigas y enemigas (`friendlyMaterial` y `enemyMaterial`, "for visual team identification") ([docs IA, Projectile](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/Projectile-Documentation.xml)).
- Inferencia del video: el disco del flash se ve **opaco** (blanco plano con borde amarillo duro), sin halo sumado. Es pixel art con alfa normal.

### A.4 Impactos

**Qué dispara el código** ([docs IA, Projectile](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/Projectile-Documentation.xml)):
- `MakeEffects(particles, x, y, useRayCast, hitNormal, hitPoint)` "Generates sparks with physics-based trajectories, optional puff effects, and plays impact sounds". Si hay raycast, usa la **normal de la superficie** para orientar.
- `sparkCount` = **10** por defecto ("Different impact contexts use full count or reduced counts").
- `MakeSparkShower` = **12 chispas** a "250+ units".
- `whitePopEffect`: elige entre el pop blanco y el normal.

**Familias de efectos de impacto** ([docs IA, EffectsController](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/EffectsController-Documentation.xml)):
- `CreateProjectilePopEffect`: pop animado (`projectileFlickPuff`) más "glowing flash".
- `CreateProjectilePuff`: puff más "small muzzle flash glow". Reusa el glow del fogonazo en el impacto.
- `bulletPoofPrefab`: "small dust cloud when bullets hit surfaces".
- `projectileLargeFlickPuff` para armas pesadas, y `whitePunchPopPrefab` y `whiteFlashPop(Small)Prefab`.

**Chispas por código:**
- `CreateSparkParticles(…, redM, lifeM)` colorea por "temperatura": "Color interpolates from yellow (1,1,0.3) to red (1,0,0) based on the redM parameter".
- Hay tres emisores: `sparkParticleShower` (cae), `sparkParticleFloat` (flota) y `sparkParticleFire`. `CreateSparkShower` mezcla los dos primeros con `particlesFloatM` ([docs IA](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/EffectsController-Documentation.xml)).

**Esquirlas y casquillos (`Shrapnel`)** ([docs IA, Shrapnel](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/Shrapnel-Documentation.xml)):
- Son sprites con física propia: gravedad 500 u/s² × `gravityM`, rebote `bounceM` 0,4, vida con variación aleatoria × `lifeM`, rotación según la velocidad horizontal, y opciones de achicarse (`shrink`) y desvanecerse (`fades`).
- El casquillo de Rambro (`bulletShell`) es un Shrapnel que "fly backward relative to Rambro's facing direction" ([docs IA, Rambro](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/Rambro-Documentation.xml)).
- Ejemplo de chispa direccional sobre una pared, en BroMaker: `CreateShrapnel(shrapnelSpark, hit.point + normal*3, 4f, 30f, 3f, normal.x*60f, normal.y*30f)`. Las chispas salen **a lo largo de la normal** ([SwordHero.cs](https://github.com/Gorzontrok/Bro-Maker/blob/main/BroMakerLib/CustomObjects/Bros/SwordHero.cs)).

**Medición en video del impacto en pared** (mismo video ≈ 1:01; tira en `refs/broforce/bf_rambro_impacto_pared_*.png`; medición propia):

| Fase | Frames | Qué se ve | Tamaño |
|---|---|---|---|
| 1 | **2** | **Disco blanco sólido** | ≈ 51–55 px ≈ **0,7 H** |
| 2 | **3–4** | **Amarillo saturado**: anillo grueso, después disco, más un **anillo fino que se expande** | Diámetro máximo ≈ 63–73 px ≈ **0,85–0,95 H** |
| Total | **≈ 6 frames ≈ 0,1 s** | Como entra una bala cada 6 frames, los pops se encadenan sin hueco | — |

- Además quedan **cuadraditos amarillos de 1 px de arte** (≈ 4 px de pantalla) que caen y se quedan unos frames en el piso: son las chispas.
- Lectura: el blanco sólido de 2 frames "marca" el punto de contacto y el amarillo que se abre "enfría" el golpe.

### A.5 Citas de Free Lives

- **s/d:** no encontré ninguna declaración de Free Lives sobre cómo diseñaron fogonazos o chispas. Las entrevistas encontradas hablan del origen y de las películas de acción ([GamingBolt, 2015](https://gamingbolt.com/broforce-interview-developing-a-badass-action-hero-style-video-game); vista sólo por el resumen del buscador).
- Lo más cercano es la descripción de BroMaker de la capa del arma: "each has its own frame rate and frame counter… use your weapon and have the animation for it play independently" ([BroMaker wiki](https://github.com/Gorzontrok/Bro-Maker/wiki/Spritesheets)). Es de la comunidad, no de Free Lives.

---

## B. Enter the Gungeon

### B.1 Fogonazo: estructura de datos

Lo que sigue son nombres de campos del juego tal como los usa el código de mods que compila contra él (hecho). La semántica sale del uso (inferencia leve).

- **`Gun.muzzleFlashEffects`** es un **`VFXPool`**:
  - `type`: `VFXPoolType`. En los mods aparecen `None`, `All` y `Single`; los demás valores no los vi.
  - `effects`: un `VFXComplex[]`. Cada **`VFXComplex`** tiene un `VFXObject[]`.
  - Un **`VFXObject`** trae ([Alexandria, VFXBuilder.cs](https://github.com/Nevernamed22/Alexandria/blob/main/VisualAPI/VFXBuilder.cs)):
    - `effect`: un GameObject con `tk2dSprite` y `tk2dSpriteAnimator`. Es decir, **un flipbook 2D Toolkit** con un clip "start" de N frames a `fps`, en `WrapMode.Once`, que se autodestruye con `SpriteAnimatorKiller`.
    - `attached`: si se emparenta al cañón.
    - `orphaned`: si queda suelto en el mundo.
    - `persistsOnDeath`.
    - `usesZHeight` y `zHeight`.
    - `alignment`: `Fixed`, `NormalAligned` o `VelocityAligned`.
    - `destructible`.
- **Otros campos del arma relacionados con el feedback del disparo** (conteo de uso en los 4 repos de mods, con `grep`):

  | Campo | Para qué |
  |---|---|
  | `finalMuzzleFlashEffects` | Fogonazo del último tiro del cargador |
  | `CriticalMuzzleFlashEffects` | Fogonazo del tiro crítico |
  | `usesContinuousMuzzleFlash` | Armas de chorro |
  | `shellCasing`, `shellsToLaunchOnFire`, `shellCasingOnFireFrameDelay` | Casquillo eyectado con retardo en frames |
  | `clipObject`, `clipsToLaunchOnReload`, `reloadClipLaunchFrame` | Cargador que cae al recargar |
  | `doesScreenShake` / `gunScreenShake`, `directionlessScreenShake` | Screenshake por arma |

  Ejemplos de uso en [GungeonCraft, Extensions.cs](https://github.com/pcrain/GungeonCraft/blob/master/src/Extensions.cs) y [OMITB, CortexBlaster.cs](https://github.com/Nevernamed22/OnceMoreIntoTheBreach/blob/master/MakingAnItem/Content/Items/Guns/CortexBlaster.cs).
- **Enemigos:** las balas de enemigos llevan su propio fogonazo en `AIBulletBank.Entry.MuzzleFlashEffects`, con `MuzzleLimitOncePerFrame` y `MuzzleInheritsTransformDirection` ([Alexandria, EnemyBuilder.cs](https://github.com/Nevernamed22/Alexandria/blob/main/EnemyAPI/EnemyBuilder.cs)). Por el nombre, `MuzzleLimitOncePerFrame` evitaría apilar N fogonazos cuando un patrón dispara muchas balas en el mismo frame (inferencia). Es un detalle útil para la ráfaga del blaster.
- **Fogonazos vanilla "más comunes":** s/d como dato vanilla. Como proxy, los fogonazos vanilla que más reusan los mods (`muzzleFlashEffects = (GetById(n) as Gun).muzzleFlashEffects`, conteo propio con `grep`) son:
  - Polaris (97): 9 veces.
  - Heroine (41), Wind-Up Gun (334) y Dungeon Eagle (23): 8 cada uno.
  - Rogue Special (89): 7.
  - Magnum (38), Serious Cannon (37), Tear Jerker (33), Particulator (228) y Crossbow (12): 5 cada uno.

  Aparte, GungeonCraft usa el de Mailbox (28) 25 veces como default (`muzzleFrom: Items.Mailbox`). Los nombres de los IDs salen de la tabla `Items` en [GungeonCraft, Databases.cs](https://github.com/pcrain/GungeonCraft/blob/master/src/Databases.cs). Esto mide la popularidad entre modders, no la frecuencia en el juego.

### B.2 Fogonazo: medición

**Video:** [ETG – Marine Sidearm Only Run, 720p60](https://www.youtube.com/watch?v=XKjPjhZgqW4&t=217s), ≈ 3:37, pelea con Bullet King. Tiras en `refs/gungeon/etg_marine_sidearm_fogonazo_*.png`. Medición propia, 2 disparos (frames 44–53 y 77–86 del recorte), con cuenta de píxeles blancos, amarillos y naranjas por frame:

| Fase | Frames a 60 Hz | Qué se ve |
|---|---|---|
| 1, "calor blanco" | **3** | **Cono** blanco con borde amarillo, abierto hacia adelante y orientado al ángulo de apuntado. 87–196 px blancos y 400–520 amarillos. En el 3.º frame ya asoma la bala (círculo blanco) |
| 2 | **4** (2 + 2) | **Estallido radial** amarillo-naranja, más chico y "roto". 0 px blancos, ≈ 90–145 amarillos |
| 3 | **3** | **Brasas naranjas sueltas** (pixeles aislados) que se abren en abanico |
| Total | **10 frames ≈ 0,167 s** | Fase caliente: **0,05 s** |

- El ritmo 3/2/2/3 sugiere ≈ 4 dibujos a ≈ 24 fps (inferencia).
- **Tamaño** (medición propia sobre el frame 78):
  - Marine: H ≈ 52 px, de y 132 a 184.
  - Arma: ≈ 25 px (≈ 0,48 H).
  - Cono: ≈ 40–48 px de largo × ≈ 27 px de alto, o sea **≈ 0,75–0,9 H de largo y ≈ 0,5 H de alto, ≈ 1,6–1,9× el arma**.
  - Alrededor del cono se ve un **halo pálido** suave: el bloom del emisivo (inferencia).
- **Variación:** los dos disparos muestran el mismo dibujo, sólo rotado con el apuntado (muestra chica: no descarta variantes).
- **Fogonazo de enemigo (Bullet King, mismo video, ≈ 3:37):** media luna amarilla (3 frames), después anillo naranja (4), después rojo que se apaga (3). Total **10 frames**, con la misma curva **blanco/amarillo → naranja → rojo**. Tira en `refs/gungeon/etg_bulletking_fogonazo_enemigo_*.png`.
- **Fogonazos de mods con estilo Gungeon** (referencia de estilo, **no vanilla**). En [GungeonCraft](https://github.com/pcrain/GungeonCraft/tree/master/RawResources/MuzzleVFX) hay 22 fogonazos de armas. El fps sale del código del arma, que usa 60 por defecto cuando no lo declara. Conteo propio de PNGs por fogonazo y cálculo propio de frames/fps:
  - **3–8 frames, mediana 4–5**, a **20–120 fps**, casi siempre 30 o 60.
  - Duración de **0,067–0,27 s, mediana ≈ 0,13 s**.
  - Ejemplo: `muzzle_sub_machine_gun` = 5 frames a 30 fps, escala 0,5 ([SubMachineGun.cs](https://github.com/pcrain/GungeonCraft/blob/master/src/Cwaff-Guns/SubMachineGun.cs)).

### B.3 Anclaje

- **`Gun.barrelOffset`** es un `Transform` hijo del arma. Los mods lo mueven con `barrelOffset.localPosition`, en unidades de mundo de 16 px de arte por unidad. Por ejemplo `pistol.barrelOffset.localPosition -= new Vector3(0.3f, 0.2f, 0)` ([ExpandTheGungeon, BootlegGuns.cs](https://github.com/ApacheThunder/ExpandTheGungeon/blob/BepInEx/ExpandTheGungeon/ItemAPI/Items/BootlegGuns.cs)).
- **Cómo se dispara un fogonazo a mano:** `muzzleFlashEffects.SpawnAtPosition(gun.barrelOffset.position, gun.CurrentAngle, …)`. Posición = boca del cañón, rotación = ángulo del arma ([OMITB, UnderbarrelShotgun.cs, l. 54](https://github.com/Nevernamed22/OnceMoreIntoTheBreach/blob/master/MakingAnItem/Content/Items/Misc%20Passives/UnderbarrelShotgun.cs)).
- El constructor de Alexandria marca `attached = true`, o sea que **el fogonazo sigue al cañón** mientras dura ([VFXBuilder.cs](https://github.com/Nevernamed22/Alexandria/blob/main/VisualAPI/VFXBuilder.cs)).
- GungeonCraft usa por defecto `alignment: Fixed`, `attached: true` y `orphaned: false` para fogonazos ([Extensions.cs, `SetMuzzleVFX`](https://github.com/pcrain/GungeonCraft/blob/master/src/Extensions.cs)).
- **Anclaje por frame de animación:** el `barrelOffset` vanilla es **fijo por arma** (inferencia). GungeonCraft tuvo que agregar "dynamic barrel offsets" leyendo el **attach point "Casing"** que cada frame del sprite del arma trae en tk2d ([GungeonCraft, `GetBarrelOffsetsForAnimation`](https://github.com/pcrain/GungeonCraft/blob/master/src/Extensions.cs)).
  - O sea: el sprite del arma tiene puntos de anclaje por frame (al menos para el casquillo).
  - Para el ranger, con anim de cuerpo entero, esto equivale a tener **un punto de boca por frame** (ver C.6).

### B.4 Blending

- Lo que sigue sale de los shaders que asignan los mods; **inferencia sobre vanilla**.
  - Los VFX de modders usan `Brave/LitTk2dCustomFalloffTintableTiltedCutoutEmissive`, `Brave/LitTk2dCustomFalloffTiltedCutoutEmissive` y, para no iluminados, `Brave/UnlitTintableCutoutColorEmissive` o `tk2d/CutoutVertexColorTilted` ([Alexandria, VFXBuilder.cs](https://github.com/Nevernamed22/Alexandria/blob/main/VisualAPI/VFXBuilder.cs); [GungeonCraft, VFXToolbox.cs](https://github.com/pcrain/GungeonCraft/blob/master/src/VFXToolbox.cs)).
  - Los parámetros son `_EmissivePower`, `_EmissiveColorPower` y `_EmissiveColor`.
  - Opcionalmente se agrega una **`Light` puntual** hija del VFX (`lightStrength`, `lightRange`).
- Conclusión probable: **pixel art "cutout"**, es decir alpha test, píxel lleno o vacío, sin semitransparencias. El "brillo" sale de **emisión + bloom + luz dinámica**, no de blending aditivo del sprite.
- Existe un shader interno aditivo (`Brave/Internal/GlitterPassAdditive`), pero se usa para efectos especiales, no para fogonazos (sólo lo vi en ese contexto).
- Esto cuadra con el video: los bordes del cono son duros y alrededor hay un halo suave aparte.

### B.5 Impactos

**Estructura.** `Projectile.hitEffects` es un `ProjectileImpactVFXPool` con VFX **separados por superficie y caso**:
- `tileMapHorizontal` y `tileMapVertical`: paredes horizontales y verticales, cada una su `VFXPool`.
- `enemy`: pegarle a un enemigo.
- `deathAny`, `deathTileMapHorizontal`, `deathTileMapVertical`, `deathEnemy`: cuando la bala muere en ese caso.
- `overrideMidairDeathVFX`: la bala se agota en el aire. Lleva `midairInheritsRotation`, `midairInheritsVelocity`, `midairInheritsFlip` y `alwaysUseMidair`.
- `CenterDeathVFXOnProjectile`.
- `suppressHitEffectsIfOffscreen`.

Fuente: copia campo por campo en [GungeonCraft, Extensions.cs](https://github.com/pcrain/GungeonCraft/blob/master/src/Extensions.cs); el uso más común en mods es `overrideMidairDeathVFX` (191 apariciones, conteo propio).

- **Direccionalidad:** como hay VFX distintos para pared horizontal y vertical, más `alignment = NormalAligned` (el default del constructor de Alexandria), **el impacto se orienta a la normal de la pared** (inferencia razonable).
- **Duración del impacto en pared:** s/d. No conseguí un impacto limpio en pared en los videos.

**Flash del enemigo (medición propia):**
- Videos: [Marine Sidearm Only Run](https://www.youtube.com/watch?v=XKjPjhZgqW4&t=216s), golpes al Bullet King a ≈ 3:36–3:37, y [mismo run](https://www.youtube.com/watch?v=XKjPjhZgqW4&t=91s), Bullet Kin a ≈ 1:31. Tira en `refs/gungeon/etg_bulletking_hitflash_*.png`.
- **1 frame de silueta blanca sólida** (en el jefe: 18.273 px blancos contra ≈ 1.400 de base), **1 frame ≈ 50 % blanco** y vuelta a lo normal. Se repitió igual en 4 golpes.
- Es una propiedad del componente de vida, `HealthHaver.flashesOnDamage` ([ExpandTheGungeon, ExpandUtility.cs](https://github.com/ApacheThunder/ExpandTheGungeon/blob/BepInEx/ExpandTheGungeon/ExpandUtilities/ExpandUtility.cs)). Es **código, no un dibujo por enemigo**.
- El "spark" de la bala en el enemigo es muy chico (un destello amarillo de 1–2 frames). El peso del feedback lo lleva el flash blanco.
- **Permanencia:** en el mismo video, ≈ 1:31, los cadáveres de Bullet Kin quedan tirados en el piso de la sala (observación). Es la "permanencia" de Vlambeer (ver C.1).
- **Casquillos en el video:** no los pude distinguir a esa resolución (s/d visual). Que existen como objeto eyectado sale de los campos `shellCasing` y `shellsToLaunchOnFire` (B.1).

### B.6 Citas de Dodge Roll

- **s/d:** no encontré declaraciones de Dodge Roll sobre el diseño de fogonazos o impactos. Las entrevistas a Dave Crooks que aparecen tratan el origen, el contenido y la salida del juego ([Gameranx, 2016](https://gameranx.com/features/id/48447/article/enter-the-gungeon-interview-with-dodge-rolls-dave-crooks-the-past-present-and-future/); [PC Games Insider, 2019](https://www.pcgamesinsider.biz/indie-interview/68862/why-dodge-roll-has-decided-to-part-ways-with-enter-the-gungeon/)).
- Contexto de prensa, **no cita de dev**: PC Games Insider lo resume como "Binding of Isaac style dungeon crawling with Vlambeer gunplay" (frase de la periodista, Natalie Clayton).

---

## C. Teoría general (corta)

### C.1 "Juice" en disparos: la receta Vlambeer, con números

- **Charla:** Jan Willem Nijman, "The Art of Screenshake" (INDIGO Classes 2013) ([video](https://www.youtube.com/watch?v=AJdEqssNZ-U)). No pude verificar timestamps: YouTube bloqueó los subtítulos (HTTP 429) y la filmación es del escenario, con la pantalla ilegible. Por eso cito la versión escrita del mismo autor, que es más precisa.
- **Entrevista a Nijman sobre Nuclear Throne** ([Rock Paper Shotgun, 21/10/2013, copia Wayback](https://web.archive.org/web/2014/http://www.rockpapershotgun.com/2013/10/21/interview-jan-willem-nijman-on-nuclear-thrones-feel/)). Es primaria, con números del pistol, a 30 fps y 320×240:

  | Elemento | Qué dice |
  |---|---|
  | **Fogonazo de 1 frame** | "The bullet is circular the first frame, after that it's more of a bullet shape. This is a simple way to pretend we have muzzle flashes." El fogonazo es literalmente **el primer frame de la bala** |
  | **Balas grandes** | "the bullets in most of our games are about the same size as the players" |
  | **Impacto claro** | "communicate clearly (with some animated effects) when hitting something" |
  | **Golpe al enemigo** | "always starts with a frame white, then two frames of the character looking hit with big eyes" |
  | **Freeze** | "The game also freezes for about 10-20 milliseconds whenever you hit something" |
  | **Cámara y arma** | Cámara 6 px hacia atrás del apuntado, +4 al screenshake, kick del arma 2 |
  | **Casquillo** | 2–4 px/frame a 100–150° del apuntado |
  | **Bala** | 16 px/frame, con 0–4° de desvío |

- **Juice general:** Martin Jonasson y Petri Purho, "Juice it or lose it" ([GDC Europe 2012, video](https://www.youtube.com/watch?v=Fy0aCDmgnxg)). Es la referencia clásica de "agregar partículas, tweens y shake encima de una mecánica pelada". No la re-vi para esta nota.

### C.2 Por qué los fogonazos duran 1–3 frames

- **Física:** el fogonazo real dura **≈ 1–2 ms**. Algunos .30-06 llegan a ≈ 7 ms (Burke y Bratlie 2011, citado en [arXiv 1410.6025](https://arxiv.org/pdf/1410.6025)). Un solo frame a 60 Hz (16,7 ms) **ya es 8–16× más largo** que el real (cálculo propio). Cualquier fogonazo visible es una exageración. Mostrarlo 1 frame es lo más "realista", y mostrarlo más es una decisión de lectura.
- **Práctica:**
  - Vlambeer usa **1 frame**.
  - Un pack de VFX (Reactorcore, CC-BY, autor de assets; no es un juego comercial) recomienda "quickly show the muzzle flash sprite for a single frame when a weapon fires, followed by a particle system that spews yellow/orange pixels" ([OpenGameArt](https://opengameart.org/content/gun-muzzle-flash-effects-fire-and-ion-and-melee)).
  - Mis mediciones: **3 frames de núcleo** en Broforce y Gungeon, más **3–7 frames de residuo** que se enfría.
- **Por qué funciona corto** (inferencia, coherente con las fuentes):
  - El ojo registra el destello aunque dure 1 frame, porque es el elemento de mayor contraste de la pantalla.
  - Si dura mucho, **tapa la bala y al enemigo** en armas rápidas. A 10 disparos/s, un flash de 6 frames ya queda encendido todo el tiempo, como pasa en Broforce.
  - El patrón que se repite es **núcleo corto y brillante + residuo largo y apagado**.

### C.3 Primer frame blanco/sólido y rampa de "temperatura"

- **Hecho, en las fuentes y mediciones de arriba:**
  - El golpe de Nuclear Throne empieza con **un frame blanco** (RPS).
  - En Gungeon, el enemigo golpeado hace **1 frame de silueta blanca sólida + 1 al 50 %** (medición propia).
  - El impacto en pared de Broforce arranca con **2 frames de disco blanco sólido** (medición propia).
  - Los fogonazos de Gungeon, del jugador y del enemigo, siguen **blanco → amarillo → naranja → rojo o brasas** (medición propia).
  - Las chispas de Broforce interpolan **amarillo (1, 1, 0,3) → rojo (1, 0, 0)** ([docs IA](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/EffectsController-Documentation.xml)).
- **Para un blaster cian** (inferencia): la misma rampa en frío sería **blanco → cian → azul → violeta o azul oscuro**. El primer frame va **blanco puro**, no cian, porque el blanco es lo que "pega".

### C.4 Variar por disparo

- **Fuentes:**
  - Reactorcore recomienda tener **sets** y "randomly show one of them for each firing" ([OpenGameArt](https://opengameart.org/content/gun-muzzle-flash-effects-fire-and-ion-and-melee)).
  - Broforce orienta el puff con la velocidad de la bala, que trae dispersión aleatoria (±≈ 3° en la bala base, ±≈ 27° en el chorro del mod; ver A.1).
  - Nuclear Throne desvía la bala 0–4° (RPS).
  - En Gungeon no vi variantes en 2 disparos.
- **Receta barata en canvas** (inferencia): con 2–3 dibujos de núcleo alcanza si cada disparo además **rota ±10–20°** sobre el eje del cañón, **escala ×0,85–1,15** y hace **flip vertical al 50 %**, que es invisible en un cono simétrico. Así no se repite el mismo cuadro dos veces seguidas sin agregar arte.

### C.5 Blending aditivo en 2D y su problema sobre fondos claros

- **Canvas 2D:** `globalCompositeOperation = 'lighter'` = **aditivo** ("the color is determined by adding color values"). `'screen'` = invertir, multiplicar e invertir, que satura más suave. `'source-over'` = alfa normal ([MDN](https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/globalCompositeOperation)).
- **Problema:** aditivo **nunca oscurece**. Sobre negro brilla, pero sobre un fondo claro (cielo, explosión, pared iluminada) **satura a blanco y pierde la forma y el color**. Un cian sumado sobre un cielo celeste prácticamente desaparece. Es un problema conocido en foros de VFX; un ejemplo es [este hilo de Babylon.js](https://forum.babylonjs.com/t/particle-blend-modes-for-transparent-backgrounds/12076), sobre partículas que no se ven sobre fondo blanco (visto por el resumen del buscador). Lo demás es consecuencia directa de la suma de colores.
- **Salida estándar:** **alfa premultiplicado**, que permite "regions of regular alpha blending (e.g. smoke)" y "regions with additive blending mode (e.g. flame and glitter effects)" en la misma imagen ([Wikipedia, Alpha compositing](https://en.wikipedia.org/wiki/Alpha_compositing)).
- **En canvas** (inferencia): el **núcleo** se dibuja con `source-over`, opaco, con borde oscuro o saturado que lo separe del fondo. Encima va un **halo** con `lighter` o `screen` de alfa baja. Así el flash se lee sobre fondo claro y "brilla" sobre fondo oscuro.
- **Lo que hacen los dos juegos** (inferencia): Broforce y Gungeon dibujan el fogonazo **opaco** (pixel art) y ponen el brillo aparte (distorsión en Broforce; emisión, bloom y luz en Gungeon). Ninguno depende de que el sprite sea aditivo.

### C.6 Anclaje al punto de la boca

- **Spine**, "point attachments": "can be used to spawn particles or anything else that involves a position and/or rotation". Su posición no se keyea: se anima el **hueso** y el punto lo sigue ([Spine User Guide, Points](http://esotericsoftware.com/spine-points)).
- **Gungeon:** `barrelOffset` es un Transform hijo del arma, y el fogonazo `attached` sigue al cañón (B.3).
- **Broforce:** el puff se emparenta al bro y el glow queda en el mundo (A.2).
- **Cuphead** tiene una tabla fija de offsets por pose ([nota previa](../Movimiento%20y%20disparo%20en%20run-and-guns/cuphead_broforce.md)).
- **Regla común** (inferencia): lo que **es parte del arma** (núcleo del fogonazo) **sigue a la boca** mientras dura. Lo que **es del mundo** (humo, chispas, casquillos, el anillo del impacto) **se suelta** en coordenadas de mundo.
- **Para un sprite de cuerpo entero sin esqueleto** (el ranger): hace falta **un punto de boca por frame** de cada animación de disparo, incluyendo el ángulo. Es lo que GungeonCraft reconstruye con los attach points por frame (B.3).

### C.7 Hit sparks y hitstop

- **Para qué sirven:** "useful as additional feedback and establishing the point of contact". Hitstop es "when the game freezes the characters at the point of collision" y "gives the eyes a few frames to register" (Celia Wagar, [critpoints.net, 2017](https://critpoints.net/2017/05/17/hitstophitfreezehitlaghitpausehitshit/)).
- **Cuánto dura en fighting games:** en SF2 ≈ 14 frames sin importar el botón; en "most games", ≈ 9 / 11 / 13 frames para golpe débil, medio y fuerte (Maj, ["Impact Freeze", 2010](https://sonichurricane.com/?p=1043)).
- **Disparos:** un run-and-gun dispara 10 veces por segundo, así que el freeze tiene que ser mucho menor. Vlambeer usa **10–20 ms** por impacto (RPS), ≈ 1 frame a 60 Hz (cálculo propio).
- **Direccionalidad y código de color (SF6, columna de Capcom):** "attacks which hit go into the opponent whereas blocked moves stop right in front of them". Además "deliberately connected the color blue with blocking" ([EventHubs, traduce la columna "effects003" de Capcom](https://eventhubs.com/news/2023/jul/18/capcom-early-sf6-drive-parry)). En SF clásico los golpes conectados llevan chispas amarillas y los bloqueados un efecto azul ([Street Fighter Wiki, fan](https://streetfighter.fandom.com/wiki/Hit_Confirmation); lo saqué del resumen del buscador, no abrí la página).
- **Para un shooter** (inferencia): el impacto en enemigo **entra** en la dirección de la bala. El impacto en pared **rebota** a lo largo de la normal (Broforce: chispas por la normal; Gungeon: VFX por orientación de pared).
- **Sakurai** escribió una columna sobre hitstop ([traducción fan, Source Gaming](https://sourcegaming.info/2015/11/11/thoughts-on-hitstop-sakurais-famitsu-column-vol-490-1/)) y tiene un video con técnicas para potenciarlo, por ejemplo sacudir al golpeado ([resumen, Nintendo Wire](https://nintendowire.com/news/2022/12/12/this-week-in-sakurai-12-5-12-11-fine-tuning-hit-stop-and-cheating-the-system/)). Ninguno da números para disparos.

### C.8 Partículas por código vs. sprites dibujados

| | Sprite dibujado (flipbook) | Partículas/formas por código |
|---|---|---|
| **Control de silueta y estilo** | Total: el artista decide la forma de cada frame (cono de Gungeon, disco de Broforce) | Formas genéricas (puntos, cuadrados, círculos). El estilo sale de color, tamaño y movimiento |
| **Variedad** | Cuesta arte: cada variante es un set. Se estira con rotación, escala y flip | Gratis: cada disparo es distinto (ángulo, velocidad, vida al azar) |
| **Física e interacción** | Ninguna: el flipbook es fijo | Gravedad, rebote, orientación a la normal, "temperatura" (Broforce `Shrapnel`, chispas) |
| **Costo en runtime** | Bajo: 1 quad por efecto | Bajo a medio según cantidad. 10–12 chispas por impacto (Broforce) es nada |
| **Dónde lo usan Broforce y Gungeon** | Núcleo del fogonazo, pop de impacto, fogonazo de enemigo | Chispas, esquirlas, casquillos, cargadores, flash blanco del enemigo, screenshake, glow, distorsión o luz |

- El pack de Reactorcore recomienda la misma división: sprite de 1 frame + partículas ([OpenGameArt](https://opengameart.org/content/gun-muzzle-flash-effects-fire-and-ion-and-melee)).
- **Lectura** (inferencia): la pregunta no es (a) o (b). Es **qué parte de cada efecto necesita silueta autoral**: el núcleo del fogonazo y el anillo del impacto. **Todo lo demás conviene que sea código**. Eso es (c).

---

## D. Qué sugiere esto para el ranger (inferencia, no está medido)

1. **Fogonazo (c):**
   - **2–3 dibujos de núcleo** hechos por IA o a mano, en pixel art opaco: frame 1 **blanco** con borde cian, frame 2 cian, frame 3 cian-azul roto.
   - Cada uno se muestra **1 frame a 60 Hz**, o 2 si se ve corto. Núcleo total ≈ **0,03–0,05 s**, como Broforce y Gungeon.
   - Tamaño **≈ 0,5–0,8 H** de largo. Broforce ≈ 0,73 H y Gungeon ≈ 0,75–0,9 H; ojo, que los dos tienen personajes chiquitos y el ranger es más grande en pantalla.
   - **Emparentado a la boca**. Por disparo: rotación ±15°, escala ±15 % y flip vertical al azar.
   - **Residuo por código** de 4–7 frames: 3–6 partículas cian/azules que salen en abanico y se apagan.
   - **Halo** con `'lighter'` o `'screen'` de alfa baja.
2. **Impacto en pared (c):**
   - 1–2 frames de **disco o anillo blanco sólido**, después 3–4 frames de **anillo cian que se abre** (dibujado o un círculo por código).
   - Más **4–10 chispas por código** a lo largo de la **normal**, con gravedad, que se enfríen de blanco a cian y a azul.
   - Total ≈ 0,1 s, como el pop de Broforce.
3. **Impacto en enemigo (a):**
   - **1 frame de silueta blanca + 1 al 50 %** (flash por código, como `flashesOnDamage`).
   - Un spark chico que **entra** en la dirección de la bala.
   - Opcional: un freeze de 1 frame (10–20 ms, Vlambeer).
4. **Probar sobre el fondo más claro del nivel** antes de decidir el blending. El núcleo opaco garantiza lectura y el aditivo es sólo halo.

**Huecos principales:**
- Cantidad exacta de dibujos y fps del fogonazo vanilla de Gungeon. Haría falta el asset con su `tk2dSpriteAnimation`.
- Duración del impacto en pared en Gungeon.
- Cuántos frames tiene el `muzzleFlashPrefab` de Broforce. El video mezcla puff y arma.
- Citas de desarrolladores de Free Lives o Dodge Roll sobre efectos.
