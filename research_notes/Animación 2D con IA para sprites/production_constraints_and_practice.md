# Production constraints, real-world practice, costs, and legal/market risk for AI-generated 2D sprite animation (as of 15 Oct 2026)

Scope: production targets (frame counts, fps, resolutions, animation lists), consistency practice, real AI sprite case studies, cost per character, legal terms and copyright, storefront disclosure rules, and player/industry reception. The other notes in this folder cover the video models themselves, the video-to-sprite post-processing pipeline, dedicated sprite tools, and alternatives (Spine/ComfyUI/Mixamo). None of this is legal advice. Legal points are US-centric unless marked. Dates are given wherever a source shows one. Items marked "secondary" or "vendor" come from aggregators or tool sellers, not primary sources.

---

## 1. Frame counts and fps by animation type (pixel art vs HD/hand-drawn)

### Takeaway
Pixel art usually plays at about 8–12 fps with small loops: idle 2–4 frames, walk 4–8, run 6–8, attack 4–6, hurt 1–2, death about 5. Hand-drawn HD games draw far more frames. Cuphead animates at 24 fps "on ones" (24 drawings per second), and Skullgirls averages about 1,300 frames per character. Most hand-drawn 2D falls between those, around 12 drawings per second ("on twos"). Timing (how long each frame is held) matters more than raw frame count. That helps an AI pipeline: a video model produces around 24 fps, and you only need to pick a few key frames from it.

### Cited Findings
**Pixel art: practitioner and educator sources**
- Raymond Schlitter (Slynyrd), *Pixelblog 50: Human Walk Cycle* (24 May 2024), cut a side-view walk built from video reference down to an **8-frame loop**. He calls 8 frames the balance between economy and smoothness, and says "size, details, and frame count must be carefully considered in terms of time cost" when designing animated characters — [Slynyrd Pixelblog 50](https://slynyrd.com/blog/2024/5/24/pixelblog-50-human-walk-cycle)
- Slynyrd's *Pixelblog 8: Intro to Animation* (19 Aug 2018) notes that 8-bit JRPGs commonly reuse a **2-frame walk cycle as the idle** — [Slynyrd Pixelblog 8](https://slynyrd.com/blog/2018/8/19/pixelblog-8-intro-to-animation)
- Slynyrd's "Elona Run Cycle" is **12 frames**, but he says most pixel-art games "can get away with a more economical sequence of **8 or 6 frames**" — [Slynyrd Patreon](https://www.patreon.com/posts/20778494)
- Pedro Medeiros (Saint11; art director of Celeste and TowerFall at Miniboss) publishes GIF tutorials on running, attack animation, and other topics. The archive is the standard reference, but my searches did not surface specific frame-count numbers from it — [Miniboss pixel art tutorials](https://blog.studiominiboss.com/pixelart); [Creative Bloq on the series](https://creativebloq.com/news/artist-makes-animated-gif-tutorials-to-teach-you-pixel-art)
- General pixel-art guides (secondary, partly vendor):
  - The usual range is **8–12 fps**. Slow motion can drop to 4–6 fps and fast attack effects can go to 15–24 fps.
  - Typical counts: idle 2–4 frames (long holds), walk 4–6 ("a 4-frame walk cycle looks perfectly acceptable in most 2D games"), run about 6, attack 4–6 (wind-up, swing/strike, contact, follow-through, recovery), hurt 2, death about 5, jump 3 (anticipation, air, landing).
  - "Four frames can feel like twelve with uneven hold times." Hold the impact frame longer and keep the wind-up short.
  - [Pixnote animation basics](https://pixnote.net/en/learn/animation); [Sprite-AI guide (vendor)](https://www.sprite-ai.art/guides/how-to-animate-pixel-art); [Divoom fps article](https://divoom.com/blogs/setup-ideas/pixel-art-animation-frame-rate)
- The same guides warn that a 12-frame hand-made walk "often looks worse than a 4-frame one" because inconsistencies between frames become more visible. They also advise keeping frame counts consistent across a character's animations — [Sprite-AI guide (vendor)](https://www.sprite-ai.art/guides/how-to-animate-pixel-art)

**Traditional timing (ones/twos)**
- Film runs at 24 fps. Animating "on ones" means 24 drawings per second. "On twos" means each drawing is held for 2 frames, so **12 drawings per second**. Animators adopted twos to halve their workload — [Animating on ones, twos and threes (explainer)](https://publish.obsidian.md/mister-chad/animation/animating+on+the+ones%2C+two%2C+and+threes). Richard Williams' *The Animator's Survival Kit* covers timing in its "Drawing in Time" chapter, but I could not retrieve his exact text on twos — [archive.org text](https://dn721807.ca.archive.org/0/items/taskav-01/The__Animator%27s_Survival_Kit%5B1%5D_text.pdf)

**HD / hand-drawn / hybrid games**
- **Cuphead (Studio MDHR, 2017):**
  - Animation plays at **24 fps, drawn on ones**, while the game runs at **60 fps**. Chad Moldenhauer: "for every one second there will be 24 individually-drawn frames" — [Inverse](https://www.inverse.com/article/36647-xbox-one-cuphead-animation); [Unity Made With: Cuphead](https://unity.com/made-with-unity/cuphead)
  - A single frame took **about 25 minutes on average** — [GamesRadar, The making of Cuphead](https://gamesradar.com/the-making-of-cuphead)
  - Total frame count is disputed: about 50,000 per [GamesRadar](https://gamesradar.com/the-making-of-cuphead), versus "120,000-plus" per [Inverse](https://www.inverse.com/article/36647-xbox-one-cuphead-animation)
- **Skullgirls (Reverge Labs, 2011–12):** each character is fully hand-animated and averages about **1,300 high-resolution frames**, described at the time as the most of any fighting game. Every frame was sketched, inked and colored by hand — [PlayStation Blog, 2 Sep 2011](https://blog.playstation.com/archive/2011/09/02/meet-the-skullgirls-the-next-generation-of-psn-fighters); [Skullgirls.com, On Animation](https://skullgirls.com/?p=231)
- **Dead Cells (Motion Twin), 3D-to-2D pipeline** (Thomas Vasseur, Game Developer, 25 Jan 2018):
  - Characters are **50 px tall** in game. Animators key 3D models pose-to-pose, then an in-house tool ("Cruncher") renders them very small with no antialiasing and exports PNG frames plus normal maps for a toon shader.
  - Reusing 3D parts saved "hundred[s] of hours". Re-timing an attack to nerf a weapon only meant moving keyframes.
  - The team accepted some pixel flicker rather than hand-cleaning it.
  - [Game Developer, Vasseur](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)
- **Hollow Knight:** Team Cherry describes traditional frame-by-frame 2D animation and a simpler art style chosen partly for production efficiency, but publishes no fps or frame counts — [Team Cherry blog](https://www.teamcherry.com.au/blog/introducing-hollow-knight)

### Inferences
- A typical image-to-video clip is around 24 fps (confirm against the video-models note). An 8-second clip therefore has about 190 frames. A pixel walk loop needs 6–8 of them, and an HD loop on twos needs about 12–16. The work is selecting and timing key frames, not keeping every generated frame. This matches Cuphead and Dead Cells, which both separate animation rate from game rate.
- The 25 minutes per frame for Cuphead is a useful upper benchmark for hand-drawn HD labour. A 50-frame character at that rate is about 21 hours of drawing (my arithmetic).
- Keeping loops small (4–8 frames) is also the cheapest way to hide AI frame-to-frame inconsistency, which the pixel guides note becomes more visible as frame count grows.

### Gaps
- I found no published frame counts or fps for Hollow Knight, Rayman Legends (UbiArt cut-out animation), or Ori. I did not research these further.
- I found no public source for Kingdom Rush unit frame counts or fps. Only the studio's history is public ([Wikipedia](https://en.wikipedia.org/wiki/Kingdom_Rush)). The team's own production archives are the authoritative source.
- I could not retrieve specific numbers from Saint11's or MortMort's tutorials, or from Brandon James Greer.

---

## 2. Sprite resolutions, screen resolution, camera zoom and atlas limits

### Takeaway
Pixel-art games choose a low internal resolution that scales by a whole number (integer) to 1080p and 4K, such as 320×180 (×6) or 640×360 (×3). Characters there are usually 16–64 px tall: Shovel Knight about 32 px at 400×240, Dead Cells 50 px. HD games draw characters at hundreds of pixels and display them scaled down. The practical ceiling is the texture atlas: 2048² is the safe mobile default, 4096² is common on modern mobile (Apple's SpriteKit uses it), and PC GPUs go to 16384². For HD frame-by-frame animation, the atlas budget (frames × frame size × directions) usually becomes the binding constraint before art quality does.

### Cited Findings
- **Integer-scaling bases:** 320×180 scales ×6 to 1080p and ×12 to 4K. 640×360 scales evenly to both 1280×720 and 1920×1080. 1280×720 on a 1080p screen does not divide evenly and looks distorted. Off-grid bases like 320×240 on 16:9 screens force fractional scaling with shimmer and uneven pixels — [Bugnet, choosing a pixel art resolution](https://bugnet.io/blog/choosing-a-pixel-art-resolution-for-your-game); [Shweep devlog, Resolving Resolutions](https://shweep.itch.io/the-machine-that-breathes/devlog/114161/resolving-resolutions)
- **Shovel Knight:**
  - Internal resolution is **400×240**, which is ×4.5 at 1080p (not an integer) — [Yacht Club, Breaking the NES](https://www.yachtclubgames.com/blog/breaking-the-nes/); [Game Developer mirror](https://www.gamedeveloper.com/design/breaking-the-nes-for-shovel-knight)
  - The Knight's sprite is reportedly **32 px tall** (low-quality source) — [the-artifice.com](https://the-artifice.com/?p=63913)
- **Dead Cells:** characters are **50 px tall** — [Game Developer, Vasseur 2018](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)
- **Common pixel character sizes** appear in commission price sheets: 16×16, 32×32, 48×48, 64×64 and 128×128 tiers, priced higher as size grows (see Q6) — [Fiverr seller](https://www.fiverr.com/psyonyx/create-pixel-art-designs-and-8-bit-icons). A 2026 vendor blog says Celeste-like games mostly use 32×32 or 32×48 character cells. That is unverified, and I found no reliable source for Celeste's internal resolution or Madeline's height — [GDevelop forum thread](https://forum.gdevelop.io/t/how-can-i-set-multiple-resolutions-like-celeste/24582)
- **Atlas limits:**
  - Apple's SpriteKit docs describe "a common maximum texture size of **4,096 × 4,096** pixels" for atlas packing — [Apple, About Texture Atlases](https://developer.apple.com/documentation/spritekit/about-texture-atlases)
  - A GDevelop/Spine forum user reports typical hardware maximums of **16384 on PC and 2048 or 4096 on mobile** (user observation, not a spec) — [GDevelop forum](https://forum.gdevelop.io/t/spine-regarding-texture-packer-max-size-criteria-and-black-screen-issues-on-pc-mobile/77329)
  - Older community guidance (2014–2017) recommends **2048×2048** as the safe atlas default and checking GL_MAX_TEXTURE_SIZE at runtime. Unity's Texture2D.PackTextures capped atlases at 4096 on Android/iOS until a 2019.1 fix — [html5gamedevs](https://html5gamedevs.com/topic/14319-sprite-sheet-maximum-size); [Unity issue tracker](https://issuetracker.unity3d.com/issues/android-ios-texture2d-dot-packtextures-caps-maximumatlassize-to-4096)

### Inferences
- **Atlas arithmetic** (mine; uncompressed RGBA8):
  - A 2048² atlas is 16 MB and holds 64 frames of 256×256 or 256 frames of 128×128.
  - A 4096² atlas is 64 MB and holds 256 frames of 256×256.
  - Example: an HD tower-defense unit with about 60 frames at 256 px fits in one 4096² atlas, or about one 2048² atlas if trimmed and packed tightly. Ten unit types do not fit, so you need several atlases plus compression (ASTC/ETC2) or a smaller authoring size.
- **For AI output:** video models generate at 720p–1080p (and some at 4K), far above any sprite size. Final sprite size is therefore a downscale decision. For pixel art, the downscale plus grid snapping plus palette quantization step is where most AI artefacts are either removed or made worse (see Q4).
- On a phone, a tower-defense unit occupies only a few dozen screen points. Fine detail lost on downscale (fingers, small facial features) does not need to survive, which suits AI-generated motion.

### Gaps
- I found no authoritative 2025–2026 Khronos/Apple/Google document giving recommended mobile atlas sizes. The 2048 default rests on community and engine practice.
- I found no published on-screen unit sizes for Kingdom Rush or similar tower-defense games. The team's own data applies.

---

## 3. Standard animation sets and total frames per character

### Takeaway
A minimal playable set is about 5–6 animations (idle, move, attack, hurt, death, plus jump for platformers). A full action-game set runs to 15–30 or more. Directions multiply everything. A top-down 8-direction character usually needs only 5 drawn directions, with the 3 left-facing ones mirrored, and a 4-direction character needs 3. Asymmetric details (a weapon in one hand, a shoulder bag) break mirroring. Real shipped tower-defense units can be tiny: Bullet Girl ships 5 frames per unit.

### Cited Findings
- **Mirroring:** a common practice is to draw 5 directions (up, up-right, right, down-right, down) and flip the 3 right-facing ones at runtime to get left. An "8-direction" sprite is often "a 5-direction sprite, mirrored". Engines expose a mirrored/flip flag tied to movement angle (e.g. mirror between 90° and 270°) — [OpenGameArt 5(8)-direction character](https://opengameart.org/node/69675); [Construct forum](https://www.construct.net/en/forum/construct-2/how-do-i-18/flip-sprite-using-8-134599)
- **Shipped minimal tower-defense set:** *Bullet Girl: Zombie Defense* (Sojourner.Game, Godot 4.6.1, released 28 Apr 2026) ships 10 unit types with **5 frames each**: 2 walk, 2 attack, 1 hurt. Death is a hurt frame plus a fade-out. Enemy zombies looked acceptable with 2-frame walks plus shader and tween squash-and-stretch, but the 2-frame walks on friendly units "looked very unnatural" — [Ludo.ai indie spotlight, 22 May 2026 (vendor)](https://ludo.ai/blog/indie-spotlight-bullet-girl-zombie-defense)
- **Per-action counts** from the guides in Q1: idle 2–4, walk 4–8, run 6–8, jump 3 (simple) or split into anticipation, rise, apex, fall and land, attack 4–6, hurt 2, death about 5 — [Pixnote](https://pixnote.net/en/learn/animation); [Slynyrd](https://slynyrd.com/blog/2024/5/24/pixelblog-50-human-walk-cycle)
- **Fighting-game upper bound:** about 1,300 frames per Skullgirls character — [PlayStation Blog 2011](https://blog.playstation.com/archive/2011/09/02/meet-the-skullgirls-the-next-generation-of-psn-fighters)

### Inferences
These frame budgets are my synthesis from the per-action counts above. They are planning numbers, not sourced standards.

**(a) Side-view platformer / action character**
- **Minimal (pixel), about 30–40 frames:** idle 4, run 8, jump about 5 (rise 2, apex 1, fall 2; land can reuse), attack 6, hurt 2, death 6.
- **Full (pixel), about 100–160 frames:** adds walk 8, turn 2–3, crouch 2, dash 4–6, a 3-hit combo (about 18), heavy attack 8–10, air attack 6, wall-slide or climb 4–8, cast 8, interact 4, longer death 10.
- **HD on twos:** multiply roughly ×1.5–2.

**(b) Top-down character**
- Per direction (idle 4, walk 6–8, attack 6, hurt 2, death 6) is about 26 frames:
  - 4 directions with mirroring = 3 drawn directions, about 78 frames.
  - 8 directions with mirroring = 5 drawn directions, about 130 frames.
  - Without mirroring: about 104 and 208 frames.
- Death is often drawn in 1–2 directions only. Doing that cuts about 20–25 frames.

**(c) Kingdom Rush-style tower-defense unit**
- Enemies follow paths in screen-space directions (side, plus up and down along the path). Barracks soldiers and heroes need idle, walk, melee attack and death, and heroes add abilities.
- A plausible budget: walk in 3 drawn directions (side mirrored, up, down) at 6–8 frames each, about 18–24; attack 6–10; death 6–10; idle 2–4. That totals about **35–50 frames per enemy type**.
- Heroes with 2–3 skills might reach about **80–120 frames**.
- The Bullet Girl example shows the commercial floor is much lower.
- The team's Ironhide experience will be more precise than this estimate.

**Direction count is the biggest AI cost multiplier**
- Each drawn direction is a separate image-to-video generation.
- Keeping the character identical across directions is a known weak spot. Of the dedicated tools, the vendor-described PixelLab handles rotations with a pose skeleton, not video (see the sprite-tools note).

### Gaps
- I found no authoritative published "standard animation list" document, such as an outsourcing studio's spec sheet with frame counts. The lists above are synthesis.
- Kingdom Rush's actual animation lists and directions are not public in anything I found.

---

## 4. Consistency across animations (studio practice vs AI failure modes)

### Takeaway
Studios keep characters on-model with a few standard tools:
- model sheets and turnarounds aligned with horizontal construction lines
- a locked style guide plus an approved "style test asset" before batch production
- a fixed canvas size and pivot (e.g. bottom-centre) per animation cell
- for 3D-to-2D pipelines like Dead Cells, a shared skeleton and shader

AI video breaks consistency in predictable ways: identity drift ("character bleed" in hats and hair), morphing, sub-pixel and semi-transparent edges, grid drift, palette drift between frames, and inconsistent scale and baseline between clips. Practitioners fix this by:
- anchoring every generation to the same reference or first frame
- locking a single palette and quantizing every frame to it after downscaling
- snapping to a fixed grid
- normalizing pivots and baselines per animation
- often redrawing or painting over the frames by hand

### Cited Findings
**Studio practice**
- A turnaround (front, side, three-quarter, back) keeps a character "on-model" across animators, layout and riggers. Consistency comes from "horizontal construction lines... that align key features like the eyes, shoulders, and waist across all views". Studios bundle turnarounds, pose sheets and expression sheets into a style guide, because "a character might be drawn thousands of times by dozens of different artists" — [CG Wire, Character Sheets (2026)](https://blog.cg-wire.com/character-sheet-animation)
- In outsourcing, the "biggest operational risk is unclear art direction combined with unlimited revisions". Vendors lock a style guide and get a style-test asset approved before batch production, and specify resolution, atlas format, animation export settings and engine requirements up front — [Thundercloud Studio](https://thundercloud-studio.com/article/2d-game-art-outsourcing-workflow/)
- **Pivots:** each animation sheet often pads the character to a slightly different height, so characters land on different baselines. The fix is to draw every frame at the same canvas size and set the pivot at the same spot (e.g. bottom-centre), or set a pivot per animation tag — [Chronocrash forum, pivot/anchor tips](https://chronocrash.com/forum/threads/tips-the-power-of-pivot-anchor-point.3856/latest); [Aseprite tag-pivots plugin](https://necronomison.itch.io/aseprite-tag-pivots)
- **Dead Cells** got consistency from reused 3D skeletons and components rendered through one toon-shading pipeline. It accepted some pixel flicker rather than hand-cleaning it — [Game Developer, Vasseur](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)

**AI failure modes and fixes (mostly vendor and practitioner sources)**
- "Standard video models tend to produce morphing artifacts that break the sprite's grid structure" — [pixie.haus (vendor)](https://pixie.haus/resources/creating-movement-engineering-pixel-art-animation-ai)
- Diffusion output is continuous, not discrete. Edges come out as "dozens of semi-transparent, blended colors" that look muddy under nearest-neighbour scaling — [pixie.haus, grid snapping (vendor)](https://pixie.haus/articles/the-mathematics-of-nostalgia-why-true-grid-snapping-is-the-secret-to-ai-pixel-art)
- AI "pixel art" often has irregular pixel sizes and drifting grid alignment. Snapping tools fix this so sprites "can be scaled cleanly without jittering" — [Scenario Pixel Snapper docs (vendor)](https://help.scenario.com/en/articles/pixel-snapper-the-essentials); [unfake (open source, Wu quantization + scale detection)](https://pypi.org/project/unfake/)
- "Character bleed", where the character's hat or hair changes shape between frames, is described as a 2026 problem. Anchoring to a reference sprite is the stated mitigation — [aiindigo review (secondary)](https://aiindigo.com/blog/simple-sprite-sheet-generation-deep-dive-technical-review)
- An indie dev reports that generating sprite sheets directly gave "inconsistent motion, unstable style, and often unusable output". Generating video first and extracting frames fixed motion continuity, at the cost of manual frame-by-frame background removal and trouble with semi-transparent effects — [yewlark MP4toSprite itch page](https://yewlark.itch.io/mp4tosprite)
- Practical pixel cleanup order from tool docs: downscale first, then quantize to a fixed palette (so dithering lines up with the final grid), then snap to grid. Very small sources (<100 px) collapse and should be upscaled first — [sorceress.games True Pixel tutorial (vendor)](https://sorceress.games/tutorials/true-pixel); [Phaser tidy-pixel-art tool](https://phaser.io/tools/tidy-pixel-art)

### Inferences
- Concrete rules for an AI pipeline, mirroring studio practice:
  1. Make a human-approved model sheet and a locked palette before generating any motion.
  2. Start every clip from the same canonical frame (same scale, camera, framing and background colour).
  3. Normalize every extracted animation to one canvas size and one pivot or baseline.
  4. Quantize all frames of all animations against the same palette (not each frame on its own).
  5. Treat a style-test animation (e.g. the walk) as the approval gate before batch-generating the rest.
- HD vector-style art like Kingdom Rush shows line-weight and outline drift more than pixel art does, because there is no quantization step to absorb it. Expect more paint-over per frame for HD styles. This is inference; I have no measured data.

### Gaps
- I found no rigorous measurement of temporal flicker or identity drift for video models on sprite-style input. Evidence is practitioner and vendor anecdote.
- I found no source on keeping line weight consistent across animations (studio or AI).
- LoRA training on a character for consistency is covered elsewhere (alternatives/ComfyUI note). I did not find shipped-game evidence for it in this pass.

---

## 5. Real end-to-end case studies, 2025–2026

### Takeaway
Publicly documented cases of AI-generated sprite animation in shipped games are rare and small-scale.
- The best-documented shipped example is *Bullet Girl: Zombie Defense* (April 2026). It used Ludo.ai's sprite-sheet tool after Google Veo failed to produce clean walk cycles, and Seedance 2.0 produced good motion but needed too much manual extraction and cleanup.
- Hobbyist Veo 3 tests (r/aigamedev, 2025) conclude the method is "amazing for prototyping" but still needs a pixel artist's cleanup.
- The "100% AI" *Codex Mortis* drew strong negative reaction for muddy visuals.
- The best-documented large-studio cases are cautionary: AI placeholder or "early iteration" 2D assets that slipped into shipped builds (Clair Obscur, Crimson Desert, 1666: Amsterdam), followed by apologies and replacement patches.

### Cited Findings
**Bullet Girl: Zombie Defense (Sojourner.Game; Steam, 28 Apr 2026; Godot 4.6.1)** — [Ludo.ai spotlight, 22 May 2026 (vendor; promotes its own product)](https://ludo.ai/blog/indie-spotlight-bullet-girl-zombie-defense)
- **Goal:** replace stiff 2-frame walks on 5 friendly units.
- **Veo:** rejected. It "couldn't generate clean walk cycles" and kept adding unwanted motion, and the $20 plan allowed only **3 video generations per day**.
- **Seedance 2.0:** good raw output, but per character the developer had to generate video, manually screenshot frames, remove backgrounds and assemble sheets by hand.
- **Ludo:** chosen. Walk cycles looked natural on the first pass for 4 of 5 units and came out as sprite sheets ready for Godot.
- **Attacks:** quality varied, and some were handled by hand. Hurt and death output was decent but unused.
- **Not reported:** total time or cost.

**r/aigamedev "More Veo 3 Sprite Animation Tests" (2025)** — [Redlib mirror of r/aigamedev](https://redlib.ssps.io/r/aigamedev/comments/1la885i/more_veo_3_sprite_animation_tests); related thread [TIL Veo 3 can animate sprites](https://redlib.hackliberty.org/r/aigamedev/comments/1l4am0n/til_veo_3_can_animate_sprites)
- Method: several animations from one sprite via Veo 3 image-to-video in Google Flow (reference added as a frame), then a Photoshop action to remove the white background.
- Verdict: they would still hire a pixel artist to clean up and improve the design, but the method is "amazing for prototyping".
- A commenter recommended Whisk plus Veo 2 first/last-frame interpolation for more control.
- Low-resolution (32×32 top-down) input was not tested.

**Other practitioner reports**
- An itch.io forum pipeline: Veo 3 (or LMArena for free), extract frames from 2–3 s of video, remove the background, cut and compress frames. The author found it "hard and time-consuming" — [itch.io post](https://itch.io/post/14144159/view-in-topic)
- Tools now exist to automate video-to-sheet extraction, e.g. Sprite Lab (Runway/Sora video to sprite sheets; v0.4 devlog 26 Jan 2026) — [Sprite Lab devlog](https://fedeiatech.itch.io/spritelab/devlog). MP4toSprite offers background removal tuned for the checkerboard backgrounds in AI video — [MP4toSprite](https://yewlark.itch.io/mp4tosprite)

**Codex Mortis (Grolaf; Steam demo Dec 2025), marketed as the "first game made 100% with AI"**
- Press called it a functioning Vampire Survivors-style game but not distinctive in art style — [Interesting Engineering](https://interestingengineering.com/ai-robotics/worlds-first-game-completely-made-with-ai)
- GameStar reported user opinions that the look is "muddy" and unclear — [GameStar](https://www.gamestar.de/artikel/das-erste-komplett-ki-generierte-steam-spiel-gespielt,3448840.html)
- Xataka headlined player rejection as "almost unanimous" — [Xataka](https://www.xataka.com/videojuegos/primer-videojuego-hecho-integramente-ia-llega-a-steam-rechazo-jugadores-ha-sido-casi-unanime)
- A third-party mirror showed "Very Positive (83)" on a small sample (unverified) — [Discord game listing](https://discord.com/game/codex-mortis-1456486629395927243)

**AI as a placeholder, replaced before commercial release (accepted pattern)**
- *The Roottrees are Dead*: the itch.io version used AI portraits, and the Steam release uses replacement art. The developer declined to ship the AI portraits ("No, but you could investigate modding them in"). Players said they checked this before buying — [Steam discussion](https://steamcommunity.com/app/2754380/discussions/0/597389996280810619)

**AI placeholder assets that shipped by accident (cautionary)**
- **Clair Obscur: Expedition 33** (launched Apr 2025): temporary AI textures were removed within about 5 days. The Indie Game Awards still revoked its Game of the Year and Debut Game awards around 20–22 Dec 2025, because Sandfall had stated no gen AI was used — [Malay Mail, 21 Dec 2025](https://www.malaymail.com/news/tech-gadgets/2025/12/21/indie-game-awards-rescinds-honours-from-clair-obscur-expedition-33-for-genai-use/202718); [GamesBeat](https://gamesbeat.com/?p=312906)
- **Crimson Desert** (Pearl Abyss, launched 20 Mar 2026): players spotted AI paintings and 2D props. They were undisclosed on Steam. The studio apologized, called them "early-stage iteration" pieces, and announced an audit and replacement patches — [Engadget](https://engadget.com/gaming/crimson-desert-developer-apologizes-and-promises-to-replace-ai-generated-art-183716439.html); [Gigazine, 23 Mar 2026](https://www.gigazine.net/gsc_news/en/20260323-crimson-desert-ai-art)
- **1666: Amsterdam** (Panache, Aug 2026): AI paintings and portraits in the free prologue. The studio said early-production assets slipped through review, and Désilets said all AI assets were removed before Early Access launched on 25 Aug — [FinalBoss](https://finalboss.io/1666-amsterdam-removes-ai-art-after-demo-backlash-what-players-should-check-next)

**Concept-only use reversed under pressure**
- Larian (Divinity, Dec 2025 – Jan 2026): the CEO said gen AI was used for concept exploration and placeholders and that none would ship. After backlash, the studio said in a January 2026 Reddit AMA it would "refrain from using genAI tools during concept art development". Writing director Adam Smith rated text-generation experiments "3/10 at best" — [VGC](https://www.videogameschronicle.com/news/holy-f-guys-were-not-replacing-artists-larian-boss-responds-to-ai-backlash); [CGMagazine](https://www.cgmagonline.com/news/larian-generative-ai-divinity-reddit)

**Conference content**
- I found no GDC 2026 session specifically on AI sprite animation. Related sessions: Keywords Studios, "Art of the Possible: Experimenting with AI in Art" (production 2D/3D/video pipelines; speaker Sergei Gourski previously led animation on Fieldrunners), and Ubisoft, "AI Models for 2D Generation" — [GDC schedule, Keywords](https://schedule.gdconf.com/session/art-of-the-possible-experimenting-with-ai-in-art-presented-by-keywords-studios/917956); [GDC schedule, Ubisoft](https://schedule.gdconf.com/session/ai-models-for-2d-generation/915061)

### Inferences
- Lessons that repeat across cases:
  1. Generic video models (Veo, Seedance) produce usable motion but leave a heavy manual extraction and cleanup step. Sprite-specific tools win on workflow, not raw quality.
  2. Walk and run cycles are the most reliable AI output. Attacks are the least reliable and often get hand animated.
  3. Low-frame-count, small on-screen units (tower defense) are the most forgiving target.
  4. "Placeholder" AI assets are a release-management risk. Studios need an asset-provenance register and a pre-ship audit.
- No case reports measured hours of cleanup per animation. That is the critical unknown for the cost model (Q6) and should be measured in the team's own pilot.

### Gaps
- No verified 2025–2026 postmortem from a commercially significant game that shipped AI-generated character animation with hours and costs.
- No 80.lv or Game Developer article on an AI sprite-animation pipeline surfaced in my searches.
- X/Twitter threads and YouTube devlogs were not searchable with the tools available.

---

## 6. Cost per character: AI pipeline vs traditional outsourcing

### Takeaway
API costs per character are small: roughly $10–$150 for a few animations, even with many retries. Human cleanup dominates, and no one has published measured cleanup hours. Traditional outsourcing benchmarks (2023–2025, self-reported):
- pixel art at about $6–$20 per frame, depending on size and shading
- Spine rig plus animations at about $350–$850 per character
- general 2D animators at about $20–$38/h median on Upwork, with pros at $25–$50/h and specialists at $50–$80/h

The AI pipeline is cheaper only if cleanup stays under several hours per animation.

### Cited Findings
**Video API prices (Gemini API pricing page, updated 15 Oct 2026)** — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)

| Model (paid tier, with audio) | 720p | 1080p | 4K |
|---|---|---|---|
| Veo 3.1 Standard | $0.40/s | $0.40/s | $0.60/s |
| Veo 3.1 Fast | $0.10/s | $0.12/s | $0.30/s |
| Veo 3.1 Lite | $0.05/s | $0.08/s | not supported |

- Veo is **not available on the Gemini API free tier**. Charges apply only to successful generations.

**Image prices**
- Gemini API: Nano Banana 2 (Gemini 3.1 Flash Image) costs about $0.067 per 1K image and Nano Banana Pro about $0.134. Batch is about 50% off — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- OpenAI (developers.openai.com pricing, undated, retrieved Oct 2026): image models are billed per token. Image output is $30/1M tokens for gpt-image-2 and gpt-image-2.5 variants, $32/1M for gpt-image-1.5, $40/1M for gpt-image-1, and $8/1M for gpt-image-1-mini. Batch is half price — [OpenAI API pricing](https://developers.openai.com/api/docs/pricing)
- The OpenAI page listed no Sora video API prices when fetched.

**Kling 3.0**
- Official pricing is in credits: 6–12 credits/s depending on resolution and audio.
- Third-party API resellers charge about $0.075–$0.44/s (EvoLink $0.075/s; PiAPI $0.10–$0.20; fal.ai $0.168–$0.392; Krea $0.176–$0.441) — [EvoLink Kling 3 pricing guide](https://evolink.ai/blog/kling-3-api-pricing-integration-guide); [Krea guide](https://www.krea.ai/blog/kling-3-0-api-access-guide-pricing-code-examples-for-multi-shot-ai-video)

**Consumer plans**
- Bullet Girl's developer reports the $20 Google plan allowed **3 Veo generations per day** (early 2026) — [Ludo.ai spotlight](https://ludo.ai/blog/indie-spotlight-bullet-girl-zombie-defense)

**Sprite tools (secondary; conflicting)**
- PixelLab: about $10–12/month entry tier (roughly 1,000–2,000 generations), about $30/month mid tier (about 3,000), about $50/month top tier — [Cinevva comparison](https://app.cinevva.com/guides/ai-pixel-art-generators); [Knowara review](https://knowara.com/ai-tools/image/pixellab-review/)
- Retro Diffusion Aseprite extension: about $20 Lite or $65 full, one-time purchase — [Cinevva](https://app.cinevva.com/guides/ai-pixel-art-generators)

**Traditional pixel-art rates**
- A Fiverr pixel animator charges a base fee plus a per-frame fee: **32×32 at $10 + $6/frame; 64×64 at $25 + $10/frame; 128×128 at $65 + $15/frame** — [Fiverr seller](https://www.fiverr.com/psyonyx/create-pixel-art-designs-and-8-bit-icons)
- PixelJoint thread (2020) suggests hourly tiers of about $10/h hobbyist, $20–35/h professional, and $50–60/h expert — [PixelJoint](https://pixeljoint.com/forum/printer_friendly_posts.asp?TID=27056)
- Aseprite community advice: price the whole process (frames, revisions) and add a licensing multiplier for commercial use — [Aseprite community](https://community.aseprite.org/t/a-simple-pricing-sanity-check-for-pixel-art-commissions/28697)

**Spine / HD cut-out rates (Esoteric forum posts, mostly undated)**
- A studio quote: Spine rig from scratch $150–200, each animation $50–80
- One experienced animator: about €350–450 per character (rig + animations + changes)
- One quote: $1,200 for 20 animations + 4 rigs
- Hourly rates quoted from $15–28/h up to $45/h
- [Esoteric forum "rates"](https://esotericsoftware.com/forum/d/22571-rates); [Esoteric forum "looking for spine animators"](https://esotericsoftware.com/forum/d/23220-looking-for-spine-animators)

**General animators (Upwork)**
- Upwork's cost page gives a median of roughly **$20–$38/h** for animators. Individual 2D animator listings range from $25/h (Indonesia) to $35/h (UK, 10+ years) to $80/h (US) — [Upwork animator cost](https://www.upwork.com/hire/animators/cost/); [Upwork 2D animators](https://www.upwork.com/hire/2d-animators/id/)

**Hand-drawn HD benchmark**
- Cuphead averaged about 25 minutes per frame — [GamesRadar](https://gamesradar.com/the-making-of-cuphead)

### Inferences
Worked estimates (my arithmetic and assumptions; treat as planning ranges).

**Example: one tower-defense unit, 6 animation clips**
- Clips: idle, walk side, walk up, walk down, attack, death.
- Assumptions: 5 generations per clip on average, 8 s each, so about 240 s of video.

| Video route | Cost for 240 s |
|---|---|
| Veo 3.1 Lite, 720p | $12 |
| Veo 3.1 Fast, 720p | $24 |
| Veo 3.1 Fast, 1080p | $29 |
| Veo 3.1 Standard | $96 |
| Kling 3.0 via cheapest reseller | about $18 |

- Concept and model-sheet images (about 30 at about $0.07–$0.17 each): about $2–$5. The OpenAI per-image figure assumes token counts similar to gpt-image-1 high-quality 1024², about 4k output tokens, which I did not verify for gpt-image-2.
- **API subtotal: about $15–$100 per unit.**
- Top-down 8-direction (5 drawn directions) multiplies clip count by about 5, giving **$60–$500**.

**Human cleanup is the swing factor**
- Assume 1–4 hours per animation for frame selection, background removal, pivot and baseline, palette quantization or line repair, and timing.
- Six animations then take 6–24 hours. At $25–$50/h that is **about $150–$1,200 per unit**, or the founders' own time.

**Traditional comparators for about 50 frames**
- Pixel at 64×64: $25 + 50 × $10 = **$525**
- Pixel at 128×128: $65 + 50 × $15 = **$815**
- Spine cut-out (rig + 6 animations at the studio rates above): **$450–$680**
- Cuphead-grade frame-by-frame: 50 × 25 min ≈ 21 h, about **$520–$1,040 at $25–$50/h**

**Implication**
- The AI route is clearly cheaper only if cleanup stays at about 1–2 h per animation or less, or the style tolerates raw output (small on-screen units, low frame counts).
- If every frame needs a paint-over to match a Kingdom Rush-like line style, costs converge with Spine or outsourced frame-by-frame, and the AI route also carries the legal and market risks in Q7–Q8.
- Consumer-plan rate limits (e.g. 3 Veo generations per day on the $20 tier) make the paid API, or batch-capable resellers, the realistic production route. Wall-clock iteration time matters as much as dollars.

### Gaps
- **No published measured cleanup hours** per AI-generated animation (Veo, Kling, Runway or Seedance). This is the most important missing number. Measure it in a pilot of 2–3 characters.
- Pixel and Spine rate data are self-reported, often undated or pre-2025. I found no 2025–2026 survey of sprite-animation rates.
- I found no rate data specific to Latin American freelance 2D animators, which matters for a Uruguay- or Argentina-based team hiring locally.
- Sora 2 API pricing was not shown on the OpenAI pricing page when fetched.

---

## 7. Legal (as of Oct 2026): output terms, watermarks, copyright, storefront rules

### Takeaway
**Output terms**
- All the major providers let paying users use outputs commercially, and none claims ownership of them. But they do not guarantee exclusivity or copyrightability, and several restrict free tiers:
  - Kling: non-commercial and watermarked on free (per third parties)
  - Luma: non-commercial below Plus
  - Runway: commercial allowed even on free, but watermarked and trained on

**Watermarks**
- Veo outputs carry an invisible SynthID watermark in every frame. OpenAI images now carry C2PA metadata and (per OpenAI's help-centre title) SynthID.
- Whether SynthID survives heavy downscaling and palette quantization to sprite size is unknown.

**US copyright**
- Prompts alone do not make you an author (Copyright Office Part 2, Jan 2025). The courts upheld human-authorship (Thaler; cert denied 2 Mar 2026).
- Human-made expressive inputs that remain perceptible in the output, and human selection, arrangement and modification, are protectable.
- So a character designed or drawn by a human and then animated by AI keeps protection for the human design. Raw AI in-between frames do not get it.

**Storefronts**
- Steam (rules revised Jan 2026) requires disclosure of AI content players consume, including store and marketing assets, but not efficiency tools.
- itch.io requires disclosure on asset pages (optional on game pages).
- Epic, the console stores and the mobile stores have no comparable public game-disclosure rule that I found.
- The EU AI Act's Article 50 transparency duties have applied since 2 Aug 2026. They mainly bind providers (watermarking) and deepfakes.

### Cited Findings

#### 7.1 Output ownership and commercial-use terms
- **Google Gemini API terms** ("Effective March 23, 2026"; last updated 2026-04-28) — [Gemini API Additional Terms](https://ai.google.dev/gemini-api/terms)
  - Google "won't claim ownership" of generated content, but "may generate the same or similar content for others".
  - **Unpaid services:** Google uses submitted content and generated responses "to provide, improve, and develop" products, "human reviewers may read, annotate, and process your API input and output", and users must not submit confidential information.
  - **Paid services:** Google "doesn't use your prompts... or responses to improve our products" (it logs them for a limited time).
  - Users must be 18+ and access the services only "within an available region". Developing competing models is prohibited.
  - The terms contain no SynthID or watermark clauses. Note again that **Veo is not available on the free tier of the API** ([pricing](https://ai.google.dev/gemini-api/docs/pricing)).
- **Google Generative AI Prohibited Use Policy** (last modified 17 Dec 2024) — [Google Prohibited Use Policy](https://policies.google.com/terms/generative-ai/use-policy)
  - Bars "Misrepresenting the provenance of generated content by claiming it was created solely by a human, in order to deceive".
  - Bars content that "violates the rights of others, including... intellectual property rights", and "circumvention of abuse protections or safety filters".
  - It does not explicitly mention removing watermarks.
- **OpenAI Terms of Use** — [OpenAI ToU (ROW)](https://openai.com/policies/row-terms-of-use/); [ConductAtlas provision analysis](https://conductatlas.com/platform/openai/terms-of-use-row/openai-assigns-output-ownership-to-user/)
  - "you (a) retain your ownership rights in Input and (b) own the Output", "to the extent permitted by applicable law".
  - "We hereby assign to you all our right, title, and interest, if any, in and to Output".
  - Output "may not be unique", and other users may receive similar output.
  - The "if any" wording means you get only whatever rights OpenAI has, which may be none.
- **Runway** (official help centre) — [Runway Usage rights](https://help.runwayml.com/hc/articles/18927776141715-Usage-rights); [ConductAtlas Runway](https://conductatlas.com/platform/runway/runway-terms-of-service/company-does-not-restrict-commercial-use-of-outputs/)
  - On all plans (Free, Standard, Pro, Max, Unlimited) "you retain ownership and all your rights to content that you upload and generate", and "the Company does not restrict your commercial use of your Outputs".
  - Free output is watermarked (removable from Standard up). Inputs and outputs are used for training by default on Free, Standard, Pro and Unlimited (secondary).
- **Luma Dream Machine:** Luma's own information page lists the Free plan as "Limited use; watermarked output; draft quality", with "commercial usage rights" on paid tiers. Third parties disagree on whether Lite or only Plus ($29.99/mo) and above is commercial — [Luma official info](https://lumalabs.ai/llm-info); [LicenseOrg](https://licenseorg.com/guide/ai-content/luma-dream-machine)
- **Kling (Kuaishou)** (secondary only; official ToS not retrieved) — [CometAPI](https://www.cometapi.com/are-kling-videos-private/); [ConductAtlas Kling](https://conductatlas.com/platform/kling-ai/kling-ai-terms-of-service/)
  - Free-tier output is watermarked and restricted from commercial use. The Standard paid plan and above remove the watermark and allow business use.
  - Free-tier generations may not become commercially usable just because you later upgrade.
  - Users grant Kling/Kuaishou a worldwide, non-exclusive, royalty-free, sublicensable licence to their content.
  - Free-tier generations may appear in a public feed.
- **MiniMax / Hailuo** (secondary): on paid subscriptions the provider reportedly claims no ownership and the user keeps commercial rights. Free tier reportedly lacks commercial use. The primary ToS (last modified 25 Nov 2024; contracting entity Nanonoble Pte. Ltd.) did not show its IP clauses in my retrieval — [Hailuo ToS](https://hailuoai.video/doc/terms-of-service.html); [zsky.ai](https://zsky.ai/blog/is-minimax-3-free)
- **ByteDance Seedance (Dreamina / BytePlus)** (secondary): paid Dreamina/Jimeng plans include a commercial licence, and API terms vary by provider. BytePlus applies content filters and **visible watermarks**, requires compliance with its GenAI Acceptable Use Policy, and requires likeness authorization for real people — [BytePlus blog](https://www.byteplus.com/blog/dreamina-seedance2-5); [seedance.tv commercial-use guide](https://www.seedance.tv/blog/is-seedance-2-5-safe-for-commercial-use)
- **PixelLab** (terms last updated 23 Nov 2025) — [PixelLab ToS](https://www.pixellab.ai/termsofservice)
  - Users hold copyright in their creations "for both commercial and non-commercial purposes with no need for permission".
  - Training other models on outputs is prohibited without written permission.
  - Users bear full responsibility for non-infringement.
  - API use for reselling or building services requires contacting PixelLab.

#### 7.2 Watermarks and provenance
- **SynthID video:** Google says its video watermark covers "all frames in generated videos" and is imperceptible, while noting SynthID "isn't a silver bullet" — [Google DeepMind, May 2024](https://deepmind.google/discover/blog/watermarking-ai-generated-text-and-video-with-synthid)
- **Veo on Vertex AI:** videos are watermarked with SynthID — [The Decoder](https://the-decoder.com/googles-veo-ai-video-generator-now-available-on-vertex-ai)
- **Is SynthID optional on Veo?** A reseller FAQ says Veo 3.1's SynthID "cannot be disabled". I found no Google documentation of an opt-out — [Atlas Cloud blog (reseller)](https://www.atlascloud.ai/blog/tips/veo-watermark-remover)
- **Visible Veo watermark:** a visible watermark was added to Veo videos except those "made by AI Ultra members using Flow" (May 2025). A 2026 third-party guide says the visible mark depends on subscription tier. Third-party removers work only on the visible mark, not on SynthID or C2PA — [Android Authority, May 2025](https://www.androidauthority.com/google-veo-3-ai-pro-3562934/); [whiskailabs guide](https://whiskailabs.net/?p=10743)
- **SynthID Detector:** availability is reported inconsistently, from limited testers (2025) to public worldwide in English from 7 Oct 2026 (one guide; unverified) — [ITdaily](https://itdaily.com/news/software/google-synthid-detector-ai-generated-content/); [aiidelist guide](https://aiidelist.com/blog/google-synthid-detector.md)
- **OpenAI provenance:** OpenAI's help article is titled "C2PA and SynthID in OpenAI-generated images". Per search snippets, images from ChatGPT, Codex and the API include both C2PA metadata and SynthID, and can be checked at openai.com/verify. OpenAI acknowledges that C2PA metadata "can easily be removed either accidentally or intentionally" (e.g. screenshots, social-media uploads). The article returned HTTP 403 when fetched, so exact wording is unverified — [OpenAI Help 8912793](https://help.openai.com/en/articles/8912793); [VentureBeat on C2PA labels](https://venturebeat.com/ai/openai-joins-meta-in-labeling-ai-generated-images)

#### 7.3 US Copyright Office and courts
- **Part 2 report: Copyrightability** (29 Jan 2025) — [USCO Part 2 report (PDF)](https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf); [Copyright Alliance summary](https://copyrightalliance.org/ai-report-part-2-copyrightability/); [IPWatchdog](https://ipwatchdog.com/2025/01/29/part-two-copyright-office-ai-report-says-creative-prompting-doesnt-constitute-authorship/)
  - "[G]iven current generally available technology, prompts alone do not provide sufficient human control to make users of an AI system the authors of the output". Iterative prompting does not change this.
  - A human's own copyrightable input that is **perceptible in the output** stays protected.
  - Human selection, coordination, arrangement or modification of AI output can be protected. Each case is decided individually, and the Office saw no need for new legislation. More than 10,000 comments were received.
- **Registration guidance** (March 2023): applicants must disclose AI-generated material that is more than de minimis and limit the claim to human authorship — [USCO AI registration guidance (PDF)](https://www.copyright.gov/ai/ai_policy_guidance.pdf)
- **Zarya of the Dawn** (USCO letter, 21 Feb 2023): registration was kept for the human-authored text and the selection and arrangement of images and text. The individual Midjourney images were excluded — [USCO Zarya letter (PDF)](https://www.copyright.gov/docs/zarya-of-the-dawn.pdf)
- **"A Single Piece of American Cheese"** (Invoke; registered 30 Jan 2025):
  - First rejected in 2024. Registered after Invoke submitted a timelapse and records of inpainting decisions.
  - The protection covers only the **selection, coordination and arrangement of inpainted AI components**, not the individual AI segments.
  - [IPKat, Feb 2025](https://ipkitten.blogspot.com/2025/02/a-single-piece-of-us-copyright-are-ai.html); [Invoke press release](https://pressreleases.triplepointpr.com/2025/02/10/invoke-receives-first-of-its-kind-copyright-registration-for-ai-assisted-visual-artwork-from-u-s-copyright-office-develops-provenance-records-tool-to-help-others-do-the-same/)
- **Thaler v. Perlmutter:**
  - The D.C. Circuit (18 Mar 2025) unanimously affirmed refusal to register a work naming an AI system as author — [Carlton Fields](https://www.carltonfields.com/insights/publications/2025/no-copyright-protection-for-ai-assisted-creations-thaler-v-perlmutter)
  - The **Supreme Court denied certiorari on 2 Mar 2026** (No. 25-449). The lower-court ruling stands, though a cert denial sets no precedent — [SCOTUSblog case file](https://www.scotusblog.com/cases/case-files/thaler-v-perlmutter)
- **Allen v. Perlmutter** (D. Colo., No. 1:24-cv-02665; *Théâtre D'opéra Spatial*):
  - Cross-motions for summary judgment were briefed in early 2026. The government notes Allen used at least 624 prompts plus Midjourney variations and upscales and Photoshop cleanup, and argues the expressive elements came from Midjourney.
  - **I found no ruling as of Oct 2026.**
  - [ChatGPT Is Eating the World tracker](https://chatgptiseatingtheworld.com/category/allen-v-perlmutter/); [Law360](https://www.law360.com/technology/articles/2432068)

#### 7.4 Training-data litigation bearing on risk
- **Disney & Universal v. Midjourney** (C.D. Cal., filed June 2025), consolidated with Warner Bros. Discovery's suit (Sept 2025):
  - The court ordered private mediation by **19 Aug 2026**, with a joint report due 21 Aug and a status conference on 31 Aug 2026.
  - I could not find the outcome.
  - [Graphic Policy, 14 Nov 2025](https://graphicpolicy.com/2025/11/14/court-suggests-disney-v-midjourney-go-to-mediation/); [ChatGPT Is Eating the World](https://chatgptiseatingtheworld.com/2025/11/17/judge-kronstadt-order-for-disney-v-midjourney-to-private-mediation-adr-procedure-no-3-with-deadline-of-aug-19-2026/)
- **Getty Images v. Stability AI (UK)** — [Judiciary UK judgment](https://www.judiciary.uk/judgments/getty-images-and-others-v-stability-ai/); [Burges Salmon](https://www.burges-salmon.com/articles/102lydc/getty-images-v-stability-ai-getty-granted-permission-to-appeal); [Cleary Gottlieb](https://www.clearygottlieb.com/news-and-insights/publication-listing/uk-high-court-issues-landmark-ruling-in-getty-images-v-stability-ai)
  - High Court judgment of 4 Nov 2025 ([2025] EWHC 2863 (Ch)). Getty dropped its primary training claims because training happened outside the UK.
  - The court held Stable Diffusion is not an "infringing copy" because it does not store Getty's works. Getty won only "extremely limited" trade-mark findings on early versions.
  - Getty has permission to appeal on secondary infringement, and the **appeal is pending**.
- **Andersen v. Stability AI / Midjourney / DeviantArt / Runway** (N.D. Cal.): deadlines extended about 3 months in Feb 2026, and the summary-judgment hearing moved to **17 Feb 2027**. No trial date is confirmed — [ChatGPT Is Eating the World, 3 Feb 2026](https://chatgptiseatingtheworld.com/2026/02/03/sarah-andersens-copyright-lawsuit-the-1st-filed-v-ai-companies-gets-pushed-back-again-at-her-request/)

#### 7.5 EU and other jurisdictions (brief)
- **EU AI Act, Article 50** (transparency): applies from **2 Aug 2026** — [Goodwin, Aug 2026](https://www.goodwinlaw.com/en/insights/publications/2026/08/alerts-technology-dpc-eu-ai-act-transparency-obligations-now-in-force); [Houthoff](https://www.houthoff.com/insights/news/ai-act-transparency-obligations-and-the-ai-omnibus-regulation/); [Mondaq, implications for game developers](https://www.mondaq.com/uk/new-technology/1592660/some-implications-of-the-eu-ai-act-on-video-game-developers)
  - The Digital Omnibus delayed the high-risk rules, not Article 50.
  - Generative systems already on the market get until **2 Dec 2026** for the Art. 50(2) machine-readable marking duty, which falls on **providers**.
  - Deployers have disclosure duties for **deepfakes** (realistic depictions of real people) and for some public-interest text.
  - Fines reach up to €15M or 3% of turnover.
  - Studios using third-party tools are generally "deployers", while studios that build their own generators are "providers".
  - The final Commission guidelines (reported as C(2026) 5054, July 2026) say NPC interactions in a single-player game may be "obvious" and need no extra notice.
- **Uruguay:** a Frente Amplio bill (reported June 2026) would address the use of protected works to train AI. Current law has no AI-specific provisions — [Prensa Latina, 26 Jun 2026](https://www.prensa-latina.cu/2026/06/26/proyecto-defiende-en-uruguay-derechos-de-autor-ante-avance-de-ia/)
- **Argentina:** Ley 11.723 is built on human creativity, and I found no AI-specific reform — [Derecho en Zapatillas, 2025](https://www.derechoenzapatillas.com/2025/derechos-de-autor-y-la-inteligencia-artificial-quien-es-el-autor-en-la-era-digital/); [Estudio Vilaplana, 11 Oct 2026](https://estudiovilaplana.com.ar/2026/10/11/derechos-autor-inteligencia-artificial-argentina/)

#### 7.6 Storefront disclosure rules
- **Steam, original policy (10 Jan 2024):** the Content Survey split AI use into two categories — [Valve, "AI Content on Steam"](https://store.steampowered.com/news/group/4145017/view/3862463747997849618); [GamingOnLinux](https://www.gamingonlinux.com/2024/01/valve-announces-new-rules-for-games-with-ai-content-on-steam/); [TechRaptor](https://techraptor.net/gaming/news/steam-changes-rules-on-ai-to-allow-vast-majority-of-games-that-use-it)
  - **Pre-Generated:** made during development. Under the Distribution Agreement you promise no illegal or infringing content, consistent with your marketing.
  - **Live-Generated:** made at runtime. You must also describe guardrails, and players can report content via the overlay.
  - Disclosures appear on the store page.
- **Steam, revision (mid-January 2026; outlets date it 16–19 Jan):** the survey now says "efficiency gains through the use of these tools are not the focus of this section"
  - Code assistants and other back-end tools no longer need disclosure.
  - Disclosure targets content players consume: in-game assets and, per Gigazine's paraphrase of Valve, content "from marketing and concept assets" to in-game content.
  - [Outlook Respawn, 18 Jan 2026](https://respawn.outlookindia.com/amp/story/gaming/gaming-news/valve-clarifies-steam-ai-policy-focus-shifts-to-content-consumed); [Gigazine, 20 Jan 2026](https://gigazine.net/gsc_news/en/20260120-steam-updates-ai-disclosure-guidelines)
- **Steam disclosure volume:**
  - **7,818 games (about 7% of Steam titles)** publicly disclose gen AI, and at least **20% of 2025 releases** reportedly use it — [Gigazine](https://gigazine.net/gsc_news/en/20260120-steam-updates-ai-disclosure-guidelines)
  - A law-firm guide says about 8,000 by H1 2025, versus about 1,000 in all of 2024 — [Legal Moves](https://legalmoveslawfirm.com/steam-ai-policy/)
  - An independent census (13 Jul 2026) counts **about 9,400 AI-flagged titles** and **about one in three new releases** by mid-2026 — [fragwyz Substack](https://fragwyz.substack.com/p/three-years-of-ai-on-steam)
  - Another review says about one in five listed games carries the label (Jul 2026) — [Tech-Insider](https://tech-insider.org/steam-ai-disclosure-2026)
- **Steam enforcement:** Crimson Desert's undisclosed AI art was flagged as a breach of Steam's disclosure expectation — [Gigazine](https://www.gigazine.net/gsc_news/en/20260323-crimson-desert-ai-art). Activision disclosed AI use in Black Ops 7 on Steam after player complaints — [Windows Central](https://windowscentral.com/gaming/activision-is-forced-to-confirm-the-use-of-ai-in-call-of-duty-due-to-steams-disclosure-policy)
- **itch.io** (Nov 2024) — [80.lv](https://80.lv/articles/asset-creators-on-itch-io-now-have-to-disclose-the-use-of-generative-ai/); [GamingOnLinux](https://gamingonlinux.com/2024/11/itchio-store-now-requires-ai-generated-content-disclosures-for-assets)
  - Disclosure is **mandatory for asset pages**. Sub-tags cover Graphics, Sound, Text & Dialog and Code, and pages without AI get a "No AI" label.
  - Untagged AI assets, "even if modified afterward", are dropped from browse indexing and may be delisted.
  - Game pages may optionally tag. Itch cited "legal ambiguity" around AI rights.
- **Epic Games Store:** no AI disclosure requirement.
  - Tim Sweeney said in late Nov 2025 that store AI labels "make no sense" because "AI will be involved in nearly all future production". In 2026 he called Valve's policy "really irresponsible", a "Scarlet Letter of AI".
  - Epic-owned Sketchfab reportedly labels AI content since Dec 2025 (secondary).
  - [VGC](https://www.videogameschronicle.com/news/epics-tim-sweeney-says-it-makes-no-sense-for-game-stores-to-flag-when-ai-has-been-used-in-development); [VGC, "really irresponsible"](https://videogameschronicle.com/news/epic-games-ceo-says-its-really-irresponsible-of-steam-to-make-studios-disclose-ai-use); [Tech-Insider](https://tech-insider.org/steam-ai-disclosure-2026)
- **Consoles and mobile:** no public AI-disclosure rule found for PlayStation Store, Xbox Store, Nintendo eShop, or the mobile app stores (2026 secondary analysis). Xbox's XR-018 user-generated-content policy (revised March 2025) requires in-game reporting for player-visible UGC, including AI-assisted content (secondary, unverified) — [Tech-Insider](https://tech-insider.org/steam-ai-disclosure-2026); [OtakuKart](https://otakukart.com/xbox-tightens-ugc-and-ai-content-rules-leaving-sony-and-nintendo-behind/)

### Inferences
**Protecting the character**
- The strongest US position: humans design the character (model sheet, key poses) and use that drawing as the first frame or reference for image-to-video. The human design stays protectable as a perceptible expressive input.
- Keep provenance records (who drew what, prompts, selections, edits, timelapses), as Invoke did, to support registration or enforcement.
- Raw AI in-between frames, and a character generated entirely by GPT from prompts, are likely unprotectable. Substantial human redrawing or editing can add protectable expression.
- Trademark (names, logos) protects the brand regardless of copyright.

**Contract hygiene**
- Use paid tiers for all assets that ship. Free tiers are commercially restricted (Kling, Luma), watermarked, or used for training (Gemini unpaid, Runway).
- Generating concepts on a free tier and upgrading later may not "clean" those outputs (Kling).

**Disclosure**
- Shipping AI-generated sprite frames on Steam requires disclosure under both the 2024 and 2026 rules. Using AI only for internal prototypes that are fully replaced does not appear to.
- Google's Prohibited Use Policy separately bars claiming AI-generated content was made "solely by a human, in order to deceive". Denying AI use when asked would breach both Valve's expectation and Google's policy.

**SynthID in sprites**
- Whether SynthID survives a downscale to 32–128 px, palette quantization and hand paint-over is unknown.
- Nothing found in US law or the provider terms requires keeping it. The EU marking duty falls on providers, and stylized fantasy sprites are not deepfakes.
- Practically, assume the provenance signal may persist in HD frames that get light processing.

**Training-data suits**
- These mainly create indirect risk. The direct risk for a developer is an output that resembles a protected character (the Midjourney complaints rest on outputs of famous characters).
- Avoid prompting with existing IP or named artists' styles, and review outputs for resemblance.

### Gaps
- I could not retrieve the full official Kling, Seedance/Dreamina, MiniMax, Retro Diffusion or Scenario terms. The Kling, Seedance and MiniMax points are secondary.
- I did not verify whether the Gemini API's "available regions" include Uruguay and Argentina for paid Veo access.
- I could not confirm a Google-documented opt-out for SynthID on Veo, whether the API (as opposed to the Gemini app or Flow) ever adds a visible watermark, or SynthID robustness to pixel-art quantization.
- I could not verify verbatim the OpenAI help article (403) and Valve's exact Jan 2026 survey wording (only press quotes).
- Outcomes not found: the Disney/Universal/WBD v. Midjourney mediation (deadline 19 Aug 2026) and Allen v. Perlmutter (no ruling found).
- Google Play and Apple App Store policies on AI-generated content in games were not researched in depth.
- Two items may have changed and should be re-checked: the Copyright Office leadership dispute (Perlmutter's removal and litigation), and any Part 3 (training) developments.

---

## 8. Player and industry reception (2024–2026), prototyping vs shipped assets

### Takeaway
**Industry sentiment is hardening while use grows**
- GDC 2026: 36% of professionals use gen AI at work, but 52% now say it harms the industry (up from 30% and 18% in the two prior surveys).
- Visual and technical artists are the most negative group (64%).

**Players are negative but split by measure**
- Attitude surveys show strong dislike: Quantic Foundry finds 85% negative, highest for art.
- Purchase-intent surveys show a smaller hard core: Circana finds just over 25% would be less likely to buy or would refuse, and GameDiscoverCo finds 8% of engaged Steam users would refuse any AI game.

**The market penalty is real but uneven**
- AI-flagged Steam games reach 100+ reviews at about 55% of the non-AI rate. Several high-profile games still sold strongly despite AI controversies (Arc Raiders).

**Backlash pattern**
- Backlash is harshest when AI touches visible art, is undisclosed or denied, or is framed as replacing artists.
- AI used for prototyping and placeholders that are fully replaced before release is broadly accepted, though Larian's case shows even concept-stage use can provoke backlash.
- The awards and press ecosystem now also penalizes AI (Indie Game Awards).

### Cited Findings
**Industry surveys**
- **GDC 2026 State of the Game Industry** (published 29 Jan 2026; more than 2,300 respondents) — [GDC article](https://gdconf.com/article/gdc-2026-state-of-the-game-industry-reveals-impact-of-layoffs-generative-ai-and-more/); [Business Wire, 29 Jan 2026](https://www.businesswire.com/news/home/20260129438528/en/2026-State-of-the-Game-Industry-Report-Reveals-Widening-Effect-of-Layoffs-Broader-Perspectives-on-Generative-AI-Unionization-Tariffs-and-More); [GamesBeat](https://gamesbeat.com/state-of-game-industry-survey-sheds-light-on-layoffs-genai-views-unionization-and-tariffs-gdc-survey/)
  - **Use:** 36% use gen AI at work (30% at game studios, 58% at publishers, support and marketing).
  - **Sentiment:** 52% say gen AI has a negative impact on the industry (30% the previous year, 18% the year before). 7% say positive (13% in 2025).
  - **Negative by discipline:** visual and technical art 64%, design and narrative 63%, programming 59%.
  - **Uses:** research and brainstorming 81%, email and daily tasks 47%, code 47%, **prototyping 35%**.
  - **Tools:** ChatGPT 74%, Gemini 37%, Copilot 22%.

**Player surveys**
- **Quantic Foundry** (Q4 2025, N=1,799): 85% hold a negative attitude toward gen AI in games, and 63% chose the most negative option. Attitudes are most negative for artistic and creative uses, more open for gameplay uses such as dynamic difficulty. Female and non-binary gamers and younger gamers are more negative — [Quantic Foundry, 18 Dec 2025](https://quanticfoundry.com/2025/12/18/gen-ai/); [GamesMarket](https://www.gamesmarket.global/quantic-foundry-most-gamers-are-negative-about-the-use-of-gen-ai-in-video-games)
- **Circana PlayerPulse** (Dec 2025, US): just over 25% say knowing a game used gen AI for art, dialogue, text or music makes them less likely to buy or makes them refuse (about 22% in Mar 2024). Fewer than 10% say it makes them more interested, and the majority is neutral or unsure — as reported by [Outlook Respawn](https://respawn.outlookindia.com/gaming/gaming-news/do-gamers-care-about-genai-new-data-reveals-a-silent-majority); [Pixel P&L](https://pixelpnl.beehiiv.com/p/pixel-p-l-85-of-gamers-reject-generative-ai-in-video-games-survey-finds)
- **GameDiscoverCo Steam survey** (about 3,800 engaged Steam users, 25 Jun – 2 Jul 2026):
  - 23.4% have "absolutely no problem" with AI, 19.6% are fine with it, and **8.1% won't play any game using AI**.
  - Another summary of the same data gives 43% with no major issue, 31% negative, and 56% wanting AI coding tools disclosed.
  - [games.gg](https://games.gg/news/steam-players-ai-games-survey/); [OtakuKart](https://otakukart.com/steam-survey-finds-majority-players-accept-ai-in-game-development-but-31-still-oppose-ai-generated-content/)

**Market performance proxy (independent census, 13 Jul 2026)** — [fragwyz Substack](https://fragwyz.substack.com/p/three-years-of-ai-on-steam)
- AI-flagged games reach ≥100 reviews at **about 55% of the non-AI rate**, unchanged over two years. AI's revenue share (10–27%) is below its launch share (about 33%).
- Among AI games, art and image use appears in 57% of successes but 72% of flops.
- Successful games wrote longer disclosures (median 22 vs 13 words), used more "assist/supplementary" framing (59% vs 41%), and more often reassured players about human oversight (21% vs 12%).
- 22% of significant-revenue AI games added the flag after release.
- Caveat: single analyst, review-count revenue proxy.

**Backlash cases (shipped or announced visible assets)**
- **Jurassic World Evolution 3** (Frontier, Oct 2025): AI scientist portraits had been disclosed on Steam. After backlash they were removed ("We have opted to remove the use of generative AI for scientist portraits") — [TechRadar](https://www.techradar.com/gaming/jurassic-world-evolution-3-thankfully-wont-feature-ai-generated-character-portraits-following-community-backlash); [Aftermath](https://aftermath.site/jurassic-world-evolution-3-ai-removed/)
- **Call of Duty: Black Ops 7** (Nov 2025): AI-looking calling cards and profile images drew complaints, and Activision confirmed AI use via its Steam disclosure — [Windows Central](https://windowscentral.com/gaming/activision-is-forced-to-confirm-the-use-of-ai-in-call-of-duty-due-to-steams-disclosure-policy)
- **Postal: Bullet Paradise** (Dec 2025):
  - Publisher Running With Scissors cancelled it about 1–2 days after reveal over AI-art allegations, and developer Goonswarm Games announced closure.
  - Goonswarm had first denied the allegations. It later admitted AI in its "promo art" and promised human-made replacements.
  - [VGC](https://www.videogameschronicle.com/news/postal-game-developer-shuts-down-after-its-project-was-cancelled-due-to-allegations-of-generative-ai-use); [Decrypt](https://decrypt.co/351204/new-postal-game-canceled-one-day-after-reveal-generative-ai-allegations)
- **Clair Obscur: Expedition 33:** Indie Game Awards GOTY and Debut revoked in Dec 2025 over temporary AI textures that were removed within days of launch — [Malay Mail](https://www.malaymail.com/news/tech-gadgets/2025/12/21/indie-game-awards-rescinds-honours-from-clair-obscur-expedition-33-for-genai-use/202718)
- **Larian / Divinity** (Dec 2025 – Jan 2026): backlash over concept-stage use led to a pledge to drop gen AI from concept art — [CGMagazine](https://www.cgmagonline.com/news/larian-generative-ai-divinity-reddit)
- **Crimson Desert** (Mar 2026): undisclosed AI 2D props, apology and audit. Mixed reviews despite strong sales — [Engadget](https://engadget.com/gaming/crimson-desert-developer-apologizes-and-promises-to-replace-ai-generated-art-183716439.html)
- **Neverness to Everness** (May 2026): AI-art controversy days after global launch. Billboard art resembled Makoto Shinkai films, and VTuber Ironmouse cancelled a sponsorship. The source is a fan guide site and should be verified — [NTE Guide timeline](https://nteguide.com/en/blog/nte-ai-art-controversy-timeline/)
- **1666: Amsterdam** (Aug 2026): AI assets in the prologue were removed before Early Access, and the prologue's Steam score was reportedly 66% Mixed (secondary) — [FinalBoss](https://finalboss.io/1666-amsterdam-removes-ai-art-after-demo-backlash-what-players-should-check-next)
- **Arc Raiders** (Embark): AI voices drew Western backlash, yet the game launched with strong reviews and more than 480,000 concurrent Steam players (aggregator figure) — [LetsDataScience](https://letsdatascience.com/news/gamers-push-back-against-ai-generated-game-content-020ccc28)

**Accepted or tolerated use**
- AI placeholders replaced before the commercial release (*The Roottrees are Dead*) — [Steam discussion](https://steamcommunity.com/app/2754380/discussions/0/597389996280810619)
- Small-scale disclosed AI walk cycles in a niche pixel tower-defense game. I found no reported backlash, but did not verify its review page — [Ludo.ai spotlight](https://ludo.ai/blog/indie-spotlight-bullet-girl-zombie-defense)

**Platform-holder rhetoric**
- Epic's Sweeney argues labels will become meaningless as AI becomes ubiquitous — [VGC](https://www.videogameschronicle.com/news/epics-tim-sweeney-says-it-makes-no-sense-for-game-stores-to-flag-when-ai-has-been-used-in-development)

### Inferences
**Prototyping vs shipped assets.** The evidence clearly separates these.
- AI for animatics, timing tests and placeholder motion that artists then redraw draws little public reaction, if properly replaced and audited.
- AI frames that ship as the character art the player looks at for hours are the highest-risk category. The penalty grows if the AI use is undisclosed, denied, or visibly low-quality ("muddy", morphing).

**Positioning advice drawn from the cases and the census**
1. Disclose specifically and honestly on Steam, e.g. "character animations were generated from our hand-drawn designs and cleaned up frame-by-frame by our artists". Never deny or under-disclose.
2. Make sure human authorship is visible and true: human character design, human paint-over, credited artists.
3. Keep an asset-provenance register and run a pre-ship audit so no placeholder AI slips through.
4. Avoid AI in key art, capsule and trailer assets, where accusations start (Postal, Black Ops 7).
5. Expect zero tolerance from awards bodies and some press. The IGA rule disqualified any production use.
6. For an ex-Kingdom Rush team, brand reputation amplifies both attention and scrutiny. A known-studio AI controversy (Larian, Frontier) attracts far more coverage than an anonymous indie case.

**Audience segment matters**
- Hostility is higher among younger players and core PC audiences.
- Mobile tower-defense audiences may be less sensitive, but I found no mobile-specific survey.

### Gaps
- I found no player survey specific to mobile or tower-defense audiences on AI art.
- I found no measured review-score or sales impact for a game whose AI use was specifically character animation (as opposed to portraits, textures or voices).
- The Circana figures are from press reports, not the primary Circana release.
- The Neverness to Everness details come from a fan guide site.
- The Arc Raiders concurrent-player figure comes from an aggregator.
- I found no 2026 Unity or Google Cloud developer-survey data on gen AI in art pipelines in this pass.
