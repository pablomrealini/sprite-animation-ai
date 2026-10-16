# Fogonazos e impactos: Metal Slug (1, 2/X, 3; Neo Geo) y Contra: Hard Corps (Genesis)

Notas para decidir cómo dibujar el fogonazo y los impactos del blaster cian del ranger. No repito lo que ya está en `Movimiento y disparo en run-and-guns/` (`metal_slug_sheets.md`, `hardcorps_blazingchrome_sheets.md`, `metal_slug_carl27_rip.md`): me apoyo en esos números (H, ángulos, cadencias) y los cito por archivo.

**Convención.** **medición propia** = medido sobre rip o video; **conteo propio** = frames contados; **cálculo propio** = aritmética; **s/d** = sin dato; el resto lleva link. "f" = frame de pantalla a ~60 Hz. En Metal Slug la lógica y los sprites se actualizan cada 2 f (≈30 Hz, ver `metal_slug.md`), así que los tiempos de MS salen en múltiplos de 2 f ("1 tick" = 2 f). Hard Corps actualiza a 60 Hz (cada frame es distinto, medición propia).

**H de referencia** (de las notas previas): Marco 38 px; Ray 40 px; Fang 47 px. Largo de arma: pistola de Marco 9–12 px, HMG ≈20 px (`metal_slug_sheets.md`); rifle de Ray ≈30 px en total, ≈15 px asoman delante del torso (medición propia, S-RAY, frame idle).

---

## 0. Resumen comparado

| | Metal Slug (pistola) | Metal Slug (HMG) | Hard Corps (todas las armas de Ray/Fang) |
|---|---|---|---|
| Dibujos de fogonazo | **3** (rojo oscuro → núcleo blanco/amarillo → hilacha amarilla) por dirección (conteo propio) | **2** formas que alternan (A bola blanca, B lengua naranja) + variante A' con humo (conteo propio) | **4** (cruz chica "+" → estrella "X" → anillo → chispas de 1 px) (conteo propio) |
| Duración en pantalla | **6 f** = 3 dibujos × 2 f (4 disparos medidos, conteo propio) | continuo mientras dispara: A/B cambia **cada 2 f** (1 bala cada 4 f) | **4 f** por bala = 4 dibujos × 1 f; con 1 bala cada 4 f queda un loop continuo |
| ¿Varía entre disparos? | No: misma secuencia en los 4 disparos medidos | Sí: alterna A/B en cada tick | No: misma secuencia siempre; los mismos 4 dibujos en todas las direcciones y en Ray y Fang |
| Tamaño máx. | adelante 15×11 px (**0.39 H**, 1.3–1.7× el arma); arriba 14×21 (**0.55 H**); abajo 11×17 (0.45 H) | adelante 23×17 px (**0.61 H**, ≈1.15× el arma); arriba ≈10×23 | anillo **16×16 px** (0.40 H de Ray, ≈0.5× el rifle) |
| Forma / orientación | alargada sobre el eje del caño, dibujada aparte para adelante/arriba/abajo | alargada sobre el eje; dibujos propios para cada uno de los 7 ángulos de tiro | radial, simétrica: sirve para los 8 ángulos sin redibujar |
| Anclaje | **Horneado en el torso** (evidencia fuerte: paleta compartida, sigue el parpadeo de invencibilidad) | Horneado en el torso (misma evidencia de paleta) | **Objeto aparte** en la boca, centrado en la punta del caño (inferencia fuerte) |
| Brillo sin blending | blancos/amarillos de la propia paleta; secuencia oscuro→claro; disco negro + disco blanco en explosiones; tinte de paleta del blanco | idem | 3 colores cálidos de la paleta del jugador (naranja, amarillo, blanco); fundidos por dither; ciclado de paleta del blanco. No vi shadow/highlight |
| Impacto | en roca: domo → huevo blanco → llama vertical → chispas, ≈10 f, hasta 14×26 px (0.68 H), **no apunta hacia la bala** (1 caso) | en blindado: chispa redonda amarilla ≈11×10 px que se deshace en puntos, ≈12–14 f; + el blanco se tiñe de naranja en bloques de 2 f | Vulcan Laser: **sin chispa en el cuerpo**; la bala sigue como nube de puntos de 1 px (≈15×15 px) **en su dirección de viaje**; el blanco cicla paleta cada frame. Crash: racimo de esferas. Spread: salpicadura roja con dither |

---

## 1. Fuentes y método

### 1.1 Sprite sheets (TSR por Wayback; el sitio vivo da 403 por Cloudflare y no lo salteé)

Listados de juego usados para encontrar las hojas: [MS1](https://web.archive.org/web/20241230045443/https://www.spriters-resource.com/neo_geo_ngcd/ms/), [MS2/X](https://web.archive.org/web/20250114162746/https://www.spriters-resource.com/neo_geo_ngcd/ms2/), [MS3](https://web.archive.org/web/20241230045443/https://www.spriters-resource.com/neo_geo_ngcd/ms3/), [Hard Corps](https://web.archive.org/web/20230730182534/https://www.spriters-resource.com/genesis_32x_scd/contrahc/).

| Archivo en `refs/metal_slug_hardcorps/` | Hoja | Tamaño PNG | Página / PNG (Wayback) |
|---|---|---|---|
| `ms_marco_11225.png` | Marco (composite MS1–MS7) | 1818×17959 | [PNG](https://web.archive.org/web/20230512095229im_/https://www.spriters-resource.com/resources/sheets/11/11225.png) (la misma de `metal_slug_sheets.md`) |
| `ms1_weapon_sfx_20583.png` | "Weapon SFX", ripper Gussprint | 605×6950 | [página](https://web.archive.org/web/20250417121124/https://www.spriters-resource.com/neo_geo_ngcd/ms/sheet/20583/), [PNG](https://web.archive.org/web/20250417121124im_/https://www.spriters-resource.com/resources/sheets/19/20583.png?updated=1460954961) |
| (no guardadas) | "Weapon SFX" de MS2/X (20587) y MS3 (20654) | 605×6950 | [20587](https://web.archive.org/web/20250705231944im_/https://www.spriters-resource.com/resources/sheets/19/20587.png?updated=1460954962), [20654](https://web.archive.org/web/20250507120445im_/https://www.spriters-resource.com/resources/sheets/19/20654.png?updated=1460954969): **mismo MD5** que 20583, es una sola compilación de toda la serie |
| `ms1_explosion_sfx_11301.png` | "Explosion SFX", Gussprint | 592×3357 | [página](https://web.archive.org/web/20250504052208/https://www.spriters-resource.com/neo_geo_ngcd/ms/sheet/11301/), [PNG](https://web.archive.org/web/20250504052208im_/https://www.spriters-resource.com/resources/sheets/11/11301.png?updated=1460954087). Las páginas de MS2 (11302) y MS3 (11305) declaran el mismo tamaño; no las bajé |
| `ms1_debris_168193.png` | "Debris", Lukebarz | 810×984 | [página](https://web.archive.org/web/20250820220416/https://www.spriters-resource.com/neo_geo_ngcd/ms/sheet/168193/), [PNG](https://web.archive.org/web/20250820220416im_/https://www.spriters-resource.com/resources/sheets/165/168193.png?updated=1642884999) |
| `ms1_blood_32528.gif` | "Blood", Kevin Huff | 504×407 GIF | [página](https://web.archive.org/web/20250823101627/https://www.spriters-resource.com/neo_geo_ngcd/ms/sheet/32528/), [GIF](https://web.archive.org/web/20250823101627im_/https://www.spriters-resource.com/resources/sheets/30/32528.gif?updated=1460956421) |
| `hc_ray_28048.png` | Ray | 985×631 | [PNG](https://web.archive.org/web/20230802021243im_/https://www.spriters-resource.com/resources/sheets/26/28048.png?updated=1460955832) (la de `hardcorps_blazingchrome_sheets.md`) |
| `hc_fang_27275.png` | Fang | 695×2322 | [PNG](https://web.archive.org/web/20230802021249im_/https://www.spriters-resource.com/resources/sheets/25/27275.png?updated=1460955759) |
| `hc_sheena_27843.png` | Sheena | 934×423 | [PNG](https://web.archive.org/web/20230802021250im_/https://www.spriters-resource.com/resources/sheets/25/27843.png?updated=1460955811) |

- **Hard Corps no tiene hoja de efectos/armas en TSR.** La sección Miscellaneous del listado sólo tiene Events, Instructor, Introduction y Police Cruiser. Los efectos de Hard Corps salen de la hoja de Fang (que trae fogonazos, una bala, una explosión y el lanzallamas) y del video.
- **En TSR no encontré la bala de la pistola de Metal Slug ni las chispas de impacto.** "Weapon SFX" trae trazadoras de HMG, cohetes, llamas, láser, escopeta, etc., pero ni la bala de pistola ni el "hit spark". Los medí en video.
- Los rips son de fans; las etiquetas ("MS5 Palette", "Post-MSX", "UNUSED") son del ripper y no las verifiqué.

### 1.2 Videos (bajados con `yt-dlp`, cliente `web_embedded`, al scratchpad; no van al repo)

| ID | Video | Formato | Uso |
|---|---|---|---|
| MS-V | [Metal Slug Arcade [60fps] Hardest – Marco Rossi No Death Speedrun](https://www.youtube.com/watch?v=_iOu1ozwk5s) (el mismo de `metal_slug.md`) | 1440×1080 @ 60 fps; 320×224 nativo → 4.5 × 4.82 | pistola, HMG, impactos, explosiones (Misión 1) |
| HC-A | [Contra Hard Corps Sega Genesis no death (Path E) 60fps – arronmunroe](https://www.youtube.com/watch?v=GCf_A9AXy_k) (el mismo de `hardcorps_blazingchrome_measured.md`) | 1600×1200 @ 60 fps (VP9); 320×224 → 5.0 × 5.357 | fogonazo, balas, impactos, Crash, Spread |

Frame `f` = `t × 60` desde el inicio del video (extraje con `ffmpeg -ss` antes de `-i`, que hace seek exacto al transcodificar). Para contar, reduje a 320×224 con filtro "area" y miré cuadro a cuadro con zoom NEAREST; los tamaños en px salidos de video tienen ±1 px por el escalado y la compresión. MS-V es una captura de emulador a 60 fps de un juego a 59.19 Hz: cada ~70 f aparece un frame duplicado, por eso a veces un "tick" dura 3 f.

### 1.3 Método sobre los sheets
Scripts en el scratchpad (`research_ms_hc/scripts/`), corridos con `python3.10 -I`, imágenes abiertas sólo como datos. Fondo del sheet por color exacto, componentes 8-conexas propias (sin scipy), bounding boxes en px del sheet. Para separar fogonazo de cuerpo usé la columna/fila de la boca del caño (tomada del frame sin fogonazo de la misma fila) y verifiqué con la lista de colores.

---

## 2. Metal Slug

### 2.1 Fogonazo de la pistola

**Hechos (medición/conteo propio, sheet M11225, fila "shoot forward" y=1046; filas arriba y=1550 y abajo y=2267):**
- La animación de disparo del torso tiene 10 dibujos; **el fogonazo está sólo en los dibujos 1–3**.
- Los 3 dibujos de fogonazo, hacia adelante:

| Dibujo | Caja | Colores | Notas |
|---|---|---|---|
| 1 | 13×9 px, pegado a la boca | (120,0,0) rojo oscuro, (176,64,0) naranja quemado | el "fogonazo" arranca **oscuro** |
| 2 | 15×11 px, pegado | (248,248,232) blanco cálido, (248,224,72) amarillo, (224,152,40) naranja | núcleo blanco con borde amarillo |
| 3 | 13×5 px, **despegado 2 px** de la boca | amarillo + blanco | hilacha que se va |

- Hacia arriba: 14×21 → 12×21 → 4×18 px. Hacia abajo: 9×17 → 11×17 → 3×14 px. En arriba/abajo el ripper dejó los dibujos 2–3 separados del cuerpo (el 1 está pegado), igual que el 3 de adelante.
- **Casquillo:** en los dibujos 2–4 de la fila hacia adelante hay 2–3 px naranjas que suben por detrás del arma: la vaina está dibujada dentro del frame del torso, no es un objeto aparte (componentes de 3 px en x=147–149 y x=203–205, medición propia).
- **Duración en pantalla (MS-V, conteo propio):** 4 disparos, todos iguales, **dibujo 1 = 2 f, dibujo 2 = 2 f, dibujo 3 = 2 f → 6 f ≈ 0.10 s** (cálculo propio, 6/59.19). Frames 545–550, 557–562, 579–584, 589–594 ([t≈9.1–9.9 s](https://www.youtube.com/watch?v=_iOu1ozwk5s&t=9s)). Intervalo entre disparos tocando el botón: 10–12 f (conteo propio).
- **Tamaño relativo (cálculo propio):** 15 px adelante = **0.39 H**, 1.3–1.7× el largo de la pistola (9–12 px). Vertical 21 px = 0.55 H.

### 2.2 Fogonazo de la HMG

**Hechos (sheet M11225, fila y=3659; video MS-V):**
- 4 dibujos de torso disparando con el fogonazo adentro: **A** bola blanca (22×17 px, blanco + amarillo), **B** lengua naranja (23×12, naranja + amarillo, despegada 1 px), **A'** bola (22×15) con un humo dibujado sobre el caño, **B'** lengua (23×10) (medición propia). Ya estaba documentado que cada ángulo diagonal tiene 2 variantes de fogonazo (`metal_slug_sheets.md`); acá confirmo que es el mismo patrón A/B en la pose de frente.
- Arriba: los 3 primeros dibujos tienen el fogonazo pegado (sprite de 69–71 px de alto vs ≈49 sin él → fogonazo ≈20–22 px); el 4.º lo tiene suelto, 10×23 px (medición propia, fila y=4142).
- **Duración (MS-V, conteo propio):** mientras se mantiene el fuego, el fogonazo **nunca se apaga**: cambia A↔B **cada 2 f** (frames 2706–2719, [t≈45.1 s](https://www.youtube.com/watch?v=_iOu1ozwk5s&t=45s)). Con 1 bala cada 4 f ([TASVideos](https://tasvideos.org/9815S), citado en `metal_slug.md`), cada bala ve una A y una B.
- **Tamaño relativo (cálculo propio):** 23 px = **0.61 H**, ≈1.15× el largo de la HMG (≈20 px).

### 2.3 Anclaje: horneado en el frame del torso

**Hechos:**
1. **El fogonazo no agrega colores.** El conjunto de colores de los torsos de pistola con fogonazo (dibujos 1–3) es idéntico al de los dibujos sin fogonazo (4–10): 13 colores en total. En la HMG, fila de disparo y fila de follow-through: los mismos 15 colores (conteo propio). En Neo Geo cada tile de 16×16 elige una de 256 paletas de 16 entradas, con la 0 transparente ([NeoGeoDev – Palettes](https://wiki.neogeodev.org/index.php/Palettes), [Sprites](https://wiki.neogeodev.org/index.php/Sprites)): el fogonazo usa entradas de la paleta del personaje (el rojo del chaleco, el amarillo y el blanco del pelo/vincha).
2. **El fogonazo cambia de color cuando Marco cambia de paleta.** Al empezar la misión Marco parpadea con una paleta clara en bloques de 2 f. En ese estado el dibujo 1 del fogonazo sale **naranja** (≈(151,90,2) en el video) en vez de **rojo oscuro** (≈(130,9,3) con la paleta normal) (MS-V frames 545 vs 557, medición propia). Si fuera un objeto con paleta propia no seguiría el parpadeo del personaje.
3. El fogonazo está pegado al caño en las cajas del sheet y existe una variante por cada pose (adelante, arriba, abajo, 7 ángulos de HMG × 2), algo que sólo tiene sentido si es parte del dibujo de cada pose. Neo Geo no rota sprites: sólo espeja y achica ([NeoGeoDev – Sprites](https://wiki.neogeodev.org/index.php/Sprites)).

**Inferencia:** el fogonazo de MS es arte del torso (o como mínimo un pedazo del mismo metasprite con la misma paleta). El costo es un dibujo de fogonazo por pose y por ángulo, a cambio de que la forma siga el eje del caño y la animación de retroceso.

### 2.4 Cómo logra el brillo sin blending (Neo Geo)

**Hechos:** el Neo Geo no tiene semitransparencia por sprite: el único "transparente" es el índice 0 ([NeoGeoDev – Sprites](https://wiki.neogeodev.org/index.php/Sprites)). Hay un oscurecido global (REG_SHADOW), de pantalla completa, no por sprite ([neogeo-diag-bios, video DAC](https://github.com/jwestfall69/neogeo-diag-bios/blob/master/docs/tests/68k/video_dac.md)). Lo que vi que hace MS en su lugar:
- **Colores al tope de la paleta:** núcleo (248,248,232), borde (248,224,72), afuera naranja/rojo. Los fogonazos usan 2–3 colores planos, sin antialias (sheet).
- **Secuencia oscuro → claro → fino** en la pistola: el primer dibujo es rojo oscuro y recién el segundo es blanco. Inferencia: el contraste con el frame anterior hace que el blanco se lea más brillante.
- **Flash de explosión con discos sólidos:** cada explosión del sheet "Explosion SFX" empieza con un **disco oscuro (32,24,0) y después un disco blanco (248,248,248)**, de un solo color, del diámetro de la explosión: 32, 48 y 80 px en la chica, la mediana y la grande. Recién después aparece la bola de fuego (28, 42, 73 px). La explosión chica tiene 2 discos + 26 dibujos de fuego que terminan en píxeles sueltos (conteo propio). En video: disco negro ≈3–4 f, disco blanco ≈3 f (MS-V frames 2153–2165, [t≈35.9 s](https://www.youtube.com/watch?v=_iOu1ozwk5s&t=35s), medición propia ±1 f).
- **Tinte del objetivo por paleta:** el jefe de la Misión 1 se pinta entero de naranja cuando recibe balas, en bloques de **2 f naranja / 2 f normal** que se alargan a 4–6 f con varios impactos seguidos (frames 2690–2799, medición propia).
- **Invencibilidad:** el personaje entero cambia a una paleta clara cada 2 f (punto 2 de §2.3).
- **Fundidos por puntos:** explosiones, chispas y salpicaduras terminan en píxeles sueltos dispersos, no en transparencia (sheets).

### 2.5 Balas

- **Pistola (MS-V, medición propia):** óvalo naranja con centro blanco-amarillo, **≈10×6 px** (0.26 H). Avanza ≈16–18 px por tick ≈ 8–9 px/f (frames 551–556; puede haber scroll de cámara metido). No está en TSR.
- **HMG (sheet Weapon SFX, medición propia):** trazadora afinada, cabeza blanca y cola naranja, **30×5 px** (0.79 H, 1.5× la HMG). Tiene **17 dibujos pre-rotados entre 0° y 90°** (≈5.6° de paso); el ripper escribe: "For the rest of the frames, just rotate the sprites at 90°". La versión "Big/Heavy Machinegun Deluxe" trae 6 puntos que crecen (6→16 px) y una trazadora de 45×6 px.

### 2.6 Impactos

**a) Pistola contra superficie dura (roca de la Misión 1), MS-V frames 587–597, [t≈9.8 s](https://www.youtube.com/watch?v=_iOu1ozwk5s&t=9s), medición propia ±1 px:**

| Frames | Dibujo | Caja aprox. |
|---|---|---|
| 587–588 | la bala apoyada en la superficie | 9×5 |
| 589–590 | domo bajo amarillo con centro blanco, base plana sobre la roca | 12×8 |
| 591–592 | "huevo" blanco con borde amarillo | 14×14 (0.37 H) |
| 593–595 | llama vertical con núcleo blanco | 14×26 (**0.68 H**) |
| 596–597 | tallo fino + chispas/fragmentos sueltos | ≈12×24 |

- Total ≈10 f (5 ticks) antes de que se encime el impacto de la bala siguiente; el final queda tapado, así que puede durar un poco más (s/d).
- **No es direccional en este caso:** la bala venía horizontal desde la izquierda y la llama sube vertical. Es un solo caso, y la bala pegó en el borde superior de la roca: no sé si contra una pared vertical sale igual (s/d).
- Es sólo sprite (secuencia dibujada): las "chispas" del final son píxeles del mismo dibujo, no partículas con física (inferencia, por cómo se repite la forma).

**b) HMG contra blindado (jefe de la Misión 1), MS-V frames 2724–2745, [t≈45.4 s](https://www.youtube.com/watch?v=_iOu1ozwk5s&t=45s), medición propia:**
- Chispa redonda amarillo-blanca de **≈11×10 px** en el pico (0.29 H, ≈½ HMG). Después se achica en estrella y se deshace en puntos amarillos sueltos. En total ≈12–14 f, cada dibujo 2 f.
- Redonda: **no apunta** a la dirección de la bala.
- Mientras el jefe está naranja, la chispa sigue amarilla, así que es un objeto con paleta propia (medición propia). Encima se suma el tinte naranja del jefe (§2.4) y el daño progresivo dibujado en el jefe: la cubierta se va rompiendo.

**c) Soldados:** no vi chispa sobre el cuerpo. El soldado pasa directo a su animación de muerte y sale una **salpicadura** grande (en MS-V es **blanca**, frames 540–546 y 569–590). La hoja "Blood" tiene 3 chorros chicos (8, 8 y 10 dibujos; el tercero es un **cono direccional**) y una salpicadura grande de 8 dibujos de 72–118 px de ancho (≈2–3 H) (conteo/medición propia). La sangre es una opción de soft-DIP que hay que activar ([MiSTer forum](https://www.misterfpga.org/viewtopic.php?p=20267)). **Inferencia:** la salpicadura blanca es la versión "sin sangre" de los mismos sprites. No lo verifiqué.

**d) Objetos destructibles:** la hoja "Debris" tiene escombros de metal, madera y roca en rotaciones de 8 dibujos (conteo propio). Son objetos aparte que salen volando al romper cajas o estructuras; en MS-V la caja de madera se rompe en los frames 600–611.

**e) Piso/pared con HMG:** s/d (no encontré un caso limpio en el tramo analizado).

### 2.7 Gaps MS
- MS2/X/3: no medí video; la hoja de Marco y la de Weapon SFX son compilaciones de toda la serie, así que los dibujos valen para MS1–3, pero no los tiempos.
- El sprite de impacto de pistola/HMG no está en TSR: los tamaños salen sólo de video (±1 px).
- No medí cuánto dura el fogonazo de la HMG cuando se suelta el botón (si queda un último dibujo).

---

## 3. Contra: Hard Corps

### 3.1 Fogonazo

**Hechos:**
- **4 dibujos**, iguales para Ray y Fang y en todas las direcciones: **"+"** chica (7×8 px) → **estrella "X"** (13×13) → **anillo con puntas y centro hueco** (16×16) → **chispas** (16×16 de caja, 25 px sueltos). Fuente: hoja de Fang, que los trae compuestos sobre el cuerpo (fila de 5 frames: sin fogonazo + 4 etapas) y **además sueltos, aparte del cuerpo**; también arriba, en diagonal corriendo, cuerpo a tierra y en el salto (medición/conteo propio, S-FANG y=575–600).
- Colores: sólo 3, naranja (255,148,74), amarillo (255,222,106) y blanco (255,255,255) (S-FANG, medición propia).
- **Duración (HC-A frames 25478–25501, [t≈424.6 s](https://www.youtube.com/watch?v=GCf_A9AXy_k&t=424s), conteo propio):** **1 f por dibujo**: "+" (el frame en que nace la bala) → estrella → anillo → chispas, y vuelve a empezar con la bala siguiente. Con 1 bala cada 4 f (`hardcorps_blazingchrome_measured.md`) el loop es continuo y no hay frames vacíos.
- **Siempre la misma secuencia,** sin variantes entre disparos.
- **Posición:** centrado sobre la punta del caño, con la mitad encima del caño. En la hoja de Fang, el frame con "+" sobresale 3 px de la boca, el de la estrella 6 px y el del anillo 8 px (medición propia).
- **Tamaño relativo (cálculo propio):** anillo de 16 px = **0.40 H** de Ray, 0.34 H de Fang, ≈0.5× el rifle de Ray (≈30 px).
- El cuerpo no se mueve al disparar: sólo cambia el fogonazo (ya documentado en `hardcorps_blazingchrome_sheets.md` §4).

### 3.2 Anclaje: objeto aparte en la boca

**Hechos:** (1) el ripper los lista sueltos al lado de los frames compuestos; (2) son los mismos 4 dibujos para dos personajes distintos y para todas las direcciones; (3) el ciclo de 4 f del fogonazo corre con el cuerpo quieto; (4) el sheet de Ray (otro ripper) no trae ningún fogonazo en los frames del cuerpo.
**Inferencia (fuerte):** es un objeto de efecto genérico que se crea en el punto de boca de cada pose (igual que la tabla de bocas por pose de Contra NES, ver `contra_hardcorps_blazingchrome.md` §6). Como es radial y simétrico, no necesita dibujos por ángulo: sólo un offset de boca por pose. No encontré el código ni un debug que lo confirme (s/d).

**Paleta:** los 3 colores del fogonazo están dentro de la paleta del jugador. La de Ray en el sheet (13 colores) coincide con la de Fang, salvo el redondeo RGB de cada ripper, e incluye (248,144,72), (248,216,104) y (248,248,248) (medición propia). Los celestes de la bala del Vulcan Laser y de sus puntos de impacto, (144,216,248), (0,144,176) y (0,72,104), también son de esa paleta. **Inferencia:** jugadores, balas y fogonazos comparten una línea de paleta. El Genesis tiene sólo 4 líneas de 16 colores, con la 0 transparente ([Raster Scroll – VDP](https://rasterscroll.com/mdgraphics/vdp-inner-workings/)).

### 3.3 Brillo sin blending (Genesis)
- El VDP tiene **shadow/highlight**: con colores "operador" (paleta 3, colores 14/15) un sprite puede aclarar u oscurecer lo que tiene debajo ([Raster Scroll – Shadow and Highlight](https://rasterscroll.com/mdgraphics/graphical-effects/shadow-and-highlight/)). **No encontré fuente de que Hard Corps lo use** (s/d). En lo que medí, los fogonazos, las balas y los discos blancos de las explosiones son de colores planos y opacos, y el fondo no se ve aclarado debajo (observación propia, HC-A). Si usara highlight, se vería la textura del fondo aclarada.
- Lo que sí vi: blanco puro + amarillo + naranja en dibujos muy chicos que cambian cada frame (a 60 Hz la estrella y el anillo "titilan" por forma, no por apagado). **Fundidos por dither:** la explosión de la hoja de Fang tiene 9 dibujos, 16×16 → 48×90 px, y el último es un tramado de puntos; la salpicadura del Spread también es tramada (medición propia). **Ciclado de paleta del blanco** al recibir (§3.5).

### 3.4 Balas de Ray (A–D)

Lo que dice el wiki de Contra ([Ray Poward, vía Wayback](https://web.archive.org/web/20241127050539/https://contra.fandom.com/wiki/Ray_Poward)): A = **Vulcan Laser**, "Besides for the blue, slim coloration, this weapon plays out exactly like the default gun"; B = **Crash**, que explota al pegar o después de cierta distancia; C = **Spread**, 5 balas rojas esféricas; D = **Homing**.
- **Default (antes de agarrar la A):** el ícono del HUD es un punto rojo (HC-A t≈15–20 s). La bala de Fang en su hoja es un punto rojo de 6×6 px (medición propia). El impacto de la bala default no lo medí (s/d).
- **A, Vulcan Laser (HC-A frames 25478–25489, medición propia):** raya **cian de 16×2 px** (0.40 H), **8 px/f**, una cada 4 f, o sea 32 px entre balas. Nace con 12 px de largo en la boca, en el mismo frame que la "+". **Es la referencia más directa para el blaster cian del ranger.**
- **B, Crash (HC-A frames 7326–7372, [t≈122 s](https://www.youtube.com/watch?v=GCf_A9AXy_k&t=122s)):** cápsula chica a rayas rojas y blancas (≈6×3 px) que termina en un **racimo de esferas**: disco blanco → esferas naranjas con banda → rojas → tramado. Esferas de ≈10–14 px, varias a la vez y escalonadas (medición propia).
- **C, Spread (HC-A frames 27424–27447, [t≈457 s](https://www.youtube.com/watch?v=GCf_A9AXy_k&t=457s)):** esferas rojas. Al pegar en el jefe dejan **salpicaduras rojas tramadas**; con el jefe cargado de sprites no pude aislar una sola (observación propia). El fogonazo es el mismo de 4 dibujos.
- **D, Homing:** s/d (no lo medí).

### 3.5 Impactos

**a) Vulcan Laser contra un enemigo (arena del Path E), HC-A frames 25106–25124, [t≈418.5 s](https://www.youtube.com/watch?v=GCf_A9AXy_k&t=418s), medición propia:**
- **No hay chispa ni estrella sobre el cuerpo.** La bala desaparece en el enemigo y **del otro lado aparece una nube de ≈15×15 px de puntos de 1 px** (blanco, celeste y azul, los colores de la bala). La nube **sigue en la dirección de la bala** a ≈8–10 px/f durante ≈4–5 f, hasta salir de pantalla. **Es direccional:** continúa el vector de la bala.
- **El enemigo cicla paleta cada frame:** gris/blanco → multicolor "negativo" → rojo → normal, un ciclo de 4 f en fase con la cadencia de 4 f. Sólo cicla la parte golpeable (torso y piernas); la cabeza queda normal.
- **Pared/piso:** en esa arena las balas que no pegan llegan al borde de la pantalla, y no vi un impacto contra pared. s/d.

**b) Crash, Spread:** ver §3.4. Las explosiones de Hard Corps son **racimos de esferas** (blanco → naranja → rojo → tramado) con muchas esferas en simultáneo, no un único sprite grande (observación propia en todo el video).

### 3.6 Gaps HC
- No hay hoja de efectos en TSR: tamaños de impactos y explosiones sólo de video (±1 px) y de la hoja de Fang.
- No confirmé con código ni con debug que el fogonazo sea un objeto aparte.
- Impacto de la bala default, del Homing y contra paredes: s/d.

---

## 4. Citas de devs
- **Sobre fogonazos o chispas puntualmente: s/d** para SNK/Nazca y para Konami (Hard Corps). Busqué en Shmuplations, Automaton, Siliconera y en la entrevista de BEEP! resumida en Wikipedia, sin resultado.
- Contexto de MS2: Akio estima la animación en "about 6000 frames" y Meeher habla del slowdown por la cantidad de sprites de gallinas ([Shmuplations, entrevista de 1998](https://shmuplations.com/?p=19321); citas leídas a través de un resumen de la página, no verifiqué el contexto exacto). En otra nota, Akio cuenta que sus animaciones largas les complicaron la vida a los programadores ([Automaton](https://automaton-media.com/en/news/metal-slug-artist-akio-says-his-elaborate-pixel-animations-made-his-programmers-want-to-rip-their-hair-out-but-it-was-so-worth-it/); sólo leí el titular).
- Nakazato dirigió Hard Corps ([GamesBeat](https://gamesbeat.com/the-retrobeat-bringing-back-contra/)); no encontré declaraciones suyas sobre efectos.

---

## 5. Inferencias para el ranger (blaster cian)

Todo esto es inferencia, no dato.
- **Fogonazo estilo Hard Corps (objeto aparte, radial):** con 4 dibujos de 1 f cada uno, centrados en la boca, cubrís todos los ángulos de tiro con un solo set y sólo necesitás un punto de boca por pose. Se puede dibujar con IA o con formas por código: son estrella, anillo y puntos de 3 colores, figuras simples. Escalado al ranger (cálculo propio, H=128 px): anillo ≈51 px (0.40 H), bala ≈51×6 px a ≈26 px/f si se copia 8 px/f × 3.2.
- **Fogonazo estilo Metal Slug (horneado por pose):** se ve más "pesado" y acompaña el retroceso, pero te obliga a un fogonazo por pose y por ángulo, y a 2 variantes si es automático. Con el pipeline de IA por pose eso multiplica los frames a generar. Si se hornea, conviene que la secuencia sea de 3 tiempos: **oscuro/saturado → núcleo blanco → hilacha que se despega** (MS, 6 f en total).
- **Brillo:** ninguno de los dos usa blending. El "brillo" sale de núcleo blanco + 1–2 colores saturados planos, formas que cambian cada frame y un disco blanco sólido de 1–2 ticks al empezar las explosiones. En HTML/canvas el aditivo está disponible (`globalCompositeOperation = 'lighter'`), pero para el look retro alcanza con colores planos. El tinte de paleta del blanco (MS: bloques de 2 f; HC: ciclo de 4 colores) es el feedback de "le pegué" más barato.
- **Impacto del láser cian:** Hard Corps es la referencia directa, porque su Vulcan Laser es una raya cian de 16×2. Ahí no hay chispa en el cuerpo: la bala se deshace en puntos de su propio color que siguen su dirección, más el flash de paleta del enemigo. Esto sale fácil por código (partículas de 1–2 px con la velocidad de la bala). Para paredes, la referencia es la llama de MS: un sprite de ≈10 f que no depende de la dirección.
