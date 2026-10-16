# Celeste player movement and platformer jump-feel literature (for the "comando" run-and-gun)

Conventions used throughout:
- Evidence tags: **[code]** = read directly in public source code; **[dev]** = developer statement; **[community]** = community wiki/docs/fan projects; **[secondary]** = third-party article or search-result summary I could not open in full; **(own calculation)**, **(own measurement)**, **(own count)** = my own work, inputs shown.
- Celeste runs at 60 fps on a 320×180 canvas (the 320×180 figure is confirmed by [Maddy Thorson, "Celeste & Forgiveness"](https://maddymakesgames.com/articles/celeste_and_forgiveness/); 60 fps is the task premise and is consistent with every frame count on the [Celeste Wiki Tech page](https://celeste.ink/wiki/Tech)). 1 frame = 1/60 s.
- Celeste normalization heights: **H_hb = 11 px** (collision hitbox height, [code](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L263)) and **H_vis ≈ 16 px** (visible standing sprite, own measurement, see Q3). The comando uses **H_vis = 128 px** and **H_hb = 108 px** (team spec).
- Player.cs links point to `master` of github.com/NoelFB/Celeste. I read the file on 2026-10-15 (5,471 lines), so the line numbers apply to that version.

## Q1. Celeste's exact movement constants and forgiveness mechanics (Player.cs + input buffering)

### Takeaway
Player.cs has every movement constant in px/s or px/s² and seconds, in lines 23–138. Celeste uses one gravity (900 px/s²) for both rising and falling. Its jump feel comes from four things: a 0.2 s "sustain" that holds the launch speed while the button is held; half gravity near the apex while the button is held; a low terminal velocity; and many small forgiveness windows (0.1 s coyote timer, about 4-frame input buffer, 4 px corner correction, wall-jump checks 3 px out).

### Cited Findings
**Run and air control** [code]
- `MaxRun = 90f`, `RunAccel = 1000f`, `RunReduce = 400f`, `AirMult = .65f`, `HoldingMaxRun = 70f` — [Player.cs L30–35](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L30-L35). `WalkSpeed = 64f` (cutscene walking) — [L138](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L138).
- How they are applied: `mult = onGround ? 1 : AirMult`. If |Speed.X| > max and the input points the same way, speed moves toward max at `RunReduce*mult` ("Reduce back from beyond the max speed"). Otherwise it moves toward `max*moveX` at `RunAccel*mult`. That one rate covers accelerating, braking with no input (target 0) and turning around — [L2879–2895](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2879-L2895). So Celeste has no separate deceleration or turn constant: friction equals acceleration (1000 px/s² on the ground, 650 in the air). RunReduce only gently bleeds off speed above the cap (for example after a jump boost or a dash).

**Gravity, fall, apex** [code]
- `MaxFall = 160f`, `Gravity = 900f`, `HalfGravThreshold = 40f`, `FastMaxFall = 240f`, `FastMaxAccel = 300f` — [L23–28](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L23-L28).
- Gravity is applied only when airborne: `mult = (Math.Abs(Speed.Y) < HalfGravThreshold && (Input.Jump.Check || AutoJump)) ? .5f : 1f; Speed.Y = Calc.Approach(Speed.Y, max, Gravity * mult * Engine.DeltaTime);` — [L2952–2957](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2952-L2957). Gravity is halved only while |vy| < 40 px/s **and** jump is held. Gravity stops adding speed at the current max fall speed (`Approach`), so terminal velocity is a hard cap.
- Fast fall: holding Down while already at ≥ MaxFall raises the cap from 160 toward 240 at 300 px/s². The sprite also stretches as it nears that speed (scale lerps to 0.5×1.5) — [L2897–2925](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2897-L2925).

**Jump, variable jump** [code]
- `JumpGraceTime = 0.1f`, `JumpSpeed = -105f`, `JumpHBoost = 40f`, `VarJumpTime = .2f`, `CeilingVarJumpGrace = .05f`, `UpwardCornerCorrection = 4` — [L48–53](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L48-L53).
- `Jump()`: consumes the buffer, zeroes the coyote timer, sets `varJumpTimer = VarJumpTime`, `Speed.X += JumpHBoost * moveX`, `Speed.Y = JumpSpeed`, adds platform lift (`LiftBoost`) and stores `varJumpSpeed = Speed.Y`. It also squashes the sprite to scale (0.6, 1.4) — [L1660–1693](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1660-L1693).
- How the variable jump works: `if (varJumpTimer > 0) { if (AutoJump || Input.Jump.Check) Speed.Y = Math.Min(Speed.Y, varJumpSpeed); else varJumpTimer = 0; }` — [L2960–2967](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2960-L2967). While held, for up to 0.2 s, upward speed is **re-pinned to the launch speed every frame**, so gravity is cancelled and the character rises at a constant 105 px/s. Releasing just ends the sustain. There is **no velocity cut and no gravity change** on release, so the rest of the arc is a normal ballistic one.
- Ceiling bonk: on hitting a ceiling while rising, the game first tries corner correction. If that fails, the variable jump is cancelled, unless the jump started less than 0.05 s ago (`if (varJumpTimer < VarJumpTime - CeilingVarJumpGrace) varJumpTimer = 0;`) — [L2585–2615](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2585-L2615).

**Coyote time** [code]
- While `onGround`, `jumpGraceTimer = JumpGraceTime`; while airborne it counts down by DeltaTime — [L712–720](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L712-L720). A press calls `Jump()` whenever `jumpGraceTimer > 0`, before any wall-jump check — [L2970–2975](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2970-L2975).
- `onGround` is computed only when `Speed.Y >= 0`, from a Solid (or a JumpThru, from outside) 1 px below the hitbox — [L632–651](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L632-L651).
- [community] "5 coyote frames" after walking off a ledge — [Celeste Wiki, Tech §1.4](https://celeste.ink/wiki/Tech); also "up to 5 frames" in the [DGMI wiki, Coyote Time](https://dgmiwiki.wpi.edu/mechanic/coyote_time).

**Jump input buffer** (Input / VirtualButton)
- [code] Player.cs reads `Input.Jump.Pressed` and calls `Input.Jump.ConsumeBuffer()` on every jump type ([L1662](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1662), [L1739](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1739)). The constant that sets the buffer length lives in Celeste's `Input.Initialize`, which is **not** in the open-sourced file.
- [code, Everest reimplementation] The modding framework's replacement of Monocle `VirtualButton` shows how the buffer works. `Update()` does `bufferCounter -= Engine.DeltaTime`, sets `bufferCounter = BufferTime` on a new press, and **sets `bufferCounter = 0` whenever the button is not down**. `Pressed` returns true while `bufferCounter > 0` unless already consumed — [Everest VirtualButton.cs L56–62, L153–185](https://github.com/EverestAPI/Everest/blob/dev/Celeste.Mod.mm/Patches/Monocle/VirtualButton.cs). So the buffer only survives **while the button is held**. This matches Maddy's wording: "If you press and hold the jump button a short time before landing…" ([dev](https://maddymakesgames.com/articles/celeste_and_forgiveness/)). Caveat: this is Everest's `[MonoModReplace]` copy of vanilla code, not the vanilla file itself.
- [community] Buffer = **4 frames**: "Attempting to perform an action that's not currently possible will 'buffer' (store) the input for the next 4 frames" — [Celeste Wiki, Tech §1.9](https://celeste.ink/wiki/Tech). Older wiki revisions say 5 frames ([Techniques](https://celeste.ink/wiki/Techniques), [User:Snowmanonahoe/Techniques](https://celeste.ink/wiki/User:Snowmanonahoe/Techniques)). This conflict is unresolved in the sources.
- A BufferTime of 0.08 s is often quoted from decompiled code. I could **not** confirm it in any public source. Treat it as unverified, though it would give exactly 4 frames (see Q2).

**Ducking** [code]
- Hitboxes: `normalHitbox = new Hitbox(8, 11, -4, -11)`, `duckHitbox = new Hitbox(8, 6, -4, -6)`, `normalHurtbox = new Hitbox(8, 9, -4, -11)`, `duckHurtbox = new Hitbox(8, 4, -4, -6)` — [L263–266](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L263-L266). Ducking swaps the collider ([L2112–2133](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2112-L2133)), so the box shrinks from 11 to 6 px tall (55%).
- You duck when on the ground, holding Down, with vy ≥ 0. The sprite squashes to (1.4, 0.6) — [L2856–2876](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2856-L2876). Ducked ground friction is `DuckFriction = 500f` ([L40](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L40), [L2880–2881](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2880-L2881)).
- Un-duck forgiveness: if a ceiling blocks standing up and the player is stopped, the game looks up to `DuckCorrectCheck = 4` px left and right for room and slides there at `DuckCorrectSlide = 50f` px/s — [L41–42](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L41-L42), [L2830–2856](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2830-L2856). Un-ducking squashes the sprite to (0.8, 1.2).

**Corner correction** [code]
- Upward (jump): when rising into a ceiling, the game tries offsets of 1…4 px sideways (in the direction of Speed.X, or both directions if Speed.X = 0) combined with 1 px up, and takes the first free spot — [L2585–2612](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2585-L2612) with `UpwardCornerCorrection = 4`.
- Dash: `DashCornerCorrection = 4`, `DashVFloorSnapDist = 3` — [L82–83](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L82-L83). A horizontal dash that hits a wall tries ±1…4 px vertical shifts ([L2398–2418](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2398-L2418)). An air dash moving down that lands near a ledge corner tries 1…4 px horizontal shifts to slip off it ([L2504–2531](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2504-L2531)). A horizontal dash snaps down onto a floor up to 3 px below ([L920–925](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L920-L925)).
- Jump-through assist: while rising inside a one-way platform, the player is nudged up at `JumpThruAssistSpeed = -40f` — [L127](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L127), [L916–918](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L916-L918).

**Wall jump grace, climb hop** [code]
- `WallJumpCheckDist = 3`, `WallJumpForceTime = .16f`, `WallJumpHSpeed = MaxRun + JumpHBoost` (= 130 px/s), `WallSpeedRetentionTime = .06f` — [L54–58](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L54-L58). `WallJumpCheck(dir)` tests whether the hitbox, shifted 3 px toward the wall, overlaps a Solid — [L1731–1734](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1731-L1734). With Monocle's right/bottom-exclusive rectangles (an assumption, since the engine isn't in the repo), this accepts a gap of up to 2 px, which matches Maddy's "2 pixels away" ([dev](https://maddymakesgames.com/articles/celeste_and_forgiveness/)). The community wiki says "no more than 3 pixels away" ([Tech §3.2](https://celeste.ink/wiki/Tech)), probably counting differently.
- A wall jump sets Speed = (±130, −105), restarts the 0.2 s sustain, and forces the horizontal direction for 0.16 s if a direction was held — [L1736–1770](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1736-L1770).
- Climb hop: `ClimbHopY = -120f`, `ClimbHopX = 100f`, `ClimbHopForceTime = .2f`, `ClimbHopNoWindTime = .3f` — [L115–119](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L115-L119). When climbing upward runs past the top of the wall, `ClimbHop()` pops the player up (vy ≤ −120) and forward (100 px/s) onto the ledge, with input locked for 0.2 s — [L3136–3150](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3136-L3150), [L3291–3313](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L3291-L3313).

**Frame-order detail** [code]
- Order within `Player.Update`: ground check and timers (coyote, varJump) first → state machine (`base.Update()`: run, gravity, var-jump, jump press) → `MoveH(Speed.X * DeltaTime)` then `MoveV(Speed.Y * DeltaTime)` with sub-pixel remainders — [L632–744](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L632-L744), [L908–935](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L908-L935). The developers' readme says "Celeste's physics system is very similar to TowerFall's" and links Maddy's TowerFall physics article — [Readme.md](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Readme.md).

### Inferences
- Celeste's rise is **linear then parabolic**: constant 105 px/s for about 0.2 s, then a short parabola softened by half gravity. Upward speed never jumps instantly, so a quick tap still gives a smooth (if short) arc.
- Because gravity is the same both ways but the rise includes the linear sustain, the fall (≈0.30 s) is still shorter than the rise (≈0.36 s) (own calculation, Q2). Celeste gets an "asymmetric" jump without a separate fall-gravity constant.

### Gaps
- The vanilla `Input.Initialize` (jump BufferTime) and Monocle `Engine` (exact DeltaTime) are not public. Engine.DeltaTime could be 1/60 or 0.0166667 (166,667 ticks); I found no public source for which. The community frame counts (5 coyote frames, 4 buffer frames) match DeltaTime slightly above 1/60 (Q2).

## Q2. Derived Celeste metrics in comparable units (own calculations)

### Takeaway
A full held jump rises about **28 px** (≈2.5 hitbox heights, ≈1.75 visible heights, ≈3.5 tiles of 8 px). It reaches the apex in about **0.36 s (≈22 frames)** and lasts about **0.63–0.66 s (38–40 frames)** on flat ground. A tap jump rises about **7–8 px** (≈28% of full). Max run is **90 px/s = 1.5 px/frame ≈ 8.2 hitbox heights/s ≈ 5.6 visible heights/s**, reached in **6 frames** on the ground and **9 frames** in the air.

### Cited Findings
Inputs come from [code] Q1 (JumpSpeed 105, Gravity 900, HalfGravThreshold 40, VarJumpTime 0.2, MaxFall 160, MaxRun 90, RunAccel 1000, AirMult 0.65, JumpHBoost 40, RunReduce 400; [Player.cs L23–53](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L23-L53)).

**Full jump, continuous math (own calculation)**
- Sustain phase: 105 px/s × 0.2 s = **21.0 px**, 0.200 s.
- Decelerate 105→40 at 900: (105² − 40²)/(2·900) = **5.24 px**, 65/900 = 0.072 s.
- Apex zone 40→0 at half gravity 450: 40²/(2·450) = **1.78 px**, 40/450 = 0.089 s.
- **Height = 28.0 px; time to apex = 0.361 s = 21.7 frames.**
- Fall (still holding): 0→40 at 450 (1.78 px, 0.089 s), 40→160 at 900 (13.33 px, 0.133 s), then the remaining 12.9 px at the 160 px/s cap (0.081 s) → **fall = 0.303 s; total airtime = 0.664 s = 39.8 frames.**
- Without half gravity (counterfactual): 21 + 105²/1800 = **27.1 px**, so the apex trick adds only ~0.9 px of height but ~0.09 s of hang time.

**Frame-exact simulation (own calculation)**: a float32 replay of the Update order above, with integer pixel moves and sub-pixel remainders; script kept in scratchpad, not in the repo.
- DeltaTime = 1/60: full hold = 29 px, apex at frame 20–21, lands frame 39 (0.650 s), 13 frames at −105 px/s.
- DeltaTime = 0.0166667: full hold = 27 px, apex at frame 18–21, lands frame 38 (0.633 s), 12 frames at −105.
- Hold 1 frame (tap) = 7 px, lands frame 14 (0.233 s). Hold 4 = 12 px. Hold 6 = 16 px. Hold 8 = 19 px. Hold 10 = 23 px. Hold 12 = 26 px. Height grows almost linearly with hold time (~1.75 px per held frame), which makes the jump very controllable.
- Tap, continuous: 105/60 + 105²/1800 = 7.9 px; airtime ≈ 0.27 s (≈16 frames). The discrete sim gives 14 frames because landing is snapped to whole pixels.

**Timer windows at 60 fps (own calculation, float32)**
- Coyote (0.1 s timer): **5 airborne frames** with DeltaTime 0.0166667, or 6 with exact 1/60. The community says 5 ([Tech §1.4](https://celeste.ink/wiki/Tech)).
- Var-jump sustain (0.2 s): 11 frames after the press frame (0.0166667) or 12 (1/60).
- A hypothetical 0.08 s buffer gives 4 frames after the press under both DeltaTimes, matching the wiki's 4 frames ([Tech §1.9](https://celeste.ink/wiki/Tech)).

**Run metrics (own calculation)**
- 90 px/s = **1.5 px/frame**; 90/11 = **8.2 H_hb/s**; 90/16 = **5.6 H_vis/s**; 90/320 = 28% of screen width per second.
- Ground 0→90: 90/1000 = 0.09 s = 5.4 → **6 frames**. Air: 90/650 = 0.138 s = 8.3 → **9 frames**. Ground stop from 90: 6 frames. Ground turnaround (+90→−90): 10.8 → 11 frames. Air turnaround: 16.6 → 17 frames.
- JumpHBoost: jumping while holding a direction adds 40 px/s (130 px/s total, 1.44× MaxRun). That extra speed decays at RunReduce×AirMult = 260 px/s² in 0.154 s (≈9 frames).
- Horizontal reach of a full running jump on flat ground: 90 × 0.664 + ½·40·0.154 ≈ **62.8 px ≈ 7.9 tiles ≈ 5.7 H_hb ≈ 3.9 H_vis**.

**Other conversions (own calculation)**
- Gravity 900 px/s² = 0.25 px/frame². JumpSpeed 105 px/s = 1.75 px/frame. MaxFall 160 = 2.67 px/frame (= **1.52× jump speed**). FastMaxFall 240 = 4 px/frame (2.29× jump speed). Apex threshold 40 px/s = 0.38× jump speed = 0.044 s × g.
- Jump squash (0.6, 1.4) recovers toward 1 at 1.75/s ([L1165–1166](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1165-L1166)): 0.4/1.75 = 0.23 s ≈ 14 frames.

### Inferences
- In hitbox heights Madeline's jump is very tall (2.5 H_hb). Against the visible sprite it is 1.75 H_vis. The comando's 108 px apex is 0.84 H_vis / 1.0 H_hb, about **half** Madeline's jump relative to body, with almost the **same airtime** (0.674 s vs 0.664 s).

### Gaps
- No public source gives "official" jump height or airtime; all of these numbers are derived. Real values depend on sub-pixel remainder at takeoff and on DeltaTime (±1–2 px, ±1 frame).

## Q3. Celeste hitbox vs sprite, ledges and the edge (teeter) animation

### Takeaway
The collision box is 8×11 px with its origin at bottom-centre; the hurtbox is 8×9 and leaves out the bottom 2 px (feet). The visible Madeline is about 16 px tall and 10–12 px wide (own measurement). She has front-edge ("edge") and back-edge ("edgeBack") teeter animations. They play when she is idle on the ground and the floor is missing 1 px ahead of her centre and at her front hitbox edge. She stays standing as long as any part of her 8 px box overlaps ground, so up to 7 of 8 columns can hang over the void. There is no other ledge forgiveness beyond coyote time and the dash corner slips.

### Cited Findings
- [code] Hitboxes as in Q1: `Hitbox(8, 11, -4, -11)` means width 8, height 11, offset (−4, −11). The entity Position is the **bottom-centre** of the box — [L263–266](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L263-L266). The hurtbox `Hitbox(8, 9, -4, -11)` covers only the top 9 px, so the bottom 2 px of the collision box are not hurtable. The community wiki notes the same ("wall-collision hitbox extends 2 pixels below the hurtbox", [Tech §3.2.2](https://celeste.ink/wiki/Tech)).
- [code] Edge animation condition, inside the on-ground animation branch: `else if (Math.Abs(Speed.X) <= RunAccel / 40f && moveX == 0)` (i.e. |vx| ≤ 25 px/s and no horizontal input), not holding anything, and
  `!Scene.CollideCheck<Solid>(Position + new Vector2((int)Facing * 1, 2)) && !Scene.CollideCheck<Solid>(Position + new Vector2((int)Facing * 4, 2)) && !CollideCheck<JumpThru>(Position + new Vector2((int)Facing * 4, 2))` → `Sprite.Play(PlayerSprite.FrontEdge)`. The mirrored test (`-(int)Facing`) → `Sprite.Play("edgeBack")`. Otherwise she plays lookUp (Up held) or idle — [L1246–1270](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1246-L1270). The probes are single points 2 px below the feet, at 1 px and 4 px from the centre line toward the facing side (front edge) or the back side (back edge).
- [code] Standing support: `onGround` is true whenever the box moved 1 px down overlaps a Solid ([L637–644](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L637-L644)). Any 1-px overlap of the 8-px box keeps her standing.
- (own measurement) Visible sprite size. I measured two official 1920×1080 Steam screenshots ([store page](https://store.steampowered.com/app/504230/Celeste/); 1920/320 = 6× scale), sampling one point per 6×6 block. Standing Madeline spans **15–17 game px tall** (hair top to boot bottom, with or without the 1-px dark outline) and **≈10–12 px wide** (backpack to front hand). I use **H_vis ≈ 16 px**. So the hitbox is ≈69% of visible height (11/16) and ≈67–80% of visible width (8/10–12). The hurtbox is ≈56% of visible height (9/16).
- [dev] The narrow, forgiving positional windows are deliberate: "All are centered around widening timing or positioning windows" — [Maddy Thorson, Celeste & Forgiveness](https://maddymakesgames.com/articles/celeste_and_forgiveness/).

### Inferences
- Teeter onset (own calculation): with right/bottom-exclusive rectangles and a solid ending at x = E, facing the edge, the front-edge pose starts when X ≥ E − 1. The 8-px box then covers [E−5, E+3), so **3 of 8 columns (37.5%) are over the void**. Because the visible sprite is wider than the box, about 45–50% of the visible body already looks unsupported. She keeps standing until X = E + 3 (**7 of 8 columns, 87.5%, over the void**). The **teeter band** is therefore ~5 px, or ~60% of the box width. This result depends on Monocle's edge-exclusive collision, which I inferred and could not read.
- The 2 px of non-hurtable feet and the 8-px box narrower than the 10–12 px sprite help both sides: spikes and walls are forgiving, and the player can stand visibly "on the lip" of a ledge, with the teeter pose telling them so.

### Gaps
- PlayerSprite.cs (the animation-ID strings such as the literal value of `PlayerSprite.FrontEdge`) and Monocle's collision code are not public, so the exact pixel threshold relies on the inference above.

## Q4. Celeste animation: frame counts, timing and animation-selection rules

### Takeaway
I could not get Celeste's `Sprites.xml` frame delays or frame counts from a reachable public source; it is game content and the main rip site blocked automated access. Player.cs does give exact **animation-selection rules** and some frame-index clues. Run animations have footsteps on frames 0 and 6, which suggests ~12-frame cycles. Push has events on frames 8 and 15, so it has at least 16 frames.

### Cited Findings
- [code] Selection rules on the ground — [L1243–1300](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1243-L1300):
  - push: moving into a wall.
  - idle / idleCarry / edge / edgeBack / lookUp: |vx| ≤ 25 px/s with no input.
  - skid: input opposite to motion and |vx| > MaxRun.
  - flip: input opposite to motion, below MaxRun.
  - runWind: running into wind.
  - runSlow: |vx| < 45 px/s (MaxRun × 0.5); otherwise runFast.
- [code] Selection rules in the air — [L1300–1331](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1300-L1331):
  - wallSlide.
  - Rising: jumpFast if |vx| > MaxRun (latched as `fastJump`), else jumpSlow.
  - Falling: fallFast if vy ≥ MaxFall (160) or after a fast jump, else fallSlow.
- [code] Frame-indexed events — [L363–392](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L363-L392):
  - Footstep SFX on frames 0 and 6 of runSlow, runFast, runCarry, walk and runWind; frame 6 of runStumble; frame 4 of flip.
  - Hand-hold SFX on frame 5 of climbUp/climbDown.
  - Dust bursts on frames 8 and 15 of push.
- [code] Idle variants: after 3 s idle, each time the idle loop ends there is a 20% chance to play a variant. Weights in cold areas are idleA 5 / idleB 3 / idleC 1; in warm areas idleA 5 / idleB 3 — [L203–205](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L203-L205), [L400–415](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L400-L415). Sprite playback rate is 0.5 in space levels, otherwise 1 — [L1334–1340](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1334-L1340).
- [code] Code-driven squash and stretch (not drawn frames):
  - Jump: (0.6, 1.4).
  - Landing: scale lerps toward (1.6, 0.4) in proportion to fall speed / 240 — [L2554–2559](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2554-L2559).
  - Duck: (1.4, 0.6). Un-duck: (0.8, 1.2).
  - Recovery at 1.75 scale-units/s.
- [dev] The developers say the animation code should have been more data-driven: "having `if frame == whatever` inside the player class is ugly" — [Readme.md](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Readme.md).
- [community] Sprite data format: an itch.io thread says the game's sprite files are custom run-length-encoded bitmap data, not standard images; per that thread, fan conversion scripts are pinned in the speedrunning Discord. A Sprites.xml `<Anim id=… delay="0.1" frames="2-7">` syntax example (not vanilla player data) is in the [SkinModHelper guide](https://github.com/AAA1459/SkinModHelper/blob/release/docs/guide/README.md).
- [secondary] One blog states Madeline's run cycle has 4 frames ([sprite-ai.art, FR](https://www.sprite-ai.art/fr/blog/pixel-art-animation), search summary only). This conflicts with the code: a footstep event on frame index 6 needs at least 7 frames. I treat that claim as unreliable.

### Inferences
- Footsteps on frames 0 and 6 point to a 12-frame run cycle (two steps per cycle, evenly spaced). That is a strong inference, not a count.
- For the comando at 12 fps: Celeste switches clips by velocity thresholds (25 px/s for idle, 0.5 × MaxRun for slow/fast run, MaxRun for fast jump, MaxFall for fast fall). It relies on code-driven squash instead of drawn anticipation frames. Both carry over directly to a low-frame-rate HD sprite.

### Gaps
- Exact per-animation frame counts and `delay` values (idle, runSlow/runFast, jumpSlow/fallSlow, edge, edgeBack) are unavailable. The Spriters Resource page ([Madeline](https://www.spriters-resource.com/pc_computer/celeste/asset/242410/)) returned a bot-protection challenge, which I did not bypass. A team member could open it in a browser.

## Q5. Developer statements: Maddy Thorson's forgiveness thread/article, Noel Berry / Pedro Medeiros

### Takeaway
Maddy Thorson's March 2020 thread, later republished as "Celeste & Forgiveness", lists 10 assists. Only two come with numbers: wall jump from 2 px away, and super wall jump from about 5 px away. The article explicitly says these techniques weren't invented by Celeste. Noel Berry and Maddy's joint readme gives code-structure statements, but no tuning numbers.

### Cited Findings
- [dev] The ten items: (1) coyote time; (2) jump buffering ("press and hold … a short time before landing", jump fires on the landing frame); (3) halved-gravity jump peak while holding jump, "more time to adjust for landing"; (4) jump corner correction; (5) dash corner correction; (6) semi-solid popping when dashing sideways through one-way platforms; (7) lift momentum storage that lasts "a few frames" after the platform stops; (8) wall jump from 2 px away ("a quarter of a tile" at 320×180); (9) super wall jump from ~5 px away ("more than half a tile"); (10) stamina refund on straight-up wall jumps. The thesis is that they all widen timing or positioning windows so the game is fudged in the player's favour — [Celeste & Forgiveness](https://maddymakesgames.com/articles/celeste_and_forgiveness/); thread mirror at [threadreaderapp](https://threadreaderapp.com/thread/1238338574220546049.html).
- [dev] "I don't think we invented any of these" — quoted in [Gigazine, 2020-03-17](https://gigazine.net/gsc_news/en/20200317-celeste-action-feel-things).
- (own calculation) Thread date: tweet ID 1238338574220546049 decodes (Twitter snowflake: (id >> 22) + 1288834974657 ms) to **2020-03-13 05:38 UTC**. Coverage appeared on 2020-03-17 ([Gigazine](https://gigazine.net/gsc_news/en/20200317-celeste-action-feel-things)).
- [code vs dev] Item 8 matches `WallJumpCheckDist = 3` (a 3-px probe accepts a 2-px gap). Item 7 matches the community value "liftboost … still applied for 10 frames after Madeline stops being in contact" ([Tech §1.10](https://celeste.ink/wiki/Tech)).
- [dev] Noel and Maddy's readme: two programmers; one big Player class kept "sequential for maintainability" because "the player behavior code needs to be very tightly ordered and tuned"; physics "very similar to TowerFall's" — [Readme.md](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Readme.md).

### Inferences
- None of the 10 assists need visible animation, except that the teeter pose (Q3) and code-driven squash support the reading of the generous windows.

### Gaps
- I found no Pedro Medeiros statement about Madeline's movement or sprite size. Search returned only a podcast listing ([AWN](https://awn.com/tag/careers-animation)).
- GMTK's "Why Does Celeste Feel So Good to Play?": I could not reach a transcript (the [Amara page](https://amara.org/v/C3BEJ/) needs a login), so I report no numbers from it.

## Q6. Jump-math literature: parametrizing by height and time instead of raw gravity

### Takeaway
The standard relations, credited to Kyle Pittman's GDC 2016 talk, are **v0 = 2h/t_h** and **g = 2h/t_h²**. With horizontal speed v_x and the horizontal distance to apex x_h, they become **v0 = 2h·v_x/x_h** and **g = 2h·v_x²/x_h²**. A separate **fall gravity g_f = 2h/t_f²** comes from a chosen descent time. GMTK's Platformer Toolkit, GDQuest and Dawnosaur's Unity controller all use the height/time-to-apex form in code.

### Cited Findings
- [primary listing] Kyle Pittman (Minor Key Games), "Math for Game Programmers: Building a Better Jump", GDC 2016. The overview says it builds jump arcs from designer-friendly inputs such as height and distance, covers integration methods, and extends to variable height based on input and faster falling after the apex — [GDC Vault](https://gdcvault.com/play/1023148/Math-for-Game-Programmers-Building).
- [secondary] A GDC 2016 recap says Pittman argues gravity should be "determined by the constraints of the level design". It gives v_y = 2h·v_x/x_h and writes g as "−2h/t_h". The missing square is presumably a transcription slip; dimensionally g = 2h/t_h². The recap also says he used different gravity for ascent and descent — [JCCC blog, GDC16 Day 1](https://blogs.jccc.edu/dpatter/2016/03/15/gdc16-day-1/) (403 on fetch; search summary only).
- [secondary/tutorial] GDQuest: `jump_velocity = (-2*height)/time_to_peak`, `jump_gravity = (2*height)/time_to_peak²`, `fall_gravity = (2*height)/time_to_descent²`. Example values are height 50, peak 0.4 s, descent 0.25 s — [GDQuest, Kinematic jump formulas](https://www.gdquest.com/library/kinematic_jump_formulas/). (own calculation) That example's fall/rise gravity ratio is (0.4/0.25)² = **2.56×**.
- [secondary/dev-tool] GMTK Platformer Toolkit (Mark Brown, MIT-licensed code; "Behind the Code" devlog dated Jun 22 2022):
  - Gravity from height and time: `newGravity.y = (-2 * jumpHeight) / (timeToJumpApex * timeToJumpApex)`. Jump speed: `Mathf.Sqrt(-2f * gravity * jumpHeight)`.
  - Gravity multiplier = 1 at rest; `downwardMovementMultiplier` when vy < 0; `jumpCutoff` multiplier while rising without the button held (variable jump by **gravity switch**).
  - Coyote time "usually something like 0.2"; a jump-buffer counter keeps the jump request alive for `jumpBuffer` seconds.
  - Source: [Behind The Code](https://gmtk.itch.io/platformer-toolkit/devlog/395523/behind-the-code). The toolkit page says it exposes "over 30 variables", including max speed, jump height, squash and stretch and coyote time ([itch.io page](https://gmtk.itch.io/platformer-toolkit)).
- [community code] Dawnosaur's open Unity controller computes `gravityStrength = -(2*jumpHeight)/(jumpTimeToApex²)` and `jumpForce = |g|*jumpTimeToApex`. It exposes fallGravityMult, jumpCutGravityMult, jumpHangGravityMult, jumpHangTimeThreshold, coyoteTime and jumpInputBufferTime — [PlayerData.cs](https://github.com/DawnosaurDev/platformer-movement/blob/main/Platformer%20Demo%20-%20Unity%20Project/Assets/Scripts/PlayerData.cs).
- (own calculation) The team's prototype in this form: h = 640²/(2·1900) = 107.8 px, t_h = 640/1900 = 0.337 s, so 2h/t_h = 640 px/s and 2h/t_h² = 1900 px/s². Example re-parametrizations for the comando (h in px, times in s):
  - h 108, t_up 0.337, t_down 0.337 → v0 641, g_up 1902, g_down 1902 (current, symmetric).
  - h 128 (1.0 H_vis), t_up 0.35, t_down 0.25 → v0 731, g_up 2090, g_down 4096 (1.96×), airtime 0.60 s.
  - h 128, t_up 0.40, t_down 0.28 → v0 640, g_up 1600, g_down 3265 (2.04×), airtime 0.68 s.
  - h 160 (1.25 H_vis), t_up 0.40, t_down 0.30 → v0 800, g_up 2000, g_down 3556 (1.78×), airtime 0.70 s.

### Inferences
- Celeste does **not** follow the textbook form. It is "launch speed + hold-to-sustain + half gravity near apex + low terminal speed". To mimic it with height and time controls, set h_full, t_sustain (≈0.2 s), the apex half-gravity threshold, and a terminal velocity, rather than h and t only.

### Gaps
- The original Pittman slides (mathforgameprogrammers.com PDF) failed on TLS. I could not check his exact recommendation on velocity cut vs gravity switch, or his integration-method advice beyond the Vault overview.

## Q7. Typical values in shipped games and references: coyote, buffer, fall gravity, apex hang, terminal velocity, air control

### Takeaway
Typical windows are **coyote ≈ 0.08–0.2 s** and **buffer ≈ 0.067–0.2 s**. Celeste sits at the tight end: 5 coyote frames and about 4 buffer frames. Fall gravity multipliers in reference code range from **1.5× to 2.5×**. Celeste is the exception at 1.0×, because its asymmetry comes from the sustain and the terminal velocity. Apex hang ×0.5 is the Celeste reference. Terminal velocity is typically ~0.7–1.5× launch speed. Air acceleration is 0.65× ground in Celeste.

### Cited Findings
- Coyote time:
  - Celeste: 0.1 s timer [code](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L48) = 5 frames [community](https://celeste.ink/wiki/Tech).
  - Neon White: 0.3 s [community, DGMI wiki](https://dgmiwiki.wpi.edu/mechanic/coyote_time).
  - GMTK: "usually something like 0.2" [Behind the Code](https://gmtk.itch.io/platformer-toolkit/devlog/395523/behind-the-code).
  - Generic guidance: 0.05–0.15 s [secondary, Bugnet blog](https://bugnet.io/blog/coyote-time-and-input-buffering-explained) (search summary).
  - Dawnosaur presets: Celeste-style 0.1, Hollow-Knight-style 0.2, Super-Meat-Boy-style 0.2 [community, fan approximations](https://github.com/DawnosaurDev/platformer-movement/tree/main/Platformer%20Demo%20-%20Unity%20Project/Assets/Scriptable%20Objects/Player%20Types).
- Jump buffer:
  - Celeste: 4 frames [community](https://celeste.ink/wiki/Tech), only while held [Everest code](https://github.com/EverestAPI/Everest/blob/dev/Celeste.Mod.mm/Patches/Monocle/VirtualButton.cs).
  - GameMaker official blog example: `buffer_max = 4` frames [GameMaker, Flynn: Advanced Jump Mechanics](https://gamemaker.io/en/blog/flynn-advanced-jump-mechanics).
  - Dawnosaur presets: 0.1 / 0.2 / 0.2 s [community].
  - Generic: 0.05–0.15 s [secondary, Bugnet].
- Fall gravity multiplier:
  - Celeste: 1.0 [code].
  - Common Unity "BetterJump" pattern: FallMultiplier 2.5, LowJumpMultiplier 2 [secondary, Unity Discussions](https://discussions.unity.com/t/help-with-jumping/828326) (search summary).
  - Dawnosaur presets: 1.5 (Celeste-style), 2 (HK), 2 (SMB) [community].
  - GDQuest example: 2.56× (own calculation from [GDQuest](https://www.gdquest.com/library/kinematic_jump_formulas/)).
  - GMTK exposes `downwardMovementMultiplier` with no default published [GMTK].
- Apex hang:
  - Celeste: ×0.5 gravity while |vy| < 40 px/s **and** jump held [code](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2952). That threshold is 38% of launch speed, or 0.044 s × g (own calculation).
  - Dawnosaur Celeste-style: jumpHangGravityMult 0.5, threshold 1 unit/s on a 23.3 unit/s launch (≈4%, own calculation), plus 1.1× acceleration and 1.3× max speed during the hang [community]. Its HK and SMB presets have no hang.
- Variable jump method:
  - Celeste: hold-to-sustain launch speed for ≤0.2 s, no cut [code].
  - GMTK: gravity multiplier `jumpCutoff` on release [GMTK].
  - Unity BetterJump: lowJumpMultiplier 2 [secondary].
  - Dawnosaur: jumpCutGravityMult 2 (Celeste-style), 3.5 (HK), 4 (SMB) [community].
  - Generic knob tables suggest a velocity cut ×0.4–0.5 on release [secondary, search summary from a tooling site, low reliability].
- Terminal velocity:
  - Celeste: MaxFall 160 = 1.52× JumpSpeed, FastMaxFall 2.29× [code + own calculation].
  - Dawnosaur presets maxFall/v0 (own calculation from preset jumpHeight and jumpTimeToApex): Celeste-style 25/23.3 = 1.07; HK 18/26 = 0.69; SMB 20/20 = 1.0.
- Air control:
  - Celeste AirMult 0.65 on both acceleration and friction [code](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L33).
  - Dawnosaur: accelInAir 0.65 (Celeste-style), 1.0 (HK), 1.0 accel / 0 decel (SMB) [community].
  - GMTK uses separate maxAirAcceleration/deceleration/turn speeds [GMTK].
- [community] The Dawnosaur Celeste-style preset sets jumpHeight 3.5 units with 0.3 s to apex. If 1 unit = one 8-px tile, that is 28 px, which matches my derived 28 px (Q2) (own calculation; the unit mapping is my assumption).

### Inferences
- A "safe default" cluster for a precision-leaning action platformer is coyote 0.1 s, buffer 0.1 s, fall gravity 1.5–2×, apex hang ×0.5, terminal velocity ≈1–1.5× launch speed, air acceleration ≈0.65× ground. Celeste is at the tight, precise end for coyote and buffer. Casual or heavy characters often go up to 0.2 s.

### Gaps
- I did not find primary-source coyote or buffer values for classic run-and-guns (Contra, Metal Slug, Mega Man X) in this pass. The Dawnosaur values are fan recreations, not data from the original games.

## Q8. Ledge teetering in other platformers (Sonic, Kirby, Mega Man X) and how much body can hang over an edge

### Takeaway
Sonic (Sonic Physics Guide) balances only when **ground speed = 0**, one of his two ground sensors (at ±9 px) finds floor, and an extra centre sensor finds none. In other words, his centre X is past the edge. Sonic 2 onward adds a second pose about 6 px further out. He keeps standing until both sensors miss, so his centre can be about 9 px past the edge (≈95% of his 19-px floor span over the void). Celeste's equivalent band runs from ≈37% to 87.5% of the box over the void (Q3).

### Cited Findings
- [community, SPG] Sizes: Width Radius 9 (19 px wide), Height Radius 19 (39 px tall), Push Radius 10, Hitbox Width Radius 8 (17 px wide), Hitbox Height Radius = Height Radius − 3 — [SPG Characters (mirror)](https://github.com/trentbrew/sonic-physics-guide/blob/main/docs/03-characters.md); canonical at [info.sonicretro.org](https://info.sonicretro.org/Sonic_Physics_Guide). Ground sensors A/B sit at (±Width Radius, +Height Radius) — [SPG Slope Collision (mirror)](https://github.com/trentbrew/sonic-physics-guide/blob/main/docs/06-slope-collision.md).
- [community, SPG] Edge balancing: "When Ground Speed is 0, and only a single Block was found, an extra sensor checks at the Player's X and Y Position + Height Radius … If none's found then the balancing animation plays. In Sonic 2 onwards, if the Player is 6px away from a ledge, an alternate animation will play." Balancing also blocks ducking, looking up and spindash (S3K allows duck/spindash on terrain) — [SPG Slope Collision (mirror)](https://github.com/trentbrew/sonic-physics-guide/blob/main/docs/06-slope-collision.md).
- [community, SPG] Balance animation timing:
  - Sonic 1: 32 frames per subimage.
  - Sonic 2: forward 10, backward 20, "last" (closer to the edge) 4 frames per subimage.
  - Sonic 3: two balances, 8 and 6 frames per subimage.
  - Source: [SPG Animations (mirror)](https://github.com/trentbrew/sonic-physics-guide/blob/main/docs/21-animations.md).
- [secondary] Sonic 2 and Sonic CD use a different balance when the edge is behind him. The same article warns that triggering as soon as one sensor loses ground makes him balance too early — [sudonull overview](https://sudonull.com/post/91120-An-overview-of-physics-in-Sonic-games-Part-1-solid-tiles) (search summary).
- [community, SPG] Many platform objects use their own Width Radius instead of the combined radius, so "the Player falling off earlier than expected" — [SPG Solid Objects (mirror)](https://github.com/trentbrew/sonic-physics-guide/blob/main/docs/08-solid-objects.md).

### Inferences
- (own calculation) Sonic falls when X > edge + 9 (both A and B miss). At X = edge + 9, 18 of the 19 sensor-span pixels are over the void. Balance starts at X ≥ edge (≥50%), and the second pose (S2+) comes ≈6 px further (≈80% over).
- A reusable rule for the comando (44-px box):
  - Front-teeter when a floor probe slightly ahead of the centre finds nothing. Celeste puts it at centre + 1/8 of the width (≈ +5–6 px); Sonic at the centre itself.
  - Optionally a second, "about to fall" pose ≈30% of the width further out (Sonic 2's 6/19).
  - A back-teeter when the gap is behind.
  - Keep standing while any part of the box overlaps the floor.
  - Only trigger when idle (Celeste: |vx| ≤ 25 px/s and no input; Sonic: ground speed 0).

### Gaps
- Kirby and Mega Man X: I found no documentation of a teeter animation or its trigger in this pass, so I can make no claim. The canonical Sonic Retro site blocked automated access (bot protection), so I used the GFDL markdown mirror.

## Q9. Hitbox narrower and shorter than the sprite: practice and rationale

### Takeaway
Both reference games use collision boxes smaller than the drawn character. Celeste: 8×11 box (9-px hurtbox) for a ~10–12 × 16 px sprite. Sonic: 19-px terrain width and a 17-px object hitbox width, with the object hitbox 6 px shorter than the terrain box. The stated rationale is widening positional windows in the player's favour.

### Cited Findings
- [code] Celeste box 8×11, hurtbox 8×9 (feet excluded), duck box 8×6 — [L263–266](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L263-L266). Visible ≈16 px tall, 10–12 px wide (own measurement, Q3).
- [community, SPG] Sonic has separate terrain sensors (width radius 9, push radius 10) and a damage/object hitbox (width radius 8, height radius − 3) — [SPG Characters](https://github.com/trentbrew/sonic-physics-guide/blob/main/docs/03-characters.md).
- [dev] Rationale: "widening timing or positioning windows, so that everything is fudged a tiny bit in the player's favor" — [Celeste & Forgiveness](https://maddymakesgames.com/articles/celeste_and_forgiveness/); thread version via [threadreaderapp](https://threadreaderapp.com/thread/1238338574220546049.html).
- [community] Madeline's crouched hurtbox is 4 px vs 9 standing — [Celeste Wiki, Tech §2.8](https://celeste.ink/wiki/Tech) (matches the code).

### Inferences
- The comando's box (44×108 vs 128 px tall) covers 84% of visible height. That is generous to collision compared with Celeste's 69% (box) and 56% (hurtbox).
- A heavy two-handed gun makes the sprite much wider than the body. Keeping the 44-px box on the torso and legs, with the gun outside it, follows the same practice. It also makes the teeter pose more important, because the drawn silhouette (gun barrel) will often hang over edges while the box is still supported.
- Splitting **terrain box** and **hurtbox**, as both games do, lets the team keep a stable terrain box while shrinking the damage box (for example, excluding the feet and the gun).

### Gaps
- I found no published "readability" rationale from these developers beyond forgiveness. I also have no measured visible width for Sonic.

## Q10. What the literature says about the comando prototype's choices

### Takeaway
The prototype's ground-to-air acceleration ratio (0.65) and its time to top speed (≈0.09 s) are almost exactly Celeste's. Its airtime (0.674 s) matches Celeste's full jump (0.664 s). It departs from the references in four ways: (a) symmetric gravity without the apex hang, sustain or terminal velocity that make Celeste's symmetric gravity work; (b) no coyote time; (c) no jump buffer; (d) much lower jump and run relative to body size. Its velocity-clamp variable jump is a recognized method and gives a short-hop ratio (≈26% of full height) close to Celeste's (≈28%).

### Cited Findings
Each item below gives the prototype value, then the comparison and what the literature says. Prototype values are from the team spec; comparisons are own calculations against Q2 and Q7.

- **Run 230 px/s**
  - 3.83 px/frame at 60 fps, 19.2 px per 12-fps animation frame; 1.80 H_vis/s and 2.13 H_hb/s.
  - Celeste: 5.6 H_vis/s and 8.2 H_hb/s.
  - The comando moves about 3× slower relative to body height than Madeline.
- **Ground acceleration 2600 px/s²**
  - 0→230 in 0.088 s (5.3 frames).
  - Celeste: 0.09 s (5.4 frames → 6) ([code](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L31)). Essentially identical responsiveness.
  - Celeste also brakes and turns at this same rate (no separate decel), worth checking against the prototype's braking.
- **Air acceleration 1700 px/s²**
  - Ratio 1700/2600 = **0.654**, which is Celeste's `AirMult = .65` ([code](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L33)). 0→230 in 0.135 s (8.1 frames) vs Celeste 0.138 s.
- **Gravity 1900 px/s², the same up and down**
  - Pittman (Vault overview), GDQuest, GMTK and Unity BetterJump all add a stronger fall gravity, about 1.5–2.5× (Q6, Q7).
  - Celeste also keeps one gravity, but adds:
    - a 0.2 s sustain (linear rise), so the rise outlasts the fall: 0.36 s up vs 0.30 s down;
    - ×0.5 apex hang;
    - a hard terminal velocity of 1.52× launch speed.
  - The prototype has none of these, so its arc is a pure symmetric parabola: 0.337 s up, 0.337 s down.
- **Jump velocity 640 px/s, apex ≈108 px, airtime ≈0.67 s**
  - Apex = 0.84 H_vis = 1.0 H_hb. Celeste: 1.75 H_vis = 2.5 H_hb.
  - Airtime: 40.4 frames at 60 fps (≈8 animation frames at 12 fps) vs Celeste 38–40 frames.
  - Running jump covers 230 × 0.674 = 155 px = 1.2 H_vis. Celeste: 3.9 H_vis.
  - Expressed by height and time: h = 108, t_h = 0.337 (Q6).
- **Variable jump: clamp vy to 260 on release**
  - This is a velocity-cut method. Cut ratio 260/640 = 0.41, inside the ×0.4–0.5 range in generic knob tables (low-reliability source).
  - Minimum hop (release on the first 60-fps frame): ≈10.5 px + 260²/3800 = 17.8 px → ≈28 px = **0.26 of full**, airtime ≈0.33 s. Celeste's tap/full ratio is 7.9/28 = 0.28.
  - Alternatives in the literature: a gravity switch on release (GMTK `jumpCutoff`, BetterJump lowJumpMultiplier 2, Dawnosaur jumpCutGravityMult 2–4) or Celeste's hold-to-sustain, which has no discontinuity on release.
- **No coyote time**
  - Every reference above uses one: Celeste 0.1 s (5 frames), up to 0.2–0.3 s in other games and tools.
  - Maddy lists it first among Celeste's forgiveness mechanics ([dev](https://maddymakesgames.com/articles/celeste_and_forgiveness/)).
- **No jump buffer**
  - Every reference above uses one: Celeste ≈4 frames (held), GameMaker example 4 frames, Dawnosaur presets 0.1–0.2 s.
- **No terminal velocity stated**
  - Celeste caps at 1.52× launch speed (2.29× on fast fall). Dawnosaur presets sit at 0.7–1.07×. The prototype's landing speed from a full jump is 640 px/s (1.0×), but long drops are uncapped.
- **No apex hang**
  - Celeste: ×0.5 while |vy| < 40 px/s and held. Scaled to the comando, the equivalent threshold is ≈84 px/s if matched by time (40/900 s × 1900), or ≈244 px/s if matched by fraction of launch speed (0.38 × 640). The time-matched value keeps the same ≈0.09 s of extra hang.
- **No corner correction**
  - Celeste: 4 px = 50% of the 8-px box width (half a tile).
  - Scaled to a 44-px box that is up to 22 px. A conservative start would be 25–35% (11–15 px). That last figure is my inference, not from a source.

### Inferences
- If the team wants the comando to stay "heavy" (low jump, slow run) but feel fair:
  - The cheapest wins from the literature are coyote time (~0.1 s), a buffer (~0.1 s), a terminal velocity, and either fall gravity ~1.5–2× or Celeste's apex hang.
  - Upward corner correction matters for a 108-px-tall box under platforms.
  - None of these change the drawn animation count. At 12 fps, a 0.674 s jump is about 8 drawn frames, so rise, apex and fall clips need clear velocity thresholds (Celeste's jumpSlow/fallSlow/fallFast rules, Q4).

### Gaps
- No source compares run-and-gun genre norms (Contra, Metal Slug, Gunstar) for jump height or run speed per body height. Other researchers may cover this.

## Q11. Summary tables

### Takeaway
Table (a) converts Celeste's code constants into px/frame, px/s, body heights and frames. Table (b) gathers the ranges the references give for the forgiveness and arc-shaping knobs, with Celeste and the comando prototype side by side.

### Cited Findings
**(a) Celeste values (60 fps; H_hb = 11 px hitbox height; H_vis ≈ 16 px visible height)**. Source for every constant: [Player.cs](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs) at the cited lines. Conversions are own calculations; frame windows come from the [Celeste Wiki Tech page](https://celeste.ink/wiki/Tech) where noted.

| Quantity (code name, line) | Code value | px/frame | Normalized | Frames / seconds | Tag |
|---|---|---|---|---|---|
| MaxRun (L30) | 90 px/s | 1.5 | 8.2 H_hb/s; 5.6 H_vis/s | — | code + calc |
| RunAccel (L31), ground accel = decel = turn | 1000 px/s² | +16.7 px/s per frame | — | 0→max 6 f (0.09 s); turn 11 f | code + calc |
| AirMult (L33) | 0.65 → 650 px/s² | +10.8 px/s per frame | — | 0→max 9 f (0.138 s); air turn 17 f | code + calc |
| RunReduce (L32), over-cap decay | 400 px/s² (260 in air) | — | — | +40 boost bleeds off in ≈9 f | code + calc |
| Gravity (L24) | 900 px/s² | 0.25 px/f² | — | — | code |
| HalfGravThreshold (L25) | 40 px/s, ×0.5 g while held | 0.67 | 0.38 × JumpSpeed | hang zone ≈0.18 s total | code + calc |
| MaxFall (L23) | 160 px/s | 2.67 | 14.5 H_hb/s; 10 H_vis/s; 1.52 × JumpSpeed | — | code + calc |
| FastMaxFall (L27) / FastMaxAccel (L28) | 240 px/s / 300 px/s² | 4.0 | 2.29 × JumpSpeed | — | code + calc |
| JumpSpeed (L49) | 105 px/s up | 1.75 | 9.5 H_hb/s | — | code |
| JumpHBoost (L50) | +40 px/s | 0.67 | 0.44 × MaxRun | — | code |
| VarJumpTime (L51), sustain at launch speed | 0.2 s | — | — | 11–12 f after press | code + calc |
| CeilingVarJumpGrace (L52) | 0.05 s | — | — | 3 f | code |
| Full jump height (held) | — | — | ≈28 px = 2.5 H_hb = 1.75 H_vis = 3.5 tiles | apex ≈0.36 s (≈22 f); airtime ≈0.66 s (38–40 f) | own calc / sim (27–29 px) |
| Minimum (tap) jump | — | — | ≈7–8 px = 0.7 H_hb = 0.5 H_vis (≈28% of full) | airtime ≈0.23–0.27 s (14–16 f) | own calc / sim |
| Running-jump horizontal reach | — | — | ≈63 px = 5.7 H_hb = 3.9 H_vis | — | own calc |
| JumpGraceTime (L48), coyote | 0.1 s | — | — | 5 f (wiki); 5–6 f (calc) | code + community |
| Jump buffer (Input, not public) | (0.08 s, unverified) | — | — | 4 f (wiki; older revisions 5); only while held | community + Everest code |
| UpwardCornerCorrection (L53) | 4 px sideways + 1 up | — | 50% of box width; 0.36 H_hb | — | code |
| DashCornerCorrection (L82) / DashVFloorSnapDist (L83) | 4 px / 3 px | — | — | — | code |
| WallJumpCheckDist (L56) | 3 px probe (2 px gap) | — | 25–37% of box width | — | code + dev |
| WallJumpHSpeed (L58) / WallJumpForceTime (L57) | 130 px/s / 0.16 s | 2.17 | — | ≈10 f forced direction | code + calc |
| ClimbHopY / ClimbHopX / ClimbHopForceTime (L115–117) | −120 px/s / 100 px/s / 0.2 s | 2.0 / 1.67 | — | 12 f | code + calc |
| Hitbox / hurtbox (L263, L265) | 8×11 / 8×9 (feet excluded) | — | box ≈69% of visible height | — | code + own measurement |
| Duck hitbox / hurtbox (L264, L266); DuckFriction (L40) | 8×6 / 8×4; 500 px/s² | — | 55% of standing box | — | code |
| DuckCorrectCheck / Slide (L41–42) | 4 px / 50 px/s | 0.83 | — | — | code |
| Edge (teeter) trigger (L1246–1262) | idle (\|vx\| ≤ 25 px/s, no input) and no Solid at centre ±1 px and ±4 px, 2 px below feet | — | teeter from ≈3/8 to 7/8 of box over void | — | code + own inference |

**(b) Recommended ranges from the references**

| Knob | Celeste | Other references | Suggested range (my synthesis) | Comando prototype now |
|---|---|---|---|---|
| Coyote time | 0.1 s timer = 5 f @60 ([code](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L48), [wiki](https://celeste.ink/wiki/Tech)) | 0.2 s "usual" ([GMTK](https://gmtk.itch.io/platformer-toolkit/devlog/395523/behind-the-code)); 0.1–0.2 s ([Dawnosaur presets](https://github.com/DawnosaurDev/platformer-movement)); 0.3 s Neon White ([DGMI](https://dgmiwiki.wpi.edu/mechanic/coyote_time)); 0.05–0.15 s generic ([Bugnet](https://bugnet.io/blog/coyote-time-and-input-buffering-explained)) | 0.08–0.15 s (5–9 f); up to 0.2 s for a forgiving or heavy character | none |
| Jump buffer | ≈4 f (≈0.067–0.08 s), only while held ([wiki](https://celeste.ink/wiki/Tech), [Everest](https://github.com/EverestAPI/Everest/blob/dev/Celeste.Mod.mm/Patches/Monocle/VirtualButton.cs)) | 4 f ([GameMaker](https://gamemaker.io/en/blog/flynn-advanced-jump-mechanics)); 0.1–0.2 s (Dawnosaur); 0.05–0.15 s generic (Bugnet) | 0.067–0.15 s (4–9 f) | none |
| Fall gravity multiplier | 1.0, with sustain + apex hang + terminal velocity making the fall shorter than the rise ([code](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2952)) | 2.5 ([Unity BetterJump](https://discussions.unity.com/t/help-with-jumping/828326)); 1.5–2 (Dawnosaur); 2.56 implied by [GDQuest](https://www.gdquest.com/library/kinematic_jump_formulas/) example; GMTK `downwardMovementMultiplier` | 1.5–2.5×, or 1.0 only if you copy Celeste's sustain, hang and cap | 1.0 (symmetric) |
| Apex hang threshold / multiplier | ×0.5 g while \|vy\| < 40 px/s and held (0.38 × v0; 0.044 s × g) ([code](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L25)) | ×0.5, threshold ≈4% of v0, plus 1.1× accel / 1.3× max speed (Dawnosaur Celeste-style); none in HK/SMB-style presets | ×0.5 for \|vy\| < g × 0.045 s (comando: ≈85 px/s) or < 0.38 × v0 (≈245 px/s) | none |
| Variable jump method | Hold-to-sustain launch speed ≤0.2 s; release just stops the sustain ([code](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L2960)) | Gravity switch on release: GMTK `jumpCutoff`, lowJumpMultiplier 2 (Unity), jumpCutGravityMult 2–4 (Dawnosaur); velocity cut ×0.4–0.5 (low-reliability knob table) | Any of the three; target tap/full height ≈0.25–0.35 (Celeste 0.28) | velocity clamp to 260 (0.41 × v0); tap/full ≈0.26 |
| Air control ratio (air accel / ground accel) | 0.65, also used for air friction and turning ([code](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L33)) | 0.65 (Dawnosaur Celeste-style); 1.0 (HK/SMB-style accel, SMB air decel 0); GMTK separate air accel/decel/turn | 0.5–1.0; 0.65 is the Celeste reference | 0.654 |
| Terminal velocity / launch speed | 1.52× (fast fall 2.29×) ([code](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L23)) | 0.69–1.07× (Dawnosaur presets, own calc) | ≈1.0–1.5× | not specified |
| Corner correction | 4 px = 50% of box width ([code](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L53)) | Listed as a core assist by [Maddy](https://maddymakesgames.com/articles/celeste_and_forgiveness/) | 25–50% of box width (comando: 11–22 px) | none |
| Teeter trigger | idle and no floor at centre +1 px and at the box edge (≈37.5% over) ([code](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs#L1246)) | Sonic: ground speed 0 and centre past edge; 2nd pose +6 px (S2+) ([SPG](https://github.com/trentbrew/sonic-physics-guide/blob/main/docs/06-slope-collision.md)) | Trigger at ≈40–50% of the box over the void; optional 2nd pose at ≈80% | — |

### Inferences
- The "suggested range" column is my synthesis of the cited references, not a published standard.

### Gaps
- GMTK Platformer Toolkit preset values (if any exist) and default slider values were not published on the pages I could reach.
