# AI-assisted 2D sprite animation: production constraints and practitioner experience (as of 15 Oct 2026)

Scope: craft standards, keeping one character consistent, end-to-end case studies, cost, legal and platform rules, and player sentiment for a pipeline of GPT Image (concept) → Google Veo image-to-video (motion) → sprite sheets.

Source quality note: many of the "how-to" and pricing pages on this topic are vendor or reseller blogs. Each is labelled where it matters. Primary sources (Google docs and terms, Steamworks, Apple guidelines, developer write-ups) are preferred wherever I could reach them. I could not open OpenAI's terms page directly (HTTP 403), so the OpenAI wording below comes from search snippets of openai.com and mirrors of it.

---

## 1. Craft standards: frame counts, fps, resolutions, animation sets

### Takeaway
Game sprites use far fewer unique frames than film or AI video. Typical counts are 2–4 frames for idle, 4–8 for walk, 6–8 for run, and 3–6 for a light attack. Timing (how long each frame is held) matters more than frame count. A Veo clip is 24 fps (96–192 frames), so the pipeline's main craft step is **choosing about 6–12 key poses** and retiming them, not playing back all the video frames. Pixel art is usually drawn on a low base canvas such as 320×180 and scaled up by whole-number multiples. HD hand-drawn work like Cuphead runs at 24 fps "on ones" and costs much more.

### Cited Findings
**Frame counts and timing**
- Game sprite animation uses "many fewer frames" than film. A one-second sword swing is 24 frames in feature animation, but about 3 sprites in a very simple game style and up to about 9 in a more fluid style. A walk cycle is about 6 frames in a simple style and up to about 12 in a fluid one — [Adafruit Learn, Sprite Animation Fundamentals](https://learn.adafruit.com/makecode-arcade-pixel-animation/sprite-animation-fundamentals)
- Reference table (vendor blog, updated 12 Aug 2026, **cites no external sources** and says its counts "come from analyzing actual indie games"): Idle 2–4 frames at 400–800 ms/frame; Walk 4–8 (4 for small sprites, 6–8 for 32×32+) at 80–120 ms/frame; Run 6–8 at 50–80 ms/frame ("faster timing, not necessarily more frames"); Jump 3–5 (anticipation, air, land); Attack 3–6 (wind-up, strike, recovery), e.g. wind-up 150 ms, anticipation peak 200 ms, strike 50 ms, recovery 120 ms; Hit reaction 2–3; Death 4–6 (one-shot); Climb 4–6 — [Sprite AI, "Sprite animation frames: how many do you actually need?"](https://www.sprite-ai.art/blog/sprite-animation-frames)
- The same vendor source gives these game examples, which I could not verify against developer sources: Celeste's Madeline has a 4-frame run cycle; Shovel Knight's walk is 6 frames; Dead Cells attacks are 8–12 frames — [Sprite AI](https://www.sprite-ai.art/blog/sprite-animation-frames)
- Guides agree that a 12-frame walk often looks worse than a 4-frame one because inconsistencies become visible, and that timing, not frame count, makes an animation feel snappy — [Sprite AI animation guides (search summary)](https://www.sprite-ai.art/guides/animation-principles); [spritesheetgenerator.online, Animation Timing in 2D Games](https://spritesheetgenerator.online/blog/animation-timing-fps-pixel-art)
- Celeste's artist Pedro Medeiros (saint11) posted "Animating for celeste, 175 frames on this character." This appears to be the total across one character's whole animation set — [saint11 on X](https://x.com/saint11/status/852227659883065344)

**Animating "on ones" vs "on twos" and HD reference points**
- Cuphead: lead artist Chad Moldenhauer said the animation runs at 24 fps on top of 60 fps gameplay — [Windows Central](https://www.windowscentral.com/check-out-how-cuphead-team-makes-its-cool-looking-2d-animations)
- A secondhand forum repost of a developer quote says Cuphead is animated on ones (24 unique drawings per second) and sometimes goes up to 40 fps of unique drawings to get timings right. Treat this as unverified — [NeoGAF thread](https://www.neogaf.com/threads/engadget-cuphead-is-as-wondrous-as-it-is-difficult.1422272/page-3)
- "On twos" means each drawing is held for two frames, so 24 fps playback shows 12 unique drawings per second — [Punished Backlog, Examining the Animation of Cuphead](https://punishedbacklog.com/cuphead-animation/)
- Dead Cells (Motion Twin) solved the frame-count and revision problem with a 3D-to-2D pipeline. Animations are built pose-to-pose on keyframes "with the fewest frames possible." Interpolation frames are added before or after keyframes, never in between. The 3D model is rendered at tiny size without antialiasing, with a normal map per frame and a toon shader. Retakes were faster than uploading the GIFs. The in-game character is about 50 px tall, and the earlier ScarKrow prototype ran at 30 fps — [Game Developer, Art Design Deep Dive: Dead Cells](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)
- Owlboy (D-Pad Studio): a house-interior loop is 8 frames on a 300×260 canvas and took about two weeks. Vegetation gets "at least 8 frames" to sell a sway — [D-Pad Studio dev blog, Animations of Owlboy Part 2](https://dpadstudio.tumblr.com/post/697123665705402368/the-animations-of-owlboy-part-2-today-we)

**Resolutions**
- Celeste renders at a fixed internal 320×180, scaled to 960×540 at 3× and 1280×720 at 4× (a user statement on the Steam forum, consistent across posts). Whole-number multiples of 320×180 or 640×360 map cleanly onto 16:9 screens — [Steam Community, Celeste](https://steamcommunity.com/app/504230/discussions/0/3832043350345268297)
- Common output sizes for AI video-to-sprite converters are 64×64, 128×128 and 256×256 px cells — [DoSprite on itch.io](https://agemar.itch.io/dosprite)
- A detailed AI sprite guide (Layr Kits) used a 960×960 source video canvas and 256×256 output cells. It kept 12 frames as the game asset and 24 frames as a smoother reference, giving sheets of 3072×256 and 6144×256 — [Layr Kits, How to Create a Game-Ready 2D Sprite Sheet](https://www.layrkits.com/guides/sprite-sheet)

**Veo's native output vs sprite needs**
- Veo 3.1 / Fast / Lite output is **24 fps**, in clips of **4, 6 or 8 s**, at aspect ratio **16:9 or 9:16 only**. 720p is the default. 1080p and 4K require 8 s clips — [Google Gemini API, Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- Kling outputs 30 fps and Veo 24 fps, so you downsample either way for sprites — [ImagineArt comparison (vendor)](https://imagine.art/blogs/kling-ai-vs-other-ai-video-generators)

### Inferences
- A 4 s Veo clip is 96 frames and an 8 s clip is 192. A typical game animation needs 4–12 of them. Treat Veo as **reference footage**: pick the extremes and breakdown poses, then retime by hand with per-frame durations in the engine (Unity Animator, Godot AnimatedSprite2D / SpriteFrames, Phaser `frameRate` or per-frame `duration`). Do not resample the video at a fixed rate.
- Pixel-art targets (characters about 16–64 px tall on a 320×180 or 640×360 canvas) mean downscaling roughly 10–20× from a 720p character. AI video's soft shading and sub-pixel motion do not survive that well. Expect palette reduction, hand cleanup and pixel-by-pixel fixes; this is where pixel-art vendors (PixelLab, Retro Diffusion-style tools) position themselves. HD 256–512 px sprites keep much more of the AI footage and are the more natural fit for a Veo pipeline.
- Fewer frames read better because each held pose is a clear silhouette, and a held impact frame sells weight. Interpolated AI frames tend toward even "floaty" spacing, which is the failure the Sprite AI guide warns about (six evenly spaced frames at a constant rate feel flat).
- Standard animation set (from general industry practice; I found no single authoritative source):
  - Platformer: idle, run (or walk + run), jump in phases (takeoff, rising, apex, falling, landing), attack(s), hurt, death, often plus wall-slide, dash or crouch.
  - Top-down: the same core set (idle, walk, attack, hurt, death) multiplied by directions. With 4 directions, side views are often mirrored, so 3 are unique. With 8 directions, 5 are unique (N, NE, E, SE, S) and the rest are mirrored.
  - This multiplication matters for cost and consistency (see sections 2 and 4). The open-source sprite-sheet-creator tool generates walk/jump/attack/idle for side view and separate direction sets for isometric mode — [GitHub, blendi-remade/sprite-sheet-creator](https://github.com/blendi-remade/sprite-sheet-creator)

### Gaps
- No developer-primary source found for per-animation frame counts in Celeste, Hollow Knight or Dead Cells. Counts circulating online (e.g. Celeste's 4-frame run) trace to unsourced blogs.
- No official animation fps or sprite resolution found for Hollow Knight. Forum guesses only. Madeline's exact sprite dimensions are unverified.
- No authoritative published "standard animation set" list. The lists above are inference from common practice.

---

## 2. Consistency across many animations (identity, scale, proportions)

### Takeaway
Video models generate each clip without memory of earlier ones, so identity drift is the central problem. Practitioners handle it four ways:
- (a) Use **one canonical reference image as the first frame** of every clip, and describe only motion in the prompt.
- (b) Use first/last-frame interpolation and model reference-image features. Veo 3.1 accepts up to 3 reference images, but only on 8 s clips and not on Lite.
- (c) Use pose templates or character sheets.
- (d) For high volume, train a LoRA, which needs roughly 30–50 images.

Scale consistency is handled mostly in post: keep the canvas fixed, never crop per frame, and anchor feet to a baseline.

### Cited Findings
- Veo 3.1 and 3.1 Fast support image-to-video (`image`), first+last frame interpolation (`lastFrame`), and up to **3 reference images**. Reference images require 8 s clips and are **not supported on Veo 3.1 Lite**. A `seed` parameter "improves but doesn't guarantee determinism." One video per request — [Google Gemini API, Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- Veo constraint relevant to character art: for image-to-video, interpolation and reference images, `personGeneration` must be `allow_adult`. In the EU, UK, CH and MENA, `allow_adult` is the only allowed value. Generated videos are deleted from Google's servers after **2 days**, so download immediately — [Google Gemini API, Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- Practitioner tip: generate a multi-frame sprite sheet with Nano Banana Pro, then feed that single sheet as an "Ingredient" to Veo 3.1 (Ingredients to Video in Flow). The author says it seems to help spatial and temporal consistency. This is a single social post — [Nick Matarese on X](https://x.com/nmatares/status/1993801190803742729)
- First/last-frame workflow: generate the sprite on magenta with Nano Banana, then ask it for the animation's final frame, then use Flow/Veo 3 to animate between the two — [LarsDu88, Hacker News, Sept 2025](https://news.ycombinator.com/item?id=45238184)
- Guidance from a guide (vendor): "the image is the identity contract; the video prompt is the motion contract." Avoid re-describing the character in each video prompt. Chaining clips by reusing the last frame works, but errors accumulate along the chain — [Envato, AI Video Consistent Character Guide](https://elements.envato.com/learn/ai-video-consistent-character)
- Layr Kits pipeline details:
  - For non-idle actions, the image model first makes a **small transition pose away from idle**, which is then used as the first frame.
  - Keep the camera locked and the character centred.
  - Keep animation-safe margins so weapons stay in frame.
  - Vertical moves (jump, landing) make the character drift, so dust and wind effects are made as separate overlays.
  - Keep the canvas intact, with no per-frame cropping.
  - Using the same image as first and last frame sometimes produced a static clip. Final frames too close to the first made loops look stuck.
  — [Layr Kits guide](https://www.layrkits.com/guides/sprite-sheet)
- Layr Kits also found that image models could not reliably draw walk or run cycles, even in pixel art (top-down was the exception). Image models also ignored grid and transparency rules, so scripts fixed layout and background — [Layr Kits guide](https://www.layrkits.com/guides/sprite-sheet)
- An indie tool author tried direct AI sprite-sheet generation first and got "inconsistent motion, unstable style." Generating short videos and extracting frames fixed motion continuity but left heavy manual cleanup (background removal, semi-transparent effects) — [MP4toSprite on itch.io](https://yewlark.itch.io/mp4tosprite)
- Kling 2.6 Pro Motion Control applies motion from a reference video to a static character image. The vendor says this keeps appearance consistent. It is useful when one walk motion should drive many characters — [MindStudio, Kling 2.6 Pro Motion Control](https://www.mindstudio.ai/blog/what-is-kling-2-6-pro-motion-control-video)
- SpriteForge LoRA project (fighting-game 4×4 sheets): "consistency comes from the template, not the generation." A new character is swapped into a fixed pose template. The author reports that base Qwen-Image-Edit without the LoRA gave inconsistent appearance and incoherent sequences — [SpriteForge](https://tantk.github.io/spriteforge-pipeline/)
- LoRA training typically needs about 30–50 reference images. One creator found IP-Adapter with a frozen reference beat LoRA: at a scale of 0.65 it worked, at 0.85+ it also copied the reference pose (which kills new actions), and at 0.4 the face drifted — [DEV Community, Character consistency in AI comics](https://dev.to/qcrao/character-consistency-in-ai-comics-3-tricks-that-beat-lora-training-for-me-3ad7)
- Academic work on the same problem: "Sprite Sheet Diffusion: Generate Game Character for Animation" (arXiv 2412.03685) — [arXiv](https://arxiv.org/html/2412.03685v2)
- Real-world failure: in Vapor World: Over The Mind (2026), AI-generated cutscenes drew the top Steam review saying the AI "couldn't even keep the main character's model consistent." The cutscenes were pulled — [Everything Edinburgh](https://everythingedinburgh.com/games/news/vapor-world-steam-ai-cutscene-backlash/)
- How non-AI pipelines get consistency: Dead Cells relies on shared 3D skeletons, reusable components, one toon shader and one render/pixelation tool — [Game Developer, Dead Cells deep dive](https://www.gamedeveloper.com/production/art-design-deep-dive-using-a-3d-pipeline-for-2d-animation-in-i-dead-cells-i-)

### Inferences
- Recommended setup for this studio:
  1. Lock a **canonical character sheet** (front, side, back; neutral pose; flat chroma background), made once with GPT Image or Nano Banana and then frozen.
  2. For each animation, generate the **start pose (and optionally the end pose) as edits of that sheet**.
  3. Run Veo 3.1 image-to-video, or first/last frame for one-shots, with a fixed camera, a fixed character scale in frame and a templated motion-only prompt.
  4. Use reference images (up to 3, 8 s only) when identity drifts.
  5. Normalise scale in post with a fixed canvas and foot baseline, and record a pivot in the sheet's JSON.
- Seeds cannot be relied on for reproducibility (Google says so), so keep every prompt, seed and input image in a manifest per clip. This doubles as provenance records for Steam disclosure and copyright (sections 5–6).
- Loops (idle, walk, run) are the hardest for video models because the last frame must match the first. First+last-frame mode with the same pose sometimes produces a still clip, so use a slightly offset end pose and close the loop by hand-picking frames.
- If the studio partners are 3D-capable, the Dead Cells approach (3D rig → pixelated render) gives near-perfect consistency and cheap retakes. It may beat AI video for the playable character, with AI reserved for concepts, NPCs, effects or HD cutscene art.

### Gaps
- No controlled benchmark found comparing identity drift across idle, walk and attack for Veo 3.1 vs Kling 3.0. Evidence is anecdotal.
- Whether Veo's `allow_adult` restriction blocks image-to-video of child-like or chibi stylised characters was not documented. Test before committing to an art style.
- No first-hand report found of LoRA-plus-video pipelines specifically for game sprites at production scale.

---

## 3. End-to-end case studies (2025–2026)

### Takeaway
Public evidence is thin and mostly prototypes. I found **no documented commercial game that shipped player characters animated with Veo or Kling and wrote a postmortem**. The documented cases are hobbyist and tutorial pipelines. They agree on a pattern: image model for the pose, then video model for motion, then scripted frame extraction, chroma key, frame picking and cleanup. They report that it works but is "laborious," and that generation cost is negligible next to cleanup time.

### Cited Findings
- **Layr Kits guide (2026, undated page):** the most complete documented pipeline.
  - Tools: GPT Image 2 or Nano Banana 2 for the first pose, Kling for motion, and Codex to write local Python scripts (FFmpeg/ffprobe extraction to numbered PNGs plus a JSON report; Pillow chroma key on exact #00FF00 with despill and noise removal; a matting fallback).
  - Frames are chosen by hand from a contact sheet, anchored on start pose, recovery pose and key beats. Output is 12 or 24 frames at 256×256 per cell.
  - Problems: image-only sprite sheets failed for walk and run (about **two days** lost before switching to video); Kling pushed weapons and limbs out of frame; vertical drift on jumps; static clips when first and last frame matched; a **fixed corner watermark logo** was covered with a transparent box on each cell.
  - No dollar costs given; image generation is called "dirt cheap" and image re-runs cheaper than video re-runs.
  — [Layr Kits](https://www.layrkits.com/guides/sprite-sheet); also published as an [X article](https://x.com/LayrKits/article/2050277473116619240)
- **LarsDu88 (Hacker News, 14 Sept 2025):** Nano Banana sprite on magenta, then Nano Banana final frame, then Flow/Veo 3 interpolation. Called "astoundingly effective, but still rather laborious and lacking in ergonomics." Problems: fixed video aspect ratio, and the magenta shade had to be fixed by hand for keying. Opinion: Veo 3 is good enough for sprites and animations of a 2000s-style 2D RTS — [Hacker News](https://news.ycombinator.com/item?id=45238184)
- **star4droid (itch.io, 15 Sept 2025):** "Hatsune Miku walking animation." Character made in Gemini, animated in Veo 3 (or free via LMArena), 2–3 s of frames extracted, background removed, compressed. "It's hard and took a long time." Errors on two characters in the batch. Built two helper web tools in Google AI Studio. Note that the subject is a third-party IP character, which would be a legal problem in a commercial game — [itch.io post](https://itch.io/post/14144159/view-in-topic)
- **MP4toSprite (itch.io tool, $5+):** made by a dev who found direct sprite-sheet generation unusable and video-first extraction workable but heavy on manual cleanup — [yewlark.itch.io/mp4tosprite](https://yewlark.itch.io/mp4tosprite)
- **DoSprite (free browser tool):** converts video (named sources: Kling, Luma, Grok) into pixel-art frames at 64, 128 or 256 px with tolerance-based background removal and a retouch brush, all processed locally — [agemar.itch.io/dosprite](https://agemar.itch.io/dosprite)
- **Nick Matarese (X, late 2025):** Nano Banana Pro sprite sheet as a Veo 3.1 "Ingredient" for consistency — [X](https://x.com/nmatares/status/1993801190803742729)
- **sprite-sheet-creator (open source, GitHub):** Nano Banana Pro/Lite via fal.ai generates 2×2 sheets for walk/jump/attack/idle plus an isometric directional mode, producing playable characters. Image-only, no video model — [GitHub](https://github.com/blendi-remade/sprite-sheet-creator)
- **Commercial "image to sprite sheet" products** (Ludo.ai Animate / Keyframe Animation with up to 3 key poses / Transfer Motion; Scenario; AutoSprite; SpriteLab; Sorceress; PixelLab) package the same pipeline. Their consistency claims are marketing — [Ludo.ai docs](https://ludo.ai/docs/sprite-generator/image-to-sprite-sheet); [Scenario blog](https://www.scenario.com/blog/ai-sprite-generator); [AutoSprite](https://autosprite.itch.io/autosprite); [PixelLab](https://www.pixellab.ai/)
- **Negative case:** Vapor World: Over The Mind swapped in-engine cutscenes for AI versions. It launched to a reported 36% positive (64 reviews), and the studio restored the originals within days. Director Young Kim said the fault "lies not with the tool" but with the studio — [Everything Edinburgh](https://everythingedinburgh.com/games/news/vapor-world-steam-ai-cutscene-backlash/). Dates conflict: one summary puts the early access launch at 19 Aug 2026 with 100k wishlists; Everything Edinburgh reports it around 25 Sept 2026 — [Everything Edinburgh](https://everythingedinburgh.com/games/news/vapor-world-steam-ai-cutscene-backlash/)

### Inferences
- The time sink is not generation. It is (1) frame selection and retiming, (2) background keying and despill, (3) pixel cleanup and palette for pixel art, and (4) fixing drift and scale per frame. Budget artist hours for these per animation. The studio should script steps 1–2 on day one (FFmpeg plus Pillow, as Layr Kits did) and keep a contact-sheet review UI.
- Veo-specific friction for sprites:
  - The canvas is 16:9 or 9:16 only, so square sprites need padding. Keep the character small and centred with margins.
  - Native audio is always generated and billed on the Gemini API. It is useless for sprites but included in the price.
  - Clips must be downloaded within 2 days.
- No public postmortem of a shipped game using this exact pipeline exists that I could find. The studio would be among the early documented adopters, and should expect to discover its own failure modes.

### Gaps
- No YouTube or Reddit (r/aigamedev, r/gamedev) thread with concrete numbers (generations per usable clip, hours per character) surfaced in searches. Reddit pages were not returned by the search tool.
- No documented shipped Steam or mobile game confirmed to use Veo- or Kling-derived sprite animation for its main character.

---

## 4. Cost modeling

### Takeaway
At list prices, generation is cheap. A full 8-animation side-view character costs roughly **$7–$100 in Veo fees**, depending on tier and clip length, plus a few dollars of image generation. Top-down 8-direction characters multiply this 5–8×. Labor (frame picking and cleanup) dominates total cost. The number of attempts per usable clip is not documented, so the multipliers below are assumptions.

### Cited Findings
- **Veo on the Gemini API (official), per second of output, audio included:**

  | Model | 720p | 1080p | 4K |
  |---|---|---|---|
  | Veo 3.1 | $0.40 | $0.40 | $0.60 |
  | Veo 3.1 Fast | $0.10 | $0.12 | $0.30 |
  | Veo 3.1 Lite | $0.05 | $0.08 | not supported |

  There is no free tier for any Veo 3.1 model. Paid-tier content is not used to improve Google products — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- Veo's audio is always generated on the Gemini API. A video-only SKU exists on Vertex AI at separate rates — [benchlm.ai Veo pricing summary](https://benchlm.ai/md/media-pricing/veo.md)
- Veo blocked videos (e.g. safety blocks on audio) are not charged. Clips are 4/6/8 s, and 8 s is required for 1080p, 4K and reference images — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- A reseller claim of $0.75/s for Veo 3.1 contradicts Google's sheet and should be disregarded — [Veo3Gen blog](https://www.veo3gen.app/blog/veo-3-1-api-access-cost)
- **Image models (official Gemini):** Nano Banana 2 (Gemini 3.1 Flash Image) $0.067 per 1K image ($0.034 batch); Nano Banana Pro (Gemini 3 Pro Image) $0.134 per 1K/2K image; Gemini 2.5 Flash Image is deprecated with shutdown on 2 Oct 2026 — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- **gpt-image-2 (OpenAI, via third parties):** token-based. Reported per-image cost at 1024×1024 is about $0.006 low, $0.053 medium and $0.211 high, with batch at half price. I could not open OpenAI's pricing page; verify there — [aireiter summary](https://aireiter.com/blog/gpt-image-2-api-pricing); [Segmind](https://www.segmind.com/models/gpt-image-2/pricing)
- **Kling (resellers only; official page not found):**
  - Kling 3.0 is listed from about $0.06/s (Pro 1080p $0.08, 4K $0.30), and one reseller cites $0.084/s on the official API.
  - Kling 2.6 is listed from $0.03/s (Pro $0.05) with 5 or 10 s clips and an optional end frame.
  - Kling 3.0 clips run 3–15 s.
  — [Atlas Cloud](https://www.atlascloud.ai/blog/tips/kling-ai-api-pricing); [EvoLink](https://evolink.ai/blog/kling-3-api-pricing-integration-guide); [apiframe](https://apiframe.ai/blog/kling-3-0-api-providers)
- **Kling consumer plans:** the paid Standard plan is about $6.99–$10/month, the first tier with commercial rights and no watermark. The free plan has a visible watermark and no commercial use (third-party reviews) — [Atlas Cloud Kling pricing](https://www.atlascloud.ai/blog/guides/kling-ai-pricing); [crepal.ai](https://crepal.ai/blog/?p=8001)
- **Runway:** the free plan is 125 one-time credits with a watermark. Standard is about $12–15/user/month with the watermark removed (third-party) — [gptprompts.ai](https://gptprompts.ai/runway-pricing); [toolsforhumans](https://www.toolsforhumans.ai/ai-tools/runway)
- **Labor reference points:** Layr Kits lost about 2 days on image-only attempts before switching to video ([Layr Kits](https://www.layrkits.com/guides/sprite-sheet)). Practitioners call the process "laborious" ([HN](https://news.ycombinator.com/item?id=45238184)) and "took a long time" ([itch.io](https://itch.io/post/14144159/view-in-topic)).
- **Market comparison for finished assets:** a 42-animation hand-painted FX pack sells for $49 on itch.io — [itch.io](https://sprite-sheet.itch.io/cartoon-effects-explosions-fire-water-smoke-flashes-stylized)

### Inferences (worked estimates from Google's official per-second prices; the attempt counts are assumptions, not sourced)
- **Per clip (Veo):**
  - Lite 720p: 4 s = $0.20; 8 s = $0.40.
  - Fast 720p: 4 s = $0.40; 8 s = $0.80. Fast 1080p 8 s = $0.96.
  - Standard 720p or 1080p 8 s = $3.20.
  - Reference images force 8 s and Fast/Standard, so an "identity-locked" clip costs at least $0.80.
- **Side-view platformer character: 8 animations × 4 attempts = 32 clips**
  - Lite 4 s: about $6
  - Fast 4 s: about $13
  - Fast 8 s with reference images: about $26
  - Standard 8 s: about $102
  - Add about 20–50 concept and pose images: about $1–$10 at Nano Banana 2 or gpt-image-2 medium/high.
- **Top-down 8-direction character:** about 6 animations × 5 unique directions (mirroring the other 3) = 30 animation-directions × 4 attempts = 120 clips. That is about $48 on Fast 4 s or about $384 on Standard 8 s. Without mirroring, multiply by 8/5.
- **Kling comparison:** a 5 s Kling 2.6 clip at $0.03–0.05/s is about $0.15–0.25, and a 5 s Kling 3.0 clip at about $0.084/s is about $0.42. That is roughly the same range as Veo Lite/Fast, so model choice should rest on motion quality and consistency, not price.
- Even at 10 attempts per animation, Veo Standard spend for one character stays in the low hundreds of dollars. The real cost is 0.5–2+ artist days per animation for picking, retiming and cleanup. That is an assumption based on the "laborious" reports and not measured. Model the pipeline's ROI on labor saved versus traditional frame-by-frame work, not on API spend.

### Gaps
- No documented statistic for generations per usable clip in sprite work. Kling official API pricing was not retrieved, only reseller figures. OpenAI gpt-image-2 prices come from third parties.
- No measured hours-per-character figure from a practitioner.

---

## 5. Legal, licensing and platform-policy constraints

### Takeaway
- **Contract rights:** OpenAI and Google both disclaim ownership of outputs. OpenAI assigns its rights to the user; Google "won't claim ownership." Neither guarantees uniqueness, and both say similar output may go to others. Use **paid tiers**: the Veo API has no free tier, and free consumer tiers of Kling and Runway carry visible watermarks and (Kling) no commercial rights.
- **Copyright:** under US Copyright Office guidance (Jan 2025), purely prompt-generated art is **not copyrightable**. Human selection, arrangement and modification can be. The Supreme Court declined Thaler on 2 Mar 2026.
- **Platforms:** Steam requires disclosure of AI content that ships (pre-generated) and is generated live, but exempts efficiency tools since Jan 2026. itch.io requires tagging for asset packs. Epic, Apple and Google Play have no AI-art disclosure requirement for games.
- **Watermarks:** SynthID is embedded in every Veo video. The API docs mention no visible watermark.

### Cited Findings
**OpenAI**
- The user retains rights in Input and owns Output to the extent permitted by law. OpenAI assigns "all our right, title, and interest, if any, in and to Output." Under "Similarity of content," the terms say output "may not be unique and other users may receive similar output." The assignment does not extend to other users' output or Third Party Output — [OpenAI Terms of Use (search snippets; direct fetch blocked)](https://openai.com/policies/row-terms-of-use/); [mirror of OpenAI ToU](https://open.windriver.com/info/uni-license-list/licenses/openai-tou-20241211.html)
- Business terms: "Customers retain all ownership rights in Input and own all Output" — [OpenAI Business terms](https://openai.com/policies/nov-2023-business-terms/)

**Google Gemini API / Veo**
- "Google won't claim ownership over that content." Also: "Google may generate the same or similar content for others and that we reserve all rights to do so." Users must be 18+ and may not develop competing models. Unpaid Services content is used to improve Google products; paid prompts are not, and are logged only for abuse detection and legal needs. Terms last updated 2026-04-28 (effective 23 Mar 2026) — [Gemini API Additional Terms](https://ai.google.dev/gemini-api/terms)
- Veo videos carry SynthID watermarks, verifiable on the SynthID platform. The API docs mention no visible watermark — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo); [Google Developers Blog, Veo 3 in Gemini API](https://developers.googleblog.com/en/veo-3-now-available-gemini-api/)
- In consumer products, Veo 3 videos carry a **visible** watermark except those made in Flow by Ultra subscribers — [BGR](https://www.bgr.com/tech/those-amazing-veo-3-videos-will-finally-tell-you-they-were-made-with-ai/)
- Third-party claims that stripping SynthID violates Google's terms were not confirmed in Google's own text, and the Gemini API terms page does not mention watermarks — [Gemini API terms](https://ai.google.dev/gemini-api/terms); [wan27.org (third party)](https://wan27.org/blog/veo-3-1-watermark-remover)

**Kling and Runway (third-party sources; official terms not retrieved)**
- Kling's free Basic plan does not allow commercial use and carries a visible Kling watermark. Cropping or covering the watermark does not change the license. Free-tier outputs do not automatically become commercial after upgrading. Kling's terms reportedly grant Kuaishou a worldwide, royalty-free license to user content — [aitoolsatlas](https://aitoolsatlas.ai/tools/kling/free-vs-paid); [St-Hakky](https://book.st-hakky.com/en/data-science/kling-ai-pricing-usage-kling-3-0); [blocksentient review](https://blocksentient.com/review/kling-ai); [CometAPI](https://www.cometapi.com/are-kling-videos-private/)
- Runway: whether the free tier allows commercial use is disputed between sources. Free exports are watermarked. One source says Runway trains on inputs and outputs by default on non-Enterprise tiers (unverified) — [terms.law Runway](https://terms.law/ai-output-rights/runway/); [conductatlas](https://conductatlas.com/platform/runway/runway-terms-of-service/company-does-not-restrict-commercial-use-of-outputs/)

**Copyright (US)**
- USCO, "Copyright and Artificial Intelligence, Part 2: Copyrightability" (29 Jan 2025):
  - "given current generally available technology, prompts alone do not provide sufficient human control to make users of an AI system the authors of the output." Repeated or revised prompting does not change this.
  - Protection is available where human-authored expression is perceptible in the output, or where a human creatively selects, arranges or modifies AI output. Decided case by case.
  — [IPWatchdog](https://ipwatchdog.com/2025/01/29/part-two-copyright-office-ai-report-says-creative-prompting-doesnt-constitute-authorship/); [Sidley Data Matters](https://datamatters.sidley.com/?p=7917)
- Thaler v. Perlmutter: the Supreme Court denied cert on 2 Mar 2026, leaving the human-authorship requirement standing — [SCOTUSblog](https://www.scotusblog.com/cases/thaler-v-perlmutter/)

**Steam**
- The Content Survey's AI section concerns "content that ships with your game."
  - **Pre-Generated AI**: content "created with the help of AI tools during development."
  - **Live-Generated AI**: content created while the game runs. This requires describing guardrails against illegal content, and Valve will not ship live-generated adult-only sexual content.
  - Valve evaluates AI output the same way as other content. Under the Steam Distribution Agreement the developer promises no illegal or infringing content.
  — [Steamworks, Content Survey](https://partner.steamgames.com/doc/gettingstarted/contentsurvey)
- January 2026 update (reported 16 Jan 2026): developers no longer disclose "AI powered tools" used for efficiency. They do disclose AI used "to generate content for the game," including store page and marketing assets, with a text box describing tools, and AI "content generated during gameplay" — [Game Developer](https://www.gamedeveloper.com/business/valve-tweaks-and-clarifies-ai-disclosure-rules-for-steam)
- Scale (secondary): more than 7,300 Steam games had disclosed AI content by March 2026, and about one in five games in a July 2026 review carried a disclosure — [tech-insider.org](https://tech-insider.org/steam-ai-disclosure-2026/); [tbreak](https://tbreak.com/steam-ai-disclosure-policy-update-developers/)

**itch.io**
- Since Nov 2024, **asset packs** must be tagged AI Generated if AI was used in any way, even if hand-edited. Untagged assets lose browse indexing and may be delisted. For games, disclosure is optional or encouraged — [PC Gamer](https://www.pcgamer.com/software/platforms/indie-distribution-platform-itch-io-now-requires-asset-creators-to-disclose-the-use-of-generative-ai-in-their-work/); [itch.io quality guidelines](https://itch.io/docs/creators/quality-guidelines); [IF Community forum](https://intfiction.org/t/gen-ai-disclosure-on-itch-io/72448)

**Epic Games Store**
- No AI disclosure requirement. Store GM Steve Allison: "We do not police how developers make their games." Tim Sweeney said disclosure "makes no sense for game stores, where AI will be involved in nearly all future production" — [GamesRadar](https://www.gamesradar.com/games/we-do-not-police-how-developers-make-their-games-epic-games-store-boss-says-we-let-players-decide-on-games-that-use-gen-ai/); [Insider Gaming](https://insider-gaming.com/epic-games-ceo-says-ai-disclosure-makes-no-sense-for-game-stores/)

**Apple App Store**
- The only AI mention in the Review Guidelines is 5.1.2(i): "You must clearly disclose where personal data will be shared with third parties, including with third-party AI, and obtain explicit permission before doing so." There is no AI-art disclosure requirement. Some blogs claim a labeling rule, but the guideline text does not support it — [Apple App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/); [newly.app (Oct 2026)](https://newly.app/guides/does-apple-accept-ai-generated-apps)

**Google Play**
- The AI-Generated Content policy covers apps that **generate** content (chatbots, image generators). They must prevent restricted content and provide in-app reporting. It does not require labeling pre-made AI art in games — [Play Console Help, AI-Generated Content](https://support.google.com/googleplay/android-developer/answer/13985936?hl=en); [Understanding Google Play's AI-Generated Content policy](https://support.google.com/googleplay/android-developer/answer/14094294?hl=en)

### Inferences
- **SynthID and sprites:** SynthID is an invisible pixel-level signal designed to survive common edits. After keying, heavy downscaling to 32–128 px, palette quantisation and hand repainting, it is unlikely to remain detectable in pixel-art sprites, though this is not verified. HD sprites closer to source resolution may retain it. Either way it has **no functional or visual impact**, and no store requires its preservation or checks for it. The practical risk is reputational: detectable provenance could surface AI use the studio did not disclose. Disclose on Steam regardless; Veo-derived sprites are clearly "Pre-Generated AI." Do not attempt to strip SynthID deliberately.
- **Avoid visible watermarks** by using the Gemini/Vertex API (no visible mark documented) or paid tiers of Kling and Runway. The Layr Kits practice of boxing out a corner logo is only legitimate if that tier grants commercial rights. Covering it does not change the license.
- **Copyright exposure:** raw AI sprites are likely unprotectable in the US. A competitor could reuse ripped frames, and the studio may not be able to register them. Meaningful human cleanup, repainting, frame selection and arrangement into an animation adds protectable expression. **Keep a human-authorship trail** (layered files, before/after frames, manifests). The character design is stronger if a human artist draws or substantially reworks the canonical sheet.
- **IP contamination:** do not prompt with existing characters or artists. The itch.io Miku example shows how easily that happens. The Steam Distribution Agreement makes the developer liable for infringing content.
- **Data and confidentiality:** use paid API tiers so unreleased character designs are not used for training (Gemini paid tier; check OpenAI API data controls). Kling's broad content license is a confidentiality concern for unannounced IP.
- **Age:** Gemini API users must be 18+, which is irrelevant for a studio but relevant if partners build tools for others.

### Gaps
- Official Kling and Runway terms were not retrieved directly. Commercial-rights statements rely on third-party summaries.
- No Google statement found on whether SynthID survives pixel-art downscaling or quantisation. No official confirmation that removing SynthID breaches the Gemini API terms.
- Copyright outside the US (EU, UK, Uruguay/LatAm) was not researched. The UK's computer-generated works provision differs.
- I could not open OpenAI's terms page directly to confirm the effective date.

---

## 6. Industry sentiment and risk mitigation

### Takeaway
Player and press backlash against visible generative-AI art in games was intense through late 2025 and 2026. Awards were rescinded, AI assets were pulled after launch, and AI-looking capsules were ignored. The "it was just a placeholder" defence is now met with scepticism. Mitigations that work in practice: keep AI out of final player-facing art, or make the human cleanup pass substantial and real; track every AI-touched asset so none ships by accident; and disclose honestly. Undisclosed AI that is later discovered is punished hardest.

### Cited Findings
- **Clair Obscur: Expedition 33 (Dec 2025):** the Indie Game Awards rescinded its Game of the Year and Debut Game wins after Sandfall confirmed gen-AI use "on the day of the Indie Game Awards 2025 premiere." Sandfall said the AI textures were placeholders that slipped past QA and were patched out — [Engadget](https://www.engadget.com/gaming/the-indie-game-awards-snatches-back-two-trophies-from-clair-obscur-over-its-use-of-generative-ai-164730842.html); [Yahoo/Tech](https://tech.yahoo.com/gaming/articles/indie-game-awards-strips-clair-111710724.html)
- The Alters, Crimson Desert and Clair Obscur all blamed AI placeholders that slipped past QA, and the excuse is now treated sceptically — [Production Alchemist](https://www.productionalchemist.com/p/clair-obscur-indie-awards-ai-placeholder-texture)
- **Larian / Divinity (Dec 2025):** after Swen Vincke told Bloomberg the studio used gen-AI tools in development, the backlash led Larian to say "There is not going to be any GenAI art in Divinity" and to stop using gen-AI in concept art to avoid doubt about provenance. A former QA tester disputed claims that staff were comfortable with it — [TheGamer](https://www.thegamer.com/larian-backtracks-gen-ai-divinity/); [Kotaku](https://kotaku.com/larian-gen-ai-divinity-baldurs-gate-3-rpg-2000653912); [Game Developer](https://www.gamedeveloper.com/production/dev-backlash-to-larian-ceo-s-ai-comments-is-about-leadership-not-just-tech)
- **Arc Raiders (launched Oct 2025):** disclosed AI text-to-speech voices on Steam, faced criticism, and re-recorded some lines with human actors after launch. Embark stressed that no gen-AI was used for the visuals — [GameSpot](https://www.gamespot.com/articles/arc-raiders-now-has-fewer-ai-voices-as-dev-re-recorded-lines-amid-controversy/1100-6538780/); [Kotaku](https://kotaku.com/arc-raiders-replaced-ai-generated-content-human-recorded-dialogue-voices-2000678774)
- **Vapor World: Over The Mind (2026):** AI cutscenes replaced in-engine ones. The game launched at a reported 36% positive, the top review called out character inconsistency, and the studio restored the originals within days. PC Gamer's view was that player-facing AI that substitutes for creative work is what audiences reject — [Everything Edinburgh](https://everythingedinburgh.com/games/news/vapor-world-steam-ai-cutscene-backlash/); [PC Gamer Steam Week in Review](https://www.pcgamer.com/gaming-industry/steam-week-in-review-a-touch-of-ai-is-all-it-takes-to-trigger-backlash-as-a-promising-new-indie-falls-afoul-of-slop-skeptics/)
- **1666: Amsterdam:** Patrice Désilets removed AI-generated assets from Early Access and pledged no further AI use after community backlash (date not verified) — [TechPowerUp](https://www.techpowerup.com/352122/1666-amsterdam-developer-drops-gen-ai-art-after-community-backlash)
- **False accusations:** Shrine's Legacy (Oct 2025) got negative Steam reviews accusing it of AI art, which the developer denies. Dozens of developers reported being wrongly accused before Feb 2026 Next Fest — [PC Gamer / search summary](https://www.pcgamer.com/gaming-industry/steam-week-in-review-a-touch-of-ai-is-all-it-takes-to-trigger-backlash-as-a-promising-new-indie-falls-afoul-of-slop-skeptics/); [The Outpost](https://theoutpost.ai/news-story/steam-next-fest-faces-backlash-as-ai-art-floods-3-455-demos-sparking-calls-for-better-filters-24062/)
- **Steam Next Fest Feb 2026:** about 3,455 demos, many with AI-art capsules. A Palworld publishing lead said he would skip demos with AI capsules — [The Outpost](https://theoutpost.ai/news-story/steam-next-fest-faces-backlash-as-ai-art-floods-3-455-demos-sparking-calls-for-better-filters-24062/); [PC Gamer on AI capsule art](https://www.pcgamer.com/gaming-industry/steam-week-in-review-spammy-ai-generated-capsule-art-is-a-pox-and-it-makes-browsing-steam-less-fun/)
- An indie developer deleted their own game from Steam out of shame over AI use — [Futurism](https://futurism.com/artificial-intelligence/indie-developer-deleting-entire-game-ai)
- **Unverified statistic:** a "Stanford study" claiming games with identifiable AI art see 18% lower first-three-month sales and a 25% higher negative review ratio. It is cited by a marketing blog, and I could not find the primary study, so treat it as unreliable — [Metricus blog](https://metricusapp.com/blog/indie-game-distribution-user-acquisition-painpoints-2025-2026/)
- **Counter-position:** Epic's leadership argues AI will be in "nearly all future production" and that labels are a "scarlet letter" — [Windows Central](https://www.windowscentral.com/gaming/epic-games-ceo-steam-ai-disclosure-scarlet-letter)

### Inferences
- **Risk is highest for the hero character and marketing art**, which are the most visible and scrutinised. Players spot AI through inconsistency (shifting models, malformed hands and weapons, floaty interpolated motion). Those are the exact weaknesses of video-to-sprite pipelines, so cleanup must remove them. The practical rule: **nothing that "reads as AI" ships.**
- Mitigation playbook drawn from the cases above:
  1. Use AI for prototyping, previs and timing reference, with final frames redrawn or substantially cleaned by an artist. This is the Larian position after the backlash.
  2. Keep a **provenance register** of every AI-touched asset (tool, tier, date, cleanup level), so placeholders never slip into release (the Clair Obscur failure) and the Steam disclosure is accurate.
  3. Disclose on Steam for any pre-generated AI content. Undisclosed AI that is later discovered was punished more than disclosed use (Arc Raiders kept selling; Clair Obscur lost awards).
  4. Never use AI for store capsules or trailers.
  5. Consider the Dead Cells 3D-to-2D route for the main character if AI output cannot reach the bar.
- Because false accusations also happen, keep work-in-progress files that prove human authorship even for hand-made art.

### Gaps
- No reliable quantitative data on the sales impact of AI disclosure. The Stanford figure is unverified.
- Mobile-specific backlash evidence (App Store / Google Play reviews) was not found. Sentiment data is PC- and Steam-centric.
