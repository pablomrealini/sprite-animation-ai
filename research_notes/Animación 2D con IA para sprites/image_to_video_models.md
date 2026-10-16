# Image-to-video models for 2D game sprite animation (state as of 15 October 2026)

Scope: hosted and open-weight image-to-video (I2V) models used as the "motion engine" for 2D character sprites (side-view platformer and top-down; HD illustrated and pixel art). Out of scope here (covered in sibling notes): skeletal/cutout, ComfyUI/ControlNet/Wan Animate/Kling Motion Control pose-driven pipelines, 3D→2D, video→sprite post-processing, dedicated sprite tools, and in-depth legal analysis.

Reading guide: prices are dated wherever the source gives a date. "Runway API price" means Runway's resale price at $0.01/credit (see Q3). Anything from before mid-2025 is marked **[possibly stale]**. Vendor or reseller blogs are labelled as such. Claims that only came from a search-engine summary, with no page I could open, are kept in **Gaps** rather than presented as facts.

---

## Q1. Which models matter in October 2026, and what are their output specs (resolution, fps, duration, aspect ratio)?

### Takeaway
The field moved a lot between mid-2025 and October 2026:
- **Sora 2 is gone.** The API was shut down on 24 Sep 2026.
- **Google now has two I2V lines.** Veo 3.1 (Standard / Fast / Lite) and the newer **Gemini Omni Flash / Omni 1.1 Flash**. The Gemini API docs now recommend Omni Flash as the default.
- **New "3.x / 2.5-generation" Chinese models now top the general I2V leaderboard:** MiniMax H3 (Hailuo 3), Seedance 2.5, Kling 3.0 / O3 and Wan 3.0.
- **Format limits:**
  - Veo and Omni only output 16:9 or 9:16, at 24 fps.
  - Veo's minimum clip is 4 s. Omni's is 3 s. Kling's is 3 s.
  - Kling, Seedance and Wan offer 1:1 and other aspect ratios.

### Cited Findings

**Google Veo 3.1 (Gemini API / AI Studio / Vertex = "Gemini Enterprise Agent Platform" / Flow)**
- Gemini API model IDs:
  - `veo-3.1-generate-preview` and `veo-3.1-fast-generate-preview` (latest update January 2026)
  - `veo-3.1-lite-generate-preview` (March 2026)
  - `veo-3.0-generate-001` and `veo-3.0-fast-generate-001`, marked **deprecated**

  — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- On Google Cloud the GA IDs are `veo-3.1-generate-001`, `veo-3.1-fast-generate-001` and `veo-3.1-lite-generate-001` (preview). The page was last updated 2026-10-15. — [Google Cloud: first & last frames](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/generate-videos-from-first-and-last-frames)
- Veo 3.1 / 3.1 Fast specs:
  - 720p (default), 1080p and 4K. 1080p and 4K are 8 s only.
  - 24 fps.
  - Durations of 4, 6 or 8 s. The duration "must be 8" when using extension, reference images, 1080p or 4K.
  - Aspect ratio 16:9 (default) or 9:16.

  Veo 3.1 Lite has the same specs without 4K and without reference images or extension. — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- Older line: Veo 2 on Cloud takes 5–8 s. Veo 3 models take 4/6/8 s. 4K is listed for Veo 3.1 preview models only on Cloud. — [Google Cloud: first & last frames](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/generate-videos-from-first-and-last-frames)
- The Gemini API video overview (last updated 2026-06-30) recommends **Gemini Omni Flash as the default**. It suggests Veo 3.1 "for scene extension, last-frame control, or legacy pipeline integration". — [Gemini API video overview](https://ai.google.dev/gemini-api/docs/video)
- **No Veo 4.** As of a 19 May 2026 overview, Google had published no Veo 4 model ID, card or pricing. The I/O 2026 video model was Gemini Omni Flash instead. I found nothing newer confirming a Veo 4. — [PixVerse blog (third-party)](https://pixverse.ai/en/blog/veo-4-release)

**Google Gemini Omni Flash / Omni 1.1 Flash (new since May 2026)**
- Launched 19 May 2026 around Google I/O. It takes mixed text/image/audio/video inputs and offers conversational multi-turn video editing. — [LetsDataScience news summary](https://letsdatascience.com/news/google-launches-gemini-omni-flash-video-model-2cd9175a) (secondary)
- Omni 1.1 Flash was announced 27 Aug 2026:
  - Start and end keyframes.
  - Video references of up to 3 s.
  - Scene extension in 10 s increments up to 40 s total.
  - A **360p draft mode**, "up to 60% faster" and about one third of the 720p cost.
  - 1080p and 4K outputs via upscaling.

  Available in the Gemini API (`gemini-omni-1.1-flash`), AI Studio and Flow. — [Google blog, 27 Aug 2026](https://blog.google/innovation-and-ai/technology/developers-tools/build-with-gemini-omni-1-1-flash/)
- Specs:
  - Aspect ratio 16:9 (default) or 9:16.
  - Resolution 360p, 720p (default), 1080p (upscaled) or 4K (upscaled).
  - Generates audio by default.

  — [Gemini API Omni docs](https://ai.google.dev/gemini-api/docs/omni)
- On Cloud, Omni duration is any integer from 3 to 10 s. The original `gemini-omni-flash-preview` supports 720p only. — [Google Cloud: first & last frames](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/generate-videos-from-first-and-last-frames)

**Kling (Kuaishou)**
- Kling 3.0 ("V3") and Kling 3.0 Omni ("O3") launched together. Launch dates differ by source: 31 Jan, 4 Feb or 5 Feb 2026. There is no Kling 3.1. — [howaiworks](https://howaiworks.ai/models/kling); [Hedra O3 page](https://www.hedra.com/models/video/kling/o3-standard) (aggregators)
- Runway's API catalogue:
  - Kling 3.0 Standard: 720p.
  - Kling 3.0 Pro: 1080p.
  - Kling 3.0 4K.
  - All three take 3–15 s, multishot prompts and optional audio.
  - Kling O3 adds video input and image references.
  - Kling 2.5 Turbo Pro: 5 or 10 s, optional last frame.

  — [Runway API models](https://docs.dev.runwayml.com/guides/models/)

**Runway (own models)**
- Gen-4.5 (`gen4.5`) does text-to-video and image-to-video. Gen-4 Turbo (`gen4_turbo`) does image-to-video. Aleph 2.0 (`aleph2`) is video-to-video with keyframe-guided control. Runway's models page gives no duration, resolution or fps for Gen-4.5. — [Runway API models](https://docs.dev.runwayml.com/guides/models/)

**Luma (Dream Machine / Ray)**
- **Ray3.2** was announced 9 Jun 2026:
  - Clips "up to 20 seconds long at 1080p".
  - Native HDR and 16-bit EXR export.
  - Up to 16 keyframes per clip.
  - Performance tracking.
  - First time offered as an API.

  — [Luma: Introducing Ray3.2](https://lumalabs.ai/news/introducing-ray-3-2)
- fal's Ray 3.2 page says 1080p across modes, 10 s image-to-video generations, and seamless looping for text-to-video and image-to-video. — [fal Ray 3.2](https://fal.ai/ray-3.2)
- Luma's own API docs page (updated 10 Jul 2026) still documents only `ray-2` and `ray-flash-2`, at 540p / 720p / 1080p / 4K. — [Luma API docs](https://docs.lumalabs.ai/docs/video-generation)
- A comparison site also lists Ray3.14 and Ray3 HDR tiers. — [CostBench (third-party)](https://www.costbench.com/software/ai-media-apis/luma-dream-machine-api/)

**OpenAI Sora 2: discontinued**
- "The Sora 2 models and Videos API were shut down on September 24, 2026 and are no longer available." No replacement is offered. — [OpenAI video generation guide](https://developers.openai.com/api/docs/guides/video-generation)
- Shutdown was announced 24 Mar 2026. The app went dark 26 Apr 2026 and the API followed on 24 Sep 2026. — [The Decoder](https://the-decoder.com/openai-sets-two-stage-sora-shutdown-with-app-closing-april-2026-and-api-following-in-september/); [Engadget](https://engadget.com/ai/openai-is-shutting-down-its-sora-video-generation-app-211023358.html)
- Historical note: the API rejected input images that contained human faces. — [OpenAI video generation guide](https://developers.openai.com/api/docs/guides/video-generation)

**MiniMax Hailuo**
- Hailuo 02 (mid-2025) **[possibly stale]**. It was superseded by:
  - **Hailuo 2.3** (28 Oct 2025; max 1080p; max 10 s).
  - **MiniMax H3 / "Hailuo 3"** (July 2026; max 2K; max 15 s; native audio).

  — [gradually.ai comparison](https://www.gradually.ai/en/ai-video-model-comparison/minimax-h3-vs-hailuo-2-3/) (third-party; it also claims H3 has "open weights, 33B parameters", which I could not verify)
- Runware lists H3 (`minimax:h3@0`) with a release date of 30 Jul 2026. It takes first/last frames, and in frame mode the output "takes the aspect ratio of the image you feed it". — [Runware H3 docs](https://runware.ai/docs/models/minimax-h3/guides/first-and-last-frame)
- Runway's catalogue lists H3 Max (`h3_max`) at 480p / 768p with first and last frames, and `hailuo3` at 768p / 2K. — [Runway API models](https://docs.dev.runwayml.com/guides/models/); [Runway API pricing](https://docs.dev.runwayml.com/guides/pricing/)
- Conflicting claim: one blog says "Hailuo 3.0" is native 4K60 with 5–30 s clips. Treat that as unreliable. — [VidMuse](https://vidmuse.ai/blog/hailuo-3-0)

**ByteDance Seedance**
- Seedance 1.0 / 1.5 Pro (2025) **[older generation]**.
- **Seedance 2.0** (model ID `dreamina-seedance-2-0-260128`, plus `-fast-`). Its modes are:
  - text-to-video
  - first-frame I2V
  - first+last-frame I2V
  - multimodal reference-to-video
  - video editing

  — [BytePlus ModelArk docs](https://docs.byteplus.com/docs/ModelArk/2291680) (search snippet)
- **Seedance 2.5** was unveiled 23 Jun 2026 and rolled out publicly in July 2026 (Volcano Engine, BytePlus, Dreamina). Clips run up to 30 s. — [Atlas Cloud listing](https://www.atlascloud.ai/ko/models/bytedance/seedance-2.5/image-to-video) (reseller)
- OpenRouter lists 4–30 s, 480p / 720p, and aspect ratios 16:9, 4:3, 1:1, 3:4, 9:16, 21:9. — [OpenRouter Seedance 2.5](https://openrouter.ai/bytedance/seedance-2.5)
- Sources conflict on resolution. Runway's API lists 480p / 720p / 1080p for Seedance 2.5. — [Runway API models](https://docs.dev.runwayml.com/guides/models/)

**Alibaba Wan**
- **Open weights stop at Wan 2.2.** The Wan-AI Hugging Face org shows Wan2.2 repos and newer Animate / Dancer models, but no Wan 2.5 / 2.6 / 2.7 / 3.0 weights among the visible repos. — [Hugging Face Wan-AI](https://huggingface.co/Wan-AI)
- Wan2.2-I2V-A14B:
  - 480p / 720p.
  - Apache 2.0, with use restrictions in LICENSE.txt.
  - Released 28 Jul 2025.
  - The official single-GPU script needs ≥80 GB VRAM.

  TI2V-5B runs 720p at 24 fps on an RTX 4090 class GPU. — [Wan2.2-I2V-A14B model card](https://huggingface.co/Wan-AI/Wan2.2-I2V-A14B)
- **Wan 3.0** (August 2026) is API-only: preview on Alibaba Model Studio, up to 30 s, 480p / 720p / 1080p, "Open Source: No". — [Atlas Cloud blog](https://www.atlascloud.ai/blog/tips/is-wan-3.0-open-source); [EvoLink blog](https://evolink.ai/blog/wan-3-0-release) (resellers)
- Runway lists `wan3` at 2–30 s and 480p / 720p / 1080p with native audio. — [Runway API models](https://docs.dev.runwayml.com/guides/models/)
- Wan 2.7 (April 2026) takes 2–10 s at 720p / 1080p, with first and last frames. — [mer.vin, 19 Sep 2026](https://mer.vin/2026/09/which-ai-video-models-actually-take-a-first-and-last-frame/)

**Other notable models (brief)**
- From the AA image-to-video leaderboard:
  - Grok Imagine Video 1.5 (May 2026)
  - HappyHorse 1.0 / 1.1 (Alibaba-ATH)
  - FLUX 3 (Black Forest Labs, Jul 2026)
  - MAGI-2 Preview (Sand.ai)
  - Vidu Q3 Pro / Turbo (Jan–Feb 2026)
  - PixVerse V6 (Mar 2026)
  - LTX-2.5 Fast (Lightricks, Aug 2026)

  — [Artificial Analysis I2V leaderboard](https://artificialanalysis.ai/video/leaderboard/image-to-video)
- Midjourney video (V1, June 2025) **[possibly stale]**:
  - About 5 s clips, extendable.
  - An "Ending Frame" slot and a **Loop checkbox**.
  - Web UI only. There is no official API.

  — [dev.to guide (third-party)](https://dev.to/_37bbf0c253c0b3edec531e/how-to-use-midjourneys-v1-video-model-4i7b)

**General-preference ranking (not style-specific)**
- Elo confidence intervals are about ±14–20, so neighbouring models are effectively tied. Prices are $ per minute of 1080p on the creator's API. The newest model listed is from August 2026.

| Rank | Model | Elo | Released | Price per minute (1080p) |
|---|---|---|---|---|
| 1 | MiniMax H3 (768p) | 1141 | Jul 2026 | $5.40 |
| 2 | Seedance 2.5 | 1139 | Jul 2026 | $24.60 |
| 3 | Gemini Omni Flash 1.1 | 1134 | Aug 2026 | $9.12 |
| 4 | Wan 3.0 | 1127 | Aug 2026 | $12.00 |
| 5 | MiniMax H3 Max | 1124 | Aug 2026 | $5.76 |
| 6 | Seedance 2.0 | 1121 | Mar 2026 | $22.45 |
| 12 | Wan 2.7 | 1033 | Apr 2026 | $9.00 |
| 13 | Veo 3.1 | 1031 | Jan 2026 | $24.00 |
| 15 | Veo 3.1 Fast | 1017 | Jan 2026 | $9.00 |
| 17 | Kling 3.0 Omni Pro | 1004 | Feb 2026 | $16.80 |
| 18 | Kling 3.0 Pro | 1000 | Feb 2026 | $20.16 |

  — [Artificial Analysis I2V leaderboard](https://artificialanalysis.ai/video/leaderboard/image-to-video)

**Spec comparison table (Oct 2026)**

| Model (latest) | Max res. | fps | Clip length | Aspect ratios | Audio | Key sources |
|---|---|---|---|---|---|---|
| Veo 3.1 / Fast | 4K (8 s only); 720p default | 24 | 4/6/8 s; extend +7 s ×20 → 148 s | 16:9, 9:16 | Always on in Gemini API | [Veo docs](https://ai.google.dev/gemini-api/docs/veo) |
| Veo 3.1 Lite | 1080p (8 s only) | 24 | 4/6/8 s | 16:9, 9:16 | Always on | [Veo docs](https://ai.google.dev/gemini-api/docs/veo) |
| Gemini Omni 1.1 Flash | 4K (upscaled); 360p draft | n/s | 3–10 s (Cloud); extend to 40 s | 16:9, 9:16 | On by default | [Omni docs](https://ai.google.dev/gemini-api/docs/omni); [Cloud](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/generate-videos-from-first-and-last-frames) |
| Kling 3.0 (Std/Pro/4K) | 720p / 1080p / 4K | n/s | 3–15 s | n/s (1:1 used in a sprite tool) | Optional | [Runway models](https://docs.dev.runwayml.com/guides/models/); [GitHub skill](https://github.com/TamerinTECH/claude-skill-klingai-animation) |
| Kling O3 | 720p / 1080p / 4K | n/s | n/s (family 3–15 s) | n/s | Optional | [Runway models](https://docs.dev.runwayml.com/guides/models/) |
| Runway Gen-4.5 | n/s | n/s | n/s | n/s | n/s | [Runway models](https://docs.dev.runwayml.com/guides/models/) |
| Luma Ray3.2 | 1080p, HDR / EXR | n/s | up to 20 s (I2V 10 s on fal) | n/s | n/s | [Luma](https://lumalabs.ai/news/introducing-ray-3-2); [fal](https://fal.ai/ray-3.2) |
| MiniMax H3 | 2K (768p tier also sold) | n/s (24 fps per one secondary source) | 5–15 s | Follows the input image in frame mode | Native | [Runware](https://runware.ai/docs/models/minimax-h3/guides/first-and-last-frame); [gradually](https://www.gradually.ai/en/ai-video-model-comparison/minimax-h3-vs-hailuo-2-3/) |
| Seedance 2.5 | 720p (OpenRouter) or 1080p (Runway); conflict | n/s | 4–30 s | 16:9, 4:3, 1:1, 3:4, 9:16, 21:9 | Optional | [OpenRouter](https://openrouter.ai/bytedance/seedance-2.5); [Runway models](https://docs.dev.runwayml.com/guides/models/) |
| Seedance 2.0 | 1080p (4K per some sources) | 24 (token formula) | 4–15 s | n/s | Optional | [mer.vin](https://mer.vin/2026/09/which-ai-video-models-actually-take-a-first-and-last-frame/) |
| Wan 3.0 (API only) | 1080p | 30 (854×480 test) | 2–30 s | n/s | Native | [Runway models](https://docs.dev.runwayml.com/guides/models/); [mer.vin](https://mer.vin/2026/09/which-ai-video-models-actually-take-a-first-and-last-frame/) |
| Wan 2.2 (open) | 720p | 24 (TI2V-5B) | about 5 s | Follows the input image | None | [HF card](https://huggingface.co/Wan-AI/Wan2.2-I2V-A14B) |
| Sora 2 | n/a, shut down 24 Sep 2026 | n/a | n/a | n/a | n/a | [OpenAI](https://developers.openai.com/api/docs/guides/video-generation) |

(n/s = not stated in the sources I could read.)

### Inferences
- The users liked "Veo in AI Studio". AI Studio now pushes Gemini Omni Flash as the default video model. They should check which model actually produced the "perfect" result and test both.
- Omni has some sprite-relevant advantages over Veo 3.1:
  - 3 s minimum clip.
  - 360p drafts.
  - A documented first=last loop (Q2).
- Veo's 16:9 / 9:16-only output and 720p floor mean a sprite fills only a small part of the frame. You will crop and downscale anyway, so this is mostly a cost-per-useful-pixel issue, not a blocker. Kling, Seedance and H3-in-frame-mode allow square or input-shaped canvases, which fit a sprite cell better.
- 24 fps output is far more frames than a sprite needs (8–12 fps). Frame selection, not frame rate, is the real constraint.

### Gaps
- No primary spec sheet found for Runway Gen-4.5 duration, resolution or fps, or for Kling 3.0 aspect ratios and fps.
- Seedance 2.5 maximum resolution conflicts across sources (720p vs 1080p vs 4K).
- The MiniMax H3 open-weights claim is unverified.
- I could not confirm whether any Veo 4 has launched after May 2026. Google's own pages still list Veo 3.1 as the newest Veo.

---

## Q2. Conditioning and loop control: first frame, last frame, references, motion brush, camera control, and does first frame == last frame give a seamless loop?

### Takeaway
- **First+last frame is now common:** Veo 3.1, Omni, Kling 3.0 / O3 / 2.5 Turbo, Seedance 2.0 / 2.5, H3, Wan 2.7, Luma, Vidu, PixVerse and LTX all take it.
- **Only a few models have an explicit loop feature:**
  - Luma Ray (`loop: true`)
  - Gemini Omni (same image as first and last frame is officially documented as a loop)
  - Midjourney (Loop checkbox)
- **In practice, first == last tends to produce a near-static clip.** The model "returns home" by barely moving. Small tests found that a local crossfade or ping-pong gave cleaner seams while keeping more motion.
- **Several "first-frame only" models silently ignore a second frame:** Runway Gen-4.5, Wan 3.0, Hailuo 2.3 and Kling 2.6.

### Cited Findings

**Veo 3.1**
- Fields:
  - `image` is the first frame.
  - `lastFrame` must be used together with `image`.
  - `referenceImages` takes up to 3 `VideoGenerationReferenceImage` items (`referenceType: "asset"`, "style and content references"). They are not available on Lite or Veo 3.

  — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- Reference images must be "up to three asset images of a single person, character, or product", and the clip must be 8 s long. — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- REST constraint: when `referenceImages` are given, `image`, `video` and `lastFrame` cannot be used. You can anchor to an exact first frame or to references, not both. The "style" reference type is described as covering colour, lighting and texture. — [search summary of Google Cloud REST reference](https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/rest/Shared.Types/VideoGenerationModelInstance) (summary only; verify)
- No seed or negative-prompt parameter is documented for Veo 3.1 on the Gemini API page. Seed exists only for Veo 3 and "slightly improves" determinism. — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- Camera control is prompt-only: "aerial view", "eye-level", "top-down shot", "dolly shot", "worms eye". — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- Community reports, not confirmed by Google:
  - A Vertex user (Jan 2026) had `lastFrame` with a 4 s clip rejected ("Your use case is currently not supported").
  - A forum thread title reports Veo 3.1 reference images rejected as "not supported" despite the docs.

  — [Google AI dev forum thread](https://discuss.ai.google.dev/t/veo-3-api-generate-audio-parameter-not-supported-last-frame-limitations/119206); [forum thread title](https://discuss.ai.google.dev/t/veo-3-1-reference-images-docs-say-available-api-says-not-supported/111853)
- Flow (consumer UI) tiers:
  - Google AI Pro ($19.99) includes "Frames to Video" (first/last frame).
  - "Ingredients to Video" (up to 3 reference images) is listed under Ultra ($249.99).

  — [Google Flow about page](https://labs.google/flow/about) (via search summary)

**Gemini Omni Flash / 1.1**
- Tag semantics:
  - `<FIRST_FRAME>`: "use the image as the starting frame of the video".
  - `<LAST_FRAME>`: "use the image as the final frame of the video to transition to". It must be used with `<FIRST_FRAME>`.
  - **Declaring the same image as both "will use the first image as both the first frame and the last frame, creating a video that loops"**. Suggested prompt line: "Use this image as the first frame and the last frame."

  — [Gemini API Omni docs](https://ai.google.dev/gemini-api/docs/omni)
- `<IMAGE_REF_N>` reference images "should not be used as literal initial frames". The docs show an example with 6 reference images. Video references are capped at 3 clips of up to 3 s each and work "best with likenesses". — [Gemini API Omni docs](https://ai.google.dev/gemini-api/docs/omni)
- Negative prompts are not a parameter: "you can put your negatives in the regular prompt: e.g., 'Do not do X'". Temperature, `top_p` and system instructions are also unsupported. — [Gemini API Omni docs](https://ai.google.dev/gemini-api/docs/omni)
- On Runware, Omni frame mode takes at most 2 frames (`first`/`last`, or 0/-1) and **cannot be combined with reference images or videos**. Images must be ≤5 MB and ≤4096². — [Runware Omni 1.1 first/last frame guide](https://runware.ai/docs/models/google-gemini-omni-flash-1-1/guides/first-and-last-frame)

**Kling**
- Kling 3.0 takes a start frame, an end frame, or both on one endpoint. Per Krea, it "takes no reference images", so recurring characters must come via the start image. — [Krea Kling 3.0 guide](https://www.krea.ai/blog/kling-3-0-api-access-guide-pricing-code-examples-for-multi-shot-ai-video) (reseller)
- Kling O3 Standard accepts up to 3 reference images plus start and end frames. It also has "Element Reference" tags to lock face and clothing across cuts. — [Hedra O3 page](https://www.hedra.com/models/video/kling/o3-standard) (reseller)
- Kling image2video API fields (as exposed by the CometAPI proxy):
  - `model_name` up to `kling-v3` ("Use `kling-v3` for new requests").
  - `image_tail`: "Controls the last frame".
  - `negative_prompt`: max 200 chars.
  - `cfg_scale`: 0–1.
  - `static_mask`: motion-brush region that stays frozen.
  - `dynamic_masks`: mask plus trajectory.
  - `sound`: on/off.
  - `duration`: 5/10.

  The proxy docs do not state which features work on which Kling version. `camera_control` is not mentioned. — [CometAPI Kling image-to-video docs](https://apidoc.cometapi.com/api/video/kling/image-to-video.md) (third-party proxy)
- fal exposes Kling 3.0 Pro I2V with `start_image_url` and an optional `end_image_url`. — [fal explore page](https://fal.ai/explore/image-to-video-apis)

**Luma**
- Luma API:
  - `keyframes.frame0` / `frame1` take images or prior generations.
  - A boolean **`loop`** parameter.
  - `concepts` (e.g., `dolly_zoom`).
  - Camera-motion strings from `/generations/camera_motion/list`.
  - Extend forward or reverse, and interpolate between two generations.

  — [Luma API docs (updated 10 Jul 2026)](https://docs.lumalabs.ai/docs/video-generation)
- The loop flag conflicts with `end_image`. It exists on `luma/ray-3.2`, `ray-2-720p` and `ray-flash-2-540p`. Per the source, the Luma Ray family is the only one with a real loop flag among the 29 OpenRouter models it surveyed. — [mer.vin, 19 Sep 2026](https://mer.vin/2026/09/which-ai-video-models-actually-take-a-first-and-last-frame/)
- Ray3.2 supports up to 16 keyframes per clip. — [Luma Ray3.2](https://lumalabs.ai/news/introducing-ray-3-2)

**MiniMax H3**
- First and last frames go in `inputs.frameImages` with `frame: "first" | "last"`. The pair "works best when the two frames share a composition and differ in one thing". The page does not mention loops. — [Runware H3 docs](https://runware.ai/docs/models/minimax-h3/guides/first-and-last-frame)

**Seedance 2.0 / 2.5**
- Seedance 2.0 has first-frame, first+last, and multimodal reference modes. — [BytePlus ModelArk docs](https://docs.byteplus.com/docs/ModelArk/2291680) (search snippet)
- A ComfyUI node exposes up to 9 `reference_image_N`, 3 `reference_video_N` and 3 `reference_audio_N`, plus `first_frame_image` / `last_frame_image`. Prompts cite references with `@Image1`-style tags. — [ComfyUI ModelArk Seedance 2.0 node](https://comfy.icu/node/ModelArk-Seedance-2-0) (community)
- Seedance 2.5 supports first frame and first+last frame. Resellers claim up to 50 reference assets. — [OpenRouter](https://openrouter.ai/bytedance/seedance-2.5); [Atlas Cloud](https://www.atlascloud.ai/ko/models/bytedance/seedance-2.5/image-to-video)
- Seedance 2.5 `seed` works in its 480p draft mode. — [Runway API models](https://docs.dev.runwayml.com/guides/models/)

**Which endpoints silently ignore a last frame**
- These models are first-frame only "despite the names": `alibaba/wan-3`, `runwayml/gen-4.5`, `minimax/hailuo-2.3`, `kwaivgi/kling-v2.6`, `wan-video/wan-2.5-i2v-fast`. "The second frame is silently ignored and you are billed for a prompt-only clip." — [mer.vin](https://mer.vin/2026/09/which-ai-video-models-actually-take-a-first-and-last-frame/)
- Field names differ by provider:
  - Veo: `image` / `lastFrame`.
  - Kling, Luma, Vidu: `start_image` / `end_image`.
  - Seedance, PixVerse, LTX: `image` / `last_frame_image`.
  - Wan 2.7: a typed media list.

  — [mer.vin](https://mer.vin/2026/09/which-ai-video-models-actually-take-a-first-and-last-frame/)

**How well first == last actually loops (evidence)**
- Small measured tests, mostly a single still image with ambient motion. Metrics are churn (mean pixel change between frames) and seam (difference between last and first frame).
- Keyframe models given the same image twice moved about **10× less**:
  - `wan2.2-kf2v-flash`: tree churn 2.67 vs 34.14 for first-frame-only `wan2.6-i2v-flash`.
  - Veo 3.1 Lite: whole-frame drift 2.5 vs 29.3 unconstrained.
- In a 4-model test, none looped on its own:
  - `prunaai/p-video` was near-static.
  - LTX-2.5-fast "re-rendered" the scene (frame-0 drift 34.3).
  - Wan 3 had no last-frame input.
- Seam scores by loop strategy:

| Strategy | Seam |
|---|---|
| Raw I2V, no loop | 25.62 |
| Model keyframe loop (first == last) | 2.89 |
| Local crossfade | 2.69 |
| Local ping-pong | 1.33 |

  Conclusion: "closing the loop locally keeps the motion, while paying a keyframe model buys stillness". Prompt wording changed motion by only −28% to +10%. A clip planned as 2 s had more motion per second and a cleaner seam than the first 2 s of a 5 s clip. — [mer.vin](https://mer.vin/2026/09/which-ai-video-models-actually-take-a-first-and-last-frame/)
- Sprite-pipeline guide (Kling): using the same image as first and final frame "can produce a still video". The fix is to omit the final-frame input and pick an ending frame from the output, then generate "bridge frames" with an image model to connect to idle. — [LayrKits sprite-sheet guide](https://www.layrkits.com/guides/sprite-sheet)
- An Adobe community manager, replying to a Veo 3.1 Fast error with two identical frames, said identical first/last frames are "only a workaround" that "can still lead to issues", and recommended Luma Ray2's loop toggle. — [Adobe community thread](https://community.adobe.com/bug-reports-403/generic-error-when-using-two-reference-frames-for-video-looping-in-veo-3-1-fast-1553443) (via search summary)
- Kling's own pixel-art page says no loop is guaranteed from generation alone. It recommends trimming or crossfading the ends in an editor, and prompting motion "that doesn't end in a very different pose from its starting pose". — [Kling: animate pixel art](https://kling.ai/topics/animate-pixel-art-ai)

### Inferences
- For **idle / breathing / hover** loops, first == last (Omni, Veo, Kling `image_tail`, Luma `loop`) is worth trying, because idles have small amplitude anyway. The "near-static" failure is partly what you want. Ping-pong also works for idles.
- For **walk / run cycles**, first == last is risky. The model may shrink the stride to "get home". Ping-pong is wrong because a reversed walk looks like moonwalking. Better options:
  - Generate a longer in-place walk (4–8 s) and pick a cycle where the pose recurs (contact pose to contact pose).
  - Or use first == last only with explicit motion timing in the prompt, e.g., Omni timecodes.

  This is an inference from the measurements above plus standard sprite practice. No source tested walk cycles with first == last.
- Veo 3.1's rule that references and first/last frames cannot be combined means sprite work on Veo should use the exact concept image as `image` (first frame), not references. References only make the character "similar", which is not enough for a sprite.
- Runway Gen-4.5, Wan 3.0 and Hailuo 2.3 are poor choices when you need end-frame control, because the end frame is silently dropped.

### Gaps
- No controlled test found of first == last on a **character action cycle** (walk, run) for any model. All measured loop tests used ambient scenes.
- Unclear whether Kling v3 honours `static_mask` / `dynamic_masks` (motion brush) or whether these are older-version features. The only source is a proxy's docs.
- Exact field name and behaviour of Luma Ray3.2's loop flag in Luma's own API docs are not confirmed. Luma's docs page still shows Ray 2.

---

## Q3. API availability and price per second (October 2026)

### Takeaway
- **Cheapest useful options:**
  - Veo 3.1 Lite (~$0.05/s at 720p) and Veo 3.1 Fast (~$0.10/s) on the Gemini API.
  - Gemini Omni Flash (~$0.10/s at 720p, ~$0.034/s at 360p via Runway).
  - MiniMax H3 / H3 Max ($0.05–0.10/s).
  - Kling 3.0 Std/Pro without audio ($0.09–0.12/s).
  - Wan 3.0 480p/720p ($0.025–0.10/s).
- **Most expensive:** Veo 3.1 Standard ($0.40/s with audio) and Seedance 2.0 / 2.5 ($0.20–0.68/s).
- **Audio:** turning it off halves Veo's price on Vertex and Runway. On the Gemini API, audio cannot be turned off.
- **Duration floors** (Veo 4 s, H3 5 s, Seedance 4 s) dominate the cost of short sprite clips.

### Cited Findings

**Google direct (Gemini API, paid tier only; page "Last updated 2026-10-15 UTC")**

| Model | 720p | 1080p | 4K |
|---|---|---|---|
| Veo 3.1 Standard | $0.40/s | $0.40/s | $0.60/s |
| Veo 3.1 Fast | $0.10/s | $0.12/s | $0.30/s |
| Veo 3.1 Lite | $0.05/s | $0.08/s | n/a |

- These are the "video with audio (default)" prices. No silent price is listed. **Veo is "Not available" on the free tier.** — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- Gemini Omni Flash (`gemini-omni-1.1-flash` and `gemini-omni-flash-preview`): input $1.50 per million tokens and video output $17.50 per million tokens. At 5,792 tokens per second of 720p, that is "approximately $0.10 per second". No free tier. — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- Omni 1.1's 360p mode costs about one third of 720p. — [Google blog](https://blog.google/innovation-and-ai/technology/developers-tools/build-with-gemini-omni-1-1-flash/)
- **Vertex silent (no-audio) prices**, from a Sept 2026 third-party rate-card read (not verified on Google's own page; the Vertex pricing page did not render for me):
  - Veo 3.1 Lite $0.03 (720p) / $0.05 (1080p).
  - Veo 3.1 Fast 720p $0.08.
  - Veo 3.1 Standard 720p $0.20.

  — [mer.vin](https://mer.vin/2026/09/which-ai-video-models-actually-take-a-first-and-last-frame/)
- **Flow subscriptions:**
  - Google AI Pro gets 1,000 monthly AI credits and AI Ultra gets 25,000.
  - Per the Pro table, Veo 3.1 Fast costs 20 credits per generation and Quality costs 100.
  - One Flow request may produce 2 generations.

  — [Google One support](https://support.google.com/googleone/answer/16287445) (via search summary)

**Runway API ($0.01 per credit; a convenient multi-vendor reseller with a single bill)**

| Model | Runway API price per second |
|---|---|
| Gen-4.5 | $0.12 |
| Gen-4 Turbo | $0.05 |
| Aleph 2.0 (video-to-video) | $0.28 |
| Veo 3.1 | $0.40 with audio / $0.20 without |
| Veo 3.1 Fast | $0.15 with audio / $0.10 without |
| Gemini Omni Flash 1.1 | $0.034 (360p) / $0.10 (720p) / $0.15 (1080p) / $0.30 (4K), plus $0.01 per reference image |
| Kling 3.0 Standard | $0.09 / $0.13 with audio |
| Kling 3.0 Pro | $0.12 / $0.17 with audio |
| Kling 3.0 4K | $0.43 |
| Kling O3 Standard / Pro | $0.13 / $0.17 |
| Kling 2.5 Turbo Pro | $0.12 |
| Seedance 2.5 | $0.20 / $0.30 / $0.68 (480p / 720p / 1080p) |
| Seedance 2.0 | $0.36 (480p/720p), $0.40 (1080p), $1.50 (4K) |
| Seedance 2.0 Fast | $0.29 |
| Seedance 2.0 Mini | $0.16 |
| MiniMax `hailuo3` (H3) | $0.10 (768p) / $0.15 (2K), plus $0.02 per reference or keyframe |
| MiniMax `h3_max` | $0.05 (480p) / $0.08 (768p) |
| Wan 3.0 | $0.05 / $0.10 / $0.20 (480p / 720p / 1080p) |
| Grok Imagine 1.5 | $0.10 / $0.16 / $0.29 |

  — [Runway API pricing](https://docs.dev.runwayml.com/guides/pricing/) (the only date on the page relates to an audio model changing on 12 Oct 2026)

**fal.ai**
- Kling 3.0 Pro I2V: $0.112/s audio off, $0.168/s audio on, $0.196/s with voice control.
- Veo 3.1: $0.20/s without audio, $0.40/s with audio (720p/1080p).
- Kling 2.5 Turbo Pro: $0.35 per 5 s, then $0.07 per extra second.
- Seedance 2.0: $0.3024/s at 720p. Seedance 2.0 Fast: $0.2419/s.
- The page has no date.

  — [fal I2V explore page](https://fal.ai/explore/image-to-video-apis)
- fal article dated 13 Mar 2026:
  - PixVerse v5.6: $0.35–0.75 per 5 s clip.
  - Hailuo 2.3 Pro: $0.49 per generation.
  - LTX-2-19B: $0.0018 per megapixel of video.

  — [fal: AI image-to-video generators](https://fal.ai/learn/tools/ai-image-to-video-generators) (vendor; may be stale)

**Replicate / OpenRouter (Sept 2026 rate-card reads)**
- Wan 3: $0.025 / $0.05 / $0.10 per s (480p / 720p / 1080p).
- Seedance 1.5 Pro: $0.013 / $0.026 / $0.06 per s.
- Luma Ray 3.2 at 540p: about $0.15 per 5 s clip.
- Kling v3.0 Pro: $0.112/s on OpenRouter.
- Seedance 2.0 1080p: about $0.374/s on OpenRouter.
- Wan VACE on fal: $0.04–0.08/s.

  Billing caveats from the same source:
  - Seedance bills by video token: width × height × fps × seconds ÷ 1024.
  - Veo's 4/6/8 s floor means a "2 s" Veo 1080p clip bills as 8 s.
  - Audio is on by default for Seedance, Veo and LTX on Replicate.

  — [mer.vin](https://mer.vin/2026/09/which-ai-video-models-actually-take-a-first-and-last-frame/)

**Seedance direct (BytePlus)**
- Token-based pricing. Example costs for 5 s with no video input: $0.35 (480p), $0.76 (720p), $1.87 (1080p), $3.89 (4K). — [Picasso IA guide](https://blog.picassoia.com/seedance-api-pricing-key-byteplus-access-and-docs) (third-party, citing BytePlus)
- OpenRouter lists Seedance 2.5 from $0.1028/s. — [OpenRouter](https://openrouter.ai/bytedance/seedance-2.5)

**Kling direct**
- Official Kling developer pricing is sold as prepaid credit packs. I could not render the official page. Secondary June 2026 figures: V3 Standard 720p about $0.10/s, V3 Pro 1080p about $0.16/s, O3 with audio about $0.24–0.40/s. — [search summary citing aireiter/evolink guides](https://aireiter.com/blog/kling-3-api-pricing-guide-2026) (secondary)

**MiniMax H3 elsewhere**
- Segmind: 2K 5 s for $0.8125 and 2K 15 s for $2.4375. — [Segmind H3 pricing](https://www.segmind.com/models/minimax-h3-reference-to-video/pricing)

**Luma direct**
- API pricing is credit-based and partly "custom". Treat the figures as approximate. — [CostBench](https://www.costbench.com/software/ai-media-apis/luma-dream-machine-api/) (comparison site)

**Self-hosting**
- Wan 2.2 is free (Apache 2.0). It needs ≥80 GB VRAM for the official A14B single-GPU script, or a 4090-class GPU for TI2V-5B (720p, under 9 min per 5 s clip). — [Wan2.2 model card](https://huggingface.co/Wan-AI/Wan2.2-I2V-A14B)

### Inferences
- Example costs:
  - A 4 s, 720p Veo 3.1 Fast clip on the Gemini API costs about $0.40.
  - The same clip on Standard costs about $1.60.
  - On Lite it costs about $0.20.
  - A 3 s Omni 720p clip costs about $0.30, or about $0.10 as a 360p draft.
- A character with 6 animations at about 5 attempts each is roughly 30 clips. That is about $6–$12 on Fast or Omni and $48 on Veo Standard. Cost is not the bottleneck; iteration time and selection labour are.
- Runway's API (or fal / OpenRouter) is a practical way to A/B several vendors with one key. Resale prices can exceed direct prices, though. Veo Fast is $0.15/s with audio on Runway vs $0.10/s direct.

### Gaps
- Official Vertex AI Veo price table and official Kling / Luma / MiniMax / BytePlus price pages could not be read directly. Those figures are second-hand.
- Whether AI Studio still gives free Veo generations in its UI is unresolved:
  - The pricing page says AI Studio usage is free in available regions, while Veo shows "Not available" on the free tier.
  - A third-party site claims 5–10 free Veo generations per day in AI Studio, which I could not confirm.

  — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing); [Veo3Gen "is Veo 3.1 free"](https://www.veo3gen.app/blog/is-veo-3-1-free)

---

## Q4. Commercial use, ownership and watermarks (brief; legal is covered elsewhere)

### Takeaway
- **Google (Gemini API):** Google does not claim ownership of outputs. All Veo and Omni videos carry invisible SynthID. The unpaid tier lets Google use your data.
- **Most consumer apps:** free tiers are watermarked and often non-commercial. Use paid plans or APIs for production assets.
- **Open weights:** Wan 2.2 is Apache 2.0. LTX-2.x is free under $10M revenue.
- **Sora** is no longer an option.

### Cited Findings
- **Gemini API Additional Terms** (effective 23 Mar 2026, updated 28 Apr 2026):
  - Google "won't claim ownership over that content".
  - "You're responsible for your use of generated content".
  - Google may generate similar content for others.
  - Use is "for professional or business purposes".
  - No building competing models.
  - **Unpaid services:** content is used to improve products, human reviewers may read it, and the terms say "Do not submit sensitive, confidential, or personal information". A project counts as paid only with an active billing account.

  — [Gemini API terms](https://ai.google.dev/gemini-api/terms)
- **SynthID:** "SynthID watermark — Yes" for all Veo models. For Omni: "All generated videos include SynthID watermarking, which is invisible to viewers". — [Veo docs](https://ai.google.dev/gemini-api/docs/veo); [Omni docs](https://ai.google.dev/gemini-api/docs/omni)
- **Veo `personGeneration`:** image-to-video, interpolation and reference modes allow only `allow_adult`. In the EU, UK, CH and MENA, `allow_adult` is the only value. — [Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- **Omni regional limits:** uploading or editing images with minors, and uploaded-video editing and extension, are unavailable in the EEA, Switzerland and the UK. — [Omni docs](https://ai.google.dev/gemini-api/docs/omni)
- **Wan 2.2:** Apache 2.0, with use restrictions in LICENSE.txt. — [Wan2.2 model card](https://huggingface.co/Wan-AI/Wan2.2-I2V-A14B)
- **LTX-2.x community licence:** free commercial use under $10M annual revenue, counted at the group level; a paid agreement is needed above that. A watermarking/provenance duty flows down. Secondary sources; the licence PDF is for LTX-2, dated 5 Jan 2026. — [Lightricks LTX-2 licence PDF](https://static.lightricks.com/legal/ltx-2-open-weights-license-0.X.pdf); [St-Hakky guide](https://book.st-hakky.com/en/data-science/ltx-2-5-commercial-license-guide)
- **Consumer free tiers (third-party roundups):**
  - Runway's free tier is watermarked; commercial use is reportedly granted on all plans.
  - Kling's free-tier commercial rights are disputed between sources.
  - Luma's free output is watermarked, with commercial use from the paid Plus tier.

  — [Scrimba roundup](https://scrimba.com/articles/free-ai-video-generators-2026/); [Arcade roundup](https://www.arcade.software/post/ai-video-generator-free) (secondary; mapping of each claim to each page is approximate)

### Inferences
- Run production generations through a **paid API project**. On Google that means a billing-enabled Gemini API key or Vertex, both for the data-use terms and because Veo is not on the free tier.
- SynthID is invisible and survives in the video. Whether it survives frame extraction, downscaling to sprite size and palette quantization is untested, and matters for the legal note.

### Gaps
- Current BytePlus (Seedance), MiniMax and Kling API output-ownership clauses were not retrieved. Defer to the legal note.

---

## Q5. How well does each model keep a flat 2D illustrated look or pixel art (vs 3D shading, motion blur, morphing, camera moves)?

### Takeaway
- **There is no independent, controlled benchmark of flat-2D or pixel-art fidelity for I2V models.** General leaderboards measure realism-weighted preference.
- The scattered evidence:
  - **Veo 3.1:** one anime test found it held a studio style best.
  - **Kling 3.0:** one test found it "doesn't properly understand" a strict anime style. Kling's own guide says big or fast motion blurs pixel edges.
  - **One open-source sprite tool** advises *against* Veo and Wan 2.x because they "favor camera moves". The users' own experience (Veo "perfect") contradicts this.
- **Expect to test.** The users' successful Veo result is itself the strongest data point available.

### Cited Findings
- **Piclumen (18 Aug 2026; one 10 s anime prompt with a start frame, no scoring method):**
  - Veo 3.1 "held the Ufotable look consistently" and had the cleanest slow-motion.
  - Kling 3.0 "doesn't seem to properly understand the style".
  - Seedance 2.5 "delivered strong anime style" but with "clean, live-action-leaning detail".
  - Runway Gen-4.5 was not tested for style.

  — [Piclumen comparison](https://www.piclumen.com/blog/4-best-ai-animation-models/) (vendor blog)
- **Kling's official pixel-art guide (11 Jul 2026):**
  - "There's no special pixel mode."
  - Use small, slow, repeatable ambient motion; big or fast motion blurs crisp pixel edges.
  - Demo prompt ends "subtle looping ambient idle animation, everything stays in crisp clean pixel-art style".

  — [Kling: animate pixel art](https://kling.ai/topics/animate-pixel-art-ai)
- **Claude Code sprite skill (Kling-based):** lists `veo3*`, `cinematic_studio_*`, `soul_cast` and `wan2_*` as "avoid for sprites" because they favour camera moves. It defaults to Kling (v3 direct, or `kling2_6` via Higgsfield). — [TamerinTECH GitHub](https://github.com/TamerinTECH/claude-skill-klingai-animation)
- **Scenario (vendor, 27 Apr 2026):** recommends Seedance 2.0 as "the most capable option for animation sequences" and Veo 3.1 for "fluid, natural motion". — [Scenario blog](https://www.scenario.com/blog/ai-sprite-generator)
- **fal (vendor, Mar 2026):** describes Veo and Sora as chasing "photorealism and cinematic fidelity". PixVerse v5.6 is described as "stylized and effects-driven". — [fal article](https://fal.ai/learn/tools/ai-image-to-video-generators)
- **Kling vs Veo (Elser, 2026):** Kling was cleaner on camera movement and Veo better on natural physics. In one test Veo hallucinated a different interior scene, i.e., inconsistent prompt adherence. — [Elser blog](https://www.elser.ai/blog/kling-ai-vs-veo-2026) (via search summary)
- **First-frame fidelity varies:** frame 0 drifted from the input image by 6.1 (p-video), 6.2 (Wan 3) and 34.3 (LTX-2.5-fast, which "re-rendered" the scene and changed faces). The author calls LTX-2.5-fast "useless when the input image is the subject". — [mer.vin](https://mer.vin/2026/09/which-ai-video-models-actually-take-a-first-and-last-frame/)
- **Pixel art in diffusion generally:** don't generate at the target sprite size (32×32 "gives mush"). Generate at a comfortable resolution and reduce to the true pixel grid afterwards; that reduction step is where the pixel look comes from. — [AI gaming docs: generating sprites](https://aigaming.nuilab.org/workflows/sprites/) (image pipeline, but applies equally to video frames)
- The AA leaderboard has no animation or style category. It covers Text-to-Video, Image-to-Video and Video Editing only. — [Artificial Analysis](https://artificialanalysis.ai/text-to-video/arena?tab=leaderboard&input=image)

### Inferences
- For **HD illustrated** sprites:
  - Veo 3.1 (and probably Omni, same vendor) is the best-supported choice given the users' own success and the one anime test.
  - Seedance 2.x is worth an A/B test, but watch for "live-action-leaning" detail creeping in.
  - Kling is the most widely used in sprite tooling, mainly for camera-lock obedience and price, not style fidelity.
- For **pixel art**, no video model reliably preserves a hard pixel grid. Practical approach:
  1. Animate a 4–8× upscaled (nearest-neighbour) version of the sprite with subtle motion.
  2. Downscale with nearest-neighbour.
  3. Re-quantize to the palette in post.

  Expect the model to blur pixel edges on fast motion. (Inference from the Kling and nuilab guidance; post-processing is in the sibling note.)
- Camera drift is the main style killer for sprites, because any zoom or pan breaks frame registration. Models' camera-lock obedience matters more than their aesthetic quality here.

### Gaps
- No Reddit, X or YouTube side-by-side of Veo vs Kling vs Seedance vs H3 on a **flat cel-shaded game character** or **pixel-art sprite** could be retrieved. The search tools did not index the relevant reddit.com threads.
- Search-engine summaries mentioned several unverified claims; I could not open the specific pages that make them:
  - "Wan 2.7 most reliably keeps inked lines and flat shading".
  - "Hailuo leads for image-to-anime consistency".
  - "Seedance 2.0 cel-shading held across the clip".
  - "line-boil and colour crawl are the failure modes for flat 2D".

  Possible sources are anime-generator roundups on PixVerse, Luma and OpenArt blogs and Seedance review sites, all vendor-adjacent. Treat these claims as hypotheses to test.

---

## Q6. Keeping the same character consistent across idle, walk, run, attack, hit and death

### Takeaway
- **Most reliable technique:** start every animation from an exact first frame drawn from the same master concept. Generate pose-transition first frames with the image model for non-idle actions.
- **Reference-image features only give approximate likeness**, and on Veo and Omni they cannot be combined with an exact first/last frame:
  - Veo 3.1: 3 assets.
  - Omni: `IMAGE_REF_N`.
  - Kling O3: up to 3 refs plus Elements.
  - Seedance 2.0: 9 images, 3 videos, 3 audio.
- **Seeds are weak or absent.** Chaining by extension or last→first works for continuity, but drift accumulates.

### Cited Findings
- **Exact-first-frame method:**
  - Generate a clean first pose (or a small "transition pose away from idle" for non-idle actions) with an image model (GPT Image 2 or Nano Banana 2).
  - Use it as Kling's first frame.
  - Join animations with image-model "bridge frames".

  — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)
- The sprite skill advises reusing "the same source image and prompt structure". Character consistency still "varies". — [TamerinTECH GitHub](https://github.com/TamerinTECH/claude-skill-klingai-animation)
- **Veo 3.1:** reference images are "up to three asset images of a single person, character, or product". They require 8 s and cannot be combined with `image` or `lastFrame`. — [Veo docs](https://ai.google.dev/gemini-api/docs/veo); [Cloud REST via search summary](https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/rest/Shared.Types/VideoGenerationModelInstance)
- **Flow "Ingredients to Video":** a guide recommends a 3-view character sheet (portrait, profile, full body) as the three ingredients. Google's Flow page lists Ingredients under the Ultra tier. — [Atlas Cloud Veo 3.1 guide](https://www.atlascloud.ai/blog/guides/google-veo-3-1-guide-master-image-to-video-ai-with-native-sound-and-4k-realism) (reseller); [Google Flow](https://labs.google/flow/about)
- **Omni:**
  - `<IMAGE_REF_N>` references; video references of up to 3 clips × 3 s, which "work best with likenesses".
  - Conversational editing via `previous_interaction_id`; "Keep everything else the same" helps preserve unchanged elements.
  - Scene extension analyzes up to 10 s of prior context.

  — [Omni docs](https://ai.google.dev/gemini-api/docs/omni); [Google blog](https://blog.google/innovation-and-ai/technology/developers-tools/build-with-gemini-omni-1-1-flash/)
- **Kling O3:** up to 3 reference images plus start/end frames. Use "Element Reference tags to lock character faces and clothing across every cut". — [Hedra O3](https://www.hedra.com/models/video/kling/o3-standard)
- **Kling 3.0 (non-Omni):** takes no reference images, so recurring characters "have to come in through the start image or be described in the prompt". — [Krea guide](https://www.krea.ai/blog/kling-3-0-api-access-guide-pricing-code-examples-for-multi-shot-ai-video)
- **Seedance 2.0:** 9 image, 3 video and 3 audio reference slots, cited as `@Image1` / `@Video2`. "The model only applies a slot where the prompt points at it." — [ComfyUI Seedance node](https://comfy.icu/node/ModelArk-Seedance-2-0) (community)
- **Seeds and extension:**
  - Seed is documented only for Veo 3 ("slightly improves" determinism) and Seedance 2.5 draft mode.
  - Veo 3.1 extension adds 7 s per step, up to 148 s, at 720p only.
  - Luma supports extend, reverse-extend and interpolate between two generations.

  — [Veo docs](https://ai.google.dev/gemini-api/docs/veo); [Runway models](https://docs.dev.runwayml.com/guides/models/); [Luma docs](https://docs.lumalabs.ai/docs/video-generation)
- **Custom character model:** Scenario suggests training one on 5–15 reference images (30–60 min) so all generations inherit proportions and style. — [Scenario blog](https://www.scenario.com/blog/ai-sprite-generator)
- **Batching risk:** an itch.io dev animated about 8 characters together in one Veo 3 video to save time; 2 of the 8 came out wrong. — [itch.io thread, 15 Sep 2025](https://itch.io/post/14144159/view-in-topic)

### Inferences
Recommended consistency protocol (synthesized):
1. Lock one **master concept** (GPT image) on a flat key colour at fixed scale and canvas.
2. Use the image model to make **one start pose per animation** (idle, walk contact, run contact, attack anticipation, hit, death start), referencing the master. Keep scale and foot position identical.
3. Feed each start pose as the **exact first frame**. Use a last frame only where you need a specific end pose (attack recovery to idle, death to lying pose).
4. Reuse one prompt skeleton across all animations.
5. Reject any clip where frame 0 drifts from the input.

Chaining with last-frame-of-A → first-frame-of-B is good for transitions such as idle→attack. For cycles it accumulates drift, so re-anchor every animation on the master-derived pose instead.

### Gaps
- No quantitative test of cross-clip identity drift for illustrated characters on any model.
- Whether Kling O3 Elements or Seedance references can be combined with an exact start frame on the same request is only implied by reseller pages.

---

## Q7. Prompt templates and model-specific quirks for sprites

### Takeaway
Prompts that worked share the same parts:
- Short and literal.
- Camera instruction first, phrased positively ("locked-off tripod, fixed frame").
- Flat chroma background stated explicitly (#00FF00).
- "In place / no travel / same facing".
- Motion described as body mechanics with timing.
- An explicit return-to-start-pose for loops.

Model quirks:
- Kling has a negative-prompt field (200 chars), but sprite practitioners put everything in the main prompt.
- Omni has no negative-prompt parameter; write "Do not…" in the prompt.
- Veo and Omni need "single continuous shot, no cuts".
- Avoid "isometric / top-down 3/4" with Kling unless the art really is diagonal.

### Cited Findings

**First-frame preparation**
- Exact chroma green `#00FF00` with a perfectly flat background, and the character must not use that green. Full body visible; nothing in the outer 20–30% of the canvas; character about 40–50% of canvas height, because "video models often animate wider than the first pose suggests". — [LayrKits](https://www.layrkits.com/guides/sprite-sheet)

**Kling prompt rules**
- Kling has one prompt field, so put motion, preservation, camera, background and "avoid" rules in it; don't rely on a separate negative prompt.
- Core instructions:
  - Use the image as the exact first frame.
  - Camera locked.
  - Character centred and same size.
  - Facing direction fixed.
  - `#00FF00` background unchanged.
- Describe actions as anticipation → action → follow-through → recovery, not "fast overhead sword slash".
- Keep prompts short: long "direction-lock prompts can give Kling more ideas to reinterpret, causing travel, rotation, or redesign".
- Avoid "top-down 3/4" or "isometric" unless the first frame is truly diagonal.
- For jumps and landings, animate the body only and add dust or wind as separate overlays.

  — [LayrKits](https://www.layrkits.com/guides/sprite-sheet)
- Example from the LayrKits X article: a front-facing locked camera with motion limited to "a simple two-step pose cycle: the feet alternate a few pixels, the knees bend slightly". — [LayrKits on X](https://x.com/LayrKits/article/2050277473116619240) (paywalled; quoted via search summary)

**Sprite skill tips**
- Specify a solid green background, "no camera movement", 2–3 s clips, specific motion, and ask for the animation "to return to its starting pose".
- MiniMax prompts use "static shot, locked camera".
- Extraction at 12 fps (or 8 fps); aspect ratio 1:1.

  — [TamerinTECH GitHub](https://github.com/TamerinTECH/claude-skill-klingai-animation)

**Veo 3 prompt that worked for an itch.io dev**
- "walking animation loop for this characters, don't change characters expression, loop in the same position, loop every 3 seconds, smooth animation". Frames were taken from a 2–3 s segment. — [itch.io thread](https://itch.io/post/14144159/view-in-topic)

**Kling official pixel-art demo**
- "The paper lanterns flicker and glow warmly, the little fox character idly bobs and its tail sways gently … subtle looping ambient idle animation, everything stays in crisp clean pixel-art style." — [Kling pixel-art page](https://kling.ai/topics/animate-pixel-art-ai)

**Scenario example motion prompts**
- "character running", "character attacking", "character idle with subtle breathing motion". — [Scenario](https://www.scenario.com/blog/ai-sprite-generator)

**Veo camera locking (third-party prompting blogs)**
- Put the camera first, as one sentence, e.g., "Locked-off tripod shot, no camera movement."
- Avoid conflicting camera terms.
- Prefer positive constraints ("tripod-stable, fixed frame") over vague negatives.
- Remove verbs that imply travel ("walks toward", "turns around"), which pull the camera along.
- Reroll, because camera behaviour varies between generations.

  — [Veo3Gen shot-first guide](https://www.veo3gen.app/blog/veo-31-shot-first-prompting-a-10-minute-method-to-fix-stiff-motion-random-moves-); [EachLabs: common Veo 3 prompt mistakes](https://www.eachlabs.ai/blog/common-mistakes-in-veo-3-prompts-and-how-to-fix-them) (secondary)

**Omni official prompting rules**
- The default output may contain multiple shots; use "In a single continuous shot" and "No scene cuts".
- Timing can be written in natural language or timecodes, e.g., "[0-3s] A person is walking".
- There is no negative-prompt parameter; write "Do not do X" or "No dialogue".
- For a loop, use "Use this image as the first frame and the last frame."

  — [Gemini API Omni docs](https://ai.google.dev/gemini-api/docs/omni)
- Runware's Omni frame-mode example: "Smooth continuous transformation, no camera movement." Audio is controlled in the prompt, e.g., "no music, no dialogue". — [Runware Omni 1.1](https://runware.ai/docs/models/google-gemini-omni-flash-1-1/guides/first-and-last-frame)

**Kling API parameters**
- `negative_prompt` (≤200 chars) and `cfg_scale` (0–1, higher = closer prompt adherence) are available. — [CometAPI Kling docs](https://apidoc.cometapi.com/api/video/kling/image-to-video.md)

**Frame-rate targets**
- Retro pixel art reads best at 8–12 fps; smooth modern 2D at 12–24 fps. Walk cycles typically use 6–8 frames. — [dev.to SpriteFlow article](https://dev.to/alvy/from-text-prompt-to-sprite-sheet-generating-game-ready-2d-character-animations-with-ai-3g7a) (vendor author)

### Inferences
Synthesized templates, built from the sourced rules above. They are not quoted from any single source; adapt per model.

**A. Side-view walk cycle (HD illustrated; Veo / Omni / Kling)**
```
Locked-off tripod camera, fixed frame, no zoom, no pan, no camera movement, single continuous shot, no cuts.
Use the input image as the exact first frame. 2D side-view game sprite of the same character, facing right the whole time, same size, centered.
The character walks IN PLACE (treadmill walk, no forward travel): contact pose → passing pose → opposite contact → passing, one full stride cycle every 1 second, arms swinging opposite to legs, slight head bob.
Keep the flat 2D illustrated style, same line art and flat colors, no new shading, no lighting changes, no motion blur.
Background stays solid flat #00FF00 green, unchanged. End on the same pose as the first frame. No sound, no music, no dialogue.
```
- Kling: drop most of the style sentence, keep it short, and add `negative_prompt`, e.g., "camera movement, zoom, walking forward, turning, background change, 3D shading, motion blur, extra characters" (≤200 chars).
- Omni: replace "End on the same pose" with first == last tags, and add timecodes such as "[0-1s] stride 1, [1-2s] stride 2…".

**B. Idle loop (all models; best candidate for first == last)**
```
Locked camera, fixed frame, single continuous shot. Same character, same position, same facing. Subtle idle: gentle breathing (chest rises and falls), slight bob, cape/hair sways a little, blink once. Feet stay planted. Flat 2D style unchanged. Solid flat #00FF00 background. Return exactly to the starting pose at the end.
```
- Omni: add "Use this image as the first frame and the last frame."
- Luma: set `loop: true`.

**C. One-shot action (attack, hit, death; first frame = anticipation pose, optional last frame = recovery or final pose)**
```
Locked camera, fixed frame, no cuts. Same character, stays in place, facing right. [0-0.4s] anticipation: crouch and pull the sword back; [0.4-0.7s] fast horizontal slash forward; [0.7-1.5s] follow-through then recover to the starting stance. No camera shake, no impact flash, no particles, no background change. Solid flat #00FF00 background.
```
- Add effects (slash trails, dust) as separate overlays, per LayrKits.

**D. Top-down RPG**
- Avoid "top-down/isometric" wording with Kling (LayrKits).
- Describe the facing literally, e.g., "character seen from above-front, facing down toward the viewer, walking in place".
- Generate one direction per clip from a direction-specific first frame.

### Gaps
- No verified, published negative-prompt list for sprites on Veo. The current Gemini API Veo 3.1 page does not document `negativePrompt`.
- No primary source confirming Veo responds better to "static camera" than to "locked-off tripod". Both phrasings come from third-party blogs.

---

## Q8. Known failure modes for sprite use (and mitigations)

### Takeaway
The recurring problems:
- Camera drift and zoom.
- The character travelling, rotating or leaving frame.
- Near-static clips when the last frame equals the first.
- Background not perfectly flat.
- Pixel edges blurring on fast motion.
- Multi-shot cuts (Omni default).
- Frame-0 re-rendering (LTX).
- Silently ignored end frames.
- Unwanted audio. Audio is always on in Veo via the Gemini API, which has no off switch there; silent SKUs exist on Vertex and Runway.

### Cited Findings
- **Failure → fix table (Kling-based sprite pipeline):**

| Failure | Fix |
|---|---|
| Drift or rotation | Simplify the prompt, lock the camera, forbid turning and travel |
| Weapon or limb leaves the frame | Add margin around the first pose |
| Still video | Remove the final-frame input |
| Ending doesn't connect to idle | Generate bridge frames |
| Animation looks stuck | Drop near-duplicate end frames |
| Background not clean | Flatten border-connected pixels to exact green |

  — [LayrKits](https://www.layrkits.com/guides/sprite-sheet)
- "Cinematic models fight the static-camera requirement"; background removal depends on green saturation. — [TamerinTECH GitHub](https://github.com/TamerinTECH/claude-skill-klingai-animation)
- Pixel edges blur with big or fast motion. — [Kling pixel-art page](https://kling.ai/topics/animate-pixel-art-ai)
- Omni may default to multiple shots, so prompt "No scene cuts". — [Omni docs](https://ai.google.dev/gemini-api/docs/omni)
- **Veo audio:**
  - Gemini API pricing is "video with audio (default)" only.
  - A Vertex user's `generate_audio=False` was rejected ("not supported in Gemini API"), Jan 2026.
  - Another user (Sep 2026) found `generateAudio` rejected on `veo-3.1-generate-preview` / `lite`, yet got a silent 1080p video by omitting the field.
  - No official Google answer in the thread.

  — [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing); [Google AI forum](https://discuss.ai.google.dev/t/veo-3-api-generate-audio-parameter-not-supported-last-frame-limitations/119206)
- Runway sells Veo 3.1 with a no-audio option at half price ($0.20 vs $0.40 per s). — [Runway API pricing](https://docs.dev.runwayml.com/guides/pricing/)
- "Audio errors can block generation. You are not charged for blocked videos." Generated videos are stored for 2 days. Latency ranges from about 11 s to 6 min. — [Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- Frame-0 drift and re-rendering on some models (LTX-2.5-fast). End frames silently ignored on first-frame-only endpoints. Duration floors inflate the cost of short clips. — [mer.vin](https://mer.vin/2026/09/which-ai-video-models-actually-take-a-first-and-last-frame/)
- Veo hallucinated a different scene in one test (prompt-adherence inconsistency). — [Elser](https://www.elser.ai/blog/kling-ai-vs-veo-2026) (via search summary)
- An Adobe Firefly user reported an error when using two identical reference frames with Veo 3.1 Fast. — [Adobe community](https://community.adobe.com/bug-reports-403/generic-error-when-using-two-reference-frames-for-video-looping-in-veo-3-1-fast-1553443)

### Inferences
- For sprites, audio is simply discarded. On the Gemini API it still costs money and can block a generation. Either accept it, or route Veo through Vertex or Runway's silent SKU. Always add "No sound, no music, no dialogue" to the prompt.
- Build an automatic reject check into the pipeline:
  - Frame-0 vs input difference (catches re-rendering).
  - Character-bbox centroid drift and scale change across frames (catches camera zoom and travel).
  - Background colour variance (catches background change).

  These map directly onto the failure modes above. Implementation belongs to the post-processing note.

### Gaps
- No quantitative per-model rate of camera drift or limb morphing on sprite-style inputs.
- Whether Veo's "frame interpolation smear" (motion blur on fast limbs) can be prompted away was not tested in any source found.

---

## Q9. Evidence of people using these models end-to-end for game sprite sheets

### Takeaway
There are real but small-scale workflows and tools, mostly built on **Kling**, with some on Veo and Seedance:
- LayrKits guide.
- An MIT-licensed Claude Code skill (Kling v3).
- Scenario's "Convert to Video" (Seedance 2.0 / Veo 3.1).
- An itch.io dev using Veo 3.
- Video→sprite tools such as DoSprite and MP4toSprite.

All of them describe heavy manual selection and cleanup. None documents a polished commercial game shipped this way.

### Cited Findings
- **LayrKits:** a full pipeline (image model → Kling → FFmpeg → chroma key → 256×256 cells → validation report). It treats video as "controlled source footage for a sprite pipeline, not cinematic video". Image models had failed at leg mechanics and grid layouts, which is why the author moved to video. — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)
- **TamerinTECH `claude-skill-klingai-animation` (MIT, 2026):**
  - Image → Kling video (2–5 s) → ffmpeg extraction at 12 or 8 fps → chroma key → PNG sheet plus JSON/CSS.
  - Kling direct supports only `kling-v3`.
  - Higgsfield routes to `kling2_6`, `minimax_hailuo`, Seedance 2.0, Veo 3.1 and Wan 2.7.
  - Claimed sprite sizes are about 50–150 KB.

  — [GitHub](https://github.com/TamerinTECH/claude-skill-klingai-animation)
- **Scenario:** the in-product "Convert to Video" path uses Seedance 2.0 or Veo 3.1, followed by manual frame picking and grid assembly. — [Scenario blog, 27 Apr 2026](https://www.scenario.com/blog/ai-sprite-generator)
- **itch.io dev (Sep 2025):** Gemini image → Veo 3 → frames from 2–3 s → background removal. Found it "hard and time-consuming" and was building helper web apps in Google AI Studio. — [itch.io thread](https://itch.io/post/14144159/view-in-topic)
- **DoSprite:** free browser video→sprite tool with chroma key, auto-centring and 64/128/256 px output; names Grok, Luma and Kling as motion sources. — [DoSprite](https://agemar.itch.io/dosprite)
- **MP4toSprite:** built because video-first generation "solved the motion continuity problem" but left frame-by-frame background and semi-transparency work. — [MP4toSprite](https://yewlark.itch.io/mp4tosprite) (via search summary)
- **Kling marketing page:** Kling markets pixel-art and sprite animation directly. — [Kling pixel-art topic page](https://kling.ai/topics/animate-pixel-art-ai)

### Inferences
- Evidence on what works for the "motion engine" step converges:
  - Exact first frame on flat green.
  - Locked camera.
  - Short clips (2–5 s).
  - Extract at 8–12 fps and hand-pick frames.
- Model choice is mostly a matter of camera obedience and style retention on *your* art. Run a small bake-off before committing:
  - Veo 3.1 Fast, Gemini Omni 1.1 Flash, Kling 3.0 Pro (no audio), MiniMax H3 and Seedance 2.x.
  - About 5 clips per model on the same idle and walk prompt.
  - Cost is roughly $10–$30 at the prices above.

### Gaps
- No devlog or postmortem from a shipped game whose final sprites came from I2V output.
- YouTube tutorials could not be retrieved or verified through the available tools.
- Reddit threads (r/aigamedev, r/gamedev, r/PixelArt, r/StableDiffusion) were not reachable through search, so community sentiment is under-represented here.
