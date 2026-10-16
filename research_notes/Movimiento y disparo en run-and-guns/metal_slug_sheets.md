# Metal Slug 1 / 2 / X / 3 player sprite sheets (Marco, Tarma, Eri, Fio): frame counts, torso/legs split, aim angles, widths

These notes extend `metal_slug.md`. They come from my own counts and pixel measurements on The Spriters Resource rips, read through the Wayback Machine.

**Access.** The live site sits behind a bot check, so I did not use it. I took the sheet IDs from Wayback copies of the game listings:
- [Metal Slug listing][lms]: Marco 11225, Tarma 11254
- [Metal Slug 2 / Metal Slug X listing][lms2]: Marco 11223, Tarma 11256, Eri 11231, Fio 36307
- [Metal Slug 3 listing][lms3]: Marco 11226, Tarma 11258, Eri 11233, Fio 36308

There is no separate MSX page: MS2 and MSX share one listing. Marco 11223 had no Wayback capture (CDX query returned nothing).

**Sheets used.** The short names below are links to the exact Wayback PNG/GIF that I measured:

| Short name | Sheet | Size | Notes |
|---|---|---|---|
| [M11225][m25] | Marco, MS1 listing (2023 capture) | 1818×17959 | |
| [M11226][m26] | Marco, MS3 listing (2025 capture) | 1818×17959 | Same composite as M11225. 1.02 M pixels differ, all in added labels, split MS1/MS2 variant rows and later sections (own diff). Coordinates below hold for both. |
| [T11254][t54] | Tarma, MS1 listing | 1841×11171 | |
| [T11258][t58] | Tarma, MS3 listing | 1841×11171 | Byte-identical to T11254 (same MD5). |
| [E11231][e31] | Eri, MS2/X listing (2020 capture) | 1839×9249 | |
| [E11233][e33] | Eri, MS3 listing | 568×8041 | Older, smaller rip. Downloaded, not analyzed. |
| [F36307][f07] | Fio, MS2/X listing (2024 capture) | 1870×16724 | |
| [F36308][f08] | Fio, MS3 listing | 1278×5179 GIF | Older rip. Downloaded, not analyzed. |

These are fan rips. Labels such as "MS1", "MS2", "UNUSED", "USED IN MS1", "ADDED IN MSX" and "MS3" are the ripper's annotations; I report them as written and did not verify them.

**Methods**
- **Frame boxes:** bounding box of non-background pixels. Frames are split where 3 or more empty columns separate them, and rows are split by empty pixel rows. Coordinates are sheet pixels. Marco's sheet has two columns; all Marco y-values refer to the left column (x < 905).
- **Barrel angles:** I fitted a line to the barrel pixels by principal-axis fit (PCA). The convention is 0° = facing direction, +90° = straight up, −90° = straight down.
  - HMG: I fitted the two palette colours used only by the gun (#383008, #706038). A highlight overlay confirmed they cover only the gun. This colour pair is shared by all four characters. The gun is about 20 px long, so uncertainty is about ±3°.
  - Pistol: I fitted outline and gun colours inside a hand-drawn region around the pistol. The pistol is only 9–12 px long. A second method (dark pixels in the same region) differed by up to 10°, so treat pistol angles as **±8–10°**.
- **Torso/legs overlap:** for each character I found the placement of the idle torso and idle legs pieces that best matched the side-view full-body standing frame. Those full-body frames are redrawn, so only 46–61% of pixels matched exactly; offsets are ±1 px.

[m25]: https://web.archive.org/web/20230512095229/https://www.spriters-resource.com/resources/sheets/11/11225.png
[m26]: https://web.archive.org/web/20250815142830/https://www.spriters-resource.com/resources/sheets/11/11226.png
[t54]: https://web.archive.org/web/20190701220147/https://www.spriters-resource.com/resources/sheets/11/11254.png
[t58]: https://web.archive.org/web/20250815110054/https://www.spriters-resource.com/resources/sheets/11/11258.png
[e31]: https://web.archive.org/web/20200418233524/https://www.spriters-resource.com/resources/sheets/11/11231.png
[e33]: https://web.archive.org/web/20191208152316/https://www.spriters-resource.com/resources/sheets/11/11233.png
[f07]: https://web.archive.org/web/20240525085203/https://www.spriters-resource.com/resources/sheets/34/36307.png
[f08]: https://web.archive.org/web/20230731132948/https://www.spriters-resource.com/resources/sheets/34/36308.gif?updated=1460956958
[lms]: https://web.archive.org/web/20231208102127/https://www.spriters-resource.com/neo_geo_ngcd/ms/
[lms2]: https://web.archive.org/web/20240204014639/https://www.spriters-resource.com/neo_geo_ngcd/ms2/
[lms3]: https://web.archive.org/web/20231202180839/https://www.spriters-resource.com/neo_geo_ngcd/ms3/

---

## 1. Aim angles and transition frames (pistol and HMG)

### Takeaway
**The pistol** fires along only three axes: forward, up, and down (down only while airborne). Every in-between angle appears only in non-firing transition or recoil frames:
- forward-to-up transition: 2 frames
- forward-to-down transition: 3 frames
- The "aim-up" idle does not point straight up. It holds the pistol at **≈62–74°**, and the gun snaps to ≈90° only when it fires.

**The HMG** has **two firing intermediate angles per quadrant**. Each angle has two muzzle-flash variants, ordered shallow, steep, steep, shallow. The angles differ by character and by game:
- **Marco and Tarma (MS2 and later):** **+26° and +55°** up; **−32° and −74°** down.
- **Marco in MS1:** +26° and **+62°** up; −32° and **−63°** down.
- **Eri and Fio (one shared gun drawing):** **+49° and +60°** up; **−29° and −61°** down. The female sweep therefore has a large gap between forward (≈0–10°) and the first diagonal (49°).

### Cited Findings
**Pistol, Marco** (own measurement, sheet [M11225][m25], identical rows in [M11226][m26])
- Idle low-ready (4 idle torso frames, y263): barrel at −45°, −40°, −33°, −29°. The pistol idles pointing down-forward.
- Shoot forward (10 frames, y1046), measured in order:
  - frames 1–3, muzzle flash inside the frame: +2°, +8°, +13°
  - frames 4–5, recoil: +29°, +34°
  - frames 6–10, settling back to low-ready: +10°, −8°, −19°, −20°, −35°
  - A second 10-frame row at y1080 carries the ripper's label "USED WHEN JUMPING FOWARD" [sic] and has the same widths (own count).
- Forward-to-up transition. The ripper labels split by game:
  - MS2 and later, row y1369 (2 frames): −24°, then +35°. A dark-pixel cross-check gives −15° and +37°.
  - MS1, row y1476, labelled "MS1" (2 frames): +46°, +59°.
  - Row y1513 is a copy of y1476 labelled "MS2 UNUSED". This corrects `metal_slug.md`, which called both the y1476 and y1513 rows UNUSED.
- Aim-up hold (4-frame breathing loop, y1400):
  - Colour-region fit: 66° on frame 1.
  - Connected-component fit on all four frames: 62°, 63°, 68°, 74°.
  - So the gun is held about 20–28° short of vertical.
- Shoot up (10 frames, y1550). Muzzle flashes are separate small sprites placed above frames 1–3.
  - Frames 1–6 (colour-region fits): +89°, +94°, +115°, +126°, +126°, +103°. The recoil tips the gun **back over the head** by up to 36° past vertical.
  - Frames 7–10 (component fits): 95°, 84°, 78°, 75°, returning toward the hold.
- Single full-body "aim up" frame, 23×40 (y1431). A full-body shoot-up frame, 19×56, is labelled UNUSED (y1621).
- Forward-to-down transition, air only (3 frames):
  - MS1 (y2183): −52°, −78°, −86°
  - MS2 (y2227): −37°, −66°, −86°
- Shoot down (6 frames, y2267; flash sprites under frames 1–3): −86°, −77°, −59°, −30°, −64°, −83°. Recoil swings the barrel forward by up to 56°.

**Pistol, Fio** (own measurement, sheet [F36307][f07])
- Region fits were unreliable for Fio (elongation < 2, the forearm got included). The values below come from 2-point muzzle-to-slide-rear readings on a pixel-grid zoom, ±8°:
  - up transition (y1523, 2 frames): ≈ −17°, +36°
  - aim-up hold (y1550, 4 frames): ≈ 69°. A dark-pixel region fit gave 82°.
  - down transition (y2362, 3 frames): ≈ −48°, −69°, −86°. A dark-pixel fit gave −48°, −80°, −91°. The y2404 row has the same 3-frame structure.
- Fio's structure matches Marco's (own count): 2 up-transition frames, a 4-frame hold, a 10-frame shoot-up, 3 down-transition frames and a 6-frame shoot-down.

**Pistol, Tarma** (own measurement, sheet [T11254][t54], connected-component fit; contaminated by the forearm, ±10°)
- Up transition (y770): −21°, +30°.
- Down transition (y802): −55°, −68°, then a separate −86° frame.
- Same structure as Marco.

**HMG, Marco** (own measurement, sheet [M11225][m25]; gun-colour PCA, ±3°)
- **Idle (4 frames, y3196):** −4°, −9°, −13°, −15°. The idle bob is in the gun angle.
- **Rifle idle fidgets:** 12 (y3230), 8 (y3267), 18 (y3310) and 16 (y3351) frames. Angles range from −4° to −29°.
- **Run torso (12, y3388):** −5° to −18°.
- **Fire forward (4 frames, flash drawn into the frame, y3659):** −4°, +3°, −12°, −8°. That is ±8° of recoil jitter; frame 3 also contains a smoke smear.
- **Follow-through (10 frames, y3692):** −4° to +6°.
- **Aim-up transition, not firing (2 frames, y4010):** +26°, +47°.
- **Aim-up hold (4 frames, y4049):** +61°, +62°, +68°, +61°. The hold is **not vertical**.
- **Single full-body up frame (y4090, 23×47):** +77°.
- **Fire up (4 frames, y4142):** +86°, +95°, +86°, +75°.
- **Up recovery (6 frames, y4219):** +104°, +98°, +91°, +89°, +73°, +67°. It returns to the hold angle.
- **Another 10-frame up row (y4596):** +86° → +104° → +86°. I could not identify its purpose.
- **Diagonal-up firing (4 frames: shallow, steep, steep, shallow):**
  - MS1 (y4362): **+26°, +62°, +62°, +26°**
  - MS2 (y4430): **+26°, +55°, +55°, +26°**
  - The two frames at each angle are pixel-identical in the gun and differ only in the flash (own observation).
- **Diagonal-up, not firing (2 frames):** MS1 (y4498) +26°, +62°; MS2 (y4547) +26°, +55°.
- **Down transition (3 frames):** MS1 (y5587) −32°, −63°, −83°; MS2 (y5634) −32°, −74°, −90°.
- **Fire down (4 frames, y5683):** −83°, −79°, −81°, −91°.
- **Diagonal-down firing (4 frames):** MS1 (y5751) **−32°, −63°, −63°, −32°**; MS2 (y5816) **−32°, −74°, −74°, −32°**.
- **Down-hold sway (7 frames, y5881):** MS1 −79° → −64° → −79°. In [M11226][m26] an MS2 variant sits beside it at −86° → −68° → −86°.
- **Down recovery (6 frames, y5926):** MS1 −79°, −68°, −55°, −64°, −65°, −72°; MS2 −86°, −71°, −59°, −68°, −72°, −79°.
- **Full-circle rows labelled "UNUSED"** (y6070 and y6180 firing, 11 frames each; y6294 not firing, 11 frames). The body faces forward while the gun goes all the way round:
  - forward and down: −4°, −32°, −63°, −83°
  - down-back: −112°, −147°
  - straight back: −177.5°
  - up-back: +154°, +124°
  - up: +26°, +62°
- **Rows with spiky, blown-back hair** (y3795, 6 frames; y4799, 4; y5123, 6; y5971, 6; y6019, 4). In the 2025 revision [M11226][m26], y4799 and y6019 carry an "MS6" label, so at least those are outside MS1–3. I did not check labels on the other three rows.

**HMG, Tarma** (own measurement, sheet [T11254][t54])
- The gun pixels are identical to Marco's MS2 drawings: the PCA values match to 0.1°.
  - diagonal firing: +26°, +55° and −32°, −74° (y2621, y2703)
  - up transition +26°, +47°, then hold +61° to +68° (y2393)
  - fire up +86°, +95°, +86°, +75°
  - fire down −90°, −86°, −87°, −98°
- Tarma's sheet also has back-angle frames (y2393: +124°, +154°; y2452: −112°, −147°; y2778: −112°, −147°, −177°, +175°, −170°) without an "unused" label. This sheet has no usage labels at all.

**HMG, Eri and Fio** (own measurement, sheets [F36307][f07] and [E11231][e31]; the PCA values are identical across the two sheets, so both use the same gun drawing)
- Idle: Fio y3238 +1°, +1°, −3°, −5°; Eri y1887 −5°, −3°, +1°, +1°.
- Fire forward (Fio y3615): +3°, ≈+10°, +5°, +1°.
- **Aim-up transition (2 frames):** +49°, +57° (Fio y4184; Eri y2287).
- **Aim-up hold (4 frames):** +59°, +56°, +54°, +55°. Fio has three rows of it, labelled MS2 (y4217), **MS3** (y4253) and MS5 (y4289), all with identical angles.
- Fire up (Fio y4377): +88°, +96°, +86°, +80°. Recovery (y4452): +107° → +80°.
- **Diagonal-up firing (Fio y4590; Eri y2508):** **+49°, +60°, +60°, +49°**. The not-firing pair is +50°, +59° (Fio y4653).
- **Down transition (Fio y5682; Eri y2334):** −29°, −61°, −88°.
- **Fire down (Fio y5730):** −88°, −88°, −88°, −99°.
- **Diagonal-down firing (Fio y5801; Eri y2585):** **−29°, −61°, −61°, −29°**.
- **Down-hold sway (Fio y5865, 7 frames):** −84° → −68° → −84°.
- Rows where the gun droops (Fio y3646, 10 frames, labelled "MS2"; y3730, 13 frames, labelled "MS5 UNUSED"):
  - The gun goes −5° → −45° and holds at −41°.
  - Interpretation, unverified: this is the female "tired arms" animation after sustained HMG fire, which [Shmuplations](https://shmuplations.com/?p=19321) describes.

### Inferences
- **The pistol never fires at an intermediate angle.** Every frame with a flash is near 0–13°, +89–94° or −86°. The transition frames (2 up, 3 down) carry no flash.
- **The HMG sweep has 4 firing poses per quadrant:** forward, two diagonals, and vertical. Each pose has 2 flash variants. A forward-to-up sweep can therefore show up to 4 distinct barrel angles while firing.
  - Males: about −4°, 26°, 55°, 90°.
  - Females: about +3°, 49°, 60°, 90°.
- **Up-aim idles are deliberately short of vertical,** for both weapons and all characters (pistol ≈62–74°, HMG 54–68°). Firing frames snap to ≈90°, and recovery frames ease back to the hold angle.
- **The down-aim torso is airborne-only,** as far as the sheets can tell. The down-aim and shoot-down torsos are hunched forward over the gun and have no crouch counterpart: pressing down on the ground selects the full-body crouch set. This matches the airborne-only down shot documented in `metal_slug.md` (Sega Retro), but the sheets themselves do not say so.
- **For the comando:** copying MS2's male set gives 7 HMG firing angles across the front half-circle: −74°, −32°, 0°, +26°, +55°, +90° and down −90°. Each needs 2 flash variants. Add 2-frame non-firing transitions and an up-hold at about 60–65°.

### Gaps
- The sheets carry no timing, so I could not tell how many 30 Hz ticks each diagonal pose holds, or whether bullets leave at the pose angle.
- The usage of the back-angle (+124° to −177°) frames is uncertain. They are labelled "UNUSED" on Marco's sheet but unlabelled on Tarma's, and this was not checked in gameplay.
- I did not measure pistol angles on Eri's sheet.
- Pistol angles are only ±8–10° because the guns are 9–12 px long.

---

## 2. Body split: separate pieces, waist join, overlap, seam, whole-body states

### Takeaway
All four characters are built from a **torso piece** and a **legs piece**.

Marco and Tarma:
- torso 29 px + legs 16 px, on a ≈38 px standing figure
- the torso overlaps the legs by **≈7 px** (8 px if the figure is 37 px tall)
- the legs piece starts **16 px above the feet (0.42 H)**; the torso piece ends **9 px above the feet (0.24 H)**

Eri and Fio:
- the legs piece is **24 px tall**, with the hips starting about 18 px above the feet and a narrow strip at the back reaching 24 px
- the torso piece ends **8 px above the feet**
- the geometric overlap is **≈14–16 px**

In both cases the torso piece carries the vest or shirt hem plus the forearms and gun, held across the hips, and these cover the join.

The rifle (HMG/special-weapon) sections contain **no leg rows**, so legs are shared across weapons. Whole-body states: crouch (all actions), kick, turnaround, deaths, a few standing transitions, and the transformation/vehicle sections.

### Cited Findings
**Piece sizes and offsets**
- **Marco** (own measurement, sheet [M11225][m25]):
  - Idle torso 29×29 (x10–38, y263). Idle legs 21×16 (x149–169, y276).
  - Best placement of the legs inside the full-body standing frame (y693, 29×37): legs 1 px right of the torso and 22 rows below its top. The legs matched 58% of pixels and the torso 55%.
  - The resulting composite is 29 wide × 38 tall. The torso spans rows 0–28 and the legs rows 22–37, so the geometric overlap is 7 rows.
  - Only rows 22–26 have both pieces opaque, at most 12 shared pixels per row (own calculation).
  - The front-facing frame is 24×38 (y735). The side full-body standing frames are 29–32 × 36–37 (y693, own measurement).
- **Tarma** (own measurement, sheet [T11254][t54]): idle torso 29–31 × 27–29 and legs 21×16. The legs' row-width profile is identical to Marco's; only the top rows of the torso differ (head). Full-body standing frames 29–32 × 36–37 (y644).
- **Fio** (own measurement, sheet [F36307][f07]):
  - Idle torso 28×26 (y263). Legs 20×24 (x142–161, y265).
  - Best placement against the full-body frame (y663, 29×34): torso at rows 0–25, legs at rows 10–33, 3 px left of the torso. Both matched 51%.
  - Composite 31×34, geometric overlap 16 rows. Both pieces are opaque on rows 11–24.
- **Eri** (own measurement, sheet [E11231][e31]):
  - Idle torso 31–32 × 28 (y263). Legs 20×24 (x157–176, y266).
  - Placement against the full-body frame (y606, 30×36): torso at rows 0–27, legs at rows 12–35. They matched 46% and 52%.
  - Composite 32×36, geometric overlap 16 rows.
- **Eri and Fio share geometry.** Their legs pieces have identical row-width profiles (6, 7, 7, 8, 8, 8, 12, … 19 px), and their torsos are identical below the hair (own measurement). Eri's torso is 2 px taller because of the hair.
- **Female legs piece:** the top 6 rows are only 6–8 px wide, a strip at the back (by eye it looks like the backpack bottom or gear). The hips, 12–14 px wide, start at row 6, which is 18 px above the feet (own measurement, [F36307][f07], [E11231][e31]).

**What hides the seam** (own measurement, palettes of the overlap rows)
- Marco's torso bottom rows contain:
  - dark brown #402000 (vest hem / belt band)
  - skin #d0a058 (hands)
  - gun colours #383010 / #706838
- Marco's legs top rows are khaki trousers (#706838, #b8b070). The composite drawn either way round (torso over legs or legs over torso) looks almost the same (own observation, composite render).
- Fio and Eri's torso bottoms are the hands, gun and dark-brown shirt hem (#482800 / #402000). Their legs tops are light khaki plus dark brown.

**Weapon-specific legs and whole-body states** (own count/observation)
- Marco's RIFLE section (y2938–6854) has no leg-only rows. The rifle idle, run and jump torsos have no matching legs ([M11225][m25]); the same holds for Tarma's "Tarma with Heavy Weapon" section (from y≈1969, [T11254][t54]).
- MS1 and MS2 leg variants exist side by side for:
  - run legs (y511 / y536)
  - standing-jump legs (y894 / y923)
  - running-jump legs (y993 / y1019)
  - a 4-frame legs row (y645 / y669)
  - an unused 6-frame walk (y597 / y622)
- Fio has MS2 and MS5 standing-jump legs (y859 / y894; [F36307][f07]).
- Whole-body rows in Marco's pistol section ([M11225][m25]):
  - deaths: burn 7 frames (top of sheet), shot 14 (y819)
  - full-body standing frames: 4 (y693), 1 front-facing (y735), 4 more (y778)
  - kick: 7 (y1283)
  - full-body up-aim: 1 (y1431); unused full-body shoot-up: 1 (y1621)
  - 3 standing frames (y1682)
  - the whole crouch set (y1728–2116)
  - unused standing walks (y2553, y2597)
- Rifle whole-body: front-facing 28×38 (y3423), 4 standing 36–38 × 36–37 (y3466), deaths (y3549), kick 7 (y3965), crouch set (y4895+).
- Separate whole-body sections exist for: UNARMED, SCUBA GEAR, JETPACK, SPACE GEAR, ROPE, the vehicles, TRANSFORMATIONS (FAT, FAT TWO MACHINE GUN, MUMMY, ZOMBIE, SNOWMAN), DEATHS, PARACHUTE (own observation, section labels of [M11226][m26]).

### Inferences
- **The join sits around the hips, not the belt line of a realistic figure.** The torso piece runs down to hand and gun level (≈0.24 H from the feet) so that arms and weapon can animate freely over the hips. The legs piece starts at the hips: 0.42 H for Marco and ≈0.5 H for the females (ignoring the narrow back strip).
- **For a 128-px comando** (scale ≈3.37):
  - Marco's figures translate to a torso ending ≈30 px above the feet.
  - Legs ≈54 px tall.
  - ≈24 px of overlap.
  - Hide the overlap with the vest hem and the forearms or gun held across the hips, drawn on the torso layer.

### Gaps
- The true in-game compositing offsets (sprite-table Y offsets) cannot be read from a sheet. My overlaps come from a best match against redrawn full-body frames, so ±1 px.
- I did not exhaustively check for leg rows in the rifle sections of Eri and Fio, only from the row-size listing.

---

## 3. Frame counts per animation

### Takeaway
I verified the counts in `metal_slug.md` on [M11225][m25] / [M11226][m26]:
- idle: 4 torso + 1 legs
- run: 12 + 12
- standing jump and running jump: 6 + 6 each
- pistol shoot-forward: 10; HMG shoot-forward: 4 (+10 follow-through)
- crouch idle 4, crouch walk 7
- HMG diagonal firing: 4 per quadrant

New or corrected:
- The aim-up "hold" is an angled 4-frame loop, not vertical.
- Pistol shoot-up: 10 frames, including recoil tipping past vertical.
- HMG fire-up: 4 frames + 6 recovery.
- Down-hold: a 7-frame sway.
- A 19-frame pistol row looks like a reload (a magazine visibly drops).
- There are MS1-only "turn and fire backwards" torso sets.
- I found no dedicated fall or landing rows.

Tarma, Eri and Fio have the same structure, with the counts noted below.

### Cited Findings
Counts on Marco [M11225][m25] (own count; y = row top). The weapon-independent leg rows are listed once.

| Animation | Pistol torso | HMG/"rifle" torso | Legs / notes |
|---|---|---|---|
| Idle | 4 (y263) | 4 (y3196) | 1 legs (21×16). An extra 4-frame 21×16 leg row at y456 is unidentified. |
| Idle fidgets | 10, 8, 18, 16 (y297–422) | 12, 8, 18, 16 (y3230–3351) | over idle legs |
| Run | 12 (y477) | 12 (y3388) | 12 legs: MS1 y511, MS2 y536 |
| Unused walk(?) | 6 (y561) | – | 6 legs MS1/MS2, labelled UNUSED |
| 4-frame leg row | – | – | MS1 y645 / MS2 y669, widths 21→18→16→15. Unidentified (turn, landing or run-stop?). |
| Standing jump | 6 (y863) | 6 (y3594) | 6 legs: MS1 y894, MS2 y923 |
| Running jump | 6 (y953) | 6 (y3626) | 6 legs: MS1 y993, MS2 y1019 |
| Fall / landing | none found | none found | Inferred: the jump rows cover them. |
| Turnaround | 1 full-body front-facing (y735) | 1 (y3423, 28×38) | crouch turn 1 (y1786; rifle y4953) |
| Shoot forward | 10 (y1046) + 10 "jumping forward" variant (y1080) | 4 with flash (y3659) + 10 follow-through (y3692) | over any legs |
| Aim up | 2 transition (MS2+ y1369; MS1 y1476) + 4 hold (y1400) | 2 transition (y4010) + 4 hold (y4049) | full-body single: y1431 / y4090 |
| Shoot up | 10 (y1550; flashes separate) | 4 fire (y4142) + 6 recovery (y4219) (+10-frame y4596, unidentified) | |
| Aim / shoot down (air) | 3 transition (MS1 y2183 / MS2 y2227) + 6 shoot (y2267) | 3 transition (MS1 y5587 / MS2 y5634) + 4 fire (y5683) + 7 sway (y5881) + 6 recovery (y5926) | |
| HMG diagonal sweep | none | up: 4 fire (MS1 y4362 / MS2 y4430) + 2 non-fire (y4498 / y4547); down: 4 fire (y5751 / y5816) | |
| Grenade throw | 6 (y1157) | 6 (y3831) | crouch throw 6 (y1883) |
| Knife | slash 6 (y1192), stab 6 (y1245) | 6 + 6 (y3865, y3918) | crouch knife 7 (y1979), stab 6 (y2019) |
| Kick (full body) | 7 (y1283) | 7 (y3965) | |
| Crouch (full body) | idle 4 (y1728), walk 7 (y1757), shoot 10 (y1817), plus 4 (y1851), 8 (y1916, partly UNUSED), 4 (y1948), 5 (y2057), 8 (y2089) | idle 4 (y4895), walk 7 (y4924), shoot 4 (y4984) | the extra crouch rows are unidentified |
| Reload (inferred) | 19 (y1114) | – | a magazine drops in frames 7–10 |
| MS1-only torso firing backwards | 2 turn + 6 fire + 6 (y2384–2478, "USED IN MS1") | rows y6367–6540 ("USED IN MS1"), gun at +175° to +180° | Inferred: torso-only rear firing in MS1. |
| Deaths (full body) | burn 7 (top), shot 14 (y819) | burn 7 (y≈2951; the sheet puts an "MS6" label beside the last frame), shot 14 (y3549) | |

Other characters (own count):
- **Tarma** ([T11254][t54]). Rows are packed with 1-px separator lines.
  - idle 4 + 1 (y265)
  - fidgets 10, 18, 8, 22 (rows y299–469)
  - run 12 torso + 12 legs, then unused 6 + 6, then 4 legs (y581–637)
  - standing jump 6 + 6, then running jump 6 + 6 (y689–759)
  - crouch idle 4, walk 7 (y846–921)
  - shoot forward 10 + 10 (y928)
  - shoot up 10 (y961); shoot down 6 (y1036)
  - HMG: idle 4 (y1985), run 12 (y2273), diagonal/up/down sets as in section 1
- **Fio** ([F36307][f07]).
  - idle 4 + 1 (y263)
  - fidgets 17, 27, 9, 16, 6 (y294–463); one frame is labelled "UPDATED IN MS5"
  - run 12 + 12 (y506 / y540); unused 6 + 6 (y571 / y603); 4 legs (y634)
  - standing jump torso 6 (y827) + legs 6, in MS2 (y859) and MS5 (y894) variants
  - running jump 6 + 6 (y930 / y969)
  - shoot forward 10 + 10 (y997 / y1029); reload 21 (y1061)
  - up: 2 transition (y1523) + 4 hold (y1550) + shoot up 10 (y1655)
  - crouch idle 4 (y1827), walk 7 (y1857), turn 1 (y1887), shoot 10 (y1917)
  - down: 3 transition (y2362 / y2404) + shoot down 6 (y2446)
  - HMG idle 4 (y3238), run 12 (y3355)
  - rows labelled "ADDED IN MSX" (y2947, 5 frames) and "ADDED IN MSX UNUSED" (y3688)
- **Eri** ([E11231][e31]).
  - idle 4 + 1 (y263)
  - run torso 12 (y537); the legs row (y572) holds 16 frames: probably a 4-frame leg row followed by the 12 run legs
  - crouch idle 4 and crouch walk 7 (y811 / y858)
  - HMG idle 4 (y1887)

### Inferences
- Rows labelled "MS1" are the 1996 drawings. Unlabelled and "MS2" rows serve MS2, MSX and MS3. Fio's sheet adds explicit "MS3" and "ADDED IN MSX" rows, so a few per-game redraws exist even for the females.
- With a 12-frame run at 30 Hz, each run frame is held about 1 tick (`metal_slug.md`). This is not verifiable from the sheets.

### Gaps
- The purpose of several rows is unidentified: the 4-frame leg rows (y456; y645 / y669), the full-body rows y778 and y1682, crouch rows y1851 / y1948 / y2057 / y2089, and HMG row y4596.
- I found no dedicated fall or landing rows, so how a ledge fall is drawn cannot be confirmed from the sheets.

---

## 4. Widths vs height for all four characters, and MS1 vs MS2/X vs MS3

### Takeaway
**Marco and Tarma** share the same body pieces at every size checked:
- standing ≈36–38 px (side full-body 36–37; composite and front-facing 38)
- idle feet 21 px (0.55 H)
- idle sprite 29 px wide with the pistol, 37–38 px with the HMG
- run stride up to 31 px
- crouch 33–35 × 24 (pistol), 41 × 24 (HMG)

**Eri and Fio** are slightly shorter (side full-body 35–36 and 33–34 px) with:
- 20 px feet
- the same 30 px max stride
- taller crouches (25–28 px)
- wider HMG torsos: Fio 38, Eri 41–42
- HMG crouch 43–46 px wide (Fio)

MS1 differs from MS2 and later only in redrawn leg rows (same widths, ±1–2 px in height) and in the aim-transition and diagonal angles of section 1.

### Cited Findings
**Marco** (own measurement, bounding box of opaque pixels, [M11225][m25])
- Idle torso 29–31 × 27–29. HMG idle torso 37–38 × 27–29. Idle legs 21×16.
- Run legs 15–31 × 16–20: the MS1 and MS2 rows have identical widths except the last frame (16 vs 18).
- Standing-jump legs: MS1 18–21 × 18–24; MS2 18–21 × 19–25.
- Running-jump legs: MS1 23–33 × 14–21 (tuck 14 tall); MS2 26–33 × 16–22.
- Running-jump torso 20–32 × 29–35. Standing-jump torso 29 × 22–26.
- Crouch idle 33–34 × 24; crouch walk 34–35 × 24. HMG crouch idle and walk 41×24.
- Pistol shoot-forward torso: 32–37 wide without flash, 50–52 with flash. HMG fire-forward 60 wide with flash.
- HMG diagonal firing boxes, flash included: 55×35, 52×56, 41×60, 55×53.

**Tarma** (own measurement, [T11254][t54])
- Idle torso 29–31 × 27–29; legs 21×16; full-body 29–32 × 36–37.
- Run legs 15–31 × 16–20, identical to Marco's MS2 row.
- Standing-jump legs 18–21 × 19–25.
- Running-jump legs 26–30 × 14–22, plus one 35×29 box, probably merged with a neighbour.
- Crouch 33–35 × 24. HMG idle 37–38 × 27–29. HMG run torso 38–44 wide. HMG crouch 41×24.

**Fio** (own measurement, [F36307][f07])
- Idle torso 28×26; legs 20×24; composite 31×34.
- Side full-body 29–30 × 33–34 (y663). Front-facing 19×36 (y702).
- Run torso 26–29 × 26–27; run legs 17–30 × 23–26.
- Standing-jump torso 28–30 × 22–26; standing-jump legs 22–24 × 22–30.
- Running-jump torso 23–32 × 28–34; running-jump legs 26–33 × 17–23.
- Crouch idle 35×25; crouch walk 31–35 × 25; crouch turn 24×25.
- HMG idle 38 × 25–26. HMG crouch idle 46×25; HMG crouch walk 43–45 × 25.

**Eri** (own measurement, [E11231][e31])
- Idle torso 31–32 × 28; legs 20×24; composite 32×36.
- Side full-body 30–34 × 35–36 (y606).
- Run torso 30–32 × 28–29; run legs 17–30 × 23–26.
- Crouch idle 33–35 × 27–28; crouch walk 31–35 × 27.
- HMG idle 41–42 × 27–28.

**Between-game differences** (own diff and counts)
- [M11225][m25] (MS1 listing) and [M11226][m26] (MS3 listing) are the same composite sheet covering MS1–MS7. The 2025 revision adds:
  - "MS6" labels on the spiky-hair rows
  - split MS1/MS2 variants of the HMG down-hold and down-recovery rows
  - changes in later sections (y10729–13635 and y15702–17776)
- [T11254][t54] and [T11258][t58] are byte-identical files.
- MS1-specific drawings:
  - leg rows (run, both jumps, 4-frame row, unused walk)
  - pistol up transition (+46°, +59°) and down transition (−52°, −78°, −86°)
  - HMG diagonals (+62° and −63°) and down sway
  - torso sets that fire backwards
- Inferred, not labelled on the sheet: MS2/X/3 use the "MS2" or unlabelled rows.
- Fio's sheet has "ADDED IN MSX" rows and a separate "MS3" HMG up-hold row (angles unchanged).

### Inferences
- Visible sprite proportions are effectively identical across MS2, MSX and MS3 for each character.
- Male vs female differences:
  - longer legs piece: 24 px vs 16 px
  - narrower stance: 20 px vs 21 px
  - a crouch that is ≈1–4 px taller
  - a steeper first HMG diagonal (49° vs 26°)
- **For the comando** (scale 128/38 = 3.37 from Marco's 38 px): feet ≈71 px, idle sprite with HMG ≈125–128 px wide, max stride ≈104 px, crouch ≈81 px tall, HMG crouch ≈138 px wide (own calculation).

### Gaps
- I did not analyze the older MS3-listing rips ([E11233][e33], [F36308][f08]), so I cannot say whether those older captures differ.
- I did not measure Eri's jump rows or HMG crouch rows.
- Composite "jump tuck" heights cannot be derived without the in-game torso offset per jump frame; only piece sizes are given.

---

## 5. Edge / teeter animations and hitbox hints

### Takeaway
None of the sheets shows a teeter or ledge-balancing animation. Marco's sheet lists 49 section labels and its MISC section holds only portraits and HUD icons. The sheets contain no hitbox data.

### Cited Findings
- Marco's sheet section labels (own observation, [M11226][m26]):
  - Left column: PISTOL, RIFLE, TWO MACHINE GUN MS4/MS5, TWO MACHINE GUN MS6, UNARMED, SCUBA GEAR, JETPACK, SPACE GEAR.
  - Right column: ROPE, VEHICLES (SV-001 and the other slugs), ANTI-AIRCRAFT MACHINE GUN MS1/MS3, TRANSFORMATIONS, FAT, FAT TWO MACHINE GUN, MUMMY, ZOMBIE, SNOWMAN, DEATHS, MISC., PARACHUTE, COLD BREATH, BOMBS, WEAPONS DROP.
  - MISC (y17135–17271) contains portraits and small icons. UNARMED holds 9 empty-handed standing/walking frames and 6 tumbling frames.
- I found no row resembling a balancing pose in the pistol and rifle sections of Marco, Tarma (viewed to y≈3300) or Fio (viewed to y≈4500) (own observation).

### Inferences
- MS most likely lets the feet overhang ledges with no teeter animation and uses a narrow body box. Unverified: the sheets carry no collision data.

### Gaps
- I did not scan every row of Eri's sheet or the later Tarma and Fio sections for a teeter pose.
- Player hitboxes are not on any sheet.

---

## 6. Summary tables

### Takeaway
Table (a) gives sizes per character. Table (b) gives the per-animation structure from Marco's sheet, which I trust most because it is labelled per game, with the differences found elsewhere.

### Cited Findings
**(a) Sizes per character × game, in native px** (own measurement, bounding boxes)

H = side full-body standing height (composite or front-facing height in brackets). "Idle width" is the composite pistol idle (HMG idle torso in brackets). "Feet span" is the idle legs piece width. "Firing stance span" uses the same legs, because no firing-specific legs exist.

| Character | Games (sheet) | H | Idle width | Feet span | Firing stance span | Torso + gun width | Crouch h × w |
|---|---|---|---|---|---|---|---|
| Marco | MS1 + MS2/X/3 ([M11225][m25] / [M11226][m26]; MS1 and MS2 leg rows) | 36–37 (38) | 29 (HMG 37–38) | 21 (0.55 H) | 21 | pistol 29–31; firing 32–37 (no flash); HMG 37–38 | 24 × 33–35; HMG 24 × 41 |
| Tarma | MS1–MS3 ([T11254][t54] = [T11258][t58]) | 36–37 (38) | 29 (HMG 37–38) | 21 | 21 | pistol 29–31; HMG 37–38 | 24 × 33–35; HMG 24 × 41 |
| Eri | MS2/X ([E11231][e31]); MS3 sheet not analyzed | 35–36 (36) | 32 (HMG 41–42) | 20 (0.56 H) | 20 | pistol 31–32; HMG 41–42 | 27–28 × 33–35; HMG n/m |
| Fio | MS2/X ([F36307][f07]); MS3 sheet not analyzed | 33–34 (34–36) | 31 (HMG 38) | 20 (0.59 H) | 20 | pistol 28; HMG 38 | 25 × 31–35; HMG 25 × 43–46 |

Additional sizes (own measurement):

| Character | Max run stride | Running-jump legs (tuck) |
|---|---|---|
| Marco / Tarma | 31 | 26–33 × 14–22 |
| Eri | 30 | n/m |
| Fio | 30 | 26–33 × 17–23 |

**(b) Per animation: torso frames / leg frames, Marco** ([M11225][m25], own count; full details in section 3)

| Animation | Torso frames | Leg frames | Notes and differences in other sheets |
|---|---|---|---|
| Idle | 4 (pistol), 4 (HMG) | 1 | fidgets 10/8/18/16 pistol, 12/8/18/16 HMG. Tarma 10/18/8/22; Fio 17/27/9/16/6. |
| Run | 12 | 12 (MS1 and MS2 rows) | same counts for Tarma, Eri, Fio |
| Standing jump | 6 | 6 (MS1/MS2) | Fio legs in MS2/MS5 variants |
| Running jump | 6 | 6 (MS1/MS2) | |
| Fall / landing | – | – | no dedicated rows found |
| Crouch idle / walk | 4 / 7 (full body) | – | all characters |
| Turnaround | 1 full body | – | standing and crouched |
| Pistol shoot forward | 10 (+10 air variant) | any | Fio and Tarma also 10 + 10 |
| Pistol up | 2 transition + 4 hold (≈62–74°) + 10 shoot | any | MS1 has its own transition (+46°, +59°) |
| Pistol down (air) | 3 transition + 6 shoot | jump legs | MS1 −52/−78/−86° vs MS2 −37/−66/−86° |
| HMG shoot forward | 4 (flash in frame) + 10 follow-through | any | |
| HMG up | 2 transition (26°, 47°) + 4 hold (61–67°) + 4 fire (≈90°) + 6 recovery | any | females: 49°/57°, hold 54–59° |
| HMG diagonal sweep | up 4 firing + 2 non-firing; down 4 firing; down 3 transition + 4 fire + 7 sway + 6 recovery | any / jump legs | male MS2+: 26°/55°, −32°/−74°; MS1: 26°/62°, −32°/−63°; female: 49°/60°, −29°/−61° |
| Grenade | 6 | any | crouch 6 |
| Knife | 6 slash + 6 stab | any | crouch 7 + 6 |
| Kick | 7 full body | – | |
| Reload (inferred) | 19 | any | Fio 21 |
| Deaths | burn 7, shot 14 (full body) | – | |

### Inferences
- If one sheet is copied for the comando, Marco's MS2 rows are the cleanest template:
  - shared legs: idle 1, run 12, jumps 6 + 6
  - per-weapon torsos: idle 4, run 12, shoot 4–10, up 2 + 4 + fire, down 3 + fire, diagonals 2 angles × 2 flashes per quadrant
  - full-body crouch, kick and turn

### Gaps
- n/m = not measured: Eri HMG crouch, Eri jump rows, and both older MS3-listing rips.
