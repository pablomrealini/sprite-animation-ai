# Cuphead (Studio MDHR, 2017) and Broforce (Free Lives, 2015): player movement, jumping, shooting, aiming and sprite construction

Scope note for the report writer. Two kinds of "datamined" sources were used, and they differ in reliability:

- **Cuphead:** an unofficial, publicly published community decompilation on GitHub ([jmxamongusmodder/cuphead-decomp](https://github.com/jmxamongusmodder/cuphead-decomp)). It includes the DLC (Ms. Chalice), so it reflects the 2022+ build (v1.3.x), not necessarily the 2017 launch build. I did not decompile anything; I only read published files. The values quoted are code defaults in `LevelPlayerMotor.Properties`, `WeaponProperties`, the collider manager and the camera. The repo's `Player.prefab` serializes no motor properties (own check: no `moveSpeed`, `jumpPower` or `dashSpeed` keys in [Player.prefab](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/PrefabInstance/Player.prefab)), which suggests the code defaults are the live values. The 50x105 collider *is* serialized there and matches the code.
- **Broforce:** community modding documentation. [alexneargarder/Broforce-Docs](https://github.com/alexneargarder/Broforce-Docs) says in its README that "the vast majority of the documentation was generated automatically by having an AI analyze the game's code", and it warns there may be mistakes. The [BroMaker wiki](https://github.com/Gorzontrok/Bro-Maker/wiki) (Gorzontrok's custom-bro framework) is human-written and lists default variable values. All Broforce values are base-class defaults (`TestVanDammeAnim`). Per-bro prefab overrides, such as Rambro's actual fire rate, were not found.
- **Units:**
  - Cuphead: world units, with the camera `OrthographicSize` = 360, so the view is 720 units tall and 1280 wide ([CupheadLevelCamera.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/CupheadLevelCamera.cs), [AbstractCupheadCamera.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/AbstractCupheadCamera.cs)). At 1920x1080 that is **1.5 px per unit** at zoom 1 (own calculation: 1080/720). Some levels change the camera zoom.
  - Broforce: world units equal art pixels. Tiles are 16 units (`Map.HalfTileSize` = 8 in the [docs XML](https://github.com/alexneargarder/Broforce-Docs/blob/master/Assembly-CSharp.xml)), and bro frames are 32x32 px.
- **Physics rate:** Cuphead's fixed timestep is 1/60 s ([TimeManager.asset](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/ProjectSettings/TimeManager.asset): `Fixed Timestep: 0.01666667`).
- **Blocked source:** The Spriters Resource returned HTTP 403, so frame counts come from the published Unity animation clips (Cuphead) and from the community example sheets shipped with BroMaker (Broforce).

**Reference heights used for normalization (H):**

- **Cuphead:**
  - ≈ 153 units (≈ 230 px at 1080p) including the straw, or ≈ 123 units (≈ 185 px) from shoe sole to cup rim. These are own measurements on the 1920x1080 Steam screenshot [ss_6154…](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/268910/ss_615455299355eaf552c638c7ea5b24a8b46e02dd.1920x1080.jpg) (Beppi fight; Cuphead standing in the shooting pose). Straw top ≈ y 627, cup rim ≈ y 675, soles ≈ y 860, so ±10 px. Converted with 1.5 px/unit.
  - Scale cross-check: the finger tip sits ≈ 125 px ahead of the body centre, against the code's forward muzzle offset of 78 u × 1.5 = 117 px. That agrees, so the screenshot is roughly at zoom 1.
  - Collider height = 105 units.
- **Broforce:** Rambro's standing body is 19 px tall × 15 px wide inside a 32×32 cell (own measurement: opaque-pixel bounding box of cell (row 0, col 0) of [rambroAnim.png](https://github.com/Gorzontrok/Bro-Maker/tree/main/images/Example%20Spritesheets)). H = 19 units.

---

## Movement: run speed, acceleration, dash, wall climbing and ledges

### Takeaway
- **Cuphead:** runs at a constant 490 u/s with instant start and stop. That is ≈ 735 px/s at 1080p, or ≈ 3.2 H/s (≈ 4.0 body-heights/s). The dash covers ≈ 330 u (≈ 2.2 H) in 0.3 s, at fixed height with no gravity, and you can't shoot during it.
- **Broforce:** the base bro runs at 110 u/s, which is ≈ 5.8 H/s, so it is much "faster" relative to its tiny body. Acceleration is ramped but snappy. Wall climbing (knife stabs) and ceiling or zipline hanging are standard. Ledge grab is a per-bro flag (default false per BroMaker), and corner "chimney flips" carry you over overhangs.

### Cited Findings
**Cuphead**

- **Run speed:** `moveSpeed = 490` units/s. Horizontal velocity is set directly as `input axis (−1/0/1) × moveSpeed` every fixed step, with no acceleration or friction term, so start and stop are instant ([LevelPlayerMotor.cs, HandleWalking and Properties](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs)).
  - Conversion (own calculation): 490 × 1.5 = **735 px/s at 1080p**.
  - In heights: 490/153 = **3.20 H/s** (with straw), 490/123 = 3.98 body-H/s, 490/105 = 4.67 collider-H/s.
  - It takes 1280/490 = 2.61 s to cross a 1280-unit screen.
- **When you can't walk:** walking is suppressed when the lock button is held, or when down is held on the ground (that is duck instead) ([same file, HandleWalking: `LookDirection.y >= 0 || !Grounded) && !Locked`](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs)).
- **Dash:** `dashSpeed = 1100` u/s for `dashTime = 0.3` s ([LevelPlayerMotor.cs Properties](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs)).
  - Distance (own calculation): 1100 × 0.3 = **330 u ≈ 495 px at 1080p ≈ 2.16 H** (2.68 body-H). At the 60 Hz step that is 18–19 frames.
  - Direction: the dash goes in the facing direction (`TrueLookDirection.x`).
  - Velocity: walking velocity is zeroed at dash start, vertical velocity is zeroed every dash frame, and `HandleFalling` returns early while dashing. So the air dash is perfectly horizontal with no gravity (same file).
  - Ground dash: there is a 0.1 s cooldown after a ground dash (`DASH_COOLDOWN_DURATION = 0.1`).
  - Air dash: the dash state only returns to Ready when grounded, so **one air dash per airtime** (own reading of HandleDash, same file).
  - Jump hold: dashing cancels the variable-jump hold.
- **Other dash constants:** `dashEndTime = 0.21` (exact use not traced) and `verticalDashSpeed = 935` (used by the DLC directional-dash charm, `WeaponProperties.CharmDirectionalDash`) ([LevelPlayerMotor.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs); [WeaponProperties.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/WeaponProperties.cs)).
- **Wiki on the dash:** a short ground and air dash, with no invulnerability unless the Smoke Bomb charm is equipped ([Cuphead Wiki, Cuphead](https://cuphead.wiki.gg/wiki/Cuphead_(character)); invulnerability note via [Fandom article summary in search](https://www.fandom.com/articles/1547-beginner-tips-to-save-your-soul-in-cuphead), not opened).

**Broforce**

- **Run speed:** `speed` default **110 units/s** ([BroMaker wiki, Variables](https://github.com/Gorzontrok/Bro-Maker/wiki/Variables); [Broforce-Docs TestVanDammeAnim](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/TestVanDammeAnim-Documentation.xml): "Base horizontal movement speed in units per second (default 110)"). The community bro template also uses `"speed": 110` ([Bro Template.json](https://github.com/alexneargarder/Broforce-Templates/blob/master/Bro%20Template/Bro%20Template/_ModContent/Bro%20Template.json)).
  - In heights (own calculation): 110/19 = **5.8 H/s** = 6.9 tiles/s.
  - At 1080p: in one Steam screenshot ([ss_700c…](https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/274190/ss_700cda119dab1d0333b8d91771cf216ac7f8cafa.1920x1080.jpg)) a jumping bro measures ≈ 80 px tall, which is ≈ 4.2–4.5 screen px per art pixel. That gives ≈ 460–495 px/s for the run (own rough measurement; camera zoom varies).
- **Acceleration (AI-generated docs):** it is ramped. `AddSpeedLeft/Right` accelerate "with speed limits and multipliers... Base acceleration is 2x, dashing provides 4x... extra 2.6x boost when below maximum speed". `ClampSpeedPressingLeft/Right` force at least 10 u/s the moment a direction is pressed "to ensure responsive... movement initiation" ([Broforce-Docs TestVanDammeAnim](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/TestVanDammeAnim-Documentation.xml)). Time-to-max-speed is not given.
- **Sprint and dash (AI-generated docs):**
  - Triggers: a dash button, or a double-tap within `minDashTapTime` 0.33 s.
  - Multiplier: `dashSpeedM` defaults to 1.0. A "Sprinting on ground" animation exists ([Broforce-Docs](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/TestVanDammeAnim-Documentation.xml); [BroMaker Spritesheets](https://github.com/Gorzontrok/Bro-Maker/wiki/Spritesheets)). The sprint speed multiplier itself was not found.
  - Air dash for bros with `canAirdash` (e.g. Nebro, BroLee, Brocketeer): 2.3× speed horizontally, after a 0.15 s charge-up. `airdashMaxTime` is 0.5 s, ×0.8 for up and ×5 for the down slam. One dash per direction until landing.
- **Wall climbing (AI-generated docs):**
  - `canWallClimb` defaults to true. The climb is animated as alternating knife stabs, with `knifeClimbStabHeight` 18 units between stabs.
  - `maxWallClimbYI` = 100 u/s is the maximum upward speed when the climb starts.
  - `wallDragTime` 0.2 s gives a brief "stick" on contact, and wall drag clamps the slide speed (summary cites −40).
  - Wall jumps exist, with a 0.2 s timing gate (`lastJumpTime`) ([Broforce-Docs TestVanDammeAnim](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/TestVanDammeAnim-Documentation.xml); [Assembly-CSharp.xml](https://github.com/alexneargarder/Broforce-Docs/blob/master/Assembly-CSharp.xml)).
- **Ledges and ceilings:**
  - **Ledge grab:** BroMaker lists `"canLedgeGrapple": false` as the default ([BroMaker wiki, Variables](https://github.com/Gorzontrok/Bro-Maker/wiki/Variables)). The AI-generated docs say "Default true" ([Broforce-Docs](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/TestVanDammeAnim-Documentation.xml)), so **the sources conflict**.
  - **Chimney flip:** "The move where you go up and over a corner" (sheet slot 20) ([BroMaker Spritesheets](https://github.com/Gorzontrok/Bro-Maker/wiki/Spritesheets)). Players confirm: "Jumping at an overhang above you will cause your Bro to flip up over it" ([Steam tips thread](https://steamcommunity.com/app/274190/discussions/0/611701360820425405)).
  - **Ceiling hang and zipline:** ceiling hanging and ziplines exist (sheet slot 14), with `hangGraceTime` 0.3 s ([Broforce-Docs](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/TestVanDammeAnim-Documentation.xml); [BroMaker Spritesheets](https://github.com/Gorzontrok/Bro-Maker/wiki/Spritesheets)).

### Inferences
- Relative to body size, Broforce's base bro moves ≈ 1.8× faster than Cuphead (5.8 vs 3.2 H/s). In absolute screen terms they are comparable: ≈ 460–495 vs 735 px/s at 1080p, because the Broforce bro is only ≈ 80 px tall on screen against Cuphead's ≈ 230 px.
- Scaled to the team's comando (H = 128 px at 1x), own calculation:
  - Cuphead-feel run ≈ 3.2 × 128 ≈ **410 px/s**.
  - Broforce-feel run ≈ 5.8 × 128 ≈ **740 px/s**.
  - Cuphead-feel dash ≈ 2.2 × 128 ≈ 276 px in 0.3 s.
- Cuphead's no-shoot dash makes the dash a pure defensive commitment. A heavy-MG soldier could keep that rule, with no fire during the dash or roll.

### Gaps
- Cuphead: the purpose of `dashEndTime` = 0.21 was not traced.
- Broforce: the exact acceleration curve (time to 110 u/s), the sprint multiplier, Rambro's own prefab overrides (if any), and whether `canLedgeGrapple` is true for vanilla bros were all not found. The camera zoom in px per unit is not documented; my value comes from one screenshot.

---

## Jump: height, airtime, variable jump, air control, gravity, coyote time, buffering, parry, double jump

### Takeaway
- **Cuphead:**
  - The jump is "constant-velocity rise while held, then strong gravity". The upward velocity is held for up to 0.15–0.16 s.
  - **Full jump:** ≈ 265 u (≈ 397 px at 1080p ≈ 1.7 H) and ≈ 0.63 s airtime.
  - **Tap:** ≈ 115–134 u (0.75–0.87 H) and ≈ 0.40–0.43 s.
  - Air control is full and instant. Fall speed is capped at 1620 u/s.
  - Coyote time is 0.0834 s, and an input buffer of 0.134 s exists (mainly for inputs during a dash).
  - Pressing jump again in the air is the parry. It bounces ≈ 206 u on success, and there is no double jump (Ms. Chalice only).
- **Broforce:** the same structure: 260 u/s held for 0.123 s, gravity 1100 u/s², and a fall cap of 400 u/s. That gives ≈ 63 u (≈ 3.3 H, ≈ 3.9 tiles) and ≈ 0.70 s airtime for a full jump (own calculation). There is landing-jump buffering, and no default double jump.

### Cited Findings
**Cuphead (constants from [LevelPlayerMotor.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs))**

- **Constants:** `jumpPower = −0.755`, `jumpHoldMin = 0.01` s, `jumpHoldMax = 0.16` s, `maxSpeedY = 1620`, `timeToMaxY = 7.3`, with linear `yEase`.
- **Vertical velocity:** it is stored in a normalized value *y*, clamped to [−10, 1], and converted as `velocity = −1620 × y`. So the jump launch is 0.755 × 1620 = **1223 u/s** (≈ 1835 px/s). The fall is **capped at 1620 u/s** (≈ 2430 px/s) (VelocityManager.Total and the `y` clamp).
- **Gravity:** each fixed step adds `maxSpeedY/(timeToMaxY×60) × FixedDelta` to *y*. That is ≈ **5,992 u/s²** (≈ 8,990 px/s² at 1080p) (own calculation from HandleFalling). From rest, terminal velocity is reached after ≈ 0.27 s.
- **Variable jump:** while the button is held, the jump state stays at "Hold" and velocity is re-set to `jumpPower` every step. The hold ends when the button is released after at least `jumpHoldMin`, at `jumpHoldMax`, or on hitting a ceiling (HandleJumping).
  - Own discrete simulation at 60 Hz, using the code's update order (input, then gravity, then move):

    | Hold | Apex | Time to apex | Airtime |
    |---|---|---|---|
    | Full (button held) | **264.6 u = 397 px = 1.73 H** (2.15 body-H, 2.52 collider-H) | 0.333 s | **0.633 s** |
    | Minimum tap | 114.8–133.5 u = 172–200 px = **0.75–0.87 H** | — | 0.40–0.43 s |

  - Landing after a full jump is at the 1620 u/s cap.
  - Gravity is the same rising and falling. The asymmetry comes from the hold phase (a linear rise) and the fall cap. For a full jump the rise is ≈ 0.33 s and the fall ≈ 0.30 s.
- **Coyote time:** after leaving the ground, the Ready jump state expires once `timeInAir > 0.0834` s (FixedUpdate). The literal 0.0834 also appears as the constant `JUMP_BUFFER_TIME`. At 60 Hz this is **5 frames**.
- **Input buffer:** `INPUT_BUFFER_TIME = 0.134` s (≈ 8 frames) for Jump, Dash and Super. `BufferInputs()` is only called while input is disabled or **while dashing**, so this is a dash-cancel and lock-out buffer, not a general "pressed jump just before landing" buffer (HandleInput, BufferInputs).
- **Air control:** full and instant. `HandleWalking` applies `moveSpeed` in the air, and the "down blocks walking" rule only applies when grounded. The lock button only works when grounded (`HandleLocked` requires `Grounded`).
- **Parry:** pressing jump while airborne (jump state not Ready) triggers the parry. On a successful parry the velocity is set to `parryPower = −1`, i.e. **1620 u/s upward**. Own simulation: an extra apex of ≈ 206 u (≈ 308 px, ≈ 1.34 H), reached in 0.27 s (HandleParry, Properties).
  - The wiki adds that the parry targets pink objects and refills the super meter ([Cuphead Wiki, Parry Slap](https://cuphead.wiki.gg/wiki/Parry)).
- **Double jump:** none for Cuphead or Mugman. Only Ms. Chalice has `chaliceFirstJumpPower = −0.63` and `chaliceSecondJumpPower = −0.55` (Properties, ChaliceDoubleJump).

**Broforce (AI-generated docs plus BroMaker defaults)**

- **Constants:** `_jumpForce` default **260** u/s, `JUMP_TIME` **0.123** s ("Duration... that jump force is applied when the jump button is held... allows for variable jump heights"), and `GRAVITY` **1100** u/s². `maxFallSpeed` is **−400** u/s ([BroMaker wiki, Variables](https://github.com/Gorzontrok/Bro-Maker/wiki/Variables); [Broforce-Docs TestVanDammeAnim](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/TestVanDammeAnim-Documentation.xml)).
  - The docs also say `jumpTime` is "Set to 0.13 seconds at the start of a standard jump", which slightly conflicts with 0.123 ([Broforce-Docs](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/TestVanDammeAnim-Documentation.xml)).
- **Jump arc (own calculation):** this assumes 260 u/s is held for the full 0.123 s with no gravity during the hold, followed by ballistic flight. The exact integration order is not documented.

  | Hold | Apex | Time to apex | Airtime | Landing speed |
  |---|---|---|---|---|
  | Full | **≈ 62.7 u ≈ 3.3 H ≈ 3.9 tiles** | ≈ 0.36 s | **≈ 0.70 s** | ≈ 371 u/s |
  | Tap | ≈ 30.7 u ≈ 1.6 H | — | ≈ 0.47 s | — |

  - A full jump lands just under the 400 u/s cap. Terminal velocity is reached after 0.36 s and 72.7 u of fall.
- **Jump buffer:** `pressedJumpInAirSoJumpIfTouchGroundGrace`: "When jump is pressed in air... If player lands while timer is positive, automatic jump occurs". The duration was not given. `airDashJumpGrace` also exists ([Broforce-Docs](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/TestVanDammeAnim-Documentation.xml)).
- **Jump spacing:** 0.08 s minimum between jumps, 0.2 s for wall jumps, 0.3 s for ceiling-grab attempts (`lastJumpTime`) ([Assembly-CSharp.xml](https://github.com/alexneargarder/Broforce-Docs/blob/master/Assembly-CSharp.xml)).
- **Double jump:** none by default. `AirJump` is "Empty in base class". `doubleJumpsLeft` is reset to 0. `BroBase.AirJump` and `AirFlexJump` (fart or flex air jumps, 0.5–1.8× force) are perk-driven ([Assembly-CSharp.xml](https://github.com/alexneargarder/Broforce-Docs/blob/master/Assembly-CSharp.xml); [BroBase docs](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/BroBase-Documentation.xml)).

### Inferences
- Both games use the same "hold to sustain launch velocity for ~0.12–0.16 s" variable jump, with nearly the same full-jump airtime: ≈ 0.63 s (Cuphead) vs ≈ 0.70 s (Broforce). Broforce's jump is about twice as tall *relative to the body* (3.3 H vs 1.7 H) because its bros are tiny compared to the tile grid.
- For the comando at H = 128 px, own calculation:
  - Cuphead-like full jump ≈ 222 px with gravity ≈ 8,990 × (128/230) ≈ 5,000 px/s². Min hop ≈ 96–111 px.
  - Broforce-like jump ≈ 420 px.
- A heavy two-handed MG suggests the lower, Cuphead-like ratio (≈ 1.5–1.8 H) unless traversal over 3–4-tile walls matters.
- Cuphead's 5-frame coyote time and 8-frame dash buffer are good defaults to copy at 60 Hz.

### Gaps
- Broforce: the coyote-time value (the docs only mention "air jump grace periods" inside `CalculateMovement`) and the jump-buffer duration were not found.
- Broforce: whether gravity acts during the hold, and the air acceleration magnitude, were not found. The docs imply the same `AddSpeed` functions apply.
- Cuphead: no human-verified (speedrun or wiki) jump heights were found to cross-check the simulation.

---

## Shooting and aiming: directions, selection, lock button, run, duck and air, dash, fire rates

### Takeaway
- **Cuphead:** 8-direction aiming selected by the stick, with the reachable set depending on state:
  - **Standing, not locked:** forward, or straight up.
  - **Running:** forward, or diagonal-up in the run direction. Holding down on the ground ducks and stops movement.
  - **Ducking:** forward only, low.
  - **In the air:** all 8 directions with no aim pose.
  - **Lock (held, ground only):** zeroes walking and allows all 8 directions in place.
  - **Dashing:** no shooting.
  - The Peashooter fires every 0.11 s in code. That is ≈ 8.57 shots/s after 60 Hz quantization (own calculation), at 4 damage per shot.
- **Broforce:** primary fire is horizontal in the facing direction for the base bro. The base-class default `fireRate` is 0.0334 s (≈ 30 shots/s), and the community template uses 0.1 s. Firing works while running, jumping and climbing because the gun is a separate overlay layer. No up/down aim for the default primary was found.

### Cited Findings
**Cuphead (from [LevelPlayerWeaponManager.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerWeaponManager.cs), [LevelPlayerMotor.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs), [LevelPlayerAnimationController.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerAnimationController.cs))**

- **Aim angles:** `UpdateAim()` maps the direction pose to fixed angles. Facing right gives 0°, 45° (Up_D), 90° (Up), −45° (Down_D) and −90° (Down). Facing left mirrors these to 180°, 135°, 90°, −135° and −90°. That is 8 directions total (forward and back come from facing).
- **Pose selection (`GetCurrentPose`):**
  - EX takes priority.
  - Then **Duck**: down held, grounded, not locked.
  - Then **Jump**: airborne.
  - Then, if **Locked**: Up, Up_D, Down, Down_D or Forward, depending on the stick.
  - Else, if moving horizontally: **Forward_R** (run-shoot forward), or **Up_D_R** (run-shoot diagonal up) when up is also held.
  - Else, standing: **Up** when up is held, **Duck** when down is held, otherwise **Forward**.
  - So while running, the only directions are forward and diagonal-up. Down-diagonal on the ground becomes a duck with no movement (`HandleWalking`, `Ducking` = down && !Locked && Grounded).
- **Duck shots:** the bullet rotation is forced to 0° or 180°, i.e. forward only (`GetBulletRotation`).
- **Air shots:** the direction pose uses the stick freely (Up, Up_D, Forward, Down, Down_D, plus facing). That is 8-way in the air with no lock needed (`GetDirectionPose`).
- **Lock button:** `HandleLocked()`: Locked is true while the lock button (input action 6) is held **and** the player is grounded. When Locked, `HandleWalking` sets move = 0 and the animator's MoveX is forced to 0.
  - `HandleJumping` and `HandleDash` run before `HandleLocked`, so jump and dash still work from lock. Leaving the ground releases the lock automatically.
  - Locked aim uses dedicated `locked_*` idle clips plus `shoot_*` fire/hold clips (see the sprite section).
- **No firing while dashing or hit:** `HandleWeaponFiring()` returns immediately while dashing or hit. During a dash the direction pose reports Forward.
- **Animation layers:** layer weight 1 (**ShootRun**) is set to 1 while shooting, or for 0.0833 s after shooting stops (`STOP_SHOOTING_DELAY`). Layer 2 (**ShootRunDiag**) is weighted only when the stick is held up (`LookDirection.y > 0`).
  - The OnFire trigger, which drives the stationary shoot "fire" clip, fires only when grounded and (not moving, or locked, or ducking).
- **Fire rates and damage** ([WeaponProperties.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/WeaponProperties.cs)). The code-name to in-game-name mapping is my inference, except "spreadshot", which the [Fandom wiki](https://cuphead.fandom.com/wiki/File:Chaser.png) (per search summary) confirms as Spread's code name.
  - **Peashooter (`LevelWeaponPeashot`):** damage 4, bullet speed 2250 u/s (= 3375 px/s ≈ 14.7 H/s), `rapidFireRate` 0.11 s.
  - **Spread (`LevelWeaponSpreadshot`):** 1.24 per bullet, 2250 u/s, range `distance` 375 u, rate 0.13 s.
  - **Chaser (`LevelWeaponHoming`):** 2.85 damage, 1000 u/s, 0.15 s.
  - **Roundabout (`LevelWeaponBoomerang`):** 8.5 damage, 1400 u/s, 0.25 s.
  - **Lobber (`LevelWeaponBouncer`):** 11.6 damage, rate 0.33 s.
  - **Charge (`LevelWeaponCharge`):** base 6 damage, rate 0.25 s.
  - **Crackshot (`LevelWeaponCrackshot`):** 10.56 initial damage, 0.32 s.
- **Rate quantization:** the fire timer advances by `FixedDelta` (1/60 s) until it reaches the rate ([AbstractLevelWeapon.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/AbstractLevelWeapon.cs)), so rates round up to whole frames (own calculation):
  - Peashooter: 0.11 s → 7 frames = 0.1167 s → **8.57 shots/s**, ≈ 34.3 DPS.
  - Spread: 0.13 → 8 frames → 7.5 volleys/s.
  - Chaser: 9 frames → 6.67/s.
  - Roundabout: 15 frames → 4/s.
  - Lobber: 20 frames → 3/s.
- **Community figures:** a guide lists "8.57 peas per second", which matches the quantized value ([Expert Beacon](https://expertbeacon.com/what-is-the-best-super-in-cuphead/), via search summary, page not opened). The wiki lists Peashooter "Damage 4, DPS 30, EX 8.33 per hit (max 25)" ([Cuphead Wiki, Peashooter](https://cuphead.wiki.gg/wiki/Peashooter)). The wiki's 30 DPS conflicts with 4 × 8.57 ≈ 34.3; the source of the wiki number is not stated.
  - Code EX values: `damage 8.334`, `maxDamage 25`, speed 1500. The wiki says the EX "can be aimed in the usual eight directions" ([Cuphead Wiki, Peashooter](https://cuphead.wiki.gg/wiki/Peashooter)).
- **Community perception:** players describe a "limited 8 (?) way aiming system". One reply: "You either stay stationary and shoot in whatever direction or you run like hell... there is no inbetween" ([Steam discussion](https://steamcommunity.com/app/268910/discussions/0/1519260397784593893)).
  - **Contradicted by code:** a guide claims "You can aim and shoot in one direction while moving or dashing in another" ([ludo.guide](https://www.ludo.guide/guide/cuphead/walkthrough-progression/the-ultimate-guide/core-gameplay-mechanics/shooting-aiming-fundamentals)). The code blocks firing during the dash, and running allows only forward or diagonal-up.

**Broforce**

- **Fire rate (AI-generated docs):** `fireRate`: "Time interval between automatic weapon shots in seconds. Default value of 0.0334 provides approximately 30 shots per second". `fireCounter` accumulates time and fires when it exceeds `fireRate` ([Broforce-Docs TestVanDammeAnim](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/TestVanDammeAnim-Documentation.xml)). BroMaker also lists `"fireRate": 0.0334` as the global default ([BroMaker wiki, Variables](https://github.com/Gorzontrok/Bro-Maker/wiki/Variables)).
  - The community bro template (which uses Rambro's sprites) sets `"fireRate": 0.1` (10 shots/s) ([Bro Template.json](https://github.com/alexneargarder/Broforce-Templates/blob/master/Bro%20Template/Bro%20Template/_ModContent/Bro%20Template.json)).
- **Gun recoil animation:** on each shot `gunFrame` is set to 3 and counts down every 0.0334 s ([Broforce-Docs](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/TestVanDammeAnim-Documentation.xml)). The 4th gun frame "is displayed first when the fire button is pressed, then it animates backwards towards the first frame" ([BroMaker Spritesheets](https://github.com/Gorzontrok/Bro-Maker/wiki/Spritesheets)).
- **Independent gun layer:** the gun sheet "is overlaid on top of the main sprite sheet, and each has its own frame rate and frame counter... This allows you to use your weapon and have the animation for it play independently of the animation for your running / ducking / jumping" ([BroMaker Spritesheets](https://github.com/Gorzontrok/Bro-Maker/wiki/Spritesheets)).
- **Gun sheet rows:**
  - #0 Idle/Firing
  - #1 Idle/Firing while hanging
  - #2 Walking/Running
  - #3 Walking/Running while ducking
  - #4 unused ([BroMaker Spritesheets](https://github.com/Gorzontrok/Bro-Maker/wiki/Spritesheets))

  There is no up-aim or down-aim row.
- **Directional specials:** some bros' specials are aimable, e.g. Brochete: "Use your directional controls to send his special knife burst wherever you want" ([Steam tips thread](https://steamcommunity.com/app/274190/discussions/0/611701360820425405)).

### Inferences
- **The Cuphead lock is a "plant and aim" modifier, not a toggle.** It turns the movement stick into a pure 8-way aim stick only while held and only on the ground. Free movement and aiming are mutually exclusive on the ground, except for the diagonal-up run-shoot. For a heavy-MG comando this maps naturally to "brace/plant to aim", with only forward and diagonal-up while running. That would need 2 run-shoot cycles instead of 1, plus 5 planted aim directions.
- **Broforce shows that forward-only fire works for a Rambo parody** when movement verbs are rich (wall climb, chimney flip, hang) and destruction is high. The comando's current forward-only shooting already matches Broforce's model.
- The Peashooter's 3-drawing shoot loop (3 frames at 24 fps = 0.125 s) is roughly one drawing cycle per shot (0.117 s) (own comparison). At 12 fps the comando's shoot loop would need ≈ 1–2 drawings per shot at ≈ 8 shots/s, or a separately timed muzzle-flash and recoil layer, as Broforce does at 30 fps.

### Gaps
- Cuphead: the default lock binding. Search summaries said RB on Xbox and "C" on PC, but neither page could be opened (TrueAchievements HTTP 403).
- Broforce: Rambro's actual `fireRate` and projectile spread, and an authoritative statement that the primary cannot aim up or down, were not found. The latter is inferred from the gun sheet's rows and the absence of any aim fields in the docs.

---

## Sprite construction and animation frame counts (per state, per aim direction)

### Takeaway
- **Cuphead:** every pose is a full-body, hand-drawn frame on a single sprite renderer. There is no separate arm or gun layer for Cuphead and Mugman.
  - Aim directions are separate clips: 5 locked aim idles (11 frames each), and for each direction a 3-frame "fire" plus a 3-frame "hold".
  - Run-shoot is two extra full 16-frame run cycles (forward and diagonal-up), on Animator layers synchronized with the 16-frame run.
  - The air pose (spinning ball) has no aim drawings. Bullets spawn from per-pose hard-coded muzzle offsets.
  - Everything is 24 fps, except the jump and parry at 30 fps.
- **Broforce:** 32×32 px cells. The body sheet (32 columns × 16 rows) omits arms and gun in most locomotion frames. A separate 32×32 gun-and-arms sheet (32 × 2 cells) is overlaid and positioned by code offsets.
  - Body animation defaults to ≈ 15 fps and the gun animation to ≈ 30 fps.
  - Run (walk) and sprint are 8 frames each, the jump is 6 + 6 velocity-indexed frames, and idle is a single frame.

### Cited Findings
**Cuphead**

- **Developer statements:** animation was "set at 24 frames-per-second – just as it was in the 1930s – while the game runs at... 60 frames-per-second". Chad Moldenhauer describes "hand-drawing and inking each frame, animating on the ones". "All of the game's animated artwork has been drawn, penciled and inked on paper, and then colored in Photoshop." The page heading cites "50,000 frames" ([Unity, Made with Unity: Cuphead](https://unity.com/made-with-unity/cuphead)).
  - Inverse quotes MDHR: "We animated on the ones, and it's really, really fluid", and cites 120,000+ total frames ([Inverse](https://www.inverse.com/article/36647-xbox-one-cuphead-animation); from a search summary, page not opened). That conflicts with Unity's 50,000.
- **Frame counts:** own count of sprite keyframes in the published Unity clips ([AnimationClip folder](https://github.com/jmxamongusmodder/cuphead-decomp/tree/main/Assets/AnimationClip), e.g. [anim_player_run.anim](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/AnimationClip/anim_player_run.anim)). Each clip has one `m_Sprite` curve on the path "Cuphead", with parallel curves for the Mugman renderer.
  - Sprite references are stripped (placeholder GUIDs), so these are keyframe counts. Whether every key is a unique drawing could not be verified. Keys are spaced 1/24 s apart ("on ones").

  | Clip | Frames | Rate | Loop length | Loops? |
  |---|---|---|---|---|
  | idle | **11** | 24 fps | 0.5 s | yes |
  | run | **16** | 24 fps | 0.667 s | yes |
  | run_shoot_forward | **16** | 24 fps | 0.667 s | yes |
  | run_shoot_diagonal_up | **16** | 24 fps | 0.667 s | yes |
  | run_turnaround / run_shoot_turnaround / run_shoot_diagonal_turnaround | 2 each | 24 fps | — | — |
  | jump (the air "ball" loop) | **8** | **30 fps** | 0.267 s | yes |
  | parry | 8 | 30 fps | — | — |
  | locked_forward / locked_diagonal_up / locked_up / locked_diagonal_down / locked_down | **11 each** | 24 fps | 0.5 s | yes |
  | shoot_{forward, diagonal_up, up, diagonal_down, down}_fire | **3 each** | 24 fps | 0.125 s | no |
  | shoot_{…}_hold | **3 each** | 24 fps | — | yes |
  | duck_transition_in | 7 | 24 fps | — | — |
  | duck_idle | 11 | 24 fps | — | — |
  | duck_shooting_fire / duck_shooting_hold | 3 each | 24 fps | — | — |
  | duck_turn, duck_transition_out | 1 each | 24 fps | — | — |
  | dash_ground_pre / dash_air_pre | 2 each | 24 fps | — | — |
  | dash_ground / dash_air | 6 each | 24 fps | 0.25 s | — |
  | hit_ground | 10 | 24 fps | — | — |
  | ex_forward_ground | 15 | 24 fps | — | — |

  - There are 10 EX clips (5 directions × ground and air). The repo has 450 `anim_player_*` clips in total (most are other characters' or effects); none are named teeter, edge or ledge.
- **Aim set, totalled (own calculation):**
  - Ground aim poses for Cuphead: 5 locked directions × (11 idle + 3 fire + 3 hold) = 85 keys.
  - Plus run-shoot 2 × 16 = 32, plus duck-shoot 6.
  - Air aiming adds **zero** drawings: the jump-ball clip is used for all 8 directions.
- **Single full-body renderer:** the Player prefab has one renderer per character ("Cuphead", "Mugman"); the animation clips animate the `m_Sprite` of that single renderer ([Player.prefab](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/PrefabInstance/Player.prefab)). The 2022 DLC character **Ms. Chalice** instead has separate child renderers per aim direction ("ChaliceUpShoot", "ChaliceDiagUpShoot", "ChaliceForwardShoot", "ChaliceDiagDownShoot", …), plus code (`ChaliceAimSpriteHandling`, `chaliceJumpShootRenderers`) toggling overlay aim sprites. So MDHR moved to a layered aim overlay for the newer character ([Player.prefab](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/PrefabInstance/Player.prefab); [LevelPlayerAnimationController.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerAnimationController.cs)).
- **Muzzle and bullet spawn points:** a hard-coded table, `ProjectilePosition.Get(pose, direction)`, in units from the character origin. x is mirrored by facing; y is flipped by reversed gravity ([LevelPlayerWeaponManager.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerWeaponManager.cs)).

  | Pose | Offset (x, y) |
  |---|---|
  | Forward | (78, 64) |
  | Forward_R (run) | (70, 46) |
  | Up | (27, 158) |
  | Up_D | (71, 107) |
  | Up_D_R (run diagonal) | (73, 107) |
  | Down | (28, −11) |
  | Down_D | (71, 20) |
  | Duck | (102, 24) |
  | Jump, forward | (78, 64) |
  | Jump, up | (0, 158) |
  | Jump, up-diagonal | (71, 107) |
  | Jump, down | (0, −11) |
  | Jump, down-diagonal | (71, 20) |

  Ms. Chalice has her own values. Normalized (own calculation, H = 153), the forward muzzle sits 0.42 H high and 0.51 H forward, and the up muzzle 1.03 H high.

**Broforce**

- **Sprite and gun layers:** bro animation is "combining together the main sprite sheet and gun sprite sheet... many of the frames on the main sprite sheet leave the gun and arms of the bro out of the animation". Melee, special, high-five and climbing frames include the arms, and the gun sprite is hidden while they play ([BroMaker wiki, Spritesheets](https://github.com/Gorzontrok/Bro-Maker/wiki/Spritesheets)).
- **Frame sizes:** `spritePixelWidth` and `spritePixelHeight` default to **32** px, and `gunSpritePixelWidth` and `gunSpritePixelHeight` also to **32**. `gunSprite` is a "Sprite renderer component for the character's weapon. Updated independently from character sprite" ([Broforce-Docs TestVanDammeAnim](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/TestVanDammeAnim-Documentation.xml)).
  - Gun position comes from `SetGunPosition(xOffset, yOffset)`. For example, ducking uses offset (2, −1) ([Broforce-Docs](https://github.com/alexneargarder/Broforce-Docs/blob/master/Assembly-CSharp.xml)). BroMaker adds a per-bro `GunSpriteOffset` on top ([CustomHero.cs](https://github.com/Gorzontrok/Bro-Maker/blob/main/BroMakerLib/CustomObjects/Bros/CustomHero.cs)).
  - Custom bros index the gun sheet in 32-px steps, e.g. `gunSprite.SetLowerLeftPixel(32 * gunFrame, 32)` ([CaptainAmeribro.cs](https://github.com/alexneargarder/BroforceMods/blob/master/Captain%20Ameribro/Captain%20Ameribro/CaptainAmeribro.cs)).
- **Animation timing:** `frameRate` defaults to 0.0667 s per frame (≈ **15 fps**) for body animation. `gunCounter` updates every 0.0334 s (≈ **30 fps**). Idle "displays a static pose". Jump frames are chosen by velocity: rising if yI > 20, falling if yI < −55. The ducking run is an "8-frame cycle with foot effects every 4 frames" ([Broforce-Docs](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/TestVanDammeAnim-Documentation.xml)).
- **Rambro sheet frame counts:** own count of non-empty 32×32 cells in [rambroAnim.png](https://github.com/Gorzontrok/Bro-Maker/tree/main/images/Example%20Spritesheets) (1024×512 = 32 × 16 cells), mapped to the slot numbers in the labeled version and the slot table in [BroMaker Spritesheets](https://github.com/Gorzontrok/Bro-Maker/wiki/Spritesheets). Slot numbers are in brackets.
  - Idle/Ladder [0]: 4 cells. Only the first frame is the standing idle (1 frame); the other 3 are ladder frames.
  - Normal walking [7]: **8**.
  - Running or walking in a one-tile gap (duck-run) [8]: 8.
  - Sprinting [13]: **8**.
  - Jump with sideways momentum [10]: **6**.
  - Jump standing still [11]: **6**.
  - Crouch [2]: 4.
  - Knife wall-climbing [12]: 20.
  - Zipline/ceiling hang [14]: 18.
  - Rolling [9]: 13.
  - Ground melee [6]: 7.
  - Midair melee [19]: 7.
  - Chimney flip [20]: 12.
  - Special or grenade throw [17]: 8.
  - High-five [5]: 6.
  - Death [1]: 2.
- **Rambro gun sheet:** own count, [rambroGun.png](https://github.com/Gorzontrok/Bro-Maker/tree/main/images/Example%20Spritesheets) is 1024×64 = 32 × 2 cells.
  - Idle and fire: 4 cells (1 idle + 3 recoil).
  - Hanging idle and fire: 4.
  - Second row: 32 filled cells whose pixel counts repeat with period 8. Read as running gun bob 8, ducking-run gun bob 8, and 16 unused.
- **Measured sizes (own measurement, opaque bounding boxes):**
  - Idle body 15 × 19 px (x 7–21, y 12–30 inside the 32-px cell).
  - Walk and jump frames 14–15 × 18–19 px.
  - Gun overlay at idle 16 × 8 px. The firing frame with muzzle flash is 22 × 9 px.
  - Body plus gun at idle spans ≈ 18 px wide.
- **Pixel size on screen:** no Free Lives statement found. The Ludum Dare origin is "Rambros" (April 2012) ([Wikipedia, Free Lives](https://en.wikipedia.org/wiki/Free_Lives), via search summary).

### Inferences
- **Two opposite philosophies.** Cuphead pays for every aim direction with full-body drawings: about 120 extra keys per character just for aiming and run-shooting. It avoids air-aim art by making the jump a ball. Broforce pays almost nothing for weapon animation because arms and gun are an overlay, and it never draws up/down aims.
- **For an HD, 128 px, 12 fps comando with a heavy MG, a hybrid is the realistic middle ground.** This is in line with MDHR's own later choice for Ms. Chalice.
  - Draw full-body frames for the 2 run-shoot cycles (forward, diagonal-up).
  - Use a separate upper-body or arms+gun overlay (Broforce style) for the 5 planted lock directions and the air directions.
  - Keep a code-side muzzle-offset table per pose, as both games do.
- **Frame-budget translation (own calculation):** at 12 fps, a cycle as long as Cuphead's run (0.667 s) needs 8 frames. A Broforce-length cycle (8 frames at 15 fps = 0.533 s) needs ≈ 6–7 frames. Run-shoot cycles must have the same frame count and length as the base run so the layers can switch mid-stride, as Cuphead's 16/16/16 does.

### Gaps
- Cuphead: unique drawings per clip (sprite GUIDs stripped), the exact Animator state machine (controller not inspected), and Cuphead's sprite texture resolution and pixels-per-unit (sprite assets not in the repo) were not found.
- Broforce: the exact frame rates for running and jumping per bro, and whether vanilla bros other than Rambro share the layout. BroMaker says "for the most part they should".

---

## Hitbox vs visible sprite, and platform-edge behaviour

### Takeaway
- **Cuphead:** a 50 × 105-unit box on the ground (≈ 75 × 158 px at 1080p), against a ≈ 153-unit-tall figure including the straw. In the air the box shrinks to 50 × 50 and when ducking to 50 × 35. Ground detection uses the full 50-unit width, so Cuphead stays grounded until the whole box clears the edge. There is no teeter animation.
- **Broforce:** a 12-unit-wide body (`halfWidth` 6) against a 15-px-wide visible body (≈ 18 px with gun). Head height is 18 standing and 13 ducking. Ledge-grab and edge-slip logic exist, but the details are thin.

### Cited Findings
- **Cuphead colliders:**
  - Default collider: center (0, 62), size **(50, 105)**, so it spans 9.5–114.5 units above the origin.
  - Air: center (0, 50), size **(50, 50)**.
  - Ducking: center (0, 27), size **(50, 35)**.
  - Sources: [LevelPlayerColliderManager.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerColliderManager.cs). The default box is also serialized in [Player.prefab](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/PrefabInstance/Player.prefab) as `m_Offset {0, 62}`, `m_Size {50, 105}`.
  - Conversion (own calculation): the ground box is 75 × 158 px at 1080p. It covers ≈ 0.69 of the 153-u total height, excluding the straw and upper cup.
- **Cuphead visible width:** ≈ 70–90 units including the cup handle and pointing hand (own rough measurement on the same Steam screenshot; low precision), against a 50-unit box.
- **Cuphead edges:** ground and ceiling probes are box casts the full `DefaultWidth` (50 u) wide ([LevelPlayerMotor.cs, HandleRaycasts](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs)). So the player remains grounded with the centre up to ≈ 25 u (≈ 0.16 H) past a platform edge (inference from the cast width). No teeter or edge clip exists among the published player clips (own check of [AnimationClip](https://github.com/jmxamongusmodder/cuphead-decomp/tree/main/Assets/AnimationClip) names).
- **Broforce body (AI-generated docs):**
  - `halfWidth` default **6** ("used throughout for wall collision boundaries, ledge detection").
  - `standingHeadHeight` 18 and `duckingHeadHeight` 13.
  - `standingWaistHeight` 10 and `duckingWaistHeight` 6.
  - `toeHeight` 4 standing and 5 ducking.
  - `feetWidth` 4 for ground raycasts.
  - `Unit.width` and `Unit.height` default to 8 (base Unit class; apparently overridden by the hero fields).
  - Source: [Broforce-Docs TestVanDammeAnim](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/TestVanDammeAnim-Documentation.xml); [Unit docs](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/Unit-Documentation.xml).
- **Broforce edges (AI-generated docs):** `CalculateMovement` includes "edge slip prevention". Ledge grapple uses `ledgeOffsetY` (0–13) to pick the frame. One-armed hanging uses row 11, frame 0 ([Broforce-Docs](https://github.com/alexneargarder/Broforce-Docs/blob/master/Classes/TestVanDammeAnim-Documentation.xml)).
- **Broforce visible size:** body 15 × 19 px; with gun ≈ 18 px wide; firing ≈ 22 px (own measurement, see the sprite section).

### Inferences
- Both games make the hurtbox narrower than the art:
  - Cuphead: 50 u against ≈ 70–90 u visible, ≈ 0.55–0.7 of the width.
  - Broforce: 12 against 15–18 px, ≈ 0.65–0.8.
- Cuphead's hurtbox also excludes the top of the head, and it shrinks to a 50 × 50 ball in the air.
- For the comando, a hurtbox ≈ 0.5–0.6 of the visible width that excludes the protruding MG barrel follows both references.

### Gaps
- Broforce: the exact ground-probe geometry and the edge-slip rule (whether bros can stand on ≥ 4 u of overhang) were not found.
- Cuphead: no precise visible-width measurement, because sprite rips were inaccessible.

---

## Datamined values and developer statements (provenance summary)

### Takeaway
- **Cuphead:** almost all numbers come from a published community decompilation (reliable as code, unofficial, post-DLC build). MDHR's public statements cover 24 fps on ones, the 60 fps game rate and frame totals, but not the lock-button rationale.
- **Broforce:** numbers come from AI-generated community docs plus BroMaker's human-written defaults table. No Free Lives statements about controls or pixel scale were found.

### Cited Findings
- **Cuphead decomp provenance:**
  - It is a "Decompilation of cuphead" including the DLC ([GitHub repo](https://github.com/jmxamongusmodder/cuphead-decomp)).
  - Other public decomps exist ([tanosshi/Cuphead-Decomp](https://github.com/tanosshi/Cuphead-Decomp), Unity 5.6.2p1 per search summary).
  - The input buffer is `INPUT_BUFFER_TIME = 0.134`, coyote time is 0.0834, and the fixed step is 1/60 ([LevelPlayerMotor.cs](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/Assets/Scripts/Assembly-CSharp/LevelPlayerMotor.cs); [TimeManager.asset](https://github.com/jmxamongusmodder/cuphead-decomp/blob/main/ProjectSettings/TimeManager.asset)).
- **MDHR on influences:** Chad Moldenhauer said they really love Contra (paraphrase; [GameRevolution preview](https://www.gamerevolution.com/games/67242-cuphead-preview), via search summary). Other references cited are Contra, Gunstar Heroes and Mega Man ([GoNintendo](https://gonintendo.com/stories/331523-switch-news-channel-features-a-nintendo-interview-with-jared-mold), via search summary). No statement explaining the lock or aim scheme was found.
- **Broforce-Docs reliability:** the README says "generated automatically by having an AI analyze the game's code... I would advise against completely trusting it" ([Broforce-Docs README](https://github.com/alexneargarder/Broforce-Docs)).
- **BroMaker defaults** (`speed 110`, `_jumpForce 260`, `JUMP_TIME 0.123`, `maxFallSpeed −400`, `fireRate 0.0334`, `canWallClimb true`, `canLedgeGrapple false`) are presented "with their default values" ([BroMaker wiki, Variables](https://github.com/Gorzontrok/Bro-Maker/wiki/Variables)).

### Inferences
- Treat the Cuphead constants as high-confidence for the current PC build, and the Broforce constants as medium-confidence base-class defaults: they agree across two independent community sources, but per-bro prefab values are unknown.

### Gaps
- No GDC talk by Studio MDHR or Free Lives about player controls was found. No Free Lives devlog about bro pixel resolution or the forward-only fire design was found.

---

## Comparison summary (one row per game)

### Takeaway
Cuphead is a precise, HD, full-body-redraw design: slower relative to its body, an 8-way aim gated by a ground "lock", and costly aim art. Broforce is a fast, tiny-sprite, layered design: forward-only fire, a gun overlay, and rich traversal verbs. The comando sits between them: HD like Cuphead, but forward-only like Broforce.

### Cited Findings
All values are sourced in the sections above. H = character height: Cuphead 153 u (230 px at 1080p, including the straw; 105-u collider), Broforce 19 u (19 px art; ≈ 80–85 px on a 1080p screenshot).

| Game | Run speed | Accel | Jump height / airtime | Air control | Variable jump / coyote / buffer | Shoot directions & selection | Shoot while running / air | Aim lock | Sprite construction | Frames & fps: idle / run / jump / shoot | Hitbox vs sprite width | Edge behaviour |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Cuphead** | 490 u/s = 735 px/s at 1080p = 3.2 H/s (4.0 body-H/s). Dash 1100 u/s × 0.3 s = 330 u ≈ 2.2 H, horizontal, no gravity, 1 per airtime, no firing | Instant (velocity = axis × speed) | Full ≈ 265 u = 397 px = 1.73 H, 0.63 s. Tap ≈ 115–134 u = 0.75–0.87 H, 0.40–0.43 s. Launch 1223 u/s, g ≈ 5,992 u/s², fall cap 1620 u/s. Parry bounce ≈ 206 u | Full, instant, same speed as ground | Hold 0.01–0.16 s (sustained launch velocity). Coyote 0.0834 s (5 f). Buffer 0.134 s, mainly during dash or lock-out. No double jump (Ms. Chalice only) | 8 fixed angles (0/45/90/−45/−90°, mirrored), chosen by the movement stick. Idle: forward or up. Duck: forward only | Running: forward and diagonal-up only. Air: all 8, no aim pose. Dash: no shooting | Hold lock (ground only): stops walking, stick aims 8 ways in place. Jump and dash still allowed | Full-body hand-drawn frames on one renderer. Separate clips per aim direction. Run-shoot as synchronized Animator layers. Muzzle table per pose. (DLC Ms. Chalice uses aim overlays) | Idle 11 @24. Run 16 @24 (0.667 s). Jump ball 8 @30. Locked aim 11 @24 ×5 directions. Shoot fire 3 + hold 3 @24 per direction. Run-shoot 16 @24 ×2 | Collider 50 × 105 u (air 50 × 50, duck 50 × 35) against ≈ 70–90 u visible (≈ 0.55–0.7) | Grounded until the 50-u box clears the edge (centre up to ~25 u over). No teeter anim. No ledge grab |
| **Broforce** (base bro / Rambro sheets) | 110 u/s = 5.8 H/s (≈ 460–495 px/s on one 1080p screenshot). Sprint via dash button or double-tap (multiplier not found) | Ramped but snappy (≥ 10 u/s on press; exact curve not found) | Full ≈ 63 u = 3.3 H ≈ 3.9 tiles, ≈ 0.70 s. Tap ≈ 31 u = 1.6 H, ≈ 0.47 s. Jump 260 u/s, g 1100 u/s², fall cap 400 u/s (own calc. from defaults) | Present (same AddSpeed functions; magnitude not documented) | Hold up to 0.123 s (docs also say 0.13). Landing-jump buffer exists (duration not found). Coyote not found. No double jump (perk-only air jumps) | Horizontal in the facing direction for the primary. Some specials are directional (e.g. Brochete) | Yes: the gun is an independent overlay, so it fires while running, jumping or climbing | None | 32 × 32 px body sheet (32 × 16 cells) without arms/gun in locomotion, plus a 32 × 32 gun-and-arms overlay sheet (32 × 2) positioned by code offsets | Idle 1 static frame. Walk 8, sprint 8 (body ≈ 15 fps → ≈ 0.53 s cycle). Jump 6 + 6, velocity-indexed. Gun: idle 1 + 3-frame recoil @ ≈ 30 fps (0.1 s). Fire rate default 0.0334 s (template 0.1 s) | `halfWidth` 6 → 12 u, against a 15 px body (≈ 18 px with gun, 22 px firing) | Ledge grapple flag (default false per BroMaker, true per AI docs). Chimney flip over corners. Wall climb, wall drag, ceiling/zipline hang. "Edge slip prevention" (details unknown) |

### Inferences
- **Rough feel targets for the comando** (H = 128 px at 1x; own calculation):

  | Feel | Run | Jump apex | Airtime | Gravity |
  |---|---|---|---|---|
  | Cuphead-like | ≈ 410 px/s | ≈ 220 px (tap ≈ 100 px) | ≈ 0.63 s | ≈ 5,000 px/s² |
  | Broforce-like | ≈ 740 px/s | ≈ 420 px | ≈ 0.7 s | — |

  A heavy two-handed MG argues for the Cuphead end, or a little slower.
- **The aim decision maps directly to cost:**
  - Forward-only (Broforce) costs nothing.
  - Cuphead-style costs, per character: 2 extra run cycles (forward, diagonal-up), 5 planted directions × (idle + fire + hold), and 1 duck-shoot. Air aim can be free if the jump pose hides the gun (Cuphead's ball). Otherwise it needs an arms+gun overlay (Broforce or Ms. Chalice style).

### Gaps
- See the per-section gaps. The largest are:
  - Broforce: Rambro's real fire rate, coyote time and buffer durations, and the camera px-per-unit.
  - Cuphead: a verified default lock binding and unique-drawing counts per clip.
