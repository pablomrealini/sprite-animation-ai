# Fogonazos e impactos en Cuphead (Studio MDHR, 2017) y Blazing Chrome (JoyMasher, 2019)

Parte de la investigación "partículas por código vs sprites animados vs mezcla" para el blaster cian del ranger. Este archivo cubre sólo Cuphead y Blazing Chrome; no repite lo ya medido en `research_notes/Movimiento y disparo en run-and-guns/` (alturas H, escala de cámara, offsets de boca por pose, etc.), lo cita.

## Fuentes y método

**Cuphead**
- **Decomp:** [jmxamongusmodder/cuphead-decomp](https://github.com/jmxamongusmodder/cuphead-decomp) (commit `1b17964`, dic-2023, build con DLC; proyecto exportado como Unity 2017.3.0f3 según `ProjectSettings/ProjectVersion.txt`). Bajé sólo blobs puntuales (clon `--filter=blob:none` + sparse checkout) y resolví GUIDs prefab → `AnimatorController` → `AnimationClip` con un parser propio. Los sprites están *stripeados* en el decomp (GUID `deadbeef`): se ven **keyframes, tiempos y eventos**, no los dibujos.
- **Dibujos:** sheet "Peashooter" de The Spriters Resource, ripeado por AndrewDev, 2048×2048 RGBA, leído por Wayback ([página](https://web.archive.org/web/20230730073946/https://www.spriters-resource.com/pc_computer/cupheaddontdealwiththedevil/sheet/142808/), [PNG](https://web.archive.org/web/20230730073946im_/https://www.spriters-resource.com/resources/sheets/140/142808.png?updated=1604517596)). Tiene rótulos `bullet_spawn` (= fogonazo), `bullet_loop`, `bullet_death`, `EX_loop`, `EX_death`. Hay sheets de las demás armas en el mismo índice (Spread 142809, Roundabout 142813, Lobber 161833, Chaser 161852, Charge 161821, Crackshot 179719); no los analicé.
- **Video:** [Sally Stageplay, Peashooter only, Sidewalk1986](https://www.youtube.com/watch?v=QoKv2p74dIw&t=42s), 1080p, 59.94 fps, Mugman parado disparando hacia adelante en t = 42.0–43.0 s.
- **Escala:** en ese tramo la bala recorre 56–57 px de video por frame (**medición propia**), y 2250 u/s × 1.5 px/u ÷ 60 = 56.25 px/f (**cálculo propio**, velocidad del decomp y 1.5 px/u de la nota de movimiento). O sea, cámara a zoom 1. Mugman mide ≈ 227 px de pajita a suela (**medición propia**), coherente con H ≈ 230 px = 153 u de la nota previa. **Los px del rip coinciden ≈ 1:1 con px de pantalla a 1080p**: la bala mide 102–110 × 19–24 px de núcleo cian en video y 99–138 × 14–21 px (α ≥ 128) en el rip (**medición propia**).

**Blazing Chrome**
- **Sin sprite sheets:** la nota previa ya verificó que TSR no tiene (ni en Wayback) sheets de Blazing Chrome (`hardcorps_blazingchrome_sheets.md` §6). Todo lo de BC acá es **medición propia sobre video**.
- **Video:** ["[HARDCORE] Blazing Chrome - All Bosses, No Hits, Starting Weapons Only", Vix Vidya](https://www.youtube.com/watch?v=yHNwfRtqPR4), PC, 1280×720 a 60/1 fps, con Mavra y el **arma inicial**. Analicé t = 3.0–11.0 s (jefe 1). "Frame i" abajo = t = 3.0 + i/60 s.
- **Escala:** periodicidad de bordes 3 px en ambos ejes ⇒ 1 px nativo = 3 px de video (**medición propia**; coincide con el ≈ 427×240 ×3 de la nota previa). H de Mavra = 43–44 px nativos (`hardcorps_blazingchrome_measured.md` §1).
- **Limitación de descarga:** YouTube cortó todas las descargas a ≈ 20–30 MB (HTTP 403), así que sólo tengo el primer minuto de cada video. Todo lo de BC sale de ese tramo de un único jefe.

**Herramientas:** Python 3.10 (PIL/numpy) con `-I`, scripts en el scratchpad. Nada de lo que está en `refs/` es asset.

**Material de análisis en `refs/cuphead_bc/`** (gitignoreado):
- **Cuphead:**
  - `cuphead_tsr_142808_peashooter.png` (sheet original);
  - `cuphead_peashooter_muzzle_4frames_x3.png`, `cuphead_peashooter_death_6frames_x3.png`, `cuphead_muzzle_f3_glow_alpha_x6.png` (recortes del sheet);
  - `cuphead_video_*` (recortes del video a 60 fps).
- **Blazing Chrome:**
  - `bc_video_muzzle_variants_grid.png`, `bc_video_yHNwfRtqPR4_muzzle_montage.png` (los 21 fogonazos);
  - `bc_video_f400-431_mavra_firing.png`, `bc_video_flash_follows_gun.png`, `bc_video_diag_flash.png`;
  - `bc_video_hit_spark_grid.png`, `bc_video_f446-475_impacts_hitflash.png`, `bc_video_floor_impact.png`, `bc_video_boss_hitflash_palette.png`.
- **Regla en las grillas:** marcas cada 5 px nativos (15 px de video).

---

## 1. Fogonazo (muzzle flash)

### Cuphead: hechos

**Cómo se crea** ([AbstractLevelWeapon.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/AbstractLevelWeapon.cs), `fireProjectile`)
- En **cada disparo** se instancia un prefab nuevo `basicEffectPrefab.Create(posición de la bala, escala del arma)`. Es un objeto aparte por tiro, no una animación del cuerpo del personaje.
- La posición es `GetBulletPosition()`: origen del player + offset fijo por pose (la tabla `ProjectilePosition` de la nota de movimiento, p. ej. Forward = (78, 64) u) ([LevelPlayerWeaponManager.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerWeaponManager.cs)).
- El cuerpo además dispara su propio clip `shoot_*_fire` de 3 dibujos (nota de movimiento). Fogonazo y "retroceso" del cuerpo son capas separadas.

**Clip del Peashooter** ([Player_Weapon_Peashot_Muzzle.prefab](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/PrefabInstance/Player_Weapon_Peashot_Muzzle.prefab) → `animator_weapon_peashot_basic_flash.controller` → [anim_weapon_peashot_basic_flash_a.anim](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/AnimationClip/anim_weapon_peashot_basic_flash_a.anim))
- `m_SampleRate: 20`, **4 keyframes de sprite** a t = 0, 0.05, 0.10, 0.15, y evento `OnEffectComplete` a **0.2 s**, que destruye el objeto.
- Duración (**cálculo propio**): 4 dibujos × 3 frames a 60 Hz = **12 frames = 0.2 s**. Ojo: el fogonazo va a 20 fps, no a los 24 fps del resto de la animación.
- El sheet tiene exactamente **4 dibujos** en `bullet_spawn` (**conteo propio**):
  1. disco cian dentado;
  2. anillo blanco con agujero;
  3. salpicadura blanca con rayos;
  4. estrella fina de 4 puntas cian con borde blanco.

**Cadencia y solapamiento**
- El Peashooter tira **cada 8 frames a 60 Hz = 7.5 tiros/s** (**conteo propio** en video: balas nuevas en los frames 4/5, 12/13, 20/21, 28/29, 36/37 del tramo de 42.0 s).
- El código explica el 8. El coroutine suma `FixedDelta` mientras `t < 0.11` y dispara en el *siguiente* step. Con t = 7/60 = 0.1167 ≥ 0.11, el disparo cae en el step 8 (**cálculo propio**).
- **Corrección:** la nota de movimiento dice "7 frames → 8.57 tiros/s". Según código + video son 8 frames (7.5 tiros/s).
- Con vida de 12 frames cada 8, conviven **1–2 fogonazos superpuestos** (12/8 = 1.5 en promedio, **cálculo propio**). En video se ve siempre alguno encima del dedo (**observación propia**).

**Variantes** ([Effect.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/Effect.cs) + prefab)
- El Animator tiene `Count = 1`: **una sola secuencia de dibujos**.
- La variedad sale del prefab, que tiene `randomRotation: 1`, `randomMirrorX: 1`, `randomMirrorY: 1`. Por tiro: rotación aleatoria 0–360° y espejado X/Y aleatorio (`Effect.Initialize`).
- Por eso los dibujos son formas radiales (estrella, anillo, salpicadura) que funcionan en cualquier ángulo. En video se ven en orientaciones distintas tiro a tiro (**observación propia**).
- `Effect` también soporta N variantes al azar (`Animator.SetInteger("Effect", Random.Range(0, Count))`). El fogonazo no lo usa; los impactos de jugador y otros efectos sí (§4).

**Tamaño**

Bbox por dibujo en px del rip ≈ px a 1080p (**medición propia**):

| Dibujo | α > 0 | α ≥ 128 |
|---|---|---|
| 1 | 60×69 | 49×59 |
| 2 | 65×77 | 55×68 |
| 3 | 91×87 | 82×77 |
| 4 | 101×97 | 93×89 |

Relativo a H = 230 px (con pajita) (**cálculo propio**):
- **≈ 0.21–0.44 H** de ancho (α ≥ 128 a α > 0), o ≈ 33–67 u. Crece del primer dibujo (≈ 0.21–0.26 H) a la estrella final (≈ 0.40–0.44 H).
- Relativo al "arma" (el guante que apunta, ≈ 50 px = 0.22 H, **medición propia** en video): el fogonazo mide **≈ 1.1–2× el guante**.
- En video, dos fogonazos superpuestos llegan a ≈ 90 × 115 px (**medición propia**, a ojo sobre una regla, ±10 px).

**Otras armas**

Todas usan la misma clase `WeaponSparkEffect`, el mismo material y los mismos flags de random rot/mirror, y todas tienen `Count = 1`. Clips (**conteo propio** sobre los `.anim`):

| Arma (código) | Prefab de fogonazo | Clip | Dibujos visibles | Duración |
|---|---|---|---|---|
| Peashooter (`Peashot`) | `Player_Weapon_Peashot_Muzzle` | 4 keys @20 fps | 4 | 0.20 s (12 f) |
| Spread (`Spread`) | `Player_Weapon_Spread_Muzzle` | 4 @20 | 4 | 0.20 s |
| Chaser (`Homing`) | `Player_Weapon_Homing_Muzzle` | 5 keys @24, evento a 0.1667 s | 4 (el 5º nunca se ve) | 0.167 s (10 f) |
| Charge | `Player_Weapon_Charge_Muzzle` | 4 @20 | 4 | 0.20 s |
| Lobber (`Bouncer`) | `Player_Weapon_Bouncer_Muzzle` | 5 keys @20, evento a 0.2 s | 4 | 0.20 s |
| Roundabout (`Boomerang`) | `Player_Weapon_Boomerang_Muzzle` | 4 @20 | 4 | 0.20 s |
| Crackshot (DLC) | `Player_Weapon_Crackshot_Muzzle` | 4 @24 | 4 | 0.167 s |
| Twist-Up / Converge (DLC, `Upshot`/`Wideshot`) | `..._Upshot_Muzzle`, `..._Wideshot_Muzzle` | 4 @24 | 4 | 0.167 s |

- Fuentes: los prefabs en [PrefabInstance/](https://github.com/jmxamongusmodder/cuphead-decomp/tree/main/Assets/PrefabInstance) y los clips `anim_weapon_*_basic_flash_a.anim` en [AnimationClip/](https://github.com/jmxamongusmodder/cuphead-decomp/tree/main/Assets/AnimationClip).
- Las armas sin terminar `WeaponArc` y `WeaponExploder` reusan el fogonazo del Peashooter.
- Mapeo de nombres de código a nombres del juego: nota de movimiento.
- Patrón general: **siempre 4 dibujos, 0.17–0.2 s**. Para el EX, el `exEffectPrefab` es `Player_Weapon_Peashot_Ex_Stars`: 3 variantes al azar (`Count = 3`) de 14–15 keys @24 (0.54–0.58 s), más `CupheadLevelCamera.Shake(5, 0.5)` al disparar.

### Blazing Chrome: hechos (medición propia, arma inicial, Mavra)

**Frames y duración**
- **Duración:** cada fogonazo dura **2 frames a 60 Hz (≈ 33 ms)**. En 21 fogonazos detectados (frames 150–476) siempre fueron 2 frames, salvo uno de 3 (164–166, posiblemente un frame duplicado del video) (**conteo propio**).
- **Cadencia con fuego sostenido:** uno cada **7 frames ⇒ ≈ 8.6 tiros/s**. Fogonazos en 383, 390, 397, 404, 411, 418, 425, 432, 439 (t = 9.38–10.32 s) (**conteo propio**).
- **Duty cycle:** el fogonazo está visible ~2 de cada 7 frames (**cálculo propio**). No hay solapamiento: cada fogonazo es un dibujo único sostenido 2 frames, sin animación interna.

**Variantes:** al menos 2 dibujos.
- (a) **Estrella gruesa de 5 puntas** con una estela horizontal hacia adelante.
- (b) **Asterisco de rayos finos** con puntas rojas, también con estela.
- **Ambas:** núcleo blanco → amarillo → naranja → rojo en las puntas.
- **Secuencia observada:** X, estrella, X, estrella, X, X, estrella, estrella(?), X. **No es alternancia estricta**; parece azar (inferencia, n = 9).
- **Diagonales:** en disparo diagonal (frames 285–286, t = 7.75 s) la forma se ve girada 45° con la estela sobre la diagonal (**observación propia**). No pude distinguir si es un dibujo aparte o una rotación nearest-neighbour.

**Tamaño** (bbox de píxeles rojos/calientes sobre fondo oscuro, **medición propia**)
- **≈ 22–30 × 22–29 px nativos** (frames 351, 404, 411, 425, 432, 439). Con la estela, el largo llega a ≈ 30–35 px.
- Relativo (**cálculo propio**): **≈ 0.6–0.7 H** de ancho (H = 43–44).
- Relativo al arma: ≈ **1.3–1.6× el largo del arma** (arma ≈ 17–18 px nativos, **medición propia**, frame 424). El fogonazo es enorme relativo al personaje, más del doble que el de Cuphead.

**Arma iluminada y retroceso**
- Mientras dura el fogonazo, el arma se redibuja en una **variante dorada/"iluminada" durante 3 frames** (p. ej. 404–406, gris otra vez en 407) (**conteo propio**).
- En el frame de disparo el arma aparece corrida **≈ 4–5 px nativos (≈ 0.1 H) hacia atrás** (403 → 404, con la cabeza quieta) (**medición propia**, confianza media).

**Vainas:** por disparo salen rectángulos chicos color latón (≈ 1×3 px nativos) hacia atrás/arriba, que caen con gravedad (frames 403–431) (**observación propia**). Son partículas simples, aparte del sprite del fogonazo.

### Inferencias
- **Dos filosofías opuestas con la misma base (sprite dibujado):**
  - **Cuphead:** 4 dibujos radiales a 20 fps con vida larga (12 f) que se solapan, y variedad por *transform* (rotación + espejo al azar) en vez de por dibujos.
  - **BC:** un solo dibujo direccional muy grande sostenido 2 frames, con 2+ variantes de dibujo. Le suma "lit sprite" del arma, retroceso y vainas.
- **Lectura de feel:** en Cuphead el fogonazo es un "halo" que vibra sobre el dedo. En BC es un estallido que parpadea a ~8.6 Hz y casi tapa el arma.

---

## 2. Anclaje a la boca

### Cuphead: hechos ([WeaponSparkEffect.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/WeaponSparkEffect.cs), `AbstractLevelWeapon.fireProjectile`)
- **Nacimiento:** el efecto nace en **coordenadas de mundo** en el punto de boca de la pose.
- **Se cuelga del player:** si la pose es `Forward`, `Forward_R` (corriendo), `Up_D` o `Up_D_R` **y el player está en el piso**, se llama `SetPlayer`: el efecto pasa a ser **hijo del transform del player** (conserva su escala) y sigue al personaje mientras corre.
- **Se suelta:**
  - si el player deja el piso (`FixedUpdate`: `!Grounded` ⇒ `parent = null`);
  - si el player se da vuelta (`LateUpdate`: cambia `localScale.x` ⇒ espeja la x local y se desengancha).
- **Queda fijo en el mundo:** en el aire (todas las direcciones), en `Up`, `Down`, `Down_D` y `Duck` el fogonazo no se mueve con el personaje. En la práctica esas poses no se desplazan en el piso: ducking y lock frenan la caminata.
- **Orden de dibujo:**
  - Sorting layer "Player", `order = -100`, es decir **detrás del cuerpo** (Cuphead está en `order 10` en [Player.prefab](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/PrefabInstance/Player.prefab)).
  - Excepción: `Pose.Down` llama `BringToFrontOfPlayer()` ⇒ `order = 100`, delante (si no, quedaría tapado por el cuerpo).
  - En video el guante se dibuja encima del fogonazo (**observación propia**).
- **Separación fogonazo/bala:** el fogonazo nace en el offset base. La bala del Peashooter se corre además `y += {0, 20, 40, 20}` u en ciclo ([WeaponPeashot.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/WeaponPeashot.cs), `yPositions`).
  - En video las balas salen a 0 / +30 / +60 / +30 px por encima del centro del fogonazo (**medición propia**: tops en y = 804 / 774 / 744 / 774), es decir, el chorro "abanica" verticalmente mientras el fogonazo queda fijo en el dedo.
- **Hitbox a quemarropa:** cada tiro agrega `Level_Weapon_Generic_Firing_Hitbox`, una caja de 100×10 u con offset −30 u (cubre de −80 a +20 u sobre el eje del disparo). Vive **1–2 steps** (se destruye en el segundo `FixedUpdate` de la bala), y el collider de la bala está apagado mientras tanto ([AbstractProjectile.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/AbstractProjectile.cs), `AddFiringHitbox`/`FixedUpdate`). Sirve para que el tiro pegue aunque la boca esté dentro del enemigo.

### Blazing Chrome: hechos
- **Sigue al arma.** Entre los dos frames de un mismo fogonazo con Mavra saltando (425 → 426, t = 10.08 s), el fogonazo se desplazó lo mismo que el personaje: ≈ 5 px nativos arriba y ≈ 1–2 px a la izquierda (**medición propia**, `refs/cuphead_bc/bc_video_flash_follows_gun.png`).
- **Comportamiento:** con 2 frames de vida, se comporta como pegado a la boca, en el aire y en el piso.
- **Orden respecto al arma:** s/d. El cañón parece verse por encima del borde del fogonazo, pero no es concluyente.

### Inferencias
- **Ninguno de los dos deja el fogonazo "atrás" cuando el personaje se mueve en el piso.** Cuphead lo resuelve parentando en el piso y lo suelta en el aire, donde el desfase de 12 frames a 1620 u/s se notaría poco porque el fogonazo es radial. BC no lo necesita: dura 2 frames.
- **Para el ranger:** si el fogonazo dura más de ~3 frames, conviene **parentarlo a la boca**. Si dura 1–2 frames, da lo mismo.

---

## 3. Blending y técnica de dibujo

### Cuphead: hechos
- **Material:** todos los fogonazos, balas básicas e impactos de jugador usan el material built-in `{fileID: 10754}` (Sprites-Default de Unity, inferido por el fileID estándar) ⇒ **alfa normal, no aditivo**.
  - En los 1081 prefabs del repo, ese material aparece en 1619 renderers (**conteo propio**).
  - En los prefabs `Player_Weapon_*`, `Level_Weapon_*`, `Player_Parry_*` y `Player_Hit` hay 59 renderers con Sprites-Default y sólo 2 con otro material (**conteo propio**).
- **Las 2 excepciones son efectos "grandes", no el disparo básico:**
  - El proyectil **EX** del Peashooter (la bola de fuego cian) usa `mat_sprites_hard_light.mat` → shader `Sprites/Blend Modes/Hard Light` ([Level_Weapon_Peashot_Ex.prefab](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/PrefabInstance/Level_Weapon_Peashot_Ex.prefab)).
  - El sprite "Top" de `Player_Parry_Effect` usa `mat_boss_screen_10.mat` → shader `Cuphead/SpriteBlendDynamic/Screen`, que computa `1 − (1 − a)(1 − b)` en el fragment (modo **screen**, no add) ([shader](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Shader/CupheadSpriteBlendDynamicScreen.shader)).
- **Halo horneado en la textura** (**medición propia** en el rip):
  - Los dibujos son formas planas (cian `≈ (152,253,254)` / blanco `≈ (235,254,254)`) con un **halo suave de ~4–6 px horneado en el alfa**.
  - 42–70 % de los píxeles del fogonazo son semitransparentes; en el impacto, 75–98 %.
  - El halo es un degradé liso, no tinta (`refs/cuphead_bc/cuphead_muzzle_f3_glow_alpha_x6.png`).
  - O sea, el "brillo" está **pintado en la textura con alfa**, no sale de un blend aditivo.
- **MDHR:**
  - Sobre el proceso en general, la nota de movimiento ya cita a Unity: todo dibujado a lápiz y tinta en papel y coloreado en Photoshop, a 24 fps "on ones".
  - No encontré ninguna cita que hable específicamente de los efectos (fogonazo, chispas, humo). La charla GDC 2017 de Jake Clark sobre animación de jefes ([resumen](https://windowscentral.com/take-deep-dive-cupheads-animation-process)) no aparece descripta con detalle de VFX.
- **Post-proceso:** existe un shader global `HiddenCupheadChromaticAberrationFilmGrain` ([Shader/](https://github.com/jmxamongusmodder/cuphead-decomp/tree/main/Assets/Shader)). En video los fogonazos muestran franjas de color en los bordes (**observación propia**), atribuible a ese post-proceso (inferencia).

### Blazing Chrome: hechos
- **Todo opaco y con paleta corta** (**observación propia**):
  - Fogonazo, impactos, balas, la burbuja de energía del jefe y el tajo cuerpo a cuerpo se ven como pixel art opaco de paleta corta: bordes duros y colores planos, sin píxeles intermedios que mezclen con el fondo.
  - El efecto azul del tajo (frames 237–241) **tapa por completo** la cabeza del jefe.
  - Los mismos colores de fogonazo aparecen igual sobre piso gris y sobre fondo rojo oscuro.
- **Desvanecimientos sin alfa:**
  - Achican o afinan la forma (impacto: medialuna → "C" → arco fino);
  - o "enfrían" el color de las chispas (blanco → amarillo → naranja → rojo).
  - Confianza media: el H.264 a 720p no deja descartar semitransparencias sutiles.
- **JoyMasher:**
  - Danilo Dias (director de arte) dice que en Blazing Chrome quiso más detalle y textura, pero: "I still used limitations on colours and resolution, however." ([MCV/UK, "When We Made… Vengeful Guardian: Moonrider", 10-mar-2023](https://mcvuk.com/?p=223533)).
  - En el blog de PlayStation describe un sistema de animación propio para "simulate the old rotation and scaling effects of the Mega Drive" ([PS Blog, 10-jul-2019](https://blog.playstation.com/archive/2019/07/10/this-is-how-blazing-chromes-horde-of-unique-retro-style-bosses-were-built)).
  - No encontré declaraciones sobre transparencias ni sobre cómo hicieron los efectos de disparo.

### Inferencias
- **Ninguno de los dos usa blending aditivo para el disparo.**
  - **Cuphead** consigue el "brillo" con halo pintado en alfa sobre blend normal. Reserva los modos de mezcla (hard light, screen) para el EX y el parry.
  - **BC** se queda en la estética Mega Drive: sin translucidez, con brillo por paleta (blanco en el centro, rojo en el borde) y "fade" por cambio de dibujo y color.
- **Para un blaster cian en HTML/canvas:** el equivalente Cuphead es `source-over` con un PNG que trae el glow en alfa. Usar `lighter` (aditivo) sería una decisión propia, no algo que copien estas referencias.

---

## 4. Impactos (hit sparks) y reacción del enemigo

### Cuphead: hechos

**Mecánica** ([AbstractProjectile.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/AbstractProjectile.cs), [BasicProjectile.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/BasicProjectile.cs))
- **La chispa de impacto es la propia bala.** Al morir (`Die()`):
  - `move = false` (se frena donde pegó);
  - se apaga el collider;
  - se sortea `Variant` y se dispara el trigger `OnDeath` del Animator, que salta al clip de muerte.
- **No se instancia otro objeto.** Hereda la rotación de la bala (orientada según la dirección del tiro) y el `scale.y = ±1` según el lado al que mira el player (`GetBulletScale`).
- **Enemigo vs escenario: el mismo dibujo.** En el Peashooter, `OnCollisionDie` sólo cambia el **sonido**: `player_shoot_hit_cuphead` si lo que tocó tiene `DamageReceiver` activo, si no `projectileMissImpactSFX`.

**Peashooter**
- **Bala** (`animator_peashot_basic.controller`):
  - `MaxVariants = 6`: 6 arranques A–F (2 keys @24 cada uno) elegidos al azar, que después pasan a un `Loop` de 6 keys @24.
- **Muerte** ([anim_peashot_basic_die.anim](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/AnimationClip/anim_peashot_basic_die.anim)):
  - 7 keys @24, pero `OnDieAnimationComplete` a 0.25 s ⇒ **6 dibujos visibles, 0.25 s = 15 frames** (**conteo propio**; el sheet tiene 6 dibujos en `bullet_death`).
  - Una sola variante de muerte.
- **Forma** (sheet):
  - un anillito cian con 3 esquirlas;
  - que **explota en un estallido radial** de trazos y gotas cian/blancas;
  - que se agranda y se afina hasta quedar un anillo de rayitas sueltas.
  - Las "partículas" están **dibujadas dentro de cada cuadro**: no hay sistema de partículas.
- **Tamaño** por cuadro, α ≥ 128 (**medición propia**): 59×46, 70×69, 145×142, 211×218, 236×248, 239×259 px.
  - Relativo a H (**cálculo propio**): de **≈ 0.26 H a ≈ 1.1 H** de diámetro.
  - Para comparar: el collider de la bala es un círculo de radio 5 u (`CircleCollider2D`, prefab).
- **Dirección:** no es direccional por forma (es radial). Sí gira con la bala, cosa que se nota poco.

**Otras armas** (**conteo propio** de keys hasta el evento de fin)

| Arma | Muerte / impacto | Variantes | Duración |
|---|---|---|---|
| Spread | `die_hit` vs `die_distance` (el tiro que se agota por alcance tiene otra anim), × small/large | 1 por caso | hit 5–6 dibujos ≈ 0.21–0.25 s; distance 4 dibujos 0.167 s |
| Chaser | `anim_homing_basic_die` | 1 | 4 dibujos, 0.167 s |
| Charge | `DeathSmall` / `DeathFull` | 1 c/u | 6–7 dibujos 0.25–0.29 s / 13–14 dibujos 0.54 s |
| Lobber | `anim_bouncer_basic_death` | 1 | 6 dibujos, 0.25 s |
| Roundabout | `anim_boomerang_basic_die` | 1 | 6–7 dibujos, 0.25 s |
| Crackshot | `ImpactSmallA/B`, `ImpactCometA/B` | A/B (elegida por el bool `IsB`/`useBComet`; no verifiqué si es al azar) | 5–8 dibujos, 0.21–0.29 s |
| Converge (DLC) | **efecto aparte** `Player_Weapon_Wideshot_HitFlash` (`WeaponSparkEffect`) instanciado en el punto de golpe | **3 al azar** (`Count = 3`) + rot/espejo al azar | 7 dibujos, 0.29 s |

- **Truco barato de variedad en la bala Chaser:** sus 5 "variantes" A–E son **el mismo clip** de 8 keys reproducido a velocidad 0, −1, −0.5, +0.5 y +1 (`animator_homing_basic.controller`).

**Reacción del enemigo** ([HitFlash.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/HitFlash.cs))
- **Mecanismo:** con cada daño, `Flash(0.1)` pone `SpriteRenderer.color = damageColor` (multiplica el sprite) durante **0.0416 s** (≈ 2–3 frames) y lo vuelve al normal 0.0832 s. El ciclo se repite mientras el timer (que cada golpe resetea a 0.1 s) siga positivo, así que con fuego sostenido es un **pulso de ≈ 2.5 frames cada ≈ 7.5 frames** (**cálculo propio**).
- **Color:** en 107 de 113 instancias serializadas es `(0.603, 0.957, 1.0)`, un **tinte cian claro** que baja el rojo (**conteo propio**; `HitFlash` aparece en 99 prefabs).
- **Alcance:** lo requieren los enemigos de plataforma (`[RequireComponent(typeof(HitFlash))]` en `AbstractPlatformingLevelEnemy`) y algunos jefes. **No es universal** en los jefes.

**Parry** ([AbstractParryEffect.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/AbstractParryEffect.cs))
- **Chispa:** por cada proyectil rosa parriado se crea `Player_Parry_Spark` **en la posición del proyectil**, con rotación y espejo X/Y al azar, sorting `-1000`. Clip de 9 keys @24 ⇒ **0.375 s**.
- **Pausa global (hit-stop):** `PauseManager.Pause()` pone `CupheadTime.GlobalSpeed = 0` durante **0.185 s ≈ 11 frames** (0.139 s si lo parriado es un enemigo).
  - Los efectos con `AnimationHelper.ignoreGlobal = 0` se congelan, incluida la chispa.
  - El parry de Cuphead es entonces **chispa + congelado de pantalla**, y suma la capa en modo screen descripta en §3.

### Blazing Chrome: hechos (medición propia, t = 10.48–10.75 s)

**Chispa de impacto**
- Es un **sprite en forma de medialuna/"C" de fuego** (blanco → amarillo → naranja con borde rojo) que nace en el punto de impacto.
- **Direccional:** la concavidad queda **hacia el tirador**, como una salpicadura que rebota.
- **Duración:** ≈ **6 frames (0.1 s)** por impacto, en 3 etapas aparentes de ~2 frames: medialuna chica → "C" grande → arco fino. Ejemplos: frames 449–454 y 455–460 (**conteo propio**).
- **Tamaño máximo:** ≈ **15 × 18 px nativos ≈ 0.35–0.4 H** (**medición propia**, frame 451).

**Partículas sueltas**
- Además del sprite, salen **decenas de puntos de 1 px nativo** (blancos/amarillos) **hacia atrás**, en el sentido opuesto a la bala, en un cono de ~25–35 px.
- Duran bastante más que el sprite (≳ 10–15 frames).
- **Se "enfrían" de color:** en 462–464 ya no quedan blancos y sí naranjas y rojos (**conteo propio** de colores por frame, confianza media porque otros objetos ensucian la cuenta).

**Impacto contra el piso**
- Mismo tipo de dibujo orientado según el ángulo de entrada: en un tiro diagonal hacia abajo aparece una **"U" de fuego** abierta hacia arriba (frames 287–288, t = 7.78 s), ≈ 13 × 17 px nativos.
- Después parece aplanarse y ensancharse (≈ 21 × 10 px, frames 289–291).
- Confianza baja: se superpone con el polvo del rolido de Mavra.
- No vi balas pegando en paredes: s/d.

**Reacción del enemigo**
- **Swap de paleta del sprite entero** a tonos **durazno/piel claros**, conservando el detalle interno (no es blanco plano).
- **3 frames** por golpe (449–451, 455–457, 465–467) (**conteo propio**).
- **No todos los impactos lo disparan:** hubo impactos sin flash, así que podría tener cooldown (inferencia).
- **Cuerpo a cuerpo:** la cabeza del jefe pasa a **paleta azul hielo** ≈ 5–6 frames (237–242, t = 6.95 s) (**conteo propio**).

### Inferencias
- **Cuphead:** impacto = la bala se transforma en un estallido radial **dibujado** que crece hasta ~1 H y dura 0.25 s. Es grande y legible, pero barato en código: sin partículas y sin distinguir enemigo de pared salvo por sonido.
- **BC: mezcla real de sprite + partículas por código.**
  - El sprite direccional chico (~0.4 H, 0.1 s) da la forma.
  - Los puntos de 1 px con cambio de color dan la "chispa" y la persistencia.
  - El enemigo responde con un swap de paleta de 3 frames.
- **Para el ranger, si los impactos van a ser muy frecuentes (7.5–8.6 tiros/s), las dos referencias sugieren:**
  - un sprite de impacto corto (0.1–0.25 s);
  - variedad por transform o variantes;
  - y, opcionalmente, partículas de 1–2 px para la cola, que es lo que hace BC.

---

## 5. Tabla resumen

| | Cuphead (Peashooter) | Blazing Chrome (arma inicial) |
|---|---|---|
| Fogonazo: técnica | Sprite dibujado a mano (4 dibujos) instanciado por tiro | Sprite pixel art (1 dibujo × 2 frames) por tiro |
| Fogonazo: duración | 0.2 s = 12 f a 60 Hz (clip a 20 fps); Chaser/Crackshot/DLC 0.167 s | 2 f (≈ 33 ms) |
| Cadencia | 1 tiro / 8 f = 7.5/s (código + video) ⇒ 1–2 fogonazos superpuestos | 1 tiro / 7 f ≈ 8.6/s ⇒ visible 2 de cada 7 f |
| Variantes | 1 secuencia + rotación 0–360° y espejo X/Y al azar por tiro | ≥ 2 dibujos (estrella / asterisco), orden no estrictamente alternado; versión diagonal |
| Tamaño | 57–100 px a 1080p ≈ 0.25–0.44 H; ≈ 1.1–2× el guante | ≈ 22–30 px nativos ≈ 0.6–0.7 H; ≈ 1.3–1.6× el arma |
| Anclaje | Nace en offset de boca por pose; hijo del player en el piso (forward / diag-up, también corriendo); se suelta en el aire o al girar; detrás del cuerpo salvo apuntando abajo | Se mueve con el arma (verificado en salto) |
| Extras al disparar | Clip de cuerpo `shoot_*_fire` (3 dibujos); hitbox a quemarropa de 1 step | Arma "iluminada" 3 f; retroceso ≈ 4–5 px nativos; vainas eyectadas |
| Blending | Alfa normal (Sprites-Default); glow pintado en el alfa de la textura (hard light sólo en el EX, screen sólo en el parry) | Opaco, sin translucidez visible; brillo por paleta |
| Impacto | La bala se convierte en un estallido radial de 6 dibujos, 0.25 s, de ~0.26 a ~1.1 H; igual en enemigo y pared (sólo cambia el SFX) | Medialuna direccional ~0.4 H, ~6 f + decenas de puntos de 1 px que se enfrían de color; "U" en el piso |
| Reacción del enemigo | Tinte cian `(0.6, 0.96, 1)` multiplicado, pulsos de 0.04 s on / 0.08 s off (enemigos de plataforma y algunos jefes) | Swap de paleta a durazno 3 f (balas); azul ~5–6 f (cuerpo a cuerpo) |
| Parry / extra | Chispa al azar (rot/espejo) 0.375 s + pausa global 0.185 s + capa en modo screen | s/d (BC no tiene parry) |

---

## 6. Huecos

- **Cuphead:**
  - Los dibujos de fogonazo e impacto de Spread/Chaser/Lobber/Charge/Roundabout/Crackshot no se miraron (los sheets existen en TSR vía Wayback, IDs arriba).
  - Los tamaños en pantalla dependen del zoom de cámara de cada nivel; lo medido es a zoom 1.
  - No hay cita de MDHR específica sobre efectos.
- **Blazing Chrome:**
  - Todo sale de ~8 s de un jefe, con un personaje y una sola arma.
  - **s/d:** las otras armas (láser, látigo, plasma, etc.), Doyle, impactos contra paredes, si el fogonazo cambia por pose (sólo vi forward y una diagonal) y si hay más de 2 variantes.
  - La descarga quedó limitada por los 403 de YouTube (≈ 20–30 MB por video). Con un video completo o captura propia del PC a 427×240 se podrían cerrar variantes y frames por dibujo.
  - No encontré cita de JoyMasher sobre efectos o transparencias.
