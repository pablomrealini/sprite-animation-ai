# From AI video clip to game-ready 2D sprite sheet: the post-processing pipeline (state as of October 2026)

Scope: what to do after a Veo/Kling/Wan image-to-video clip of a 2D character exists, up to an atlas imported in Unity/Godot/Phaser. Choosing the video model, dedicated sprite generators (PixelLab etc.), and Spine/ComfyUI/Mixamo-style alternatives are covered in other notes in this folder.

Verification note: the ffmpeg commands marked **[tested]** were run on this Mac on 2026-10-15 with **ffmpeg 8.1.2 (Homebrew)**, using a synthetic 24 fps green-screen clip. Filter defaults quoted below come from `ffmpeg -h filter=<name>` on that build. Python snippets were **not executed** because numpy/Pillow aren't installed on this machine. They use standard APIs but should be smoke-tested. All other claims carry inline sources.

Recommended stage order (rationale in the sections below):
1. Probe the clip and extract **all native frames** as lossless PNG.
2. Find the loop and trim to it at native fps.
3. (Optional) interpolate in RGB, before any alpha exists.
4. Remove the background.
5. Stabilize and align to a pivot on a common canvas.
6. Decimate to game fps (or decimate right after step 2, if the loop length is a multiple of the decimation factor).
7. Downscale (HD), or pixelize and quantize (pixel art).
8. Alpha cleanup and bleed.
9. Pack.
10. Import into the engine.

---

## 1. Frame extraction & fps resampling (ffmpeg fps vs select vs blending, VFR, mpdecimate, interpolation)

### Takeaway
Extract every native frame losslessly as PNG first, then choose frames by **integer decimation** (24→12/8/6, 30→15/10, 16→8). Decimate with `select='not(mod(n,K))'` or `fps=` and never blend frames: `tmix`, `framerate` and `minterpolate` all create ghosted frames. AI clips are normally constant-frame-rate (Veo 3.1 is fixed at 24 fps), so `mpdecimate`/VFR handling is only a safety check. RIFE interpolation is rarely needed for sprites because you're reducing fps, not increasing it. Its main uses are bridging a loop seam and raising Wan's 16 fps.

### Cited Findings
- Veo 3.1 output is a fixed 24 fps across tiers. Resolution is 720p or 1080p (some tiers 4K), with 4/6/8-second lengths and 1080p/4K locked to 8 s. Sources: [CometAPI Veo 3.1 specs](https://www.cometapi.com/models/google/veo3-1/) and [veo3ai resolution guide 2026](https://www.veo3ai.io/blog/veo-3-1-resolution-1080p-4k-guide-2026). These are secondary sources and disagree on resolutions.
- Wan 2.2 open weights natively output about 16 fps (480p–720p, max 81 frames). Hosted versions often report 24 fps. Source: [ComfyUI Wan 2.2 guide](https://comfyui.nomadoor.net/en/basic-workflows/wan-2-2/).
- I found no source confirming Kling 2.5's native fps ([Morphic Kling 2.5 glossary](https://morphic.com/ai-glossary/Kling-25) gives resolution only).
- `fps` filter options on ffmpeg 8.1.2 [tested]: `fps` (default "25"), `start_time`, `round` (zero/inf/down/up/near; default `near`), `eof_action` (round/pass). It forces a constant frame rate by dropping or duplicating frames based on timestamps. Docs: [ffmpeg fps](https://ffmpeg.org/ffmpeg-filters.html#fps).
- `mpdecimate` options [tested]:
  - `max`: default 0
  - `keep`: default 0; the number of similar frames kept before dropping starts
  - `hi`: default 768
  - `lo`: default 320
  - `frac`: default 0.33

  On a clip with continuous motion it dropped nothing (72 in, 72 out) [tested]. Docs: [ffmpeg mpdecimate](https://ffmpeg.org/ffmpeg-filters.html#mpdecimate).
- `framestep` ("select one frame every N frames"), `framerate` ("upsamples or downsamples… between specified frame rates", i.e. it blends), `minterpolate` (motion interpolation) and `tmix` (mixes successive frames) all ship in the 8.1.2 build [tested `ffmpeg -filters`]. Docs: [ffmpeg-filters](https://ffmpeg.org/ffmpeg-filters.html).
- `vfrdet` reports a VFR ratio. A CFR clip printed `VFR:0.000000 (0/71)` [tested].
- Practical-RIFE:
  - Latest model is v4.26 (2024-09-21); v4.25 is recommended as the default. MIT licensed, including the weights.
  - "the anime scenes have been significantly improved" in 4.25, and 4.24+ are described as suited to post-processing diffusion-generated video.
  - Video: `python3 inference_video.py --multi=2 --video=video.mp4` (add `--scale=0.5` for high-res input). PNG sequences: `--img=input/`.
  - Source: [Practical-RIFE README](https://github.com/hzwer/Practical-RIFE).

### Inferences

#### Recommended commands (macOS, bash/zsh)
```bash
# 0) Probe: fps, frame count, colour tags. If r_frame_rate != avg_frame_rate, suspect VFR.  [tested]
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,r_frame_rate,avg_frame_rate,nb_frames,pix_fmt,color_space,color_range \
  -of default=nw=1 hero_walk.mp4
ffmpeg -hide_banner -i hero_walk.mp4 -vf vfrdet -an -f null - 2>&1 | grep VFR   # [tested]

# 1) Extract ALL native frames, lossless, numbered from 0. Explicit BT.709 -> RGB avoids a colour shift
#    when the file is untagged (my synthetic clip reported color_space=unknown).  [tested]
mkdir -p raw && ffmpeg -i hero_walk.mp4 \
  -vf "scale=in_color_matrix=bt709:in_range=limited:flags=lanczos+accurate_rnd+full_chroma_int,format=rgb24" \
  -fps_mode passthrough -start_number 0 raw/f_%04d.png

# 1b) Only a time range (seconds) at native fps  [tested: -ss/-to with fps=12 gave 24 frames for 2 s]
ffmpeg -ss 0.5 -to 2.5 -i hero_walk.mp4 -fps_mode passthrough -start_number 0 raw/f_%04d.png
# 1c) Frame-exact range (frames 12..35 inclusive)  [tested: 24 frames]
ffmpeg -i hero_walk.mp4 -vf "select='between(n\,12\,35)'" -fps_mode passthrough -start_number 0 raw/f_%04d.png

# 2) Decimate to game fps
# a) every Kth frame (24->12: K=2, 24->8: K=3, 30->10: K=3, 16->8: K=2)  [tested: 72 -> 36 frames]
ffmpeg -i hero_walk.mp4 -vf "select='not(mod(n\,2))'" -fps_mode passthrough g12/f_%04d.png
# b) the same by timestamps (safer for VFR); with an integer ratio it picks the same frames  [tested]
ffmpeg -i hero_walk.mp4 -vf "fps=12:round=near" g12/f_%04d.png
# c) on an already extracted PNG folder, just copy every Kth file (keeps exact loop control)
i=0; for f in raw/f_*.png; do [ $((i%2)) -eq 0 ] && cp "$f" g12/; i=$((i+1)); done

# 3) Safety check for duplicated/frozen frames (rare with Veo; common with screen-recorded or re-encoded clips)
ffmpeg -i hero_walk.mp4 -vf "mpdecimate=hi=768:lo=320:frac=0.33,setpts=N/FRAME_RATE/TB" -fps_mode vfr dedup/f_%04d.png
```

#### Practical rules
- **Do the loop search (section 2) on native-fps frames, then decimate.** Make the native loop length a multiple of K: an even number of frames for 24→12, a multiple of 3 for 24→8. Otherwise the wrap from the last kept frame back to frame 0 has a different time step than the rest.
- **Avoid non-integer ratios** (24→10, 30→12). The `fps` filter then picks frames on an uneven cadence, which reads as stutter in a short cycle.
- **Never blend.** `tmix`, the `framerate` filter and `minterpolate` produce double-exposed limbs that look terrible as sprite frames. `select`/`fps` only drop frames, so they are safe.
- **Smart picking.** AI video often has motion-blurred frames during fast moves. Within each group of K native frames you can pick the sharpest one (highest variance of the Laplacian) instead of always the first. The cost is slightly uneven timing. This is fine for attacks but not for walk cycles.
- **Per-frame durations beat a fixed fps.** For "holds" (anticipation, impact) use per-frame durations rather than duplicated frames. Aseprite JSON exports frame `duration`, Godot SpriteFrames has per-frame duration multipliers, and Phaser frames accept a `duration`.
- **Interpolation (RIFE/FILM)** is an RGB-only step. Run it **before** background removal, on frames that still have their flat background, and re-matte afterwards. Interpolating RGBA isn't supported by these tools, and interpolating cutouts produces edge garbage. It's mostly useful for:
  - converting 16 fps Wan output to 24 so that 24→12/8 decimation works;
  - generating 1–3 bridging frames between the last and first frame of a nearly-looping clip (section 2).
- **Typical frame budgets.** An 8 s Veo clip is 192 frames at 24 fps, far more than a game needs. A walk cycle is usually about 1 s, so 24 native frames become 8–12 game frames.

### Gaps
- I couldn't extract the ffmpeg docs text for these filters (the page is too large to fetch). Option names and defaults were verified locally with `ffmpeg -h filter=…` instead.
- Kling's native frame rate is unconfirmed. Run `ffprobe` on the actual downloads.
- FILM (Google frame-interpolation) license and status weren't checked in this session. From memory it's Apache-2.0; verify.

---

## 2. Loop point detection and seam repair

### Takeaway
Treat loop finding as a search over (start, end) pairs at native fps. Score each pair by how similar a **short window** around the start is to the window around the end. Comparing windows rather than single frames also matches the direction of motion. Compare downscaled, alpha-premultiplied grayscale frames with SSIM or MSE. Existing open-source tools do this already: looplab (velocity-aware), loopsmith (normalized cross-correlation) and LoopyCut (hash/SSIM). Repair residual seams by:
1. trimming one frame;
2. a 2–4 frame overlap crossfade (risks ghosting);
3. RIFE-generated bridge frames;
4. ping-pong, but only for symmetric motions like breathing idles.

### Cited Findings
- **loopsmith** finds the longest loopable segment in a clip.
  - It compares grayscale thumbnails with normalized cross-correlation, scoring all pairs at once as a matrix product.
  - Among pairs above a similarity threshold (default 0.85), the pair with the largest gap wins. CLI for single files or whole folders.
  - Source: [loopsmith](https://github.com/jpratt9/loopsmith).
- **looplab** exhaustively scores every (start, length) pair and renders the best cut.
  - Its author notes that frame similarity alone can produce loops that look right on a still but jump in motion (same position, opposite direction), so it adds velocity-aware scoring.
  - Needs ffmpeg and Python ≥3.10. Supports MLX, CUDA and numpy, with a heatmap explorer.
  - Source: [looplab](https://github.com/shihanqu/looplab).
- **LoopyCut** has hash, batch-SSIM and hybrid modes, with a default similarity threshold of 98/100 and fixed or automatic loop length. Source: [LoopyCut CLI](https://github.com/carmelosantana/loopycut-cli).
- An older reference algorithm (MoviePy "FramesMatches") compares each frame to frames in a window before it and keeps pairs under a distance threshold. Its API is outdated. Source: [Zulko 2015 blog](http://zulko.github.io/blog/2015/02/01/extracting-perfectly-looping-gifs-from-videos-with-python-and-moviepy/).
- ffmpeg tools relevant to seams [tested present in 8.1.2]:
  - `reverse` (reverse a clip)
  - `loop`
  - `xfade` (options `transition`, `duration`, `offset`)
- A ping-pong sequence built from N PNGs plus the reversed list without its two end frames gave 2N−2 frames (36 → 70) with no duplicated turnaround frames [tested].

### Inferences

#### Loop finder (numpy + Pillow, scikit-image optional): untested snippet
```python
# find_loop.py  —  python3 -m pip install numpy pillow scikit-image
# usage: python3 find_loop.py raw/ 16 [--from0]   (16 = minimum loop length in native frames)
import sys, glob, numpy as np
from PIL import Image
try:
    from skimage.metrics import structural_similarity as ssim
except ImportError:
    ssim = None

paths = sorted(glob.glob(sys.argv[1].rstrip("/") + "/*.png"))
MIN_LEN = int(sys.argv[2]) if len(sys.argv) > 2 else 8
FROM0 = "--from0" in sys.argv          # i2v clips often must loop back to frame 0 (= concept pose)

def load(p, size=160):
    im = Image.open(p).convert("RGBA"); im.thumbnail((size, size))
    a = np.asarray(im, dtype=np.float32) / 255.0
    return (a[..., :3] * a[..., 3:4]).mean(axis=2)   # premultiplied gray: works with or without alpha

F = [load(p) for p in paths]; N = len(F)

def sim(a, b):
    if ssim: return ssim(a, b, data_range=1.0)
    return 1.0 - float(np.mean((a - b) ** 2)) * 10   # crude MSE-based score

def seam(i, j):
    # loop = frames i .. j-1; seamless if frame j looks like frame i AND motion matches around the seam
    ks = (0, 1) if i == 0 else (-1, 0, 1)
    return np.mean([sim(F[i + k], F[j + k]) for k in ks if j + k < N])

starts = [0] if FROM0 else range(0, N - MIN_LEN - 1)
cands = [(seam(i, j), i, j) for i in starts for j in range(i + MIN_LEN, N - 1)]
for s, i, j in sorted(cands, reverse=True)[:8]:
    print(f"score {s:.4f}  keep frames {i}..{j-1}  (length {j-i}; even? {(j-i)%2==0}; /3? {(j-i)%3==0})")
```
- Prefer the top candidate whose length is divisible by your decimation factor K. Then copy frames `i..j-1`. Frame `j` is dropped because it duplicates frame `i`.
- For a cycle that has to start from the exact concept pose (frame 0 of an image-to-video clip), use `--from0`.

#### Seam repair options, in order of preference
1. **Trim**: shift `j` by ±1 and re-check the score. This often fixes a one-frame pop.
2. **Bridge frames with RIFE**:
   1. Take the last kept frame and the first frame (still on the flat background).
   2. Interpolate 1–3 intermediates with RIFE (`--img` folder mode with the two frames; check exact flags in the README).
   3. Append them, then matte.

   This is better than crossfading when the poses differ by a small movement.
3. **Overlap crossfade** (needs K extra frames after the loop end). Output frame `m < K` becomes `(1-w)·frame[L+m] + w·frame[m]`. It is done premultiplied so edges don't darken. Keep K at 2–4: drawn characters ghost visibly with longer fades.
```python
# crossfade_loop.py src/ dst/ L K   — output L frames; requires src to contain >= L+K frames (untested)
import sys, glob, os, numpy as np
from PIL import Image
src, dst, L, K = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
P = sorted(glob.glob(src.rstrip("/") + "/*.png")); os.makedirs(dst, exist_ok=True)
def load(p):
    a = np.asarray(Image.open(p).convert("RGBA"), dtype=np.float32) / 255; a[..., :3] *= a[..., 3:4]; return a
def save(a, p):
    al = a[..., 3:4]; rgb = np.where(al > 0, a[..., :3] / np.maximum(al, 1e-6), 0)
    Image.fromarray((np.concatenate([rgb, al], -1).clip(0, 1) * 255 + .5).astype(np.uint8), "RGBA").save(p)
for m in range(L):
    a = load(P[m])
    if m < K:
        w = (m + 1) / (K + 1)
        a = (1 - w) * load(P[L + m]) + w * a
    save(a, f"{dst}/f_{m:04d}.png")
```
4. **Ping-pong** (forward, then reversed without its two end frames). This is only valid for symmetric motions such as breathing, a bobbing idle or a flag. Walks and runs look wrong reversed, because the contact/passing order inverts and secondary motion (hair, cloth) plays backwards. [tested]
```bash
mkdir -p pp; i=0
for f in $(ls loop/*.png); do cp "$f" pp/$(printf %04d $i).png; i=$((i+1)); done
for f in $(ls -r loop/*.png | sed '1d;$d'); do cp "$f" pp/$(printf %04d $i).png; i=$((i+1)); done
```
5. **Prevention**, from prior knowledge and not re-verified here (see the video-model note): Veo 3.1, Kling and Wan (FLF2V) all offer first-frame + last-frame conditioning. Passing the same image as first and last frame asks the model for a closed loop, and is usually the cheapest fix.

### Gaps
- I didn't benchmark loopsmith, looplab or LoopyCut on cartoon or character footage. Their maintenance status and star counts weren't retrieved.
- I found no ffmpeg-native "find loop" filter.

---

## 3. Background removal: chroma key vs ML matting, temporal consistency, halos, licenses

### Takeaway
**Licensing is the first filter.**
- **Commercially safe:** BiRefNet (all variants, MIT), ToonOut (MIT, a BiRefNet fine-tune for anime/cartoon characters), SAM 2/2.1 (Apache-2.0), and ffmpeg's keyers.
- **Not safe without a paid agreement:** BRIA RMBG-1.4 and RMBG-2.0 (non-commercial). Note that rembg's README now lists `bria-rmbg` as its default model.
- **Check first:** MatAnyone 1/2 (NTU S-Lab License 1.0) and Robust Video Matting (GPL-3.0, human-trained).

**Recommended route for flat-shaded HD characters on a solid background:**
1. If the clip has a truly flat background, try a chroma key first.
2. Otherwise use ToonOut or BiRefNet per frame.
3. If masks flicker, use SAM 2.1 video propagation as a temporally stable "where is the character" mask, and refine the edges inside it per frame.
4. Always fix colour spill and bleed edge colours into transparent pixels.

**For pixel art,** the alpha ends up hard-thresholded anyway (section 5).

### Cited Findings
**ffmpeg keyers** (defaults from `ffmpeg -h filter=…`, 8.1.2) [tested]:
- `chromakey`: operates on YUV. Options: `color` (default black), `similarity` 1e-5–1 (default 0.01), `blend` 0–1 (default 0), `yuv` (default false). [ffmpeg chromakey](https://ffmpeg.org/ffmpeg-filters.html#chromakey)
- `colorkey`: the same options, but in RGB. [ffmpeg colorkey](https://ffmpeg.org/ffmpeg-filters.html#colorkey)
- `hsvkey`: keys an HSV range.
- `backgroundkey`: turns a *static* background into transparency. Options `threshold` 0.08, `similarity` 0.1, `blend` 0.
- `despill` options:
  - `type`: green (default) or blue only, so there is **no magenta mode**
  - `mix`: 0.5
  - `expand`: 0
  - `red`: 0
  - `green`: -1
  - `blue`: 0
  - `brightness`: 0
  - `alpha`: false

  [ffmpeg despill](https://ffmpeg.org/ffmpeg-filters.html#despill)
- **[tested] pitfall:** after `chromakey` alone, fully transparent pixels keep their key colour (RGBA `00ff00 00`). After `despill` they became near-black (`000001 00`).
  - Any later bilinear filtering or non-premultiplied resize pulls that hidden colour into the edges, producing green or dark halos.
  - The 8.1.2 build includes `premultiply` / `unpremultiply` (and `premultiply_dynamic`). The chain `premultiply=inplace=1,scale=…,unpremultiply=inplace=1` ran fine on RGBA PNGs.

**rembg** (25.1k stars; Python ≥3.11, <3.14) — [rembg README](https://github.com/danielgatis/rembg):
- Models: `u2net`, `u2netp`, `u2net_human_seg`, `u2net_cloth_seg`, `silueta`, `isnet-general-use`, `isnet-anime` ("high-accuracy segmentation for anime character"), `sam`, `birefnet-general`, `birefnet-general-lite`, `birefnet-portrait`, `birefnet-dis`, `birefnet-hrsod`, `birefnet-cod`, `birefnet-massive`, and `bria-rmbg` (listed as **default**; RMBG-2.0, about 1.02 GB, 1024², "requires a paid agreement for commercial use").
- CLI modes: `rembg i in out`, `rembg p indir outdir` (with `-w` watch mode), `rembg s` (HTTP server), `rembg b W H -o pattern` (raw RGB24 stream).
- Flags: `-m` model, `-a` alpha matting (closed-form, slow), `-om` mask only, `-ppm` binarize mask ("not with `-dc`"), `-dc` colour decontamination, `-vm` ViTMatte refinement (extra download of about 110 MB).

**BRIA licenses:**
- RMBG-2.0 is "CC BY-NC 4.0 … for non-commercial use"; "Commercial use is subject to a commercial agreement with BRIA". It is built on BiRefNet and runs at 1024×1024. [HF RMBG-2.0](https://huggingface.co/briaai/RMBG-2.0)
- RMBG-1.4 (IS-Net based, 1024×1024) uses the "bria-rmbg-1.4" license: source-available for non-commercial use, with commercial use needing an agreement. [HF RMBG-1.4](https://huggingface.co/briaai/RMBG-1.4)

**BiRefNet** is MIT licensed. Source: [BiRefNet README](https://github.com/ZhengPeng7/BiRefNet).
- Variants:
  - general (Swin-L)
  - `BiRefNet_HR` (2048², Feb 2025)
  - `BiRefNet_HR-matting` (2048², Feb 2025)
  - `BiRefNet-matting` (Oct 2024)
  - `BiRefNet_dynamic` (256–2304 px, Mar 2025)
  - `BiRefNet_lite` and `BiRefNet_lite-2K` (2560×1440)
- FP16 runs at 17 fps at 1024² on an RTX 4090. SDPA attention (Sep 2025) lowered memory use.
- The README points to ToonOut, an anime fine-tune, and notes RMBG-2.0 is "not aware of transparency" (binary-mask oriented).

**ToonOut** fine-tunes BiRefNet for anime characters. The weights are **MIT**; the dataset is CC-BY 4.0. Sources: [HF joelseytre/toonout](https://huggingface.co/joelseytre/toonout) and [arXiv 2509.06839](https://arxiv.org/html/2509.06839v1). The GitHub repo's LICENSE file wasn't confirmed; this comes from Hugging Face metadata.

**SAM 2** (code and checkpoints) is Apache-2.0. Sources: [SAM 2 repo](https://github.com/facebookresearch/segment-anything-2) and [PyPI sam2](https://pypi.org/project/sam2/0.4.0).

**SAM 3** (Nov 2025) detects, segments and tracks in images and video from text or visual prompts. Sources: [InfoQ](https://www.infoq.com/news/2025/11/meta-sam3) and [heise](https://www.heise.de/en/news/Meta-SAM-3-and-3D-available-as-open-models-11125470.html?view=print).
- It uses Meta's custom "SAM License". Secondary mirrors describe it as royalty-free and allowing commercial use, with termination on IP litigation and an indemnity clause. Source: [HF mirror README](https://huggingface.co/AEmotionStudio/sam3/blob/main/README.md).
- The official repo is gated, so read the LICENSE before shipping.

**MatAnyone** (CVPR 2025; [repo](https://github.com/pq-yang/MatAnyone)):
- Input: a video plus a first-frame mask (for example from the SAM2 demo).
- Run: `python inference_matanyone.py -i video.mp4 -m mask.png [--save_image] [--max_size N]`.
- License: "NTU S-Lab License 1.0". Training code was released 2026-03.

**MatAnyone 2** ("Scaling Video Matting via a Learned Quality Evaluator", CVPR 2026 Highlight; [repo](https://github.com/pq-yang/MatAnyone2)):
- Run: `matanyone2 -i frames_or_video -m first_frame_mask.png --save-image`.
- Same S-Lab license. It is described as a *human* video matting framework.

**Robust Video Matting** code was re-released under GPL-3.0 (Sep 2021). Source: [RVM repo](https://github.com/PeterL1n/RobustVideoMatting).

**Existing pipeline tools:**
- [Sunwood video-background-remover-cli](https://github.com/sunwood-ai-labs/video-background-remover-cli) uses RMBG-1.4, so it's non-commercial by default.
- [FrameKit](https://github.com/joepUI/framekit-web)'s chroma key removes background "connected" to the image edges, which preserves same-coloured interior details, and includes despill and fringe trimming.

### Inferences

#### A. Chroma key (when Veo gave you a flat green or magenta background) [tested chain]
```bash
# Green background. similarity 0.08–0.20 and blend 0.02–0.08 are typical starting points for compressed AI video
ffmpeg -i loop.mp4 -vf "chromakey=color=0x00FF00:similarity=0.12:blend=0.05,despill=type=green:mix=0.5:expand=0.1,format=rgba" \
  -start_number 0 keyed/f_%04d.png
# Sample the real background colour first (AI backgrounds are never exactly #00FF00):
ffmpeg -i loop.mp4 -vf "crop=8:8:4:4,scale=1:1:flags=area" -frames:v 1 -f rawvideo -pix_fmt rgb24 - | xxd -p
# Magenta background (good for green characters). Key in RGB with colorkey; despill has no magenta mode (see Python below)
ffmpeg -i loop.mp4 -vf "colorkey=color=0xFF00FF:similarity=0.25:blend=0.05,format=rgba" keyed/f_%04d.png
```

Why a key often fails on AI video:
- The background is noisy and gradient-shaded.
- There are ground shadows and contact shading.
- 4:2:0 chroma subsampling halves colour resolution at edges.
- The model may tint the character with the background colour.

A **"connected-to-border" key** (flood fill from the frame edges, as FrameKit does) avoids punching holes in same-coloured interior details such as a green belt on a character keyed on green.

**Magenta despill** (untested numpy): pull red and blue down toward green wherever both exceed it.
```python
spill = np.clip(np.minimum(r, b) - g, 0, None) * strength   # strength ~0.5–1.0
r -= spill; b -= spill
```

#### B. ML matting, per frame
```bash
python3 -m pip install "rembg[cpu,cli]"      # extras names from memory of the README ("rembg[gpu,cli]" on CUDA); verify
rembg p -m birefnet-general raw/ cut/         # ALWAYS pass -m: the README lists bria-rmbg (non-commercial) as default
rembg p -m isnet-anime raw/ cut_anime/        # compare on cel-shaded characters
rembg p -m birefnet-general -om raw/ masks/   # masks only (for temporal post-processing)
```
BiRefNet (or the ToonOut weights) directly through transformers (untested; loading pattern per BiRefNet README/HF card):
```python
import glob, os, torch
from PIL import Image
from torchvision import transforms
from transformers import AutoModelForImageSegmentation
dev = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
net = AutoModelForImageSegmentation.from_pretrained("ZhengPeng7/BiRefNet_HR", trust_remote_code=True).to(dev).eval()
size = (2048, 2048)  # 1024 for general/lite
tf = transforms.Compose([transforms.Resize(size), transforms.ToTensor(),
                         transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
os.makedirs("cut", exist_ok=True)
for p in sorted(glob.glob("raw/*.png")):
    im = Image.open(p).convert("RGB")
    with torch.no_grad():
        m = net(tf(im).unsqueeze(0).to(dev))[-1].sigmoid().cpu()[0, 0]
    im.putalpha(transforms.ToPILImage()(m).resize(im.size, Image.BILINEAR))
    im.save(f"cut/{os.path.basename(p)}")
```

#### C. Temporal consistency (mask flicker)
Per-frame models re-decide thin parts every frame: weapon tips, hair strands, gaps between legs. The result is boiling edges and parts popping in and out. Options, in order:
1. **SAM 2.1 video propagation** (Apache-2.0).
   1. Click or box the character on frame 0.
   2. Propagate through the clip to get a temporally coherent mask.
   3. Use it as a hard constraint: `alpha = birefnet_alpha * dilate(sam_mask, 3–5 px)`. Or use the SAM mask itself for pixel art.

   Sketch, untested, using the API names in the SAM 2 repo:
```python
from sam2.build_sam import build_sam2_video_predictor
pred = build_sam2_video_predictor("configs/sam2.1/sam2.1_hiera_l.yaml", "checkpoints/sam2.1_hiera_large.pt", device="mps")
state = pred.init_state(video_path="raw_jpg/")          # folder of JPEG frames named 00000.jpg …
pred.add_new_points_or_box(state, frame_idx=0, obj_id=1, box=[x0, y0, x1, y1])
for fidx, obj_ids, logits in pred.propagate_in_video(state):
    mask = (logits[0, 0] > 0).cpu().numpy()             # save per frame
```
   Note: the SAM 2 video loader historically expected a folder of JPEGs. Convert first, e.g. `ffmpeg -i loop.mp4 -q:v 2 -start_number 0 raw_jpg/%05d.jpg`.
2. **MatAnyone / MatAnyone 2**: first-frame mask in, temporally consistent soft alpha out. These are trained on humans, so test them on stylized characters. Their S-Lab license must be read before commercial use; I didn't confirm its terms.
3. **Cheap post-filter**: a temporal median of alpha over 3 frames, applied only where the RGB change between frames is small (static regions). This removes single-frame pops without smearing moving limbs.
4. **Avoid RVM** for cartoon characters: it's trained for human matting, and the GPL-3.0 code is awkward in a shipped toolchain. It's fine as an offline tool if you don't distribute it, but that's a legal question.

#### D. Edges: halos, spill, premultiplication, hard alpha
- **HD sprites**: keep soft alpha, but **bleed** edge colours into the fully transparent pixels before any resize or packing. This removes dark or green halos under bilinear filtering. TexturePacker `--alpha-handling ReduceBorderArtifacts` and Godot "Fix Alpha Border" do the same thing at pack or import time. Python (untested):
```python
from scipy import ndimage
a = np.asarray(img.convert("RGBA")); rgb, al = a[..., :3], a[..., 3]
idx = ndimage.distance_transform_edt(al == 0, return_distances=False, return_indices=True)
out = np.dstack([rgb[idx[0], idx[1]], al])     # transparent pixels take nearest opaque colour; alpha unchanged
```
- **Pixel art**: binarize alpha after downscaling (`alpha = 255 if a >= 128 else 0`; ffmpeg `paletteuse` uses `alpha_threshold=128` by default [tested]), then remove orphan pixels.
- **Shadows**: AI clips often include a contact shadow. Remove it (keep it out of the mask) and draw a runtime blob shadow instead, which is what Kingdom Rush-style games do.

#### E. Which method for which art style
| Material | First choice | Fallback |
|---|---|---|
| HD illustrated, thick outlines, flat or cel shading (Kingdom Rush-like) on a clean flat background | ffmpeg chromakey/colorkey + despill, or border-connected key | ToonOut / BiRefNet_HR per frame + SAM 2.1 temporal constraint |
| HD illustrated on a busy background | SAM 2.1 propagation + BiRefNet_HR(-matting) refine | MatAnyone 2 (check license) |
| Pixel-art-styled video | Key or SAM 2.1 mask → hard alpha after pixelization | ToonOut; avoid soft matting (it creates semi-transparent pixels) |

### Gaps
- No source compared ToonOut, isnet-anime and BiRefNet on Western cartoon or Kingdom Rush-style art. This needs an in-house test on the team's own frames.
- The S-Lab License 1.0 terms (MatAnyone) weren't read directly. Its commercial status is unverified.
- The SAM 3 / SAM 3.1 official license text wasn't read (the repo is gated); only secondary mirrors were.
- Whether SAM 2.1 runs well on Apple MPS for video propagation wasn't verified.
- The `isnet-anime` weights' license wasn't checked.

---

## 4. Alignment, stabilization, pivots and consistent scale

### Takeaway
Do alignment after matting, using the alpha mask. Per frame, compute the ground line (lowest opaque row) and a horizontal anchor (alpha centroid, or the centre of the foot contact band). Remove only the slow **drift** (linear trend over the cycle), not the animation's own bob. Paste onto a fixed canvas with the pivot at bottom-centre. If the camera also zooms or pans, estimate that motion from the **background** before removing it.

Normalize scale across all of a character's animations to one reference height measured on the idle. Then trim in the packer with offset-preserving modes (TexturePacker `Trim`/`CropKeepPos`, Aseprite `--trim` with JSON offsets) so the pivot survives.

`vidstab` isn't available in Homebrew's ffmpeg 8.1.2.

### Cited Findings
- On ffmpeg 8.1.2 (Homebrew) [tested]:
  - `vidstabdetect` → "Unknown filter". The build configuration has no `--enable-libvidstab`.
  - `deshake`, `bbox`, `cropdetect`, `alphaextract`, `alphamerge`, `untile` and `pad` are available.
- `alphaextract,bbox=min_val=16` prints the opaque bounding box per frame (e.g. `x1:99 x2:260 y1:99 y2:260 w:162 h:162`). Plain `bbox` on an RGBA frame measures luma and returned the full frame, so `alphaextract` is required [tested]. [ffmpeg bbox](https://ffmpeg.org/ffmpeg-filters.html#bbox)
- TexturePacker trim modes:
  - **CropKeepPos** "removes transparent borders … but keeps its original position. The anchor point stays the same."
  - **Crop** "moves the sprite to 0/0", so placement changes.

  Other options: `--trim-margin`, `--trim-threshold` (1–255, default 1), and `--common-divisor-x/y`, which forces sprite sizes to multiples. Source: [TexturePacker texture settings](https://www.codeandweb.com/texturepacker/documentation/texture-settings).
- Aseprite CLI has `--trim`, `--trim-sprite` (trim the whole sprite uniformly), `--trim-by-grid`, and `--inner-padding`. Source: [Aseprite CLI docs](https://www.aseprite.org/docs/cli/).
- Unity's Sprite Editor supports `Pivot: Custom` with Pivot Unit Mode = Pixels, with snapping to pixel corners, per sprite in a Multiple sheet. Source: [Unity 6.2 Sprite texture type](https://docs.unity3d.com/6000.2/Documentation/Manual/texture-type-sprite.html), as summarized by search.

### Inferences

#### Union bounding box of a whole animation with ffmpeg only [tested]
```bash
ffmpeg -hide_banner -framerate 12 -i keyed/f_%04d.png -vf "alphaextract,bbox=min_val=16" -f null - 2>&1 \
 | grep -oE "x1:[0-9]+ x2:[0-9]+ y1:[0-9]+ y2:[0-9]+" \
 | awk -F'[: ]' 'NR==1{a=$2;b=$4;c=$6;d=$8}{if($2<a)a=$2;if($4>b)b=$4;if($6<c)c=$6;if($8>d)d=$8}
                END{printf "crop=%d:%d:%d:%d\n", b-a+1, d-c+1, a, c}'
# -> e.g. crop=361:162:0:99 ; then crop + pad to a multiple of 4 with feet on the bottom edge  [tested: 364x164 rgba]
ffmpeg -framerate 12 -i keyed/f_%04d.png \
  -vf "crop=361:162:0:99,pad=w=ceil(iw/4)*4:h=ceil(ih/4)*4:x=(ow-iw)/2:y=oh-ih:color=0x00000000" aligned/f_%04d.png
```
Use one union box **per character across all animations** (idle, walk, attack…). Every sheet then shares the same frame size and pivot, which keeps engine-side offsets trivial.

#### Pivot alignment with drift removal (untested Python)
```python
# align.py in/ out/ CANVAS_W CANVAS_H PIVOT_X PIVOT_Y [--fixed]
import sys, glob, os, numpy as np
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]; CW, CH, PX, PY = map(int, sys.argv[3:7]); FIXED = "--fixed" in sys.argv
P = sorted(glob.glob(src.rstrip("/") + "/*.png")); os.makedirs(dst, exist_ok=True)
anc = []
for p in P:
    al = np.asarray(Image.open(p).convert("RGBA"))[..., 3]
    ys, xs = np.nonzero(al > 128)
    ground = ys.max()                                    # feet / lowest opaque row
    anc.append((xs.mean(), ground))                      # alpha centroid x is steadier than foot x in walks
anc = np.array(anc, float); t = np.arange(len(anc))
if FIXED:                       # one-shot actions (attack, death, jump): lock to frame-0 anchor
    anc[:] = anc[0]
else:                           # cycles: remove linear camera drift, keep the animation's own bob/sway
    for k in (0, 1):
        anc[:, k] = np.polyval(np.polyfit(t, anc[:, k], 1), t)
for p, (ax, ay) in zip(P, anc):
    im = Image.open(p).convert("RGBA")
    cv = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    cv.paste(im, (int(round(PX - ax)), int(round(PY - ay))))   # no mask arg: plain copy keeps alpha intact
    cv.save(os.path.join(dst, os.path.basename(p)))
```
Notes:
- For pixel art, round offsets to multiples of the downscale factor. A 1-HD-pixel jitter becomes a sub-pixel shimmer after pixelization.
- With `paste` into a transparent canvas, don't pass the image as its own mask. With a mask, Pillow blends all bands including alpha, which squares the alpha.

#### Camera zoom or pan in the source
Image-to-video models sometimes push in or drift even when prompted for a "static, locked-off camera".
- **Background present:** estimate per-frame similarity transforms on background features. With OpenCV, use ORB/AKAZE matches restricted to the inverse of the dilated character mask, then `cv2.estimateAffinePartial2D`. Invert the accumulated transform before matting.
- **Background already gone:** you can only normalize **scale** by a body measure that shouldn't change, such as head width or the bbox height of the idle stance.
- **vidstab:** if you really want it, use a non-Homebrew-core ffmpeg build with libvidstab (e.g. a static build or a third-party tap; not verified here). `deshake` is meant for handheld shake, not slow zooms.

#### Consistent scale across clips
Every Veo generation frames the character differently. Choose the **in-game height** first, for example "the soldier is 96 px tall at 1× on a 1080p reference screen", then compute `scale = target_height / measured_idle_height` for each clip. Measure the idle on the body only (exclude raised weapons and hair) and apply the same factor to every animation generated from that clip.

#### Trimming without losing pivots
- **Option a:** export uniform frames (fixed canvas, pivot at a known pixel) and let the packer trim with offset metadata. TexturePacker `--trim-mode Trim` stores the source size and offset in the data file; the engine importer restores them. `CropKeepPos` keeps the anchor. Avoid `Crop`.
- **Option b:** use Aseprite `--trim` with JSON (`spriteSourceSize`/`sourceSize` fields). Its `--trim-sprite` trims all frames by the same rect, which keeps a common pivot without engine support for per-frame offsets.

### Gaps
- No published tool specifically does "alpha-mask-based pivot alignment" for AI sprite clips. The snippet above is my own pattern.
- Whether Homebrew offers an ffmpeg variant with libvidstab in Oct 2026 wasn't verified.
- TexturePacker's `Trim` mode semantics come from general knowledge. The fetched page only explained `CropKeepPos` and `Crop`.

---

## 5. Downscaling HD frames vs true pixel-art conversion

### Takeaway
**HD sprites:**
- Downscale once, from the aligned full-resolution frames to the final size. Use area/box (≥2× reduction) or Lanczos, in **premultiplied** alpha, and add a light unsharp mask.
- Ship at 1× and maybe 2× (or 0.5×/1× for mobile). Don't upscale in-engine.

**Pixel art:**
- There are two paths:
  - **(a)** If Veo produced "fake pixel art" (a pixel look with an irregular grid), use **Proper Pixel Art** (`ppa`, MIT), which has video mode with one shared grid and palette across frames, or **unfake.js/unfake.py** (MIT).
  - **(b)** If the frames are HD illustrations, downscale by an integer factor with area averaging, quantize **all frames of all animations to one fixed palette with dithering off**, binarize alpha, and clean up by hand in Aseprite.
- Temporal flicker comes from per-frame palettes, dithering and sub-pixel jitter. Fix all three.

### Cited Findings
- ffmpeg 8.1.2 [tested]:
  - **palettegen**: `max_colors` 2–256 (default 256), `reserve_transparent` (default true), `transparency_color` (default lime), `stats_mode` full/diff/single (default full).
  - **paletteuse**: `dither` bayer/heckbert/floyd_steinberg/sierra2/sierra2_4a (default)/sierra3/burkes/atkinson (plus none), `bayer_scale` 0–5 (default 2), `diff_mode`, `new` (per-frame palette; default false), `alpha_threshold` (default 128).
  - Generating one palette over a whole PNG sequence and applying it with `dither=none` produced indexed `pal8` PNGs with transparency.
  - Docs: [palettegen](https://ffmpeg.org/ffmpeg-filters.html#palettegen) and [paletteuse](https://ffmpeg.org/ffmpeg-filters.html#paletteuse).
- **Proper Pixel Art** — `pip install proper-pixel-art` or `uvx --from proper-pixel-art ppa …`. MIT, 576 stars. Source: [proper-pixel-art README](https://github.com/KennethJAllen/proper-pixel-art).
  - CLI: `ppa input -o out -c <colors> -s <scale> -t`.
    - `-t`: transparent background
    - `-w`: pixel width (otherwise auto-detected)
    - `-u`: initial upscale, default 2
    - `--color-method dominant|palette`
  - Accepts `.mp4`/`.gif`: `-n` samples 8 frames by default for mesh and palette detection, then applies one shared grid and palette to all frames "to avoid jitter and flicker". GIF output uses one global palette; MP4 output is CRF 1.
  - Algorithm: Canny edges, morphological close, probabilistic Hough lines, grid spacing estimation, one colour per cell.
- **unfake.js** — MIT, 931 stars. Source: [unfake.js README](https://github.com/jenissimo/unfake.js/).
  - Pixel-size detection: runs-based or edge-aware, including fractional and "elastic" grids.
  - Downscalers: dominant, median, mode, mean, qvote, content-adaptive.
  - Palette: imagequant-based colour limiting, fixed custom palettes, alpha binarization, morphological and jaggy cleanup.
  - Native CLI: `unfake detect|snap|downscale|quantize` with a JSON pipeline manifest.
  - Related: [unfake.py](https://github.com/painebenjamin/unfake.py) (Python, Rust-accelerated quantization), the [ComfyUI-Unfake-Pixels](https://github.com/tauraloke/ComfyUI-Unfake-Pixels/) node, and a [browser demo](https://jenissimo.itch.io/unfaker). Coverage: [Gigazine](https://gigazine.net/gsc_news/en/20251202-unfaker-fix-ai-pixel-art/).
- **pyxelate** (MIT) converts images into 8-bit-style pixel art with a learned palette, which can be reused across similar images. "Super Pyxelate" adds palette transfer and better dithering. Source: [pyxelate](https://github.com/sedthh/pyxelate).
- **Aseprite CLI** can convert colour mode and apply a palette in batch:
  - `--color-mode indexed`
  - `--palette pal.png`
  - `--dithering-algorithm none|ordered|old`
  - `--dithering-matrix bayer8x8|…`
  - `--scale`

  Source: [Aseprite CLI](https://www.aseprite.org/docs/cli/).

### Inferences

#### HD downscale [ffmpeg chains tested; ImageMagick not installed here]
```bash
# Premultiplied downscale to 25% (avoids pulling hidden key colour into edges)   [tested]
ffmpeg -framerate 12 -i aligned/f_%04d.png \
  -vf "premultiply=inplace=1,scale=iw/4:-1:flags=area,unpremultiply=inplace=1" hd1x/f_%04d.png
# Lanczos for non-integer factors; then a light sharpen in Pillow or ImageMagick (IM resizes alpha-weighted):
#   magick in.png -filter Lanczos -resize 37.5% -unsharp 0x0.75+0.6+0.01 out.png    (untested here)
```
- Pillow's `Image.resize` on RGBA with a non-nearest filter internally converts to premultiplied `RGBa`. This is from my knowledge of Pillow's source; verify.
- For sharpening, apply `ImageFilter.UnsharpMask(radius=1, percent=50–80, threshold=2)` to RGB only.
- Downscale **once** from the master frames. Keep the master 1080p frames as the source of truth so you can re-export 0.5×/1×/2× later.

#### Pixel-art path (b): HD → pixel art with a global palette [tested ffmpeg parts]
```bash
F=4   # integer factor: e.g. 384-px-tall aligned frames -> 96-px sprite
# 1) area-average downscale (each output pixel = mean of an FxF block), in premultiplied alpha
ffmpeg -framerate 12 -i aligned/f_%04d.png \
  -vf "premultiply=inplace=1,scale=iw/$F:ih/$F:flags=area,unpremultiply=inplace=1" small/f_%04d.png
# 2) ONE palette for the whole animation (better: concatenate ALL animations of the character first)
ffmpeg -framerate 12 -i small/f_%04d.png -vf "palettegen=max_colors=24:reserve_transparent=1:stats_mode=full" \
  -frames:v 1 -update 1 hero_pal.png
# 3) apply it with no dithering and hard alpha -> indexed PNGs   [tested: pal8 output]
ffmpeg -framerate 12 -i small/f_%04d.png -i hero_pal.png \
  -lavfi "paletteuse=dither=none:alpha_threshold=128" px/f_%04d.png
# 4) preview at 4x with nearest neighbour  [tested]
ffmpeg -framerate 12 -i px/f_%04d.png -vf "scale=iw*4:-1:flags=neighbor" -c:v apng -plays 0 preview.apng
```
Alternatives for step 2/3:
- ImageMagick: `magick small/*.png +append -colors 24 -unique-colors pal.png && magick mogrify -dither None -remap pal.png small/*.png` (untested here).
- Aseprite batch with `--palette` and `--color-mode indexed --dithering-algorithm none`.
- Pillow: `img.convert("RGB").quantize(palette=pal_P_image, dither=Image.Dither.NONE)`.
- Best of all, use a **hand-authored palette**, e.g. one picked from the concept art and limited to 16–32 colours. That avoids muddy auto-palettes.

#### Pixel-art path (a): AI "fake pixel art" video
```bash
uvx --from proper-pixel-art ppa loop.mp4 -o hero_walk_px.gif -c 16 -t     # shared grid+palette across frames
ffmpeg -i hero_walk_px.gif -fps_mode passthrough -start_number 0 px/f_%04d.png
```
Run this before or after matting. Matting first with a hard mask tends to be cleaner, and `-t` replaces sub-50% alpha with the background colour.

#### Rules for temporally stable pixelization
- Use one palette per character, shared across animations. Set `paletteuse` `new=0`, the default.
- Dithering **off**. Error diffusion (`sierra2_4a`, the default!) re-dithers differently every frame and "crawls".
- Keep the grid origin fixed: crop and align so offsets are multiples of F before downscaling.
- Binarize alpha at a fixed threshold.
- Optional "temporal hysteresis": keep a pixel's previous palette index if its new colour differs by less than ΔE≈3–5 and alpha didn't change.
- Outline cleanup: a 1-px dark outline pass (outer silhouette), then manual Aseprite cleanup of "jaggies" and orphan pixels. unfake's jaggy/morphological cleanup can automate part of it.
- Expect manual work. Automated pixelization of a 96-px HD-styled character rarely matches hand-made pixel art at small sizes (≤32 px).

### Gaps
- I didn't find PixelLab or Retro Diffusion pixelization specifics within this scope; they're covered by the dedicated-tools note.
- Pixelorama scripting and "pixeldetector" weren't researched.
- Whether `pngquant` still supports remapping to a fixed palette from the CLI wasn't verified, so ImageMagick, ffmpeg or Aseprite are suggested instead.
- No quantitative comparison of ppa vs unfake on video was found.

---

## 6. Packing into sprite sheets

### Takeaway
- **Pixel art** (single character): use Aseprite CLI (`--sheet-type packed|rows --trim --extrude --shape-padding --data --format json-array|json-hash --merge-duplicates`).
- **HD atlases across many characters and multiple resolutions**: use TexturePacker CLI (`--trim-mode Trim|CropKeepPos --extrude 1 --shape-padding 2 --max-size 2048/4096 --multipack --alpha-handling ReduceBorderArtifacts`). A license is required for commercial use, even in free "Essential" mode.
- **Fixed grids:** ffmpeg `tile` or ImageMagick `montage`.
- **Free:** free-tex-packer.

Power-of-two isn't needed for non-mipmapped 2D on modern GPUs, but keep atlases ≤2048 for low-end mobile/WebGL safety, or ≤4096 on PC.

### Cited Findings
**Aseprite CLI:**
- `--sheet`, `--data`, `--format json-hash|json-array` (json-hash default)
- `--sheet-type horizontal|vertical|rows|columns|packed`, `--sheet-pack`, `--sheet-width/height`, `--sheet-columns/rows`
- `--split-layers`, `--split-tags`, `--tag`, `--list-tags`, `--filename-format '{title}-{tag}-{frame}.{extension}'`
- `--trim`, `--trim-sprite`, `--trim-by-grid`, `--extrude` (1 px), `--shape-padding`, `--border-padding`, `--inner-padding`
- `--merge-duplicates`, `--ignore-empty`, `--scale`, `-b` batch, `--script`/`--script-param`

Examples: `aseprite -b --tag "Run Cycle" --trim --extrude --shape-padding 2 --border-padding 1 --sheet run.png --data run.json`. The docs don't cover importing a PNG sequence, but `--oneframe` implies sequences load as frames. Source: [Aseprite CLI](https://www.aseprite.org/docs/cli/).

**TexturePacker CLI** — source: [TexturePacker texture settings](https://www.codeandweb.com/texturepacker/documentation/texture-settings).

| Area | Options |
|---|---|
| Output | `--sheet`, `--data` (placeholders `{n}`/`{n1}`/`{v}` for multipack and variants), `--format`, `--trim-sprite-names` |
| Texture | `--texture-format png|png8|webp|pvr3|ktx2|basis|dds…`, `--png-opt-level 0–7`, `--pixel-format RGBA8888|RGBA4444|RGB565|ETC2_RGBA…`, `--dither-type` |
| Alpha | `--alpha-handling KeepTransparentPixels|ClearTransparentPixels|ReduceBorderArtifacts|PremultiplyAlpha|DiscardAlpha` |
| Size | `--max-size` (default max 2048), `--size-constraints POT|MultipleOf4|WordAligned|CompressionBlocksize|AnySize`, `--force-squared` |
| Packing | `--algorithm Polygon|MaxRects|Grid|Basic`, `--pack-mode Fast|Good|Best`, `--enable-rotation`/`--disable-rotation`, `--multipack` |
| Scaling | `--scale`, `--scale-mode Smooth|Fast|Scale2x…`, `--variant <scale>:<name>…` |
| Trim | `--trim-mode None|Trim|CropKeepPos|Crop|Polygon`, `--trim-margin`, `--trim-threshold` |
| Spacing | `--extrude`, `--shape-padding`, `--border-padding`, `--padding`, `--common-divisor-x/y` |
| Other | `--disable-auto-alias` (identical sprites are shared by default) |

- `ReduceBorderArtifacts` = alpha bleeding; `PremultiplyAlpha` multiplies colour by alpha (same source as the table).
- TexturePacker's Godot exporter is now `godot-spritesheet`; `godot3-spritesheet` still works. 7.2.0 can export Unity data and textures to different directories. 7.1.0 added Phaser 9-slice support (Phaser ≥3.61). Generic formats: JSON array, JSON hash, XML. `TexturePacker --help` lists the format IDs. Sources: [TexturePacker releases](https://www.codeandweb.com/texturepacker/download) and [command line docs](https://www.codeandweb.com/texturepacker/documentation/commandline).
- TexturePacker's free tier is for non-commercial use; commercial projects need a license. Source: [CodeAndWeb FAQ: is TexturePacker free](https://www.codeandweb.com/texturepacker/knowledgebase/is-texturepacker-free). The Essential vs Pro feature table wasn't retrieved ([comparison FAQ](https://www.codeandweb.com/texturepacker/knowledgebase/whats-the-difference-between-free-and-paid-texturepacker)).
- ffmpeg `tile` options [tested]: `layout` (default 6x5), `nb_frames`, `margin`, `padding`, `color` (default black; use `0x00000000` for transparent), `overlap`, `init_padding`. A 36-frame 640×360 sequence with `tile=6x6:padding=2` produced a 3850×2170 RGBA sheet. Docs: [ffmpeg tile](https://ffmpeg.org/ffmpeg-filters.html#tile).

### Inferences

#### Commands
```bash
# A) Aseprite (pixel art; one file per character with tags idle/walk/attack)
aseprite -b px/f_0000.png --save-as hero_walk.aseprite      # loads the numbered sequence as frames (verify on your version)
aseprite -b hero.aseprite --sheet-type packed --trim --extrude --shape-padding 1 --border-padding 1 \
  --merge-duplicates --sheet hero.png --data hero.json --format json-array --list-tags
aseprite -b hero.aseprite --split-tags --sheet-type rows --sheet hero_{tag}.png --data hero_{tag}.json   # one sheet per tag (verify placeholder support in --sheet)

# B) TexturePacker (HD, several characters, multipack, 1x + 0.5x variants). Run `TexturePacker --help` to get exact --format IDs
TexturePacker sprites/ --format json --sheet out/units-{n}.png --data out/units-{n}.json \
  --trim-mode Trim --extrude 1 --shape-padding 2 --border-padding 2 \
  --algorithm MaxRects --pack-mode Best --disable-rotation --max-size 2048 --size-constraints AnySize --multipack \
  --alpha-handling ReduceBorderArtifacts --texture-format png --png-opt-level 1 --trim-sprite-names
#   Godot: --format godot-spritesheet ; Phaser 3/4: the Phaser JSON exporter ; Unity: the "Unity – Texture2D sprite sheet"
#   exporter used with CodeAndWeb's TexturePacker Importer package (IDs not verified here)

# C) ffmpeg fixed grid (all frames same size; frame index = row*cols+col)  [tested]
ffmpeg -framerate 12 -i aligned/f_%04d.png -vf "tile=8x2:padding=2:margin=0:color=0x00000000" -frames:v 1 walk_sheet.png
# D) ImageMagick 7 (not installed here; untested)
magick montage aligned/f_*.png -tile 8x -geometry +2+2 -background none walk_sheet.png
```

#### Rules
- **Padding and extrusion.** Use `--extrude 1` plus 2 px shape padding for any filtered (bilinear) or scaled sprite. Pixel art drawn with nearest filtering and integer camera zoom can use 0–1 px, but extrusion is still cheap insurance against sub-pixel sampling at fractional zooms.
- **Rotation.** Disable it unless the engine importer supports rotated frames. Godot SpriteFrames from a plain grid does not, and manual slicing in Unity doesn't either.
- **Power-of-two.** Only needed for mipmapping on old GLES2/WebGL1 targets or PVRTC (iOS, square POT). For modern GPUs and WebGL2, `AnySize` is fine.
- **Duplicates.** Use Aseprite `--merge-duplicates`, or TexturePacker's default auto-alias (keep it on). Ping-pong and hold frames then cost no extra memory.
- **Pivot.** With trimmed packing, the pivot must be stored per frame (TexturePacker pivot points / sourceSize offsets) or be implicit in a fixed untrimmed canvas. Don't mix approaches inside one character.
- **free-tex-packer** (GUI, plus a `free-tex-packer-core` npm module, [README](https://cdn.jsdelivr.net/npm/free-tex-packer-core@0.3.8/README.md)) is the main free TexturePacker alternative, with JSON hash/array, Phaser, Godot and Unity-style exporters. Its feature details weren't verified here.
- ShoeBox is old and largely unmaintained (not verified).

### Gaps
- Exact TexturePacker `--format` identifiers for Unity, Phaser 3/4 and Godot 4 (beyond `godot-spritesheet`) weren't confirmed; run `TexturePacker --help`.
- Which features are Pro-only in TexturePacker 7.x wasn't retrieved.
- Aseprite's handling of PNG sequences in `-b` mode and `{tag}` placeholders in `--sheet` file names wasn't confirmed by the docs.

---

## 7. Engine import (Unity 6, Godot 4.7, Phaser 3/4) and pixel-art settings

### Takeaway
- **Unity 6:** import PNG sheets as Sprite (Multiple), slice with Grid By Cell Size, set pivot Bottom/Custom in pixels, and use Point filter, no compression and no mipmaps for pixel art, plus the Pixel Perfect Camera (built into URP). Alternatively import `.aseprite` files directly with the **Aseprite Importer** package (1.2.x for Unity 6.1), which generates clips and an Animator Controller.
- **Godot 4.7:** use AnimatedSprite2D + SpriteFrames ("Add frames from a Sprite Sheet"), the Lossless import mode, Nearest filter for pixel art, or the **Aseprite Wizard** plugin.
- **Phaser 3/4:** `load.atlas` + `anims.create` with `generateFrameNames`.

### Cited Findings
**Unity**
- Unity Aseprite Importer 1.2.5 (1.2.x supports Unity 6.1; 1.1.x/1.0.x support 6.0, 2022.3 and 2021.3) imports `.ase`/`.aseprite`. It generates an Animator Controller when the file has more than one frame, Import Mode = Animated Sprite, and Animation Clip is checked. The controller is read-only. Source: [Unity Aseprite Importer manual](https://docs.unity3d.com/Packages/com.unity.2d.aseprite@1.2/manual/index.html).
- Pixel-art import: Texture Type Sprite (2D and UI), Filter Mode **Point**, Compression **None**, the same PPU for all sprites. Pixel Perfect Camera is built into URP; the standalone package isn't compatible with SRP. Sources: [Unity URP pixel-perfect sprite prep](https://docs-alpha.unity3d.com/Manual/urp/2d-pixelperfect-prep-sprites.html) and [Unity 2D Pixel Perfect package](https://docs.unity3d.com/Packages/com.unity.2d.pixel-perfect@5.1/manual/index.html).
- Community guidance adds: disable mipmaps, aniso off, Wrap Clamp, Max Size ≥ native sheet size, and snap settings of 1/PPU. Sources: [SpriteCook Unity pixel-art import guide (Nov 2025)](https://www.spritecook.ai/blog/unity-pixel-art-import-settings) and [Kybernetik platformer import docs](https://kybernetik.com.au/platformer/docs/art/import).
- Slicing: Sprite Mode Multiple → Sprite Editor → Slice → Automatic (detects by transparency; works best with empty space between items) or Grid By Cell Size for evenly spaced frames. Pivot is set per sprite. Source: [Unity 6.2 Sprite texture type](https://docs.unity3d.com/6000.2/Documentation/Manual/texture-type-sprite.html).

**Godot**
- AnimatedSprite2D → SpriteFrames → "Add frames from a Sprite Sheet" → set the rows/columns grid → select frames. The alternative is Sprite2D `hframes`/`vframes` + AnimationPlayer keying `frame`. The current docs are for **Godot 4.7**. Source: [Godot 2D sprite animation](https://docs.godotengine.org/en/stable/tutorials/2d/2d_sprite_animation.html).
- Import, per [Godot importing images](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_images.html):
  - **Lossless** is the default for 2D and "recommended … for pixel art".
  - **VRAM Compressed** "should be avoided for 2D" because of visible artifacts on low-res textures.
  - Mipmaps off for 2D (+33% memory if on).
  - **Fix Alpha Border** (on by default) reduces dark outlines under bilinear filtering; Premult Alpha is the alternative and needs a CanvasItemMaterial with Premul Alpha blend.
  - Filter and repeat are CanvasItem properties in 4.x, with a project-wide default.
- **Aseprite Wizard** (MIT) imports Aseprite files as SpriteFrames and also drives AnimationPlayer for Sprite2D/Sprite3D/TextureRect and AnimatedSprite2D/3D. It supports forward/reverse/ping-pong directions and loop settings from tags. It is only needed at development time; imported animations keep working after removal. The latest listing seen is v9.8.0 for Godot 4.4. Source: [Godot Asset Library – Aseprite Wizard](https://godotengine.org/asset-library/asset/edit/18417).
- TexturePacker exports `godot-spritesheet` data. Source: [CodeAndWeb Godot tutorial](https://www.codeandweb.com/texturepacker/tutorials/how-to-create-sprite-sheets-for-godot).

**Phaser**
- Phaser 4.2.1 still uses `this.load.atlas(key, png, json)` + `this.anims.create({ key, frames: this.anims.generateFrameNames(key, { prefix, start, end, zeroPad, suffix }), frameRate, repeat: -1 })`. Use `generateFrameNumbers` for plain grid spritesheets. Sources: [Phaser 4.2.1 animations SKILL.md (unpkg)](https://unpkg.com/phaser@4.2.1/skills/animations/SKILL.md) and [Phaser 3 API generateFrameNames](https://newdocs.phaser.io/docs/3.85.2/focus/Phaser.Animations.AnimationState-generateFrameNames).

### Inferences

#### Godot 4.x: build SpriteFrames from a horizontal strip by script (untested EditorScript)
```gdscript
@tool
extends EditorScript
func _run() -> void:
    var tex: Texture2D = load("res://units/hero/walk.png")
    var n := 12
    var w := tex.get_width() / n
    var h := tex.get_height()
    var sf := SpriteFrames.new()
    sf.add_animation("walk")
    sf.set_animation_speed("walk", 12.0)
    sf.set_animation_loop("walk", true)
    for i in n:
        var at := AtlasTexture.new()
        at.atlas = tex
        at.region = Rect2(i * w, 0, w, h)
        sf.add_frame("walk", at)          # optional 3rd arg = per-frame duration multiplier (holds)
    ResourceSaver.save(sf, "res://units/hero/hero_frames.tres")
```
- Pixel art: set Project Settings → Rendering → Textures → Canvas Textures → Default Texture Filter = **Nearest**. Pair it with integer scaling (stretch mode viewport/canvas_items with integer scale) and "snap 2D transforms/vertices to pixel". These are setting names from prior knowledge; confirm in the 4.7 UI.
- HD sprites: Linear filter, Lossless (or Lossy/WebP for download size), Fix Alpha Border on.

#### Unity 6: AnimationClip from a sliced sheet (untested editor script)
```csharp
// Assets/Editor/SheetToClip.cs — select the sliced PNG in the Project window, then Assets > Sheet To Clip
using System.Linq; using UnityEditor; using UnityEngine;
public static class SheetToClip {
  [MenuItem("Assets/Sheet To Clip")]
  static void Make() {
    const float fps = 12f;
    string path = AssetDatabase.GetAssetPath(Selection.activeObject);
    var sprites = AssetDatabase.LoadAllAssetsAtPath(path).OfType<Sprite>()
        .OrderBy(s => int.Parse(s.name.Substring(s.name.LastIndexOf('_') + 1))).ToArray(); // walk_0..walk_11 (numeric sort)
    var clip = new AnimationClip { frameRate = fps };
    var keys = sprites.Select((s, i) => new ObjectReferenceKeyframe { time = i / fps, value = s })
        .Append(new ObjectReferenceKeyframe { time = sprites.Length / fps, value = sprites.Last() }) // hold last frame
        .ToArray();
    AnimationUtility.SetObjectReferenceCurve(clip,
        EditorCurveBinding.PPtrCurve("", typeof(SpriteRenderer), "m_Sprite"), keys);
    var st = AnimationUtility.GetAnimationClipSettings(clip); st.loopTime = true;
    AnimationUtility.SetAnimationClipSettings(clip, st);
    AssetDatabase.CreateAsset(clip, System.IO.Path.ChangeExtension(path, ".anim"));
  }
}
```
- Pixel art in Unity: Point filter, Compression None, mipmaps off, PPU = character grid (e.g. 32), Pixel Perfect Camera (URP), and pivot in pixels at the feet.
- HD (Kingdom Rush-like) in Unity: Bilinear filter, mipmaps off (unless the camera zooms out a lot), and compression chosen per platform (section 8). Use a Sprite Atlas (V2) to batch.
- For skin and palette variants of the same animation, Unity's **Sprite Library / Sprite Resolver** (2D Animation package) swaps sprite sets while reusing one clip. Its API details weren't re-verified here.

#### Phaser 3/4
```js
// preload
this.load.atlas('hero', 'assets/hero.png', 'assets/hero.json');   // TexturePacker/Aseprite JSON hash or array
// create
this.anims.create({
  key: 'hero_walk',
  frames: this.anims.generateFrameNames('hero', { prefix: 'walk_', start: 0, end: 11, zeroPad: 4, suffix: '.png' }),
  frameRate: 12, repeat: -1
});
this.add.sprite(400, 300, 'hero').setOrigin(0.5, 1).play('hero_walk');   // origin at feet
```
- Pixel art in Phaser: game config `pixelArt: true` (nearest filtering + roundPixels; from prior knowledge, verify for v4). HD: default linear filtering.
- Aseprite JSON loads directly with `this.load.aseprite(key, png, json)` plus `this.anims.createFromAseprite(key)` in Phaser 3.50+. This is from prior knowledge; verify in v4.

### Gaps
- I didn't verify whether Phaser 4 changed `pixelArt`/`roundPixels` behaviour or the Aseprite loader.
- The name and version of CodeAndWeb's TexturePacker Importer for Unity 6 and Godot 4.7 weren't verified.
- Aseprite Wizard compatibility with Godot 4.5–4.7 wasn't confirmed; the latest listing seen targets 4.4.

---

## 8. Texture memory budgets and trade-offs

### Takeaway
Uncompressed RGBA8 costs **4 bytes per pixel** in VRAM, regardless of PNG/WebP compression on disk:
- a 2048² atlas = 16 MB
- a 4096² atlas = 64 MB
- mipmaps add 33%

Block compression saves 4–16× but damages pixel art and hard alpha edges:
- ASTC 4×4 = 8 bpp, 6×6 = 3.56 bpp, 8×8 = 2 bpp
- ETC2 RGBA8 / BC3 / BC7 = 8 bpp

So use uncompressed (or Godot Lossless) for pixel art. For HD sprites, test ASTC 4×4–6×6 / BC7 per platform.

The biggest levers are fewer frames, smaller frames, trimming, sharing frames and mirroring, not compression.

### Cited Findings
- ASTC uses a fixed 128-bit block, supports RGBA and LDR/HDR, and has these bitrates. Source: [Wikipedia ASTC](https://en.wikipedia.org/wiki/Adaptive_scalable_texture_compression).

  | Block | bpp |
  |---|---|
  | 4×4 | 8.00 |
  | 5×5 | 5.12 |
  | 6×6 | 3.56 |
  | 8×8 | 2.00 |
  | 10×10 | 1.28 |
  | 12×12 | 0.89 |
- Unity issue reports:
  - ASTC artifacts on sprite atlases, e.g. black blocks with ASTC 6×6 "fast" quality ([Unity issue](https://issuetracker.unity.com/issues/1315/visible-artifacts-on-a-sprite-atlas-preview-image-when-using-astc-6x6-compression-with-fast-quality)).
  - Masks or cutouts generated from ASTC-compressed textures show artifacts with "all ASTC compressions (excluding HDR)". Unity said compression leaves artifacts in some pixels and alpha-clipping near 0 exposes them ([Unity issue](https://issuetracker.unity3d.com/issues/masks-generated-from-images-with-astc-compression-contain-artifacts)).
- Android recommends GPU-compressed textures, which load faster and use less memory than RGBA arrays, with per-format asset pack directories. Source: [Android texture compression targeting](https://developer.android.com/guide/playcore/asset-delivery/texture-compression).
- Godot: VRAM Compressed "should be avoided for 2D"; Lossless is recommended for pixel art; mipmaps add about 33%; `Size Limit` caps imported size. Source: [Godot importing images](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_images.html).
- TexturePacker defaults to a 2048 max sheet size and supports `--multipack`, Polygon trimming, `--variant` scale variants, and auto-aliasing of identical sprites. Source: [TexturePacker texture settings](https://www.codeandweb.com/texturepacker/documentation/texture-settings).

### Inferences

#### Memory math (bytes = W × H × bpp / 8; RGBA8 = 32 bpp)
| Item | RGBA8 | ASTC 4×4 / BC7 / ETC2 RGBA (8 bpp) | ASTC 6×6 (3.56 bpp) |
|---|---|---|---|
| 1 frame 128×128 | 64 KB | 16 KB | ~7 KB |
| 1 frame 256×256 | 256 KB | 64 KB | ~28 KB |
| Walk 12 frames @ 256×256 (untrimmed) | 3 MB | 0.75 MB | ~0.33 MB |
| Character: 6 anims × 10 frames @ 256² | 15 MB | 3.75 MB | ~1.7 MB |
| Atlas 2048×2048 | 16 MB | 4 MB | ~1.8 MB |
| Atlas 4096×4096 | 64 MB | 16 MB | ~7.1 MB |

Interpretation for a Kingdom Rush-like tower-defense game (many unit types on screen):
- 20 enemy types × 60 frames × 128² RGBA8 is about 77 MB before trimming. Trimming typically cuts 30–60% for characters (estimate, not sourced).
- Halving the frame rate (24→12) halves memory.
- Shipping a 0.5× atlas for low-end phones quarters it.

#### Tricks, ordered by impact
1. **Fewer frames.** 8–12 fps cycles. Reuse frames: ping-pong idles, holds via per-frame duration, merged duplicates.
2. **Mirror at runtime** (`flipX`) instead of storing left- and right-facing sets.
3. **Trim + tight packing.** MaxRects, or Polygon in TexturePacker for irregular silhouettes, with offsets preserved.
4. **Resolution variants.** 1× and 0.5× (or 2×/1×) via TexturePacker `--variant`, chosen at runtime by device class. "Half-res + upscale in engine" blurs HD art; it's acceptable only for fast-moving or small units.
5. **Split static and animated parts.** For example a large, mostly static body with a small animated overlay. Weapons and FX can be separate sprites.
6. **Palette swaps for pixel art.** Store an indexed or grayscale (R8, 1 byte/px) texture plus a palette LUT and recolour in a shader for team colours and variants. This is a 4× VRAM saving vs RGBA8 and an N× saving vs storing variants.
7. **Compression.** HD painted sprites usually tolerate ASTC 4×4–5×5 (mobile) or BC7 (PC) when padding/extrusion is ≥2–4 px, so blocks don't straddle sprites. Pixel art and hard alpha cutouts: keep RGBA8 (or RGBA4444 only if the palette survives it; usually it doesn't).
8. **Atlas limits.** Stay at ≤2048 for broad mobile and web compatibility, ≤4096 on PC and modern mobile, and use multipack to split.
9. **PNG8/indexed on disk** (TexturePacker `png8`, `--png-opt-level`) cuts download size only. Engines expand it to RGBA8 in VRAM unless you do palette lookup yourself.

### Gaps
- I found no authoritative 2025–2026 figures for "typical" 2D texture budgets on mobile vs PC, and none from Ironhide or Kingdom Rush. Treat budgets as project-specific and measure with the Unity Memory Profiler or Godot's monitors.
- BC7, ETC2 and PVRTC bitrates above come from standard format specifications, not a fetched source in this session.
- The trimming savings percentage is an estimate.

---

## 9. Existing open-source and web tools that already do "video → sprite sheet"

### Takeaway
Nothing mature and widely adopted covers the whole pipeline (loop → stable matting → pivot alignment → pixelization → engine atlas). Existing tools are small, young projects or web apps. The most useful ready-made pieces are:
- **FrameKit** (browser, MIT) for quick key+extract+sheet
- **duyngha/video-to-spritesheet** (macOS desktop, rembg)
- **looplab/loopsmith** for loops
- **Proper Pixel Art/unfake** for pixel-art video
- **rembg/BiRefNet/ToonOut/SAM 2.1** for matting
- **Aseprite/TexturePacker CLIs** for packing

For a two-person studio, a ~200-line Python + ffmpeg script built from the snippets above is the practical "pipeline" today (inference).

### Cited Findings
**End-to-end video → sprite sheet**
- **joepUI/framekit-web**: browser-based and fully local, MIT, 40 stars, 5 commits. Source: [FrameKit repo](https://github.com/joepUI/framekit-web).
  - Video→sprite sheet with crop, frame extraction, and border-connected chroma key (tolerance/feather/smoothing/despill, fringe trimming).
  - Exports PNG sheet, PNG sequence ZIP, GIF/APNG/WebP and a "Spine-style" package (Spine 4.2 per the repo description).
  - Live demo: https://fk.designtt.cc/.
- **duyngha/video-to-spritesheet** (fork of siloebb/video-to-spritesheet): Python + Flet desktop app for macOS (arm64 .app), Apache-2.0, 0 stars, 3 commits. Source: [repo](https://github.com/duyngha/video-to-spritesheet).
  - Frame-rate and time-range extraction.
  - Chroma key / magic wand (border-connected) / rembg AI (`u2net`, `u2netp`, `isnet-general-use`, optional alpha matting).
  - Exports PNG frames, a sheet + `sheet.json` atlas, and GIF/WebP/APNG, with optional trimming.
- **prakashtaz0091/SpriteSheet-Generator**: tkinter + OpenCV + rembg; horizontal sheet with padding. Source: [repo](https://github.com/prakashtaz0091/SpriteSheet-Generator).
- **Sunwood-ai-labs/video-background-remover-cli**: rembg/RMBG-1.4 video background removal to animated WebP/GIF, with no packing step. RMBG-1.4 is non-commercial. Source: [repo](https://github.com/sunwood-ai-labs/video-background-remover-cli).

**Web apps (closed-source; maintenance not checked)**
- **SpriteFlow**: AI, magic-wand and brush background removal; Unity/Cocos/Godot presets. [spriteflow.zkk234.com](https://spriteflow.zkk234.com/)
- **spritesheetsai.com**: chroma key of up to 5 colours; Unity/Godot export. [spritesheetsai.com](https://spritesheetsai.com/)
- **"Spritesheet MP4 GIF converter pro"** on itch.io: AI auto-crop and background removal, sheet offsets (v3.00 devlog). [itch.io devlog](https://lion-in-a-box-games.itch.io/spritesheet-mp4-gif-converter-pro/devlog/549120/v-300-mega-update-ai-automatic-crop-tool-ai-remove-background-sprite-sheet-offset-and-more)

**Generators, not converters (out of scope)**
- [falsprite](https://github.com/lovisdotio/falsprite)
- [sprite-sheet-creator](https://github.com/blendi-remade/sprite-sheet-creator)

Both use fal.ai and BRIA background removal (check BRIA's commercial terms on the hosted API).

**ComfyUI**
- Official workflow templates for sprite sheets use `comfyui-rmbg`, `comfyui-kjnodes`, VideoHelperSuite `VHS_VideoCombine` and `SaveImageWithAlpha`. Sources: [ComfyUI sprite sheet template](https://comfy.org/workflows/templates-sprite_sheet-fe5600667e2c/) and [single-image sprite sheet template](https://www.comfy.org/workflows/template_purz_nb2_single_image_sprite_sheet-065f4992f6e8).
- I found no dedicated "video frames → packed atlas" custom node.
- [ComfyUI-Unfake-Pixels](https://github.com/tauraloke/ComfyUI-Unfake-Pixels/) handles pixel-art cleanup.

**Building blocks** (covered above)
- Loops: [looplab](https://github.com/shihanqu/looplab), [loopsmith](https://github.com/jpratt9/loopsmith), [LoopyCut](https://github.com/carmelosantana/loopycut-cli)
- Pixel art: [proper-pixel-art](https://github.com/KennethJAllen/proper-pixel-art) (576★, MIT), [unfake.js](https://github.com/jenissimo/unfake.js/) (931★, MIT), [pyxelate](https://github.com/sedthh/pyxelate) (MIT)
- Matting: [rembg](https://github.com/danielgatis/rembg) (25.1k★), [BiRefNet](https://github.com/ZhengPeng7/BiRefNet) (MIT)

### Inferences

#### Suggested folder-based pipeline the team can script (macOS, all CLI)
```
01_raw/        ffmpeg extract native PNGs (bt709→RGB)                       [§1]
02_loop/       find_loop.py → copy frames i..j-1; optional RIFE bridge      [§2]
03_alpha/      chromakey+despill OR rembg -m birefnet-general / ToonOut;
               SAM2.1 mask constraint if flicker; alpha bleed               [§3]
04_aligned/    align.py (pivot bottom-centre, drift removal, common canvas) [§4]
05_fps/        keep every Kth frame (K divides loop length)                 [§1]
06_final/      HD: premultiplied area/lanczos downscale (+0.5x variant)
               Pixel: integer area downscale → global palette, no dither,
               alpha≥128 → Aseprite cleanup                                  [§5]
07_atlas/      Aseprite -b … --sheet-type packed  OR  TexturePacker …       [§6]
08_preview/    ffmpeg APNG/GIF preview at game fps (APNG: -c:v apng -plays 0) [tested]
```
- Preview gotchas [tested]:
  - `-f apng` with the default `png` encoder fails; use `-c:v apng`.
  - Homebrew ffmpeg 8.1.2 has **no libwebp encoder** (`libwebp_anim` unknown), so make animated WebP previews elsewhere (e.g. `img2webp` from libwebp).
- Keep 01–04 at full source resolution and as the "master". Every later stage is reproducible, so changing the target size, palette or fps never requires regenerating the video.

### Gaps
- Star counts and last-commit dates weren't retrieved for SpriteSheet-Generator, the Sunwood CLI, looplab, loopsmith and LoopyCut.
- ezgif's sprite-sheet tool and "Proper Pixel Art"'s web UI weren't checked.
- I found no YouTube or Reddit 2025–2026 devlogs specifically documenting a Veo → sprite sheet workflow in this session (no targeted search was made), so community best practice beyond the tools above is unverified.
