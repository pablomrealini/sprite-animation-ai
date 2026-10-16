# Movement, jumping and 8-way shooting in Contra (NES, 1988), Contra: Hard Corps (Genesis, 1994) and Blazing Chrome (2019)

Conventions used below. **H** = the standing player sprite height of that game, used to normalize distances ("character heights"). "px/f" = pixels per logic frame. Values marked **(own calculation)**, **(own measurement)**, **(own reading)** or **(own observation)** are derived by the researcher; inputs are shown. "Disasm" = the annotated Contra (US) NES disassembly by vermiceli ([repo](https://github.com/vermiceli/nes-contra-us)); line anchors point to the `main` branch as fetched on 2026-10-15. The disassembly was read as text, nothing from it was run. Sprite images were downloaded only to scratch space and measured with a small PNG decoder; nothing was copied into the repo.

Source quality: Contra NES numbers come from primary code (the disassembly), so they are exact. Contra: Hard Corps numbers come from the official US manual plus secondary sources; no RAM map, disassembly or hitbox script was found. Blazing Chrome has no published technical data; its numbers are mostly own measurements from official Steam screenshots plus developer replies on Steam. Sega Retro, Giant Bomb, TV Tropes, StrategyWiki, the Contra Fandom wiki and The Spriters Resource all refused automated access (403, Anubis or Cloudflare bot-check, not bypassed). Claims from those sites are taken from search-engine excerpts and flagged as such.

## 1. Movement: run speed, acceleration, prone/crouch movement, dash/slide

### Takeaway
Contra NES moves the player at a fixed 1 px/frame: speed is set fresh every frame, with no acceleration or deceleration. That is 60.1 px/s ≈ 1.77 H/s for a 34 px sprite. There is no crawl, dash or slide. Contra: Hard Corps adds a slide (diagonal-down + jump) that is invulnerable, damages enemies and is faster than walking, and it varies by character. Blazing Chrome adds a dodge roll (Down + Jump). No run-speed numbers were found for Hard Corps or Blazing Chrome.

### Cited Findings
**Reference frames**
- NES: 256×240, 60.0988 Hz NTSC logic/refresh rate. These are the values given in the assignment and the standard NESdev figures ([NESdev cycle reference chart](https://www.nesdev.org/wiki/Cycle_reference_chart)). Contra runs its player logic once per frame through `player_state_routine_01_logic` ([disasm bank7 L4269](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4269)).
- Genesis framerate is 59.923 fps, not 60. A TASVideos author notes the previous Hard Corps movie had used an inaccurate 60 ([TASVideos 2940M](https://tasvideos.org/2940M)). The 320×224 resolution is the value given in the assignment and was not independently re-verified here.
- Blazing Chrome internal resolution is ≈427×240, i.e. a 4.5× nearest-neighbour upscale to 1920×1080 **(own measurement)**. Inputs: in official 1920×1080 Steam screenshots ([Steam store](https://store.steampowered.com/app/609110/Blazing_Chrome/)), strong luminance edges fall only on positions 0/8 and 3/4 mod 9 horizontally and 0/1 and 4/5 mod 9 vertically. Positions 1, 2, 5, 6 and 7 mod 9 have none. That pattern fits native pixels 4.5 screen-px wide and rules out integer 4×, 5× or 6× scaling: 1920/4.5 ≈ 427 and 1080/4.5 = 240. The engine is GameMaker Studio ([Wikipedia: Blazing Chrome](https://en.wikipedia.org/wiki/Blazing_Chrome), [GameMaker showcase](https://gamemaker.io/en/showcase/blazing-chrome); both seen via search listing). The logic rate is **not found** (60 Hz is likely but unsourced).

**Standing heights (H)**
- Contra NES: standing sprite `sprite_0f` (gun level, legs together) is 23×34 px of opaque pixels **(own measurement)** of the disassembly's sprite-library render ([sprite library](https://github.com/vermiceli/nes-contra-us/tree/main/docs/sprite_library)), so **H = 34 px**. Other poses measured the same way: stand-aim-up `sprite_16` 14×45 (gun raised above head); prone `sprite_17` 32×16; somersault `sprite_08` 16×20 and `sprite_09` 19×16; run frames `sprite_02`–`06` 16–20 px wide × 31–35 px tall; run-and-aim-forward `sprite_0d`/`0e` 25×34 and 25×32; run-aim-diag-up `sprite_10`–`12` 16–20×33–35; run-aim-diag-down `sprite_13`–`15` 20–21×33–35.
- Hard Corps: Ray is ≈40 px tall (±3) standing with gun level **(own measurement)**. Inputs: Wikipedia's gameplay screenshot is 365×273 ([file page](https://en.wikipedia.org/wiki/File:Contra_Hard_Corps_(gameplay).png)), assumed to be resampled from 320×224 (vertical factor 1.219). Head-to-feet measures ≈49.3 image px, and 49.3 / 1.219 ≈ 40.4. His body is ≈24 px wide without the gun and ≈39 px including it. These are low-confidence values because the image is resampled.
- Blazing Chrome: Mavra standing and aiming straight up is ≈41 px from head to feet (±2) **(own measurement)**, from 185 screen px / 4.5 in Steam screenshot `ss_431521…`. Her body is ≈15 px wide in that pose. Doyle in a wide firing stance is ≈46 px (205 screen px / 4.5, rough, partly occluded).

**Contra NES speed and acceleration**
- `PLAYER_X_VELOCITY` is cleared to 0 every frame before input is read ([bank7 L4359–4365](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4359)). It is then set to #$01 or #$ff (±1 px/frame integer) if Right or Left is held ([`handle_d_pad` L4560](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4560), [`set_player_positive_x_velocity` L4643](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4643)). Acceleration is therefore instant in both directions. RAM docs describe this variable as the fast X velocity with values #$00, #$01 or #$ff ([ram.asm](https://github.com/vermiceli/nes-contra-us/blob/main/src/ram.asm)).
- **Run speed = 1 px/f = 60.1 px/s = 1.77 H/s** **(own calculation)**: 60.0988 × 1, divided by 34.
- Horizontal air speed and edge-fall speed reuse the same ±1 px/f setter ([`set_x_velocity_from_a_code` L4774–4790](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4774)), so speed is the same on the ground and in the air.
- On a non-hazardous moving enemy (mine cart, floating rock), a carry boost `PLAYER_FAST_X_VEL_BOOST` is added to the player's X velocity ([`calc_player_x_vel` L4373](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4373)).
- Outdoor screen clamp: player X is kept between #$1a and #$e6 (26–230 px) ([L4444–4452](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4444)).
- **Prone/crouch:** Down alone with no Left or Right selects sprite sequence #$02 (prone) and leaves X velocity at 0 ([`handle_d_pad` L4560–4575](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4560)). Down+Left or Down+Right instead sets ±1 px/f and the aim becomes diagonal-down (see §3). **There is no prone crawl** **(own reading)**.
- In water, X velocity is not applied while Down is held, and the player cannot move while ducking ([`set_player_x_vel_to_a` L4651](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4651)).
- **No dash or slide routine exists** in the player state code **(own reading** of `handle_player_state` [L4454](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4454)).

**Contra: Hard Corps**
- **Slide:** pressing jump (C) while holding diagonal-down performs a slide. The player cannot be damaged during it and it can be used to attack enemies (official US manual p.11, [PDF](https://manuals.sega.com/genesismini/pdf/CONTRA_HARD_CORPS.pdf); same summary in [Wikipedia](https://en.wikipedia.org/wiki/Contra:_Hard_Corps) citing the manual).
- A TASVideos submission's Chinese-language notes describe the slide as invincible, damaging, and faster than normal walking ([TASVideos 6177S](https://tasvideos.org/6177S); machine-paraphrased).
- Per-character slide: Browny is the smallest character and has the longest slide (Sega Retro, [page](https://segaretro.org/Contra:_Hard_Corps), seen only as a search excerpt). Fang is described as large-bodied, an easier target, with a weaker slide; Browny is small, a harder target, with a strong slide (Giant Bomb, [page](https://www.giantbomb.com/games/3030-13902/), search excerpt only).
- The characters can climb walls and move along ceilings (manual p.11).
- **Run speed and acceleration: not found.**

**Blazing Chrome**
- **Dodge roll:** Down + Jump grants temporary invincibility per [HG101](https://www.hardcoregaming101.net/blazing-chrome/). One review says the roll is *not* invulnerable ([Wccftech review](https://wccftech.com/review/blazing-chrome-a-hard-corps-afternoon/amp/)). **Conflict unresolved.**
- A JoyMasher developer ("IURI", tagged [developer] on Steam) said a roll can be cancelled by pressing the opposite direction. He also said that rolling being blocked while holding the Aim button was already fixed internally for a coming patch ([Steam discussion, July 2019](https://steamcommunity.com/app/609110/discussions/0/1643168364650459700)).
- The Speed assist drone makes the player faster and grants double jumps ([HG101](https://www.hardcoregaming101.net/blazing-chrome/)). The unlockable melee characters Raijin and Suhaila move more quickly ([HG101](https://www.hardcoregaming101.net/blazing-chrome/)). Mavra and Doyle play identically ([HG101](https://www.hardcoregaming101.net/blazing-chrome/)).
- **Run speed, acceleration, roll distance and duration: not found.**

### Inferences
- Contra NES uses digital movement only: the speed is a single integer constant and there is no inertia state. That makes 8-way aim selection trivial, because a diagonal press always means "move + aim diagonal" (see §3).
- Scaled to the comando (H = 128 px) at 60 Hz, Contra's 1.77 H/s is ≈226 px/s ≈ 3.8 px/frame **(own calculation)**.

### Gaps
- Hard Corps and Blazing Chrome run speed, acceleration, and slide/roll speed, distance and frame counts: not found. The only route would be frame-stepping gameplay video or an emulator RAM search, which was not done.
- Blazing Chrome logic rate: not found.

## 2. Jump: height, airtime, air control, facing, gravity, variable jump, coyote time, buffering, drop-through, jump hitbox

### Takeaway
Contra NES has a fixed-height somersault jump of ≈58–59 px (≈1.7 H) and ≈59 frames (0.98 s) airtime, with gravity symmetric on the way up and down. There is no variable height, no coyote time and no input buffer. Air control is "sticky": once a horizontal direction is pressed in the air, drift continues at 1 px/f until landing even after release. It can be reversed instantly but never cancelled to zero. Down+A drops through floors. Hard Corps adds Browny's hover/double jump and drop-down from moving objects and walls. Blazing Chrome uses an upright (non-somersault) jump, has no drop-through, and only gets double jumps from a power-up. No jump numbers were found for Hard Corps or Blazing Chrome.

### Cited Findings
**Contra NES**
- **Take-off velocity.** `set_jump_status_and_y_velocity` loads fast/fractional Y velocity #$fb/#$f0 outdoors and #$fc/#$90 indoors ([bank7 L4533](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4533)). The disassembly comments read these as "-5.94" and "-4.56". The position update instead adds the fractional byte into an accumulator and carries into the fast byte (`player_jumping_set_y_pos`, [L5114](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L5114)). The effective two's-complement values are therefore **−4.0625 px/f outdoors** (−5 + 240/256) and **−3.4375 px/f indoors** (−4 + 144/256) **(own calculation; disagrees with the comment's interpretation)**.
- **Gravity:** `apply_gravity` adds #$23/256 = 0.1367 px/f² every airborne frame ([L5139](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L5139)). The same routine runs while rising and falling, so **there is no gravity asymmetry**. The routine contains no terminal-velocity clamp **(own reading)**. In SI-like units this is v0 ≈ 244 px/s (7.2 H/s) and g ≈ 494 px/s² (14.5 H/s²) **(own calculation**: ×60.0988 and ×60.0988²; /34).
- **Height and airtime** **(own calculation**: a frame-exact simulation of `apply_gravity` then `player_jumping_set_y_pos`, over all 256 possible values of the never-cleared accumulator `PLAYER_JUMP_COEFFICIENT`):
  - Outdoors: apex **58–59 px = 1.71–1.74 H** at frame 26–29 (0.43–0.48 s). The player is back at take-off height at **frame 59 (0.98 s)**.
  - Indoors (base levels): 41–42 px (1.2 H), 49–50 frames.
  - The 1 px spread comes from `PLAYER_JUMP_COEFFICIENT` not being cleared between jumps, which the disassembly notes speedrunners exploit to jump higher ([ram.asm L658](https://github.com/vermiceli/nes-contra-us/blob/main/src/ram.asm#L658)).
- **Horizontal reach on flat ground:** ≈59 px ≈ 1.74 H **(own calculation**: 59 frames × 1 px/f).
- **Variable jump: none.** After take-off, `handle_jump` never reads the A button; it only applies gravity, checks ceiling and floor collision, and reads Left/Right ([L4708–4765](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4708)) **(own reading)**.
- **Hitting a ceiling:** a solid tile 10 px above the anchor zeroes the Y velocity while ascending ([L4733–4746](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4733)).
- **Air control (verified).** Each airborne frame, `get_x_velocity_d_pad_code` returns #$20 for Right or #$40 for Left. That value is OR-ed into `PLAYER_JUMP_STATUS` bits 5/6 after clearing them, but only when a direction is pressed; with no direction pressed, the old bits are kept ([L4759–4772, L4785–4798](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4759)). The bits then set X velocity to ±1 px/f ([`set_x_velocity_from_a_code` L4774](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4774)). Results **(own reading)**:
  - A neutral jump rises straight up.
  - Pressing a direction at any point starts a 1 px/f drift that **persists after release** until landing.
  - Pressing the opposite direction reverses the drift instantly; there is no way back to zero drift in mid-air.
  - Take-off sets only the facing bit (#$11 right / #$91 left), so a running jump gets its drift from the d-pad on the next frame.
- **Facing in air:** the somersault sprite's horizontal flip comes from bit 7 of `PLAYER_JUMP_STATUS`, which is set only at take-off ([`set_player_jump_sprite`, bank2 L1039](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank2.asm#L1039)). Aim direction, however, is recomputed from the d-pad every frame (§3). So reversing in mid-air does not flip the spinning ball, but bullets fire in the new direction. On landing the sprite flip is re-synced to the aim direction ([`player_land_on_ground` L4847](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4847)).
- **No input buffering:** a jump starts only on a frame where A is *newly pressed* (`CONTROLLER_STATE_DIFF`) while grounded ([L4485–4495](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4485)). A press made in the air is not stored **(own reading)**.
- **No coyote time.** Per-frame order is aim → `check_player_ledge` → fire → movement ([L4269–4273](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4269)). `check_player_ledge` sets `EDGE_FALL_CODE` on the first frame the floor probe is empty ([L5038](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L5038)). `handle_player_state` then takes the edge-fall branch before it ever reads A ([L4454–4475](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4454)). That leaves **0 frames** of coyote time **(own reading)**.
- **Walking off a ledge:**
  - The player keeps moving 1 px/f in the facing direction (`EDGE_FALL_CODE` #$21 right / #$41 left).
  - X direction cannot be changed until the player has fallen 20 px (#$14) below the ledge (`PLAYER_FALL_X_FREEZE`, [L4509–4530](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4509), [L4681–4706](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4681)). From rest under this gravity, that freeze lasts ≈17 frames **(own calculation**: √(2·20/0.1367)).
  - The falling player is drawn with one non-spinning frame, `sprite_05` (a walk frame) ([bank2 L1020](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank2.asm#L1020)).
- **Drop-through (Down + A):**
  - If only Down is held when A is pressed, the game calls `can_player_drop_down` ([L4485–4500](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4485)). Dropping is refused if the tile 16 px below is solid, or if no floor or water exists anywhere below down to the screen bottom; vertical levels always allow it ([L5276–5330](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L5276)). When refused, nothing happens (no jump).
  - A successful drop uses `EDGE_FALL_CODE` #$81, which has no X drift for the first 20 px of fall.
  - Down-diagonal + A is a normal jump.
- **Jump hitbox:** while airborne the player's hurt region shrinks to ≈12×12 px versus 10×31 standing (details in §5). It sits around the ball center.

**Contra: Hard Corps**
- C jumps (manual p.10). Pressing straight Down + C while standing on a moving object, or while hanging from a wall or ceiling, makes the character jump down (manual p.11, [PDF](https://manuals.sega.com/genesismini/pdf/CONTRA_HARD_CORPS.pdf)). The manual does not describe dropping through ordinary floors.
- Browny hovers when C is pressed during a jump (manual p.17). He is described as able to double jump/hover but with weaker individual jumps than the other characters (TV Tropes, [page](https://www.tvtropes.org/pmwiki/pmwiki.php/VideoGame/ContraHardCorps), search excerpt only). His jetpack is said to give a short vertical boost before he floats down (Sega Retro excerpt).
- **Jump height, airtime, air control, somersault frame count, coyote time and buffering: not found.**

**Blazing Chrome**
- **Upright jump, no somersault.** Official screenshots show Doyle airborne in an upright pose firing horizontally, and Mavra airborne upright. Black drop-shadow ellipses mark the airborne characters' ground position **(own observation**, Steam screenshots `ss_b311215c…` and `ss_bf35ebc1…`, [store page](https://store.steampowered.com/app/609110/Blazing_Chrome/)).
- **No drop-through platforms.** A player says the game was designed without drop-down. The developer (IURI) calls adding it a big change, proposes a "Type B" scheme mapping Down+Jump to drop-down with roll on another button, and says he will discuss it with Danilo (Dias). Players in 2022 report the Type B option is greyed out ([Steam discussion](https://steamcommunity.com/app/609110/discussions/0/1643168364650459700)).
- Down+Jump is the roll. A player reports that jumping while aiming diagonally down while running produces a roll instead of a jump ([same thread](https://steamcommunity.com/app/609110/discussions/0/1643168364650459700), via search excerpt). The developer says jumping is blocked in some roll situations because players would otherwise jump accidentally ([same thread](https://steamcommunity.com/app/609110/discussions/0/1643168364650459700)).
- Double jump is available only from the Speed drone ([HG101](https://www.hardcoregaming101.net/blazing-chrome/)) or a boots power-up ([Worthplaying review](https://worthplaying.com/article/2019/10/30/reviews/116742-pc-review-blazing-chrome/)).
- **Jump height, airtime, air control, variable jump, coyote time and buffering: not found.**

### Inferences
- Contra's "sticky drift" air control is very forgiving for an 8-way shooter. The player can aim freely in the air (§3) without accidentally killing horizontal momentum, because only a real direction press changes drift. A modern design would likely add coyote time and buffering that Contra lacks.
- Contra's take-off velocity is effectively −4.06 px/f, not the −5.94 the comment suggests. Anyone reusing these constants should use the simulated 58–59 px apex, not the comment.
- Scaled to the comando: Contra ≈ 1.72 H ≈ 221 px apex and ≈1 s airtime. Gravity is ≈14.5 H/s² ≈ 1,860 px/s² and v0 ≈ 7.2 H/s ≈ 920 px/s **(own calculation**, ×128).

### Gaps
- Hard Corps and Blazing Chrome jump numbers, air control, coyote/buffer, and any variable jump: not found.
- Whether Hard Corps uses a somersault jump: not confirmed from an accessible source in this pass.

## 3. Shooting: directions, selection, per-state availability, aim lock, fire rates

### Takeaway
All three games are 8-way shooters steered with the d-pad. In Contra NES, diagonals are only reachable while moving or airborne because pressing a diagonal also walks. Standing allows only forward, straight up, and prone-forward. In the air all 8 directions work, including straight down. Contra NES has no lock.

Hard Corps adds a toggle between Type I (move while firing) and Type II (cannot move while firing, aim 8-way). It is toggled by holding B (fire) and pressing A, the weapon-switch button.

Blazing Chrome adds a held, remappable lock button: hold it to stand still and aim in 8 directions. It locks position, not direction.

Contra NES fire: the default gun fires 1 shot per new press, max 4 on screen, at 3 px/f. M fires every 8 frames while held, 7.5 shots/s peak and ≈6.7/s sustained, max 6 on screen, at 3 px/f.

### Cited Findings
**Contra NES: direction set and selection**
- `PLAYER_AIM_DIR` values, which also encode facing ([ram.asm L840](https://github.com/vermiceli/nes-contra-us/blob/main/src/ram.asm#L840)):
  - #$00 up (facing right) and #$09 up (facing left)
  - #$01 up-right, #$02 right, #$03 down-right
  - #$04 prone facing right, #$05 prone facing left
  - #$06 down-left, #$07 left, #$08 up-left
- `set_player_aim_for_input` runs every frame. It picks row 0 (facing right) or row 1 (facing left) from the previous frame's aim, then indexes `d_pad_player_aim_tbl` with the raw 4-bit d-pad ([L4982–5036](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4982)). Rows 2–3 apply only to indoor boss screens. Facing-right mapping:

  | Input | Aim |
  |---|---|
  | none | forward |
  | Right | forward |
  | Left | turn left |
  | Down | prone |
  | Down+Right | down-right |
  | Down+Left | down-left |
  | Up | up |
  | Up+Right | up-right |
  | Up+Left | up-left |

- Any input containing Left or Right also sets X velocity ±1 px/f in the same frame ([`handle_d_pad` L4560](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4560)). **Availability by state (verified, own reading):**
  - **Standing still:** forward, straight up (`sprite_16`), prone-forward (`sprite_17`). **No standing diagonals** (pressing one walks) and no straight-down.
  - **Running:** forward, diagonal-up, diagonal-down. **No straight up while running** (Up+Right resolves to up-right).
  - **Airborne (jump):** the same table applies. The fire routine then converts aim #$04/#$05 (Down) into straight down, using velocity index #$0b = (0, +3) ([bank6 `@run_create_bullet_routine` L347–380](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank6.asm#L347)). Result: **all 8 directions**, with up/down available in both facings.
  - **Falling off a ledge:** `PLAYER_JUMP_STATUS` = 0 there, so Down fires horizontally at prone height rather than straight down **(own reading)**.
  - **In water:** no down-right, prone or down-left shots ([bank6 `check_player_fire` L290–300](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank6.asm#L290)).
- **No aim lock or strafe button exists.** B fires and A jumps; nothing else is read for aiming **(own reading)**.

**Contra NES: fire rate, capacity and bullet speed**
- **Default gun:** a bullet is created only on a new B press (`CONTROLLER_STATE_DIFF`), so it is semi-automatic ([bank6 L290–335](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank6.asm#L290)).
  - Max **4 bullets on screen** (`create_bullet_max_04`, [L598](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank6.asm#L598)).
  - Speed is 3 px/f along axes and 2.12/2.12 diagonally (normalized to 0.707), from `bullet_velocity_normal` ([L897](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank6.asm#L897)). With Rapid (R) it is 4 px/f, from `bullet_velocity_rapid` ([L922](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank6.asm#L922)).
  - 3 px/f = 180 px/s = 5.3 H/s; 4 px/f = 240 px/s = 7.1 H/s **(own calculation)**.
  - The practical rate is capped by press speed plus the 4-bullet limit. Example **(own calculation**, assuming bullets despawn at the screen edge): firing right from mid-screen, a bullet needs ≈43 frames to cross 128 px, which gives ≤4 shots per ~43 frames ≈ 5.6 shots/s.
- **M (machine gun):** fires while B is *held* ([`gen_m_bullet_if_delay_met` L439](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank6.asm#L439)). The counter's low nibble must reach 8 between bullets, and the high nibble counts bullets. At #$60, the delay becomes a 15-frame wait before the counter resets ([ram.asm L755](https://github.com/vermiceli/nes-contra-us/blob/main/src/ram.asm#L755)).
  - A frame-exact simulation **(own calculation)** gives shots every **8 frames** (7.5 shots/s). The first burst is 6 shots; after that each burst is 7 shots followed by a **15-frame pause**, averaging **≈6.7 shots/s**.
  - Max **6 M bullets on screen** (`create_bullet_max_a_p2_0a` with a=#$05).
  - M uses the same velocity table as the default gun (3 px/f, or 4 with R) ([L897–945](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank6.asm#L897)). The disassembly's Enemy Glossary describes M bullets as faster than the default weapon's ([Enemy Glossary](https://github.com/vermiceli/nes-contra-us/blob/main/docs/Enemy%20Glossary.md)). **Conflict:** the code shows no speed difference. M differs in auto-fire, capacity, and a higher weapon-strength code (#$02 vs #$00, [bank7 `weapon_strength` L4111](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4111)).
- **Other weapons:**
  - S: 5 bullets per shot, max 10 on screen ([bank6 L495–520](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank6.asm#L495)).
  - F: max 4 on screen, 1.5 px/f (2 px/f with R).
  - L: 4-segment beam.
- **Recoil feedback:** every bullet sets `PLAYER_RECOIL_TIMER` = 15 frames ([bank6 `create_enemy_bullet` L622–626](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank6.asm#L622); decremented in [bank7 L4091](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4091)). Its sprite effects are covered in §4.

**Contra: Hard Corps** (official US manual p.10–11, [PDF](https://manuals.sega.com/genesismini/pdf/CONTRA_HARD_CORPS.pdf))
- **Buttons:** the d-pad controls both movement and weapon aim; B shoots; A selects a weapon; C jumps.
- **Shot types:** holding B and pressing A toggles between them. Type I lets the player move while firing; Type II stops the player from moving while firing. The HUD shows the current type (`SHOT·I` in the screenshot) **(own observation**, [Wikipedia screenshot](https://en.wikipedia.org/wiki/File:Contra_Hard_Corps_(gameplay).png)).
- **Type II aims 8-way.** Wikipedia, citing manual p.10, describes the stationary mode as holding the character still while aiming in one of eight directions ([Wikipedia](https://en.wikipedia.org/wiki/Contra:_Hard_Corps)).
- **Movement is only locked while firing.** In Type II the character can still move when not shooting, and pressing the toggle again returns to move-and-shoot ([Gaming Past Time review](https://gamingpastime.com/contra-hard-corps-review/)). The same review warns that A both switches weapons and toggles the lock, so stray presses are risky.
- **Six-button pad: conflict.** The US manual notes that X, Y and Z have no function. Sega Retro (search excerpt) and a ROM-hack readme ([readme, via search excerpt](https://otakon273.duckdns.org/Consoles/RomHacking.net/rhdn_20240801/hacks/genesis/patches/4665readme.txt)) say X/Y/Z toggle the mode. This may be a regional difference (Japanese release) and is **unresolved**.
- **Straight down on the ground** (Sega Retro, search excerpt only): in Type II, Down then B fires straight down, while B then Down fires lying prone. In Type I the character cannot fire straight down and Down+B always gives the prone shot.
- **Hanging from walls or ceilings:** the character can shoot but cannot move while firing, except with Fang's Power Punch and Psychic Blaster (manual p.11).
- **Weapons:** everyone has a machine gun plus up to four character-specific weapons A–D, and bombs (manual pp.13–17). Fang's D weapon takes 90 frames to charge ([TASVideos 6177S](https://tasvideos.org/6177S)).
- **Fire rates and bullets on screen: not found.**

**Blazing Chrome**
- A dedicated lock-aim button, R1 on PS4 per image filename, combined with fire locks movement so the player can aim in any of the 8 directions without moving ([PlayStation Country review](https://playstationcountry.com/blazing-chrome-ps4-review)).
- While moving the player can aim in only a few directions; standing still with the lock raises that to eight specific directions ([Worthplaying review](https://worthplaying.com/article/2019/10/30/reviews/116742-pc-review-blazing-chrome/)).
- Holding a shoulder button lets the player fire without moving ([Wccftech review](https://wccftech.com/review/blazing-chrome-a-hard-corps-afternoon/amp/), paraphrase).
- **Fire input:** tap to shoot, hold for auto-fire ([PlayStation Country](https://playstationcountry.com/blazing-chrome-ps4-review)). Tapping fire near an enemy produces a melee strike ([HG101](https://www.hardcoregaming101.net/blazing-chrome/); [Wccftech](https://wccftech.com/review/blazing-chrome-a-hard-corps-afternoon/amp/)).
- Weapons are cycled with the triggers or shoulder buttons ([PlayStation Country](https://playstationcountry.com/blazing-chrome-ps4-review), [Wccftech](https://wccftech.com/review/blazing-chrome-a-hard-corps-afternoon/amp/)).
- Diagonal-down aim while running exists ([Steam thread](https://steamcommunity.com/app/609110/discussions/0/1643168364650459700), search excerpt).
- **Standing diagonal aim.** A screenshot shows Doyle standing still aiming diagonally up-left next to Mavra aiming straight up. That standing diagonal is presumably the lock mode, since running diagonals come with movement **(own observation**, Steam `ss_431521…`).
- Rolling was impossible while holding Aim before a patch (developer IURI, [Steam thread](https://steamcommunity.com/app/609110/discussions/0/1643168364650459700)).
- **Fire rates, bullets on screen, and whether straight-down firing exists on the ground or in the air: not found.**

### Inferences
- **Contra NES** reaches 8 directions with zero extra buttons by tying diagonals to movement. The cost is that the player cannot hold position while shooting diagonally. That is exactly what Hard Corps' Type II (1994) and Blazing Chrome's held lock (2019) fix.
- **Blazing Chrome's** held button is more discoverable than Hard Corps' modal toggle. Hard Corps' toggle shares the weapon-switch button and is criticized for accidental activation.
- **Direction is never locked in either game; only position is.** Neither offers a "strafe" mode that keeps the aim angle while moving. That is a separate design option the comando team could consider.

### Gaps
- Hard Corps:
  - Whether Type I allows standing diagonals.
  - Which directions are available in the air (straight down?) and while running.
  - Fire rates.
- Blazing Chrome:
  - The exact aim set while moving (only a few directions per the review).
  - Whether straight down exists.
  - Fire rate, bullet capacity and bullet speed.
- None of these were found.

## 4. Sprite construction and frame counts (incl. Hard Corps roster)

### Takeaway
Contra NES uses a **split torso/legs construction at the metasprite-data level**. Each player sprite code is an upper-body tile group, unique per aim pose, plus a pointer to one of **three shared leg groups**. All run variants step through the same 6-step index, so aim changes and firing swap only the torso while keeping the leg phase. In total there are ≈7 torso drawings, 3 leg drawings, 1 prone, and 2 somersault drawings (rotated by flips).

Run steps last 8 frames (7.5 fps; 48-frame cycle). Somersault steps last 5 frames (12 fps; 20-frame spin). Idle, stand-aim-up and prone are single frames.

For Hard Corps and Blazing Chrome, construction and frame counts could not be sourced: sprite-rip sites were bot-blocked. Blazing Chrome screenshots show full-body upright poses for each aim state, including airborne ones.

### Cited Findings
**Contra NES: data format**
- Sprites are 8×16 hardware objects ([Graphics Documentation](https://github.com/vermiceli/nes-contra-us/blob/main/docs/Graphics%20Documentation.md)). Each metasprite entry gives Y offset, tile, attributes and X offset. An entry whose first byte is #$80 is a pointer that continues reading at another address, so sprites can share tile groups ([bank1 header comments before `sprite_01`](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank1.asm)).
- **Shared leg groups** in bank1:
  - `player_walking_1_bottom` ([L4559](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank1.asm#L4559)): 3 entries.
  - `player_walking_2_bottom`: 3 entries.
  - `player_bottom` ([L4607](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank1.asm#L4607)): 3 entries.
- **Upper-body groups:**
  - Run with gun lowered: tiles 28/2a, 2c/2e, 30/32.
  - Gun level/forward: 94/96/98, 3 columns wide.
  - Diagonal up: 8c/8e.
  - Diagonal down: 86/88/8a.
  - Straight up: 80/82/84, with the gun tile 34 px above the anchor.
  - The aim sprites jump to a leg group via #$80 ([bank1 L4729–4905](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank1.asm#L4729)).
- **Gameplay sprite codes, outdoor** ([bank2 `set_player_sprite` L864–1100](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank2.asm#L864)):

  | State | Sprite codes | Frames (own count) | Timing |
  |---|---|---|---|
  | Idle / stand (no input) | `sprite_0f` (gun-level torso + `player_bottom`) | 1, no idle animation (sequence #$00 = standing, no animation, [ram.asm L821](https://github.com/vermiceli/nes-contra-us/blob/main/src/ram.asm#L821)) | static |
  | Stand aim up | `sprite_16` | 1 | static |
  | Prone | `sprite_17` (4 tiles wide, no leg pointer) | 1 | static |
  | Run, gun lowered | 02,03,04,05,03,06 (`player_frame_sprite_tbl_00`) | 6 steps / 5 unique; torsos A,B,C,C,B,A over legs 1,2,3,1,2,3 | 8 frames/step |
  | Run, gun level (15 f after any shot) | 0d,0e,0f ×2 (`_tbl_01`) | 3 unique | 8 frames/step |
  | Run, aim diag-up | 10,11,12 ×2 (`_tbl_02`) | 3 unique | 8 frames/step |
  | Run, aim diag-down | 13,14,15 ×2 (`_tbl_03`) | 3 unique | 8 frames/step |
  | Jump (somersault) | 08,09,08,09; steps 3–4 flipped H+V | 2 drawings → 4 orientations | 5 frames/step |
  | Walk off ledge / drop-through | `sprite_05` | 1 | static |
  | Death | 0a,0b, then flipped 0a,0b, then 0c lying | 3 drawings | 8 frames/step |

  Sources: tables at [bank2 L945–975](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank2.asm#L945) and [L1039–1082](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank2.asm#L1039).
- **Timing:** `PLAYER_ANIMATION_FRAME_INDEX` advances when `PLAYER_ANIM_FRAME_TIMER & 7 == 0`, i.e. every 8 frames, wrapping at 6 ([bank2 L916–940](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank2.asm#L916)). That gives **7.5 animation fps, a 48-frame (0.80 s) torso cycle and a 24-frame leg cycle** **(own calculation)**. The somersault index advances every 5 frames, wraps at 4, and alternates two drawings, with H+V flip on steps 2–3 ([L1039–1082](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank2.asm#L1039)). That gives **12 fps and 20 frames per full revolution, ≈3 revolutions per 59-frame jump** **(own calculation)**.
- **Aim switching keeps leg phase.** `set_player_frame_sprite` picks the table from `PLAYER_AIM_DIR` via `player_frame_sprite_type_tbl` but indexes it with the same running `PLAYER_ANIMATION_FRAME_INDEX` ([L905–950](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank2.asm#L905)). Every run table uses legs 1,2,3,1,2,3 in the same order, so changing aim or firing swaps only the torso tiles and leaves the leg pose untouched **(own reading** of the tables in bank2 and bank1).
- **Recoil:** while `PLAYER_RECOIL_TIMER` ≥ #$0c (the first 4 of 15 frames), sprite attribute bit 3 draws the sprite 1 px lower ([bank2 `@check_sprite_recoil` L831](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank2.asm#L831)). The draw routine clears that bit when it hits the #$80 shared-legs pointer, so **only the torso drops 1 px; the legs stay put** ([bank1 L4110–4134](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank1.asm#L4110); [ram.asm SPRITE_ATTR docs](https://github.com/vermiceli/nes-contra-us/blob/main/src/ram.asm)). While the recoil timer is non-zero, running forward also switches from the gun-lowered torso set to the gun-level set.
- **Asset totals, outdoor, one character** **(own count)**:
  - 16 ground composite codes (02–06, 0d–0f, 10–15, 16, 17), 2 somersault drawings, 3 death drawings.
  - Built from ≈7 upper-body drawings (3 lowered-gun run, 1 level, 1 diag-up, 1 diag-down, 1 up), 3 leg drawings, 1 prone and 2 curl. Water and indoor states use separate sets.
- Player 2 (Lance) shares the same sprite codes with a palette swap (`sprite_xx_p2` renders in the [sprite library](https://github.com/vermiceli/nes-contra-us/tree/main/docs/sprite_library)).

**Contra: Hard Corps: roster (manual pp.14–17, [PDF](https://manuals.sega.com/genesismini/pdf/CONTRA_HARD_CORPS.pdf))**
- Ray Poward: Vulcan Laser, Crash, Spread, Homing.
- Sheena Etranzi: Genocide Vulcan, Shower Crash, Break Laser, Ax Laser.
- Brad Fang: Beast Shooter, Power Punch, Flame Thrower, charged Psychic Blaster. He is described as best at close range.
- Browny (combat robot CX-1-DA300): Victory Laser, Gemini Scatter, Electromagnetic Yo-Yo, Shield Chaser. He hovers with C during a jump.
- Two players cannot pick the same character (manual p.6).
- Size and movement differences: Browny is smallest with the longest slide (Sega Retro excerpt). Fang is larger, an easier target, with a weaker slide (Giant Bomb excerpt). Ray ≈40 px tall **(own measurement**, §1).
- The European Probotector release replaced all four with robots (search excerpt from [Giant Bomb/Wikipedia listing](https://en.wikipedia.org/wiki/Contra:_Hard_Corps)).
- **Hard Corps frame counts and torso/leg construction: not found.** [The Spriters Resource](https://www.spriters-resource.com/) returned a Cloudflare bot challenge, which was not bypassed.

**Blazing Chrome** (own observation of official Steam screenshots, [store](https://store.steampowered.com/app/609110/Blazing_Chrome/))
- Distinct full-body poses are visible for:
  - standing aim straight up (Mavra);
  - standing aim diagonal up (Doyle);
  - running/striding aim diagonal up (Mavra);
  - wide-stance forward fire (Doyle);
  - airborne forward fire (Doyle, legs tucked, upright torso);
  - a melee slash with a large green arc effect (Mavra).
- Characters cast an elliptical ground shadow, including while airborne. Sprites are ≈41–46 px tall at ≈427×240.
- **Frame counts, animation rates, and whether torso and legs are split: not found.** No JoyMasher statement on animation was found.

### Inferences
**Contra pattern for the comando.** The cheapest proven way to support 5 ground aim states while running is Contra's: a torso layer per aim angle over a shared, phase-locked leg cycle. With a heavy two-handed machine gun this maps naturally to separate upper-body animation over a common leg run cycle. It needs torso frames drawn per aim angle × run-cycle bob, with legs shared.

**Somersault vs. upright jump.** Contra's ball avoids drawing any air-aim poses: shots come from a ring of offsets around the ball (§6). Blazing Chrome's upright jump needs dedicated air poses per aim angle. At 128 px HD and 12 fps that means:
- **Contra-style:** ≈7 torso variants + 3–6 leg frames + prone + idle + a 4–8 frame spin.
- **Blazing-Chrome-style:** additionally ≈5 air aim poses (mirrored for left) plus standing diagonal poses for the lock (aim up-diag and down-diag while planted).

**Animation rate.** Contra's 8-frame run step is 7.5 fps, slower than the comando's 12 fps (5 logic frames per drawing at 60 Hz). Its 5-frame spin step matches 12 fps exactly.

### Gaps
- Hard Corps and Blazing Chrome per-state frame counts, animation rates, and sprite construction method (split vs full-body): not found. Sprite rips would be needed; The Spriters Resource blocked access.
- Hard Corps per-character size differences in pixels: not found beyond qualitative "smallest/largest" claims.

## 5. Hitbox vs sprite, and edge behavior

### Takeaway
Contra NES hurt regions are much narrower than the visible sprite. Against a regular enemy bullet the region is 10 px wide × 31 px tall standing (sprite 23×34), 12×12 jumping (ball 16×20), and 24×4 prone, a thin band near the floor (sprite 32×16).

Floor support is a single point probe at the sprite anchor 16 px down, on a 16×16 px collision grid. The player falls the instant the anchor leaves the floor cell, so roughly half the leg span can overhang the edge. There is no teeter animation. Hard Corps and Blazing Chrome numbers were not found.

### Cited Findings
**Contra NES: how the hit test works**
- Player/enemy collision tests the player's anchor point against the enemy box offset by a per-player-state table. The tables are: water (00), jumping (01), crouching/prone (02, when the sprite is `sprite_17`), standing (03) ([`check_players_collision` L6695–6790](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L6695); [`collision_box_codes_tbl` L7241–7330](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L7241)).
- A regular enemy bullet uses collision code #$01 ([Enemy Glossary, Bullet](https://github.com/vermiceli/nes-contra-us/blob/main/docs/Enemy%20Glossary.md)).
- Entry #$01 in each table (Y offset, X offset, height, width) gives the effective hit regions around the player anchor (X, Y) below **(own calculation)**. Each region is the Minkowski sum of player and bullet, so it slightly overstates the body.

  | State | Table entry | Hit if bullet is in | Region (w × h) | Visible sprite |
  |---|---|---|---|---|
  | Standing / running | #$f0,#$fb,#$1f,#$0a ([L7308](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L7308)) | Y−15…Y+16, X−5…X+5 | **10 × 31 px** (0.29 × 0.91 H) | 23 × 34; about 0.43 of its width |
  | Jumping | #$f6,#$fa,#$0c,#$0c ([L7270](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L7270)) | — | **12 × 12 px** | ball 16 × 20 |
  | Prone | #$f3,#$f4,#$04,#$18 ([L7289](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L7289)) | Y+9…Y+13 | **24 × 4 px**, a band just above the floor (floor at Y+16) | 32 × 16 |

- The variable-size hazard table `collision_code_f_base_tbl` annotates the player's own base box per state ([L7220](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L7220)): water 10×10, jumping 8×16, crouching 22×4, normal 8×29 (w×h). This is the closest thing to the "intrinsic" hurtbox **(own interpretation)**.
- Special cases:
  - Ducking in water makes the player untouchable ([L6752–6760](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L6752)).
  - Indoors, crouching avoids bullets entirely ([L6705–6715](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L6705)).
  - While ascending in a jump, contact with "landable" enemy types is ignored ([L6741–6750](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L6741)).
- Respawn invincibility is 128 frames, about 2 s, during which the sprite flickers on alternate frames ([bank7 L4199](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4199); [bank2 L775–790](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank2.asm#L775)).

**Contra NES: floor probe and edges**
- The floor test is one point: `get_player_bg_collision_code` reads background collision at (X, Y+16) ([L5077–5105](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L5077)).
- Background collision is stored per quarter of a 32×32 super-tile, i.e. on 16×16 px cells ([ram.asm `BG_COLLISION_DATA` L1652–1656](https://github.com/vermiceli/nes-contra-us/blob/main/src/ram.asm#L1652); rows advance 4 bytes per 16 px row in [`check_collision_below` L5296](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L5296)).
- **Edge overhang** **(own calculation** from `sprite_0f`/`player_bottom` offsets, [bank1 L4607, L4765](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank1.asm#L4765)): the legs span X−9…X+6 and the gun reaches X+16. When the anchor crosses the cell edge, the front 6 px of legs plus the gun already hang over, while the rear ≈9 px are still above the floor. About half the leg span (and ~70% of the visible width, gun included) can project past the edge before the fall triggers.
- **No teeter animation:** no balance sprite exists among the player codes 02–17. Walking off immediately switches to `sprite_05` and the edge fall starts the same frame **(own reading)**.
- Landing snaps Y to the 16-px grid + 4 ([`set_player_landing_y_offset` L4956](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank7.asm#L4956)).

**Contra: Hard Corps**
- Qualitative only: Browny's small body makes him harder to hit and Fang's large body makes him easier to hit (Giant Bomb, search excerpt). This suggests hurtboxes scale with sprite size.
- **Hitbox and edge numbers: not found.** No Hard Corps hitbox Lua script was found; TASVideos hosts one for Contra III only ([user file](https://tasvideos.org/UserFiles/Info/49605850624573728)).

**Blazing Chrome**
- **Not found.**

### Inferences
- **Contra hitboxes are about one third of sprite width, roughly the torso core.** The prone band is placed so that standard-height bullets pass over it. That is the mechanical reason prone exists as a "pose," not a movement mode.
- For a 128 px comando, a Contra-like ratio would be a ~38 px wide × ~117 px tall standing hurtbox (×128/34) **(own calculation)**.

### Gaps
- Hard Corps and Blazing Chrome hurtbox sizes, edge tolerance, and teeter animations: not found.

## 6. Bullet origin per aim pose

### Takeaway
Contra NES spawns bullets at **per-pose muzzle offsets** from a 10-entry table for grounded poses (e.g. +16,−5 forward; +5,−27 up; +16,+9 prone). In the air it uses a separate table: a ~16 px ring around the ball center. Blazing Chrome screenshots show muzzle flashes at each pose's gun tip, consistent with per-pose origins (own observation). Hard Corps: not found.

### Cited Findings
**Contra NES**
- `init_bullet_sprite_pos` adds an (X, Y) offset chosen by `PLAYER_AIM_DIR` to the player anchor ([bank6 L673–705](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank6.asm#L673)). It uses ground or air tables, with separate indoor variants.
- **Outdoor ground offsets**, `bullet_initial_pos_00` ([L714](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank6.asm#L714)), X right-positive and Y down-positive:

  | Aim | Offset (X, Y) | Note |
  |---|---|---|
  | Up | +5, −27 | gun above head |
  | Up-right | +13, −16 | |
  | Right | +16, −5 | chest height |
  | Down-right | +13, +6 | |
  | Prone right | +16, +9 | 7 px above floor |
  | Left-facing poses | mirrored | |

  These are true per-pose muzzle positions. The "up" and "prone" muzzles are 36 px ≈ 1.06 H apart vertically **(own calculation**: 27 + 9 = 36; 36/34).
- **Outdoor jumping offsets**, `bullet_initial_pos_01` ([L742](https://github.com/vermiceli/nes-contra-us/blob/main/src/bank6.asm#L742)): (0,−16) up, (+15,−15) up-right, (+16,0) right, (+15,+15) down-right, (0,+16) down. These form a ring of radius ≈16 px around the somersault center. That works because the ball has no visible gun.
- **Bullet direction comes only from the aim code** via fixed velocity tables (§3). There is no angle interpolation or spread for the default gun and M.

**Contra: Hard Corps**
- **Not found.**

**Blazing Chrome**
- Muzzle flashes appear at the gun tip for:
  - forward fire (Doyle, at about chest height);
  - diagonal-up fire (Mavra and Doyle);
  - straight-up fire (Mavra).

  This fits per-pose muzzle origins **(own observation**, Steam screenshots). Exact offsets: **not found**.

### Inferences
- **Contra's 10-entry offset table is the minimum data** a muzzle-origin system needs. For an HD comando with a long two-handed gun, per-pose (and ideally per-run-frame) muzzle anchors matter more, because the barrel tip moves with the torso bob and recoil.
- **A Contra-style ring for the air** is only acceptable if the air pose hides the gun.

### Gaps
- Hard Corps and Blazing Chrome muzzle-offset data: not found.

## 7. Developer statements (JoyMasher, Konami)

### Takeaway
No developer statements were found explaining the aim systems' design rationale or giving frame counts or resolutions. What exists:
- **JoyMasher's IURI**, on Steam, explains control restrictions as anti-accident measures and confirms there is no drop-through.
- **Danilo Dias** cites Contra's speed and Metal Slug's melee, bosses and vehicles as inspirations.
- **Konami:** a 1994 Hard Corps commentary covers tone and presentation only.

### Cited Findings
**JoyMasher**
- IURI (tagged [developer]) on Steam, July 2019 ([thread](https://steamcommunity.com/app/609110/discussions/0/1643168364650459700)):
  - Jump is blocked during certain roll situations because playtesters jumped accidentally; this was the team's chosen trade-off.
  - Leaving the mech requires being on the ground and not shooting, to prevent accidental exits.
  - The aim-hold roll restriction was being fixed.
  - A Type B scheme (Down+Jump = drop through platforms, roll on its own button) would be discussed with Danilo. Players in 2022 report the option exists but is greyed out.
- Danilo Dias (Siliconera interview, [article](https://www.siliconera.com/blazing-chrome-developer-talks-contra-hard-corps-metal-slug-inspirations/)) cites Contra's speed and frantic style plus Metal Slug's big mechanical bosses, melee mechanics and vehicles as the core mix. He says Hard Corps showed that each weapon could be good at something. No control or animation specifics are given.
- In a later interview (via [CB Insights summary](https://www.cbinsights.com/company/joymasher), search excerpt), Dias describes self-imposed colour and resolution limits while moving to more detailed art for Blazing Chrome.

**Konami**
- *Contra: Hard Corps* commentary from BEEP! Mega Drive, Oct 1994 ([Shmuplations translation](https://shmuplations.com/contrahc/)). Shmuplations credits it to development leader "Oh!Aji", while [Wikipedia](https://en.wikipedia.org/wiki/Contra:_Hard_Corps) attributes the same remarks to director Nobuya Nakazato (attribution discrepancy noted, not resolved). It says:
  - Choosing Browny turns the tone comedic while Ray keeps it serious.
  - The team prioritized presentation and wrote custom code for multi-sprite enemies.
  - There is nothing on controls, shot modes or animation.
- Wikipedia's infobox credits Nakazato (director), Kenji Miyaoka (programmer), and Shinichiro Shimamura and Kazuya Suzuki (artists), without inline citations ([Wikipedia](https://en.wikipedia.org/wiki/Contra:_Hard_Corps)).

### Inferences
- The lack of a drop-through in Blazing Chrome is a deliberate input-collision trade-off: Down+Jump was spent on the roll. A design that wants both down-shooting and dodging needs a dedicated dodge button, as IURI's proposed Type B shows.

### Gaps
- No JoyMasher statement on frame counts, animation rate, resolution, or why the lock is a hold button.
- No Konami staff interview on Contra (NES) player controls was searched in depth this pass; Shmuplations has no Contra NES controls interview in the results seen.
- Hardcore Gaming 101's Hard Corps article URL returned 404.

## 8. Compact comparison (all three games)

### Takeaway
Contra NES has the most fully documented system: 1 px/f instant run, a fixed 1.7 H somersault, sticky air drift, and 8-way aim derived from movement (no lock). It uses a torso-over-shared-legs sprite construction with phase-locked swaps. Hard Corps keeps d-pad 8-way aiming and adds a modal Type II stand-and-aim mode and a slide (its sprite construction and physics are undocumented). Blazing Chrome adds a held lock button and a roll, and uses upright, full-body air poses.

### Cited Findings
Every cell restates a value sourced in §1–§6. "nf" = not found. H = standing sprite height.

| | Contra (NES 1988) | Contra: Hard Corps (Genesis 1994) | Blazing Chrome (2019) |
|---|---|---|---|
| Native res / logic rate / H | 256×240 / 60.0988 Hz / H = 34 px (own meas.) | 320×224 / 59.923 Hz / Ray ≈ 40 px (own meas., ±3) | ≈427×240 (own meas.) / nf / Mavra ≈ 41 px (own meas.) |
| Run speed | 1 px/f = 60.1 px/s = 1.77 H/s | nf (slide faster than walk) | nf |
| Acceleration | Instant start and stop (velocity reset every frame) | nf | nf |
| Prone / crouch move | Prone is stationary; Down+L/R = run aiming diag-down; no crawl | Prone fire with Down+B; slide = diag-down + C, invulnerable, damages; Browny longest slide, Fang weaker | Crouch/prone exists; roll = Down+Jump (invuln. disputed); roll-cancel with opposite direction |
| Jump height / airtime | 58–59 px = 1.71–1.74 H; 59 f = 0.98 s; apex at f 26–29; indoors 41–42 px / 49–50 f | nf; Browny hover/double jump (C in air) | nf; double jump only with Speed drone/boots |
| Gravity | 0.1367 px/f² both ways (494 px/s², 14.5 H/s²); v0 −4.06 px/f | nf | nf |
| Air control | Yes, 1 px/f; drift persists after release, instant reversal, no stop; sprite spin direction fixed, aim free | nf | nf (upright air poses observed) |
| Variable jump / coyote / buffer | None / 0 frames / none (A must be a new press on a grounded frame) | nf | nf |
| Drop-through | Down+A if floor exists below; no X drift for first 20 px | Down+C only from moving objects or wall/ceiling hang (manual) | None (dev-confirmed design) |
| Shoot directions and selection | 8 via d-pad. Standing: fwd / up / prone. Running: fwd / diag-up / diag-down. Air: all 8 incl. straight down | 8 via d-pad; Type II on ground adds straight down (Sega Retro excerpt) | 8 via d-pad; only a few while moving, 8 while locked |
| Shoot while running / air | Yes / yes (8-way from the ball) | Type I yes / nf | Yes / yes (forward observed) |
| Aim lock | None | Modal toggle (hold B + press A). Type II = cannot move while firing, 8-way aim; position lock only while firing; direction free | Held (remappable) lock button: stand still, aim 8-way; position lock, direction free; no roll while held (pre-patch) |
| Fire rate / cap | Default: 1 shot per press, ≤4 on screen, 3 px/f (4 with R). M: hold, 1 per 8 f (7.5/s peak), 7-shot bursts + 15 f pause (≈6.7/s), ≤6 on screen | nf (machine gun default; Fang D charges 90 f) | nf (tap or hold auto-fire; tap near enemy = melee) |
| Sprite construction | Upper-body groups per aim + 3 shared leg groups via #$80 pointer; phase-locked torso swaps; somersault ball (2 drawings + flips) | nf | Full-body upright poses per aim state, incl. air (observed); split nf |
| Frames / timing | Idle 1 (static); run 6 steps (5 unique) at 8 f/step = 7.5 fps, 48 f cycle; aimed runs 3 unique ×2; jump 2 drawings → 4 steps at 5 f = 12 fps; prone 1; stand-up 1; recoil = torso −1 px for 4 f | nf | nf |
| Hitbox vs sprite | Standing 10×31 vs 23×34; jump 12×12 vs 16×20; prone 24×4 vs 32×16 (vs regular bullet) | nf (Browny smaller and harder to hit, Fang larger) | nf |
| Edge behavior | Single point probe (X, Y+16) on 16 px grid; ~half the leg span overhangs; no teeter; falls with 1 px/f momentum, X frozen 20 px | nf | nf |
| Bullet origin | Per-pose table (fwd +16,−5; up +5,−27; prone +16,+9 …); air ring r ≈ 16 px | nf | Gun-tip flashes per pose (observed), offsets nf |

### Inferences
These are for the comando: 128 px tall HD, 12 fps animation, heavy two-handed machine gun, currently forward-only with no lock.

- **Minimum viable aim set (Contra model):** 5 ground aims plus the air.
  - Ground: forward, up (standing), diag-up and diag-down (while running), prone-forward.
  - Air: if the jump is a somersault, all 8 come for free from a muzzle ring and need no extra art.
  - This needs no extra button. The cost is that there are no standing diagonals.
- **Modern standard (Hard Corps Type II / Blazing Chrome):** add a **held** lock button that plants the feet and opens all 8 directions on the ground. That adds standing diag-up and diag-down poses, plus straight down if wanted.
  - Prefer Blazing Chrome's hold over Hard Corps' toggle on the weapon button, which reviewers call error-prone.
  - Neither game locks the *direction* while moving. A direction-lock/strafe would be an addition beyond these references.
- **Sprite budget:**
  - Contra's split is the strongest precedent for a heavy-gun character: ≈5–7 torso-angle sets over one phase-locked leg cycle. Swapping torso mid-run never breaks the stride.
  - An upright air jump (Blazing Chrome) adds roughly one air pose per aim angle.
  - The 12 fps target matches Contra's spin (5 logic frames per drawing at 60 Hz) and is faster than Contra's 7.5 fps run.
- **Scaled Contra numbers for 128 px** **(own calculation)**:
  - run ≈ 226 px/s;
  - jump apex ≈ 221 px, airtime ≈ 1.0 s;
  - standing hurtbox ≈ 38×117 px;
  - muzzle forward at ≈ (+60, −19) px from the body anchor.

### Gaps
- All Hard Corps and Blazing Chrome numeric movement, jump, fire-rate, frame-count and hitbox data: not found in accessible sources.
  - Sprite-rip and wiki sites blocked automated access.
  - No RAM maps or disassemblies exist for these games as far as this search found.
- Closing these gaps would require frame-stepping footage or an emulator/RAM study (Hard Corps), or frame-capturing the PC version (Blazing Chrome).
