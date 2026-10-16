# Sprite-sheet analysis: Contra: Hard Corps (Genesis, 1994; Ray, Sheena, Fang, Browny) and Blazing Chrome (2019; Mavra, Doyle)

This file adds sheet-based measurements to `contra_hardcorps_blazingchrome.md` (main file) and `hardcorps_blazingchrome_measured.md` (video addendum). It fills their "nf"/"nm" cells for sprite construction, frame counts, aim poses and widths where a sheet exists.

**Sheets used.** All three come from The Spriters Resource (TSR), read through Wayback Machine copies. The live TSR site returned HTTP 403 (Cloudflare bot check) for both HTML pages and direct PNG URLs. It was not bypassed.

| Short name | Character | Ripper (as written on the sheet) | Size | Page (Wayback) | PNG used (Wayback) |
|---|---|---|---|---|---|
| **S-RAY** | Ray Poward | Eckles D. Fum | 985×631 | [sheet 28048 page](https://web.archive.org/web/20230730182534/https://www.spriters-resource.com/genesis_32x_scd/contrahc/sheet/28048/) | [28048.png](https://web.archive.org/web/20230802021243im_/https://www.spriters-resource.com/resources/sheets/26/28048.png?updated=1460955832) |
| **S-RAY25** | Ray, Jan-2025 revision of the same sheet | — | 985×631 | — | [28048.png?updated=1738154899](https://web.archive.org/web/20250817003002im_/https://www.spriters-resource.com/resources/sheets/26/28048.png?updated=1738154899) |
| **S-SHE** | Sheena Etranzi | Eckles D. Fum | 934×423 | [sheet 27843 page](https://web.archive.org/web/20230730182540/https://www.spriters-resource.com/genesis_32x_scd/contrahc/sheet/27843/) | [27843.png](https://web.archive.org/web/20230802021250im_/https://www.spriters-resource.com/resources/sheets/25/27843.png?updated=1460955811) |
| **S-FANG** | Brad Fang | DJGameFreakTheIguana | 695×2322 | [sheet 27275 page](https://web.archive.org/web/2023/https://www.spriters-resource.com/genesis_32x_scd/contrahc/sheet/27275/) | [27275.png](https://web.archive.org/web/20230802021249im_/https://www.spriters-resource.com/resources/sheets/25/27275.png?updated=1460955759) |

- S-RAY25 is pixel-identical to S-RAY except for one added panel, "Unused content": 2 Ray sprites plus 2 small icons.
- Sizes match the dimensions stated on the archived pages.
- Below, "(own count, S-RAY)" means the sheet whose PNG link is in the table.

**Method.** All scripts ran with `python3 -I` from a scratch directory. Images were opened only as data. Nothing was copied into the repo.
- **Segmentation:** the background colours were removed (TSR green #00FF00, blue #0000FF and teal #008080; Fang's purple #20004A). Each sprite is an 8-connected component.
- **Split test (leg comparison):**
  - Two sprites are aligned on their bottom row.
  - The best horizontal shift is searched over ±25 px.
  - Rows are then counted upward from the soles while they stay **exactly identical**: same palette colour at every pixel, and same transparency.
  - A count of N rows means "the bottom N rows are the same art".
- **Torso test:** the rows above the waist are compared between frames of one aim set, with shifts of ±14 px horizontally and ±4 px vertically.
- **Barrel angles:** measured by tracing the 1-px staircase of the barrel edge in pixel dumps. A PCA line fit was used as a cross-check.
- **Spans:** outer opaque columns of the bottom 3 rows (feet), of rows below the waist (legs/stride), or of rows above the waist (torso and gun).
- **Fractions** are of each character's standing height H, in native pixels.

**Trustworthiness of the sheets.** They are fan rips assembled by hand, not ROM dumps, so frame order and baseline placement are the ripper's.
- **The rips are 1:1 with the game.** Ray's idle sprite is 40 px tall, exactly the video addendum's 40 px. His slide (24 px) and crouch-skid (31 px) sprite heights also equal the heights measured in video.
- **No prompt-injection text** was found in any page or sheet. The sheets contain only ripper credits and jokes. tcrf.net was not visited.

---

## 1. Construction: split torso over shared legs, or full body per angle?

### Takeaway
**Hard Corps uses a split construction for all three characters on the sheets.**
- Every aimed run frame uses pixel-identical leg art for the same cycle phase: forward, diagonal-up and diagonal-down (and Sheena's/Fang's gun-lowered run).
- The legs are the bottom **≈19 of 40 rows for Ray**, **17–22 of 37–38 for Sheena** and **mostly 22–24 of 46–47 for Fang**. The waist line therefore sits at **≈0.47–0.55 H above the soles**.
- Each aimed torso (diag-up, diag-down, Sheena's forward-firing run) is **one drawing reused over all 6 leg frames**, offset 1 px by the leg bob.
- The non-firing run has **4 distinct torso drawings over 6 leg frames** (arm swing).
- Standing has one leg drawing. It is shared by idle-forward and all four planted aim poses (diag-up, up, diag-down, down).
- The sheets show only composited full bodies; torso and leg pieces are not stored separately. The split is proven by pixel identity.

**Blazing Chrome: no sheet exists in any archive reached** (§6), so its split/full-body question remains undetermined.

### Cited Findings
**Ray (S-RAY)**

- **Run legs are shared across aims** (own count, [S-RAY](https://web.archive.org/web/20230802021243im_/https://www.spriters-resource.com/resources/sheets/26/28048.png?updated=1460955832); leg comparison method):
  - The sheet has three run rows of 6 frames each, all in the same phase order: "Running" (forward, gun level), and "Running while Aiming" diag-up and diag-down.
  - **Forward vs diag-up:** frame i of one matches frame i of the other on the **bottom 18–19 rows exactly** for i = 1…5. Frame 6 matches 19 rows except 1 stray pixel at row 2.
  - **Forward vs diag-down:** 9–11 identical rows. Above that, every mismatch is a pixel present only in the diag-down sprite, forming a 45° band: the gun barrel drawn over the thighs. The legs underneath are the same.
  - **Different phases** never match (0–1 rows). So there are **6 distinct leg drawings**, each phase-locked across the 3 aim sets.
- **Waist line** (own measurement, S-RAY): forward vs diag-up frame 1 is identical on rows 0–18 from the sole. Row 19 differs in 2 pixels (belt buckle colour) and row 20 differs in 12. The torso/leg seam is therefore **19–20 px above the soles of a 39–40 px sprite (≈0.48 H)**.
- **One torso drawing per aimed direction** (own measurement, S-RAY, torso method):
  - Diag-up torsos match each other within 0–5 px across all 6 frames.
  - Diag-down torsos match within 0–5 px.
  - Forward "Running" torsos fall into **4 distinct drawings**: frames 1=5, 2=4, 3 and 6 unique. Pairs differ by 89–176 px in the rear shoulder, arms and gun position.
  - **Bob:** the diag-up sprite top is 1 px lower in frames 3 and 6. Those are exactly the frames whose leg drawing is 39 rows instead of 40, so the torso rides on the leg height.
- **Standing legs are shared across all standing aims** (own count, S-RAY):
  - Idle-forward ("Idle" frame 1) vs planted diag-up ("Aiming" frame 1): bottom 20 rows identical except 3 pixels on the rear leg's inner edge.
  - Planted diag-up vs planted up: 21–23 rows identical.
  - Planted up vs planted diag-down/down: the legs are identical wherever the downward gun does not overlap them.
- The **"Idle"-labelled gun-vertical frames 2–4** share their bottom 8–13 rows. Each frame's upper body is the previous one shifted down 1 px. This is a 3-step body "sink" over static feet (own measurement, S-RAY).

**Sheena (S-SHE)**

- **Run legs** (own count, [S-SHE](https://web.archive.org/web/20230802021250im_/https://www.spriters-resource.com/resources/sheets/25/27843.png?updated=1460955811)): four run rows of 6 frames: "Running" (gun lowered), and "Running/Aiming" diag-up, diag-down and forward.
  - The ripper started each row at a different phase: gun-lowered frame 4 = diag-up frame 1 = forward-aim frame 2.
  - Matched by phase, gun-lowered, diag-up and forward-aim give 18 phase-matched pairs.
    - 12 of them share the **bottom 17–22 rows exactly**.
    - The other 6 share only 7–10 rows exactly, but 17–21 rows when ≤2 differing pixels per row are allowed (isolated pixel differences).
  - Diag-down shares 7–12 rows, with the gun overlapping above.
- **Torsos** (own measurement, S-SHE):
  - Diag-up: one drawing (0 mismatching pixels across 6 frames).
  - Diag-down: one drawing (≤3 px).
  - Forward-aim run: one drawing (≤1 px).
  - Gun-lowered run: 4 distinct drawings (frames 2=6, 3=5, 1 and 4 unique).
- **Standing** (own count, S-SHE): idle-forward legs match planted diag-up (19 rows) and planted up (22 rows). Planted diag-down matches 12 rows below the gun.

**Fang (S-FANG)**

- **Run legs** (own count, [S-FANG](https://web.archive.org/web/20230802021249im_/https://www.spriters-resource.com/resources/sheets/25/27275.png?updated=1460955759)): rows for run gun-low, diag-up, diag-down and forward-firing (5 frames, with muzzle flashes).
  - Phase-matched frames are identical on the **bottom 22–24 rows**, except one phase at 18 rows. Diag-down matches 15–16 rows, where the gun crosses the legs.
  - The firing-forward row has the same legs as the non-firing run.
- **Torsos** (own measurement, S-FANG):
  - Diag-up: one drawing (0 px mismatch over 6 frames).
  - Diag-down: one drawing (0 px).
  - Gun-low run: 4 distinct drawings (frames 1=5, 2=4, 3 and 6 unique).
- **Standing:** stand-aim-up and stand-fire-forward share their bottom 24 rows. The idle frame shares 17 of them (own count, S-FANG).

**Browny**
- No Browny sheet exists. The archived Hard Corps index lists only Fang, Ray and Sheena as playable characters ([TSR game index, Jul 2023](https://web.archive.org/web/20230730182534/https://www.spriters-resource.com/genesis_32x_scd/contrahc/)).
- The PAL *Probotector* page has robot sheets CX-1 to CX-3 only ([CX-2](https://web.archive.org/web/20211207000115/https://www.spriters-resource.com/genesis_32x_scd/probotector/sheet/39832/), [CX-3](https://web.archive.org/web/20211206233523/https://www.spriters-resource.com/genesis_32x_scd/probotector/sheet/39833/)). These were not analysed.

**Agreement with video:** the video addendum found that Ray's legs keep their 8-frame cycle through a mid-run forward→diag-up switch, with leg drawings shared across aims ([video addendum §5](hardcorps_blazingchrome_measured.md)). The sheet test confirms this and generalises it to Sheena and Fang.

### Inferences
- **Hard Corps reuses Contra NES's model:** shared, phase-locked leg cycle + per-aim upper body.
- **It extends that model in two ways:**
  - **Aimed torsos are a single static drawing per angle.** Only the non-firing run gets arm-swing variants.
  - **The standing pose is also split.** One stance serves idle and all planted aims.
- **Art budget per character (inferred):**
  - Run: 6 leg drawings, plus 1 torso each for forward-firing, diag-up and diag-down, plus 4 torsos for the non-firing run.
  - Stand: 1 leg drawing plus 5 torsos (forward, diag-up, up, diag-down, down).
- **For the comando (H = 128 px, two-handed heavy gun):**
  - Hard Corps' seam at ≈0.48 H maps to **≈61 px above the soles** (own calculation, 0.48 × 128).
  - A single static torso per aim angle is what Hard Corps shipped. At HD and 12 fps, a heavy gun probably still needs a small per-phase bob or sway layer. That is a design choice, not evidence.
- **Overlap rule:** for downward aims the gun is drawn over the shared legs. A split rig therefore needs the torso/gun layer ordered in front of the legs. Alternatively, a down-aim leg variant can be drawn.

### Gaps
- Whether the Genesis hardware stores the two halves as separate sprite pieces (VRAM/sprite-table layout) was not checked; the evidence is pixel identity in composites. No ROM, RAM or disassembly was used.
- Browny: no sheet.
- Blazing Chrome: no sheet (§6).

---

## 2. Aim angles drawn, barrel angles, and transition frames

### Takeaway
**Every drawn aim in Hard Corps is a multiple of 45°.** The diagonal barrels are clean 1:1 pixel staircases.
- The sheets contain **no in-between angles and no turn or transition frames**: aim snaps between poses.
- **Standing** has 5 aims per facing (forward, diag-up, up, diag-down, down).
- **Running** has 3 (forward, diag-up, diag-down).
- **Ceiling-hanging** has 5; **wall-climbing** has 8.
- **Prone and kneel** are forward only.
- **The jump** is a gunless curled ball in 4 orientations at 90° steps.

### Cited Findings
**Barrel angles** (own measurement):
- Ray, planted diag-up: the barrel's lower-left edge steps exactly 1 px left per 1 px down over 9 rows (y 30→38, x 794→786) = **45.0°** ([S-RAY](https://web.archive.org/web/20230802021243im_/https://www.spriters-resource.com/resources/sheets/26/28048.png?updated=1460955832)).
- Ray, run diag-up frame 1: 1:1 over 9 rows (x 409→401) = **45.0°**.
- Ray, run diag-down frame 1: the white barrel stripe steps +1 px per row over 7 rows = **−45.0°**.
- Ray, planted diag-down: the 4-px barrel stripe steps +1 px per row over 5 rows = **−45.0°**.
- A PCA cross-check on gun-coloured pixels near the muzzle gives 47–48° for the diag-up poses. That bias comes from the barrel thickness inside a small window.
- Ray, idle forward: the barrel occupies rows y 48–50 out to the muzzle at x 40, **0.9°** by PCA. Planted up and down: vertical columns, ±88–90°.
- Sheena, planted diag-up: 1:1 over 7 rows, **45°**. Sheena, planted diag-down: the barrel's outline end steps 1:1 over the 4 visible barrel rows, **−45°** ([S-SHE](https://web.archive.org/web/20230802021250im_/https://www.spriters-resource.com/resources/sheets/25/27843.png?updated=1460955811)).
- Fang, run diag-up: 1:1 over 8 rows, **45°** ([S-FANG](https://web.archive.org/web/20230802021249im_/https://www.spriters-resource.com/resources/sheets/25/27275.png?updated=1460955759)).

**Aim poses present per state** (own count; facing right; left = mirror):

| State | Ray (S-RAY) | Sheena (S-SHE) | Fang (S-FANG) |
|---|---|---|---|
| Standing / planted | fwd (= idle frame), diag-up, up, diag-down, down | fwd, diag-up, up, diag-down, down | fwd (firing row), up. No planted diagonal or down poses on this sheet. |
| Running | fwd (gun level), diag-up, diag-down | gun-lowered, fwd-aim, diag-up, diag-down | gun-low, fwd-firing, diag-up, diag-down |
| Prone / kneel | prone fwd, kneel fwd | prone ×2, kneel fwd | prone fwd (+4 prone-firing flash stages), crouch fwd + 2 crouch-punch |
| Jump | curled ball, 4 orientations, no gun pose | same | same |
| Ceiling hang | 5 aims (fwd, diag-up, up, diag-down, down) + 4 traverse | 5 aims + 3 traverse | not on sheet |
| Wall climb | 8 aims (all 45° steps, incl. backward) + 3 climb | 8 aims + 3 climb | not on sheet |

- **No intermediate angles** (e.g. 22.5°) and no aim-transition frames appear in any panel of the three sheets (own observation).
- **Mid-run aim switch:** the video addendum saw the switch happen within one 8-frame leg hold. The torso changed while the legs kept phase ([video addendum §5](hardcorps_blazingchrome_measured.md)). That is consistent with the absence of transition art.

### Inferences
- **Hard Corps reaches 8-way aim with only 45° art:** 5 standing torsos and 3 running torsos per facing, with no tweening.
- For the comando's heavy gun, 45° snaps without in-betweens are proven in this genre. A 1–2 frame transition would be an addition beyond these references, not a requirement.
- Genesis H40 pixels are non-square on a 4:3 display. A 1:1 staircase therefore displays slightly steeper than 45°. The exact pixel aspect was not sourced here.

### Gaps
- Bullet spawn offsets per pose: not on the sheets.
- Whether Type I (move-and-shoot mode) also uses the planted diag/up/down torsos when standing still: the sheet does not tie poses to modes. Video tied the diag-up and up planted poses to the "SHOT·II" HUD.

---

## 3. Widths vs height (stance, torso and gun, stride, crouch)

### Takeaway
**In Hard Corps the idle stance *is* the planted firing stance** (same leg drawing).
- **Feet span:** Ray **29 px = 0.73 H** (H = 40), Fang **26 px = 0.55 H** (H = 47), Sheena **19 px = 0.50 H** (H = 38).
- **Run stride max:** 0.72–0.78 H.
- **Kneel height:** 0.63–0.78 H.
- **Width with the forward gun:** ≈0.74–1.0 H.

The "wide stance" seen in Type II video is therefore Ray's normal standing stance, not a separate lock pose.

### Cited Findings
All values are own measurements on the sheets, in native px and as a fraction of H. Feet span = outer boot edges, bottom 3 rows. Stride = width of the leg rows below the waist. With-gun width = sprite bbox width.

| Measure | Ray ([S-RAY](https://web.archive.org/web/20230802021243im_/https://www.spriters-resource.com/resources/sheets/26/28048.png?updated=1460955832)) | Sheena ([S-SHE](https://web.archive.org/web/20230802021250im_/https://www.spriters-resource.com/resources/sheets/25/27843.png?updated=1460955811)) | Fang ([S-FANG](https://web.archive.org/web/20230802021249im_/https://www.spriters-resource.com/resources/sheets/25/27275.png?updated=1460955759)) |
|---|---|---|---|
| Standing height H (idle/fire forward) | **40** | **38** | **47** (stand-fire); idle frames 47/46/45 |
| Idle full width (incl. gun) | 40 (1.00 H) | 28 (0.74 H) | 35–38 (gun arm hanging) / 36 stand-fire (0.77 H) |
| Idle feet span | **29 (0.73 H)** | **19 (0.50 H)** | **26 (0.55 H)** |
| Planted aim stance feet span | **29 (0.73 H)**, all 4 planted poses, same legs as idle | **19 (0.50 H)**, all 4 | **26 (0.55 H)**, stand-up and stand-fire |
| Torso-with-forward-gun width (rows above waist) | 40 (1.00 H) | 28 (0.74 H) | 31 (0.66 H) stand-fire |
| Body width without a protruding gun (aim-up pose, rows above waist) | 21 (0.53 H) | 16 (0.42 H) | 24 (0.51 H) |
| Run sprite height | 39–40 (bob 1 px) | 37–38 | 45–47 |
| Run diag-up / diag-down sprite height | 46–47 / 39–40 | 40–41 / 35–36 | 53–54 / 47–48 |
| Run stride max (leg rows) | **31 (0.78 H)** | **28 (0.74 H)** | **34 (0.72 H)** |
| Run frame width incl. gun | 38–46 | 26–35 | 22–40 (gun low), 36–50 firing |
| Kneel/crouch height | **31 (0.78 H)**, 40 wide | **24 (0.63 H)**, 29 wide | **35 (0.74 H)**, 32–48 wide |
| Prone (w×h) | 53×16 (1.33×0.40 H) | 41×14 and 40×16 | 59×18 (1.26×0.38 H) |
| Slide pose (w×h) | 48×24 | not identified | not on sheet |
| Jump ball (w×h) | 24×20 (0.60×0.50 H) | 19×18 | 30×24 |
| Planted aim-up height (gun tip) | 55 (1.38 H) | 48 | 62 |

- **Muzzle position, Ray idle-forward** (own measurement, S-RAY):
  - Barrel centre is 26 px above the soles (**0.65 H**).
  - Muzzle tip is 24 px ahead of the stance centre (**0.60 H**).
- **Ray's "Idle"-labelled gun-vertical frames:** narrow legs-together stance, feet span **14 px (0.35 H)**, 53–55 px tall including the gun (own measurement, S-RAY).
- **Cross-check against video** ([video addendum §1, §4](hardcorps_blazingchrome_measured.md)): video gave Ray as 40 px tall and 41 px wide with the gun; the sheet gives 40×40. Video's slide pose is 24 px tall and its crouch-skid 31 px; the sheet has a 48×24 and a 40×31 sprite.

### Inferences
- Ray's 0.73 H stance is the wide, heavy-weapon stance. It is the closest Hard Corps analogue to the comando. Scaled to 128 px:
  - feet span ≈ 93 px;
  - stride max ≈ 100 px;
  - kneel ≈ 100 px tall;
  - forward muzzle ≈ 83 px above the soles and ≈ 77 px ahead of the stance centre.
  (Own calculation, ×3.2.)
- Hard Corps does **not** widen the stance for planted/locked fire: idle and lock share legs. If the comando wants a visible "brace" when locking, that is a change from Hard Corps, and the previous video notes suggest Blazing Chrome may do it.
- Sheena (0.50 H) and Fang (0.55 H) show the stance width varies by character archetype.

### Gaps
- Browny: no sheet.
- Fang: no planted diagonal or down poses on the sheet.
- Spans are in native pixels. On-screen proportions depend on the Genesis pixel aspect, which was not sourced.

---

## 4. Frames per animation (sheet counts)

### Takeaway
**Hard Corps run cycle:**
- **6 leg drawings** per character.
- Combined with the video's 8 frames per drawing, this closes Ray's run cycle at **48 frames (0.80 s)**.

**Idle:**
- A **single static forward frame**.
- Each sheet also has a 3-frame "Idle"-labelled pose whose purpose is unconfirmed.

**Jump:**
- A curled ball in **4 orientations**, built from 1–2 drawings plus H+V flips.

**Other states:**
- **No separate fall or landing frames** on any sheet.
- **No body recoil frames**: Fang's firing rows change only the muzzle flash.

### Cited Findings
Own counts on each sheet. Ripper panel labels are in quotes. Purposes not stated by the ripper are marked *(inferred)*.

**Ray** ([S-RAY](https://web.archive.org/web/20230802021243im_/https://www.spriters-resource.com/resources/sheets/26/28048.png?updated=1460955832))
- **"Idle": 4 sprites.**
  - Frame 1: standing aim forward, 40×40.
  - Frames 2–4: frontal pose, gun held vertical at the side, narrow feet. The upper body sinks 1 px per frame.
  - Frames 2–4 are a breathing/idle loop, an intro pose or the stand-aim-up *(inferred; unconfirmed)*. The video addendum saw 300+ static frames with no idle animation.
- **"Running": 6.**
- **"Running while Aiming": 12** = 6 diag-up + 6 diag-down.
- **"Aiming": 4** planted (diag-up, up, diag-down, down).
- **"Jumping": 4** orientations.
  - Frames 2 and 3 are exact 90° and 270° rotations of frame 1.
  - Frame 4 is the H+V flip of frame 1.
  - Pixel test: 0 mismatches for each.
- **"Duck/Slide": 3**:
  - prone 53×16 *(inferred: prone fire)*;
  - 48×24 *(inferred: slide body, matching the 24-px slide pose in video)*;
  - kneel 40×31 *(inferred: crouch/skid, matching the 31-px crouch skid in video)*;
  - plus 3 dust puffs.
- **"Defeated": 6.**
- **"Hanging": 9** = 4 traverse + 5 aims *(ceiling/rail hang, arms overhead)*.
- **"Climbing": 11** = 8 aims + 3 climb.
- **"Slopes": 4.**
- **"Misc"**: portrait, map figure, art.
- **S-RAY25** adds "Unused content": 1 forward stance and 1 aim-up sprite, not analysed.

**Sheena** ([S-SHE](https://web.archive.org/web/20230802021250im_/https://www.spriters-resource.com/resources/sheets/25/27843.png?updated=1460955811))
- **"Idle": 4.**
  - Frame 1: aim forward, 28×38.
  - Frames 2–4: gun held diagonally across the body, hair moving between frames *(inferred: idle loop; unconfirmed)*.
  - Frame 2 has the idle legs (21 rows identical). Frames 3–4 share only their bottom 4–6 rows with it, so the legs are partly redrawn.
- **"Aiming": 4** (diag-up, up, diag-down, down).
- **"Running": 6** (gun lowered).
- **"Running/Aiming": 18** = 6 diag-up + 6 diag-down + 6 forward.
- **"Jumping": 4.** Exact 90° rotations, and frame 3 = H+V flip of frame 1.
- **"Defeated": 7.**
- **"Hanging": 8** = 3 traverse + 5 aims.
- **"Climbing": 11** = 8 aims + 3 climb.
- **"Ducking/Sliding": 3** (41×14, 40×16, kneel 29×24).
- **"Slopes": 4.**

**Fang** ([S-FANG](https://web.archive.org/web/20230802021249im_/https://www.spriters-resource.com/resources/sheets/25/27275.png?updated=1460955759))
- The sheet has no panel labels. Rows are listed top to bottom.
- **Idle and standing:**
  - Idle: 3 (gun arm hanging, body 47→46→45 px tall, i.e. a breathing loop *(inferred)*).
  - Stand aim-up: 1, plus aim-up firing: 4 flash stages.
  - Stand fire forward: 5. The body is static; only the flash changes: none → 3 growing stages → sparks.
- **Running:**
  - Run, gun low: 6.
  - Run diag-up: 6, plus firing 6.
  - Run diag-down: 6, plus firing 6.
  - Run forward firing: 5 (the ripper omitted one phase).
- **Prone and crouch:**
  - Prone: 1, plus prone firing: 4.
  - Crouch: 3 (crouch-forward and 2 crouch-punch).
- **Jump: 4, plus 4 jump-firing.**
  - Frame 3 = exact H+V flip of frame 1, and frame 4 = H+V flip of frame 2.
  - Frame 2 is a 90° rotation of frame 1 except 16 pixels, i.e. a separately drawn second curl.
- **Weapons and other:**
  - Death: 7.
  - Punch rows (wind-up + punch, ×3 variants) *(inferred: Power Punch)*.
  - A ≈34-frame standing loop with sparkles *(inferred: Psychic Blaster charge)*.
  - Flamethrower and explosion effects.
- **Fang has no slide, hang or climb frames on this sheet.**
- The ripper's note says the sheet was made for a fan project and is not 100% done.

**Timing (from the earlier video notes, combined with the counts above):** Ray's leg drawing changes every 8 frames ([video addendum §6](hardcorps_blazingchrome_measured.md)). With 6 drawings per cycle (own count, S-RAY), that gives **48 f per cycle = 0.80 s at 59.92 Hz**, and **96 px per cycle (2.4 H)** at 2 px/f (own calculation).

### Inferences
- **Hard Corps uses Contra NES's somersault economy**: 2 curl drawings (or 1 drawing plus its 90° rotation) and H+V flips for the other two orientations. No per-angle air aim poses are drawn.
- **A Hard Corps-style comando set, per facing:**
  - Run: 6 leg drawings, 3 aimed torsos and 4 swing torsos.
  - Stand: 1 stance and 5 torsos.
  - Plus kneel, prone, slide, 2 curl drawings and 6–7 death frames.
  - Firing feedback via a separate muzzle-flash object (4–5 stages), not body recoil.

### Gaps
- **Not on any sheet:**
  - somersault and idle-loop timing;
  - fall and landing frames (the video saw only a ≈4 f positional settle);
  - Type II-specific frames;
  - whether the 3-frame "Idle" loops actually play in normal gameplay.

---

## 5. Teeter / balance and ledge-hang frames

### Takeaway
**None of the three Hard Corps sheets contains a teeter, balance or ledge-grab frame.**
- Ray and Sheena have **ceiling/rail-hang** sets (traverse + 5 aims) and **wall-climb** sets (climb + 8 aims).
- Both also have 4 **slope** stances.
- Fang's sheet has none of these.

### Cited Findings
- Ray: "Hanging" 9 sprites with arms overhead, "Climbing" 11, "Slopes" 4. No balance pose (own observation, [S-RAY](https://web.archive.org/web/20230802021243im_/https://www.spriters-resource.com/resources/sheets/26/28048.png?updated=1460955832)).
- Sheena: "Hanging" 8, "Climbing" 11, "Slopes" 4. No balance pose (own observation, [S-SHE](https://web.archive.org/web/20230802021250im_/https://www.spriters-resource.com/resources/sheets/25/27843.png?updated=1460955811)).
- Fang: none (own observation, [S-FANG](https://web.archive.org/web/20230802021249im_/https://www.spriters-resource.com/resources/sheets/25/27275.png?updated=1460955759)).

### Inferences
- **Edges:** like Contra NES (no teeter), Hard Corps appears to handle edges without a dedicated animation.
- **Hang/climb art:** the hang and climb sets add a full aim set each, which is a major cost driver in Hard Corps beyond running and standing.

### Gaps
- The sheets may be incomplete, so absence on a sheet is not proof of absence in the game.
- Edge overhang tolerance would still need stage footage.

---

## 6. Blazing Chrome: sheet availability and what could be determined

### Takeaway
**No Blazing Chrome player sprite sheet was found** on The Spriters Resource (live or archived) or elsewhere. The split vs full-body test could not be run for Mavra or Doyle.
- The video-based facts in the earlier notes stand:
  - 6-drawing / 33 f run;
  - wide planted lock stance for diag-up;
  - static idle;
  - upright tucked jump.
- One Steam screenshot gives Mavra's aim-up stance as **≈14 native px between the outer edges of the visible boot pixels (≈0.33 H)**. Confidence is low.

### Cited Findings
- **Wayback CDX** returned **no captures** of any TSR page whose slug starts with "blazingc" under `pc_computer`, `nintendo_switch`, `playstation_4`, `xbox_one` or `arcade`. Example query: [CDX pc_computer/blazingc*](https://web.archive.org/cdx/search/cdx?url=spriters-resource.com/pc_computer/blazingc*&output=txt).
  - The same prefix query does list neighbours such as "blazingangels…" and "blazingbeaks" ([CDX pc_computer/blazing*](https://web.archive.org/cdx/search/cdx?url=spriters-resource.com/pc_computer/blazing*&output=txt)).
  - The live TSR site returned HTTP 403 (Cloudflare bot check, not bypassed).
- **Web searches** for Blazing Chrome sprite rips or sheets returned nothing relevant (searched 2026-10-15).
- **JoyMasher's own pages** carry no sprite images. The [Blazing Chrome page](https://joymasher.com/blazing-chrome/) has only the logo. The [alpha post](https://joymasher.com/blazing-chrome-alpha/) has comic-style "BC_color" pages.
- **Mavra's aim-up stance from a screenshot** ([Steam `ss_43152195…`](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/609110/ss_43152195858e33f3cd9d0a5fe2ec2dfa104a91f5.1920x1080.jpg), 1920×1080 JPEG; own measurement on a 4.5-px native grid):
  - The visible boot pixels span ≈62 screen px ≈ **14 native px**. Black outlines merge with the black floor, so the true span may be ≈16 px.
  - The hair-to-sole height is ≈180 screen px ≈ 40 native px.
  - That gives a feet span of **≈0.33–0.37 H**. Confidence: **low**.
  - Doyle's forward-fire stance in [`ss_add23d42…`](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/609110/ss_add23d42e3ed124f284ffd1ec893b338ebc6f942.1920x1080.jpg) could not be measured: his legs are dark on a dark background and partly occluded.
- **Facts from the earlier video notes** (not new): Mavra ≈43–44 px tall; run = 6 drawings / 33 f; a planted wide stance for diag-up while locked; static idle for 190 f ([video addendum §1, §5, §6](hardcorps_blazingchrome_measured.md)).

### Inferences
- If Mavra's normal aim-up stance is ≈0.33–0.37 H wide while her lock diag-up stance is visibly wide, Blazing Chrome would widen the stance for the lock. Hard Corps does not.
  - Weak support: one screenshot measurement plus one video observation.
  - No pixel test supports it.
- Whether Blazing Chrome is split or full-body stays **undetermined**.

### Gaps
- **Blazing Chrome construction, frame counts per state, aim angles, recoil and stance widths:** all need either a sprite rip (none found) or lossless frame-stepping of footage, which this pass did not do (no browser, images only).
  - The decisive test is the same leg-pixel comparison run on two run frames at the same phase with different aims.
  - Lossless captures (PNG from the PC version at native 427×240) would be needed. YouTube's JPEG/H.264 frames would only support approximate mask comparison, as in the earlier video addendum.

---

## 7. Compact summary table

### Takeaway
Hard Corps is a **split** game for all three characters on the sheets:
- 6 shared leg drawings per run cycle;
- 1 stance shared by idle and planted aims;
- one static torso per aimed direction;
- all aims at 45° multiples, with no transition frames.

Blazing Chrome could not be tested from sheets.

### Cited Findings
Sources: [S-RAY](https://web.archive.org/web/20230802021243im_/https://www.spriters-resource.com/resources/sheets/26/28048.png?updated=1460955832), [S-SHE](https://web.archive.org/web/20230802021250im_/https://www.spriters-resource.com/resources/sheets/25/27843.png?updated=1460955811), [S-FANG](https://web.archive.org/web/20230802021249im_/https://www.spriters-resource.com/resources/sheets/25/27275.png?updated=1460955759) (own counts and measurements, §1–§5). Blazing Chrome column: [video addendum](hardcorps_blazingchrome_measured.md) and the §6 screenshot. "n/s" = no sheet.

| | Ray (HC) | Sheena (HC) | Fang (HC) | Browny (HC) | Mavra / Doyle (BC) |
|---|---|---|---|---|---|
| Height H | 40 px | 38 px | 47 px | n/s | Mavra ≈43–44 px (video) |
| Idle feet span | 29 px = 0.73 H | 19 px = 0.50 H | 26 px = 0.55 H | n/s | Mavra aim-up ≈14–16 px ≈ 0.33–0.37 H (screenshot, low) |
| Planted / lock stance span | 29 px = 0.73 H (same legs as idle) | 19 px = 0.50 H (same legs) | 26 px = 0.55 H (stand-up/fire) | n/s | "wide" (video, not measured) |
| Aims drawn: stand | fwd, diag-up, up, diag-down, down | same 5 | fwd, up (sheet incomplete) | n/s | fwd, up, diag-up (video and screenshots) |
| Aims drawn: run | fwd, diag-up, diag-down | gun-low, fwd, diag-up, diag-down | gun-low, fwd-fire, diag-up, diag-down | n/s | fwd, diag-up (video/screenshot) |
| Aims drawn: air | ball, no gun (4 orientations) | same | same | n/s | upright, fwd seen (video) |
| Aims drawn: other | prone/kneel fwd; hang 5; climb 8 | prone/kneel fwd; hang 5; climb 8 | prone/crouch fwd | n/s | prone after roll (video) |
| Barrel angles | 0/±45/±90°, 1:1 staircases, no in-betweens | same | 45° checked | n/s | not measurable |
| Construction | **Split.** Legs shared on the bottom 19 rows (0.48 H); 1 torso per aim; 4 swing torsos for the plain run | **Split.** 17–22 rows (≈0.5–0.55 H) | **Split.** 18–24 rows, mostly 22–24 (≈0.5 H) | n/s | **Undetermined** |
| Idle frames | 1 static (+3 "Idle" gun-vertical, purpose unconfirmed) | 1 (+3 hair-loop, unconfirmed) | 3 (breathing, inferred) | n/s | static (video) |
| Run frames | 6 per aim set (48 f cycle at 8 f/drawing) | 6 per set | 6 per set | n/s | 6 drawings / 33 f (video) |
| Jump frames | 4 orientations = 1 drawing + 90° rotation + H+V flips | same | 2 drawings + H+V flips | n/s | 1 tucked pose (+ hair change, video) |
| Shoot / recoil | no recoil frames on sheet | none on sheet | body static; 4–5 muzzle-flash stages | n/s | nm |

### Inferences
**"nf"/"nm" cells this file fills in the earlier notes:**
- **Main file §8:**
  - "Sprite construction" for Hard Corps: split; legs shared at ≈0.48 H; per-aim static torsos.
  - "Frames / timing" for Hard Corps: run 6 drawings / 48 f; jump 4 orientations; idle static plus an unconfirmed 3-frame pose.
- **Video addendum §6:** "Ray's full run-cycle length" is closed at 6 drawings / 48 f.
- **Both files:** Sheena and Fang now have size and construction data.

**For the comando:** Hard Corps is the cleanest precedent for the split body.
- The comando's heavy-gun look could add a wider lock stance (as Blazing Chrome seems to). It could also add a per-phase torso bob, which Hard Corps only does for the non-firing run.

### Gaps
- Browny (no sheet).
- Blazing Chrome sheets: none exist in the archives reached.
- Hard Corps fall/landing frames, somersault timing, and Type II-specific frames: not on the sheets.
