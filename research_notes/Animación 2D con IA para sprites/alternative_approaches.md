# Alternatives to video-model sprite animation: cutout/skeletal rigs, controlled diffusion, 3D-to-2D, and hybrids (state as of October 2026)

Scope note: this file covers the non-video routes, plus the video-model variants that work as pose-driven animators, and compares them with "AI video → extract frames → sprite sheet" (the route the studio liked with Google Veo). Version numbers and dates are flagged where the sources give them. Where a source is a vendor or a search summary rather than a primary page, that is said inline.

---

## 1. Skeletal / cutout animation done properly (Spine, DragonBones, Unity 2D Animation, Godot Skeleton2D, Live2D, Rive, Creature, Moho), preparing an AI character for rigging, and why the naive "split into parts" attempt looked bad

### Takeaway
Professional cutout animation looks good because of four things the naive attempt almost certainly lacked: **inpainted hidden regions** behind each part, **weighted mesh deformation** (parts bend instead of rotating as rigid rectangles), **physics-driven secondary motion**, and **parts drawn and split the way an animator would choose**. As of 2026 the prep work can be partly automated. See-through (SIGGRAPH 2026, Apache-2.0) splits an anime-style image into up to 23 inpainted layers, and tools like OCS turn that into a weighted Spine 4.2 rig. The output is still a draft that needs an animator. The runtime payoff is large: tiny files, blending and layering of animations, and the same animations reused across skins and characters. That payoff is what beats video→sprite once a game has many animations or characters.

### Cited Findings

**Spine (Esoteric Software): the reference tool**
- Spine's free-form deformation moves individual mesh vertices, so images can "stretch, squash, bend, and bounce". Meshes also skip pixels outside their polygon, which the page calls "especially important for mobile games". — [Spine in depth](https://esotericsoftware.com/spine-in-depth)
- Weights (skinning) assign vertices to bones so the mesh deforms automatically as the bones move: "Posing a character with images that can bend becomes as easy as just positioning the bones." — [Spine in depth](https://esotericsoftware.com/spine-in-depth)
- Skins swap sets of attachments to outfit a character, and "Animations can be reused for characters that look different, saving countless hours." — [Spine in depth](https://esotericsoftware.com/spine-in-depth)
- Animations can be layered (for example, shooting while running) and crossfaded. IK constraints and a multi-bone IK Pose tool are included, and code can manipulate bones at runtime (aiming at a target, leaning on slopes). — [Spine in depth](https://esotericsoftware.com/spine-in-depth)
- File size and smoothness: "Spine animations store only the bone data, which is very small," and "Spine animations use interpolation so animation is always as smooth as the frame rate." — [Spine in depth](https://esotericsoftware.com/spine-in-depth)
- Engine support: "The Spine Runtimes officially support 19 game toolkits and 7 programming languages," plus more than 40 third-party runtimes. The current editor line is **Spine 4.3** (per the site's "What's New" link). — [Spine in depth](https://esotericsoftware.com/spine-in-depth)
- Spine 4.2 added **physics constraints**, so animators no longer hand-key secondary motion for hair and clothing. A physics constraint simulates physics on a single bone, with sliders from 0 (unconstrained pose) to 100 (maximum physics offset). Physics constraints are **not** in Spine Essential. — [Spine physics constraints docs](https://esotericsoftware.com/spine-physics-constraints); [Spine 4.2: The physics revolution](https://us.esotericsoftware.com/blog/Spine-4.2-The-physics-revolution)
- **Pricing (Oct 2026):**
  - Essential: list $99, shown at $69. Excludes meshes, IK and other advanced features; Essential cannot save or export projects that use them.
  - Professional: list $449, shown at $379.
  - Enterprise: $2,499 base + $379 per user per year. Required for businesses with **$500k+ annual revenue**, and that threshold counts investment and VC financing.
  - Licenses are per named user.

  — [Spine purchase page](https://esotericsoftware.com/spine-purchase)
- Mesh limitations from Esoteric forum threads (aggregated via search summary, so treat the details as secondary):
  - Real-time skinning shrinks volume, pinches or crumples a mesh that folds onto itself, and linework visibly thins or thickens as the texture warps.
  - Auto-weighting can leave hard, angular joints that need hand-correcting at elbows.
  - Tails need many vertices.
  - Bone scale and shear give "squishy-ness" without meshes.
  - Weights are preferred over per-vertex deform keys for game runtimes, for performance.

  — [Esoteric forum thread 12052](https://esotericsoftware.com/forum/d/12052); [Esoteric forum thread 12903](https://esotericsoftware.com/forum/d/12903); [Esoteric forum 23857](https://de.esotericsoftware.com/forum/d/23857-how-can-i-move-my-skeleton-gently-like-a-video)

**Other skeletal / cutout tools**
- **Unity 2D Animation + 2D PSD Importer.**
  - The importer takes **PSB** files (save the PSD with Photoshop's Large Document Format).
  - The "Character Rig" option builds a prefab with one sprite per layer, sorted by the layer hierarchy.
  - The Skinning Editor's Auto Geometry tool creates the mesh, assigns bones and generates weights.
  - Rigs survive reimport.
  - Sprite Swap / Sprite Library lets sprites that share an identical rig be swapped (skins/variants).

  The cited manual pages are older package versions: 2D Animation 2.0, written for Unity 2018.3, and PSD Importer 4.x. Check the current package manual. — [Unity 2D PSD Importer 4.3 manual](https://docs.unity3d.com/Packages/com.unity.2d.psdimporter@4.3/manual); [Unity 2D Animation 2.0 manual](https://docs.unity3d.com/Packages/com.unity.2d.animation@2.0/manual/index.html)
- **Godot Skeleton2D (Godot 4.7 docs, marked "work in progress").**
  - Workflow: Polygon2D pieces traced by hand in the UV editor → Skeleton2D/Bone2D chain → "Sync Bones to Polygon" → paint weights → animate bones.
  - Triangulation doesn't always bend as expected, so extra internal vertices are needed.
  - The page mentions no PSD import.
  - It pitches in-engine rigging as avoiding import from Spine/DragonBones.

  — [Godot docs: 2D skeletons](https://docs.godotengine.org/en/stable/tutorials/animation/2d_skeletons.html)
- **DragonBones** looks abandoned:
  - AlternativeTo lists it as discontinued ("developer disappeared", download link dead).
  - A community Pixi runtime README says Egret "seems to have abandoned DragonBones and its libraries years ago".

  — [AlternativeTo: DragonBones](https://alternativeto.net/software/dragonbones/about); [dragonbones-pixijs README](https://unpkg.com/dragonbones-pixijs@1.0.5/README.md)
- **Creature** offers 2D skeletal + mesh animation with automatic weight painting and "motors" that generate animation procedurally from parameters. The comparison source is a vendor-adjacent blog post; I could not verify Creature's current release status. — [Creature vs Spine (DeepMotion blog)](https://www.deepmotion.com/post/2d-game-animation-creature-vs-spine); [Slant: Creature vs Spine](https://www.slant.co/versus/17857/1900/~creature_vs_spine)
- **Rive.**
  - State-machine-driven vector animation with bones, meshes and IK/path/distance constraints.
  - Runtimes for JS, Flutter, iOS, Android, React, React Native, C++, **Defold, Unity and Unreal**.
  - Plans: Free (exports show a Rive splash screen), Cadet $9/seat/mo (max 3 seats, no splash), Voyager $32/seat/mo, Enterprise $120/seat/mo for $10M+ revenue companies.

  — [Rive pricing](https://rive.app/pricing)
- A 2026 review estimates "a complex animated character with full state machine logic might be 50KB" (reviewer estimate, not a benchmark). — [Makerstack Rive review 2026](https://makerstack.co/reviews/rive-review/)
- **Live2D Cubism** is built for front-facing, layered illustrations (VTubers, gacha/visual-novel portraits).
  - AI features: semi-automatic face deformer and face-movement generation in Cubism 5.0 (2023); automatic full-body deformer generation and automatic sway (hair, small objects) in **5.1.00 (30 July 2024)**.
  - The full-body deformer feature is best for upright, forward-facing humanoids.
  - No 2026-specific AI additions were found.

  — [Live2D Cubism 5.1 new features](https://docs.live2d.com/en/cubism-editor-manual/new-function5-1/); [Cubism 5.1.00 update](https://www.live2d.com/en/cubism/update/update_5_1_00/); [Cubism 5.0 new features](https://docs.live2d.com/en/cubism-editor-manual/new-function5-0/); [Automaton (JP) on 5.1](https://automaton-media.com/articles/newsjp/20240730-303793/)
- Live2D has a Cubism SDK for Unity. Live2D's own 360° "Euclid" project only managed full rotation under limited conditions (symmetrical design, anime shading, simple hair), which points to Cubism being poor at turning characters to other facings. — [Cubism SDK for Unity docs](https://docs.live2d.com/en/cubism-sdk-manual/cubism-sdk-for-unity/); [GameBusiness.jp 2016 report](https://www.gamebusiness.jp/article/2016/07/26/12471.html)

**AI tools that auto-split a character into layers/parts (prep for rigging)**
- **See-through** (arXiv 2602.03749; SIGGRAPH 2026, conditionally accepted; Apache-2.0).
  - Decomposes one anime illustration into a layered PSD of **up to 23 semantic layers** (front/back hair, face, eyes, clothing, accessories, body parts), "fully inpainted… with inferred drawing orders". It also outputs depth maps and masks.
  - It was trained on supervision bootstrapped from commercial Live2D models.
  - Latest model is V3; changelog entries are dated April 2026.
  - VRAM: about 12–16 GB at 1280px, about 10 GB with offload, about 8 GB with NF4.
  - The authors say it is **not yet an image-to-Live2D generator**. Rigging (meshes, physics, motion curves) isn't covered, and "Live2D artists would likely make different layer-splitting choices for natural motion."

  — [See-through GitHub](https://github.com/shitagaki-lab/see-through); [See-through arXiv paper](https://arxiv.org/html/2602.03749v1)
- Downstream of See-through:
  - **OCS (OneClickSpine)**, Apache-2.0. PNG → See-through layers → auto-drops dummy layers and flags uncertain ones → user drags bones → weighted meshes + atlas + `skeleton.json` for **Spine 4.2** + HTML preview.
  - OCS needs an NVIDIA GPU (8–16 GB) or Apple Silicon (capped at 768px) and downloads about 12 GB of weights.
  - Its built-in walk/wave/jump animations assume a standing figure, and only idle exports by default.
  - The biggest quality factor is a true transparent-background PNG.
  - It is tiny and early (2 stars, 15 commits).

  — [OCS GitHub](https://github.com/sleeeppy/OCS)
- **Stretchy Studio** imports See-through PSDs and auto-rigs them with DWPose or a heuristic. It uses direct mesh deformation rather than bones, so it isn't a Spine workflow. Its README warns that realistic or non-anime styles may not decompose correctly. — [Stretchy Studio GitHub](https://github.com/MangoLion/stretchystudio)
- **Qwen-Image-Layered** (Alibaba/HKUST; paper 18 Dec 2025, weights 19 Dec 2025; Apache 2.0).
  - Decomposes any image into a variable number of RGBA layers; layers can be decomposed again recursively.
  - Exports PSD/PPTX/ZIP. Recommended resolution is 640.
  - It is general-purpose (scene elements, text, objects), not character-part-specific, and the README doesn't say whether occluded regions are completed.

  — [Qwen-Image-Layered GitHub](https://github.com/QwenLM/Qwen-Image-Layered); [Replicate listing](https://replicate.com/qwen/qwen-image-layered)
- **LayerDiffuse** (lllyasviel, arXiv 2402.17113, Feb–Jun 2024, so older).
  - Generates natively transparent images or foreground/background layer pairs on SD1.5/SDXL, trained on 1M transparent layer pairs.
  - Users preferred it over generate-then-matte in 97% of cases.
  - It is useful for generating individual parts on transparency, not for decomposing an existing character.

  — [LayerDiffuse arXiv](https://www.arxiv.org/abs/2402.17113)
- **Other AI rig helpers:**
  - Genielabs **spine-animation-ai**, a Claude skill. Places parts with SIFT+RANSAC, builds skeleton JSON and draw order, and generates idle/walk/run/attack. It needs a Gemini key and is licensed **PolyForm Noncommercial**. — [spine-animation-ai GitHub](https://github.com/GenielabsOpenSource/spine-animation-ai)
  - **Layer.ai "Create Spine Components"** produces a parts sheet that you still cut yourself. — [Layer.ai Spine components](https://layer.ai/tools/layer--create-spine-components)
  - **Scenario's 2D Animation Rigging Sheet** is a similar parts-sheet generator. — [Scenario rigging sheet app](https://scenario.com/apps/2d-animation-rigging-sheet)
  - **img2rig**: GroundingDINO+SAM masking into layered PNGs plus a custom spring runtime, not Spine. — [img2rig GitHub](https://github.com/SSnemo/img2rig)

### Inferences
- **Why the studio's naive cutout attempt looked bad.** Squashing or stretching a flat image, or rotating rectangles cut from a single front-facing drawing, misses most of what makes cutout work:
  - **No hidden-region art.** When an arm rotates, the area behind it is empty or shows a hard seam. See-through exists because inpainting occluded regions is the hard part.
  - **Rigid parts.** Parts rotate rigidly at the joints with no weighted mesh, so elbows and knees break.
  - **No secondary motion.** Hair and cloth don't follow through, which Spine 4.2 physics and Live2D 5.1 auto-sway now provide.
  - **Mechanical timing.** Linear interpolation with no pose-to-pose structure.
  - **Wrong parts.** The parts were not drawn for rigging. The See-through authors themselves say animators would split layers differently.
- Professional cutout also relies on **drawing swaps**: separate hand, mouth and eye attachments, and profile vs. 3/4 heads switched by Spine attachments/skins. A single AI front-view image provides none of these. This is the main reason "one image → rig" stays a draft.
- **Realistic 2026 AI-assisted cutout workflow:**
  1. Generate the character in a neutral A-pose on a transparent or flat background (LayerDiffuse or a cutout).
  2. Decompose it with See-through (anime styles) or Qwen-Image-Layered (general).
  3. Fix and redraw parts in Photoshop or Krita, adding extra hand/face drawings with image-edit models.
  4. Rig in Spine Professional, or Unity 2D Animation if Unity-only, with meshes only at bends.
  5. Add physics constraints.
  6. Hand-animate.

  Expect a skilled animator to still own steps 3 to 6.
- Video→sprite gives better motion quality per animation from one image (perspective changes, cloth and hair redraws). Skeletal gives far better **scaling**: one rig serves dozens of animations, many skins/characters (Spine skins, Unity Sprite Swap), runtime blending/layering/procedural aiming, and tiny files. Skeletal cannot do large perspective changes (turnarounds) without extra drawings. Live2D is the weakest choice for side-scrollers or top-down games because it is built around front-facing models.
- Tool picks: Spine Professional is the default for multi-engine cutout. Unity 2D Animation is free and fine if Unity-only. Godot's built-in system is manual and fiddly. Rive is attractive for UI/mobile/vector styles. DragonBones should be avoided as abandoned.

### Gaps
- **Moho** (Smart Bones, vector rigging) and current **Creature** release status: no sources were retrieved, so they are not assessed.
- No current (2025–2026) Unity 2D Animation package version number was retrieved; the latest manual URL returned 404.
- Spine Essential vs. Professional: the full feature matrix didn't render. Meshes, IK and physics are confirmed Professional-only.
- No independent quality evaluation of See-through → OCS/Stretchy rigs on non-anime (Western cartoon, painterly) characters was found.
- No source found for Adobe tools (e.g., Photoshop AI layer separation, Adobe Animate/Character Animator auto-rig) in a 2026 game context.

---

## 2. Diffusion-based frame generation with control (ControlNet/OpenPose + IP-Adapter/LoRA, AnimateDiff, pose-driven video models such as Wan Animate/VACE, Kling Motion Control, Animate-Anyone-style) and skeleton-driven sprite generators

### Takeaway
Per-frame image generation (the studio's GPT-image attempt, or ControlNet+IP-Adapter frame by frame) is fundamentally prone to drift. Even the purpose-built academic model (Sprite Sheet Diffusion, 2024–25) lists subject consistency and fine detail as open problems. The 2026 state of the art has converged on **pose-driven video models**:
- **Wan 2.2 Animate**: open weights, Apache 2.0, runs in ComfyUI.
- **Kling Motion Control 2.6 → 3.0**: commercial.

Both take a character image plus a skeleton or reference motion video. They are the same family as Veo, with one key addition: **you control the motion** (timing, loopability, identical cycles across characters). For pixel art, **PixelLab's skeleton-based animation** (posed rig plus 4/8-direction rotation) is the specialized tool most recommended in 2026 guides.

### Cited Findings
- **Sprite Sheet Diffusion** (arXiv 2412.03685; v2, 16 Mar 2025).
  - Adapts Animate Anyone with ReferenceNet (appearance), a Pose Guider and a Motion Module (temporal smoothness).
  - Fine-tuned, it reaches SSIM 0.659 and LPIPS 0.125 in-sample, vs. 0.330/0.557 for vanilla Animate Anyone.
  - Dataset is tiny: 152 action sequences from GameArt2D/SpriteDatabase.
  - Stated limitations: lost details (a missing gun), weaker hair and props, "subject consistency and fine detail remain open problems". Pixel art is not addressed.

  — [Sprite Sheet Diffusion arXiv](https://arxiv.org/html/2412.03685v2)
- Community reports on prompt-only frame generation: a 2024 OpenGameArt thread reports random, inconsistent frames. The advice was to start from a well-defined base image and keep prompts consistent. — [OpenGameArt: AI for spritesheet generation](https://opengameart.org/forumtopic/ai-for-spritesheet-generation)
- A 2026 comparison guide's test for prompt-based animation tools is to "look at frame two", where "the proportions shift, a colour changes, a detail vanishes". It credits skeleton-based animation with avoiding this because the same rig drives every frame. — [Cinevva: AI pixel art generators 2026 (4 Sep 2026)](https://app.cinevva.com/guides/ai-pixel-art-generators)
- **Wan 2.2 Animate** (14B, open weights, Apache 2.0, Alibaba Tongyi).
  - Reproduces a performer's movements and expressions on a chosen character using "spatially-aligned skeleton signals". In ComfyUI, pose is extracted with DWPose from a driving video.
  - Two modes: **Move/Animation**, where the character image is animated by the video's motion and the video only drives timing, and **Mix/Replacement**, which swaps the character into the footage.
  - Dimensions must be multiples of 16.
  - Caveats: occlusion or out-of-frame limbs break pose guidance; long clips risk "small identity shifts or blending artifacts".

  — [ComfyUI docs: Wan2.2 Animate](https://docs.comfy.org/tutorials/video/wan/wan2-2-animate); [Scenario: Wan 2.2 Animate essentials](https://help.scenario.com/en/articles/wan-2-2-animate-models-the-essentials); [ComfyUI Wiki: Wan2.2 Animate](https://comfyui-wiki.com/en/tutorial/advanced/video/wan2.2/wan2-2-animate)
- **Wan 2.1 VACE First-Last-Frame**: you give a start and an end frame, and the model synthesizes the motion in between in latent space (not optical flow). It follows a 4n+1 frame-count rule. The 14B model does clean 480p/720p. — [ComfyUI workflow: Wan2.1 VACE FLF](https://comfy.org/workflows/video_wan_vace_flf2v-45c0ce6bcf2e/)
- **Kling Motion Control.**
  - Transfers body motion and facial expression from a reference video (or a motion library) onto a character image.
  - VIDEO 3.0 Motion Control (Kling post dated 5 Mar 2026) improves facial consistency over 2.6. Third-party docs say 2.6 handles up to 30 s.
  - Kling advises matching body proportions, avoiding cuts and camera moves, and avoiding overly fast or complex actions. The character should be over 5% of the frame and unoccluded.

  — [Kling Motion Control guide](https://kling.ai/quickstart/motion-control-user-guide); [Kling 2.6 Motion Control tutorial](https://kling.ai/blog/ai-motion-transfer-video-tutorial); [Scenario: Kling v2.6 Motion Control](https://www.scenario.com/models/kling-v26-motion-control); [RunComfy: Kling 2.6 Motion Control](https://www.runcomfy.com/models/kling/kling-2-6/motion-control-standard)
- **PixelLab.**
  - Offers one-click, text-prompt and **skeleton-based** animation, plus 4- and 8-direction character rotation for top-down/isometric games.
  - Its character creator makes 8 rotational directions and "animations that play correctly in every direction".
  - From $12/month, with a 40-generation trial (per a third-party guide).

  — [PixelLab homepage](https://pixellab.ai/); [PixelLab llms.txt](https://www.pixellab.ai/llms.txt); [Cinevva guide](https://app.cinevva.com/guides/ai-pixel-art-generators)
- **Retro Diffusion**: a local Aseprite extension (one-time $20 Lite / $65 full) that makes animation frames and tilesets from **text prompts** (no rig). — [Cinevva guide](https://app.cinevva.com/guides/ai-pixel-art-generators)
- **SpriteCook**'s sprite animator requires pixel-art input ≤256×256 that fills most of the frame. — [SpriteCook docs](https://www.spritecook.ai/docs/guide-animate-sprite)
- A hobbyist tutorial recommends generating the character in a T/A-pose with Pose ControlNet (or Qwen Image Edit / Flux without ControlNet), then building and rigging a 3D model (Blender/Mixamo) for consistency across angles. In other words, the community often escapes 2D drift by going through 3D (see §3). — [itch.io AI-gen sprite tutorial](https://tawusgames.itch.io/ai-gen-sprite-tutorial)

### Inferences
- **ControlNet/IP-Adapter/LoRA frame-by-frame (and AnimateDiff on SD1.5)** is effectively superseded for character animation by 14B-class video DiTs that model time jointly. Generating frames independently is exactly what produced the studio's "jumpy" GPT-image results. Pose control fixes the skeleton but not the textures, colors or accessories from frame to frame. I found no 2026 source arguing AnimateDiff is still competitive.
- **The most useful upgrade over plain Veo image-to-video is pose-driven video (Wan 2.2 Animate Move mode, Kling Motion Control):**
  1. Render a clean **skeleton or mannequin video** of the exact cycle needed, from Mixamo/Meshy mocap in Blender or Unity, or a filmed actor.
  2. Feed it to the pose-driven model with the character image.

  This gives repeatable timing, exact loop points, consistent framing and identical cycles across many characters. Free-form prompting can't guarantee any of those. With Wan the cost is GPU time on open weights; with Kling it is per-generation credits.
- **VACE FLF2V** is the tool for **loops and transitions**: set the first and last frame to the same pose to force a loop, or to two key poses to generate a transition such as idle→attack.
- Every video-derived route still needs the same post-processing as the Veo route:
  - background removal or matting
  - frame selection
  - downscale and palette quantization for pixel art
  - jitter cleanup

  Identity drift on long clips is a documented risk, so keep cycles short.
- For **pixel art**, skeleton-driven specialized tools (PixelLab) beat general video models on consistency and direction handling. General video models generate at 480–720p and must be downsampled, which produces soft edges and noise that need manual cleanup.

### Gaps
- No primary sources retrieved for **UniAnimate, MimicMotion, Hunyuan (HunyuanVideo-I2V / avatar variants), Animate Anyone 2**, or **Wan 2.5/2.6+** animate variants. Their 2026 standing relative to Wan 2.2 Animate is unverified.
- No independent 2026 benchmark comparing Veo vs. Wan Animate vs. Kling Motion Control specifically on stylized 2D game characters was found.
- No verified source on publicly released **sprite-sheet LoRAs** (e.g., for Flux/Qwen-Image-Edit) and their quality.
- Kling pricing per second and Wan Animate VRAM floor were not retrieved.

---

## 3. 3D-to-2D pipeline (image-to-3D → auto-rig → mocap → render to sprites with orthographic camera and toon/pixel shaders)

### Takeaway
3D-to-2D is the proven route for **many animations, many characters, and many facing directions**. Dead Cells (2018) is the canonical case: it reused animations across monsters and saved "hundreds of hours", and retakes were faster than uploading GIFs. The costs are flickering pixels at low resolution, reduced detail, and a style that reads as "3D-rendered" unless the shading and timing are deliberately art-directed (Guilty Gear Xrd: custom cel shaders and deliberately dropped frames). In 2026, AI shortens the front end:
- Image-to-3D: Meshy, Tripo, Hunyuan3D, TRELLIS.
- Auto-rig: Meshy (humanoid/quadruped, 500+ presets), Tripo (biped, plus multi-limb in v2.5), Mixamo (humanoid).

AI-generated meshes from flat 2D art are the weak link for preserving a hand-drawn look.

### Cited Findings
- **Dead Cells** (Thomas Vasseur, Motion Twin; Game Developer article, 25 Jan 2018). Pipeline:
  1. A simple pixel-art model sheet.
  2. Character and skeleton built in 3ds Max, exported as FBX.
  3. A custom in-house tool rendered meshes "at a very small size with no antialiasing".
  4. Each frame exported as PNG plus a **normal map**, with a basic toon shader using the normals for volume.

  Further details:
  - Characters were about **50 px tall** in game.
  - Animation was pose-to-pose: interpolation frames only before or after keys, with VFX selling the impact.
  - **Benefits:** fast retakes (re-timing an overpowered weapon by moving keys), animation reuse across models and recycled monsters ("the most useful trick", saving hundreds of hours), and modular gear attached to the 3D model.
  - **Drawbacks:** flickering pixels from low-res no-AA rendering, "never fully solved", and limited detail.
  - Vasseur was the only artist for about a year.

  — [Game Developer: Using a 3D pipeline for 2D animation in Dead Cells](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)
- A free Houdini digital asset recreates the Dead Cells-style pixel render (via Copernicus/COPs) from 3D renders or live models. — [Pixel-art renderer for Houdini (itch.io)](https://fatalexit.itch.io/pixelart-renderer-for-sidefx-houdini)
- **Guilty Gear Xrd** (Arc System Works; GDC 2015 talk by Junya Motomura).
  - Custom cel shaders plus models built specifically for those shaders, so the 3D resembles their legacy sprites.
  - The team "shunned mathematical accuracy" to get consistent cel shading.
  - Deliberately cut animation frames (limited animation) to give the illusion of hand-drawn art.

  — [Motomura GDC slides (PDF)](https://www.ggxrd.com/Motomura_Junya_GuiltyGearXrd.pdf); [BlenderNation write-up](https://www.blendernation.com/2015/07/26/junya-c-motomura-behind-the-scenes-of-guilty-gear-xrd/); [Giant Bomb: Guilty Gear Xrd](https://www.giantbomb.com/games/3030-42679/)
- **Meshy auto-rig and animate.**
  - Rigs humanoid and quadruped characters, with **500+ animation presets** (walk/run, daily actions, fighting).
  - Best results from T- or A-pose. Exports FBX/GLB.
  - Custom choreography needs manual animation or Mixamo retargeting.
  - Non-standard body plans may not be recognized.

  — [Meshy docs: Animate](https://docs.meshy.ai/en/webapp/guides/animate)
- **Tripo.**
  - Image-to-3D with an optional quad topology (FBX output) that helps deformation.
  - Rigging v1 handles bipeds. v2.5 adds quadrupeds, hexapods, octopods, avian, serpentine and aquatic body plans.
  - Export can include the skeleton, animations and a bottom-center pivot.

  — [Scenario: Tripo family guide](https://help.scenario.com/articles/4692888910-tripo-family-the-complete-guide); [Civitai: 3D recipes](https://developer.civitai.com/orchestration/recipes/3d)
- **Mixamo** is humanoid-focused; community advice is to clean the mesh in Blender first (merge doubles, fix normals). This comes from a search-summarized guide, so it is secondary. — [Civitai: 3D recipes](https://developer.civitai.com/orchestration/recipes/3d)
- **Image-to-3D for stylized/anime input.**
  - A Japanese 2026 comparison lists TRELLIS at 1536³ with PBR, MIT license, runnable locally on a GPU with ≥6 GB.
  - Vendor comparisons say TRELLIS 2 takes a single image only, while Hunyuan3D accepts text, single-image and multi-view input with textures up to 8K.
  - A guide notes **flat 2D illustrations are the harder case** compared with photos.
  - No head-to-head test on anime/flat 2D characters was found.

  — [lilting.ch 2026 3D generator comparison (JP)](https://lilting.ch/articles/ai-3d-generation-tools-comparison); [3DAI Studio: TRELLIS 2 vs Hunyuan 3D (vendor)](https://www.3daistudio.com/blog/trellis-2-vs-hunyuan-3d-differences-explained); [Sorceress: lift a 2D image to 3D](https://sorceress.games/blog/lift-a-2d-image-to-3d-model-browser-six-models)

### Inferences
- **Style preservation.** Image-to-3D models reproduce silhouette and colors but flatten painterly linework into textures, and lighting comes from the renderer, not the artist. To read as 2D, the pipeline needs:
  - stepped, limited animation (render on 2s/3s, or pose-to-pose like Dead Cells)
  - a hard-edged toon ramp, ideally with hand-tuned normals
  - outlines (inverted hull or Freestyle)
  - for pixel art, a render at native sprite resolution with no AA, plus palette quantization and some hand cleanup

  Guilty Gear Xrd shows the ceiling is very high, but that took a dedicated technical-art team.
- **Where 3D-to-2D beats video→sprite:**
  - **8-direction top-down games.** Rotating the camera gives perfectly consistent directions; video gives one view per generation, and 8 directions × N animations multiplies drift risk.
  - **Large libraries of animations**, via preset mocap libraries.
  - **Many characters sharing animations**, via retargeting.
  - **Equipment/variant swaps.**
  - **Cheap retakes.** Re-time keys and re-render instead of regenerating.
  - **Normal maps for 2D dynamic lighting**, which come for free.
- **Where it loses:** a single hero character in a painterly HD style with few animations, where video→sprite gives a more "hand-drawn" feel per frame. Also small studios without 3D or technical-art skills.
- **A strong 2026 hybrid:** use the rigged 3D model only as a **motion source**. Render the mocap as a skeleton or grey-mannequin video and feed it to Wan 2.2 Animate or Kling Motion Control with the 2D character image (§2). That keeps 3D's control and reuse while the video model supplies the 2D look.

### Gaps
- **AccuRIG** (Reallusion) and Rodin (Hyper3D): no sources retrieved.
- Credit pricing for Meshy/Tripo/Hunyuan3D rigging and generation was not retrieved.
- No source covers turnkey 2026 "3D→sprite sheet" renderers in Unity/Godot. The Houdini tool is one example; Blender setups are described only in unsourced community advice.
- No measured data on how well current image-to-3D preserves a specific 2D art style; all evidence is anecdotal or vendor-based.

---

## 4. Hybrid approaches: video for motion reference + cleanup, AI in-betweening (ToonCrafter), EbSynth style transfer, RIFE/FILM interpolation; do they help or hurt sprites?

### Takeaway
In-betweening and interpolation **help only for HD, smooth-motion styles**, and they **hurt pixel art and deliberately limited animation**. Optical-flow interpolators (RIFE/FILM) blend frames: they produce ghosting and smearing, lose fine patterns, and create off-palette colors. Generative in-betweeners (ToonCrafter, 2024; Wan VACE first-last-frame) handle large cartoon motion better but can invent details. EbSynth 2 (2025) is a useful non-generative tool for restyling motion footage from a few painted keyframes, but it can't invent unseen sides of a character. The most productive hybrid is **AI motion as reference or draft, with an artist owning the key poses and final cleanup.**

### Cited Findings
- **ToonCrafter** (Xing et al., 2024, so older) is a latent video diffusion model for cartoon interpolation built on DynamiCrafter and trained on about 270k cartoon clips.
  - It targets the non-linear, large and occluded motion that traditional linear-motion interpolators fail on.
  - A sketch encoder lets a single sketch guide motion across frames.
  - Code and weights are public.

  — [Hugging Face paper page: ToonCrafter](https://huggingface.co/papers/2405.17933); [DEV summary](https://dev.to/mikeyoung44/tooncrafter-generative-cartoon-interpolation-4pim)
- **RIFE on game art.**
  - A developer used RIFE to in-between two hand-drawn keys. Commenters called the blur and odd details "AI-like", and a patterned outfit lost its pattern because it "just blends the two frames".
  - In general, interpolation artifacts are ghosting, smearing along the motion path, and incoherent blending, which appear when motion estimation fails.
  - No source tests RIFE specifically on pixel art.

  — [itch.io post (RIFE in-betweens)](https://itch.io/post/15745160); [Morphic glossary: frame interpolation](https://morphic.com/ai-glossary/frame-interpolation)
- **Dead Cells** chose pose-to-pose timing, with interpolation frames only before or after keys and never between, for attack readability. That is evidence that game "snap" often benefits from *fewer* in-betweens. — [Game Developer: Dead Cells 3D pipeline](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)
- **Guilty Gear Xrd** deliberately cuts frames to look hand-drawn. Smooth interpolation works against that aesthetic. — [Giant Bomb: Guilty Gear Xrd](https://www.giantbomb.com/games/3030-42679/)
- **EbSynth 2** (around Sept 2025).
  - Non-generative texture synthesis: propagates a painted keyframe's look across a video using optical flow and patch matching, using only your video and keyframes.
  - Adds a timeline, layers, keyframe import/export and optional AI keyframe generation.
  - Sources conflict on whether it runs in the browser (videos uploaded to their servers, then deleted) or offline on desktop.
  - It can't stylize parts not visible in the keyframe, so turns need intermediate keyframes.

  — [CG Channel: EbSynth 2](https://www.cgchannel.com/?p=170455); [80.lv: EbSynth 2 released](https://80.lv/articles/photoshop-for-video-ebsynth-2-released); [Digital Production: EbSynth V2 (Sept 2025)](https://digitalproduction.com/2025/09/24/ebsynth-v2-real-time-preview-timeline-layers/)
- **Wan VACE first-last-frame** generates motion between two anchor frames generatively rather than with optical flow. It is usable as a "smart in-betweener" between artist-drawn keys. — [ComfyUI workflow: Wan2.1 VACE FLF](https://comfy.org/workflows/video_wan_vace_flf2v-45c0ce6bcf2e/)

### Inferences
- **Help:**
  - EbSynth or video models used to *restyle* motion from a controllable source: a 3D render, a filmed actor, or a Wan Animate output. Paint 1–3 keyframes in the target style and propagate.
  - VACE FLF or ToonCrafter used between artist-approved key poses for HD games, with a human pass on every generated frame.
  - Interpolation for UI, VFX or background loops where exact pixels don't matter.
- **Hurt:**
  - RIFE/FILM on pixel art. Blended in-between colors break the palette and smear dithering and outlines, so you must re-quantize and hand-fix, which removes most of the time savings.
  - Doubling frame rate on deliberately limited or pose-to-pose game animation, which reduces snap and readability.
  - Any interpolation of video-model output that already has frame-to-frame jitter, since the jitter gets smeared, not removed.
- A practical "video for reference" workflow for a pixel-art team: generate the motion with a video model → rotoscope or trace key poses at target resolution in Aseprite → hand-draw in-betweens. This is slower than direct extraction but gives clean, ownable art. It is the same logic as the 2026 guides' "trace-first" advice.

### Gaps
- No primary source tested FILM, RIFE or ToonCrafter on pixel-art sprites.
- No 2025–2026 successor to ToonCrafter (a dedicated cartoon in-betweener) was verified. "Cadmium" was not found in the retrieved sources.
- EbSynth 2 platform, pricing and licensing need confirmation on the official site.

---

## 5. Which approach for which game type (pixel-art platformer, HD hand-drawn, top-down 8-direction RPG, many characters/NPCs, mobile)

### Takeaway
No single route wins:
- **Video→sprite (Veo, or better, pose-driven Wan/Kling):** best per-frame quality for a few hero animations in an HD illustrated style.
- **Spine-style skeletal (AI-assisted prep):** wins when animation count × character count is high, on mobile, or when runtime blending is needed.
- **3D-to-2D:** wins for 8-direction games and huge animation libraries.
- **Skeleton-driven pixel tools (PixelLab):** win for pixel-art characters with many directions.

Most studios in 2026 should expect to mix routes: for example, Spine or 3D for the NPC crowd and video-derived frames for hero moves.

### Cited Findings
- Skeletal advantages relevant to scale and mobile:
  - bone-data-only files
  - interpolation to any frame rate
  - meshes skipping transparent pixels ("especially important for mobile")
  - skins reusing animations across different-looking characters
  - layered/blended animations and runtime procedural control

  — [Spine in depth](https://esotericsoftware.com/spine-in-depth)
- Rive characters with full state machines are estimated at about 50KB (reviewer estimate). Runtimes exist for Unity, Unreal and Defold. — [Makerstack Rive review](https://makerstack.co/reviews/rive-review/); [Rive pricing](https://rive.app/pricing)
- 3D-to-2D at pixel scale: Dead Cells (about 50 px characters) got animation reuse across monsters, fast retakes and normal-mapped toon shading, but unsolved pixel flicker. — [Game Developer: Dead Cells](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)
- For pixel games with more than a couple of animated characters, a Sept 2026 guide says PixelLab is "where the time saving actually shows up". It also offers 4/8-direction rotation for top-down/isometric games. — [Cinevva guide](https://app.cinevva.com/guides/ai-pixel-art-generators); [PixelLab](https://pixellab.ai/)
- Pose-driven video models need unoccluded, well-framed characters and short, moderate motions. — [Scenario: Wan 2.2 Animate](https://help.scenario.com/en/articles/wan-2-2-animate-models-the-essentials); [Kling 2.6 Motion Control tutorial](https://kling.ai/blog/ai-motion-transfer-video-tutorial)
- Live2D is optimized for forward-facing humanoids, and 360° turning was only feasible under restricted conditions. — [Live2D 5.1 features](https://docs.live2d.com/en/cubism-editor-manual/new-function5-1/); [GameBusiness.jp](https://www.gamebusiness.jp/article/2016/07/26/12471.html)

### Inferences

**Memory and file size (my own arithmetic, not sourced).** An uncompressed 512×512 RGBA frame is 512×512×4 bytes = 1 MiB. A modest HD character with 10 animations × 12 frames is about 120 MiB raw. At 8 directions that becomes about 960 MiB, before atlas packing and GPU texture compression (which typically cut it by about 4–8×). A skeletal character is one atlas of parts (often 1–4 MiB) plus kilobytes of animation data, regardless of how many animations it has. This is the core reason video→sprite stops scaling for HD multi-direction games and mobile.

**Recommendations by game type:**

| Game type | Recommended primary route | Why / notes |
|---|---|---|
| **Pixel-art platformer (side view, 32–96 px)** | Skeleton-driven pixel tool (PixelLab) or 3D-to-2D (Dead Cells style) for volume; video→sprite only as a motion draft, then hand-cleaned | At low resolution every stray pixel shows. Video output (480–720p) must be downscaled and palette-quantized, and its jitter becomes pixel flicker. Pixel art needs hand cleanup on any route; Dead Cells never fully solved 3D flicker either. |
| **HD hand-drawn / illustrated style, few characters** | **Video→sprite** (Veo, or pose-driven Wan 2.2 Animate / Kling Motion Control for controlled cycles), with VACE FLF for loops and transitions | Best per-frame "drawn" quality from one image, and it handles perspective, cloth and hair redraws that cutout can't. Watch texture memory at HD and trim frame counts (pose-to-pose). |
| **HD style, many animations or skins (fighters, action RPGs, gacha)** | **Spine Professional** with AI-assisted layer prep (See-through / Qwen-Image-Layered → manual fix → rig), or 3D with cel shading à la Guilty Gear Xrd | Animation reuse across skins, blending, small files. Needs a real animator; the AI only removes the segmentation and inpainting drudgery. |
| **Top-down 8-direction RPG** | **3D-to-2D** (image-to-3D → auto-rig → mocap presets → ortho render at 8 angles + toon/pixel shading), or PixelLab for pixel art | Directional consistency comes free from 3D. With video, 8 separate generations per animation multiply drift and cost. Cutout rigs need separate drawings per facing. |
| **Many characters / NPCs** | Skeletal (shared skeleton + skins) or 3D retargeting (Meshy 500+ presets, Mixamo) | Animation cost is paid once per skeleton, not per character. A video route costs N characters × M animations generations plus cleanup. |
| **Mobile** | Spine or Rive (vector/mesh, tiny files, runtime state machines); 3D-to-2D only with low frame counts | Download size and texture memory dominate. Frame-by-frame HD sprites are the most expensive option. |

**When video→sprite remains the right call:**
- the style is painterly or HD;
- each character has a small fixed set of animations (roughly ≤10–15);
- no runtime blending or equipment swapping is needed;
- the art team can't build rigs or 3D;
- the animations need 3D-ish motion (turns, cloth flips) that cutout can't fake.

Prefer the pose-driven variants (Wan 2.2 Animate, Kling Motion Control) over free-prompt image-to-video, so cycles are repeatable and share timing across characters.

### Gaps
- No published cost-per-animation comparison across these routes was found. The memory figures above are my own arithmetic.
- No 2025–2026 postmortem of a shipped commercial game using AI-generated video→sprite animation was found to validate the HD recommendation at production scale.
- No source quantified pixel-art cleanup time for video-derived vs. 3D-derived vs. PixelLab sprites.
