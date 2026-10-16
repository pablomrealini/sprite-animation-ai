# Dedicated AI tools for generating and animating 2D game sprites (state as of October 2026)

Scope: purpose-built sprite tools only. General image-to-video models (Veo, Kling, etc.), the video→sprite-sheet post-processing pipeline, and skeletal/ComfyUI/3D routes are covered in sibling notes and are referenced here only where a sprite tool wraps them.

Research date: 15 Oct 2026. Reddit could not be crawled (blocked to the research agent's user agent), so "real user" evidence comes from Hacker News, itch.io, independent blogs and dated hands-on articles. Many 2026 "comparison" pages are written by competing vendors (Ludo, SpriteCook, Gamelabs, Sorceress, Sprite-AI). They are flagged where used.

---

## 1. PixelLab (pixellab.ai): what it does today, limits, export, pricing, API/MCP, licensing

### Takeaway
PixelLab is the most complete pixel-art-only sprite tool in Oct 2026. It has a character creator (4/8 directions), several animation engines (text-to-animation, skeleton, a MiniMax-named "PixMiniMax" beta, interpolation, animation editing), tilesets, an Aseprite plugin, a REST API and a hosted MCP server. Its MCP `animate_image` tool, and "Animate with Text" from a reference image, accept images made elsewhere. The hard ceiling is resolution: animation tops out around 256×256 px, and some modes are limited to 64 or 128 px. It is a pixel-art tool, not an HD-illustration tool.

### Cited Findings
**Features (official docs, 2026)**
- Character creator generates a character from text in 4 or 8 directions (S, SE, E, NE, N, NW, W, SW) and adds walk/run/idle/attack animations. Other features: a map editor with Wang tilesets, and a "Game Builder" agent that edits and deploys a Phaser 4 + TypeScript project (it writes code, not art). — [PixelLab llms.txt](https://www.pixellab.ai/llms.txt)
- Animation tools listed: "Animate with text (new)", "Animate with text (Pro)", "Animate with skeleton", "Create animations (automatic)", "Interpolation", "Edit animation (Pro)". The MCP tool `animate_image` animates any image, not only PixelLab characters. — [PixelLab llms.txt](https://www.pixellab.ai/llms.txt)
- Camera views: low top-down, high top-down, sidescroller. Free-text action descriptions are accepted, so custom actions are possible. "Animate with Text (New)" keeps the first frame identical to the uploaded reference. Skeleton animation can reuse existing frames as templates. — [PixelLab llms-full.txt](https://www.pixellab.ai/llms-full.txt)
- The "Create 8-Directional Sprite (Pro)" tool accepts concept images up to 1024×1024 and outputs frames up to 168×168. This is the documented route for turning an external concept (e.g., a GPT image) into a pixel sprite with 8 directions. — [PixelLab llms-full.txt](https://www.pixellab.ai/llms-full.txt)

**Size and frame limits (official docs and API page, 2026)**

| Mode | Max canvas | Frames |
|---|---|---|
| Animate with Text (New) / text v3 | 256×256 (w×h×frames ≤ 524,288, so 256² allows 4–8 frames and 64² up to 16) | 4–16, even |
| Animate with Text (Pro) / text v2 | 256×256 | 4, 9 or 16 |
| Animate with Skeleton (classic) | 128×128 (docs also list 16–256 square canvases; Tier 1) | n/s |
| Skeleton v3 (beta) | 256×256 | 3–15 |
| PixMiniMax (beta, Tier 1+) | 256×256 | 4–40, multiples of 4 |
| Animation to Animation | 128 (Tier 2) | depends on size |
| Create Animations (Automatic) | 64×64 (Tier 1) | n/s |
| Interpolation | exactly 64×64 | n/s |
| 8 rotations v3 | 256×256, from a south-facing character | 8 views |
| Character Pro / 8-dir Pro | up to 168 | n/a |

— [PixelLab llms-full.txt](https://www.pixellab.ai/llms-full.txt); [PixelLab API page](https://www.pixellab.ai/pixellab-api)
- Image generation is larger: Pixflux up to 400×400 (Tier 2+; 200×200 free, 320×320 Tier 1). "Create S-XL image" and Pro tools go up to 512×512. — [PixelLab llms-full.txt](https://www.pixellab.ai/llms-full.txt); [PixelLab API page](https://www.pixellab.ai/pixellab-api)
- A competitor comparison and GameDev AI Hub (2026) both cite a ~128×128 animation cap. That matches the classic skeleton endpoint but is out of date for the 256-px v3 / PixMiniMax endpoints. — [GameDev AI Hub](https://gamedevaihub.com/retro-diffusion-vs-pixellab/); [Gamelabs vs PixelLab (competitor)](https://gamelabstudio.co/blog/gamelabs-studio-vs-pixellab)

**Export**
- Characters export as sprite sheets or individual frames "structured for direct import into game engines". Skeletons can be saved as images or Aseprite files. GIF/ZIP export is not mentioned in the docs. — [PixelLab llms.txt](https://www.pixellab.ai/llms.txt); [PixelLab llms-full.txt](https://www.pixellab.ai/llms-full.txt)
- Tilesets export as Wang tilesets (usable in Sprite Fusion), dual-grid 15-tile sets, and 3×3 sets. — [PixelLab llms-full.txt](https://www.pixellab.ai/llms-full.txt)

**Pricing (subscription; the official pricing widget did not render for the crawler)**
- Tiers: Pixel Apprentice $12/mo (2,000 generations), Pixel Artisan $24/mo, Pixel Architect $50/mo (10,000 generations); 40-generation free trial. — [Cinevva guide, 4 Sep 2026](https://app.cinevva.com/guides/ai-pixel-art-generators)
- Ludo's Oct 2026 comparison (competitor) lists $12/mo (2,000 images; $8.25/mo yearly) and $50 Architect (10,000). — [Ludo: best AI sprite generators, Oct 2026](https://ludo.ai/compare/best-ai-sprite-generators)
- A Dec 2025 hands-on reviewer reports basic models cost 1 credit per request and newer Pro models 40 credits, with loyalty discounts capping at $9/mo (Tier 1) and $22/mo (Tier 2). — [Jonathan Yu review, 31 Dec 2025, upd. 7 Feb 2026](https://www.jonathanyu.xyz/2025/12/31/pixellab-review-the-best-ai-tool-for-2d-pixel-art-games/)
- Older undated figures ($10/$30/$50 for 1,000/3,000/6,000 generations) are probably stale. — [cutout.pro](https://www.cutout.pro/learn/pixellab/)
- Tier gating: skeleton animation, Pro tools and tilesets need Tier 1. Animation-to-Animation, Instant Character and Multi-image need Tier 2. The trial does not support the Aseprite extension. — [PixelLab llms-full.txt](https://www.pixellab.ai/llms-full.txt)
- Generation costs inside the subscription: Animate with Text (New) at 64×64 costs 1/2/3 generations for 4/8/16 frames. At 128×128 it costs 3/5/9; at 256×256 it costs 9 for 4 frames. Animate with Text (Pro) costs 10–25 depending on size. — [PixelLab llms-full.txt](https://www.pixellab.ai/llms-full.txt)

**API (pay-per-call USD estimates, official API page, 2026)**
- Base URL `https://api.pixellab.ai/v2`, Bearer token, OpenAPI schema, Python and JS SDKs. — [PixelLab llms.txt](https://www.pixellab.ai/llms.txt)
- Example per-call prices:
  - animate-with-text v3: 32×32/4 frames $0.0221; 256×256/8 frames $0.0302; 128×128/16 frames $0.0424
  - skeleton v3: $0.0436 (3 frames) to $0.0622 (15 frames)
  - PixMiniMax: 64/4 frames $0.0178; 256/40 frames $0.0787
  - Pro animate-with-text v2: up to $0.15 (≤256 px)
  - 8 rotations v3: $0.0293–$0.0377
  - animate-character (per direction): v3 4 frames $0.0129–0.0145; Pro $0.08–0.15
  — [PixelLab API page](https://www.pixellab.ai/pixellab-api)

**MCP / plugins**
- Hosted MCP at `https://api.pixellab.ai/mcp` (same Bearer token). Creation jobs are async, roughly 30 s to 5 min, polled via `get_*`. Tool groups cover images (incl. `animate_image`), characters, objects, tiles, UI, account and Game Builder. Documented clients: Claude Code, Claude Desktop, Cursor, Windsurf, ChatGPT and others. — [PixelLab llms.txt](https://www.pixellab.ai/llms.txt)
- GitHub repo `pixellab-code/pixellab-mcp`: tools `create_character` (4/8 dirs), `animate_character`, `create_tileset`, `create_isometric_tile`. It has 42 stars, 17 commits and 8 open issues, and is not open-source licensed ("© 2025 PixelLab. All rights reserved"). — [GitHub pixellab-mcp](https://github.com/pixellab-code/pixellab-mcp)
- Official Aseprite plugin (needs Aseprite ≥ v1.3.7; open source; repo `pixellab-code/aseprite-pixellab-plugin`) and a Pixelorama plugin. A reviewer says the Aseprite plugin gets the latest features and the web tool has fewer features. — [PixelLab llms-full.txt](https://www.pixellab.ai/llms-full.txt); [PixelLab llms.txt](https://www.pixellab.ai/llms.txt); [Jonathan Yu review](https://www.jonathanyu.xyz/2025/12/31/pixellab-review-the-best-ai-tool-for-2d-pixel-art-games/)

**Licensing / training data**
- ToS (last updated 2025-11-23):
  - "You own the copyrights to your creations"; commercial and non-commercial use is allowed. No free-vs-paid distinction appears in the ToS.
  - Outputs may not be used to train other models without written permission.
  - PixelLab does "not use any user inputs or generated content to train our models".
  - No IP warranty or indemnity; the service is provided "as is".
  — [PixelLab ToS](https://www.pixellab.ai/termsofservice)
- Models are described only as custom models "built on Stable Diffusion techniques". No training-data provenance claim was found. — [PixelLab llms.txt](https://www.pixellab.ai/llms.txt)
- The FAQ says AI assets can be used in Steam games and quotes Steam's pre-generated vs live-generated AI disclosure categories. — [PixelLab FAQ](https://www.pixellab.ai/docs/faq)

### Inferences
- For a GPT-made concept, the documented PixelLab path is to upload it to the 8-Directional Pro tool (concept up to 1024², output ≤168 px). Another path is to downscale it with image-to-pixel-art and then use it as the reference/first frame for Animate with Text, or `animate_image` via MCP. Either way the character becomes pixel art ≤256 px. It will not stay an HD illustration.
- "PixMiniMax" (4–40 frames, priced by generation time) is most likely a pixel-adapted wrapper around a MiniMax/Hailuo video model. This is inferred from the name and pricing; PixelLab does not document it. If so, PixelLab now offers both the video-model route and the skeleton route, under pixel constraints.
- API costs are very low: cents per animation. Automation via MCP from Claude Code is realistic and cheap.

### Gaps
- The official pricing page did not render. Tier prices come from third parties (Sep–Oct 2026), and two of them agree.
- No official frame count is documented for the character-creator template animations or classic skeleton mode.
- No YouTube or Reddit hands-on reviews could be retrieved. No shipped Steam game publicly credited to PixelLab was found.

---

## 2. Retro Diffusion (retrodiffusion.ai / Astropulse)

### Takeaway
Retro Diffusion is a pixel-art model family with a strong ethical-provenance claim: trained on licensed art from Astropulse and consenting pixel artists. Its web/API "advanced animations" do take an uploaded input image. They support walk, idle, jump, crouch, attack, destroy, custom action, subtle motion and 8-direction rotate at 32–256 px with 4–16 frames, priced at $0.10–$0.25 per call. The one-time-purchase Aseprite extension is static-only, with no animation, and is being phased out for a standalone editor.

### Cited Findings
- API animation styles (official GitHub api-examples):
  - Prompt-only: `rd_animation__four_angle_walking` / `four_angle_walking_idle` at 48 px, $0.07; `small_sprites` at 32 px, $0.07; `any_animation` at 64 px, $0.25; `big_animation` at 128 px, $0.25; `vfx`, `battle_sprites` (idle/walk/jump/attack) and `8_dir_rotation`.
  - Image-input ("advanced"): `rd_advanced_animation__walking / idle / jump / crouch / attack / destroy` at 32–256 px, $0.14; `custom_action` and `subtle_motion` at $0.25; `rotate` (8 views) at $0.10. `input_image` is required, and the docs call advanced animations "the most powerful workflow".
  - Frames via `frames_duration`: 4, 6, 8, 10, 12 or 16.
  - Output is a transparent GIF by default, or a PNG spritesheet with `return_spritesheet: true` (3×3 sheet for rotate).
  - Free `check_cost` dry runs.
  — [Retro Diffusion api-examples (GitHub)](https://github.com/Retro-Diffusion/api-examples)
- Image models: rd_fast ~$0.03/image, rd_plus $0.06, rd_pro $0.18 (up to 9 reference images), 64–384 px. — [Retro Diffusion api-examples](https://github.com/Retro-Diffusion/api-examples)
- An official MCP server exists (`estimate_inference_cost` tool, prepaid credits that don't expire). It is listed as used by Replicate, Poe and Scenario (third-party directory claim). — [mcpservers.org listing](https://mcpservers.org/servers/retro-diffusion/retro-diffusion-mcp)
- The model is also on Replicate as `retro-diffusion/rd-animation`, with presets at fixed sizes (four_angle_walking 48 px, small_sprites 32 px, vfx 24–96 px) and spritesheet PNG output. — [Replicate rd-animation](https://replicate.com/retro-diffusion/rd-animation/versions/a9f33da7d9a985064dbc2d99621b87da5b8a22ed4d412c3a1c34ab4b807a6d8f/api)
- Web credits run from $5 (250) to $50 (3,500). The Aseprite extension is a one-time $65 (Lite $20). — [Cinevva guide, Sep 2026](https://app.cinevva.com/guides/ai-pixel-art-generators); [itch.io Retro Diffusion](https://astropulse.itch.io/retrodiffusion)
- Aseprite extension:
  - Runs locally (GPU needed: 64×64 takes <2 s on an RTX 3090 and ~2.5 min on a GTX 1050 Ti). Version 15.0.0, status "In development".
  - A recent developer reply says the extension "can't handle any kind of animation" (the website can). Local models differ from the website's.
  - The developer says it is being phased out for a standalone native editor, expected free for existing owners "within the year".
  - Comments complain about installs, AMD support and update pace.
  — [itch.io Retro Diffusion](https://astropulse.itch.io/retrodiffusion)
- Training-data claim: "trained on licensed assets from Astropulse and other pixel artists, with their consent". It appears only in the developer's own listings; no independent verification was found, and the local and web models differ. — [itch.io Retro Diffusion](https://astropulse.itch.io/retrodiffusion); [itch.io Lite](https://astropulse.itch.io/retrodiffusionlite)
- Ownership: the developer said in a comment, "Yes, you own the images generated by it." — [itch.io Retro Diffusion](https://astropulse.itch.io/retrodiffusion)
- GameDev AI Hub (2026):
  - Pros: RD has more "authentic" pixel-grid output.
  - Cons: confusing site/extension split, no engine-ready export, manual sheet assembly.
  - Suggested combo: base sprites in RD, then rotations and animation in PixelLab.
  - It evaluates neither RD animation quality nor RD rotations (its "no rotations" claim conflicts with the API docs above).
  — [GameDev AI Hub](https://gamedevaihub.com/retro-diffusion-vs-pixellab/)

### Inferences
- Retro Diffusion is the strongest choice when provenance matters, because of its consent-trained claim. Its image-input advanced animations are a direct alternative to PixelLab for animating an existing (already pixelized) character, at ~$0.14–0.25 per animation.
- The product is in transition (extension → standalone editor), so tooling may change soon.

### Gaps
- No hands-on reviews of RD's advanced (image-input) animation quality or loop closure were found.
- The training-data claim is self-reported only. Whether it covers the newest web/animation models is not stated.

---

## 3. Ludo.ai Sprite Generator

### Takeaway
Ludo has become a full "animate anything" sprite tool. You can upload your own static art and animate it from a text prompt, up to 3 keyframes, a reference video, or 641 motion presets. It supports up to 64 frames and 5 s, frames 32–384 px or native size, 8 directions, 32 styles (pixel and non-pixel), Fix Loop, and engine exports, plus API/MCP/CLI. It is one of the few dedicated tools that targets HD and non-pixel sprites as well as pixel art. Its per-second credit pricing strongly suggests a video-model backbone.

### Cited Findings
- Animation inputs:
  - Uploads of your own static character art are supported (best with sprite only; background removal available).
  - Drivers: text motion prompt, up to 3 keyframe poses, reference video (~4 s ideal), or 641 presets in 34 categories.
  - Up to 5 s; sheets of 4/9/16/25/36/49/64 frames max.
  - Frame size 32–384 px, plus "Max" (native) and "True Size", and a 1.5× AI upscale.
  — [Ludo Sprite Generator page, Oct 2026](https://ludo.ai/features/sprite-generator)
- Directions: 8 compass directions and 5 camera perspectives (Side, Isometric, Top-Down, Tactical, Hero). "Change Direction" turns a still; "New Direction" re-renders a finished animation. — [Ludo Sprite Generator](https://ludo.ai/features/sprite-generator)
- Styles and models:
  - 32 styles, including 5 pixel styles (4 snap to a strict grid).
  - Models: Hydra (default, adds a sound effect), Hydra+, Forge and Forge Pixel.
  - "Fix Loop" is a one-click repair for non-looping animations.
  — [Ludo Sprite Generator](https://ludo.ai/features/sprite-generator)
- Exports: transparent PNG sheet, TexturePacker JSON, frames ZIP, GIF, MP4, Animation Pack ZIP, for Unity, Godot, Unreal and GameMaker. Also a Unity plugin. — [Ludo Sprite Generator](https://ludo.ai/features/sprite-generator)
- Credit costs:
  - Hydra 3 credits/s; Hydra+ 4/s; Forge and Forge Pixel 1.5/s.
  - Fix Loop and Improve Details 1/s.
  - New Direction 3–4/s (3 s minimum); new static sprite 0.5.
  — [Ludo Sprite Generator](https://ludo.ai/features/sprite-generator)
- Plans:
  - Indie $20/mo ($15/mo yearly) with 250 credits across all asset types.
  - Pro $50/mo with unlimited web image generation plus API/MCP/CLI (API calls use credits).
  - Studio $300/mo for 10 seats (per Cinevva).
  - 30-credit free trial, watermarked, with exports locked until you subscribe.
  - "You own generated assets and can use them commercially on every plan."
  — [Ludo comparison, Oct 2026 (vendor)](https://ludo.ai/compare/best-ai-sprite-generators); [Ludo vs AutoSprite (vendor)](https://ludo.ai/compare/ludo-vs-autosprite); [Cinevva](https://app.cinevva.com/guides/ai-pixel-art-generators)
- Cinevva (Sep 2026) notes sprite generation draws from a shared credit pool, so the real cost per sprite is higher than the headline price. — [Cinevva guide](https://app.cinevva.com/guides/ai-pixel-art-generators)

### Inferences
- A 5-s Hydra animation costs 15 credits, so the 250-credit Indie plan covers roughly 16 such animations a month. That is not cheap for iteration.
- Ludo is a packaged version of the "image-to-video → sheet" pipeline the team already validated with Veo. It adds keyframe control, reference-video motion transfer, loop fixing, direction re-rendering and engine export. Whether its underlying model matches Veo's quality is unverified.

### Gaps
- No independent hands-on reviews of Ludo sprite animation quality were found. All detailed claims come from Ludo's own pages.
- The underlying video models behind Hydra and Forge are not disclosed.

---

## 4. AutoSprite (autosprite.io)

### Takeaway
AutoSprite is an "animation-first" tool. It takes one uploaded character image (or a text prompt), generates short video clips, and slices them into engine-ready sheets with atlas metadata, per-move FPS and loop hints. It has idle/walk/run/jump/attack presets plus a ~100-clip motion library, custom moves and motion transfer from video, 8-direction isometric packs, a Unity extension, and a REST API and MCP. Pricing is cheap ($12–$29/mo). Independent reviews are essentially absent.

### Cited Findings
- Input and motion:
  - Upload a single character image or start from a prompt.
  - Presets: idle, walk, run, jump, attack; custom moves via text, storyboard keyframes and reference images; motion transfer from existing motions or video.
  - Per-move frame rate; 8-direction isometric movement sets; side-scroller and top-down support.
  — [AutoSprite homepage](https://www.autosprite.io/)
- Exports: PNG spritesheet with atlas file, frames ZIP, loop hints in metadata. Engines: Unity, Unreal, Godot, GameMaker, Phaser, RPG Maker, Astrocade. — [AutoSprite homepage](https://www.autosprite.io/)
- API and MCP: REST API (characters, animations, jobs, downloads) and an MCP server for Claude Code, Cursor, Codex, Windsurf, Cline and Gemini CLI. — [AutoSprite homepage](https://www.autosprite.io/)
- Per Ludo's competitor comparison (Oct 2026):
  - It generates short video clips and slices them into frames; idle is "typically 6–12" frames, with up to 64 selectable.
  - The 8-direction isometric pack costs 15 credits per action. Its MCP has 33 tools.
  - Plans: Free (15 credits/mo + 3/day login, 2 sheet exports/mo), Starter $12/mo (500 credits ≈ 100 sheets), Pro $29/mo (1,500 credits, rollover).
  - The pricing page and docs disagree on whether API/MCP starts at Starter or Pro.
  - Its FAQ admits AI "can alter minor character details".
  - Ownership: users own outputs, subject to rights in inputs, with no originality/non-infringement warranty.
  — [Ludo vs AutoSprite (vendor)](https://ludo.ai/compare/ludo-vs-autosprite)
- Its itch.io page claims 12 art styles but shows "In development" status and a single rating. AlternativeTo shows no reviews. — [AutoSprite itch.io](https://autosprite.itch.io/autosprite); [AlternativeTo](https://alternativeto.net/software/autosprite/about)

### Inferences
- AutoSprite is functionally "Veo-style video + automatic slicing + engine export". It is complementary to what the team does by hand, and a cheap way to test the packaging layer on their own GPT concept. The underlying video model is undisclosed, so quality relative to Veo must be tested.

### Gaps
- The underlying video model, max output resolution and HD vs pixel limits are not stated.
- No hands-on reviews were found. A "Games Made with AutoSprite" section exists, but no titles were retrieved.

---

## 5. God Mode AI (godmodeai.co)

### Takeaway
God Mode AI animates one uploaded character image into sprite sheets from an action library, with side-scrolling, 8-direction isometric and top-down views. Notably, it also auto-rigs a single image into a Spine 3.5–4.2 skeleton. It is the only dedicated tool found with Spine export, which matters for HD games. It is expensive per credit, its subscription makes generations public, and its 2025 Show HN drew heavy quality criticism.

### Cited Findings
- Features:
  - Animations from a single image, plus a "rich action library" (combat, movement, special) and a custom action tool.
  - Directions: side-scrolling, 8-direction isometric, top-down. A pixel-art sprite generator uses a low-res model.
  - Exports: transparent sprite sheets, MP4, transparent WebM, GIF, Spine 3.5–4.2 (skeleton.json + atlas + PNG), and FBX/GLB for 3D.
  - Commercial licensing is included. REST API and "MCP & Agent Skills" pages are listed without details.
  — [God Mode AI homepage](https://www.godmodeai.co/)
- Pricing: $29/mo for up to 200 *public* generations, or credit packs ($32 for 30, $100 for 125). New accounts get 3 credits; all purchases are final. — [God Mode AI homepage](https://www.godmodeai.co/)
- The Spine Show HN (2025) claims you can "directly apply 2k+ animations" with auto-rigging. A commenter questioned bone accuracy for non-standard characters. — [Show HN: 2D Spine Animation AI](https://news.ycombinator.com/item?id=45438288)
- Show HN (6 Jun 2025, 162 points, 116 comments) for the sprite generator (godmodeai.cloud):
  - Criticism dominated: costume details lost mid-animation (gloves vanish), AI "fuzziness", jitter, cycles that don't loop, a pixel-art character distorted and restyled. Comments included "need quite bit of hand editing" and "not good, by any metric".
  - One user still called it "a huge time boost". Queue and payment bugs were reported at launch.
  - **This is older than mid-2025 and possibly stale.**
  — [HN item 44204181](https://news.ycombinator.com/item?id=44204181)
- Ludo (competitor) ranks it last of 8: "less polished"; public-only generations don't suit private team work. — [Ludo comparison](https://ludo.ai/compare/best-ai-sprite-generators)

### Inferences
- God Mode's Spine auto-rig from one image is the most interesting feature for HD games. It is a third route between frame-by-frame video and hand rigging. But the bone-accuracy doubts, and the public-generation subscription (a leak risk for unannounced IP), make it a "test with throwaway art first" option.

### Gaps
- No 2026 hands-on reviews were found. Max resolution, frame counts and underlying models are not stated.

---

## 6. Scenario (scenario.com)

### Takeaway
Scenario is a studio platform for custom-trained style/character models plus a hub of third-party image and video models. For animation it routes you to general video models (Seedance, Pixverse, Kling motion control, Wan Animate), dedicated apps (Run Cycle Spritesheet, 8-Direction Sprite Generator) and the hosted Retro Diffusion animation model. Its official spritesheet workflow is largely manual frame picking. It is strongest for style consistency across many assets, not for animation itself.

### Cited Findings
- Official spritesheet guide (updated ~Aug/Sep 2026):
  1. Make a side-view base image (Flux, Gemini, a custom model, or an upload).
  2. "Convert to Video" with Seedance 1 Lite/Pro or Pixverse v4.5 (first/last frame).
  3. Pick key poses manually or with a video editor, then assemble the sheet in an external tool.
  - Loop tip: swap first and last frames. The guide admits motion "may be slow or slightly imperfect".
  — [Scenario help: Create spritesheets](https://help.scenario.com/articles/9088582240-create-spritesheets-with-scenario)
- Apps: the Character Run Cycle Spritesheet app (one portrait in, run cycle with slicing out) and an 8-Direction Sprite Generator (front-facing image to multiple angles). Its blog recommends prompting GPT Image 2 or Gemini 3.1 for grid sheets. — [Scenario app](https://scenario.com/apps/character-run-cycle-spritesheet); [Scenario gaming apps](https://help.scenario.com/en/articles/scenario-apps-for-gaming); [Scenario blog](https://www.scenario.com/blog/ai-sprite-generator)
- Ludo (competitor) says Scenario hosts the Retro Diffusion animation model (walk/run/idle), exports GIF and sprite sheets, has a REST API, an MCP server and "Pixel Snapper", and is SOC 2 Type II. — [Ludo comparison](https://ludo.ai/compare/best-ai-sprite-generators)
- Pricing (no effective date; © 2026): Starter $15/mo (1,500 credits), Pro $45/mo (5,000, custom training), Max $75/mo (10,000), Enterprise custom. Free tier is 50 daily credits, for personal/evaluation use only. Paid plans include a commercial license. Video credit costs vary by model. — [Scenario pricing](https://www.scenario.com/pricing)
- SpriteCook (competitor) says Scenario sprites come from general models, you slice them yourself, and animation can drift in pixels. — [SpriteCook vs Scenario (vendor)](https://www.spritecook.ai/compare/scenario)

### Inferences
- For this team, Scenario's value is training a house style or character model on their own art to keep GPT-concept variants consistent. Animation inside Scenario is just access to the same video models they can call elsewhere.

### Gaps
- No credit costs per video/animation, and no independent animation-quality reviews.

---

## 7. Layer.ai

### Takeaway
Layer is a studio-oriented generation platform (style training, 2D/3D/video, LiveOps). Its sprite feature generates walk-cycle-type sheets from one image on a shared ground line and anchor, with uniform-cell PNG export. Pixel art uses retro "machine registers" (NES, GBA, etc.). It has API/MCP/CLI and usage-based pricing. There is little evidence of deep animation tooling.

### Cited Findings
- Cycles are generated as one sheet, so frames share scale, ground line and anchor. Walk cycles are the documented example (8-frame example); other action types are unclear.
- A general "Animate an image" feature makes short video loops.
- Export: split and pack to uniform-cell transparent PNGs, for Unity, Godot, GameMaker and Unreal Paper2D.
- Pixel palettes: C64, NES, Game Boy, Mega Drive, GBA, Amiga, and custom hex.
- Pricing: consumption-based Creative Units, from $10/mo for 300 CUs, no seat fees. REST API, MCP and CLI are available.
- It claims "400+ game studios".
— [Layer sprite generation page](https://www.layer.ai/use-cases/sprite-generation)
- Ludo (competitor) says extra CUs cost $60 per 1,000, that costs rise quickly with video, and that Layer is focused on marketing and LiveOps. — [Ludo comparison](https://ludo.ai/compare/best-ai-sprite-generators)
- Cinevva lists "commercial licence on all plans" and "limited" animation. — [Cinevva guide](https://app.cinevva.com/guides/ai-pixel-art-generators)

### Inferences
- Layer is not a better animation path than Veo for a 2-person team. It is relevant mainly for a studio-scale style-locked asset volume.

### Gaps
- Licensing and IP terms, training-data claims and max resolution are not on the sprite page (they are in the Trust Center, not retrieved). No hands-on animation reviews.

---

## 8. Leonardo.ai

### Takeaway
As of Oct 2026, Leonardo has no dedicated sprite or animation feature. "Motion" is generic image-to-video (Motion 2.0, plus third-party models such as Veo 3.1). Sprite sheets require prompting a grid layout or extracting video frames yourself. It is a general concept/image tool, not a sprite tool.

### Cited Findings
- Leonardo API docs: Motion 1.0 (SVD) is retired after 17 Jun 2026. Sora 2 and Sora 2 Pro are removed from the API as of 9 Jul 2026, and Veo 3.1 models are recommended instead. — [Leonardo docs: Deprecations](https://docs.leonardo.ai/docs/deprecations-changes)
- Ludo (competitor) says no game presets or sprite models are marketed by Leonardo as of Aug 2026, and there is no image → engine-ready sheet path. SpriteCook (competitor) says Leonardo animation is video, not game frames. — [Ludo: Leonardo alternatives](https://ludo.ai/compare/leonardo-alternatives); [SpriteCook vs Leonardo](https://www.spritecook.ai/compare/leonardo-ai)
- Pricing: free 150 tokens/day (non-commercial); Apprentice $12/mo (8,500 tokens), then $30 and $60 tiers with commercial rights. Output is not grid-based, so pixel art needs downscaling and cleanup. — [Cinevva guide](https://app.cinevva.com/guides/ai-pixel-art-generators)

### Inferences
- Leonardo is effectively a reseller of Veo 3.1 and similar models. It offers no advantage over calling Veo directly for this team.

### Gaps
- None material.

---

## 9. SEELE (seeles.ai)

### Takeaway
SEELE is an AI game-creation workspace with a prompt-based sprite sheet generator. It handles text-to-sprite with selectable states, 256/512 px, FPS 4/8/12 and 2–4 s duration, exporting a PNG sheet plus JSON. Animating an uploaded character image is not documented. Licensing is vague.

### Cited Findings
- States: idle, walk, run, jump, attack, hurt, death, dash, climb, shoot, block (multi-select, written into the prompt). — [SEELE sprite sheet generator](https://www.seeles.ai/games/2d/ai-sprite-sheet-generator)
- Controls: duration (still / 2 s / 4 s), target FPS (4/8/12), resolution 256 or 512 px. Frame count and viewpoint are set in the prompt. Export: PNG sprite sheet, JSON metadata, frames. Free credits; paid prices not listed. Commercial terms say only "Review the current Seele usage terms". No API or model information. — [SEELE sprite tool](https://www.seeles.ai/p/tool/sprite)

### Inferences
- SEELE is not a fit for animating an existing GPT concept with identity preservation.

### Gaps
- Upload/reference support, underlying models, pricing and licensing are all unverified.

---

## 10. Notable smaller tools and 2025–2026 newcomers (SpriteCook, FrameSprite, Sprite-AI, SpriteLab, Sprixen, Rosebud, Replicate/fal options, Midjourney, others)

### Takeaway
A wave of 2025–2026 tools wrap general image models (GPT Image 2/2.5, Nano Banana) and video models (MiniMax, Seedance) with sprite-specific packaging: background removal, slicing, style lock, engine export and MCP. The most relevant for animating an existing image in HD or pixel art are SpriteCook and FrameSprite. Pixel-only budget tools (Sprite-AI, SpriteLab, Sprixen) are cheap but thin. Retro Diffusion's model is directly callable on Replicate.

### Cited Findings
- **SpriteCook** (spritecook.ai):
  - Pixel and HD/detailed styles. It animates an existing image into a looping cycle (idle, walk, run, attack, jump, custom).
  - Saved theme for palette/style consistency; sheet slicing; PNG/sheet export with Unity and Godot 4 guides.
  - 40 free credits/mo. REST API plus hosted MCP (`npx spritecook-mcp setup`, Claude Code/Codex/Cursor).
  - "Assets you generate are yours to use commercially."
  - Frame, direction and resolution limits are not stated.
  — [SpriteCook](https://www.spritecook.ai/)
- **FrameSprite** (framesprite.com):
  - 8 styles (pixel, retro, clean HD, chibi, anime, cartoon, realistic, painterly); 14 action presets; eight-direction identity lock.
  - Models disclosed: GPT Image 2.5 for images and MiniMax H3 for animation (routes checked 30 Sep 2026). Failed generations are refunded.
  - Page last updated 11 Sep 2026.
  — [FrameSprite](https://www.framesprite.com/)
  - A search snippet says its changelog shows motion transfer from a 2–5 s reference video (6 Oct 2026) and that 8-direction animation is "experimental"; not verified on the page. — [search result: FrameSprite](https://www.framesprite.com/)
- **Sprite-AI** (sprite-ai.art): pixel art; animator for 32×32 to 256×256 with custom prompts (Sidehunt, May 2026). Ludo says the animator does 8–24 frames, 32–400 px, sheet plus JSON atlas, $8/mo launch price. Cinevva (Sep 2026) says "no animation", which conflicts. — [Sidehunt](https://sidehunt.io/launches/project-sprite-ai); [Ludo comparison](https://ludo.ai/compare/best-ai-sprite-generators); [Cinevva](https://app.cinevva.com/guides/ai-pixel-art-generators)
- **SpriteLab**: animate mode from a described motion; 4/8 directions on paid plans; 16–64 px micro mode; REST API and MCP on every plan; commercial license even on the free tier; $7.99/mo. — [Ludo comparison](https://ludo.ai/compare/best-ai-sprite-generators)
- **Sprixen**: small-sprite animation, "Style Lock" (palette, resolution, proportions), $10/mo. — [Cinevva](https://app.cinevva.com/guides/ai-pixel-art-generators)
- **Rosebud AI**: its sprite-sheet animation generator was "still in development" per an undated page (possibly stale). PixelVibe offers sprite-generation models; no 2026 animation launch was found. — [Rosebud sprites animation](https://rosebud.ai/sprites-animation)
- **Replicate / fal.ai**:
  - Replicate hosts `retro-diffusion/rd-animation`. — [Replicate](https://replicate.com/retro-diffusion/rd-animation/versions/a9f33da7d9a985064dbc2d99621b87da5b8a22ed4d412c3a1c34ab4b807a6d8f/api)
  - No dedicated sprite model on fal.ai was found. An open-source "sprite-sheet-creator" uses fal-hosted Nano Banana and GPT Image 2 for 4-frame 2×2 walk sheets. — [GitHub sprite-sheet-creator](https://github.com/blendi-remade/sprite-sheet-creator)
  - An open FLUX.2 Klein LoRA makes 32×32 pixel walk/jump sheets. — [HF LoRA](https://huggingface.co/svntax-dev/pixel_spritesheet_4walk_small_lora_v1/blob/main/README.md)
- **Midjourney**: V1 video (18 Jun 2025) is image-to-video with `--loop` and end-frame options. No sprite-sheet, transparency or frame-accurate features were found. — [Geeky Curiosity on MJ looping](https://geekycuriosity.substack.com/p/midjourneys-new-video-features-looping); [AI Lab: MJ video](https://theailab.substack.com/p/its-official-midjourney-has-video)
- **Sprite Fusion** is a tilemap editor, not an animation tool. PixelLab exports Wang tilesets usable in it. — [PixelLab llms-full.txt](https://www.pixellab.ai/llms-full.txt)
- **Meshy / Cascadeur / Kaedim**: 3D tools, relevant only to the 3D→2D route covered in the sibling note. A May 2026 test of Meshy found a 42K-tri mesh that needed ~25 min of retopo. — [Techsy, Sep 2026](https://techsy.io/en/blog/best-ai-game-asset-generators)

### Inferences
- Most "new" 2026 sprite animators are thin wrappers over the same frontier video models (MiniMax, Seedance, likely Veo/Kling). They differ in packaging (identity lock, slicing, loop repair, engine/MCP integration), not in a fundamentally different animation technique. The only genuinely different techniques in this space are PixelLab's skeleton-driven pixel animation and God Mode's single-image Spine auto-rig.

### Gaps
- Not checked in depth: Krea, Hotpot, Kaedim, Spritesheets.ai, Sorceress Auto-Sprite, Gamelabs Studio. They were found only via competitor or SEO pages (e.g., [Gamelabs vs PixelLab](https://gamelabstudio.co/blog/gamelabs-studio-vs-pixellab), [Sorceress blog](https://sorceress.games/blog/how-to-make-a-sprite-sheet-in-2-minutes-with-ai-in-2026)), with no verifiable specs.
- No Product Hunt sprite-tool launch could be confirmed for 2026.

---

## 11. Cross-cutting: can these tools animate an EXISTING character image (e.g., made in GPT) while preserving identity?

### Takeaway
Yes, for most tools in 2026, with caveats. Pixel tools (PixelLab, Retro Diffusion) accept an uploaded image but convert it to pixel art at ≤256 px. HD-capable tools (Ludo, AutoSprite, God Mode, SpriteCook, FrameSprite) accept an uploaded illustration and run it through video models, so they inherit video-model drift. Every hands-on report still describes detail drift and manual cleanup.

### Cited Findings
| Tool | Upload own image? | Output style / max size | Directions | Evidence |
|---|---|---|---|---|
| PixelLab | Yes (`animate_image`; reference/first frame in Animate with Text; 8-dir Pro takes concepts up to 1024²) | Pixel only; anim ≤256×256 | 4/8 | [llms.txt](https://www.pixellab.ai/llms.txt), [llms-full.txt](https://www.pixellab.ai/llms-full.txt) |
| Retro Diffusion | Yes (advanced animations require `input_image`) | Pixel only; 32–256 px | rotate → 8 views | [api-examples](https://github.com/Retro-Diffusion/api-examples) |
| Ludo | Yes | 32 styles incl. non-pixel; 32–384 px or native | 8 + 5 cameras | [Ludo sprite generator](https://ludo.ai/features/sprite-generator) |
| AutoSprite | Yes | n/s (12 styles claimed) | 8-dir iso, side, top-down | [AutoSprite](https://www.autosprite.io/) |
| God Mode AI | Yes (sprites and Spine auto-rig) | Pixel + other; n/s | side / 8-dir iso / top-down | [God Mode AI](https://www.godmodeai.co/) |
| SpriteCook | Yes | Pixel + HD; n/s | n/s | [SpriteCook](https://www.spritecook.ai/) |
| Scenario | Yes (upload → Convert to Video) | Any (general models) | 8-dir app | [Scenario help](https://help.scenario.com/articles/9088582240-create-spritesheets-with-scenario) |
| Layer | "Single character or object image" → sheet | Pixel registers; HD n/s | n/s | [Layer](https://www.layer.ai/use-cases/sprite-generation) |
| SEELE | Not documented (prompt-based) | 256/512 | prompt | [SEELE](https://www.seeles.ai/p/tool/sprite) |
| Leonardo | Only via generic video | Any | none | [Leonardo docs](https://docs.leonardo.ai/docs/deprecations-changes) |

- AutoSprite's own FAQ says AI generation can alter minor character details. — [Ludo vs AutoSprite (citing AutoSprite FAQ)](https://ludo.ai/compare/ludo-vs-autosprite)
- PixelLab (May 2026 test): in an 8-frame top-down walk, "The first six frames held shape and palette beautifully". In frames 7–8 the belt shifted a couple of pixels and the shadow flickered, a fix estimated at ~2 min in Aseprite. The 4-direction set held up better than the animation. — [Techsy, tests May 2026, upd. 6 Sep 2026](https://techsy.io/en/blog/best-ai-game-asset-generators)
- PixelLab text-to-animate keeps the reference as the first frame, but sliding feet in walk cycles, frame nudging and palette unification are still expected by hand. — [GameDev AI Hub](https://gamedevaihub.com/retro-diffusion-vs-pixellab/)
- HN practitioner (2025): generating start and end frames with Nano Banana, then in-between motion with Veo 3, is "astoundingly effective" but "laborious and lacking in ergonomics". — [HN comment 45238184](https://news.ycombinator.com/item?id=45238184)

### Inferences
- For identity preservation, the most reliable pattern is a tool that pins the uploaded image as frame 1. PixelLab Animate with Text does this; Ludo, AutoSprite and FrameSprite use reference/keyframe inputs. Even then, expect accessory drift (belts, gloves, weapons) on frames far from the reference.
- HD tools add ergonomics around a Veo-like process: auto background removal, slicing, loop repair, per-move FPS and engine atlases. That is exactly the "laborious" part the HN commenter describes, so they are complementary to Veo rather than a quality upgrade.

### Gaps
- No controlled side-by-side test was found (same GPT concept animated in PixelLab vs Ludo vs AutoSprite vs Veo). The team would need to run one.

---

## 12. Cross-cutting: licensing, ownership, training-data provenance and Steam/player perception

### Takeaway
All main tools grant output ownership or commercial use on paid plans. Free tiers are sometimes restricted (Scenario and Leonardo free are non-commercial; God Mode's subscription makes outputs public). None offers IP indemnity. Only Retro Diffusion makes a specific "licensed and consented training data" claim, and it is self-reported. PixelLab and others disclose no provenance beyond "custom models". Steam requires disclosing pre-generated AI content regardless of tool.

### Cited Findings
- PixelLab: user owns copyright; commercial OK; no training other models on outputs; no use of user inputs for training; no warranty or indemnity (ToS 2025-11-23). — [PixelLab ToS](https://www.pixellab.ai/termsofservice)
- Retro Diffusion: "licensed assets from Astropulse and other pixel artists, with their consent" (self-claim); the developer says users own outputs. — [itch.io Retro Diffusion](https://astropulse.itch.io/retrodiffusion)
- Scenario: free tier is personal/evaluation only; paid plans include a commercial license. — [Scenario pricing](https://www.scenario.com/pricing)
- Ludo: users own assets, commercial on all plans. — [Ludo vs AutoSprite](https://ludo.ai/compare/ludo-vs-autosprite)
- AutoSprite: users own outputs subject to input rights; no originality or non-infringement warranty. — [Ludo vs AutoSprite](https://ludo.ai/compare/ludo-vs-autosprite)
- God Mode AI: commercial licensing included; $29/mo plan covers "public generations". — [God Mode AI](https://www.godmodeai.co/)
- SpriteCook: "yours to use commercially". FrameSprite: "Commercial game use is allowed under the published terms". SEELE: unspecified. — [SpriteCook](https://www.spritecook.ai/); [FrameSprite](https://www.framesprite.com/); [SEELE](https://www.seeles.ai/p/tool/sprite)
- Leonardo: free tier non-commercial; paid tiers include commercial rights. — [Cinevva](https://app.cinevva.com/guides/ai-pixel-art-generators)
- Steam's Content Survey separates "pre-generated" AI content (made during development) from "live-generated" content. Sprites made with these tools are pre-generated and must be disclosed. — [PixelLab FAQ quoting Steam](https://www.pixellab.ai/docs/faq)
- Player perception: in the God Mode Show HN thread, some commenters said they would avoid games with AI-generated assets, and several comments were flagged. — [HN 44204181](https://news.ycombinator.com/item?id=44204181)
- itch.io has "no-ai" tags across asset and tool stores, and an itch.io comment thread shows AI-accusation disputes over pixel-art packs. — [itch.io no-ai tag](https://itch.io/game-assets/store/tag-animated-sprite/tag-no-ai); [itch.io comment thread](https://pixelslime99.itch.io/buildingforge-urban-edition/comments)

### Inferences
- For a commercial Steam release by known ex-Ironhide developers, Retro Diffusion's consent claim is the only marketing-usable provenance story among dedicated tools, and it applies to pixel art only. For HD, every option runs on undisclosed or frontier video models with no provenance claims. Disclosure on Steam is mandatory either way.

### Gaps
- No tool publishes a dataset card. No indemnity offers were found (enterprise contracts may differ but were not checked). Layer's Trust Center was not retrieved.

---

## 13. Cross-cutting: real practitioner reviews and evidence of shipped games

### Takeaway
Independent hands-on evidence is thin and mostly about PixelLab. Practitioners call it the best pixel-art sprite tool but say outputs are a starting point that needs Aseprite cleanup, especially for walk cycles. Small sprites (≤16 px) are weak. Homepage examples are "cherry-picked". Video-based single-image animators (God Mode 2025) drew harsh criticism for drift, fuzz and broken loops. No shipped commercial game publicly credited to any of these tools was found.

### Cited Findings
- Techsy (tests May 2026): PixelLab is the "best pixel-art and sprite option, with a human pass needed for frame consistency". Generation is the "easy 80%"; cleanup is still manual. — [Techsy](https://techsy.io/en/blog/best-ai-game-asset-generators)
- Jonathan Yu (Dec 2025 / Feb 2026):
  - PixelLab is "the one standout" among the pixel AI tools he tried, with pixel-perfect output versus Midjourney/Gemini.
  - It is weak at 16×16 and below. Docs are often out of date, and experimenting wastes credits.
  - He did not personally test the skeleton, rotation or animation features in depth.
  — [Jonathan Yu review](https://www.jonathanyu.xyz/2025/12/31/pixellab-review-the-best-ai-tool-for-2d-pixel-art-games/)
- HN (~late 2025): PixelLab homepage examples are "extremely cherry-picked". Paying users likely use outputs as a rough start and fix by hand. Walk-cycle leg positioning is still unsolved. — [HN 46001962](https://news.ycombinator.com/item?id=46001962)
- Other HN comments mention PixelLab as having "a ways to go in features and UX, but it shows promise", with a $12/mo price. These came from search snippets; the exact thread is uncertain (one candidate is [HN 43792366](https://news.ycombinator.com/item?id=43792366)).
- A general HN critique (thread title snippet): "The pixel art these models produce continues to look like shit and not be actual [pixel art]". — [HN 42731765](https://news.ycombinator.com/item?id=42731765)
- Another HN commenter on a browser-RTS Show HN said GenAI pixel art "pixels aren't aligned to a traditional grid", which causes fringing. This came from a search snippet; the exact thread was not opened.
- God Mode Show HN (Jun 2025): detail loss, jitter, non-looping cycles, non-humanoids and 16×16 handled poorly, "a huge time boost" despite edits. — [HN 44204181](https://news.ycombinator.com/item?id=44204181)
- An itch.io creator said PixelLab could reproduce their pack's style "with less details". — [itch.io comments](https://pixelslime99.itch.io/buildingforge-urban-edition/comments)
- No source names a Steam game crediting PixelLab sprites. — [search: PixelLab FAQ / Steam](https://www.pixellab.ai/docs/faq)

### Inferences
- The consistent message across sources is that dedicated tools reduce cost per animation to cents or dollars but do not remove the cleanup pass. The pass is smaller for pixel art with frame-1 pinning, and larger for HD video-based outputs.

### Gaps
- Reddit (r/gamedev, r/PixelArt, r/aseprite, r/IndieDev, r/StableDiffusion) could not be accessed, so Reddit sentiment is unverified.
- No YouTube reviews could be retrieved.
- Several "reviews" (knowara, tryanai, cutout.pro) read as SEO/affiliate content and were not relied on for quality claims.

---

## 14. Overall: which tool is best for (a) pixel-art sprites, (b) HD illustrated sprites like Kingdom Rush, (c) animating an existing GPT concept

### Takeaway
- **(a) Pixel art:** PixelLab is the consensus pick for animated, multi-direction characters. Retro Diffusion is the pick when consent-trained provenance or authentic grid quality matter; its image-input animations at $0.14–0.25 each are a real alternative.
- **(b) HD illustrated:** no dedicated tool is clearly better than the team's Veo pipeline. Ludo, AutoSprite, SpriteCook and FrameSprite are video-model wrappers that add convenience (slicing, loop repair, directions, engine export). God Mode's single-image Spine auto-rig is the one structurally different HD option and worth a test.
- **(c) Animating an existing GPT concept:** Ludo and AutoSprite are the most direct for HD (upload, preset or keyframe, sheet). PixelLab's 8-Directional Pro, Animate with Text and `animate_image` are the most direct for pixel art.

### Cited Findings
- Cinevva (Sep 2026): PixelLab for animated characters; Retro Diffusion for Aseprite users wanting a one-time purchase; Ludo as one tool for all assets; Scenario or Layer for studio style consistency. — [Cinevva](https://app.cinevva.com/guides/ai-pixel-art-generators)
- GameDev AI Hub: PixelLab for a solo dev building a full animated game, especially top-down/isometric 8-direction; "nothing here beats it"; RD for pixel purists. — [GameDev AI Hub](https://gamedevaihub.com/retro-diffusion-vs-pixellab/)
- Techsy: PixelLab is the best pixel and sprite option; Scenario is best for on-style 2D batches once trained. — [Techsy](https://techsy.io/en/blog/best-ai-game-asset-generators)
- Ludo (vendor) ranks itself #1, then PixelLab, Scenario, Layer, AutoSprite, Sprite AI, SpriteLab, God Mode. — [Ludo comparison](https://ludo.ai/compare/best-ai-sprite-generators)
- HD-capable dedicated tools found: Ludo (32 styles, up to 384 px or native) [Ludo](https://ludo.ai/features/sprite-generator); FrameSprite ("clean HD", "painterly") [FrameSprite](https://www.framesprite.com/); SpriteCook ("detailed/HD") [SpriteCook](https://www.spritecook.ai/); God Mode (Spine export) [God Mode AI](https://www.godmodeai.co/); AutoSprite (12 styles claimed) [AutoSprite itch.io](https://autosprite.itch.io/autosprite).

### Inferences
**Summary matrix (inferred from the cited data above):**

| Need | Primary | Secondary / complementary | Avoid |
|---|---|---|---|
| Pixel sprites, many directions | PixelLab (skeleton/v3/PixMiniMax, 8 rotations, MCP) | Retro Diffusion advanced animations (provenance) | Leonardo, SEELE |
| HD illustrated (Kingdom Rush-like) | Keep Veo pipeline; trial Ludo or AutoSprite as packaging; trial God Mode Spine auto-rig | Scenario (custom style model for concept consistency) | Pixel-only tools (≤256 px) |
| Animate an existing GPT concept | HD: Ludo / AutoSprite / SpriteCook. Pixel: PixelLab 8-dir Pro + Animate with Text | Retro Diffusion `input_image` (pixel) | SEELE (prompt-only) |
| Automation from Claude Code | PixelLab MCP, Ludo MCP/CLI (Pro), AutoSprite MCP, SpriteCook MCP, Retro Diffusion MCP | Layer MCP/CLI, Scenario MCP | — |

- Cost per animation is low across the board: PixelLab API $0.02–$0.15, Retro Diffusion $0.14–$0.25, AutoSprite ~5 credits per sheet (≈$0.12 on Starter), Ludo ~15 credits per 5-s Hydra clip. This is cheap enough to A/B test all of them on one GPT concept for under ~$50.
- For a Kingdom Rush-like HD game, the realistic hybrid is to keep Veo (or a Ludo/AutoSprite wrapper) for motion and use dedicated tooling only for packaging, directions and loop repair. Consider God Mode's Spine output if skeletal reuse across many units matters.

### Gaps
- No source evaluates any tool specifically on Kingdom Rush-style HD tower-defense units (small on-screen size, many units, 2–4 directions).
- Whether Ludo, AutoSprite or FrameSprite match Veo 3.x motion quality is untested. FrameSprite discloses MiniMax H3, while Ludo and AutoSprite do not disclose their models.
