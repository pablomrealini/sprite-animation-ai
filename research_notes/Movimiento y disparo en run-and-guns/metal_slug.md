# Metal Slug 1 / 2 / X / 3 (Nazca/SNK, Neo Geo): player movement, jumping, shooting and the split-body aiming sprites

Labels used in these notes:
- **(own measurement)**: I measured it myself from a 60 fps capture of MS1 (arcade) or from a sprite rip. The inputs are given.
- **(own count)**: frames counted on the sprite rip.
- **(own calculation)**: arithmetic on cited or measured inputs.

**Reference values used for normalization** (details and sources in section 1):
- Marco's standing sprite is about **38 px** tall (H = 38 px).
- The Neo Geo MVS runs at **59.1856 Hz**. Metal Slug's game logic and sprites update every 2nd frame (about 30 Hz).
- The capture shows a **304 × 224** visible area. The hardware's active display is 320 × 224.

**Primary measurement sources:**
- Speed and jump numbers come from video [Metal Slug Arcade [60fps] Hardest - Marco Rossi No Death Speedrun](https://www.youtube.com/watch?v=_iOu1ozwk5s) (1440×1080 @ 60 fps, Mission 1, t ≈ 9.85–11.4 s). I stepped through it frame by frame in the browser and analyzed pixels from a canvas.
- Frame counts come from The Spriters Resource sheet "Marco Rossi" (uploaded by The Huntress, additional credits Kevin Huff, 1818×17959 px). The same sheet is listed under [Metal Slug](https://www.spriters-resource.com/neo_geo_ngcd/ms/asset/11225/), Metal Slug 2/X (asset 11223) and Metal Slug 3 (asset 11226). The live site was behind a bot check, so I read the [Wayback copy of the PNG](https://web.archive.org/web/20230512095229/https://www.spriters-resource.com/resources/sheets/11/11225.png). I used it only to count and measure.

---

## 1. Movement: speed, acceleration, turnaround, shooting while moving, crouch-walk

### Takeaway
Marco walks/runs at about **1.5 px/frame**, which is 3 px per 30 Hz logic tick:
- That is ≈ **89 px/s**, or ≈ **2.3 character heights per second**.
- Acceleration looks instant.
- The legs keep running at full speed while the torso shoots or knifes.
- Jumping moves faster horizontally (≈2.1–2.35 px/frame), so experts "bunny-hop".

All four MS1–MS3 characters move identically. No source gives crouch-walk speed.

### Cited Findings
**Hardware and frame rate**
- Neo Geo MVS timing:
  - 24 MHz master clock / 4 = 6 MHz pixel clock.
  - 384 pixels per line → 15.625 kHz.
  - 264 lines → **59.1856 frames/s**.
  - The NTSC AES runs at 59.599 Hz.
  - Source: [NeoGeoDev wiki – Framerate](https://wiki.neogeodev.org/index.php?title=Framerate)
- Active display is 320 px per line (1280 mclks) and 224 active scanlines out of 264. — [NeoGeoDev wiki – Display timing](https://wiki.neogeodev.org/index.php?title=Display_timing)
- The capture shows only **304 px** of width (own measurement).
  - Inputs: the HUD "INSERT COIN" text is 11 fix-layer characters of 8 px each. It spans 417 px in the 1440-px-wide capture, so one native px = 4.74 capture px, and 1440 / 4.74 ≈ **304 px**.
  - Vertical scale is 1080 / 224 = 4.82.
  - So MS1 uses the common 304×224 visible area inside the 320×224 frame.
- Metal Slug games "actually only run at 30 FPS, compared to the 60 FPS of most 2D side-scrollers." — [Hardcore Gaming 101 – Metal Slug](https://www.hardcoregaming101.net/metal-slug/)
  - Confirmed (own measurement): in the 60 fps capture, every second frame is identical. The background scroll and Marco's sprite change only on alternate frames (14 consecutive ticks checked, t = 10.008–10.542 s).
  - The TAS notes agree: every documented timing is a multiple of 2 frames ("once every 4 frames", "2 frame delay"). — [TASVideos #9815 (MSX)](https://tasvideos.org/9815S)

**Character height (normalization unit)**
- Marco's standing height is ≈ **37–38 px** (own measurement on the sprite sheet). Full-body standing frames measure:
  - 29–32 × 36–37 px (pistol, sheet y=693)
  - 24 × 38 px (front-facing frame, y=735)
  - 36–38 × 36–37 px and 28 × 38 px (rifle section, y=3466 and y=3423)
- In the capture, the running Marco measured ≈ 36–37 native px from hair top to boot sole (own measurement, grid overlay at t = 10.008 s). **H = 38 px is used below.**
- Crouched full-body sprites are **24 px** tall (33–35 px wide) with the pistol, which is 0.63 H (own measurement, sheet y=1728/1757).
- Characters were "almost all identical, up until *Metal Slug 6*", so Marco = Tarma = Eri = Fio in MS1–MS3. — [HG101](https://www.hardcoregaming101.net/metal-slug/)

**Ground speed (own measurement)**
- Method: during a steady run on the Mission 1 bridge, the camera tracked Marco exactly. His vest stayed at screen x = 632–641 capture px. So camera scroll equals player speed.
- I measured the scroll by cross-correlating a 120-px-tall strip of the bridge layer (capture y 880–1000) between frames.
- Every logic tick (every 2nd video frame) the scroll was **14 capture px** (one tick read 9, a measurement outlier). 14 / 4.737 = **2.96 → 3 native px per tick**.
- Converted (own calculation):
  - 3 px / 2 frames = **1.5 px/frame**
  - × 59.1856 Hz = **88.8 px/s**
  - / 38 px = **2.34 H/s**
  - Crossing the 304-px screen takes ≈ 3.4 s.
- Acceleration:
  - In the sample, the first tick in which the camera moved already moved the full 14 px. I saw no ramp-up (own measurement, t = 10.025 → 10.042 s).
  - Corroboration: holding left or right for only 2 frames before jumping is enough to "gain more distance". — [TASVideos #9399 (MS4)](https://tasvideos.org/9399S), [#9815 (MSX)](https://tasvideos.org/9815S)
  - Caveat: I did not capture a true start from standstill, so "instant" is an inference (see Inferences).

**Jumping is faster than walking**
- "Jumping has a higher max speed than walking, making it faster most of the time." — [TASVideos #9399](https://tasvideos.org/9399S), [#9815](https://tasvideos.org/9815S)
- "Most of the time, jumping is faster than walking." — [TASVideos #5392 (MS3)](https://tasvideos.org/5392S)
- JumpLab says SNK's Metal Slug (1996) multiplies horizontal velocity by a factor >1 at the moment of takeoff ("Acceleration is used in SNK 'Metal Slug' (1996)"). — [JumpLab – Vx adjustment at takeoff](https://fukuchi.org/en/works/jumplab/settings-jump-vxAdjustmentAtTakeoff.html)
- Measured jump horizontal speed (own measurement), as scroll per tick plus the change in Marco's screen x:
  - Jump 1: started at 3 px/tick (14 capture px) and rose to ≈4–5 px/tick (19–24 capture px). Average **2.13 px/frame** (445 capture px scroll + 80 px screen drift over 52 frames).
  - Jump 2 (chained): **2.35 px/frame** (498 + 59 px over 50 frames).
  - That is ≈ 126–139 px/s ≈ **3.3–3.7 H/s**, about 1.4–1.6× ground speed (own calculation).
  - The speedrunner in the capture hops continuously (t = 12.6–17.5 s). Scroll stays at ≈38–43 capture px per 4 frames, ≈2.0–2.3 px/frame (own measurement).

**Turnaround**
- Turning is effectively instant and is used to cancel actions.
  - MS3/MS4 "Turnaround cancel": "While crouching, when you attack, you can immediately turn around and do something else." — [TASVideos #5392](https://tasvideos.org/5392S)
  - In MSX, "turnaround cancel only became a thing from Metal Slug 3 and onward". MSX instead uses a crouch/stand toggle to cancel. — [TASVideos #9815](https://tasvideos.org/9815S)
- "Moonwalking": press up, then hold the direction opposite to the one you face. This walks one way while facing the other. — [TASVideos #9815](https://tasvideos.org/9815S), [#9399](https://tasvideos.org/9399S)
- The sheet has single front-facing frames (own count): pistol standing 24×38 (y=735), crouching 21×26 (y=1786), rifle standing 28×38 (y=3423). These look like one-frame turn poses (interpretation, unverified).

**Shooting and melee while moving**
- Neither stops the legs (own measurement and observation). Between t = 9.86 and 10.54 s Marco fires the pistol and then performs the 6-frame overhead knife slash on a crate.
  - The run-cycle legs keep animating under the attacking torso.
  - The scroll stays at 3 px/tick throughout.
- In MS1 the player does not die from touching enemies, so you can walk into them and melee. — [Wikipedia – Metal Slug (1996)](https://en.wikipedia.org/wiki/Metal_Slug_(1996_video_game)), [HG101](https://www.hardcoregaming101.net/metal-slug/)

**Crouch**
- The crouch-walk animation has **7 frames** of full-body crouched sprites, 34–35×24 px (own count, sheet y=1757).
- No speed found (see Gaps).

### Inferences
- Ground acceleration and deceleration are probably instant, with a 1-tick (2-frame) granularity. This fits the 30 Hz update and the TAS's "2 frames" rule. Movement feels "digital", and takeoff then adds speed.
- With 3 px per tick and a 12-frame run-leg cycle (own count), one leg cycle covers 36 px ≈ 0.95 H, if each leg frame lasts one tick. That is a stride of ≈18 px per step. Leg frame timing was not verified (see section 4).
- **For the comando at 128 px** (scale 128/38 = 3.37, own calculation):
  - Marco-equivalent ground speed ≈ 299 px/s (2.34 H/s).
  - Jump drift ≈ 420–470 px/s.

### Gaps
- No source gives crouch-walk speed. I could not measure it because the speedrunner never crouch-walked in the sampled segment.
- Not measured for MS2/MSX/MS3. I measured MS1 only. HG101 says the characters are identical, but per-game physics constants were not confirmed.
- No disassembly or RAM map with velocity constants was found (searched Data Crystal, TASVideos and GitHub).

---

## 2. Jump: height, airtime, arc, air control, variable jump, coyote, buffer

### Takeaway
Measured running jump in MS1 (own measurement):
- Height ≈ **59 px ≈ 1.55 H**.
- Airtime ≈ **50 frames ≈ 0.84 s**.
- Arc: ≈22 frames rising, ≈8 frames hanging at the apex, ≈22 frames falling. It is **symmetric**, with no faster fall.

Mechanics from the TAS notes:
- Standing jumps rise faster, hang longer and fall faster, but land on the same frame as moving jumps.
- Horizontal speed builds up *during* the jump, so the arc is not a fixed launch.
- I found no evidence of variable jump height, coyote time or buffering.

### Cited Findings
**Height and airtime (own measurement)**

Method: I tracked the top of Marco's red vest (pixels with R>150, G<70, B<60) every tick during two consecutive running jumps on flat ground (t ≈ 10.47–12.3 s).
- Ground y was 667 capture px. Apex y was 382 capture px, held for 4–5 ticks.
- Δ = 285 capture px / 4.821 = **59.1 native px**. That is **1.55 H**.
- Uncertainty is about ±4 px, because the jump torso may sit slightly differently on the body than the run torso.

Per-tick vertical displacement in native px (own measurement):
- Rising: 10.0, ~7.6, ~7.6, 7.1, 5.8, 5.0, 5.0, 3.3, 3.9, 1.9, 2.1 (sums to ≈59).
- Apex: 0 for 4 ticks.
- Falling: 2.1, 2.1, 2.9, 4.1, 5.0, 5.0, 5.8, 7.1, 7.1, 8.1, 8.9.

Airtime (own measurement):
- Jump 1: takeoff at video frame ≈29, landing at ≈80, so ≈52 frames.
- Jump 2: ≈49–50 frames.
- So **≈50 ± 2 frames ≈ 0.84 s** at 59.19 Hz.
- Rise to apex ≈22 frames (0.37 s), apex hang ≈8 frames (0.14 s), fall ≈22 frames (0.37 s) (own calculation).

**Standing vs moving jump** (all from [TASVideos #9399 (MS4)](https://tasvideos.org/9399S) and [#9815 (MSX)](https://tasvideos.org/9815S))
- "Standing jumps gain height faster, linger at the peak longer, and descend faster."
- "Moving jumps gain horizontal speed faster."
- "Both types of jumps still spend the same amount of time in the air (you will land on the same frame)."

**Momentum and pre-jump input**
- "Holding left/right for at least 2 frames before jumping will gain more distance than pressing left/right and jump at the same time." — [TASVideos #9399](https://tasvideos.org/9399S), [#9815](https://tasvideos.org/9815S)
- Jumping off slopes gives a short speed boost that depends on where on the slope you jump. Jumping out of an area instead of walking "can save 4 frames". — [TASVideos #9399](https://tasvideos.org/9399S)
- MSX Metal Slug vehicle: after landing in the Slug you get a forced-forward boost. "This speed can be preserved by jumping while not holding any directional keys." Speed is lost gradually while jumping. — [TASVideos #9815](https://tasvideos.org/9815S)
- JumpLab: Metal Slug multiplies horizontal velocity at takeoff (acceleration). — [JumpLab](https://fukuchi.org/en/works/jumplab/settings-jump-vxAdjustmentAtTakeoff.html)

**Design intent**
- A hover ability triggered by repeated jump presses was tested and removed because it would have ruined the "jump-jump-jump tempo" (Meeher, MS2 planner). — [Shmuplations – Metal Slug 2 1998 developer interview](https://shmuplations.com/?p=19321)

**Shooting from the air**
- Jumping while firing pistol, H or 2H upward makes bullets deal damage 2 frames earlier. Landing adds a 2-frame delay that restores the normal rate. — [TASVideos #9815](https://tasvideos.org/9815S), [#9399](https://tasvideos.org/9399S)

**Sprites (own count)**
- Separate standing-jump and running-jump torso sets (6 frames each) and leg sets (6 frames each, MS1 and MS2 variants) exist. See section 4.
- A fan wiki claims the two body sprites "occasionally… merge when jumping, making the character really squat." — [All The Tropes – Metal Slug/YMMV](https://allthetropes.org/wiki/Metal_Slug/YMMV) (unverified fan claim)

### Inferences
- **Air control.** The arc is *not* fully committed. The TAS wording that moving jumps "gain horizontal speed faster" than standing jumps implies horizontal acceleration is applied in the air, toward a cap of ≈2.1–2.35 px/frame. A standing jump followed by holding a direction therefore drifts.
  - I could not confirm whether pressing the opposite direction mid-air reverses momentum or only turns the character.
  - In-game experience suggests you can turn and shoot backwards mid-air, but this is **unverified here**.
- **Gravity.** The running-jump arc is close to symmetric, with gravity ≈0.8–0.9 px/tick². Because takeoff ≈10 px/tick and apex take 11 ticks, g ≈ 10/11 ≈ 0.91 px/tick² gives h ≈ 55 px, close to the 59 px measured (own calculation).
  - The rising profile has small irregularities, possibly table-driven. The standing jump uses a different curve (TAS).
- **Variable jump height** probably does not exist. The TAS says both jump types land on the same frame and never mentions a release or short hop. Most MS speedrun strategies rely on full hops. This is inference, not confirmed.
- **For the comando at 128 px (own calculation):**
  - A Marco-like jump would be ≈199 px high (1.55 H) with 0.84 s of airtime.
  - At the comando's 12 fps animation, that is ≈10 drawn frames for the whole jump.

### Gaps
- No source states coyote time (late jump off ledges) or jump buffering. Neither could be measured with the available footage.
- Standing-jump height and airtime were not measured. No standing jump appeared in the sampled run, because the speedrunner always jumps while moving.
- Whether facing can change mid-air (to shoot backwards) has no source.

---

## 3. Shooting: directions, selection, rates, HMG sweep, knife, grenades

### Takeaway
The pistol fires in **4 directions**, chosen with the stick plus fire:
- forward (standing, running, crouching or airborne)
- up (hold up, standing or airborne)
- down (only while airborne)
- crouch-forward (down on the ground crouches)

Diagonals were deliberately excluded. The **HMG is the only pre-MS6 weapon that can fire diagonally**. Changing the stick between forward and up (or down in the air) while it fires makes the torso **sweep through intermediate angle poses**, spraying bullets in an arc.

Rates:
- HMG: 1 bullet per 4 frames ≈ 14.8 bullets/s, fired in 4-round bursts (6-round bursts in MS1), 200 rounds.
- Pistol: about half that rate.
- Melee is context-sensitive on the same fire button.

### Cited Findings
**Directions**
- Upward shooting works standing or jumping, and downward only while jumping. There is no diagonal aiming. All weapons can be fired while ducking or jumping. — [Sega Retro – Metal Slug](https://segaretro.org/Metal_Slug) (read from search-result excerpt; the page itself was bot-protected); players confirm "jump + shoot down" — [Steam discussion (MS3)](https://steamcommunity.com/app/250180/discussions/0/540743212319100635)
- "The game famously has no diagonal aiming for weapons. According to an interview with Kazuma Kujo in Retro Gamer Issue 98, this was an intentional design decision." — [GamINGhell review](https://www.gaminghell.co.uk/MetalSlug.html) (secondary; quoted from search excerpt)
- Shooting is limited to horizontal, which makes the game easier for newcomers. The series deliberately keeps its controls simpler than the industry trend (Meeher). — [Shmuplations MS2 interview](https://shmuplations.com/?p=19321)
- A lost early (1995) build allowed diagonal aiming by pressing multiple buttons at once. — [Lost Media Wiki – early build](https://lostmediawiki.com/Metal_Slug_(lost_early_build_Japanese_arcade_run_and_gun_game;_1995)) (search excerpt)
- "The HMG is the only weapon that can fire diagonally prior to *Metal Slug 6*." — [Metal Slug Wiki – Weapons](https://metalslug.fandom.com/wiki/Weapons)

**HMG sweep (360° spray)**
- After jumping, you can turn the stick to spray the HMG in all directions (360°). This is the standard way to hit diagonal targets without a vehicle. — [Namu Wiki – Heavy Machine Gun](https://namu.wiki/w/%ED%97%A4%EB%B9%84%20%EB%A8%B8%EC%8B%A0%EA%B1%B4(%EB%A9%94%ED%83%88%EC%8A%AC%EB%9F%AC%EA%B7%B8%20%EC%8B%9C%EB%A6%AC%EC%A6%88)) (translated)
- Namu's table lists "MS2 + fat player: diagonal spray impossible". The text says the 360° spray did not work in MS2, a critical problem that was fixed in MSX. — [Namu Wiki – HMG](https://namu.wiki/w/%ED%97%A4%EB%B9%84%20%EB%A8%B8%EC%8B%A0%EA%B1%B4(%EB%A9%94%ED%83%88%EC%8A%AC%EB%9F%AC%EA%B7%B8%20%EC%8B%9C%EB%A6%AC%EC%A6%88))
- MS5 player note (outside this scope but same mechanic): the HMG "only fires diagonally if you swap from shooting left/right to up and back again". — [RetroAchievements MS5 comments](https://retroachievements.org/game/20599/comments) (search excerpt)
- HMG sweep sprite construction in MS1 and MS2 (own count, rifle section of the sheet):
  - **Diagonal-up firing:** 4 torso frames with muzzle flash (sheet y=4362 "MS1" and y=4430 "MS2"). By eye, the gun sits at only **two distinct intermediate angles, ≈25–30° and ≈60–65° above horizontal** (own measurement, ±10°). Each angle has two muzzle-flash variants, ordered shallow → steep → steep → shallow.
  - **Non-firing transitions:** 2 torso frames at the same two angles (y=4498/4547, plus y=4010).
  - **Diagonal-down:** the same 4-frame pattern at ≈30–35° and ≈65–75° below horizontal (y=5751/5816).
  - So the HMG torso has **4 aim poses per quarter-circle**: 0°, ~30°, ~60° and 90°. Muzzle-flash art is baked into the torso frames.
  - The pistol has only non-firing transition frames: 2 for up (y=1369; the MS1/MS2 variants at y=1476/1513 are marked UNUSED) and 3 for down (y=2183/2227). The pistol therefore never fires diagonally.

**Fire rates**
- HMG: "Pressing fire once with H shoots 4 bullets, each doing 10 damage every 4 frames." — [TASVideos #9815 (MSX)](https://tasvideos.org/9815S); same in MS4 — [#9399](https://tasvideos.org/9399S)
  - 1 bullet / 4 frames × 59.19 Hz = **14.8 bullets/s** (own calculation).
- The HMG fires a minimum 4-round burst, and repeated pressing doubles it. Pressing fire once and immediately crouching cancels down to 1 round. In **MS1 the minimum burst is 6 rounds**. Damage equals the handgun's but fire rate is **2×**. — [Namu Wiki – HMG](https://namu.wiki/w/%ED%97%A4%EB%B9%84%20%EB%A8%B8%EC%8B%A0%EA%B1%B4(%EB%A9%94%ED%83%88%EC%8A%AC%EB%9F%AC%EA%B7%B8%20%EC%8B%9C%EB%A6%AC%EC%A6%88))
- Damage per hit: pistol 10, H 10 (auto-fire), melee (knife or kick) 30, grenade 100. — [TASVideos #5392 (MS3)](https://tasvideos.org/5392S)
- Ammo:
  - HMG 200 rounds from MS1 to MS5. — [Metal Slug Wiki – Heavy Machine Gun](https://metalslug.fandom.com/wiki/Heavy_Machine_Gun)
  - +150 rounds per extra pickup up to MS5. — [Namu Wiki – HMG](https://namu.wiki/w/%ED%97%A4%EB%B9%84%20%EB%A8%B8%EC%8B%A0%EA%B1%B4(%EB%A9%94%ED%83%88%EC%8A%AC%EB%9F%AC%EA%B7%B8%20%EC%8B%9C%EB%A6%AC%EC%A6%88))
  - Default kit: infinite handgun plus 10 grenades. — [Namu Wiki – Metal Slug series/Weapons](https://namu.wiki/w/%EB%A9%94%ED%83%88%EC%8A%AC%EB%9F%AC%EA%B7%B8%20%EC%8B%9C%EB%A6%AC%EC%A6%88/%EB%AC%B4%EA%B8%B0)
  - Grenades are restored each new life. — [HG101](https://www.hardcoregaming101.net/metal-slug/)
- Fire-rate caps and cancels:
  - Crouching bypasses the fire-rate cap of slow weapons. This does not apply to MS1, or to pistols in MS2/X. — [Speed Demos Archive KB](https://kb.speeddemosarchive.com/Metal_Slug)
  - MSX has a 2-frame delay between rounds when firing 2H while standing, but not while crouched. — [TASVideos #9815](https://tasvideos.org/9815S)
- Cosmetic pistol reload: after about 12 shots (male characters) or 7 shots (female revolver), the character reloads when idle. This is purely cosmetic. — [Metal Slug Wiki – Weapons](https://metalslug.fandom.com/wiki/Weapons), [Namu Wiki – Weapons](https://namu.wiki/w/%EB%A9%94%ED%83%88%EC%8A%AC%EB%9F%AC%EA%B7%B8%20%EC%8B%9C%EB%A6%AC%EC%A6%88/%EB%AC%B4%EA%B8%B0)

**Melee**
- Attacking while close to a living enemy uses a melee attack instead of the gun. Male characters use a knife, and MS2 onward adds a kick. — [Namu Wiki – Weapons](https://namu.wiki/w/%EB%A9%94%ED%83%88%EC%8A%AC%EB%9F%AC%EA%B7%B8%20%EC%8B%9C%EB%A6%AC%EC%A6%88/%EB%AC%B4%EA%B8%B0), [Wikipedia – Metal Slug 2](https://en.wikipedia.org/wiki/Metal_Slug_2), [Metal Slug Wiki – Knife](https://metalslug.fandom.com/wiki/Knife)
- In MSX, Eri and Fio alternate between a tonfa and a hatchet. — [TASVideos #9815](https://tasvideos.org/9815S)
- Melee animations can be cancelled after a 2-frame wait. — [TASVideos #9815](https://tasvideos.org/9815S), [#5392](https://tasvideos.org/5392S)

**Grenades**
- In MS3, after throwing 2 bombs you must wait 8 frames before throwing 2 more. — [TASVideos #5392](https://tasvideos.org/5392S)
- Throw sprites (own count): standing throw torso 6 frames, layered on any legs (pistol y=1157; rifle y=3831). Crouched throw is 6 frames of full-body crouch sprites (y=1883).

**Female characters**
- Eri and Fio shake their hands after sustained HMG fire. The MS2 designers disliked this animation; the planner liked it. — [Shmuplations MS2 interview](https://shmuplations.com/?p=19321), [Namu – HMG](https://namu.wiki/w/%ED%97%A4%EB%B9%84%20%EB%A8%B8%EC%8B%A0%EA%B1%B4(%EB%A9%94%ED%83%88%EC%8A%AC%EB%9F%AC%EA%B7%B8%20%EC%8B%9C%EB%A6%AC%EC%A6%88))

### Inferences
- **Aim lock and stopping:**
  - Up-aim is a torso-only state. The pistol and rifle up-aim/shoot-up rows are torsos, and the single full-body "shoot up" frames are marked UNUSED on the sheet. So the legs can keep running while you aim and fire up: no stop, no aim lock (inference from sprite structure plus the observed run-and-knife behavior).
  - Down on the ground means crouch, which is a separate full-body sprite set. Crouch-shoot therefore moves at crouch-walk speed.
- **Pistol rate:** about half the HMG's, so roughly one shot per ~8 frames when tapping (≈7.4 shots/s). This is an own calculation from "HMG 2× pistol" plus "HMG one bullet per 4 frames", not measured.
- **The sweep is mostly an input trick on top of 4 discrete torso angles.** Bullets probably leave at the angle of the current torso pose, or are interpolated. The *visible* smoothness comes from the 4-frame firing poses plus alternating flashes.
- **For the comando:** an HMG-style sweep needs only **2 intermediate torso poses per quadrant** (~30°, ~60°) plus forward, up and down. That is 7 aim poses for a front half-circle, each with 2 flash variants.

### Gaps
- No source states the exact number of *bullet* angles in the HMG sweep, or how many ticks each intermediate angle holds. I could not measure bullet vectors from the footage within the available time.
- No source gives the maximum number of pistol bullets on screen.
- No source gives the exact pistol cooldown.

---

## 4. Sprite construction: the split-body system, part counts, animation rate

### Takeaway
The player is **two independently animated sprites**:
- a **torso** (head, arms, weapon and muzzle flash, down to the belt)
- **legs** (hips down)

The game composites them at runtime and switches the torso set per weapon (pistol vs "rifle" for all special weapons) while **sharing one set of legs**. The torso overlaps the top of the legs by roughly 7–8 px at the belt, which hides the seam.

Exceptions are drawn as **full-body sprites**: crouching (all crouch actions), kicks, turns, deaths, and a few transitions.

Everything updates at 30 Hz. Key counts (own count):
- run: 12 torso + 12 legs
- idle: 4 torso + 1 legs
- jump: 6 + 6 (standing and running variants)
- pistol shoot-forward torso: 10
- HMG shoot-forward torso: 4
- HMG diagonals: 4 per quadrant

### Cited Findings
**Neo Geo hardware**
- Sprites are vertical strips of 16×16 tiles: 1 tile (16 px) wide, up to 32 tiles (512 px) tall, 15 colors plus transparency. — [NeoGeoDev – Sprites](https://wiki.neogeodev.org/index.php?title=Sprites)
- Strips "can be stuck together horizontally to make huge moveable objects". — [NeoGeoDev – Sprites](https://wiki.neogeodev.org/index.php?title=Sprites)
- Limits: at most 96 sprites per scanline and 381 displayable per frame. — [NeoGeoDev – Sprites](https://wiki.neogeodev.org/index.php?title=Sprites)
- The sticky (chain) bit makes a strip inherit the previous strip's Y, height and shrink, "by just updating one coordinate pair." — [NeoGeoDev – Sticky bit](https://wiki.neogeodev.org/index.php?title=Sticky_bit)
- A Metal Slug sprite is usually limited to 15 colors. The head is "almost a third of the overall body". — [6th Division's Den – Metal Slug spriting tutorial](https://6th-divisions-den.com/ms_tutorial.html)

**Split body**
- "The player character is mostly composed of two separate sprites (the upper and lower bodies) to make the action more fluid." — [All The Tropes – Metal Slug/YMMV](https://allthetropes.org/wiki/Metal_Slug/YMMV) (fan wiki)
- Fan asset packs copying the style split "most of the sprites… into torso and leg parts so that they may change independent of each other". — [poohcom1 – Soldier Girl sprite pack](https://poohcom1.itch.io/soldier-girl-sprite-pack)
- Unity developers recreating the look report the same choice: split arms/torso on a separate layer. — [Unity Discussions](https://discussions.unity.com/t/need-help-with-a-sprite-metal-slug-style-animation-style/544549), [Unity forum](https://forum.unity.com/threads/2d-sprite-with-multiple-body-parts.224146/)
- Direct evidence from the rip (own count). The sheet's "PISTOL" and "RIFLE" sections lay out separate torso rows and separate leg rows. Leg rows even come in "MS1" and "MS2" variants (e.g. run legs at y=511/536), while the torsos above them are single rows.
- The **RIFLE section contains no leg rows at all**. The rifle idle, run and jump torsos (y=3196–3660) have no matching legs, so the legs are **shared** between weapon torso sets (own observation).
- In motion (own observation, capture t = 10.06–10.38 s), the 6-frame overhead knife torso plays over continuously cycling run legs while the scroll stays at 3 px/tick.

**Seam**
- The idle torso is 29 px tall and the idle legs 16 px. Stacked that gives 45 px, against a full-body standing height of 37–38 px, so the parts overlap by **≈7–8 px** (own calculation from own measurements).
- The torso frames include the red vest hem and belt. The leg frames start at the hips and thighs. The vest/belt band covers the join (own observation of the rip).

**Torso sets per weapon in MS1/MS2** (own count, sheet sections "PISTOL" y=0–2938 and "RIFLE" y=2938–6854)

Later sections ("TWO MACHINE GUN MS4/MS5", "TWO MACHINE GUN MS6", "UNARMED", "SCUBA GEAR", "JETPACK", "SPACE GEAR", "VEHICLES", "TRANSFORMATIONS: FAT, FAT TWO MACHINE GUN, MUMMY, ZOMBIE, SNOWMAN", "DEATHS", "MISC", "PARACHUTE") show the same torso-set approach per weapon or state.

The "rifle" torso is used for every special weapon on male characters. — [Metal Slug Wiki – Weapons](https://metalslug.fandom.com/wiki/Weapons): "All special weapons take the form of the AR-10 assault rifle for male characters".

| Part / state | Pistol | Rifle (HMG etc.) | Notes (own count; sheet y) |
|---|---|---|---|
| Idle torso | 4 (29×27–29) | 4 (37–38×27–29) | plus idle fidget variants: pistol 10, 8, 18, 16 frames; rifle 12, 8, 18, 16 |
| Idle legs | 1 (21×16) | shared | extra 4-frame leg row at y=456 (unidentified) |
| Run torso | 12 | 12 (38–44 wide) | y=477 / 3388 |
| Run legs | 12 (15–31 wide × 16–20 tall) | shared | separate MS1/MS2 rows, y=511/536 |
| Standing jump | torso 6 + legs 6 (legs 18–21 wide) | torso 6 | y=863–923 / 3594 |
| Running jump | torso 6 + legs 6 (legs 26–33 wide) | torso 6 | y=953–1019 / 3626 |
| Shoot forward | 10 (first 3 with flash), plus a 10-frame variant "used when jumping forward" | 4 (with flash) + 10 follow-through | y=1046/1080 / 3659/3692 |
| Aim up | 2 transition + 4 hold | 2 + 4 | y=1369/1400 / 4010/4049 |
| Shoot up | 10 | 4 (+6 recovery) | y=1550 / 4142/4219 |
| Aim/shoot down (air) | 3 transition + 6 shoot | 3 + 4 | y=2183/2267 / 5587/5683 |
| Diagonal firing | none | 4 up + 4 down (2 angles each) | y=4362/5751 (MS1), y=4430/5816 (MS2) |
| Grenade throw torso | 6 | 6 | y=1157 / 3831 |
| Knife torso | 6 slash + 6 stab | 6 + 6 | y=1192/1245 / 3865/3918 |
| Kick (full body) | 7 | 7 | y=1283 / 3965 |
| Crouch (full body) | idle 4, walk 7, shoot 10, throw 6, knife 7 / 6, turn 1 | similar set | y=1728–2019; rifle crouch ≈42–44×27 |
| Death (full body) | 14 shot, 7 burn | 14, 7 | y=819, 25 / 3549, 2951 |

Animation rate:
- Game state and sprites update every 2nd 59.19 Hz frame, i.e. 29.6 Hz (own measurement; [HG101](https://www.hardcoregaming101.net/metal-slug/)).
- MS1 and MS2 used separate leg rows (minor redraws). The MS2/X/3 sheet listings reuse the same composite sheet. — [Spriters Resource asset pages](https://www.spriters-resource.com/neo_geo_ngcd/ms/asset/11225/)

**Developer statements**
- Akio Oyabu, about MS2: animation detail is what lets a 2D game "compete with polygon games". — [Shmuplations](https://shmuplations.com/?p=19321)
- Akio: the animation work for the characters added in MS2 was "about 6000 frames, I believe…". — [Shmuplations](https://shmuplations.com/?p=19321)
- Meeher: frame counts can't be compared with fighting games because "the sprites aren't the same size". — [Shmuplations](https://shmuplations.com/?p=19321)
- Akio, headline: his elaborate pixel animations "made his programmers want to rip their hair out, but it was so worth it". Article body not retrievable. — [Automaton](https://automaton-media.com/en/news/metal-slug-artist-akio-says-his-elaborate-pixel-animations-made-his-programmers-want-to-rip-their-hair-out-but-it-was-so-worth-it/)
- Kinte: the tank (Slug) was originally the only player character. Stages were built around tank-only play, and adding humans required rebuilding much work. — [Shmuplations](https://shmuplations.com/?p=19321)
- Marco's physique is modeled on Stallone's Rambo III. — [Metal Slug Wiki – Marco Rossi](https://metalslug.fandom.com/wiki/Marco_Rossi)
- Pixel artists credited on MS1: Akio Oyabu, Susumu, Kazuhiro "Max.D" Tanaka, Tomohiro, Takeshi Okui and Kozo. — [Wikipedia – Metal Slug (1996)](https://en.wikipedia.org/wiki/Metal_Slug_(1996_video_game))
- *Metal Slug: The Ultimate History* (Bitmap Books) contains 11 staff interviews, including Kazuma Kujo, Takushi Hiyamuta, Kenji Andō and Takeshi Okui. I did not access it. — [Bitmap Books](https://www.bitmapbooks.com/products/metal-slug-the-ultimate-history)

### Inferences
- **Why the split body (inference; no developer quote found):**
  - It makes ROM and art cost additive instead of multiplicative. Pre-baking "pistol shoot-forward (10) × run legs (12)" alone would need up to 120 full-body frames, against 22 parts (own calculation).
  - Across states (idle, run, two jumps) × torso actions (idle, shoot forward/up/down, diagonals, throw, two knives) × 2 weapon sets, the savings compound.
  - The 6000-frame figure shows how much art was involved even with this saving.
- **How states combine.** Legs choose from idle / run / standing-jump / running-jump (plus fall and landing). The torso independently chooses from idle / run-bob / shoot / aim / throw / knife for the current weapon set.
  - The torso has run-specific and jump-specific variants (run torso 12, jump torsos 6, a shoot-forward variant for forward jumps). So the torso is not fully independent: it picks a variant per leg state so the shoulders bob correctly.
  - States that change the silhouette (crouch, kick, turn) switch to full-body sprites.
- **Animation rate.** Each animation frame lasts an integer number of 30 Hz ticks. If the run legs advance one frame per tick, the 12-frame run cycle lasts 0.405 s (own calculation). This was **not verified** frame by frame.
- **For the comando at 12 fps:**
  - Draw the torso so it covers the belt line by about 20% of torso height. Marco: 7–8 px of a 29-px torso ≈ 25% (own calculation).
  - Keep the legs a separate sprite shared across weapons.
  - Draw the muzzle flash into the torso frames, as MS does.

### Gaps
- No developer interview found explicitly explains *why* the body was split.
- The art books *Metal Slug Complete Art* and *The Ultimate History* were not accessible.
- Exact ticks per animation frame (run legs, idle, shoot) were not measured.
- Some sheet rows are unidentified: pistol 19-frame (y=1114) and 10-frame (y=1328) torso rows, the 4-frame leg rows (y=456, y=645/669), and full-body rows y=693 and y=778. They may be landing, run-start or turn frames.

---

## 5. Hitbox, platform edges and terrain

### Takeaway
I found no published hitbox numbers. The visible body is narrow:
- Idle feet span **21 px (0.55 H)**.
- The torso with gun is 29 px.
- The run-leg stride reaches 31 px.
- The crouch sprite is 24 px tall (0.63 H).

Touching enemies does not hurt, so hit detection matters mainly against projectiles and hazards. I found no teeter or edge-balance animation in the pistol section. Terrain is mostly continuous ground, slopes, bridges and destructible scenery, built originally around a tank.

### Cited Findings
**Sprite widths (own measurement on the rip)**
- Idle legs 21×16 px. Idle torso 29×29 px including pistol.
- Run legs 15–31 px wide across 12 frames.
- Standing-jump legs 18–21 px. Running-jump legs 26–33 px.
- Crouch full body 33–35×24 px (pistol) and ≈42–44×27 px (rifle).

**Contact damage**
- "The player does not die by coming into contact with enemies". Getting hit by enemy fire, colliding against solid stage obstacles or falling off-stage loses a life. — [Wikipedia – Metal Slug (1996)](https://en.wikipedia.org/wiki/Metal_Slug_(1996_video_game))
- "You can run into most enemies without dying." — [HG101](https://www.hardcoregaming101.net/metal-slug/)

**Terrain and edges**
- Stage maps were originally built for tank-only play. The Metal Slug was meant to move "like a living creature". — [Shmuplations MS2 interview](https://shmuplations.com/?p=19321)
- Vertical scrolling stages suit co-op poorly. — [Shmuplations MS2 interview](https://shmuplations.com/?p=19321)
- The tank can "catch the edge of a platform and still roll up onto it". — [HG101](https://www.hardcoregaming101.net/metal-slug/)
- Edge forgiveness is documented for the vehicle only. JumpLab defines "collision tolerance" as auto-avoiding small overlaps, without attributing it to MS. — [JumpLab](https://fukuchi.org/en/works/jumplab/settings-jump-collisionTolerance.html)
- No teeter or "balancing on the edge" animation appears among the pistol-section rows I inspected (y=0–2938) (own observation). Sections were labelled and scanned, but not every row was identified.

### Inferences
- Marco's idle stance (21 px ≈ 0.55 H) is much narrower than the comando's (90 px / 128 ≈ 0.70 H). Scaled to 128 px, Marco's stance would be ≈71 px (own calculation). A 44-px collision box on the comando is 0.34 H, roughly 13 px at Marco scale.
- MS likely keeps a narrow body hitbox and lets feet overhang ledges without a teeter animation. This is a plausible but **unverified** inference from sprite widths and the absence of a teeter row.
- Because body contact is harmless and bullets are the main threat, a slightly narrow, short (crouch = 0.63 H) hurtbox was probably acceptable.

### Gaps
- No player hitbox or hurtbox dimensions (standing or crouching) were found. There is no Metal Slug hitbox-viewer script, RAM map or disassembly in public sources (searched TASVideos, Data Crystal, general web).
- Ledge overhang before falling (one center ground probe vs. width-based probe) was not determined, and no footage of Marco standing on a crate edge was analyzed.

---

## 6. Differences between MS1, MS2, MSX and MS3 (movement/shooting-relevant only)

### Takeaway
Core movement, jump and shoot rules are shared. The differences are:
- MS1 has 6-round HMG bursts and no fire-rate crouch bypass.
- MS2 has heavy slowdown and a fat-state HMG sweep bug.
- MSX runs on an MS3-derived engine with less slowdown.
- MS3 adds turnaround-cancel and more transformation states.
- MS2 and later add a kick melee and four characters with identical stats.

### Cited Findings
- MS1 has only 2 playable characters. From MS2 on there are 4, and they are "almost all identical, up until Metal Slug 6". — [HG101](https://www.hardcoregaming101.net/metal-slug/)
- MS1 HMG minimum burst is 6 rounds; MS2+ is 4. — [Namu – HMG](https://namu.wiki/w/%ED%97%A4%EB%B9%84%20%EB%A8%B8%EC%8B%A0%EA%B1%B4(%EB%A9%94%ED%83%88%EC%8A%AC%EB%9F%AC%EA%B7%B8%20%EC%8B%9C%EB%A6%AC%EC%A6%88))
- The crouch fire-rate bypass does not apply to MS1, nor to pistols in MS2/X. — [SDA KB](https://kb.speeddemosarchive.com/Metal_Slug)
- MS1-only grenade trick: running into an object removes the grenade cap. — [SDA KB](https://kb.speeddemosarchive.com/Metal_Slug)
- MS2 "had extensive slowdown and performance issues". MSX "used a modified version of the engine from Metal Slug 3, which eliminated the slowdown problems". — [Wikipedia – Metal Slug 2](https://en.wikipedia.org/wiki/Metal_Slug_2)
  - Contradicted in part by the MSX TAS author: "this game unfortunately has large amounts of lag" (2-player, hardest). — [TASVideos #9815](https://tasvideos.org/9815S)
- MS2 introduced transformations (mummy, fat). In MSX you can become fat in every stage after Mission 2. — [Wikipedia – Metal Slug 2](https://en.wikipedia.org/wiki/Metal_Slug_2)
  - A fat player's HMG shoots round bullets. In MS2 a fat player could not do the diagonal HMG spray, fixed in MSX. — [Namu – HMG](https://namu.wiki/w/%ED%97%A4%EB%B9%84%20%EB%A8%B8%EC%8B%A0%EA%B1%B4(%EB%A9%94%ED%83%88%EC%8A%AC%EB%9F%AC%EA%B7%B8%20%EC%8B%9C%EB%A6%AC%EC%A6%88))
- MS3 adds branching paths and zombie/mummy/fat states (zombie blood attack does 100 per 2 frames). — [Wikipedia – Metal Slug 3](https://en.wikipedia.org/wiki/Metal_Slug_3), [TASVideos #5392](https://tasvideos.org/5392S)
- Turnaround cancel exists from MS3 onward, not in MSX. — [TASVideos #9815](https://tasvideos.org/9815S)
- MS2 and later add a kick to melee. — [Wikipedia – Metal Slug 2](https://en.wikipedia.org/wiki/Metal_Slug_2), [Wikipedia – Metal Slug 3](https://en.wikipedia.org/wiki/Metal_Slug_3)
- MS1-specific sprites: separate MS1/MS2 leg and aim-transition rows, and an air-shooting set marked "USED IN MS1" (own observation, sheet y=511/536, 2183/2227, 2384).

### Inferences
- Movement constants are probably unchanged across MS1–MS3. The TAS descriptions of jumps for MSX and MS4 match the MS1 behavior I measured: faster jumps, same-frame landing, 30 Hz timing. This is not independently measured for MS2, MSX or MS3.

### Gaps
- No per-game measurement of run speed or jump for MS2, MSX or MS3 was made.
- MSX's "Big" HMG fire rate is described only as "faster" by the [Metal Slug Wiki](https://metalslug.fandom.com/wiki/Weapons), without numbers.

---

## 7. Compact comparison table (MS1 / MS2 / MSX / MS3)

### Takeaway
One row covers most rules. Per-game rows follow only where sources show a difference. Numbers are MS1 own measurements unless noted. H = 38 px and 1 frame = 1/59.19 s.

### Inferences
- Treat MS2/MSX/MS3 movement numbers as "same as MS1", based on HG101 (identical characters) and the TAS jump descriptions. They are not re-measured.

### Gaps
- Hitbox sizes, coyote time, buffering, crouch-walk speed and HMG bullet-angle counts are unknown for all four games.

### Cited Findings
| Aspect | All four (shared) | MS1 | MS2 | MSX | MS3 |
|---|---|---|---|---|---|
| Run speed | 3 px/tick = 1.5 px/frame ≈ 89 px/s ≈ 2.3 H/s (own meas.) | measured here | same (inferred) | same (inferred) | same (inferred) |
| Acceleration | instant at 30 Hz tick granularity (own meas., inferred); 2-frame pre-hold matters ([TAS](https://tasvideos.org/9815S)) | | | | |
| Jump height / airtime | ≈59 px ≈ 1.55 H; ≈50 frames ≈ 0.84 s; 22 up / 8 apex / 22 down (running jump, own meas.) | measured | n/m | n/m | n/m |
| Jump horizontal speed | ≈2.1–2.35 px/frame (≈1.5× run); takeoff multiplier ([JumpLab](https://fukuchi.org/en/works/jumplab/settings-jump-vxAdjustmentAtTakeoff.html)) | measured | | | |
| Air control | not fully committed: horizontal speed builds in air; standing jump rises/falls faster, same landing frame ([TAS](https://tasvideos.org/9399S)); mid-air reversal and turning unverified | | | | |
| Variable jump / coyote / buffer | none documented (unknown) | | | | |
| Shoot directions and selection | fire + stick: forward; up (hold up); down only airborne; down on ground = crouch-shoot; no diagonals except HMG sweep ([Sega Retro](https://segaretro.org/Metal_Slug), [MS Wiki](https://metalslug.fandom.com/wiki/Weapons)) | HMG burst min 6 | HMG burst 4; fat player cannot sweep ([Namu](https://namu.wiki/w/%ED%97%A4%EB%B9%84%20%EB%A8%B8%EC%8B%A0%EA%B1%B4(%EB%A9%94%ED%83%88%EC%8A%AC%EB%9F%AC%EA%B7%B8%20%EC%8B%9C%EB%A6%AC%EC%A6%88))) | burst 4; sweep fixed; Big HMG | burst 4; turnaround-cancel |
| Shoot while running / in air | yes, legs keep moving (own obs.); air up-fire hits 2 frames earlier ([TAS](https://tasvideos.org/9815S)) | | | | |
| Aim lock | none; up-aim is torso-only over running legs (sheet) | | | | |
| HMG rate / ammo | 1 bullet per 4 frames ≈ 14.8/s; 200 rounds (+150 per pickup); pistol ≈ ½ HMG rate | | | | |
| Melee / grenade | context knife on fire button (30 dmg); grenade torso 6 frames over legs; 10 grenades | knife only | + kick | + kick | + kick; 2 bombs then 8-frame wait |
| Sprite construction | torso + legs composited; per-weapon torso sets (pistol, rifle); shared legs; crouch/kick/turn full-body; ~7–8 px belt overlap (own count/calc.) | own MS1 leg rows | own MS2 leg rows | (MS2 art) | same sheet reused |
| Frames: idle / run / jump / shoot | idle 4 torso + 1 legs; run 12 + 12; jump 6 + 6 (×2 types); shoot fwd pistol 10, HMG 4; up 2+10 (pistol), 2+4 (HMG); down 3+6 / 3+4; HMG diagonals 4 per quadrant (2 angles) (own count) | | | | |
| Update rate | 30 Hz logic/sprite updates (every 2nd frame) ([HG101](https://www.hardcoregaming101.net/metal-slug/); own meas.) | | heavy slowdown ([Wiki](https://en.wikipedia.org/wiki/Metal_Slug_2)) | less slowdown (MS3 engine), but TAS reports lag | |
| Hitbox vs sprite | unknown; idle feet 21 px (0.55 H), torso+gun 29 px, crouch 24 px tall; contact with enemies harmless | | | | |
| Edge behavior | no teeter animation found (own obs.); overhang tolerance unknown; terrain mostly ground, slopes, bridges | | | | |

(n/m = not measured; empty cell = same as "All four")
