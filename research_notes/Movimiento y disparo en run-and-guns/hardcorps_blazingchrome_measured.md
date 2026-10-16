# Addendum: frame-by-frame measurements of Contra: Hard Corps (Genesis, 1994; Ray Poward) and Blazing Chrome (PC, 2019; Mavra)

This addendum adds own measurements to `contra_hardcorps_blazingchrome.md`. It does not repeat that file's published facts. Every number below is **(own measurement)**, **(own count)** or **(own observation)** unless a link to a published source is given.

## How the numbers were measured

**Tools.** The built-in browser pane played the YouTube videos. Frames were read from the `<video>` element into an off-screen canvas with the browser's JavaScript tool. Nothing was downloaded and no images were saved to disk.

**Per-frame capture.** A frame index is `f = floor(t × 60)`. Frames were captured in one of two ways:
- by seeking to `(f + 0.5)/60`;
- by playing the video at 0.25–0.5× and polling `currentTime` every 4 ms.

Both methods gave identical results on a test range (frames 24918–24957 of the Hard Corps video).

**Finding the character.**
- **Static-camera arenas:** a per-pixel median background was built from 25–26 frames. The character is the connected foreground blob, picked by its costume colour: Ray's blue shirt, or Mavra's blond hair or navy suit.
- **Black backgrounds:** a brightness threshold was used instead.
- Positions are given in **native game pixels (px)**. Times are in **logic frames (f)**.

**Fitting.** Jump arcs were fitted with a least-squares parabola. Run speeds are linear regressions over many frames.

**Confidence scale.** High = many frames, clean source, results agree. Medium = few samples or a noisy detector. Low = single observation or indirect.

**Videos used:**

| ID | Video | Capture | Scale factor (video px per game px) | Used for |
|---|---|---|---|---|
| HC-A | [Contra Hard Corps Sega Genesis no death (Path E: Secret Bosses) 60fps — arronmunroe](https://www.youtube.com/watch?v=GCf_A9AXy_k) | Emulator, clean, 1600×1200 @ 60 fps, no overlays in the game area | **5.000 horizontal × 5.357 vertical**: 320×224 stretched to 4:3. Verified from where pixel edges fall: horizontal edges only at x ≡ 0 mod 5; vertical edges best fit 5.355–5.360 = 1200/224. | Ray: size, jumps, slide, aim, split body, fire rate, frame counts |
| HC-B | [Contra: Hard Corps – Ray, All Paths, No Death (No Bomb) by King iOpa](https://www.youtube.com/watch?v=rGz3VpVhUlk) | Real Genesis Model 2 + Everdrive (per the video description), 1280×720 @ 60 fps, stream overlays outside the game area | **3.02 × 3.04**: active picture spans video x 292–1258, y 27–708, for 320×224 | Ray: run speed, acceleration, turnaround |
| BC-A | [Blazing Chrome (PC) – Boss Rush [Mavra – No Miss] — CaptainGordon23](https://www.youtube.com/watch?v=y1SqrCeOehk) | PC capture, 1280×720 @ 60 fps | **3.0 × 3.0**: edges show a period of 3 video px on both axes, i.e. a native ≈426.7×240 picture. Matches the ≈427×240 found in the main file. | Mavra: size, run, jumps, roll, aim, run cycle |

**Frame-rate assumptions:**
- Hard Corps runs at 59.923 Hz ([TASVideos 2940M](https://tasvideos.org/2940M), already cited in the main file). Both Hard Corps videos are encoded at 60 fps. HC-B shows occasional duplicated or skipped frames: one +0 px step followed by one +6 px step in a 2 px/f run. HC-A showed none.
- Blazing Chrome's logic rate is **taken as 60 Hz** (own measurement). The in-game boss-rush timer read 1:27.80 at video frame 12600 and 1:42.80 at frame 13500: 15.00 s of game time in 900 video frames. Its hundredths advance in 1/60 s steps (.80 → .81 → .83 over frames 12600–12602). This is consistent with a 60 Hz frame counter but does not prove the logic rate. Confidence: medium.

**Prompt injection.** None of the pages visited (YouTube watch and search pages, one web search) contained text addressed to AI agents. tcrf.net was not visited.

---

## 1. Character size (standing height and width) and calibration

### Takeaway
Ray is **40 px tall** standing, confirming the main file's ≈40 ±3 estimate with tighter error. His body is **24 px** wide, or **41 px** including the gun aimed forward.

Mavra is **≈43–44 px tall** standing (feet to top of hair) while firing forward. That is taller than the 41 px aim-up estimate in the main file. Her body is **15–16 px** wide, or **≈32 px** with the gun.

Normalising unit used below: **H = 40 px for Ray and H = 43 px for Mavra**.

### Cited Findings
- **Ray, HC-A at 418.0 s** (frame 25080; [video t=418](https://www.youtube.com/watch?v=GCf_A9AXy_k&t=418s)):
  - The foreground blob spans rows 160–199, i.e. **40 px**, in every standing frame of the secret-boss arena. The value 160–199 repeats in hundreds of frames between 410 and 470 s.
  - Columns span 248–288 (**41 px** including the forward gun). The body alone is about 248–271 (**≈24 px**).
  - (own measurement; inputs: 5.0 × 5.357 scale, median-background segmentation; confidence **high** for height, **medium** for width.)
- **Ray, HC-B cross-check at 75.0 s** ([video t=75](https://www.youtube.com/watch?v=rGz3VpVhUlk&t=75s)):
  - A gridded zoom shows head top ≈157.3 and boot soles ≈196.5 → **≈39 px**.
  - Body ≈139–162 (≈23 px); gun tip at ≈178 (≈39–40 px total).
  - (own measurement; scale 3.02 × 3.04; confidence medium, because the 720p capture blurs pixel edges.)
- **Mavra, BC-A at 190.0 s** (frame 11400; [video t=190](https://www.youtube.com/watch?v=y1SqrCeOehk&t=190s)):
  - On a black background, the sprite spans rows 160/161–203 → **43–44 px** from top of hair to soles.
  - Body columns ≈204–220 (**15–16 px**); gun tip at ≈236 (**≈32 px** wide with gun).
  - The bright-pixel bounding box gives 160–203 × 204–235 over 190 frames of standing (frames 11373–11563).
  - (own measurement; scale 3.0; confidence **high** for height, medium for width.)

### Inferences
- The two heroes are almost the same size in pixels (40 vs 43 px). Blazing Chrome's screen is 33% wider (427 vs 320 px) and 7% taller (240 vs 224 px). So Mavra fills 18% of screen height versus Ray's 18%: nearly identical framing.

### Gaps
- No per-character size data for Sheena, Fang or Browny (not measured).

---

## 2. Run speed, acceleration, turnaround

### Takeaway
**Ray runs at exactly 2 px/f.** That is 119.8 px/s, or 3.0 H/s, in both directions. Start and stop are instant (no ramp), and turnaround takes no frames.

**Mavra runs at ≈2.09 px/f** (125 px/s, ≈2.9 H/s), also with an instant stop. In character heights per second the two games are almost identical, at ~3 H/s.

### Cited Findings
**Ray**
- **Run speed (HC-B, static boss-arena camera; [t=75](https://www.youtube.com/watch?v=rGz3VpVhUlk&t=75s)):**
  - Frames 4500–4578 (75.00–76.30 s): a head-template track moves 147 → 305 px.
  - Over 78 video frames, which contain one duplicated and one skipped pair, that is 158 px in 79 console frames = **2.00 px/f**.
  - Running left (frames 4355–4448, 72.6–74.1 s): **1.98–2.03 px/f**.
  - Camera lock checked: a background strip has its best shift at 0 px between frames 4500 and 4578.
  - (own measurement; confidence **high**.)
- **Cross-check (HC-A):**
  - Frames 25065–25083 ([t=417.75](https://www.youtube.com/watch?v=GCf_A9AXy_k&t=417s)): 217 → 253 px in 18 f.
  - Frames 26146–26157 ([t=435.8](https://www.youtube.com/watch?v=GCf_A9AXy_k&t=435s)): 44 → 64 px in 10 f.
  - Both give **2.0 px/f** (own measurement; high).
- **Unit conversions:** 2 × 59.923 = **119.8 px/s**; ÷ 40 = **3.0 H/s** (own calculation).
- **Acceleration and turnaround (HC-B):**
  - Ray stood still at x ≈ 95 facing left (frames 4449–4473), then ran right. The first moving frame already moved ≈2 px, followed by steady 2 px/f (95 → 97 → 99 → 101). The left-to-right switch shows no turn sprite and no lost frames.
  - Stop at frame 4449: the last moving step is a full 2–3 px, then x stays constant.
  - **0-frame acceleration, 0-frame deceleration, 0-frame turnaround** (own count; confidence medium-high; ±1 px template noise).
- **Air speed** equals run speed (§3).

**Mavra**
- **Run speed (BC-A, black arena; [t=188](https://www.youtube.com/watch?v=y1SqrCeOehk&t=188s)):**
  - Frames 11284–11368 (188.07–189.47 s): linear fits of the blob's left edge, right edge, midpoint and centroid give **2.090, 2.090, 2.090 and 2.098 px/f** (n = 85).
  - The capture shows frame-pacing jitter: a duplicated frame followed by a double step, e.g. centroid 69.8, 69.8, 73.8.
  - At an assumed 60 Hz: **≈125 px/s ≈ 2.9 H/s** (own measurement; confidence **high** for px per video frame, medium for px/s because the 60 Hz rate is assumed).
- **Stop:** the right edge goes 229 → 231 → 233 → 237 between frames 11368 and 11372, then is constant from 11373. The stop is instant, with no slide-to-stop (own count; medium).
- **Start acceleration and turnaround:** not measured. Mavra entered the analysed segment already running, and the hair-centroid tracker was too noisy elsewhere.

### Inferences
- 2.09 px/f is about 6.27 px per frame at 1280-wide output. Speed may be defined in a finer sub-pixel or output-resolution unit (e.g. 6.25 output px/f = 2.083 game px/f). This is unverified.
- Both games keep Contra's instant-velocity feel: no inertia at all. That fits 8-way aiming, where a diagonal press must not cause drift.
- Scaled to the comando (H = 128 px) at 60 Hz: 3.0 H/s ≈ **384 px/s ≈ 6.4 px/f** (own calculation). That is much faster than Contra NES's 1.77 H/s.

### Gaps
- Mavra's start-from-rest acceleration and turnaround frames: not measured.
- Whether Blazing Chrome's internal speed unit is fractional: not determined.

---

## 3. Jump: height, airtime, variable jump, air control, somersault vs upright

### Takeaway
**Ray (Hard Corps)** jumps in a **spinning, curled somersault**. While spinning he can fire forward, diagonally down, straight down and diagonally down-backward.
- Highest observed jump: the sprite top rises **≈85 px (2.1 H)**; airtime **≈46–48 f (0.77–0.80 s)**; apex at **≈24 f**.
- Shorter jumps were seen down to ≈73 px and 40–43 f, all with the same gravity, **≈0.30 px/f²**. This is consistent with a **variable-height jump**.
- Air control exists: a jump can start vertical and pick up 2 px/f of drift in mid-air.

**Mavra (Blazing Chrome)** jumps **upright, legs tucked**, and keeps firing forward. Her shadow stays on the floor.
- Observed rises range from **≈37 to ≈63 px (0.9–1.5 H)**, with airtime **≈30–41 f**. Again gravity is about the same, **≈0.30 px/f²**, so the jump is variable-height.
- She appears to reverse direction in mid-air.

### Cited Findings
**Ray**
- **Method:** each jump uses the sprite's top row in each frame. Standing top = 160. A parabola is fitted to the airborne frames (HC-A). "Rise" = 160 − apex top. "Airtime" = first airborne frame to landing frame, counted directly; the parabola's 160-crossings are given in brackets.

| Jump (frames) | Video time | Rise of sprite top | Airtime, counted (fit) | Apex after take-off | Fitted g (px/f²) | rms |
|---|---|---|---|---|---|---|
| 24921–24968 | [415.35 s](https://www.youtube.com/watch?v=GCf_A9AXy_k&t=415s) | **84.7 px** | 46 f (48.0) | 24 f | 0.294 | 2.0 |
| 25140–25187 | [419.0 s](https://www.youtube.com/watch?v=GCf_A9AXy_k&t=419s) | **85.1 px** | ≈47 f (48.6) | 24 f | 0.289 | 2.9 |
| 25641–25684 | [427.35 s](https://www.youtube.com/watch?v=GCf_A9AXy_k&t=427s) | 78.1 px | 43 f (45.6) | 21 f | 0.301 | 1.9 |
| 25735–25778 | [428.9 s](https://www.youtube.com/watch?v=GCf_A9AXy_k&t=428s) | 79.6 px | 43 f (44.3) | 21 f | 0.324 | 1.7 |
| 25253–25293 | [420.9 s](https://www.youtube.com/watch?v=GCf_A9AXy_k&t=420s) | 72.6 px | 40 f (42.8) | 19.5 f | 0.317 | 1.8 |

  (own measurement; inputs: scale 5.0 × 5.357, 22–42 frames per fit. Confidence: **high** for gravity and the max-jump airtime; **medium** for rise, because the curled sprite's top shifts ±3 px with rotation.)
- **Gravity:**
  - Mean fitted g ≈ **0.30 px/f²** ≈ 1,080 px/s² ≈ 27 H/s² (own calculation, ×59.923²/40).
  - One parabola fits both rise and fall with residuals ≤2.9 px rms, so **gravity is symmetric** (own inference from the fits).
- **Clearance:** at the apex of the max jumps the curled ball's bottom edge is at about row 100–105, versus the soles at 199 → **≈95 px of foot clearance (≈2.4 H)** (own measurement; medium).
- **First airborne frame:** in every jump, the frame after take-off shows the standing sprite raised 6 px (top 154, bottom 193). The curl begins the next frame (own count; high).
- **Somersault, not upright.** Zoomed frames 25644–25677 (427.4–427.95 s) show the curled body rotating between frames while firing:
  - diagonally down-right (25647);
  - straight down (25656–25665);
  - diagonally down-left (25668–25671).

  Jump 24921 shows the curled body firing diagonally down-right (24932–24956) (own observation; high).
- **Air control:**
  - In jump 24921, Ray took off from standstill. His left edge stayed at ≈61–68 px for the first ≈10 airborne frames, then moved 76 → 142 px between frames 24932 and 24966: 66 px / 34 f = **1.94 ≈ 2 px/f**.
  - Jump 25253 likewise shows ≈4 stationary airborne frames, then ≈1.8–2 px/f leftward drift.
  - Jump 25641 drifted the whole time: the shirt centroid moved 245.9 → 158.7 in 44 f = **1.98 px/f**.
  - So horizontal speed in the air equals run speed, and drift can begin after take-off (own measurement; medium-high). A mid-air *reversal* was not isolated.
- **Variable jump:**
  - The five jumps differ by 12 px of rise and 6 f of airtime under the same gravity.
  - Their time to apex matches √(2·rise/g): 85 px → 23.8 f predicted vs 24 f observed; 73 px → 22 f predicted vs 19.5 f observed.
  - This is consistent with a held-button variable jump, but input timing could not be seen (own inference; confidence **medium-low**).

**Mavra**
- **Method:** track the top of the blond hair (standing top = 161.5) and fit a parabola (BC-A, boss arena, static camera, frames 12060–14340).

| Jump (frames) | Video time | Rise of hair top | Airtime (fit) | Apex after take-off | Fitted g (px/f²) |
|---|---|---|---|---|---|
| 12427–12459 | [207.1 s](https://www.youtube.com/watch?v=y1SqrCeOehk&t=207s) | 49 px | 32.4 f | 16 f | 0.376 |
| 12767–12809 | [212.8 s](https://www.youtube.com/watch?v=y1SqrCeOehk&t=212s) | 60 px | ≈42 f (partly occluded) | 21 f | 0.270 |
| 13057–13087 | [217.6 s](https://www.youtube.com/watch?v=y1SqrCeOehk&t=217s) | 38 px | 30 f | 15 f | 0.339 |
| 13176–13210 | [219.6 s](https://www.youtube.com/watch?v=y1SqrCeOehk&t=219s) | 43 px | 33.7 f | 17 f | 0.307 |
| 13221–13259 | [220.4 s](https://www.youtube.com/watch?v=y1SqrCeOehk&t=220s) | 53 px | 38.2 f | 19 f | 0.293 |
| 13478–13510 | [224.6 s](https://www.youtube.com/watch?v=y1SqrCeOehk&t=224s) | 37 px | 31.7 f | 16 f | 0.295 |
| 13525–13566 | [225.4 s](https://www.youtube.com/watch?v=y1SqrCeOehk&t=225s) | **63 px** | **41.4 f** | 21 f | 0.295 |

  (own measurement; scale 3.0. The fits have rms 1.6–3.2 px because flowing hair moves the top ±3 px. Confidence **medium**.)
- **Gravity:** the median fitted g is **≈0.30 px/f²** (≈1,060 px/s² ≈ 25 H/s² at an assumed 60 Hz) (own calculation).
- **Range of jumps:** the highest observed rise is ≈63 px ≈ **1.47 H**, with airtime ≈41 f ≈ 0.69 s. The lowest is ≈37 px ≈ 0.86 H in ≈30–32 f.
  - The jump at 13525 shows an unusually large upward step of ≈11 px between frames 13539 and 13541. It may contain a second impulse, which would be a double jump. Double jumps are said to need the Speed drone ([HG101](https://www.hardcoregaming101.net/blazing-chrome/)), and none was identified on screen.
  - The safest "normal max" is therefore **≈53–60 px (1.2–1.4 H), 38–42 f** (own inference; low-medium).
- **Upright pose:** zoomed frames 12426–12466 and 13524–13568 show Mavra upright with legs tucked, gun level and firing forward. Her hair streams upward on the way down. Her black elliptical shadow stays on the floor under her throughout the jump (own observation; high).
- **Variable jump:** seven jumps with rises from 37 to 63 px and airtimes from 30 to 41 f, under one gravity, with time to apex scaling as √rise. This is consistent with a variable-height jump (own inference; medium-low, since inputs were not visible).
- **Air control:**
  - In jump 13176, the hair centroid moved left ≈2.3 px/f for about 12 frames, slowed, then moved right ≈2 px/f in the final ≈5 frames before landing.
  - Jump 12427 was almost vertical (x ≈ 171–178).
  - This suggests drift can be started, stopped and reversed in the air (own observation; **low-medium**, since hair motion adds noise).

### Inferences
- **Jump height:**
  - Hard Corps' max jump is about **2.1 H** (sprite top) to **2.4 H** (foot clearance). That is higher than Contra NES's 1.7 H.
  - Blazing Chrome's is a more modest **≈1.2–1.5 H**.
- **Gravity:** both games use nearly the same ≈0.30 px/f². At native pixels this is about 2.2× Contra NES's 0.137 px/f², so the arcs are much snappier.
- **Comando scaling** (H = 128 px, 60 Hz; own calculation):

  | | Max apex | Airtime | g |
  |---|---|---|---|
  | Hard Corps-like | ≈272 px | 0.8 s | ≈0.96 px/f² |
  | Blazing Chrome-like | ≈150–190 px | ≈0.65–0.7 s | ≈0.89 px/f² |

### Gaps
- **Coyote time and input buffering:** not measurable from video without input display.
- **Exact minimum (tap) jump height** in either game: the button press timing is not visible.
- **Ray mid-air reversal and Mavra's air speed:** not isolated cleanly.

---

## 4. Slide (Hard Corps) and roll/dodge (Blazing Chrome)

### Takeaway
**Ray's slide** first drops him into a prone, belly-down slide pose for ≈22 f at **≈3.6 px/f on average**. The first ≈14 f average ≈4.1 px/f (about 2× run speed). A crouched skid follows that slows from ≈1.5 to 0 px/f over ≈18 f. In total the slide covers **≈97 px (≈2.4 H) in ≈40 f (≈0.67 s)**.

**Mavra's roll** is a curled ball with a dust trail. It lasts **≈17–18 f (≈0.29 s)** at **≈3.3–3.6 px/f** (≈1.7× run speed) and covers **≈60 px (≈1.4 H)**. It ends in a 1–2 f prone pose, then she is standing ≈2 f later.

### Cited Findings
**Ray's slide** (HC-A, frames 25402–25443, [t=423.4 s](https://www.youtube.com/watch?v=GCf_A9AXy_k&t=423s)), tracked by the shirt-colour centroid:

| Phase | Frames | Sprite rows / height | Position and speed |
|---|---|---|---|
| Walking right | ≈2 px/f | | |
| Crouch-in | 25402–25403 | 169–207 / 169–199 | |
| Prone slide pose | 25404–25425 (22 f) | 176–199 (24 px tall) | Centroid 98.2 → 155.9 px by frame 25418 (57.7 px / 14 f = **4.1 px/f**), then → 173.0 by 25425 (17.1 px / 7 f = **2.4 px/f**) |
| Crouched skid | 25426–25443 (18 f) | 169–199 (31 px tall) | Centroid 178.7 → 195.7, slowing from ≈2 to ≈0.5 px/f, stopped from 25440 |
| Stands up | 25444 | 160–199 | Walks on at 2 px/f |

- Frames 25405–25417 overlap a boss sprite; positions there are interpolated.
- Totals (own measurement): **≈97 px, ≈40 f**. Confidence **medium**: the boss overlap and pose-dependent centroid shifts give ±5 px.
- The zoomed frames show Ray lying flat with the gun forward while sliding (own observation; high).

**Mavra's roll** (BC-A, frames 13707–13728, [t=228.4 s](https://www.youtube.com/watch?v=y1SqrCeOehk&t=228s)):
- **Sequence** (own observation of zoomed frames):
  - 13707: crouch;
  - 13708–13724: curled ball, rows 183–202 (≈20 px tall), with a grey dust cloud trailing;
  - 13726: prone, firing backward;
  - 13728: standing.
- **Speed:** the costume-pixel centroid moves 177.7, 179.9, 184.6, 188.5, 191.7, 196.7, 199.3, 201.5, 203.5, 207.5 over frames 13708–13717. That is 29.8 px / 9 f = **3.3 px/f** (own measurement).
- **Distance:** the ball's position in zoomed frames (≈175 → ≈237 px) gives **≈60–65 px** (own measurement).
- Confidence **medium-low**: other blue and yellow objects contaminate frames 13718–13725.

### Inferences
- Both evasive moves travel about 1.5–2× run speed. Hard Corps' slide is a longer commitment (≈0.67 s, 2.4 H). Blazing Chrome's roll is short and snappy (≈0.3 s, 1.4 H) and ends in a fire-capable prone frame.
- For the comando (H = 128), the corresponding move covers ≈180–310 px.

### Gaps
- Invulnerability windows: frame data needs hit events (not observable here).
- Slide/roll variants (Browny's long slide, Fang's short slide; Doyle vs Mavra): not measured.
- Whether the roll can be cancelled early: the developer says it can ([Steam thread](https://steamcommunity.com/app/609110/discussions/0/1643168364650459700)), but no cancel was isolated.

---

## 5. Shooting: aim directions per state, split vs full-body, fire rate

### Takeaway
**Ray:**
- Standing: forward, straight up, diagonal-up, diagonal-down. A kneeling forward shot also appears.
- Running: forward, diagonal-up, diagonal-down.
- In the air (somersault): forward, diagonal-down, straight down and diagonal-down-backward were seen.
- In **Type II** (HUD "SHOT·II") he plants in a wide stance and aims diagonal-up or straight up.
- **When the aim changed mid-run (forward → diagonal-up), the leg cycle kept going without interruption.** The legs reuse the same drawings regardless of aim angle. That is strong evidence of a **split torso/legs construction**, as in Contra NES.
- Slot-A gun fire rate ≈ **15 shots/s** (one shot per 4 f).

**Mavra:**
- Standing forward; standing **diagonal-up in a planted wide stance** (lock mode); running forward.
- Airborne: forward. Prone: fire after the roll.
- Split vs full-body: not determined.

### Cited Findings
**Ray**
- **Aim set seen** (HC-A zoomed frames; own observation):

| State | Aims seen | Frames / time |
|---|---|---|
| Standing | Forward | Frame 25080, [418 s](https://www.youtube.com/watch?v=GCf_A9AXy_k&t=418s) |
| Walking | Diagonal-down | 25398 |
| Kneeling | Forward | 25402 |
| Running | Forward | 27768–27781 |
| Running | Diagonal-up | 27782–27795, [463 s](https://www.youtube.com/watch?v=GCf_A9AXy_k&t=463s) |
| Standing, Type II wide stance | Diagonal-up | 27626, 27641, 27796, 27821, 27862, 28067 |
| Standing, Type II wide stance | Straight up | 27646, 27800 |
| Airborne (somersault) | Diag-down-right, straight down, diag-down-left | 25647, 25656–25665, 25668–25671 |
| Airborne (somersault) | Forward, diag-down | Jump 24921 |

- **HUD shot type:** "SHOT·II" at 27641 (460.7 s) and 27821 (463.7 s), with weapon slot C; "SHOT·I" at 24700 and 25440, with slot A (own observation). This ties the planted wide-stance diagonal and up poses to Type II, matching the manual's description in the main file.
- **Split-body test** (HC-A frames 27766–27800, [462.8–463.3 s](https://www.youtube.com/watch?v=GCf_A9AXy_k&t=462s)):
  - **Method:** the leg region (rows 182–199, 40 px wide, aligned to Ray) was compared frame to frame, as the count of changed mask pixels at the best ±6 px shift.
  - **Leg timing:** leg drawings change only at frames 27768, 27776, 27784, 27792 and 27800, i.e. exactly every 8 f (Δ = 122–186). In between, Δ ≤ 15.
  - **Aim change:** the gun went from forward to diagonal-up at **frame 27782**. The sprite top went 160 → 153 and the right edge pulled in from 93 to 86. The legs did not change at that frame (Δ = 7) or the next (Δ = 10). The next leg change came at the regular 27784.
  - **Shared leg drawings:** leg masks under diagonal-up aim match forward-aim run legs from other runs almost exactly.
    - Frame 27772 matches 24536 and 25068 (Δ = 9).
    - Frames 27776/27780 match 24544 and 25076 (Δ = 5–9).
    - Frames 27784/27788 match 25083 and 25462 (Δ = 12–15).
  - Conclusion: **legs keep cycling uninterrupted through an aim change, and leg art is shared across aims** (own measurement; confidence **high** for this one event).
- **Fire rate, slot-A gun, Type I** (HC-A frames 25445–25467, [424.1 s](https://www.youtube.com/watch?v=GCf_A9AXy_k&t=424s), and standing fire 25478–25544):
  - Muzzle flash and a new bullet appear every **4 f**: flash on 25447, 25451, 25455, 25459, 25463.
  - While standing and firing, the sprite's right edge repeats a 4-frame pattern (196, 205, 204, 211).
  - Result: **15 shots/s** (own count; confidence medium-high).
  - HC-B at 72.6 s shows the same 4-frame (2 + 2) alternation while standing and firing.

**Mavra**
- **Aim set seen** (BC-A pose catalogue, frames 12080–14255, one sample per 75 frames, plus jump and roll sequences; own observation):

| State | Aims seen | Frames |
|---|---|---|
| Standing, legs together | Forward | 12380, 12605, 13355 … |
| Standing, wide planted stance | **Diagonal-up**, right and left facings | 12080, 12155, 12230, 12305 ([201–205 s](https://www.youtube.com/watch?v=y1SqrCeOehk&t=201s)) |
| Running | Forward | 11280–11372, 12905, 13430, 13655 |
| Airborne | Forward | 12426–12466, 13524–13568 |
| Prone | Firing backward (after a roll) | 13726 |

- Standing diagonal aim fits the lock button described in the main file. The lock button press itself is not visible in the video.
- **Running diagonal aims:** not seen in the sampled frames. A Steam screenshot in the main file shows one.

### Inferences
- **Ray's construction:**
  - Torso swaps happen inside a leg hold, and leg drawings are shared across aim angles.
  - Hard Corps very likely uses the same **torso-over-shared-legs** construction documented for Contra NES, with a separate wide-stance standing set for Type II.
  - For the comando this is the strongest precedent: one leg cycle plus one torso set per aim angle.
- **Ray's air poses:** they need no dedicated aim art per angle in the classic sense. The curled ball's rotation frames cover the directions, much like Contra NES.

### Gaps
- **Blazing Chrome split vs full-body:** not determined. No run with a mid-run aim change was found in the sampled footage.
- **Fire rates:** Blazing Chrome's default-gun rate was not measured, because the boss-rush run uses a plasma weapon. Hard Corps' Type II rate and other weapons: not measured.
- **Directions not observed** (absence in samples, not proof of absence):
  - Ray: diagonal-up or straight up in the air; straight down standing in Type II.
  - Mavra: up in the air; straight down.

---

## 6. Animation frame counts and hold durations

### Takeaway
**Ray's run** changes leg drawing every **8 f** (7.5 fps), like Contra NES. At least 4 distinct leg drawings were found; the cycle length was not closed. Standing still shows **no idle animation** (one static frame for 300+ f). The forward firing pose cycles a **4-frame** muzzle-flash loop.

**Mavra's run** is a **6-drawing cycle of 33 f** (holds alternate 5 and 6 f; ≈5.5 f average ≈ 10.9 fps). Standing still also shows **no idle animation** (190 f static).

### Cited Findings
**Ray's run** (HC-A; leg-mask method of §5; own count):
- **Leg changes every 8 f:** frames 24534 → 24542 → 24550 (stop); 25066 → 25074 → 25082; 25452 → (25460) → 25468; 27768 → 27776 → 27784 → 27792 → 27800.
- **Distinct drawings:** clustering by mask distance gives:
  - D1: 24536, 25068, 27772;
  - D2: 24544, 25076, 25454, 27776;
  - D4: 25083, 25462, 27784;
  - D5: 27792;
  - plus a standing/stop pose, 24550.
- The order D1 → D2 → D4 → D5 repeats across runs. So **≥4 run drawings × 8 f**; a full cycle is ≥32 f. Confidence: **high** for 8 f per drawing, **medium** for the drawing count.

**Ray idle:** at frames 24600–24902 (410.0–415.0 s) the bounding box stays 160–199 × 62–101 with no change (own count; medium: he was not firing; a very slow idle could exist beyond 5 s).

**Ray firing pose:** standing Type I forward fire repeats a 4-frame pattern (§5).

**Ray jump:** the sprite rotates continuously in the curl. Rotation drawing count and timing: not resolved.

**Ray landing:** after the somersault the standing sprite appears 4 px high and settles 1 px/f over ≈4 f, at frames 25293–25297 and 27766–27771 (own count; medium). This reads as a short landing settle.

**Mavra's run** (BC-A frames 11290–11370, [188.2–189.5 s](https://www.youtube.com/watch?v=y1SqrCeOehk&t=188s), black background; leg mask rows 180–205; own count):
- **Drawing changes** at 11292, 11297, 11303, 11308, 11314, 11319, 11325, 11331, 11336, 11342, 11347, 11353, 11358, 11364, 11369. Each change has Δ = 118–191; Δ ≤ 1 between changes.
- **Holds:** 5, 6, 5, 6, 5, 6, 6, 5, 6, 5, 6, 5, 6, 5 f.
- **Cycle:** the distance matrix repeats every 6 drawings (11292 ≈ 11325 ≈ 11358, Δ = 2–7) → **6 drawings per 33 f (0.55 s)**.
- Confidence: high for the drawing count and cycle length. The 5/6 alternation could be capture pacing or real fractional timing (5.5 f).
- **Stride:** 33 f × 2.09 px/f ≈ **69 px per cycle ≈ 1.6 H** (own calculation).

**Mavra idle:** at frames 11373–11563 (189.6–192.7 s) the bounding box is constant at 160–203 × 204–235 (own count; medium).

**Mavra jump:** a single tucked pose while rising. The hair changes to stream upward while descending, around the apex (frames 12452–12462). Separate drawing counts: not resolved.

### Inferences
- Hard Corps keeps Contra's 8-frame (7.5 fps) run timing. Blazing Chrome runs its cycle at ≈11 fps with 6 drawings, closer to the comando's 12 fps target.
- At 12 fps (5 f per drawing), a 6-drawing cycle = 30 f = 0.5 s, almost exactly Mavra's 33 f.

### Gaps
- Ray's full run-cycle length and somersault drawing count/timing.
- Mavra's jump, firing-pose and roll frame counts.
- Hard Corps characters other than Ray.

---

## 7. Edge behaviour (overhang past platform edges, teeter)

### Takeaway
Not measured for either game. The analysed footage (static boss arenas with flat floors) contains no slow walk-off or stand-at-edge events.

### Cited Findings
- None (no edge events in the frames analysed: HC-A 405–476 s and 462–464 s; HC-B 70–78 s; BC-A 186–239 s).

### Inferences
- None.

### Gaps
- Edge overhang in px and as a fraction of sprite width, and any teeter animation, for both games. This would need stage footage with ledges (e.g. Hard Corps stage 1 rooftops, Blazing Chrome mission platforms) and per-frame foot-to-edge measurement against a scroll-compensated background.

---

## 8. Compact table (own measurements; one row per game; columns as in the main file's table)

### Takeaway
The table below fills the main file's empty cells with this addendum's measurements. "own" = own measurement or count with the inputs above. "nm" = not measured.

### Cited Findings
Sources for each cell: §1–§6 above; videos [HC-A](https://www.youtube.com/watch?v=GCf_A9AXy_k), [HC-B](https://www.youtube.com/watch?v=rGz3VpVhUlk), [BC-A](https://www.youtube.com/watch?v=y1SqrCeOehk).

| Game | Native res / logic rate / H | Run speed | Acceleration | Prone / crouch move | Jump height / airtime | Gravity | Air control | Variable jump / coyote / buffer | Drop-through | Shoot directions and selection | Shoot while running / air | Aim lock | Fire rate / cap | Sprite construction | Frames / timing | Hitbox vs sprite | Edge behavior | Bullet origin |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Contra: Hard Corps (Ray) | 320×224 / 59.923 Hz / **H = 40 px** (own; body 24 px, 41 px with gun) | **2.00 px/f = 119.8 px/s = 3.0 H/s** (own, high) | Instant start and stop; 0 f turnaround (own, medium-high) | Kneel fire seen. Slide: prone pose ≈22 f at ≈4.1 → 2.4 px/f, then crouch skid ≈18 f; **≈97 px (2.4 H) in ≈40 f** (own, medium) | Max: sprite-top rise **≈85 px (2.1 H)**, foot clearance ≈95 px; **46–48 f (0.78–0.80 s)**; apex at 24 f. Shorter jumps seen: 73–80 px, 40–43 f (own) | **≈0.30 px/f²** (0.289–0.324), symmetric (own, high) | Yes: 2 px/f (= run speed); drift can start mid-air (own, medium-high) | Likely variable height (5 jumps, 73–85 px, one gravity; own, medium-low) / coyote and buffer nm | nm | Standing: fwd, up, diag-up, diag-down, kneel-fwd. Run: fwd, diag-up, diag-down. Air (spin): fwd, diag-down, down, diag-down-back (own observation) | Yes / yes (from the spinning ball) | Type II = planted wide stance, diag-up and up seen with HUD "SHOT·II" (own) | Slot-A gun: **15 shots/s** (1 per 4 f) (own, medium-high); cap nm | **Split torso/legs (evidence):** legs keep their 8 f cycle through a mid-run aim change; leg drawings shared across aims (own, high) | Run: **8 f per leg drawing (7.5 fps)**, ≥4 drawings. Idle: static. Fire: 4 f loop. Landing settle ≈4 f. Jump: rotating curl (own) | nm | nm | nm |
| Blazing Chrome (Mavra) | ≈427×240 (3.0× at 720p) / ≈60 Hz (timer-based, own) / **H ≈ 43 px** (own; body 15–16 px, ≈32 px with gun) | **≈2.09 px/f ≈ 125 px/s ≈ 2.9 H/s** (own, high) | Instant stop (own, medium); start nm | Roll: curled ball ≈17–18 f at ≈3.3–3.6 px/f, **≈60 px (1.4 H)**, ends prone 1–2 f (own, medium-low) | Rise **≈37–63 px (0.9–1.5 H)**, airtime **≈30–41 f**; apex at 15–21 f; normal max ≈53–60 px / 38–42 f (own, medium) | **≈0.30 px/f²** (median of 7 fits) (own, medium) | Likely yes; mid-air reversal seen once (own, low-medium) | Likely variable height (7 jumps, one gravity; own, medium-low) / coyote and buffer nm | nm (published: none) | Standing: fwd; planted wide stance diag-up (lock). Run: fwd. Air: fwd. Prone: fwd after roll (own observation) | Yes / yes (upright, gun level) | Planted wide-stance diagonal seen (lock implied; button not visible) | nm (boss rush used a plasma weapon) | nm (no mid-run aim change found) | Run: **6 drawings / 33 f** (5–6 f holds ≈ 10.9 fps); stride ≈69 px (1.6 H). Idle: static. Jump: tucked upright pose, hair flips on descent (own) | nm | nm | nm |

### Inferences
- The two games share almost the same run pacing (≈3 H/s) and gravity (≈0.30 px/f²). They differ mainly in jump height (Hard Corps ≈2.1 H vs Blazing Chrome ≈1.2–1.5 H) and jump style (spinning curl vs upright).
- Hard Corps keeps Contra's construction and timing (split legs, 8 f steps). Blazing Chrome animates at ≈11 fps.

### Gaps
- Not measured in this pass:
  - hitboxes;
  - edge overhang;
  - bullet origins;
  - coyote time and buffering;
  - Blazing Chrome fire rate, split-body test, acceleration and turnaround;
  - Ray's full run-cycle length.
- Every value in this addendum is an own measurement from three YouTube captures. There is no RAM or disassembly cross-check, and inputs are not visible. Treat the "variable jump" and "air control" conclusions as inferences from motion only.
