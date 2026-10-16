# Movement, jump and shooting baselines: Super Mario Bros. (NES, 1985) and Mega Man / Rockman (NES, 1987)

Source-quality legend used throughout:
- **[DISASM]** = read directly from an annotated disassembly. SMB: doppelganger's `smbdis.asm` ([gist](https://gist.github.com/1wErt3r/4048722)); labels such as `JumpMForceData` are quoted so the reader can find them. Mega Man 1: Bisqwit's annotated "MEGAMAN 1 NES ROM TECH DOC" ([maincode.txt](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt), index page [here](https://bisqwit.iki.fi/jutut/megamansource/)); quoted by CPU address, e.g. `$961E`.
- **[TAS]** = TASVideos technical pages and submission notes (ROM-analysis based).
- **[RAM]** = Data Crystal RAM maps (community wiki, sometimes inconsistent).
- **[WIKI/FORUM]** = community wikis, blogs and forums.
- **(own calculation)**, **(own simulation)**, **(own measurement)**, **(own count)**, **(own reading of code)** = my own work. Inputs are shown. The simulations are small Python transcriptions of the quoted 6502 routines (`ImposeGravity`, `JumpSwimSub`, `ImposeFriction`, `MoveObjectHorizontally` for SMB; `$95BD–$9628` and `$9C59–$9C8C` for MM1).

Unit conventions:
- SMB horizontal speed (`Player_X_Speed`, $57) is in 1/16 px per frame ("16 subpixels make up 1 pixel", per [TASVideos SMB](https://tasvideos.org/GameResources/NES/SuperMarioBros)). An extra fractional byte (`Player_X_MoveForce`) holds 1/256 of a subpixel. SMB vertical speed is whole px/frame plus a 1/256 fraction.
- Mega Man speeds are 8.8 fixed point (`01.60` hex = 1 + 0x60/256 = 1.375 px/frame). Positive Y speed means up ([TASVideos Rockman Data](https://tasvideos.org/GameResources/NES/Rockman/Data)).
- 1 frame = 1/60.0988 s.
- Normalization heights: **small Mario 16 px**, **Super Mario 32 px**, **Mega Man 24 px**. Mega Man's height is my measurement of the standing sprite, 21×24 px. Hitbox heights differ and are given in the hitbox section.

Unless stated otherwise, "Mega Man" means Mega Man 1 (Rockman, 1987).

---

## Native resolution and logic rate

### Takeaway
Both games render 256×240 px. About 256×224 is visible on an NTSC TV. Both run their game logic once per frame at 60.0988 Hz NTSC, so every per-frame value below converts to per-second by ×60.0988.

### Cited Findings
- "The NES PPU always generates a 256x240 pixel picture." Actual TVs show about 224 lines, hence the commonly reported 256×224. Pixel aspect ratio on a 4:3 TV is 8:7 (≈1.143:1). — [NESdev wiki: Overscan](https://www.nesdev.org/wiki/Overscan)
- NTSC vertical scan rate is 60.0988 Hz, and the CPU runs at 1.789773 MHz. — [NESdev wiki: Cycle reference chart](https://www.nesdev.org/wiki/Cycle_reference_chart)
- SMB runs all game logic from the NMI once per frame. Frame timers (including `PlayerAnimTimer` $0781) are decremented every frame before the game engine runs (`DecTimers` loop). — [DISASM smbdis.asm](https://gist.github.com/1wErt3r/4048722)
- In both games a block / metatile is 16×16 px and the NES screen is 256 px wide. — [TASVideos Rockman](https://tasvideos.org/GameResources/NES/Rockman); SMB walls are "checked at block boundaries, which occur every 16 pixels." — [TASVideos SMB](https://tasvideos.org/GameResources/NES/SuperMarioBros)
- MM1's main loop calls `NextFrame` once per iteration, i.e. one logic step per frame. Lag frames slow movement to 1/2 or 1/3 of normal. — [DISASM Bisqwit `$913F`/`MainLoop`](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt); [TASVideos Rockman](https://tasvideos.org/GameResources/NES/Rockman)

### Inferences
- With 16-px blocks, a 16-px small Mario is 1 block tall, Super Mario is 2 blocks, and Mega Man (24 px) is 1.5 blocks.
- At 60 Hz, a 12 fps animation (the comando target) holds each drawing for 5 logic frames. That is slower than Mario's run cycle (2 frames per drawing) and similar to Mario's walk (4 frames per drawing). See the animation section.

### Gaps
- PAL timings (50 Hz) are not covered.

---

## Run/walk speed and acceleration

### Takeaway
Mario ramps up to speed and ramps down again. Walking tops out at 1.5 px/f (90 px/s) and running (B held) at 2.5 px/f (150 px/s). Top walk speed takes about 41 frames (0.68 s) from rest and top run speed about 45 frames. Releasing the stick or skidding brakes gradually, with momentum.

Mega Man is nearly instant: 1.375 px/f (82.6 px/s) on the ground and 1.3125 px/f in the air. Every fresh press starts with a 9-frame "inch" at 0.125 px/f (≈1.1 px). Releasing from full speed in MM1 gives a 13-frame slide at 0.5 px/f (≈6.5 px).

### Cited Findings
**Super Mario Bros.**
- Max-speed tables [DISASM]: `MaxRightXSpdData: .db $28, $18, $10` and `$0c` (pipe intros); `MaxLeftXSpdData: .db $d8, $e8, $f0`. Index 0 is running (B held, or the 10-frame `RunningTimer` still set), index 1 is walking, index 2 is water. — [smbdis.asm `X_Physics`/`GetXPhy`](https://gist.github.com/1wErt3r/4048722)
- "The maximum speed for walking (Left or Right without B) is ±24 (18 in hexadecimal)". "The maximum speed for running (Left or Right with B) is ±40 (28 in hexadecimal)". "Speed translates to how many subpixels/frame Mario is going". — [TASVideos submission #9971 notes](https://tasvideos.org/Forum/Posts/538365)
- "Maximum walking speed is 3/5 of maximum running speed." — [SDA Knowledge Base, Super Mario Bros](https://kb.speeddemosarchive.com/Super_Mario_Bros)
- Acceleration / friction table [DISASM]: `FrictionData: .db $e4, $98, $d0`.
  - $E4 is used when running.
  - $98 is used when walking.
  - $D0 is used when on the walking table while `RunningSpeed` is set, or speed is ≥ $21.
  - The value is added to a 1/256-subpixel fraction (`Player_X_MoveForce` $0705) that carries into `Player_X_Speed`.
  - If facing ≠ moving direction (skid / backward), the adder is doubled (`asl FrictionAdderLow / rol FrictionAdderHigh`).
  - With no L/R input on the ground, the same adder is applied toward zero (`ImposeFriction`).
  - Source: [smbdis.asm `GetXPhy2`, `ImposeFriction`](https://gist.github.com/1wErt3r/4048722)
- Skid end [DISASM]: while pressing against the motion on the ground, once `Player_XSpeedAbsolute` < $0B (0.6875 px/f), speed is zeroed and Mario's moving direction flips instantly (`ProcSkid` in `GetPlayerAnimSpeed`). — [smbdis.asm](https://gist.github.com/1wErt3r/4048722)
- RAM map labels $0702 values as "0xE4 - is running", "0x30 - skidding", "98 - normal", which matches the friction adder. The same map lists max right speed as "0x1C walking / 0x30 running", which **conflicts** with the disassembly ($18/$28) and with TASVideos (24/40). — [RAM Data Crystal SMB RAM map](https://datacrystal.tcrf.net/wiki/Super_Mario_Bros./RAM_map)
- Conversions (own calculation, ×60.0988; heights 16/32 px):
  - Walk 1.5 px/f = 90.15 px/s = 5.63 small-Mario h/s = 2.82 Super-Mario h/s.
  - Run 2.5 px/f = 150.25 px/s = 9.39 / 4.70 h/s.
  - Water cap 1.0 px/f = 60.1 px/s.
- Accelerations (own calculation; adder/4096 px/f²):
  - Walk accel $98 = 0.0371 px/f² (134 px/s²).
  - Run accel $E4 = 0.0557 px/f² (201 px/s²).
  - Release from run $D0 = 0.0508 px/f² (183 px/s²).
  - Skid ×2: $130 = 0.0742 px/f² and $1A0 = 0.1016 px/f².
- Time and distance to top speed and to stop (own simulation of `ImposeFriction` + `MoveObjectHorizontally`):

  | Situation | Frames | Distance |
  |---|---|---|
  | Rest → walk max $18 | 41 (0.68 s) | ≈30 px |
  | Rest → run max $28 | 45 (0.75 s) | ≈56 px |
  | Walk max → run max (press B) | 18 | — |
  | Release at walk max → 0 | 39 | slide ≈28 px |
  | Release at run max → 0 | 49 | slide ≈58 px |
  | Skid from walk max, then instant reversal | 11 | ≈11 px |
  | Skid from run max, then instant reversal | 18 | ≈27 px |

**Mega Man**
- "In Rockman 1 and 2, during walking, Rockman's X speed is 01.60." "In Rockman 1 and 2, during jumping/falling into some direction, Rockman's X speed is 01.50." — [TAS Rockman technical data](https://tasvideos.org/GameResources/NES/Rockman/Data)
- Mega Man "walks precisely at speed of 1.375 pix/frame". In the air "he progresses only 1.3125 pix/frame". — [TAS Rockman](https://tasvideos.org/GameResources/NES/Rockman)
- Inching: "In Rockman 1, when Rockman accelerates from non-full speed (full halt or deacceleration), his X speed is 00.20 for 9 frames before gaining full speed." Rockman 2 does the same for 7 frames. — [TAS Rockman Data](https://tasvideos.org/GameResources/NES/Rockman/Data)
- Deceleration: "In Rockman 1, when Rockman decelerates from full speed (not from acceleration), his X speed is 00.80 for 13 (decimal) frames before halting completely." Rockman 2 does this for 8 frames. — [TAS Rockman Data](https://tasvideos.org/GameResources/NES/Rockman/Data)
- Code [DISASM `$94FF–$951D`]: "if left/right is held in this frame and was not held in previous frame then Make Megaman move slowly". This sets sprite state `$03`, annotated "moving slowly (also causes slow movement!)". State `$03` becomes running `$06` when the animation counter reaches `$22` (`$9601–$9618`). On release from `$06`, the state becomes `$0C` "slowing down after running (also causes movement)" (`$95E1–$95EF`). — [Bisqwit maincode.txt](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt)
- Conversions (own calculation):
  - Walk 1.375 px/f = 82.64 px/s = 3.44 Mega-Man-heights/s (24 px).
  - Air 1.3125 px/f = 78.88 px/s = 3.29 h/s.
  - Inch: 9 × 0.125 = 1.125 px before full speed (full speed from frame 10).
  - Stop slide: 13 × 0.5 = 6.5 px.
  - Mega Man is about 8% slower than walking Mario and 45% slower than running Mario in px/s. In own-heights per second he is close to Super Mario walking (2.82 h/s) and slower than small Mario walking.

### Inferences
- From the code (own reading): reversing directly Right→Left with no neutral frame does not trigger the inch, because the "not held in previous frame" test sees a direction already held. MM1 turnarounds are therefore instant at full speed. Only starts from neutral get the 9-frame inch.
- Benchmark contrast: Mario's feel comes from a 0.7 s ramp and 0.25–0.8 s slides. Mega Man's comes from near-instant 1-frame response plus a tiny inch for pixel-precise nudging. A two-handed machine-gunner comando probably wants Mega Man-like ground response (aiming and positioning matter) with at most a short wind-up.

### Gaps
- Mario's minimum "first step" (a 1-frame tap) was not simulated. From the tables, a tap adds $98/256 of a subpixel per frame, so taps move far less than 1 px per frame.
- I did not confirm whether MM1's inch also applies to the in-air start beyond TASVideos' note: "In Rockman 1, if Rockman starts moving after not moving, his X speed first goes to 00.20, then back to 01.50" ([TAS Data](https://tasvideos.org/GameResources/NES/Rockman/Data)), which implies 1 slow frame in the air.

---

## Jump: velocity, gravity, height, airtime, variable jump

### Takeaway
Mario launches at −4 px/f, or −5 px/f at high run speed. Gravity is light while A is held and rising (0.117–0.156 px/f²) and 3.2–3.6× heavier once A is released or he starts falling (0.375–0.5625 px/f²). Fall speed caps at ≈4 px/f.
- Full standing jump: 66 px (4.1 small heights / 2.1 big heights), 53 frames of airtime.
- Full running jump: 83 px (5.2 / 2.6 heights), 57 frames.

Mega Man launches at 4.87 px/f with constant 0.25 px/f² gravity and a 12 px/f fall cap.
- Full jump: ≈50 px (2.08 heights), apex at frame 20, about 40 frames airborne.
- Releasing A does **not** zero his upward speed. It clamps it to 1.0 px/f if it was ≥ 2 px/f, so he still rises ≈2.5 px.

### Cited Findings
**Super Mario Bros. [DISASM]**
- Jump tables, indexed by horizontal speed at take-off (`ProcJumping`) — [smbdis.asm](https://gist.github.com/1wErt3r/4048722):
  - `JumpMForceData: .db $20, $20, $1e, $28, $28, $0d, $04` (gravity while rising with A held)
  - `FallMForceData: .db $70, $70, $60, $90, $90, $0a, $09` (gravity after release / when falling)
  - `PlayerYSpdData: .db $fc, $fc, $fc, $fb, $fb, $fe, $ff` (initial vertical speed, px/f)
  - `InitMForceData: .db $00, $00, $00, $00, $00, $80, $00`
  - Entries 5–6 are swimming / whirlpool.
- Speed brackets (`Player_XSpeedAbsolute` at take-off; `cmp #$09 / #$10 / #$19 / #$1c`):

  | Index | Take-off speed | px/f | Rising gravity | Falling gravity | Initial vy |
  |---|---|---|---|---|---|
  | 0 | < $09 | < 0.5625 | $20 | $70 | −4 |
  | 1 | $09–$0F | 0.5625–<1.0 | $20 | $70 | −4 |
  | 2 | $10–$18 | 1.0–1.5; includes max walk $18 | $1E | $60 | −4 |
  | 3 | $19–$1B | 1.5625–1.6875 | $28 | $90 | −5 |
  | 4 | ≥ $1C | ≥ 1.75; includes run $28 | $28 | $90 | −5 |

- Gravity units [DISASM `ImposeGravity`]: the force is added to `Y_MoveForce` (1/256 px) and carries into `Y_Speed`.
  - $20 = 0.125 px/f², $1E = 0.1172, $28 = 0.15625, $70 = 0.4375, $60 = 0.375, $90 = 0.5625 px/f² (own calculation /256).
  - In px/s²: 451, 423, 564, 1580, 1354 and 2032 respectively (own calculation ×60.0988²).
- Variable jump mechanism [DISASM `JumpSwimSub`], confirmed: gravity stays at the rising value while Y speed is negative **and** A is held this frame and last frame (`and PreviousA_B_Buttons`). Otherwise, once Mario is ≥ 1 px above the jump origin (`DiffToHaltJump` = 1), `VerticalForce` is overwritten with `VerticalForceDown` (the fall value). Once Y speed ≥ 0 the fall value is used regardless. Re-pressing A cannot restore light gravity, because the value was overwritten. — [smbdis.asm](https://gist.github.com/1wErt3r/4048722)
- Max fall speed [DISASM `MovePlayerVertically`: `lda #$04 ;set maximum vertical speed here`]. Integer speed is clamped to 4 when ≥ 4 and the fraction ≥ $80. — [smbdis.asm](https://gist.github.com/1wErt3r/4048722)
  - The RAM map says "Downward: 05 = fastest fall" and notes the fractional byte "is not accounted for when clamping to max fall velocity". — [RAM Data Crystal](https://datacrystal.tcrf.net/wiki/Super_Mario_Bros./RAM_map)
  - My simulation shows integer speed held at 4 with an average of 4.0–4.23 px/f (240–254 px/s) (own simulation).
- Walking off a ledge [DISASM `FallingSub`]: falling uses `VerticalForceDown`. That value is set only at jump start (`GetYPhy`), or to `$28` at level entry (`Entrance_GameTimerSetup`). So ledge-fall gravity is whatever the **last jump's** fall gravity was ($28 / $60 / $70 / $90) (own reading of code).
- Simulated jump results (own simulation of `JumpSwimSub` + `ImposeGravity`; flat ground; frame 1 = the A-press frame, on which Mario already moves up; "lands" = frame the feet re-enter the ground row):

  | Take-off bracket | Hold | Apex px | Small h (16) | Big h (32) | Apex frame | Land frame | Airtime s |
  |---|---|---|---|---|---|---|---|
  | 0–1 (standing / slow) | full | 66 | 4.13 | 2.06 | 29 | 53 | 0.882 |
  | 0–1 | 1-frame tap | 24 | 1.50 | 0.75 | 10 | 21 | 0.349 |
  | 2 (walk, incl. max walk) | full | 71 | 4.44 | 2.22 | 33 | 58 | 0.965 |
  | 2 | tap | 27 | 1.69 | 0.84 | 12 | 24 | 0.399 |
  | 3–4 (run) | full | 83 | 5.19 | 2.59 | 30 | 57 | 0.948 |
  | 3–4 | tap | 29 | 1.81 | 0.91 | 10 | 21 | 0.349 |

  Apex-time seconds (own calculation): 29 f = 0.483 s, 33 f = 0.549 s, 30 f = 0.499 s.
- Size does not change physics. The jump code never reads `PlayerSize` except to choose the jump sound (`PJumpSnd`). — [smbdis.asm](https://gist.github.com/1wErt3r/4048722)

**Mega Man [TAS + DISASM]**
- "In Rockman 1 and 2, when Rockman jumps, his Y speed is set to 04.DF." "Every frame, 00.40 is subtracted from his Y speed (0.25 in decimal)." "In Rockman 1 and 2, if the Y speed grows smaller than −0C.00 (−12 in decimal), it is set to −0C.00." — [TAS Rockman Data](https://tasvideos.org/GameResources/NES/Rockman/Data)
- Code [DISASM `$961E`]: `LDA #$04 / STA ObjectYSpeed / LDA #$df / STA ObjectYSpeedFraction`.
- Gravity and cap [DISASM `$9C65–$9C7F`]: `SBC #$40`, then `CMP #$f4 ... LDA #$f4`.
- Landing/bump [DISASM `$9C25–$9C2C`, `$9C4D–$9C54`]: speed is set to `$FF.40` (−0.75).
- All three Mega Man code items above are from [Bisqwit maincode.txt](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt).
- TAS states the same landing rule: "Every frame when Rockman bumps into an platform … Rockman's Y speed is set into a constant. Rockman 1: −00.C0." — [TAS Rockman Data](https://tasvideos.org/GameResources/NES/Rockman/Data)
- Variable jump: "In Rockman 1 and 2, if the Y speed is larger than 02.1F and the player is not holding the A button, the speed is immediately set to 01.00." — [TAS Rockman Data](https://tasvideos.org/GameResources/NES/Rockman/Data)
  - Code [DISASM `$9559–$956B`]: if the integer Y speed is > 1 and A is not held, `LDA #$01 / STA ObjectYSpeed / LDA #$00 / STA ObjectYSpeedFraction`. — [Bisqwit](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt)
  - The brief's hypothesis ("zeroes upward velocity") is **not correct for MM1**. The speed is set to +1.0 px/f, not 0.
  - Per TAS, Rockman 3 sets −00.80 and Rockman 4 sets −00.00 on release.
- Simulated jump results (own simulation; 8.8 fixed point; frame 1 = first frame **after** the press frame, because the jump speed is written on the press frame and position starts changing next frame):

  | A held (frames incl. press) | Apex px | Mega Man heights (24 px) | Apex frame | Land frame | Airtime s |
  |---|---|---|---|---|---|
  | 1 | 7.37 | 0.31 | 5 | 14 | 0.233 |
  | 2 | 11.99 | 0.50 | 6 | 17 | 0.283 |
  | 4 | 20.48 | 0.85 | 8 | 22 | 0.366 |
  | 6 | 27.98 | 1.17 | 10 | 26 | 0.433 |
  | 8 | 34.47 | 1.44 | 12 | 30 | 0.499 |
  | 10 | 39.96 | 1.67 | 14 | 33 | 0.549 |
  | ≥12 (full) | 49.92 | 2.08 | 20 (0.333 s) | 40 | 0.666 |

  Check (own calculation): there are 20 rising frames because 0x4DF − 0x40×19 = 0x1F > 0, and the rise is Σ(1247 − 64k)/256 for k = 0..19 = 12780/256 = 49.92 px.
- Ledge fall (own simulation, starting at the grounded −0.75 px/f): drops 16 px by frame 10 and 24 px by frame 12. The 12 px/f cap is only reached after 45 frames (> 240 px, i.e. more than a screen), so within one screen the fall is effectively uncapped.

### Inferences
- Jump heights at the comando's 128-px scale (own calculation, scaling by character height):
  - Mega Man full jump 2.08 h ≈ 266 px.
  - Super Mario full standing jump 2.06 h ≈ 264 px; running 2.59 h ≈ 332 px.
  - Small Mario 4.1–5.2 h is far beyond what a "realistic" commando should do.
- Airtime: Mario 0.88–0.97 s versus Mega Man 0.67 s. Mega Man's symmetric arc (same gravity up and down) feels "floatier at the top, slower to fall" than Mario's asymmetric arc. Mario's arc has heavy post-apex gravity, about 3.5× the rising gravity.
- Mario's take-off-speed bracket rewards running with a higher jump (+17 px). Mega Man's jump is independent of horizontal motion.

### Gaps
- TAS gives the MM1 release threshold as "> 02.1F", while my reading of the code is "integer part ≥ 2" checked after gravity. This can shift the hold-time-to-full-height threshold by about 1 frame (my simulation says ~12 frames). Not verified in an emulator.
- MM1's per-sprite collision half-height table (`TableObjectYHeightTable2`) reads $0C (12 px) for most entries in Bisqwit's listing. However, the listing's label address ($FB4B) does not match the operand the code uses ($FBB7), so I treat "Mega Man's feet are 12 px below his center" as likely but unverified.

---

## Air control

### Takeaway
Mario has momentum-based, partial air control:
- He keeps his horizontal speed with no input and accelerates or decelerates at ground-like rates when L/R is held.
- He cannot exceed walking speed in the air if he took off (or dropped) below 1.5625 px/f.
- He **cannot turn around (change facing) in mid-air**.

Mega Man has full, instant air control: 1.3125 px/f in whichever direction is held, 0 when nothing is held, instant reversal, and he can turn to face (and shoot) either way in the air.

### Cited Findings
- SMB [DISASM `JumpSwimSub`/`LRAir`]: in the air, `ImposeFriction` runs only `if left/right controller bits` are set. With no input the speed is unchanged, so there is no air drag. `PlayerFacingDir` is written only in `OnGroundStateSub` (and while swimming), so facing is locked in the air. — [smbdis.asm](https://gist.github.com/1wErt3r/4048722)
- SMB [DISASM `X_Physics`]: airborne with |speed| ≥ $19, Mario uses the run table (max $28, adder $E4). Otherwise he uses the walk table (max $18, adder $98, or $D0 if `RunningSpeed` is set). The adder doubles when facing ≠ moving direction. — [smbdis.asm](https://gist.github.com/1wErt3r/4048722)
- "In the air, you can gather more rightward speed in the air if it's above 24". — [TASVideos #9971 notes](https://tasvideos.org/Forum/Posts/538365)
- A TASVideos submission also says that if you fall under the maximum walking speed during a jump, you cannot go above it again until you touch the ground. This was surfaced via search from [TASVideos 9971S](https://tasvideos.org/9971S). It matches the code above.
- TASVideos lists a "backward small jump for faster acceleration" (press Left+Right for 1 frame, then A). This exploits the doubled adder when facing ≠ moving. — [TASVideos SMB](https://tasvideos.org/GameResources/NES/SuperMarioBros); SDA describes the same "Backwards jump acceleration" qualitatively. — [SDA KB](https://kb.speeddemosarchive.com/Super_Mario_Bros)
- Mega Man: "during jumping/falling into some direction, Rockman's X speed is 01.50." "If the player stops pressing the directional button, the speed falls immediately into 00.00." — [TAS Rockman Data](https://tasvideos.org/GameResources/NES/Rockman/Data)
- Mega Man [DISASM `$94FF–$951D`, `SetMegamanFacing $987B`]: whenever L/R is held, facing is set from the right-button bit and the "moving" flag is set. This code is not gated by ground state. — [Bisqwit](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt)

### Inferences
- Mario mid-air reversal from a full run (own calculation): the adder is $E4 = 0.0557 px/f² (not doubled while facing = moving), so 2.5 → 0 px/f takes ≈45 frames, nearly the whole 57-frame jump. A Mario arc is effectively committed. A Mega Man arc is not committed at all.
- Horizontal jump distance (own calculation, full jump on flat ground):
  - Mario running: 57 f × 2.5 = 142 px (8.9 blocks, 4.4 big-Mario heights).
  - Mario walking: 58 × 1.5 = 87 px.
  - Mega Man: 40 × 1.3125 = 52.5 px (3.3 blocks, 2.2 heights).

### Gaps
- No source quantified "how much" of a Mario jump can be steered. The numbers above come from the code tables.

---

## Coyote time and jump buffering

### Takeaway
Neither game has coyote time or jump buffering. Both require a **new** A press (pressed this frame, not last frame) on a frame where the character is registered as grounded. A press made in the air is consumed. Holding A through landing does not re-jump.

### Cited Findings
- SMB [DISASM `PlayerBGCollision`]: every frame the player state is first set to "falling" (`SetFallS: lda #$02 / sta Player_State`) and only reset to 0 (on ground) if a foot sensor finds a solid tile (`LandPlyr` → `InitSteP`). — [smbdis.asm](https://gist.github.com/1wErt3r/4048722)
- SMB `ProcJumping` jumps only if `Player_State` is 0 ("if on the ground, branch"). A mid-air press goes to `NoJump` "to prevent midair jumping". — [smbdis.asm](https://gist.github.com/1wErt3r/4048722)
- SMB `CheckForJumping` requires A pressed and **not** pressed in the previous frame (`and PreviousA_B_Buttons / beq ProcJumping`). `PreviousA_B_Buttons` is saved every frame (`SaveAB`). — [smbdis.asm](https://gist.github.com/1wErt3r/4048722)
- RAM map: `$001D` = "0x02 - Airborn by walking of a ledge", a state distinct from on-ground, so a jump in that state is not possible. — [RAM Data Crystal SMB](https://datacrystal.tcrf.net/wiki/Super_Mario_Bros./RAM_map)
- Mega Man [DISASM `$9571–$9585`, `$95BD–$95C1`, `$961E`]: the jump is issued only in the falling/grounded branch after `ObjectDoCollisionChecksAndAvoidWalls` returns carry (floor contact this frame), and only if `JoyD0` bit A is set. `JoyD` is annotated "Keys pressed on this frame", distinct from `JoyPads` "Keys held down on this frame". — [Bisqwit](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt)

### Inferences
- Both games accept a new A press on the landing frame itself (own reading of code: SMB's state is set to 0 on the previous frame's collision; MM1 checks floor contact and the A press in the same routine). The usable window is exactly "from the first grounded frame on", with 0 frames of grace before landing or after leaving a ledge.
- Mega Man: when he walks off a ledge, his speed is already the grounded −0.75 px/f. No floor contact occurs on the next frame, so a jump press there fails.
- For the comando prototype, both baselines are "unforgiving". Modern design would add both features: typically ~4–6 frames of coyote time and ~4–8 frames of buffer at 60 Hz. This is design context, not from these sources.

### Gaps
- No TASVideos page states "no coyote time / no buffer" in so many words. The conclusion rests on the disassembly logic above. Not emulator-verified frame by frame.

---

## Shooting (Mega Man; Fire Mario for contrast)

### Takeaway
The Mega Buster fires only horizontally, in the facing direction, at 4 px/f (240 px/s). It spawns 16 px in front of Mega Man's center at his center height. At most 3 shots can be on screen. Each shot needs a fresh B press (no autofire).

He can shoot while standing, running, jumping or falling, and on ladders. Each case swaps to a separate full-body "firing" sprite. The pose is held about 15 frames (0.25 s) after the last shot, and on ladders it also freezes climbing during that time.

### Cited Findings
- Fire trigger [DISASM `$9538–$953E`]: `LDA JoyD0 / AND #$02 ; If B pressed / JSR MegamanWeaponFire`. `JoyD` = "Keys pressed on this frame". — [Bisqwit](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt)
- Max bullets [DISASM `MegamanWeaponFire_P $A747–$A755`]: the routine searches object slots X = 2..4 (`CPX #$05`) for a free slot (`ObjectPosY = $F8` = dead object). With none free, nothing fires. So at most **3** buster shots exist at once. — [Bisqwit](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt); TAS: "Y coordinate F8 (−08) means a dead object." — [TAS Data](https://tasvideos.org/GameResources/NES/Rockman/Data)
- Bullet data [DISASM `MegamanWeaponFireData`, row `;P`]: `.byte $1A,$00,$00,$00,$00,$00,$04,$00,$10`. That is Y speed 0, X speed $04.00 = **4 px/f**, Y offset 0, X offset $10 = **16 px** ahead (added or subtracted by facing in `LaunchMegamanWeaponShot $A963–$A994`). — [Bisqwit](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt)
- Pose timer [DISASM `$A75C–$A75E`]: `LDA #$1f / STA ObjectFireDelay+0 ;delay for Megaman if he's standing`. — [Bisqwit](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt)
- Sprite selection [DISASM `DrawObject $D184–$D190`]: the drawn sprite = `ObjectSpriteNum + (ObjectFireDelay >> 4)`, so a high nybble of 1 selects the "+1" firing variant. At `$D1D4–$D1E6` the low nybble counts down by 1 per drawn frame and the whole byte is cleared when it reaches 1. — [Bisqwit](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt)
- Sprite state list [DISASM header]: `$00` standing, `$01`/`$04` "firing megablaster (while standing)", `$06` running, `$07` "running while firing megablaster", `$09` jumping/falling, `$0A` "firing megablaster while jumping", `$15` on ladder, `$16` "Firing while on ladder", `$6E/$6F/$70` throwing (standing / jumping / ladder; used by Cut/Bomb weapons). — [Bisqwit](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt)
- Ladder [DISASM `Ladder_B_Pressed $9854–$9862`]: on B, Mega Man faces the held L/R direction, sets `ObjectFireDelay+0 = $1F`, and fires. `Ladder_Climb $9838–$983F` reads "don't climb if weapon fire delay is active". — [Bisqwit](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt)
- Starting to walk from neutral clears `ObjectFireDelay+0` (`$9510–$9515`), which cancels the shooting pose. — [Bisqwit](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt)
- TAS: "Shooting while climbing (MM1): the delay drops from about 60 frames to about 2 frames" with a trick. — [TAS Rockman](https://tasvideos.org/GameResources/NES/Rockman) (summarized by fetch tool; context is a speedrun trick, not normal play)
- Fire Mario [DISASM `ProcFireball_Bubble`, `FireballXSpdData: .db $40, $c0`]:
  - Fires on a new B press, only if Fiery and not crouching or climbing.
  - Uses 2 fireball slots (`FireballCounter` LSB), so at most **2** fireballs.
  - Horizontal speed $40 = 4 px/f.
  - Spawns at player X + 4.
  - Shows a single "fireball throwing" frame for about `PlayerAnimTimerSet` frames (2–7).
  - Source: [smbdis.asm](https://gist.github.com/1wErt3r/4048722)

### Inferences
- Pose duration (own reading of code): `$1F` → drawn with the firing sprite while the value runs `$1F…$11`, i.e. **15 frames (0.25 s)** after each shot. Each new shot restarts it, so rapid tapping holds the pose continuously.
- Effective fire rate (own calculation): a shot needs ≥ 1 frame of B released between presses, so the hardware-input maximum is 30 presses/s. In practice it is bullet-capped. With the camera centering Mega Man (`AutoCenterScreen` sets scroll = X − 128), a shot spawned 16 px ahead travels ≈112 px to the screen edge in ≈28 frames. Against an open screen that sustains about 3 shots / 28 frames ≈ **6.4 shots/s**. It is higher when shots hit nearby enemies or walls. This assumes off-screen shots are freed at the edge, which I did not verify.
- A two-handed machine gun maps naturally to Mega Man's model: separate full-body "firing" sprites for each locomotion state, swapped in by a timer rather than layered. The 0.25 s hold avoids flicker between poses during rapid fire.

### Gaps
- Exact despawn rule for shots that leave the screen: not checked.
- Mega Man cannot shoot up or diagonally in MM1. Confirmed only indirectly (Y speed 0 in the fire data and no aim input in the fire routine).

---

## Sprites and animation

### Takeaway
Mario's metasprite is 2 tiles wide (16 px): 2×2 tiles (16×16) small and 2×4 tiles (16×32) big. He has a 3-frame walk/run cycle whose speed depends on velocity: each drawing lasts 7, 4 or 2 game frames. Jump is a single held frame, skid is 1 frame, and there is no idle animation.

Mega Man's standing sprite is ~21×24 px. He has:
- an idle stand with an occasional 9-frame eye blink;
- a 1-frame "inch/tiptoe" start;
- a 3-drawing run cycle played as 4 steps (1-2-3-2);
- 1 jump frame;
- a duplicate full-body set of firing frames (stand, 3 run, jump, ladder).

### Cited Findings
- SMB [DISASM `PlayerGraphicsTable`]: "tiles arranged in order, 2 tiles per row, top to bottom". Each frame lists 8 tiles (2 wide × 4 tall = 16×32). Small-Mario frames have `$fc` (blank) for the top 4 tiles, i.e. a 16×16 sprite in the lower half. — [smbdis.asm](https://gist.github.com/1wErt3r/4048722)
- SMB frame list [DISASM]:
  - Big Mario: walking frames 1/2/3, skidding, jumping, swimming ×3, climbing ×2, crouching, fireball throwing, plus a standing frame (offset `$c8`).
  - Small Mario: the same set without crouch and throw.
  - Source: [smbdis.asm `PlayerGraphicsTable`, `PlayerGfxTblOffsets`](https://gist.github.com/1wErt3r/4048722)
- SMB walk/run cycle [DISASM `FourFrameExtent`/`AnimationControl`]: the upper extent is 3, so the frame control cycles 0,1,2 (3 drawings). `PlayerAnimTmrData: .db $02, $04, $07` selects 2 when |speed| ≥ $1C, 4 when ≥ $0E, else 7 (`GetPlayerAnimSpeed`). — [smbdis.asm](https://gist.github.com/1wErt3r/4048722)
- SMB jump/fall [DISASM `ProcessPlayerAction`]:
  - Jumping state uses the single "jumping" frame.
  - Falling off a ledge (`ActionFalling`) keeps the current walk frame **frozen** (`GetCurrentAnimOffset` without advancing).
  - Standing (no speed, no input) uses the single standing frame.
  - Skid frame shows when |speed| ≥ $09 and facing ≠ moving.
  - Source: [smbdis.asm](https://gist.github.com/1wErt3r/4048722)
- SMB sprite measurements (own measurement on the [Mario Universe SMB rip](https://www.mariouniverse.com/sprites-nes-smb/), image `mario.png`; the sheet shows each frame mirrored; frame labels by visual identification; bounding box of non-background pixels):
  - Small Mario frames 12–17 px wide × 15–16 tall: standing 13×16, walk frames 14×16 / 12×16 / 16×16, skid 14×16, jump 17×16.
  - The 17-px value exceeds the 16-px tile width, so treat ±1 px as rip error.
  - Big Mario frames 14–16 px wide × 30–32 tall; crouch 16×22.
- Mega Man animation counter [RAM]: "Mega Man's Blink Timer (0x0440): Counts $01/frame pseudo base 9; eyes close at $A2 for 9 frames". — [Data Crystal Mega Man RAM map](https://datacrystal.tcrf.net/wiki/Mega_Man_(NES)/RAM_map)
- Mega Man animation engine [DISASM `$D2F8–$D327`]: each sprite state's animation data starts with a byte whose low nybble = delay and high nybble = last frame index. `ObjectUnknown440` (= $0440) low nybble counts up to the delay, then the high nybble (frame index) advances and wraps. — [Bisqwit](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt)
  - The per-state animation data tables themselves are not in Bisqwit's listing (they live in another bank). The "pseudo base 9" RAM note implies a delay of 8 (9 frames per drawing) for the idle animation.
- Run cycle structure: "With just 3-frames it captures more kinetic energy than most modern run cycles". "Technically there are 4 frames in the loop but the same pass frame is used twice." — [Slynyrd Pixelblog 8](https://slynyrd.com/blog/2018/8/19/pixelblog-8-intro-to-animation) [WIKI/FORUM]
- Run cycle timing: a gamedev.net forum post reportedly says the NES Mega Man run cycle advances every 8 video frames (~133 ms per drawing). This was seen only in a search-result summary; the page returned 403 to me, so it is **unverified**. — [gamedev.net thread](https://gamedev.net/forums/topic/642655-understanding-2d-walkingrun-animation-in-games/)
- Mega Man sprite measurements (own measurement on the Sprites INC "8-bit Mega Man" composite rip, [gallery page](https://www.sprites-inc.co.uk/sprite.php?local=Classic/Megaman/MM8/), image `8bitmegaman.png`; this is a composite of NES-era frames, so a few frames may come from MM2+; bounding box of non-background pixels):

  | Pose | Size (w×h px) |
  |---|---|
  | Stand (eyes open) | 21×24 |
  | Stand (blink) | 21×24 |
  | Inch / tiptoe step | 20×24 |
  | Run 1 / 2 / 3 | 24×22, 16×24, 21×22 |
  | Jump | 26×30 |
  | Stand-shoot | 31×24 |
  | Run-shoot 1 / 2 / 3 | 29×22, 26×24, 30×22 |
  | Jump-shoot | 29×30 |
  | Ladder (climb frames) | 16×29 |
  | Ladder-shoot | 24×29 |
  | Ladder top | 16×22 |
  | Teleport beam | 7×32 |
  | Teleport landing frames | 22×11 and 22×12 |

### Inferences
- Mario animation rate (own reading of code): the timer is reloaded when it reaches 0 and decremented once per frame before the check, so each drawing lasts exactly the table value:
  - Slow (< 0.875 px/f): **7 frames per drawing** (21-frame cycle, 8.6 drawings/s).
  - Walking (0.875–1.6875 px/f, including max walk 1.5): **4 frames** (12-frame cycle, 15 drawings/s).
  - Running (≥ 1.75 px/f): **2 frames** (6-frame cycle, 30 drawings/s).
  - At 12 fps the comando's 5-frame hold sits between Mario's walk (4) and slow (7) rates.
- Stride check (own calculation):
  - Mario walking: 12 frames × 1.5 = 18 px per 3-drawing cycle (≈1.1 small heights).
  - Mario running: 6 × 2.5 = 15 px per cycle.
  - Mega Man (if 8 frames/drawing × 4 steps): 32 × 1.375 = 44 px per cycle (1.8 heights), i.e. two strides of ~22 px ≈ his own width.
- Mega Man's blink (own inference from the RAM note): eyes are closed for 9 frames (0.15 s) per idle cycle. The cycle length is unconfirmed. If the idle sequence wraps right after the blink step at index A, the period would be ≈100 frames (~1.7 s), but this is speculative.
- Extra frames for shooting (own count from the rip): Mega Man needs **6 extra full-body frames**: stand 1, run 3, jump 1, ladder 1. These are complete redraws with the arm cannon extended. The shooting frames are 5–10 px wider than their non-shooting twins (e.g. stand 21 → 31 px). Mario needs 1 extra frame (throw).

### Gaps
- The Spriters Resource pages (requested source) were blocked by a Cloudflare "Verify you are human" check. I did not attempt to pass it, so I used Mario Universe and Sprites INC rips instead.
- Exact MM1 run-cycle delay, idle cycle length and the landing (`$0F`) frame duration require the ROM's animation tables or emulator frame-stepping. **Not found**.

---

## Hitbox vs sprite width, floor sensors and edge behavior

### Takeaway
Mario's hurtbox is narrower and shorter than his 16-px-wide sprite: 12×24 big, 10×12 small. His floor is tested at two foot points 9 px apart (x+3 and x+12 of the 16-px frame), so he can stand with only the outer ~4 px of his frame over a ledge.

Mega Man's hurtbox is 14×22 inside a ~21×24 sprite. His floor is tested at two points at center ±7 px, so he can stand until his center is 7 px past the edge, with only ~4 px of his sprite over the block.

Neither game has a ledge-teeter / balance animation.

### Cited Findings
- SMB hurtbox [DISASM `BoundBoxCtrlData`, "left edge, top edge, right edge, bottom edge"]: row 0 big `$02,$08,$0e,$20`; row 1 small `$03,$14,$0d,$20`; row 2 big-crouching `$02,$14,$0e,$20`. `Player_BoundBoxCtrl` is 0 for big, 1 for small, 2 for big crouching (`ChkMoveDir`). — [smbdis.asm](https://gist.github.com/1wErt3r/4048722)
- SMB background sensors [DISASM `BlockBuffer_X_Adder`/`BlockBuffer_Y_Adder`, `BlockBufferAdderData: .db $00, $07, $0e`] — [smbdis.asm](https://gist.github.com/1wErt3r/4048722):
  - Big Mario: head (x+8, y+4); feet (x+3, y+32) and (x+12, y+32); sides (x+2 / x+13, y+8 and y+24).
  - Small or crouching: head (x+8, y+18); feet (x+3 / x+12, y+32); sides (x+2 / x+13, y+24).
- SMB landing tolerance [DISASM `ChkFootMTile`]: Mario lands only if his Y low nybble is < 5 (≤ 4 px into the tile). Deeper penetration is treated as a side hit (`ImpedePlayerMove`). — [smbdis.asm](https://gist.github.com/1wErt3r/4048722)
- "There are a few pixels of room on both sides of the pipe that you can land on and immediately jump off again." — [SDA KB](https://kb.speeddemosarchive.com/Super_Mario_Bros)
- SMB contact quirks: "Enemy hitboxes affect Mario only on every other frame", and "Damage occurs only if Mario overlaps an enemy hitbox for two or more consecutive frames." — [TASVideos SMB](https://tasvideos.org/GameResources/NES/SuperMarioBros) (as summarized by fetch tool)
- Mega Man hurtbox [DISASM `RunCollisionChecks $A18B–$A1A6`]: X from PosX−7 to (PosX−7)+$0E, Y from PosY−$0B to (PosY−$0B)+$16. That is **14 px wide × 22 px tall**, centered on his position. Enemies are tested on alternating frames (`FrameCounter AND #$01`). — [Bisqwit](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt)
- Mega Man floor/ceiling sensors [DISASM `DoCollisionCheckFor $CC2D–$CC5F`]: for object 0 (Mega Man) the map is read at X + `CC5C_table`, annotated `;+7` and `;-7`. That is two points at **center ±7 px**. Landing snaps `ObjectPosY = (tileTop) − height` (`$9C3E–$9C45`). — [Bisqwit](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt)
- Mega Man top/bottom collision: "Top collision checked only when moving upwards, bottom collision checked only when moving downwards." — [TAS Rockman Data](https://tasvideos.org/GameResources/NES/Rockman/Data)
- No teeter state exists:
  - SMB's complete player frame list has no balance frame. — [smbdis.asm](https://gist.github.com/1wErt3r/4048722)
  - MM1's complete sprite-state list ($00–$19, $6E–$70) has no balance state. — [Bisqwit](https://bisqwit.iki.fi/jutut/megamansource/maincode.txt)
  - TAS notes a MM6 glitch where Mega Man "can stand or walk on air past a ledge". It is a glitch, not an animation. — [TAS Rockman](https://tasvideos.org/GameResources/NES/Rockman)

### Inferences
- Box vs sprite ratios (own calculation):
  - Big Mario: 12/16 = 75% of the width, 24/32 = 75% of the height. The hurtbox starts 8 px below the head top.
  - Small Mario: 10/16 = 62.5% of the tile width (≈77–83% of the 12–13 px visible standing sprite), 12/16 = 75% of the height.
  - Mega Man: 14/21 = 67% of the standing width, 22/24 = 92% of the height. Against the 31-px shooting pose it is only 45%, so the arm cannon is never hittable.
  - Mega Man's height basis for normalization: 24 px sprite, 22 px hurtbox, and probably 24 px for terrain (±12, see the jump-section gap).
- Edge overhang (own calculation):
  - Mario: support holds while the foot sensor x+3 (moving right off an edge) is over the block. Mario's frame can therefore extend 12 px past the block edge with 4 of its 16 px over the block. With the visible small-Mario sprite inset ~2 px, about 2 visible px remain over the block.
  - Mega Man: support holds until center−7 leaves the block. His center can sit 7 px past the edge, leaving ≈3–4 px of his 21-px standing sprite (center −10/−11) over the block, with ~17 px visually over the void.
  - Both games look generous at edges. At the comando's 128-px scale this is ≈20–24 px of overhang tolerance per side if the same proportions are kept.
- Floor-support span: Mario 10 px (62% of 16) and Mega Man 15 px (71% of 21). A comando with a 2-point foot probe at about ±30–35% of sprite width would reproduce this feel.

### Gaps
- Mega Man's horizontal wall-sensor offsets (`ObjectUpdateMovementRight/Left`) were not read. **Not found**.
- Exact pixel offset of Mega Man's position within his drawn standing sprite (whether the center is at pixel 10 or 11 of 21) was not verified. Overhang figures carry ±1 px uncertainty.

---

## Compact comparison table

### Takeaway
Mario is a momentum character: ramped acceleration, a speed-dependent and asymmetric (floaty-up, heavy-down) jump, a committed arc, and no mid-air turn. Mega Man is a precision character: instant speed, a fixed symmetric jump with an A-release clamp, full air control, and a 3-shot horizontal gun with full-body shooting frames. Neither has coyote time, buffering or a teeter animation.

### Cited Findings
Values in this table come from the cited findings in the sections above, with sources there. h = character heights (16 px small Mario, 32 px Super Mario, 24 px Mega Man). "f" = frame at 60.0988 Hz. Derived values are own calculations or simulations as labeled in the sections.

| Category | Small Mario (16 px) | Super Mario (32 px) | Mega Man 1 (24 px) |
|---|---|---|---|
| Native res / logic rate | 256×240 (≈256×224 visible), 60.0988 Hz | same | same |
| Ground top speed | walk 1.5 px/f = 90.2 px/s = 5.63 h/s; run 2.5 px/f = 150.3 px/s = 9.39 h/s | walk 2.82 h/s; run 4.70 h/s | 1.375 px/f = 82.6 px/s = 3.44 h/s |
| Acceleration | ramped: 0.0371 (walk) / 0.0557 (run) px/f²; 41 f to walk max, 45 f to run max | same | instant after a 9-f inch at 0.125 px/f (≈1.1 px) |
| Deceleration / skid | release 0.0371 or 0.0508 px/f² (39–49 f, 28–58 px slide); skid ×2 (11–18 f) then instant flip | same | MM1: 0.5 px/f for 13 f (≈6.5 px); direct reversal instant |
| Jump initial vy | −4 px/f (−5 at ≥1.5625 px/f take-off) | same | +4.871 px/f (04.DF) |
| Gravity | held & rising 0.117–0.156 px/f²; released/falling 0.375–0.5625 px/f² | same | 0.25 px/f² always |
| Max fall | 4 px/f (≈4.0–4.2 effective) | same | 12 px/f (reached after 45 f; effectively uncapped on one screen) |
| Max jump height | 66 px standing (4.13 h) / 83 px running (5.19 h) | 2.06 h / 2.59 h | 49.9 px (2.08 h) |
| Min (1-frame tap) height | 24–29 px (1.5–1.8 h) | 0.75–0.91 h | 7.4 px (0.31 h) |
| Time to apex / airtime (full) | 29–33 f (0.48–0.55 s) / 53–58 f (0.88–0.97 s) | same | 20 f (0.33 s) / ≈40 f after the press frame (0.67 s) |
| Variable jump | release A → switch to heavy fall gravity for the rest of the jump | same | release A while vy ≥ ~2 → vy = 1.0 px/f (not 0); full height needs ~12 f hold |
| Air control | keeps momentum; steer at ground rates; can't exceed walk cap if below 1.5625 px/f; **no mid-air facing change** | same | 1.3125 px/f either way, 0 when released, instant reversal and facing change |
| Coyote time | none | none | none |
| Jump buffer | none (new press required on a grounded frame) | none | none |
| Shooting | Fire form only: 2 fireballs max, 4 px/f, 1 throw frame | same | horizontal only; 3 shots max; 4 px/f; spawn +16 px; works standing, running, jumping and on ladders; new press per shot |
| Shoot pose hold | ~2–7 f (anim timer) | same | 15 f (0.25 s) after last shot; freezes ladder climbing |
| Sprite size (measured) | 16×16 tile frame; 12–17×15–16 visible | 16×32 tile frame; 14–16×30–32 visible | stand 21×24; run 16–24×22–24; jump 26×30; shoot 26–31 wide |
| Animation | stand 1, walk/run 3 drawings at 7/4/2 f each by speed, skid 1, jump 1 (held), ledge-fall freezes walk frame | same (+ crouch, throw) | stand + 9-f blink, inch 1, run 3 drawings as 1-2-3-2 (~8 f each, unverified), jump 1, +6 full-body shoot frames |
| Hurtbox vs sprite | 10×12 vs 16×16 | 12×24 vs 16×32 | 14×22 vs 21×24 |
| Floor probe | 2 points: x+3, x+12 (10-px span) | same | 2 points: center ±7 (15-px span) |
| Edge overhang | stands with 4 of 16 frame px on block | same | stands until center 7 px past edge (≈3–4 of 21 px on block) |
| Teeter animation | none | none | none |

### Inferences
- Rescaled to the comando (128 px tall, own calculation from h/s and h):
  - Mega Man-like run ≈ 441 px/s with a ≈266 px jump.
  - Super-Mario-like run ≈ 601 px/s (walk 361 px/s) with a 264–332 px jump.
  - Small-Mario ratios (9.4 h/s, 5 h jumps) would read as superhuman for a commando.

### Gaps
- Not emulator-verified: MM1 run-cycle timing, idle cycle length, despawn of off-screen buster shots, and Mega Man's wall-sensor offsets (see the sections above).
