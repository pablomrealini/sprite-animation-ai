# Image-to-video models for 2D game character animation and seamless loops (state as of 15 Oct 2026)

Scope note: the research covers the model landscape, how to close loops, how to prompt for footage you can cut into sprites, whether 2D style survives, and how to keep one character consistent across clips. Prices are USD per second of output unless stated. Most per-second figures come from official pricing pages (Google, Runway API, Together AI) or from aggregator roundups dated Aug–Oct 2026. Aggregator figures are labelled as such. Where sources disagree, both are given. The model market changed a lot in 2026 (Sora shut down, Gemini Omni Flash, Kling 3.0 and a 4.0 preview, Seedance 2.5, Wan 3.0 closed, MiniMax H3 open-weighted), so anything older than about Q2 2026 is flagged.

## 1. Which image-to-video models are current and relevant (Oct 2026), and their specs, prices and terms

### Takeaway
As of mid-October 2026 the realistic shortlist has these features: image-to-video plus first+last-frame conditioning, API access, and per-second pricing:
- Google Veo 3.1, including Fast and Lite. Google's own docs now position Gemini Omni Flash as the default video model and Veo 3.1 as the choice for "last-frame control".
- Kling 3.0 / O3. Kling 4.0 is in limited preview.
- MiniMax H3. It has open weights since 3 Aug 2026.
- Seedance 2.0 / 2.5.
- Wan 3.0, which is closed. Wan 2.2 remains the open-weights option.
- Luma Ray 3.2, the only one with an explicit seamless-loop feature in i2v.
- Runway Gen-4.5. Its API docs currently show a single prompt image, with no confirmed last frame.

OpenAI Sora 2 is gone: the API was shut down on 24 Sep 2026. Veo 3.1's own constraints matter for sprites: 24 fps, only 16:9 or 9:16 (no square), 4/6/8 s clips, and 1080p/4K/reference images only at 8 s.

### Cited Findings

**Google Veo (Gemini API / AI Studio / Vertex / Flow)**
- Model IDs in the Gemini API are `veo-3.1-generate-preview` and `veo-3.1-fast-generate-preview`, both Preview since Jan 2026, and `veo-3.1-lite-generate-preview`, Preview since Mar 2026. Veo 3 and Veo 3 Fast are marked Deprecated. — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- All Veo models output at 24 fps with native audio, one video per request. — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- Veo 3.1 and 3.1 Fast resolutions are 720p (default), 1080p and 4K. Lite offers 720p and 1080p, with no 4K. Durations are 4, 6 or 8 s. Aspect ratios are 16:9 (default) or 9:16 only. — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- 1080p and 4K require an 8 s duration. Reference images require 8 s. Video extension is limited to 720p and 8 s. — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- First and last frame (interpolation): set `image` as the first frame and `lastFrame` in the config. `lastFrame` must be paired with `image`. The docs describe the feature as Veo 3.1-only. — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- Reference images ("ingredients"): up to 3 images with `referenceType: "asset"`, to preserve a single character, person or product. Supported on Veo 3.1 and 3.1 Fast, not on Lite. Requires 8 s. — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- Extension adds 7 s per step, up to 20 times, for at most 148 s total. The input must be a Veo-generated 720p video. — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- Latency ranges from 11 s to about 6 min at peak. Outputs are stored for only 2 days. SynthID watermark. A seed parameter is listed for Veo 3 but not for Veo 3.1. — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- Gemini API paid-tier prices (default "video with audio") per resolution: Veo 3.1 costs $0.40 at 720p and 1080p, and $0.60 at 4K. Veo 3.1 Fast costs $0.10 at 720p, $0.12 at 1080p and $0.30 at 4K. Veo 3.1 Lite costs $0.05 at 720p and $0.08 at 1080p. No free tier for Veo. You are charged only for successful generations. — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- The Gemini API pricing page lists no video-only (audio off) price. Runway's API resells Veo 3.1 at $0.40/s with audio or $0.20/s without, and Veo 3.1 Fast at $0.15/s with audio or $0.10/s without. — [Runway API pricing](https://docs.dev.runwayml.com/guides/pricing/)
- An aggregator quotes Vertex video-only at $0.20/s for Standard, $0.08–$0.10 for Fast, and $0.03–$0.05 for Lite. — [Atlas Cloud](https://www.atlascloud.ai/blog/tips/veo-3.1-api-pricing). Another aggregator claims $0.40 is video-only. — [apiframe](https://apiframe.ai/guides/veo-3-api-guide) (unresolved conflict; check the Vertex pricing page)
- Google's video landing page now recommends **Gemini Omni Flash** as the default video model, and says to use Veo 3.1 "for scene extension, last-frame control, or legacy pipelines". — [Gemini API video overview](https://ai.google.dev/gemini-api/docs/video)

**Google Gemini Omni Flash (new, 2026)**
- The model ID is `gemini-omni-1.1-flash`. Resolutions are 360p, 720p (default), 1080p (upscaled) and 4K (upscaled), at 16:9 or 9:16. It supports image-to-video, first/last frame (two images plus a described transition), subject references with multiple images, and multi-turn editing via `previous_interaction_id`. Extensions add 3–10 s each, up to 40 s total. — [Gemini API Omni docs](https://ai.google.dev/gemini-api/docs/omni)
- It launched in preview around 1 Jul 2026. It is billed by tokens: $17.50 per 1M video-output tokens at 5,792 tokens/s of 720p, which works out to about $0.10/s. — [eesel.ai](https://www.eesel.ai/blog/gemini-omni-flash-pricing); [aiweekly](https://aiweekly.co/alerts/google-launches-gemini-omni-flash-and-nano-banana-2-lite)
- Runway API resale prices for `gemini_omni_flash_1.1`: $0.034/s at 360p, $0.10 at 720p, $0.15 at 1080p and $0.30 at 4K, plus $0.01 per reference image. — [Runway API pricing](https://docs.dev.runwayml.com/guides/pricing/)

**Kling (Kuaishou)**
- Kling 3.0 (Video 3.0 and Video 3.0 Omni) launched on 5 Feb 2026, and a 4K mode was added on 27 Apr 2026. — [the-decoder](https://the-decoder.com/chinese-ai-video-model-kling-3-0-takes-another-step-toward-usable-creative-assets/); [Eagle-Tribune](https://www.eagletribune.com/region/kling-ai-launches-3-0-model-ushering-in-an-era-where-everyone-can-be-a/article_45569e75-7d6b-5d33-b1f3-11a782ea3551.html)
- Clips run 3–15 s at up to 1080p, plus a 4K tier. Multi-shot. "Elements" extract a character's traits from images or a 3–8 s video. — [fal Kling 3](https://fal.ai/kling-3); [Runway model catalog](https://docs.dev.runwayml.com/guides/models/)
- Kling 3.0 (Standard, Pro, 4K) i2v accepts a first frame alone or first+last frames. Kling O3 accepts first/last keyframes plus up to 7 reference images in total, keyframes included. Kling 2.5 Turbo Pro also accepts first+last. — [Runway API inputs](https://docs.dev.runwayml.com/assets/inputs/)
- Runway API prices: Kling 3.0 Standard at 720p costs $0.09/s without audio or $0.13 with. Pro at 1080p costs $0.12 or $0.17. 4K costs $0.43. O3 costs $0.13 (Standard), $0.17 (Pro) and $0.43 (4K). Kling 2.5 Turbo Pro costs $0.12. — [Runway API pricing](https://docs.dev.runwayml.com/guides/pricing/)
- fal prices for Kling 3.0 Pro i2v: $0.112/s without audio, $0.168/s with audio. — [fal i2v explore](https://fal.ai/explore/image-to-video-apis)
- On the official Kling API, Kling 3.0 Turbo costs ¥0.8/s (about $0.11) at 720p. — [invideo (Aug 2026)](https://invideo.io/blog/ai-video-model-pricing)
- **Kling 4.0** was announced on 30 Sep 2026, with limited early access from 28 Sep and a full launch "scheduled for October 2026". Third-party summaries of the spec sheet list 3–30 s clips, up to 10 keyframes and 4K. A "4.0 Flash" build (20 s, 720p) is reportedly already available. No official confirmation was found that the full release has shipped. — [Atlas Cloud](https://www.atlascloud.ai/es/blog/tips/kling-4-flash-vs-full); [EachLabs](https://www.eachlabs.ai/blog/kling-4-0-is-coming-what-we-know); [gradually.ai](https://www.gradually.ai/en/ai-models/kling-4-0/)
- Terms: the free tier is watermarked and not licensed for commercial use. Paid tiers remove the watermark and allow commercial use. Clips made on the free tier reportedly don't become commercial-eligible after upgrading. These are secondary sources; the official ToS was not read. — [Segmind](https://blog.segmind.com/kling-ai-pricing-complete-breakdown-and-comparison/); [Atlas Cloud](https://www.atlascloud.ai/blog/guides/kling-ai-pricing); [marcandrews](https://marcandrews.com/?p=6319)

**Runway**
- Gen-4.5 (`gen4.5`) costs $0.12/s (12 credits at $0.01) with a 2 s minimum. It does t2v and i2v, 2–10 s. i2v ratios include square 960:960. — [Runway API pricing](https://docs.dev.runwayml.com/guides/pricing/); [Runway API getting started](https://docs.dev.runwayml.com/guides/using-the-api/)
- Gen-4 Turbo costs $0.05/s and is i2v only. Aleph 2.0 costs $0.28/s and does video-to-video editing "with keyframe-guided control". — [Runway model catalog](https://docs.dev.runwayml.com/guides/models/)
- For Gen-4.5 and Gen-4 Turbo, the API inputs page lists only a single "Prompt image", with no first/last frame mode. — [Runway API inputs](https://docs.dev.runwayml.com/assets/inputs/)
- The help centre says Gen-4.5 currently offers t2v and i2v, "with support for additional inputs coming soon". Keyframes are handled in a separate "Keyframes" app. — [Runway Help: Gen-4.5](https://help.runwayml.com/hc/en-us/articles/46974685288467-Creating-with-Gen-4-5)
- The API's `promptImage` can be an array with `position: "first"|"last"`, but that is documented for API version 2024-11-06 generally, not confirmed for gen4.5. — [Runway API version 2024-11-06](https://docs.dev.runwayml.com/api-details/versions/2024-11-06/)
- **PNG-sequence output** is available for Gen-4.5 and Aleph 2.0 for +5 credits/s ($0.05/s). That is directly useful for sprite extraction. — [Runway API pricing](https://docs.dev.runwayml.com/guides/pricing/)
- The Runway API is now also an aggregator. It resells Veo 3.1, Kling 3.0/O3, Seedance 2.0/2.5, MiniMax H3, WAN 3.0, Grok Imagine 1.5, HappyHorse 1.0 and Gemini Omni Flash under one key. — [Runway model catalog](https://docs.dev.runwayml.com/guides/models/)

**Luma**
- The legacy Luma API (`ray-2`, `ray-flash-2`) has a **`loop` boolean**, plus `keyframes.frame0` (start image) and `keyframes.frame1` (end image). Resolutions are 540p, 720p, 1080p and 4K, with 5 s in the examples. The page says newer docs live at docs.agents.lumalabs.ai. — [Luma API docs](https://docs.lumalabs.ai/docs/video-generation)
- **Ray 3.2**: 1080p in every mode, 10 s i2v, up to 16 keyframes per clip, and "seamless looping" listed for both t2v and i2v. Native 16-bit HDR and EXR export. Reference images in t2v. — [fal Ray 3.2](https://fal.ai/ray-3.2)
- Ray 3.2 is the first Ray model offered through an API. — [AlphaSignal](https://alphasignal.ai/news/luma-opens-ray3-2-api-so-developers-build-hollywood-grade-video-into-any-product)
- The ComfyUI Ray 3.2 keyframe nodes accept 2–64 keyframes and map 5 s to 120 frames and 10 s to 240 frames, which implies 24 fps. These docs are AI-generated, and their count conflicts with the "16 keyframes" figure above. — [ComfyUI docs](https://docs.comfy.org/built-in-nodes/LumaRay32KeyframesToVideoNode)

**OpenAI Sora 2: discontinued**
- The Sora 2 API (Videos API, `sora-2`, `sora-2-pro` and the dated aliases) was removed on 24 Sep 2026. OpenAI announced this on 24 Mar 2026 and named no replacement. The Sora consumer apps were discontinued on 26 Apr 2026. — [TechJack Solutions](https://techjacksolutions.com/ai-brief/openai-videos-api-sora-2-deprecated-september-2026/); [laozhang blog](https://blog.laozhang.ai/en/posts/sora-2-api-discontinued); [invideo](https://invideo.io/blog/ai-video-model-pricing)

**MiniMax Hailuo / H3**
- MiniMax-H3 launched on 31 Jul 2026 (API plus the Hailuo app), priced at $0.13/s at 2K with native stereo audio. Failed generations aren't billed. The first 5 reference images are free and further images cost $0.04 each. — [invideo](https://invideo.io/blog/ai-video-model-pricing)
- H3 was open-sourced on 3 Aug 2026 under the "MiniMax H3 Community License". — [ComfyUI wiki](https://comfyui-wiki.com/en/models/minimax/minimax-h3)
- It outputs up to 2K at 24 fps, about 15 s. — [ComfyUI docs](https://docs.comfy.org/tutorials/video/minimax/minimax-h3)
- An FL2VA checkpoint does t2v (no image), first- or last-frame (one image), or first+last-frame (two images). — [Vast.ai](https://vast.ai/model/minimax-h3)
- Self-hosting needs a 33B-parameter model, more than 70 GB of checkpoints and 48 GB+ VRAM. — [Atlas Cloud H3 sprite guide (20 Aug 2026)](https://www.atlascloud.ai/blog/tips/minimax-h3-game-sprites-atlas-guide)
- Runway API prices: `hailuo3` costs $0.10/s at 768p or $0.15 at 2K, plus $0.02 per reference image or keyframe. `h3_max` costs $0.05/s at 480p or $0.08 at 768p and accepts first and last frames. In H3, keyframe mode and unpositioned-reference mode cannot be mixed. — [Runway API pricing](https://docs.dev.runwayml.com/guides/pricing/); [Runway API inputs](https://docs.dev.runwayml.com/assets/inputs/)
- Older Hailuo models (pre-H3) are priced per video: $0.28 for 6 s at 768p, $0.49 for 6 s at 1080p. — [invideo](https://invideo.io/blog/ai-video-model-pricing)

**ByteDance Seedance**
- Seedance 2.0 launched on 12 Feb 2026 (Doubao/Jimeng). One source says ByteDance suspended the overseas API on 15 Mar 2026. — [Sorceress (verified 1 Jun 2026)](https://sorceress.games/blog/tune-the-best-ai-animation-generator-honest-2026-test). That is **contradicted** by current listings of Seedance 2.0 and 2.5 on Together AI and the Runway API. — [Together AI](https://docs.together.ai/docs/seedance2.0-quickstart); [Runway model catalog](https://docs.dev.runwayml.com/guides/models/)
- **Seedance 2.5** on Together AI: 480p/720p only, 4–30 s, audio always on. Up to 30 reference images and 10 reference videos. `frame_images` takes up to 2 (first/last), and **frame images cannot be combined with reference inputs**. Price: $0.115/s at 480p, from $0.249/s at 720p. — [Together AI](https://docs.together.ai/docs/seedance2.0-quickstart)
- Runway's catalog lists Seedance 2.5 at 480p/720p/1080p, priced at $0.20, $0.30 and $0.68 per second, plus a surcharge per second of input video. This conflicts with Together's 720p cap. — [Runway API pricing](https://docs.dev.runwayml.com/guides/pricing/)
- Seedance 2.0 supports 1080p and 4K and has an audio on/off toggle. — [Together AI](https://docs.together.ai/docs/seedance2.0-quickstart)
- Seedance 2.0 on the Runway API costs $0.36/s at 480p/720p, $0.40 at 1080p and $1.50 at 4K. Fast costs $0.29 and Mini $0.16. The Seedance i2v modes take "Prompt image (first/last/reference)". — [Runway API pricing](https://docs.dev.runwayml.com/guides/pricing/); [Runway API inputs](https://docs.dev.runwayml.com/assets/inputs/)

**Alibaba Wan (open and closed)**
- The Wan-Video GitHub org lists Wan2.1 and Wan2.2 (Apache-2.0), plus Wan-Animate-2 (updated Aug 2026) and Wan-Dancer. It has no repo for 2.5, 2.6, 2.7 or 3.0. — [GitHub Wan-Video](https://github.com/Wan-Video)
- Wan 2.2 (Apache 2.0) is the last open-weights flagship. **Wan 3.0 is closed**. It was released as a public beta on about 6 Aug 2026; one source says the broad release was 24 Aug. It produces up to 30 s at up to 1080p and costs $0.05/s at 480p, $0.10 at 720p and $0.20 at 1080p. — [Morphic](https://morphic.com/de/resources/models/wan-3-0); [eWeek](https://eweek.com/news/alibaba-wan3-ai-video-documents-apac-china/); [DataNorth](https://datanorth.ai/news/alibaba-launches-wan3-0-video-model)
- WAN 3.0 on the Runway API takes up to 10 image references or first/first+last keyframes, and keyframes can't be mixed with references. — [Runway API inputs](https://docs.dev.runwayml.com/assets/inputs/)
- Wan 2.6 (Dec 2025) never had published weights. — [wan27.org](https://www.wan27.org/blog/wan-2-6-open-source-guide)
- Wan 2.7's open-weights status is **disputed**. — [wan27.org](https://wan27.org/blog/wan-2-7-release-date-open-source); [localaimaster](https://localaimaster.com/blog/wan-2-7-open-source). One source calls it Apache 2.0 and self-hostable on 24 GB. — [Sorceress](https://sorceress.games/blog/tune-the-best-ai-animation-generator-honest-2026-test). The official GitHub org shows no 2.7 repo.
- Open first/last-frame options: the dedicated **Wan 2.1 FLF2V** model, or **Wan 2.2 I2V-A14B** with an end image (ComfyUI `WanFirstLastFrameToVideo`). The Wan 2.2 14B model must run its two experts (high-noise and low-noise) in a two-pass sampler. — [ComfyUI wiki FLF2V](https://comfyui-wiki.com/en/models/wan/flf2v); [Comfy.org Wan2.2 FLF2V workflow](https://www.comfy.org/es/workflows/video_wan2_2_14B_flf2v-7016f027bcf1/); [Atlas Cloud Wan FLF2V](https://www.atlascloud.ai/it/models/alibaba/wan-flf2v)

**Others (briefer)**
- **Midjourney Video (V1, June 2025, OLD):** `--loop` and `--end <image URL>` flags. — [gaga.art](https://gaga.art/blog/midjourney-video/). Extends in 4 s steps up to about 21 s. — [CometAPI](https://www.cometapi.com/how-to-create-a-video-in-midjourney-api/). The HD (720p) mode arrived in Aug 2025 at 3.2× the cost, and the default is 480p. — [Geeky Gadgets](https://www.geeky-gadgets.com/midjourney-native-hd-video-update/); [CometAPI](https://www.cometapi.com/midjourneys-hd-video-mode-goes-live/). A Nov 2025 update added loop and start/end frame to the web UI; "artistic images work better" than realistic ones. — [lilys.ai](https://lilys.ai/en/notes/ai-midjourney-20251111/midjourney-video-loop-start-end). No official 2026 "V2" video model was confirmed.
- **Pika:** Pikaframes (v2.2) on fal takes up to 5 images, can loop, and has a commercial license. — [fal blog](https://blog.fal.ai/pika-api-is-now-powered-by-fal); [modelgrep](https://modelgrep.com/media/models/fal-ai/pika/v2.2/pikaframes). A "Pika 2.5" keyframe API with 2–5 images is reported only by a secondary blog. — [seedance.tv](https://www.seedance.tv/blog/pika-multiple-keyframe-video-tutorial)
- **Grok Imagine Video 1.5 (xAI):** $0.08/s per xAI docs. — [invideo](https://invideo.io/blog/ai-video-model-pricing). On the Runway API its i2v takes a single first frame only. The 1.5 Lite variant costs from $0.02/s. — [Runway API inputs](https://docs.dev.runwayml.com/assets/inputs/); [Runway API pricing](https://docs.dev.runwayml.com/guides/pricing/)
- **HappyHorse 1.0 (Alibaba):** 3–15 s. Its i2v takes a prompt image only. $0.15/s at 720p, $0.30/s at 1080p on the Runway API. — [Runway API pricing](https://docs.dev.runwayml.com/guides/pricing/); [Runway API inputs](https://docs.dev.runwayml.com/assets/inputs/)
- **PixVerse:** V6 is priced in credits per second. — [invideo](https://invideo.io/blog/ai-video-model-pricing). Scenario used the older PixVerse v4.5 for first+last-frame attack loops. — [Scenario help](https://help.scenario.com/en/articles/create-spritesheets-with-scenario/)
- **LTX-2.3** (Lightricks): Fast costs $0.06–0.24/s and Pro $0.08–0.32/s, at 1080p–4K. — [invideo](https://invideo.io/blog/ai-video-model-pricing)

**Commercial-use terms (summary of what was found)**
- Gemini API terms: "Google won't claim ownership over that content". Google "may generate the same or similar content for others". On unpaid services (including AI Studio's free quota), Google uses submitted content and responses to improve its products. — [Gemini API Additional Terms (archived)](https://ai.google.dev/gemini-api/terms-archive/terms_10_07_25?authuser=3)
- A July 2026 rights review finds no clause that expressly grants commercial use of Veo 3.1 output, and no output-IP indemnity, on the paid Gemini Developer API. — [Vorp Labs](https://vorplabs.com/models/media-rights)
- Wan 2.1 and 2.2 weights are Apache-2.0. — [GitHub Wan-Video](https://github.com/Wan-Video)
- MiniMax H3 weights use a custom community license. — [ComfyUI wiki](https://comfyui-wiki.com/en/models/minimax/minimax-h3)

### Inferences
- For this studio's job (2D character to loopable sprite footage), the models that combine **image-to-video, first+last-frame conditioning and an API** today are: Veo 3.1 and Fast, Gemini Omni Flash, Kling 3.0/O3/2.5 Turbo, MiniMax H3 / H3 Max, Seedance 2.0/2.5, WAN 3.0, Wan 2.1/2.2 (self-hosted), Luma Ray 2 and Ray 3.2 (keyframes plus loop), Midjourney (UI only), and Pikaframes. Runway Gen-4.5, HappyHorse and Grok Imagine i2v are first-frame-only on the API as documented.
- Veo 3.1 has no square aspect ratio, so square sprite cells have to be cropped out of 16:9 or 9:16 footage. Gen-4.5 (960:960) or models with free ratios avoid wasting pixels. Veo's 8 s requirement for 1080p and for reference images also means paying for 8 s when a walk cycle needs about 1 s.
- Since audio is irrelevant here, routes that bill **video-only** are cheaper: Runway's Veo 3.1 at $0.20 vs $0.40, Kling with audio off, Seedance 2.0 with the audio toggle. The Gemini API only publishes with-audio prices, and Seedance 2.5 always bills with audio.
- Rough cost per 4 s test clip: Veo 3.1 Lite at 720p about $0.20; Veo 3.1 Fast at 720p about $0.40; Kling 3.0 Standard (no audio, Runway) about $0.36; Gen-4.5 about $0.48; Veo 3.1 Standard about $1.60. At 8 s, multiply by two. This is my own arithmetic from the cited per-second rates.
- The studio's "Veo in AI Studio" result may in future be routed to Gemini Omni Flash, because Google now recommends it as the default. Pin the model explicitly (`veo-3.1-*`) to keep results reproducible.

### Gaps
- No official Kling-side spec page was read, so Kling 3.0's fps, exact credit-to-dollar rate and the official commercial terms remain unverified. It is also unconfirmed whether Kling 4.0 is generally available as of 15 Oct 2026.
- The current official Vertex AI Veo price table (video-only vs with audio) could not be fetched; the page came back truncated.
- Luma Ray 3.2 per-clip pricing appeared only in a search snippet (about $0.30 for 5 s at 720p, $1.20 at 1080p) without a verifiable source. Luma's commercial terms were not checked.
- Runway's and Luma's output-ownership terms were not checked. No official Midjourney API exists to my knowledge, but this was not verified.
- Whether Gen-4.5 accepts `position: "last"` on the API is undocumented. Test it.
- Fps for Kling, Seedance, Wan 3.0, Omni Flash and Gen-4.5 was not found in the sources read.

## 2. How to get a perfect loop: conditioning, prompting, post-processing, failure modes

### Takeaway
There are three working strategies. (a) First-frame-only generation of a repeating motion, then an algorithmic search for the best loop window inside the clip. This is used for walk/run in the best-documented 2026 sprite pipeline. (b) First+last frame pinned to the same "ready" pose, for idle and attack. (c) Two clips, A→B then B→A, with the frames swapped. Built-in loop toggles exist only in Luma (Ray 2 `loop`, Ray 3.2 "seamless looping") and Midjourney (`--loop`). Feeding the identical image as first and last frame is a known workaround on Veo, but it can return a near-static video or an error. Crossfading is the video-editor fix, but it is a poor fit for sprite frames.

### Cited Findings
- **Iso Cycles (Scenario, 2026), a full 8-direction pixel-art hero pipeline.**
  - Walk and run were animated with Kling V3 I2V Standard from the **first frame only**. Idle and attack used **first and last frame**, with the final frame pinned to a second still that "returns to the starting ready pose".
  - The new facings were 5 s clips with the end frame pinned.
  - A local "find the loop window" step scored each candidate loop by seam size against mean frame motion, then took 8 evenly spaced frames. The search ranges were walk 12–34 frames, run 8–24, idle 24–66.
  - — [Scenario Iso Cycles](https://www.scenario.com/explorations/iso-cycles/)
- **Same image as first+last can go still.** LayrKits advises against using the same image as both first and final frame, since that can produce a still video. Instead, choose a good ending frame from the output, and if it doesn't connect to idle, generate one or a few bridge frames with an image model. If the end frames look too similar to the start, the animation reads as "stuck"; trim the redundant ones. — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)
- **Veo 3.1 same-image loop.** A guide recommends using the same still as the first and last frame and prompting for "cyclical motion that returns to the start". It also suggests a static camera and explicit constraints such as "no camera movement, no people entering or leaving, no new objects, constant lighting and exposure, no cuts, no fade, no text", and shortening the duration if the ending drifts. — [veo3ai.io loop guide](https://www.veo3ai.io/blog/veo-3-seamless-looping-video-guide-2026)
- **Trimming the seam.** A creator got a clean 8 s endless loop on Veo 3.1 Fast (in Flow) with the same image at both ends, then trimmed about 5 frames from each end. The useful range was 4–7 frames depending on the material. This is a single anecdote. — [note.com (jersey_cat)](https://note.com/jersey_cat_note/n/ne47bacdd99cc?hl=en)
- **Known failure.** Adobe Firefly users report a "generic error when using two reference frames for video looping in Veo 3.1 Fast". A community manager called the same-image approach "only a workaround". — [Adobe Community](https://community.adobe.com/bug-reports-403/generic-error-when-using-two-reference-frames-for-video-looping-in-veo-3-1-fast-1553443)
- **Attack loop by frame swap.** Generate neutral→attack with first+last frame, then a second clip with the first and last frames swapped (attack→neutral), and join them. Scenario took 16 key poses from the pair, using PixVerse v4.5 at 720p, 1:1, 5 s, "Smooth" motion mode. — [Scenario help](https://help.scenario.com/en/articles/create-spritesheets-with-scenario/)
- **Prompted three-beat attack.** A timestamped single-clip prompt: "Character wind-up stance" [0–2 s], then "Melee sword slash action" [2–4 s], then "Return to neutral stance" [4–5 s]. — [Atlas Cloud H3 sprite guide](https://www.atlascloud.ai/blog/tips/minimax-h3-game-sprites-atlas-guide)
- **Built-in loops.**
  - Luma API `loop: true|false`, alongside `keyframes.frame0` and `frame1`. — [Luma API docs](https://docs.lumalabs.ai/docs/video-generation)
  - Ray 3.2 lists "seamless looping" for i2v. — [fal Ray 3.2](https://fal.ai/ray-3.2)
  - Midjourney `--loop`. — [gaga.art](https://gaga.art/blog/midjourney-video/)
  - Pikaframes can "loop animations". — [modelgrep](https://modelgrep.com/media/models/fal-ai/pika/v2.2/pikaframes)
- **Open-model loops.** Wan FLF2V is "well suited to making loop animations". The end frame is set equal to the start frame, and the node enforces boundary conditions at t=0 and t=1 inside diffusion. — [ComfyUI wiki FLF2V](https://comfyui-wiki.com/en/models/wan/flf2v)
- **Kling vendor guidance for pixel-art loops.** Prompt continuous ambient motion that doesn't end in a very different pose. That gives a "near-seamless" loop; for a perfect one, trim or crossfade in an editor. — [Kling pixel-art topic page (11 Jul 2026)](https://kling.ai/topics/animate-pixel-art-ai)
- **Post-processing loop-point search.**
  - Pick the frame pair where the end best matches the beginning. — [CapCut guide](https://www.capcut.com/create/seamless-loop-videos-continuity-techniques); [aescripts forum (all-pairs difference idea)](https://aescripts.com/forums/discussion/2151/idea-for-a-ae-plugin-loop-helper)
  - A ComfyUI node scans the tail of a clip for the frame that best matches frame 0, trims there, and optionally crossfades. — [comfy.icu Save-Video-Eclipse](https://comfy.icu/node/Save-Video-Eclipse)
  - CLI and agent skills rank candidate cuts by distance score. They find cuts that already exist in the footage; they don't fabricate frames. — [skills.sh video-loop](https://skills.sh/coroboros/agent-skills/video-loop); [clawhub seamless-looper](https://clawhub.ai/gullish42069/seamless-looper)
- **Crossfade and ping-pong.** Typical crossfades run 0.5 s for fast motion, 1 s by default and 2 s for slow material. Skip the crossfade when first and last are already near-identical, because it only blurs the motion. A forward-reverse (ping-pong) loop avoids the jump but changes the motion's character. — [skills.sh video-loop](https://skills.sh/coroboros/agent-skills/video-loop)
- Research on seam hiding notes that methods relying on near-identical frames only work when such frames recur. — [UCL "Seam hiding for looping videos"](https://discovery-pp.ucl.ac.uk/10117777/1/Seam_hiding_for_Looping_Videos.pdf)
- **Documented failure modes.**
  - The character drifts across the frame and breaks the loop. The feet shuffle without alternating ("skating"). The design mutates between frames (palette or costume drift). — [Spriterrific](https://spriterrific.com/pixel-art-walk-cycle-generator/)
  - The character drifts or rotates. Weapons or capes leave the frame. Green on the character breaks the key. Matching first and last frames gives a still video. The loop connects poorly to idle. — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)
  - Temporal flicker, scaling drift, palette bleed, and limb distortion such as extra fingers. — [Atlas Cloud H3 sprite guide](https://www.atlascloud.ai/blog/tips/minimax-h3-game-sprites-atlas-guide)
  - Seedance 2.5 "gave a jog", so the in-place run failed. — [Scenario Iso Cycles](https://www.scenario.com/explorations/iso-cycles/)
  - A staff's glow lit up the backdrop, so the authors added "glowing halo / light spill" to the negatives. — [Scenario Iso Cycles](https://www.scenario.com/explorations/iso-cycles/)
  - Kling: "drift" is the erosion of a subject's traits across frames. Temporal inconsistency shows as jitter or flicker, warping backgrounds and pulsing textures. — [Kling blog on drift](https://kling.ai/blog/fix-ai-video-drift-consistency-guide)

### Inferences
- For **cyclic locomotion** (walk, run, idle breathing), a single long first-frame clip of a repeating motion, followed by an automatic loop-window search, is more reliable than same-image first/last pinning. That is what the Iso Cycles pipeline did. A 4–5 s clip contains several stride cycles, and one of them will close best.
- For **one-shot actions that must return to idle** (attack, hurt, cast), first+last pinning to the idle/ready pose is the right tool. If the model freezes, either pin a slightly different "recovery" still as the end, or use the two-clip swap.
- **Crossfades are a video-editor fix and a poor fit for sprite sheets.** A blended frame contains two semi-transparent poses (ghost limbs), which keys and pixelates badly. For sprites, prefer a hard cut at the best-matching frame pair. Ping-pong only suits symmetric motions such as breathing, bobbing or hovering, not walks.
- The ~4–7 frame trim seen on Veo matches the common observation that frame-pinned clips ease in and out near the pinned ends. Trimming the ease avoids a visible "hold" at the loop point. This rests on one anecdote; test it.

### Gaps
- No quantitative comparison of loop-closure quality across models was found (e.g. seam error for Veo vs Kling vs Luma loop mode).
- No official Google documentation addresses identical first/last frames or loop generation in Veo 3.1.
- Luma Ray 3.2's loop behaviour with a pixel-art or flat 2D start frame is untested in the sources found.

## 3. How to prompt for sprite-friendly footage

### Takeaway
The documented 2026 practice:
- **Start frame:** a clean full-body start frame on an exact flat key colour (#00FF00 or #FF00FF), with generous margins (character about 40–50% of canvas height, nothing in the outer 20–30%) and nothing on the character in the key colour.
- **Motion:** described mechanically and "in place, on a treadmill axis".
- **Camera:** "locked off, static orthographic view", stated positively.
- **Pose:** the same facing for the whole clip.
- **Effects:** no shadows, floor or VFX.

Then extract at 8–24 fps and keep 8–16 frames per action.

### Cited Findings
- **LayrKits template fragments:** "Use the uploaded image as the exact first frame." "Keep the character pinned to the center of the screen." "Keep the same front-facing view for the entire clip." "Locked camera."
  - Describe actions mechanically (anticipation, strike, follow-through, recovery) rather than as a vague "fast overhead sword slash".
  - For simple pixel sprites, use short literal prompts, and avoid "top-down 3/4" or "isometric" unless the first frame really is diagonal.
  - Generate body motion first and add dust or wind as separate overlays.
  - — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)
- **LayrKits start-frame spec:** exact #00FF00 background, flat, with no shadows, floor or gradients. Full body, centred, about 40–50% of canvas height for idle. Keep important pixels out of the outer 20–30% border, because video models animate wider than the first pose suggests. For non-idle actions, start from a small transition pose rather than the extreme pose. — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)
- **Atlas Cloud H3 templates:**
  - Idle: "Character performs a subtle breathing loop, chest rising and falling rhythmically, feet planted."
  - Walk/run: "Character walks forward in place on a treadmill axis, complete stride cycle."
  - Camera: "Locked off, static orthographic view, zero camera motion."
  - Source images on #00FF00 or #FF00FF at 512–768 px, 1:1.
  - Extraction rates: 12 fps for walk/run (keep 12), 8 fps for idle (keep 8), 24 fps for attack (keep 16).
  - — [Atlas Cloud H3 sprite guide](https://www.atlascloud.ai/blog/tips/minimax-h3-game-sprites-atlas-guide)
- **Iso Cycles run prompt:** "like a treadmill: the armored knight immediately starts running in place and keeps running for the whole clip."
  - Side-view prompts: the hero walks toward the right edge and the camera never sees his chest or back.
  - Every hero sits on flat magenta. Clips are cropped to one shared canvas per hero.
  - SW, W and NW are mirrors of SE, NE and E, so only five directions are generated.
  - — [Scenario Iso Cycles](https://www.scenario.com/explorations/iso-cycles/)
- **Positive phrasing:** Runway guidance (as summarized) says negative phrasing "may produce unpredictable or even opposite results". Write "Locked camera. The camera remains still." instead of "No camera movement". Name what the camera stays locked on. — [rephrase-it](https://rephrase-it.com/blog/how-to-prompt-veo-kling-runway-and-sora)
- **Spriterrific fixes:** fixed camera on a flat chroma background, explicit alternating stride poses with counter-swinging arms, and an identity anchor image. — [Spriterrific](https://spriterrific.com/pixel-art-walk-cycle-generator/)
- **Veo's own guidance:** prompts should cover subject, action, style, camera position and motion, composition, focus/lens and ambiance. Longer, more detailed prompts give more control. The text limit is 1,024 tokens. — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- **Scenario run settings:** 5 s, 1080p, 1:1, "Camera Fixed" off. The example extracted an 8-frame run cycle from contact, lift-off and mid-stride poses. — [Scenario help](https://help.scenario.com/en/articles/create-spritesheets-with-scenario/)
- **Alignment:** scale the full source canvas into each cell with the same scale and offset, with no per-frame recentring or bounding-box shifting, because that creates fake motion. — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)
- **Background removal:** rembg (RMBG-1.4) with alpha matting, 1 px alpha erosion and 2 px padding. — [Atlas Cloud H3 sprite guide](https://www.atlascloud.ai/blog/tips/minimax-h3-game-sprites-atlas-guide). Chroma-key pixels near #00FF00 and reduce green spill rather than deleting pixels "just because they contain some green". — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)
- **Transparent output research:** a method paper (10 Aug 2026) presents GameAlpha-2.4K and a generator that outputs RGB frames plus alpha mattes in one pass for game-style assets. No code or weights release was stated. — [arXiv 2608.09355](https://arxiv.org/abs/2608.09355)

### Inferences
- A practical **composite prompt** built from the cited templates (my synthesis, untested as a whole):
  > "Use the uploaded image as the exact first frame. 2D side-scrolling game sprite, side profile facing right. The character walks in place on a treadmill axis, feet alternating, arms counter-swinging, repeating stride cycle for the whole clip. The character stays pinned at the centre of the frame at the same size. Locked-off static orthographic camera; the camera remains still. Flat uniform #00FF00 background, even flat lighting, no floor, no shadow, no effects. Keep the exact palette, outlines, proportions and costume of the reference image."
- Magenta (#FF00FF) is the safer key for green-clad or nature characters. The Iso Cycles pipeline used magenta throughout.
- Choose the extraction fps per action rather than globally: about 8 for idle, about 12 for locomotion, 16–24 for attacks. That matches the Atlas guide and typical hand-made sprite frame counts (8–12 frames per cycle).
- Pinning the character centre from the prompt plus same-scale canvas cropping matters more than per-frame bounding-box fitting, which induces jitter.

### Gaps
- No official Veo, Kling or Runway prompt template specific to game sprites was found. All templates come from third-party pipelines.
- No source compares how well each model actually obeys "in place / treadmill" beyond the Seedance 2.5 "jog" failure and Kling V3's success in Iso Cycles.

## 4. Does the model preserve 2D / pixel / cel-shaded style, or push toward 3D?

### Takeaway
No controlled benchmark of 2D or pixel-art style retention across Veo, Kling, Wan and the rest was found. The documented evidence is anecdotal but consistent:
- Image-to-video carries the start frame's palette and style when motion is small and slow.
- Big or fast motion and camera moves smear crisp edges.
- Flat shading animates far more stably than volumetric shading.
- True pixel art needs a post-pass: re-pixelate, lock the palette and snap to the grid. No current video model outputs grid-exact pixels.

Kling V3 I2V Standard is the model with a published end-to-end pixel-art sprite pipeline. The studio's own result (Veo animating a GPT concept "perfectly") is a data point for painted or cel-style concepts, not for pixel art.

### Cited Findings
- Kling (vendor): the source artwork's palette and pixel style carry into the clip. There is "no special pixel mode, and the whole craft is restraint". Big or fast motion or dramatic camera moves blur pixel edges "into mush". Example prompt: "subtle looping ambient idle animation, everything stays in crisp clean pixel-art style." — [Kling pixel-art topic page (11 Jul 2026)](https://kling.ai/topics/animate-pixel-art-ai)
- Iso Cycles produced pixel-art heroes with Kling V3 I2V Standard. Post-processing downscaled each hero to a fixed height (64–96 px), mapped it to a 24–28 colour median-cut palette, and mirrored directions. Retro Diffusion Animation was tried and rejected because it produced only four directions at four frames each, with no run or attack. — [Scenario Iso Cycles](https://www.scenario.com/explorations/iso-cycles/)
- The open pipeline "pixel-video-sprites" runs Wan 2.2 I2V A14B for motion, then a Krea 2 Turbo img2img re-draw with a pixel LoRA, then a refiner that enforces the exact grid and one shared palette. Native sprites go up to 64 px, upscaled to 384² before generation. Quoted limitations: "Video models do not like destroying characters" and "Not every seed works – generate a few variants and pick one." It runs on an RTX 4090 with 24 GB VRAM. — [GitHub pixel-video-sprites](https://github.com/cueqzapper/pixel-video-sprites)
- A search-snippet summary of the same repo says the smaller Wan 2.2 5B model "grew and redesigned the character and froze the pose" in its tests. This was not confirmed in the fetched README. — [GitHub pixel-video-sprites](https://github.com/cueqzapper/pixel-video-sprites)
- A community Wan 2.2 LoRA for pixel-style attack sprites recommends 64×64 pixel characters resized to 512×512 as input. — [Civitai](https://civitai.com/models/2085866/wan22-pixel-style-attack-sprite-animation-lora)
- Volumetric shading raises frame-to-frame pixel variance by more than 40% compared with flat shading. The suggested fixes are indexed palette locking and bounding-box normalization. — [Atlas Cloud H3 sprite guide](https://www.atlascloud.ai/blog/tips/minimax-h3-game-sprites-atlas-guide)
- Pixel-grid repair tools:
  - proper-pixel-art handles animations by exploiting the fact that every frame shares one grid and palette ("consistent frame-to-frame with no flicker"). — [GitHub proper-pixel-art](https://github.com/KennethJAllen/proper-pixel-art)
  - Retro Diffusion's fixer addresses edges blurred by bilinear resampling. — [GitHub Retro-Diffusion/pixel-art-fixer](https://github.com/Retro-Diffusion/pixel-art-fixer)
- Midjourney's loop and start/end update notes that "artistic images work better" than realistic ones, which become choppy near the end. — [lilys.ai](https://lilys.ai/en/notes/ai-midjourney-20251111/midjourney-video-loop-start-end)
- Sorceress (verified 1 Jun 2026) recommends pixel-native generators (Retro Diffusion "rd-animation") for synthesized pixel sheets, and image-to-video (Wan 2.7 or Kling 3.0) plus background removal for sheets derived from video. It reports no measured style-retention results. — [Sorceress](https://sorceress.games/blog/tune-the-best-ai-animation-generator-honest-2026-test)

### Inferences
- For **painted or cel-shaded 2D** (the GPT-concept case), Veo 3.1 and Kling 3.0 both appear to hold style when motion is modest. The studio's own Veo success fits that pattern.
- For **pixel art**, plan for a two-stage pipeline whatever the model: animate at a high resolution from an upscaled sprite, then down-sample, quantize to the original palette and grid-snap every frame. Video models output anti-aliased, interpolated pixels by construction (an inference from the cited fix-up tools existing at all).
- Flat-shaded concepts (cel or flat colour, hard outlines, no gradients or rim lights) should animate with less shimmer than painterly concepts. Give the image model that instruction when making the base concept.
- The pull toward 3D or realism is most likely when prompts use cinematic language (lens, depth of field, dramatic lighting). For sprites, describe the style as "flat 2D game sprite, hard outlines, flat colour" and leave cinematography terms out. This is my inference, consistent with the Kling guidance on restraint.

### Gaps
- No head-to-head test (Veo vs Kling vs Seedance vs Wan vs Luma) on the same pixel or cel inputs, scored for palette stability, edge crispness or flicker, was found. This should be run in-house. Suggested setup: 3–5 inputs, identical prompts, scored after the same palette and grid snap.
- No Veo-specific pixel-art reports were found.

## 5. Generating many animations (idle, walk, run, attack, jump, hurt, death) of the same character consistently

### Takeaway
Most video models offer "reference" modes: Veo ingredients (up to 3), Kling Elements and O3 (up to 7 including keyframes), Seedance 2.5 (up to 30), WAN 3.0 (up to 10), and Omni Flash subject references. But several models document that **reference mode cannot be combined with first/last-frame mode** (Seedance 2.5, WAN 3.0, MiniMax H3). Veo's reference mode also forces 8 s. The approach that is actually documented for sprites keeps identity through the **start (and end) frames**:
1. Make one canonical character still.
2. With an image model, derive per-action and per-facing start poses (small transition poses) from it.
3. Animate each one with first-frame or first+last-frame i2v on the same model and settings.
4. Normalize scale and palette across all clips.

### Cited Findings
- Veo 3.1 reference images: up to 3 "asset" images to preserve a single character's appearance. Requires 8 s, and not available on Lite. — [Gemini API Veo docs](https://ai.google.dev/gemini-api/docs/veo)
- Gemini Omni Flash: subject reference with multiple images, plus multi-turn editing that "preserves the rest of the video". — [Gemini API Omni docs](https://ai.google.dev/gemini-api/docs/omni)
- Kling Elements: upload images or a 3–8 s video to extract a character's traits and appearance. O3 adds multi-image element building and multi-character coreference. — [fal Kling 3](https://fal.ai/kling-3)
- Kling O3 i2v takes first/last keyframes plus up to 7 references in total. — [Runway API inputs](https://docs.dev.runwayml.com/assets/inputs/)
- Seedance 2.5 takes up to 30 reference images and "maintains identity, style, and composition from the references", but frame images "can't be combined with any reference input". — [Together AI](https://docs.together.ai/docs/seedance2.0-quickstart)
- WAN 3.0 takes up to 10 image references, and keyframes cannot be mixed with references. In MiniMax H3, keyframe and unpositioned-reference modes cannot be mixed. — [Runway API inputs](https://docs.dev.runwayml.com/assets/inputs/)
- Iso Cycles workflow:
  - GPT Image 2.5 drew two angles (SE, NE) in one image.
  - Kling V3 animated walk and run from the first frame, and idle and attack with first+last frame.
  - GPT Image 2.5 then redrew E, S and N "from reference images, one pose per image", and each new facing was animated as a 5 s first+last-frame clip.
  - The loops were matched for size (scaled to the SE median height) and speed (per-direction fps). Every hero shares one palette.
  - — [Scenario Iso Cycles](https://www.scenario.com/explorations/iso-cycles/)
- LayrKits: for non-idle animations, generate a small transition pose from idle with the image model rather than the extreme pose. Use the same anchors for 12-frame and 24-frame versions. If an action's end doesn't connect to idle, generate bridge frames. — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)
- Scenario help: attacks are built from neutral→attack and attack→neutral first/last clips. Props such as a chest use an "open and close loop" prompt. — [Scenario help](https://help.scenario.com/en/articles/create-spritesheets-with-scenario/)
- Atlas Cloud H3 guide: first-frame i2v "locks the starting pose and color". It uses timestamped multi-beat prompts for attack and jump. — [Atlas Cloud H3 sprite guide](https://www.atlascloud.ai/blog/tips/minimax-h3-game-sprites-atlas-guide)
- Pixel-video-sprites: all frames share one palette built from the sprite's colours, so a palette lock across every animation of the same character is possible as a post step. — [GitHub pixel-video-sprites](https://github.com/cueqzapper/pixel-video-sprites)

### Inferences
- For a sprite set, **identity is best carried by the first frame**, which i2v reproduces exactly at t=0. Reference modes are designed for cinematic re-staging: they give the model freedom over composition and often can't be combined with first/last frames. For consistent framing and scale, that is a disadvantage.
- Keep **one model, one resolution and one camera prompt** for the whole move set. Mixing models changes motion style, scale behaviour and edge treatment between animations.
- Actions that leave and return to idle (attack, hurt, jump) should be pinned to the idle pose at the end. Death and other terminal actions need only a first frame. Locomotion needs only a first frame plus loop-window search.
- Mirror left and right facings in post rather than generating them. That halves cost and guarantees symmetry. Asymmetric designs (a weapon in one hand) need a deliberate decision.
- Budget for 3–5 takes per action. Practitioners report that "not every seed works" ([pixel-video-sprites](https://github.com/cueqzapper/pixel-video-sprites)), and one source notes that effective cost depends on retries ([invideo](https://invideo.io/blog/ai-video-model-pricing)).

### Gaps
- No source measured cross-clip identity drift (e.g. Veo ingredients vs a first-frame-only workflow) on stylized 2D characters.
- Veo 3.1's documentation doesn't say whether reference images can be combined with a first frame or last frame in the same request. Needs testing.
- No documented use of Kling 4.0's up-to-10 keyframes for sprite sheets yet; the model is in preview.
