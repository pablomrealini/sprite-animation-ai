# Multi-angle aiming sprites, stance/hitbox/ledge conventions, and building aim sets with an AI image-to-video pipeline (run-and-gun "comando")

Research date: 2026-10-15. Context: 128 px tall HD cartoon commando at 1x, 12 fps, heavy two-handed MG at hip/chest, Seedance 2.0 image-to-video clips at about 864×496 (16:9, 24 fps), processed by spritepipe. Existing sets: idle 19 frames, shoot 8-frame loop (forward only), run 15, jump 13. Prototype issues: forward-only fire, barrel about 5° down, leg stance about 90 px vs. a 44 px collider.

Labels: "(vendor)" = source is the seller or host of the tool. "(community)" = forum, fan wiki or user post. "(own calculation)" / "(inference)" = mine, not from a source.

---

## 1. Aim-sprite construction techniques in shipped 2D games (split body, full sprite per angle, rotating arm/gun, skeletal rig)

### Takeaway
The best-documented shipped case is FuturLab's Velocity 2X. It split every frame into a waist-and-legs half and a torso-head-arms half because full-body aim × run sprites would have needed about 1,920 frames for the run alone and more than 9,000 across five states. The split cost them per-frame hard-coded torso bob offsets and an art rule that the back arm never crosses the waist. Full-body-per-angle (Contra, Cuphead) avoids seams but multiplies drawings by angle count. Rotating arm/gun pieces and Spine IK rigs give free aim cheaply at runtime but depend on clean part separation and a pivot/joint that survives rotation.

### Cited Findings
**Split torso/legs (Metal Slug-style)**
- Velocity 2X (FuturLab; article by developer James Marsden, reposted 6 Jul 2017) split each frame into "the bottom half (waist and legs)" and "the top half (torso, head and arms)". A full set for running plus 360° shooting would have been about 1,920 frames (64 aim frames × 30 run frames), and five situations (standing, running, jumping, falling, sliding) would have needed more than 9,000 frames, which they called "impractical from both a production and physical memory point of view" — [80.lv / Velocity 2X](https://80.lv/articles/the-animation-system-of-velocity-2x/)
- Velocity 2X: 64 frames cover firing in all directions. The run is 30 frames. More than 1,000 hand-drawn frames are stitched at runtime into "over 10,000 total frames of motion" — [80.lv / Velocity 2X](https://80.lv/articles/the-animation-system-of-velocity-2x/)
- Velocity 2X seam handling: the halves are drawn with "appropriate scale, offset and overlap values" so they read as one sprite, and the artists drew the back arm so it "never overlaps her waist" — [80.lv / Velocity 2X](https://80.lv/articles/the-animation-system-of-velocity-2x/)
- Velocity 2X pitfall: the run bob means top halves need per-frame offsets matching the legs. These "needed to be hard coded for each and every frame", which the author calls "the most complicated section of code in the game". The same technique was used earlier in FuturLab's Flash game PRISM — [80.lv / Velocity 2X](https://80.lv/articles/the-animation-system-of-velocity-2x/)
- A Metal Slug-inspired commercial asset pack states its sprites "are split into torso and leg parts so that they may change independent of each other", for "Metal Slug-like gameplay" (community/asset vendor) — [poohcom1 Soldier Girl pack](https://poohcom1.itch.io/soldier-girl-sprite-pack)
- Developer advice (itch.io): use "one lower part for the legs and a top part for the rest of the body" so the run depends only on the legs and the aim animation is independent of movement (community) — [itch.io post](https://itch.io/post/339254)
- Construct forum: separate upper and lower body sprites let the upper body shoot in multiple directions "while keeping the leg animations fluid". The same thread claims Contra also splits top and bottom halves into two sprites. This is a forum claim I could not verify against a disassembly (community) — [Construct forum](https://construct.net/en/forum/construct-2/how-do-i-18/shooting-walking-66970)
- Metal Slug 2 data-mining: player graphics are "strewn all over the place and arranged in contradictory manners", with some stored as "headswap" chunks for Marco/Fio rather than full assembled frames. This shows modular storage but does not confirm a torso/legs split (community) — [Metal Slug 2 unused graphics](https://randomhoohaas.flyingomelette.com/msmia/2/ug.html)
- Sync pitfalls of two independent state machines (one per half): if a state is inserted only in the upper body, the halves desync. One Construct user waited for both halves to finish before switching to idle (community) — [Godot Q&A](https://ask.godotengine.org/142455/synchronizing-multiple-animationnodestatemachine); [Construct forum](https://www.construct.net/en/forum/construct-2/how-do-i-18/match-animations-frames-67340)
- Layered approach in Construct: a separate aiming sprite layered over the body so the body is "not bound to the shooting animations". A related bug: a missing "walk up" animation made bullets spawn from the previous animation's image point during deceleration, showing that per-animation muzzle points must exist for every state × angle (community) — [Construct: separate parts](https://www.construct.net/en/forum/construct-2/how-do-i-18/separate-character-parts-67397); [Construct: 8-direction shooting problem](https://www.construct.net/en/forum/construct-2/how-do-i-18/direction-shooting-problem-128372)

**Full sprite per angle (Contra, Cuphead)**
- Contra: the player can shoot "leftward, rightward or upward while standing", "horizontally and diagonally while running", and "in any of eight directions, including downwards, while jumping". The jump is a somersault: "he curls into a somersault instead of doing a conventional jump". Down while standing makes the character lie prone. It uses an "eight-way joystick" — [Wikipedia: Contra](https://en.wikipedia.org/wiki/Contra_(video_game))
- Cuphead: a lock button (RB on Xbox) plants the character "for 8 way directional shooting" — [TrueAchievements guide](https://www.trueachievements.com/game/Cuphead/walkthrough/2); [Giant Bomb user review](https://giantbomb.com/user-reviews/id/363/cuphead-xbox-one-thoughts)
- Cuphead scale context: Guinness lists over 45,000 hand-drawn frames in the main game (about 72,000 with DLC), at an average of about 25 minutes per frame to draw, ink, scan, colour and finalise — [Guinness World Records](https://www.guinnessworldrecords.com/world-records/508061-most-hand-drawn-frames-of-animation-in-a-videogame)
- Indie asset devlogs show the full-sprite approach growing per state: Ansimuz added diagonal-aim sprites for running, crouching and clinging. Jambo Jungle added diagonal, up and down aim while jumping, hanging and standing (community/asset vendors) — [Ansimuz devlog](https://ansimuz.itch.io/gothicvania-patreon-collection/devlog/832357/16-bit-collection-new-animations-for-the-cave-hunter); [Jambo Jungle devlog](https://didigameboy.itch.io/jambo-jungle-free-sprites-asset-pack/devlog)

**Rotating arm/gun piece**
- Common setup: a separate arm/gun sprite with its anchor at the shoulder, cropped so the pivot is exact, with the angle computed from the shoulder (not the body centre) to the target (community) — [Godot forum](https://forum.godotengine.org/t/help-pivoting-arm-to-follow-the-mouse-aim/80147); [HTML5GameDevs](https://www.html5gamedevs.com/topic/21674-make-arm-and-gun-point-at-mouse-as-children-of-torso)
- Flip the gun sprite vertically when the angle passes 90° so it is never drawn upside-down (community) — [Godot Q&A](https://godotengine.org/qa/111824/sprites-rotation-degrees-when-passes-certain-rotation-degree)
- Nuclear Throne (Vlambeer, from Jan Willem Nijman's "Art of Screenshake" walkthrough): the gun is a separate sprite. "Weapon kick" moves it back a little, then it "super quickly slides back into place". The camera is kicked back from the aim point. The muzzle flash is faked by drawing the bullet circular on its first frame — [infovore.org writeup](https://infovore.org/?p=5275)
- A pre-rendered alternative to free rotation: rotating-gun packs that ship 8 drawn directions (community) — [OpenGameArt rotating gun](https://opengameart.org/content/rotating-gun-animation-16x16-orthographic)

**Skeletal / Spine aim rigs**
- Spineboy (official Spine example): one control bone drives aiming, and "When Spineboy aims, he moves not only his arm holding the gun, but also his torso, head, and front arm". A single-bone IK constraint `aim-torso-ik` drives a tiny `aim-constraint-target` bone parented to the hip. Transform constraints (`aim-torso-transform`, `aim-head-transform`, `aim-front-arm-transform`) with different Mix values then follow that bone. Constraint order matters (vendor) — [Spine: Spineboy example](https://eu.esotericsoftware.com/spine-examples-spineboy.md)
- Spineboy layering: `run` on track 0 and `aim` on track 1. "Lower tracks are applied first", so he keeps aiming at the crosshair while running. At runtime the control bone can be moved from code to aim at a point (vendor) — [Spine: Spineboy example](https://eu.esotericsoftware.com/spine-examples-spineboy.md)
- Muzzle/bullet spawn in Spine: point attachments "can be used to spawn particles or anything else that involves a position and/or rotation", for example "different guns may shoot from different positions". Points are moved by animating their bone (vendor) — [Spine: Point attachments](https://esotericsoftware.com/spine-points)
- Spine community pitfalls: the arm only followed the aim IK correctly when fully straight, and aiming multiple weapons with one rig needs extra setup. IK Mix can be changed from script (e.g., `FindIkConstraint("aim")`) (community) — [Spine forum: multiple weapons](https://hi.esotericsoftware.com/forum/d/15709-aiming-with-multiple-weapons); [Spine forum: aim IK point](https://fr.esotericsoftware.com/forum/d/13033-make-arm-aim-at-ik-point); [Spine forum: aiming system](https://tr.esotericsoftware.com/forum/d/12476-aiming-system-with-ik)

### Inferences
- Drawings needed (inference, generalising Velocity's arithmetic): full-body = Σ over states (angles valid in that state × frames in that state). Split = Σ(leg frames per state) + Σ(torso frames per angle × torso states). Rotating piece = Σ(body frames per state) + 1 gun/arm piece. Skeletal = 1 decomposed part set plus rig authoring. Velocity's 64 × 30 = 1,920 matches the full-body formula exactly.
- Where seams are hidden (inference from Velocity + general practice): (a) split body hides the cut under a belt line or overlap, keeps arms clear of the waist, and adds per-leg-frame torso offsets. (c) rotating arm hides the shoulder joint under a pauldron/sleeve or behind the torso, or simply accepts a floating hand/gun (Nuclear Throne style).
- The comando's hip-held two-handed MG is the worst case for both (a) and (c). The gun and both hands cross the waist line, which violates Velocity's "arms never overlap the waist" rule. Both arms must follow the gun, which a single rotating "arm" piece cannot do without redrawing shoulders. Moving the gun to chest height, with the stock and hands fully above the belt, makes both options more viable.
- Contra's somersault jump is a sprite-budget trick (inference from the cited mechanic). A curled body has no readable aim pose, so 8-way aiming in the air needs no aim sprites at all. Only the bullet spawn point changes.

### Gaps
- No primary SNK/Nazca source (interview, disassembly) confirming Metal Slug's player is stored as separate torso and legs layers. The evidence is community convention and modular "headswap" storage.
- No devlog or postmortem found for Gunstar Heroes, Huntdown, Mercenary Kings, Iconoclasts, Valfaris or Blasphemous describing how aim sprites were built (layers vs. full sprites). Mercenary Kings' use of Spine was not confirmed.
- No source found on how Broforce or Terraria build arms/guns.
- The NES Contra disassembly exists (player sprite logic in bank 2) but its aim-sprite composition was not read — [nes-contra-us](https://github.com/vermiceli/nes-contra-us)
- No source found on how Cuphead's animators split (or did not split) aim drawings, beyond the 8-direction gameplay.

---

## 2. How many aim angles run-and-guns and their players actually need (8-way, analog, Metal Slug sweep, snapping, 5-drawn-angle readability)

### Takeaway
Classic and neo-retro run-and-guns overwhelmingly use 8-way digital aim (Contra, Cuphead with lock, Valfaris, Gunstar Heroes' fixed mode, Blazing Chrome with lock). Metal Slug uses fewer (forward/up/down, with diagonals only as a Heavy Machine Gun sweep). Huntdown is horizontal-only. Free 360° appears in twin-stick hybrids (Velocity 2X with 64 drawn angles) and rigs (Spineboy). Five drawn angles mirrored left/right give all 8 digital directions.

### Cited Findings
- Contra: 8-way joystick. Standing fire is limited to left/right/up, running adds diagonals, and the air allows all 8 including down — [Wikipedia: Contra](https://en.wikipedia.org/wiki/Contra_(video_game))
- Metal Slug: the player "can shoot straight up or down" but "cannot be fired in diagonal directions" — [Sega Retro](https://segaretro.org/Metal_Slug). The Heavy Machine Gun "is the only weapon that can fire diagonally prior to Metal Slug 6" (community wiki) — [Metal Slug Wiki: Weapons](https://metalslug.fandom.com/wiki/Weapons). From Metal Slug 6 the Laser Gun can travel diagonally at 45° — [Metal Slug Wiki: Laser Gun](https://metalslug.fandom.com/wiki/Laser_Gun)
- Metal Slug HMG diagonal fire happens when you swap from left/right to up and back (a sweep through the transition), per a player comment on Metal Slug 5 (community) — [RetroAchievements comments](https://retroachievements.org/game/20599/comments). An editorial calls the limited aiming an intentional design choice that makes it feel closer to a shoot-'em-up (community) — [Gaming Hell](https://www.gaminghell.co.uk/MetalSlug.html)
- Gunstar Heroes: the player picks "free" (move while firing) or "fixed" (stand still) shot at the start — [Wikipedia: Gunstar Heroes](https://en.wikipedia.org/wiki/Gunstar_Heroes). Fixed lets you "aim in eight directions" — [Co-Optimus review](https://www.co-optimus.com/review/237/Gunstar_Heroes.html). Sega-16 says the original used a 360-degree system in some modes, and the GBA remake reduced it to eight-way, "a disappointment" to the writer — [Sega-16](https://www.sega-16.com/?p=14193)
- Cuphead: lock button for 8-way directional shooting — [TrueAchievements](https://www.trueachievements.com/game/Cuphead/walkthrough/2); [Giant Bomb user review](https://giantbomb.com/user-reviews/id/363/cuphead-xbox-one-thoughts)
- Valfaris: "Aiming is restricted to eight directions via the D-pad". The reviewer found it awkward on Joy-Cons and suggests twin-stick would be better — [Pure Nintendo review](https://purenintendo.com/review-valfaris-nintendo-switch/)
- Blazing Chrome: has a remappable lock-aim button — [Seafoam Gaming review](https://seafoamgaming.com/2019/11/25/blazing-chrome-steam-review/)
- Huntdown: "You only have to worry about shooting (and being shot at) on a horizontal plane, without anything coming from above, below or diagonally". Cover and crouch replace aim angles — [TheSixthAxis review](https://www.thesixthaxis.com/?p=355778)
- Velocity 2X: 64 drawn aim frames for full 360° fire — [80.lv](https://80.lv/articles/the-animation-system-of-velocity-2x/)
- Snapping implementation: one Unity answer maps input into eight 45° sectors, of which only five are valid facings (right, up-right, up, up-left, left). It keeps the last valid direction when input is "None" (community) — [Unity Discussions](https://discussions.unity.com/t/what-technique-code-is-needed-for-contra-style-aiming/89843)
- Mirroring math for directional sprites: a vendor tool renders 5 directions and mirrors 3, claiming 37.5% less generation cost (vendor; top-down facing, same arithmetic) — [PerfectPixel](https://pp.andrew-ai.app/)

### Inferences
- With 5 drawn angles (0°, +45°, +90°, −45°, −90°) mirrored horizontally, all 8 digital directions are covered exactly (own calculation: 5 + 3 mirrored = 8, since up and down are shared). No interpolation is needed for 8-way digital input.
- For analog sticks with 5 drawn angles, snap the drawn pose to the nearest 45° and fire the bullet along the same snapped angle. Keeping the bullet and barrel on the same line is what reads; a bullet at 30° leaving a 45° barrel does not (inference). Velocity's 64 angles show what true free aim costs.
- A Metal Slug-style sweep (bullets during a forward→up transition taking intermediate angles) gives "diagonal" fire with only 2–3 drawn torso angles plus 2–4 transition frames (inference from the cited mechanic). It suits a heavy MG whose fantasy is spraying.
- For the comando, 3 drawn angles (0°, +45°, +90°) plus air-only down, or 5 angles, match genre norms. 8+ drawn angles are only justified if the design moves to twin-stick (inference).

### Gaps
- No player-research data (playtests, telemetry) found on how many angles players use or need.
- No developer source on analog-to-digital deadzones or snapping thresholds used in Cuphead, Contra reboots or Blazing Chrome.

---

## 3. Stance, silhouette, hitbox width and platform-edge conventions

### Takeaway
Shipped platformers keep the collision box narrow and fixed (Celeste's Madeline: 8 px wide). They handle "feet over the edge" with an edge/teeter animation that triggers when ground is missing under the front of the body (Celeste) or under the centre sensor (Sonic), rather than by widening the collider. A stance much wider than the collider (the comando's 90 px vs 44 px) guarantees floating feet near edges.

### Cited Findings
- Celeste `Player.cs`: `normalHitbox = new Hitbox(8, 11, -4, -11)`, `duckHitbox = new Hitbox(8, 6, -4, -6)`, `normalHurtbox = new Hitbox(8, 9, -4, -11)`, `duckHurtbox = new Hitbox(8, 4, -4, -6)`. The collider is 8 px wide and centred on the feet origin (±4 px). The hurtbox is 2 px shorter than the collider (forgiveness) — [Celeste source, Player.cs](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs)
- Celeste edge animation: when idle on the ground, if there is no Solid at (facing × 1 px, +2 px down) and none at (facing × 4 px, +2 px down), and no JumpThru at 4 px, it plays `PlayerSprite.FrontEdge`. The mirrored check behind plays `"edgeBack"`. The 4 px probe is the collider's half-width, so the front-edge pose triggers once the whole front half of the collider is over air — [Celeste source, Player.cs](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs)
- Celeste forgiveness constants: `JumpGraceTime = 0.1f` (coyote time), `UpwardCornerCorrection = 4`, `DashCornerCorrection = 4` — [Celeste source, Player.cs](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs)
- Sonic-style balancing (fan-engine devlog modelled on the classic games): "an extra ground sensor for ledge balancing on the absolute middle of the character". "If one of the 'normal' ground sensors isn't colliding with the floor, and the ledge sensor isn't colliding either, then it is balancing time!" The animation leans forward or backward depending on facing (community, devlog for v0.1 demo, Apr 2025) — [Sonic XA devlog](https://luksamuk.itch.io/sonic-the-hedgehog-xa/devlog/976431/better-late-then-never-presenting-v01-demo)
- The same two-sensor rule appears elsewhere: if only one foot sensor touches ground, play the balancing animation (community) — [BatteryCheck blog](https://gbatemp.net/blogs/batterycheck-collision-detection-is-finally-improving.15654/). A Unity reimplementation lists ledge balancing as a feature — [UniSonic](https://github.com/Giometric/UniSonic)
- Two raycasts at the collider's bottom corners: both hit means solid ground, one hit means on a ledge (community) — [Godot forum](https://forum.godotengine.org/t/detect-if-one-of-players-foot-is-on-ledge/17481). Box2D practice uses a separate foot sensor fixture for ground checks — [Phaser Box2D tutorial](https://phaser.io/tutorials/box2d-tutorials/can-i-jump)
- Pitfall: a hitbox that changes size per animation caused the character to flicker at platform edges. The fix was a fixed collision rectangle with the art following it (community) — [GDevelop forum](https://forum.gdevelop.io/t/animation-flickering-on-edge-of-platform/32562)
- Why not match the box to the art: AABBs overshoot sprites with transparent corners, so the hero "appears to float" or stick to air (community doc) — [zx-kit collision notes](https://raw.githubusercontent.com/zrebec/zx-kit/HEAD/docs/collision.md)
- Level design metrics: a Super Mario World analysis measures jumps in blocks (about 4 blocks up without momentum, about 6 with). It tracks delta height, delta width and lateral "d-distance", and notes platforms were kept under 10 blocks long — [Game Design Forum: SMW](https://www.quaddicted.com/webarchive/thegamedesignforum.com_20160521/features/RD_SMW_3.html)

### Inferences
- Comando geometry (own calculation): stance 90 px centred on a 44 px collider means each foot extends (90 − 44) / 2 = 23 px past the collider edge. The player stays supported while ≥1 px of collider overlaps the crate, so the centre can be up to 21 px past the ledge. At that point about 66 of the 90 px of stance (73%) is over air. Even at "centre exactly on the edge", the whole front foot (45 px from centre) is in the air.
- Rule from Celeste, scaled (inference): Celeste uses an 8 px wide collider (width:height 8:11) and solves edges with a teeter animation rather than a wider box. Madeline's drawn stance width was not measured here. For the comando, the outer edges of both feet in idle/aim-stand should sit within the collider plus at most about 10% (≤ about 48 px at 1x for a 44 px collider). The wide "action stance" can live in transient poses (landing, firing recoil) rather than the loop the player sees most.
- Teeter rule translated to the comando (inference from Celeste code): when idle, probe ground at centre + 1 px and centre + 22 px (half-width) toward facing. If both miss, play a front-edge teeter. Do the same behind for a back-edge teeter. This yields 2 extra short loops (front and back), each generatable as one Seedance clip from the narrow-stance start pose.
- Minimum platform width (inference; no published standard found): the smallest standable crate should be ≥ the redesigned stance width (≥ about 48 px), and ideally ≥ 1.5 × collider (about 66 px), so a centred landing shows both feet on the surface.
- Silhouette (inference): a narrow A-stance reads well if the gun and upper body carry the width. The MG barrel extending forward gives the "heavy" silhouette without widening the feet.

### Gaps
- The Sonic Physics Guide (Sonic Retro) page on balancing could not be read (bot protection). The balancing details above come from fan-engine devlogs that reimplement it, not from the SPG text.
- Madeline's drawn sprite width could not be sourced, so no exact sprite-to-hitbox width ratio for Celeste.
- No published level-design rule of thumb was found for minimum platform width relative to character or collider width.

---

## 4. Gun posture conventions: horizontal barrel, low ready vs level fire, barrel/bullet alignment, recoil

### Takeaway
I found no authoritative written convention about "barrel exactly horizontal" or "low ready" in 2D shooters. The cited practice (per-angle muzzle points, kick along the barrel axis, one-frame muzzle flash at the muzzle) implies the forward pose must be level so bullets visibly leave on the barrel line. Treat the rules in this section as inference grounded in those mechanics.

### Cited Findings
- Muzzle/bullet spawn must exist per animation × angle. A missing animation made bullets spawn from the wrong image point (community) — [Construct forum: 8-direction shooting problem](https://www.construct.net/en/forum/construct-2/how-do-i-18/direction-shooting-problem-128372)
- Spine stores spawn positions as point attachments on bones ("different guns may shoot from different positions") (vendor) — [Spine: Point attachments](https://esotericsoftware.com/spine-points)
- Nuclear Throne: weapon kick pushes the gun sprite back a little, then it "super quickly slides back into place". The camera is kicked back from the aim direction. The bullet's first frame is circular to fake a muzzle flash at the muzzle — [infovore.org](https://infovore.org/?p=5275)
- A fan recreation of the Art of Screenshake lists: increased fire rate, bigger bullets, muzzle flash, faster bullets, lower accuracy, camera lerp, hit pause and weapon recoil (community) — [DK Liao devlog](https://dkliao.itch.io/the-art-of-screenshake-recreation/devlog/451576/quick-breakdown-of-all-the-effects)
- Pixel-art advice: if only one thing animates, a shot looks weak, so add recoil to the weapon or character (community) — [Steam/Aseprite forum](https://steamcommunity.com/app/431730/discussions/0/3274687384246030962)

### Inferences
- Barrel error (own calculation): a 5° downward tilt over a gun about 60 px long (assumed at 1x) is a 60 × tan 5° ≈ 5.2 px drop along the gun. Over 300 px of bullet travel, the barrel line and a horizontal bullet line diverge by 300 × tan 5° ≈ 26 px. That is clearly visible at 128 px character scale.
- Convention to adopt (inference): in every firing pose the barrel axis should match the bullet direction within about 1° (≤1 px over the gun length), with the muzzle point stored per frame. Fix the art rather than tilting bullets to −5°, because run-and-gun levels assume horizontal fire.
- Recoil (inference from the Nuclear Throne mechanic): kick the gun and upper body back along the barrel axis (translation, not rotation), 2–4 px at 1x, recovering in 1–2 frames at 12 fps. Any rotational climb should return to the exact level line before the next shot. AI-generated fire loops should be QA'd for barrel angle per frame.
- Low ready vs level (inference): a lowered idle (gun angled 10–20° down at the hip) adds attitude but costs reaction frames. At 12 fps, raise-to-level should take ≤1–2 frames (83–167 ms), or the idle should simply hold the level firing pose. Contra and Metal Slug idles appear to keep the weapon level, but this was not verified in a source.
- QA hook for spritepipe (inference): fit a line to the barrel pixels per frame (or template-match the muzzle tip) to report barrel angle and muzzle (x, y). Reject frames outside ±1° for the forward set and store muzzle points in the atlas metadata.

### Gaps
- No animator tutorial (Saint11, Brandon James Greer, Slynyrd) on shooting poses, low ready or barrel alignment was found in this pass. Saint11's tutorial set exists but no gun-specific lesson surfaced.
- No GDC talk or postmortem found that states a "level barrel" rule explicitly.

---

## 5. AI pipeline evidence (as of October 2026): consistent multi-angle sets with image-to-video or image-editing models

### Takeaway
Seedance 2.0 supports first-frame and first+last-frame image-to-video at 24 fps, roughly 4–12/15 s (hosts disagree), and 480p–1080p/4K. The base rate card is about $0.07/s at 480p and $0.15/s at 720p via BytePlus-derived listings, or about $0.30/s at 720p on fal.ai. Community evidence for aim sets specifically is thin. The documented patterns are "one turnaround/sweep video then pick frames" (smooth, same identity, but jittery and angle-inexact) vs. "separate stills or clips per angle" (exact poses but identity drift between generations). First/last-frame control is the main tool for hitting exact end poses.

### Cited Findings
**Seedance 2.0 capabilities (as of Oct 2026)**
- BytePlus ModelArk docs (vendor; page "Last updated: September 29, 2026") list Seedance 2.0 model IDs `dreamina-seedance-2-0-260128` and `dreamina-seedance-2-0-fast-260128`, with modes text-to-video, image-to-video (first frame), image-to-video (first and last frames) and multimodal reference-to-video. Image URLs must be publicly reachable. Mode list and IDs come from the search snippet; the page body did not render in my fetch — [BytePlus ModelArk docs](https://docs.byteplus.com/docs/ModelArk/2291680)
- fal.ai (vendor/host, accessed 2026-10-15, no page date): `image_url` (start) plus optional `end_image_url` (end). Duration `auto` or 4–15 s. Resolution 480p/720p/1080p. Aspect ratios auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16. Optional `seed`. Audio included at the same price — [fal.ai Seedance 2.0 I2V](https://fal.ai/models/bytedance/seedance-2.0/image-to-video). When both images are given, "the model generates motion that transitions from the first frame to the second" — [fal.ai explore](https://fal.ai/explore/image-to-video-apis)
- Cloudflare Workers AI listing (vendor/host, undated): duration 4–12 s (default 5). Resolution 480p/720p/1080p/4k. fps fixed at 24. `camera_fixed` flag. `last_frame_image` "only works if an image start frame is also given". `reference_images` takes 1–4 images and "Cannot be used with 1080p resolution or first/last frame images". Its description says "up to 9 images, 3 videos, 3 audio files", which contradicts its own parameter list — [Cloudflare: Seedance 2.0](https://developers.cloudflare.com/ai/models/bytedance/seedance-2.0/index.md)
- A ComfyUI wrapper node exposes `first_frame_image`, `last_frame_image` and `reference_image_1`…`_9` (community wrapper) — [comfy.icu node](https://comfy.icu/node/ModelArk-Seedance-2-0). OpenRouter lists 480p/720p and 4–15 s (vendor; search snippet) — [OpenRouter](https://openrouter.ai/bytedance/seedance-2.0)
- The official ByteDance Seed page states only general capabilities ("supports text, image, audio, and video inputs", "exceptional motion stability"). No limits are given — [ByteDance Seed](https://seed.bytedance.com/en/seedance2_0)

**Seedance 2.0 pricing (no official rate card could be fetched; sources conflict)**
- BytePlus-hosted article (dated 22 Jul 2026; its footer says the content was "intelligently generated through AI tools", so it is not an official rate card): Seedance 2.0 at $0.07/s (480p), $0.15/s (720p), $0.37/s (1080p), $0.78/s (4K). Fast at $0.06/$0.12 (480p/720p only). Mini at $0.04/$0.08 — [BytePlus topic page](https://www.byteplus.com/en/topic/578667). The BytePlus pricing doc shows "Last updated: October 8, 2026" but its table did not render — [BytePlus pricing doc](https://docs.byteplus.com/en/docs/ModelArk/1544106)
- Cloudflare (vendor) lists the same non-video-input rates ($0.07/$0.15/$0.37/$0.78 per s) and higher rates when a video is used as input (480p $0.172, 720p $0.372, 1080p $0.914, 4K $1.866) — [Cloudflare](https://developers.cloudflare.com/ai/models/bytedance/seedance-2.0/index.md)
- Per-token: $7.00 per million tokens at 480p/720p without video input ($4.30 with video input). Tokens = width × height × 24 × duration / 1024 — [dev.to analysis](https://dev.to/lee_315dd1e13420e63e2b813/seedance-25-is-priced-53-above-20-per-token-and-its-480p-frame-shrank-5fki); [Segmind (vendor)](https://www.segmind.com/models/seedance-2.0/pricing); token formula also on [fal.ai](https://fal.ai/models/bytedance/seedance-2.0/image-to-video)
- fal.ai (vendor) charges more: Standard $0.3024/s at 720p in the docs ($0.3034 in the playground), $0.682/s at 1080p, Fast $0.2419/s (720p max). That equals $0.014 per 1,000 tokens. A 10 s Standard clip is about $3.02 — [fal.ai](https://fal.ai/models/bytedance/seedance-2.0/image-to-video)
- Seedance 2.5 is listed by resellers as of Oct 2026 (not evaluated here) — [Pika listing](https://dev.pika.art/models/bytedance/seedance-2.5/text-to-video/pricing)

**Other first/last-frame models**
- Veo 3.1 (Gemini API, official; model table shows Veo 3.1 Preview updated Jan 2026, Lite Mar 2026): `lastFrame` is "The final image for an interpolation video to transition. Must be used in combination with the `image` parameter". `referenceImages` takes "Up to three images" (asset type), Veo 3.1/Fast only. Duration 4/6/8 s, and must be 8 s when using reference images, 1080p or 4k. 24 fps. 16:9 or 9:16 — [Google AI: Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- Kling O1: first-and-last-frame control and up to 10 reference images (third-party blog) — [MindStudio](https://www.mindstudio.ai/blog/what-is-kling-o1-video-generation)

**Sweep/turnaround vs per-angle generation, and drift**
- Turnaround-video workflow: animate a plain front view with a "3D model turnaround" prompt at low motion, then scrub and save the frames you want. A half turnaround "may result in cleaner details if the character is symmetrical". Results can be "a little more 'Jittery'" (community guide, last edited 3/12/2026) — [Midjourney video reference-sheet guide](https://prompt-faqs.notion.site/Create-Character-Reference-Sheets-with-Midjourney-Video-299024c0a17e812f9aa9f2a6ae27ca3c)
- Stills route: a ComfyUI "360 Full-body Turnaround" template uses a Gemini image node to generate the angle views and stitches them, avoiding video extraction (community template) — [Comfy.org template](https://comfy.org/workflows/templates-character_sheet-c70904777c65/)
- Handheld props break multi-angle sheets. invideo recommends removing props before generating the sheet, and says video models reproduce only what the sheet shows (vendor) — [invideo: props](https://invideo.io/faq/whats-the-best-way-to-handle-props-or-handheld-objects/); [invideo: turnaround](https://invideo.io/faq/how-do-you-create-a-multi-angle-character-turnaround/)
- Drift order across generations: faces drift first (hairline, jaw, ears), then outfits at stitching, layering and small accessories, while silhouette holds longest (practitioner blog) — [FilmDaft](https://filmdaft.com/character-consistency-in-ai-video-workflows/). In a vendor's own five-generation test, more reference images reduced drift (vendor) — [Vidu blog](https://www.vidu.com/en/blog/ai-character-generator-for-video)
- Indie reports: generating sprite sheets directly gave inconsistent motion and unstable style. Generating short videos (e.g., Veo 3) and extracting frames solved motion continuity but still needed frame cleanup (community) — [itch.io thread](https://itch.io/post/14144159/view-in-topic)
- Vendor tools now re-target an animation to a new facing from a turned first frame (Ludo "New Direction"), with unbenchmarked consistency claims (vendor) — [Ludo.ai](https://ludo.ai/features/sprite-generator)

**Splitting AI frames into layers / rigging AI parts**
- SAM 2 (Meta): a single click, box or mask on one frame propagates a mask through the video using a memory of earlier frames, even through deformation or brief occlusion (secondary explainers, not Meta's paper) — [DataCamp](https://www.datacamp.com/blog/sam2-meta-segment-anything-model); [Voxel51](https://voxel51.com/glossary/sam-2-segment-anything-model-2)
- Qwen-Image-Layered (arXiv 2512.15603, Dec 2025) decomposes one RGB image into multiple semantically separated RGBA layers that can be moved or resized independently. It is trained on layers extracted from PSD files — [arXiv](https://arxiv.org/html/2512.15603v1); [GitHub](https://github.com/QwenLM/Qwen-Image-Layered)

### Inferences
- Team's resolution and cost (own calculation): 864 × 496 is Seedance's 480p 16:9 frame. Tokens/s = 864 × 496 × 24 / 1024 ≈ 10,044, so $7/M tokens is about $0.070/s. That is about $0.35 for a 5 s clip and $0.70 for 10 s, matching the $0.07/s rate card. On fal at $0.014/1k tokens the same clip costs about 2× more ($0.14/s at 480p). Generation cost is negligible next to cleanup labour.
- Recommended aim-set workflow (inference):
  1. Fix the base pose first (narrow stance, level barrel at chest height).
  2. Generate one "sweep" clip per direction with the start frame = forward pose and the end frame = up pose (edited start-pose still), camera fixed and legs planted. Sample frames nearest 45° and 90° as torso keys, so identity stays consistent because it is a single generation.
  3. For each angle, generate a hold/fire loop clip with first frame = last frame = that sampled key, which closes the loop for spritepipe.
  Use separate per-angle clips only from edited stills derived from the same master, and expect accessory drift (ammo belts, headband) between clips.
- The Cloudflare constraint "reference images cannot be combined with first/last frames" (if it holds on BytePlus) means the master image cannot be both an identity reference and a pinned start pose. Identity must come from the start and end frames themselves, which argues for producing all angle start poses by editing one master (inference).
- Torso/legs split of AI frames (inference): SAM 2 can propagate a "legs" mask through a run clip. However, the frames contain no pixels for what the torso layer occludes (pelvis behind the hip-held gun, back thigh behind the front leg). Every leg frame needs an overlap margin painted or inpainted above the cut, which Velocity solved with authored "overlap values". A belt or ammo bandolier at the cut hides the seam. With the gun at hip height, the cut must go around the gun and hands, so moving the gun to chest height simplifies segmentation.
- Torso bob for split run (inference): Velocity hard-coded per-frame torso offsets. spritepipe could derive them automatically by tracking the belt/pelvis anchor in the full-body run clip and storing a per-leg-frame (dx, dy) in the atlas metadata.
- Spine on AI parts (inference): decompose the master (Qwen-Image-Layered or manual masks), inpaint hidden regions, rig gun + both arms with an aim IK like Spineboy, and mark the muzzle with a point attachment. This gives the most consistent free aim but drops AI-video motion; locomotion would be animated by hand in Spine.

### Gaps
- No official BytePlus/Volcengine page with Seedance 2.0 limits and prices rendered in my fetches. Duration max is reported as 15 s (fal, OpenRouter) vs 12 s (Cloudflare). Resolution ceiling varies by host.
- No community workflow found (Reddit r/aigamedev, r/StableDiffusion, LayrKits) that specifically builds run-and-gun aim-angle sets with video models. Reddit was not reached by search.
- No quantitative study of identity drift across separate image-to-video generations.
- No documented case of SAM 2 used to split AI sprite frames into torso and legs for a game, and no Spine/DragonBones pipeline built on AI-generated parts.

---

## 6. Concrete clip counts (own calculation), approach comparison and design rules

### Takeaway
For the same coverage, split body needs roughly half the AI clips of full-body-per-angle (14 vs 25 at 5 angles), and fewer still if fire is procedural recoil. It trades clip count for seam, sync and bob-offset work. A rotating gun piece or Spine rig needs the fewest clips but fits a two-handed hip-held MG poorly unless the base pose is redesigned.

### Cited Findings
- Full-body frame count scales as angles × frames per state (Velocity: 64 × 30 = 1,920 for running alone, >9,000 for five states). Split frames scale as angles + legs (>1,000 drawn frames giving >10,000 combinations) — [80.lv / Velocity 2X](https://80.lv/articles/the-animation-system-of-velocity-2x/)
- Contra validity per state (stand: L/R/up; run: horizontal plus diagonals; air: all 8 hidden in a somersault; prone) reduces the needed set — [Wikipedia: Contra](https://en.wikipedia.org/wiki/Contra_(video_game))
- Clip cost at 480p is about $0.07/s (rate-card listings) and about $0.30/s at 720p on fal — [BytePlus topic page](https://www.byteplus.com/en/topic/578667); [fal.ai](https://fal.ai/models/bytedance/seedance-2.0/image-to-video)

### Inferences
**Definitions (own calculation).**
- Locomotion states L = {stand, run, air, crouch} (4).
- N = distinct drawn angles per facing, mirrored for the other side:
  - N=3: 0°, +45°, +90°
  - N=5: 0°, ±45°, ±90°
  - N=8: 0°, ±22.5°, ±45°, +67.5°, ±90°
- One "clip" = one successful Seedance generation that yields one loop or one-shot animation.
- Transitions, turns, landing, hurt and death are excluded.

**(b) Full sprite per angle**, clips = N × 4 (aim loop per state) + N (stand fire loop):

| N | All angles in all states | Contra-style validity* |
|---|---|---|
| 3 | 3×4 + 3 = **15** | stand 3 + run 2 + air 3 + crouch 1 + fire 3 = **12** |
| 5 | 5×4 + 5 = **25** | stand 3 + run 3 + air 5 + crouch 1 + fire 3 = **15** |
| 8 | 8×4 + 8 = **40** | stand 5 + run 5 + air 8 + crouch 2 + fire 5 = **25** |

\*Validity assumptions: stand allows angles ≥ 0°, run excludes ±90°, air allows all, crouch allows 0° (and +22.5° at N=8), and fire loops are only for stand angles. If the air state uses a somersault/tuck (Contra), the air row drops to 1 clip.

**(a) Split body**, clips = M leg clips (stand, run, air, crouch = 4) + N × T torso clips (T = 2: hold + fire loop; T = 1 if fire is procedural kick plus muzzle flash):

| N | T = 2 | T = 1 | Sweep variant: 4 legs + 2 sweeps (0→+90, 0→−90) + N fire loops |
|---|---|---|---|
| 3 | 4 + 6 = **10** | **7** | 4 + 1 + 3 = **8** |
| 5 | 4 + 10 = **14** | **9** | 4 + 2 + 5 = **11** |
| 8 | 4 + 16 = **20** | **12** | 4 + 2 + 8 = **14** |

Existing idle, run and jump clips could in principle supply leg layers, but a stance redesign invalidates them, so count them as new.

**(c) Rotating arm/gun or rig.** About 4 body clips (one per locomotion state, gun and arms removed or neutral) plus 1 gun+forearms still (+1 optional recoil clip), so **5–6 clips at any N**. Free 360° comes from rotation. A Spine rig needs 0–4 AI clips, used only as motion reference, plus part decomposition and rigging labour.

**Frames at 12 fps (own calculation).** Run aim coverage at N=5:
- Full-body: 5 × 15 = **75 run frames**.
- Split: 15 leg frames + 5 torso keys (static torso per angle, with per-frame bob offset), or 15 + 5 × 8 = 55 if each angle gets an 8-frame torso sway loop.

**Retake cost example (own calculation; the 3× retake factor is an assumption).** 25 clips × 3 takes × 5 s = 375 s, which is about $26 at $0.07/s (480p) or about $113 at fal's $0.3024/s (720p).

### Gaps
- Real retake/usable-take rates for Seedance on this character are unknown; use the team's pilot data.
- No shipped-game data on frames per aim state for Metal Slug, Contra or Cuphead to calibrate the counts against.

### (a) Comparison table of the three construction approaches

| | (a) Split body (torso + legs layers) | (b) Full-body sprite per angle | (c) Rotating arm/gun piece or skeletal rig |
|---|---|---|---|
| AI clips needed (own calculation, N = 3/5/8) | 10/14/20 (T=2); 7/9/12 (procedural fire); sweep variant 8/11/14 | 15/25/40 (all states); 12/15/25 (Contra-style validity) | ~5–6 clips at any N; rig: 0–4 reference clips + part decomposition |
| Frames scale as | legs + angles (Velocity: >1,000 drawn → >10,000 combos) [80.lv](https://80.lv/articles/the-animation-system-of-velocity-2x/) | angles × frames per state (Velocity: 64 × 30 = 1,920 for running alone) [80.lv](https://80.lv/articles/the-animation-system-of-velocity-2x/) | constant body frames + 1 rotating piece |
| Consistency risk with AI video | Medium: torso angles from 1–2 sweep generations stay consistent; legs and torso come from different clips (lighting/scale mismatch); accessory drift at the seam (inference; drift pattern per [FilmDaft](https://filmdaft.com/character-consistency-in-ai-video-workflows/)) | High: every state × angle is a separate generation, so face and accessory drift between clips is visible when switching aim (inference) | Low for the gun piece (one still); medium for body clips; lowest for a Spine rig (single master) (inference) |
| Seam / joint risk | High: waist cut, occluded pelvis needs inpainting, hip-held gun crosses the cut, per-frame bob offsets needed ([80.lv](https://80.lv/articles/the-animation-system-of-velocity-2x/)) | None | High for two-handed MG: both arms and shoulders must follow; a hip pivot past about 30° looks wrong (inference); shoulder-anchored pivots per [Godot forum](https://forum.godotengine.org/t/help-pivoting-arm-to-follow-the-mouse-aim/80147) |
| Runtime complexity | Two synced state machines, offset table, z-order rules ([Godot Q&A](https://ask.godotengine.org/142455/synchronizing-multiple-animationnodestatemachine)) | Simple: one state machine, muzzle point per frame ([Construct](https://www.construct.net/en/forum/construct-2/how-do-i-18/direction-shooting-problem-128372)) | Simple rotation plus flip ([Godot Q&A](https://godotengine.org/qa/111824/sprites-rotation-degrees-when-passes-certain-rotation-degree)); Spine runtime with IK on track 1 ([Spine](https://eu.esotericsoftware.com/spine-examples-spineboy.md)) |
| Muzzle data | Per torso frame × angle | Per frame × state × angle | Fixed offset rotated by aim angle; Spine point attachment ([Spine](https://esotericsoftware.com/spine-points)) |
| Aim resolution | Drawn angles only (e.g., 5 → 8-way with mirroring) | Drawn angles only | Free 360° |
| Examples | Velocity 2X; Metal Slug-style packs (community claim for Metal Slug and Contra) | Contra, Cuphead (8-way lock), Valfaris | Nuclear Throne (separate gun sprite); Spineboy (IK aim) |

### (b) Design rules for stance width, gun angle and hitbox (inference unless cited)
1. **Collider fixed and narrow.** Keep one constant collision rectangle across all animations; size changes cause edge flicker ([GDevelop](https://forum.gdevelop.io/t/animation-flickering-on-edge-of-platform/32562)). Keep it centred on the feet origin like Celeste's ±4 px box ([Celeste](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs)). Keep 44 px for the comando.
2. **Stance ≤ collider + 10% in looped grounded poses.** Idle, aim-stand and fire-stand outer foot edges should span ≤ about 48 px at 1x (vs. 90 px now). Put wide stances only in transient frames (landing, big recoil). Run cycles may extend further because they are not seen at ledges at rest.
3. **Edge teeter, front and back.** When idle, if no ground is found at centre + 1 px and at centre + half-width (22 px) toward facing, play the front-edge teeter, and the mirrored check plays the back-edge teeter (Celeste's FrontEdge/edgeBack logic: [Player.cs](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs); Sonic's centre sensor: [Sonic XA devlog](https://luksamuk.itch.io/sonic-the-hedgehog-xa/devlog/976431/better-late-then-never-presenting-v01-demo)). That is 2 short AI clips from the narrow-stance pose.
4. **Hurtbox smaller than collider.** Mirror Celeste's 8×9 hurtbox inside the 8×11 collider ([Player.cs](https://github.com/NoelFB/Celeste/blob/master/Source/Player/Player.cs)). Shrink the hurtbox a few px from the top and sides, and exclude the gun barrel from both boxes.
5. **Smallest standable platform ≥ stance width** (≥ about 48 px after redesign), ideally ≥ 1.5 × collider (about 66 px). Crates narrower than the collider should be avoided or treated as teeter-only perches.
6. **Level barrel in every forward firing frame.** Barrel axis within ±1° of horizontal (≤1 px over the gun length); the current 5° tilt is a 26 px mismatch over 300 px of bullet travel (own calculation). Fix it in the base pose rather than angling bullets.
7. **Barrel = bullet line at every drawn angle.** Store a muzzle point (x, y) and the angle per frame per state in the atlas metadata ([Construct](https://www.construct.net/en/forum/construct-2/how-do-i-18/direction-shooting-problem-128372); [Spine points](https://esotericsoftware.com/spine-points)). Snap analog input to the drawn angle and fire along the snapped angle ([Unity](https://discussions.unity.com/t/what-technique-code-is-needed-for-contra-style-aiming/89843)).
8. **Recoil along the barrel axis.** Kick back 2–4 px and return in 1–2 frames at 12 fps (pattern from [Nuclear Throne writeup](https://infovore.org/?p=5275)), with a one-frame muzzle flash at the muzzle point. Any rotational climb must return to the level line before the next shot.
9. **Move the MG from hip to chest/shoulder height in the redesigned base pose.** Hands, stock and gun should sit above the belt line. This enables a clean waist cut for split-body ([Velocity's waist rule](https://80.lv/articles/the-animation-system-of-velocity-2x/)) and natural raising to +45°/+90°. Keep a visible belt or bandolier at the cut line.
10. **Angle set.** Draw 5 angles (0°, ±45°, ±90°) mirrored for 8-way, with −90° and −45° used mainly in air. Alternatively draw 3 (0°, +45°, +90°) plus a Contra-style tuck jump that hides aim ([Contra](https://en.wikipedia.org/wiki/Contra_(video_game))). Consider a Metal Slug-like sweep (bullets follow transition frames) as the heavy-MG flourish ([Metal Slug Wiki](https://metalslug.fandom.com/wiki/Weapons)).
11. **Generate angle keys from one sweep clip**, using first frame = forward and last frame = up, both edited from the same master. Then generate per-angle loops with first = last = the key frame. Avoid mixing reference images with first/last frames where the host forbids it ([Cloudflare](https://developers.cloudflare.com/ai/models/bytedance/seedance-2.0/index.md)).
