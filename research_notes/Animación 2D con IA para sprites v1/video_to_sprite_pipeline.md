# Video-to-Sprite-Sheet Pipeline (AI-generated 2D character clip → engine-ready sheet)

Scope: technical post-production from an image-to-video clip (Veo / Kling / similar; 720p–1080p, 24 fps, a few seconds, solid background) to a packed, engine-importable sprite sheet. Researched 2026-10-15. Version numbers are noted where the source gave them. Commands marked "constructed" are assembled from documented options but were not executed in this session.

Recommended pipeline at a glance (synthesis — details and sources in each section below):

1. Generate the source correctly: flat `#00FF00` background, full body, centered, locked camera, walk *in place*, same framing for every animation of a character.
2. Extract all frames losslessly to PNG (ffmpeg), uncropped.
3. Find the loop closure (SSIM/MSE against frame 1, with a minimum length), then pick 8–12 keyframes from inside the cycle (contacts/passing poses first, even in-betweens after).
4. Key the background (deterministic chroma key + despill for flat green; BiRefNet/RMBG/rembg only as rescue), remove specks, fix halos.
5. Normalize: one scale factor and one paste offset per character for ALL animations; pivot at the feet baseline; fixed cell size.
6. Downscale (area/Lanczos for HD; grid-recovery tools like proper-pixel-art/unfake for pixel art, with ONE palette shared across all frames).
7. Pack (Aseprite CLI / TexturePacker / ffmpeg tile / ImageMagick montage) with padding + extrude, grid or packed atlas within 2048/4096.
8. Import (Unity Aseprite Importer or Sprite Editor + Sprite Atlas; Godot SpriteFrames / Aseprite importer plugins; Phaser atlas + `anims.create`), choose ASTC/ETC2/BC7 compression.

---

## 1. Frame extraction: ffmpeg commands, resampling, range selection, cropping, and choosing which frames to keep

### Takeaway
Extract every source frame to lossless PNG first (no cropping, no early resampling), then *select* 8–12 frames by animation beats rather than blindly resampling 24→8/12 fps; use `fps=`/`select=` in ffmpeg only for quick drafts. Never crop tightly or recenter per frame at this stage — the full canvas is what keeps frames aligned.

### Cited Findings
- The LayrKits Sprite-Pipeline extraction script uses only system `ffmpeg`/`ffprobe` + Python stdlib; its default is "source-frame-passthrough" — extract every decoded frame in playback order — with optional `--fps` (constant-FPS sampling) and `--crop` (an ffmpeg crop expression); output naming `frame_%04d.png`; it writes an `extraction_report.json` including the exact ffmpeg command used. — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)
- Pitfall stated by LayrKits: "Do not crop tightly around the character. The full canvas is part of the alignment strategy." Frames keep the original canvas and are never cropped, recentered or moved during selection. — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)
- Frame-selection order recommended by LayrKits: (1) frame 1 = a playable start (ready stance or transition, not mid-swing); (2) final frame = clean recovery / handoff to idle; (3) key beats (anticipation, contact, impact, follow-through); (4) evenly spaced in-betweens. Remove blurry, malformed or duplicate frames; keep VFX frames. For 12f vs 24f versions keep the same start, end and main beats and add in-betweens for 24f. — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)
- LayrKits example of picking 12 frames from ~60 extracted frames (roughly every 5th frame, not exactly uniform): `python tools/select_frames.py --source-dir "<run-dir>/extracted/<character>/<animation>" --output-dir "<run-dir>/selected/<character>/<animation>/12f" --indices "1,6,11,17,22,27,32,38,43,49,54,60" --frame-prefix "<character>_<animation>_12f"`. It also builds a numbered contact sheet for review: `make_contact_sheet.py --cols 12 --cell-size 128 --image-size 112`. — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)
- The Sprite-Pipeline repo defaults to 24 frames when no frame count is specified and outputs a horizontal strip, per-frame cells, a preview image and a JSON validation report. — [LayrKits/Sprite-Pipeline (GitHub)](https://github.com/LayrKits/Sprite-Pipeline)
- A Kling-based skill describes the same chain: "Source Image → Kling AI Video → Frame Extraction → Sprite Sheet + CSS", extracting at 12 fps with ffmpeg from 2–5 s MP4s. — [TamerinTECH/claude-skill-klingai-animation](https://github.com/TamerinTECH/claude-skill-klingai-animation)
- ffmpeg sampling pattern used for sprite/contact sheets: `fps` samples, `scale` shrinks, `tile` lays out — e.g. `ffmpeg -i in.mp4 -vf "fps=1/10,scale=320:-1,tile=4x3" -frames:v 1 sheet.png`; order matters (sample → scale → tile). — [techearl: ffmpeg contact sheet](https://techearl.com/ffmpeg-contact-sheet-preview)
- ffmpeg `select` can pick frames by expression, e.g. I-frames: `ffmpeg -i file.avi -vf select='eq(pict_type\,I)','scale=128:72,tile=8x8' keyframes%03d.png`. — [FFmpeg-devel patch: working tile example](https://ffmpeg.org/pipermail/ffmpeg-devel/2013-April/142315.html)
- Official tile docs note `-vsync 0` "stops ffmpeg from duplicating output frames to match the original frame rate" when writing image sequences. — [FFmpeg 7.1 tile filter docs (mirror)](https://ayosec.github.io/ffmpeg-filters-docs/7.1/Filters/Video/tile.html)

### Inferences
- Constructed commands (standard ffmpeg filter syntax; verify on your build):
  - Inspect: `ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,nb_frames -of csv=p=0 clip.mp4`
  - Lossless dump of all frames: `ffmpeg -i clip.mp4 -vsync 0 frames/f_%04d.png` (PNG keeps the decoded frame exact; avoid JPG intermediates — compression ringing around the green edge makes keying worse).
  - Range by time: `ffmpeg -ss 1.25 -to 3.25 -i clip.mp4 -vsync 0 frames/f_%04d.png`; range by frame index: `-vf "select='between(n\,30\,77)'" -vsync 0`.
  - Quick resample 24→12 fps: `-vf fps=12` (or `select='not(mod(n\,2))'` to take every 2nd frame exactly, avoiding fps-filter rounding); 24→8: `select='not(mod(n\,3))'`.
  - Crop (only to drop a watermark band or dead canvas — and with ONE rectangle for every frame of every animation of that character): `-vf "crop=W:H:X:Y"`.
- Resampling by stride is a reasonable first draft, but AI video motion is not evenly timed (ease-in/out, hesitations), so stride sampling often misses the contact poses of a walk; beat-based picking (contacts, passing, high/low points) usually reads better at 8–12 frames.
- A walk cycle at 24 fps that completes in ~1 s gives ~24 frames per cycle; keeping 8 (every 3rd) or 12 (every 2nd) from *inside one detected cycle* (see §2) is the typical reduction. Playback fps in-engine should then be set to cycle_frames_kept / cycle_duration to preserve the original speed (e.g. 12 frames over 1 s → 12 fps; 8 frames → 8 fps).
- Veo clips from the Gemini app may carry a visible watermark in a corner; LayrKits' optional "clear a watermark box in each cell" step (x0=200,y0=236,x1=256,y1=256 in a 256 cell) shows practitioners handle this by clearing a fixed rectangle — keep the character out of that corner at generation time.

### Gaps
- I did not fetch ffmpeg's `fps`, `select`, `crop` or `mpdecimate` doc pages directly in this session; the constructed commands use standard syntax but defaults were not re-verified. `mpdecimate` (drops near-duplicate frames, useful because AI video often has static "hold" frames) is listed in the filter index, but its options were not retrieved.
- No source quantified how many frames practitioners keep per animation type (idle vs walk vs attack) for AI-video-derived sprites beyond LayrKits' 12f/24f variants.

---

## 2. Finding the loop point automatically (SSIM / perceptual hash / pixel difference)

### Takeaway
There is no dominant off-the-shelf "sprite loop finder"; the standard method is to compute a frame-to-frame similarity (MSE/SSIM/cosine on downscaled, alpha-masked frames) between the start frame and every candidate end frame, impose a minimum/maximum loop length, rank, then visually verify. Better still is to close the loop at generation time with first/last-frame conditioning, while watching for the "still video" failure mode.

### Cited Findings
- The Sprite-DX loop-segment-detection doc describes: for each (start, end) pair compute similarity between the end frames (MSE, cosine similarity or SSIM), optionally adjusted by motion energy/perceptual features, add a length penalty to discourage very short/long loops, rank by combined score, then human review/correction of indices. It states no state-of-the-art end-to-end loop detector existed as of 2025. No thresholds or code given. — [sprited/sprite-dx-data: video_loop_segment_detection.md](https://huggingface.co/datasets/sprited/sprite-dx-data/blob/main/docs/video_loop_segment_detection.md)
- Academic approach: compute a frame-to-frame distance matrix (SSD) and shift it so first and last frames are compared; same structure as SSIM-based search. — [arXiv 2011.02579: Improved Algorithm for Seamlessly Creating Infinite Loops](https://arxiv.org/pdf/2011.02579)
- If no clean cut exists, seam-hiding methods modify frames around the jump instead of searching for a better cut. — [Durrant & Brostow 2017, UCL Discovery](https://discovery-pp.ucl.ac.uk/id/eprint/10117777)
- `looplab`: a headless CLI (ffmpeg + Python 3.10+) that finds the most seamless loop in footage of repetitive motion from a static camera; outputs an MP4 plus ranked JSON candidates; it only finds cuts that already exist in the footage. — [skills.cat: looplab](https://skills.cat/skills/shihanqu/looplab)
- Closing the loop at generation time: agent-sprite-forge's fal.ai route (which includes Veo 3.1, Kling, Luma) "pins the last frame on every curated model", and pads the still to 16:9 for Veo. — [0x0funky/agent-sprite-forge](https://github.com/0x0funky/agent-sprite-forge)
- Pitfall: using the same image as both first and final frame can produce a still (non-moving) video; if so, drop the final-frame input. — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)
- Pitfall: if the last frames look too similar to the first, the animation "can seem stuck"; keep the best transition frame and remove the rest. — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)

### Inferences
- Practical loop-finder recipe (constructed, untested): load frames, composite on a neutral background or use the alpha mask, downscale to ~128 px, grayscale; for candidate end k in [min_len, N), score `S(k) = SSIM(f0, fk)`; to keep motion *direction* consistent (a walk's two passing poses look alike but move opposite ways), score windows instead: `mean(SSIM(f[-1+i], f[k-1+i]) for i in 0..2)` — this mirrors the "temporal filtering of the distance matrix" idea in video-texture literature. Take the best k; the cycle is frames `0..k-1` (exclude k itself, which duplicates frame 0 and causes a visible hitch/"stuck" beat — consistent with LayrKits' warning).
  ```python
  # sketch; pip install scikit-image pillow numpy
  from skimage.metrics import structural_similarity as ssim
  import numpy as np, glob
  from PIL import Image
  fs=[np.asarray(Image.open(p).convert("L").resize((128,128))) for p in sorted(glob.glob("frames/*.png"))]
  def win(a,b,r=1): return np.mean([ssim(fs[a+i],fs[b+i]) for i in range(-r,r+1) if 0<=a+i<len(fs) and 0<=b+i<len(fs)])
  start=0; cands=sorted(((win(start,k),k) for k in range(8,len(fs)-1)),reverse=True)[:5]
  print(cands)   # review top 5 visually; cycle = frames[start:k]
  ```
- Perceptual hashes (pHash/dHash via the `imagehash` package) are a fast pre-filter for candidate ends; SSIM/MSE on the masked silhouette is the better final ranker because the background is flat and contributes nothing. Comparing alpha masks (IoU of silhouettes) is a cheap, robust complement after keying.
- Search the start frame too: for an 8 s Veo clip the first ~0.5 s is often the model "settling" from the still; scanning (start, end) pairs, as Sprite-DX describes, typically yields a cleaner cycle than forcing start=0.
- If the best score is still visibly off, options are: (a) regenerate with first+last frame pinned, (b) use image generation to make 1–2 bridge frames (LayrKits recommends this for bridging animations as cheaper than re-running video), or (c) a short cross-fade is NOT acceptable for sprites (it creates ghost double-limbs) — cut, don't blend.

### Gaps
- No open-source repo found that is specifically a "sprite-cycle loop finder" with published thresholds; SSIM threshold values for "seamless" were not found in any source.
- No source compared SSIM vs pHash vs MSE specifically on AI-generated character clips.

---

## 3. Background removal / alpha: chroma key vs AI matting, flicker, halos, spill

### Takeaway
For a flat, deliberately generated `#00FF00` background, a deterministic chroma key + conservative despill is the most consistent (zero temporal flicker, because the same rule applies to every frame); AI matting (BiRefNet / RMBG 2.0 / rembg) is the rescue path for non-flat backgrounds and is per-frame, so it can flicker at fine edges. Video-native matting (RVM, MatAnyone2, SAM2Matting) is temporally stable but human-trained and/or non-commercially licensed. Watch licenses: RMBG 2.0 is non-commercial without a Bria agreement.

### Cited Findings
**Generation-side prevention**
- Generate on exact chroma green `#00FF00` (RGB 0,255,0); the character must not use that green anywhere, including glows and anti-aliasing; no shadows, floor, gradients or props; if the generated background is a soft/near-green gradient, flatten the border-connected background to exact `#00FF00` *before* animating. — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)

**Chroma key (ffmpeg)**
- `colorkey` (since FFmpeg 2.8) works on 8-bit RGB, setting alpha to 0 within a similarity radius of the key color. Options: `color` (default black), `similarity` (default 0.01, range 0.01–1.0), `blend` (default 0.0; higher = semi-transparent pixels near the key color). Doc examples: `ffmpeg -i input.png -vf colorkey=green out.png`; `colorkey=0x3BBD1E:0.3:0.2`. — [FFmpeg 7.1 colorkey docs (mirror)](https://ayosec.github.io/ffmpeg-filters-docs/7.1/Filters/Video/colorkey.html)
- `despill` options: `type` (green/blue), `mix`, `expand` (how much remaining spill is removed), `red`, `green` ("Use -1 for a greenscreen"), `blue` ("Use -1 for a bluescreen"), `brightness`, `alpha`; defaults not listed on the page (use `ffmpeg -h filter=despill`). — [FFmpeg 7.1 despill docs (mirror)](https://ayosec.github.io/ffmpeg-filters-docs/7.1/Filters/Video/despill.html)
- A community recipe for a PNG sequence with alpha: `colorkey=0x00FF00:0.3:0.1` → `frame_%04d.png`; it claims `chromakey` "composites rather than producing alpha" — [claudeskills: ffmpeg-color-grading-chromakey](https://claudeskills.info/skills/josiahsiegel/claude-plugin-marketplace/ffmpeg-color-grading-chromakey/). *Treat this claim as doubtful*: ffmpeg's `chromakey` does output an alpha plane (YUVA); what is documented is a bug that `chromakey` does not observe pre-existing alpha in the source frame — [FFmpeg trac #8724](https://trac.ffmpeg.org/ticket/8724).
- LayrKits' chroma rules (implemented in Python, not ffmpeg): pixels exact or near `#00FF00` within tolerance → alpha 0; **spill rule**: where green is high, red and blue are low and green ≫ both, edge pixels not removed get green clamped toward max(R,B); **be conservative** — don't remove pixels merely for containing some green (cyan weapon tips, green gems get damaged); remove tiny isolated components (specks). — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)
- LayrKits uses a separate "fallback matting" only when the background is off-white/gray and can't be regenerated: estimate background from border pixels, remove close matches, soft alpha edge; avoid it on clean green "since chroma removal is more deterministic." — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)

**AI per-image matting**
- rembg (MIT code; weights have own licenses): models include `u2net`, `u2netp`, `u2net_human_seg`, `silueta`, `isnet-general-use`, **`isnet-anime`** (anime character segmentation), `sam`, `birefnet-general`, `birefnet-general-lite`, `birefnet-portrait`, `birefnet-dis`, `birefnet-hrsod`, `birefnet-cod`, `birefnet-massive`, and **`bria-rmbg` (now the default, ~1.02 GB, 1024×1024, slower; commercial use requires a paid agreement)**. Batch: `rembg p path/to/input path/to/output` (watch mode `-w`; decontamination `-dc`); `-a` alpha matting is slow and can fail to converge (falls back to decontaminated cutout); `-vm` ViTMatte learned matting; `-ppm` binarizes the mask. For batches, create one session and reuse it (`session = new_session()`, `remove(input, session=session)`). — [danielgatis/rembg](https://github.com/danielgatis/rembg)
- BiRefNet (MIT repo): weights include general (1024², ~17 FPS / 3.45 GB VRAM on RTX 4090), BiRefNet_HR (2048², Feb 2025), BiRefNet_HR-matting (Feb 2025), BiRefNet_dynamic (256–2304, Mar 2025), BiRefNet-matting (trimap-free, Oct 2024), BiRefNet_lite-2K. GPU `refine_foreground` added Jun 2025 (~80 ms on a 5090); SDPA memory reduction Sep 2025; no 2026 news entries. Repo notes RMBG-2.0 (trained on BiRefNet) is non-commercial. ComfyUI integrations exist (Comfy-Org/BiRefNet, ZHO's node "especially for video"). No temporal-consistency discussion. — [ZhengPeng7/BiRefNet](https://github.com/ZhengPeng7/BiRefNet)
- RMBG 2.0 is built on the BiRefNet architecture with Bria's own dataset; Bria's own benchmark claims 90% vs 85% for BiRefNet (vendor benchmark, image-level, not video). — [Bria blog](https://blog.bria.ai/brias-new-state-of-the-art-remove-background-2.0-outperforms-the-competition); [Bria-AI/RMBG-2.0](https://github.com/Bria-AI/RMBG-2.0)
- Frame-by-frame image matting "may inevitably cause severe flickering artifacts for moving fine details"; per-frame mattes "visibly vibrate and flicker" when reassembled into video; recurrent/temporal models reduce this. — [RVM paper, arXiv 2108.11515](https://arxiv.org/pdf/2108.11515); [Temporally Coherent Person Matting, arXiv 2109.04843](https://arxiv.org/pdf/2109.04843)

**Video-native matting**
- Robust Video Matting (RVM) is "specifically designed for robust human video matting" (recurrent, no trimap); outputs `png_sequence` with separate alpha/foreground; `downsample_ratio` 0.25 for HD, 0.125 for 4K; GPL-3.0; weights v1.0.0, last news Nov 2021. — [PeterL1n/RobustVideoMatting](https://github.com/PeterL1n/RobustVideoMatting)
  - Example: `convert_video(model, input_source='input.mp4', output_type='png_sequence', output_composition='out_dir', output_alpha='pha.mp4', downsample_ratio=None, seq_chunk=12)`.
- MatAnyone2: target-specified video matting from a first-frame mask with memory propagation for stable core regions + fine edges (secondary-source description); a ComfyUI extension pairs a SAM editor (ViT-H/L/B) with MatAnyone2 propagation. — [CSDN write-up](https://gitcode.csdn.net/69f1e96c0a2f6a37c5a6d554.html); [ComfyUI node: MatAnyone2 Interactive SAM](https://comfy.icu/node/MatAnyoneInteractiveSAM)
- SAM2Matting (arXiv 2606.27339, June 2026): SAM2/SAM3 tracker for temporal consistency + matting heads for detail; trained on images only, reports SOTA video matting; HF demo uses SAM2.1-Tiny under CC-BY-NC-SA-4.0 (non-commercial). — [arXiv 2606.27339](https://arxiv.org/abs/2606.27339); [SAM2Matting demo](https://fudancvl-sam2matting.hf.space/)
- No source tested MatAnyone/SAM 2 on non-human cartoon characters. — (search result summary; see Gaps)

**Packing-side halo control**
- TexturePacker "ReduceBorderArtifacts" (alpha bleeding) gives transparent pixels the color of the nearest solid pixel, "which can remove dark halos"; "PremultiplyAlpha" multiplies color by alpha (some frameworks require it). — [TexturePacker texture settings](https://www.codeandweb.com/texturepacker/documentation/texture-settings)

### Inferences
- Constructed ffmpeg keying chain (tune on single frames first): `ffmpeg -i f_%04d.png -vf "colorkey=0x00FF00:0.25:0.08,despill=type=green,format=rgba" keyed/f_%04d.png`. Lower `similarity` leaves green fringe; higher eats into the character; `blend>0` gives soft edges but leaves semi-transparent green-tinted pixels that then need despill. For pixel art, prefer `blend=0` (hard edges) because soft alpha gets destroyed by palette reduction anyway.
- Video-model output is H.264/H.265 with 4:2:0 chroma subsampling, so the green edge is smeared over ~2 px of chroma — this is the root cause of the 1–2 px green/dark fringe even on a "perfect" `#00FF00` background. Mitigations: key at full resolution *then* downscale (downscaling averages the fringe away), erode alpha by 1 px (`ffmpeg ... alphaextract` / ImageMagick `-morphology Erode`) for hard-edged styles, and despill on the remaining edge.
- Ranking for consistency across frames on a flat background: deterministic chroma key (no flicker by construction) > video-native matting with a first-frame mask (MatAnyone2/SAM2-based; temporal memory) > per-frame BiRefNet/RMBG/isnet-anime (best single-frame edges on messy backgrounds, but edge jitter frame-to-frame). A hybrid that works well in practice: AI mask → binarize/threshold → median-filter the alpha over time (e.g. 3-frame temporal median on the mask) → re-apply.
- For anime/cel-shaded characters, rembg's `isnet-anime` is the most domain-appropriate free model listed; `bria-rmbg` being rembg's new default matters for licensing — a studio shipping a commercial game must explicitly pick a commercially usable model (`birefnet-*`, `isnet-*`, `u2net`) or license RMBG.
- Hair, capes, smoke or glows that are semi-transparent cannot be cleanly recovered from a green background by keying alone; generate those effects as separate overlay animations (LayrKits recommends generating dust/wind as separate overlays for jump/land).

### Gaps
- No head-to-head benchmark of BiRefNet vs RMBG 2.0 vs isnet-anime on stylized/cartoon characters, nor any measurement of frame-to-frame alpha flicker for these models, was found.
- RMBG 2.0's exact license text (CC BY-NC 4.0 per common knowledge) was not fetched; sources here only state "non-commercial / paid agreement required for commercial use".
- Default values for ffmpeg `despill` were not retrieved.

---

## 4. Stabilization and alignment: pivot/feet, consistent scale across animations, in-place vs root motion, fixed cell size

### Takeaway
The robust approach is "preserve canvas": apply the same scale and the same paste offset to every frame (and every animation of the character), never auto-center or bottom-align per frame, and set the pivot (feet) once in the engine. Generate locomotion *in place* with a locked camera; per-frame trimming is fine only if the packer stores the original offsets (TexturePacker "Trim" / Aseprite JSON `spriteSourceSize`).

### Cited Findings
- LayrKits layout mode `preserve-canvas`: "Scale the whole source canvas into each cell with the same scale and paste location. Do not add per-frame bottom, ground-line, or bounding-box alignment." Output cells are transparent 256×256; 12 frames → 3072×256 strip; 24 → 6144×256. — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)
- LayrKits promotion checks: sheet size equals frame_count×256 by 256; scale and paste location identical across frames; no clipped weapon/limb/cape/effect; motion-pop and edge-contact warnings checked visually; apparent scale matches the rest of the character set. The validation report includes per-frame canvas/paste data, edge-alpha counts, adjacent-frame silhouette differences, duplicate and motion-pop warnings, edge-contact warnings. The pipeline intentionally does not align feet; engine origin is set in engine import settings. — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)
- Generation constraints for alignment: full body, centered, nothing in the outer 20–30% of the canvas; idle ≈ 40–50% of canvas height; locked camera, no zoom/pan/rotation/cuts/shake; character stays centered at the same size; for walks "use walk-in-place wording and forbid dolly movement or size change". — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)
- Kling skill likewise requires keeping the character centered with no camera movement before extraction. — [TamerinTECH/claude-skill-klingai-animation](https://github.com/TamerinTECH/claude-skill-klingai-animation)
- TexturePacker trim modes: **Trim** removes transparent borders "but the sprite keeps its original size and anchor point"; **Crop, keep position** shrinks but preserves position so anchor is the same; **Crop, flush position** sets position to 0/0 "so placement changes with the amount trimmed" (breaks animation alignment); Polygon outline for tighter packing; transparency threshold default 1. — [TexturePacker texture settings](https://www.codeandweb.com/texturepacker/documentation/texture-settings)
- Aseprite CLI: `--trim` trims each frame (for `--sheet`), `--trim-sprite` trims the whole sprite (uniform across frames), `--inner-padding N` adds pixels inside each frame. — [Aseprite CLI docs](https://www.aseprite.org/docs/cli/)
- ImageMagick: per-frame `-trim +repage` misaligns frames that need a shared origin; for a shared bounding box use `-layers trim-bounds` (e.g. `convert sprite*.png -trim -layers trim-bounds -dispose Background -coalesce +append sprite_sheet.png`) or compute one common crop from a flattened copy of all frames. — [ImageMagick forum: Crop sprites for minimal spritesheet size](https://magick.imagemagick.org/viewtopic.php?p=153008)

### Inferences
- Even with a "locked camera" prompt, video models drift (slow zoom, a few px of slide). Measure drift after keying: compute per-frame alpha bounding box bottom (lowest opaque row = feet contact) and horizontal centroid of the lower-body mask. If the foot-contact baseline varies by more than ~1–2 px *on contact frames* or the centroid slides monotonically, apply a correction — but a *single smooth* correction (linear fit over the clip), not per-frame snapping, otherwise you remove legitimate bob (the up/down of a walk is part of the motion).
- Root motion: if the character translated (didn't walk in place), track the planted foot across contact frames to estimate ground speed, subtract it to make it in-place, and give the engine the speed value (px per cycle) so the controller moves the character at the speed the feet imply — otherwise feet "skate". Regenerating with explicit in-place wording is usually cheaper than reconstructing root motion.
- Consistent scale across idle/run/attack: (1) generate every animation from the same base image at the same framing (LayrKits' 40–50% height guidance); (2) compute ONE scale factor per character (e.g. from idle height → target sprite height in px) and apply it to all animations; never "fit to cell" per animation — an attack with an extended sword would otherwise shrink the whole character. (3) Choose the cell size from the union bounding box across ALL animations (largest swing/jump) plus margin, or use a packed atlas with trim + stored offsets so cells can differ while the pivot stays fixed.
- Pivot convention: put the pivot at the feet baseline, horizontally centered on the body (not on the bounding box, which shifts when an arm or weapon extends). With "preserve canvas" this is a single constant (e.g. x=0.5, y=feet_row/cell_h) for every frame, which can be entered once in Unity's Sprite Editor (custom pivot) or as an offset on Godot's AnimatedSprite2D/Sprite2D.

### Gaps
- No open-source tool found that automatically stabilizes AI-generated sprite clips by foot contact; the feet-baseline/centroid approach above is my synthesis, not a cited tool.
- No source gave target sprite heights per genre/resolution for AI-derived sprites.

---

## 5. Downscaling and style: HD sprites vs pixel-art conversion, quantization, and frame-to-frame flicker

### Takeaway
For HD/painted sprites, key at source resolution, then downscale with an averaging filter (area/Lanczos) — never nearest. For pixel art, don't just nearest-neighbor shrink AI frames: use a grid-recovery + palette tool (proper-pixel-art, unfake.js/unfake.py, Phaser Tidy Pixel Art) and lock ONE grid and ONE palette across all frames of the animation (and ideally the whole character), which is the key to avoiding palette flicker. Expect hand cleanup in Aseprite after.

### Cited Findings
- proper-pixel-art (KennethJAllen; Python; MIT; PyPI `proper-pixel-art`; references a 2.0.0 config change; ~415 stars, last push Apr 25 2026): reconstructs the true pixel grid — trim/alpha cleanup → 2× nearest upscale → Canny edges + morphological closing → probabilistic Hough lines, clustered and snapped → estimate pixel width (validated by within-cell color variance) → one representative color per cell. CLI: `ppa <input> -o <out> -c <palette_size> -s <scale> [-t]`, e.g. `ppa assets/blob/blob.png -c 16 -s 25`; `ppa web` for a local UI; `--color-method dominant|palette`; `-w` manual pixel width; `-t` transparent. **Animations: video and GIF inputs are detected by extension; the tool samples frames (`-n`, default 8) to fix one grid and one palette, then applies them to every frame "so the output stays consistent without flicker"**; output `-f mp4|gif`. — [KennethJAllen/proper-pixel-art](https://github.com/KennethJAllen/proper-pixel-art); stats from [sourcepulse](https://www.sourcepulse.org/projects/13911015)
- unfake.js (jenissimo; MIT; core in Rust → WASM + native CLI): scale detection (`runs` / `edge` / `auto`, handles fractional grids, elastic grid for drifting cells) → grid snapping → downscale with `dominant`/`median`/`mode`/`mean`/`qvote`/content-adaptive (to avoid new colors/blur) → quantize with libimagequant (fixed custom palettes supported) → optional morphological cleanup, jaggy cleanup, alpha binarization. CLI commands `unfake detect | snap | downscale | quantize` with fixed palettes, reserved chroma color, JSON pipeline manifest. Demo: jenissimo.itch.io/unfaker. — [jenissimo/unfake.js](https://github.com/jenissimo/unfake.js)
- In a test, the Unfaker demo rejected a high-resolution input (had to be resized first) and returned a 16-color palette. — [Gigazine (Dec 2025)](https://gigazine.net/gsc_news/en/20251202-unfaker-fix-ai-pixel-art)
- unfake.py (painebenjamin; `pip install unfake`; needs Rust toolchain to build from source): dominant/median/mode/content-adaptive downscaling, alpha binarization, morphological ops, jaggy-edge removal. — [PyPI: unfake](https://pypi.org/project/unfake/)
- Phaser's "Tidy Pixel Art" tool resolves blurry/anti-aliased/over-detailed AI output down to a real pixel grid. — [Phaser: Tidy Pixel Art](https://phaser.io/tools/tidy-pixel-art)
- Video-to-pixel converters: PXLY (open source, pip; palette size, resolution, frame rate); Pixelwise (macOS; "temporal coherence to reduce flickering", GIF/APNG export); DotChange (Windows); pxanima (hackathon project, spritesheet export on roadmap). — [PyPI: pxly](https://pypi.org/project/pxly/); [Pixelwise (itch.io)](https://pixlosopher.itch.io/pixelwise); [DotChange (itch.io)](https://eye-factory.itch.io/dotchange); [pxanima (itch.io)](https://jerzakm.itch.io/pxanima)
- PixelLab and Retro Diffusion are primarily generators, not converters of existing video: PixelLab offers skeleton animation, 4/8-direction rotation, tilesets and an Aseprite plug-in; Retro Diffusion's RD Animation produces sprite sheets at 48×48 (four-angle walking) or 32×32; Retro Diffusion reported as an Aseprite extension ($65 full / $20 Lite — may have changed). No source showed either converting existing video to pixel art. — [Scenario: Retro Diffusion essentials](https://help.scenario.com/en/articles/retro-diffusion-models-the-essentials/); [Cinevva: AI pixel art generators 2026](https://app.cinevva.com/de/guides/ai-pixel-art-generators) (SEO/vendor-style comparison — verify prices)
- LayrKits notes tiny pixel sprites may need a transition pose image first, and "simple pixel sprites" need short, literal prompts. — [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet)

### Inferences
- HD path (constructed): key at 1080p → crop with the fixed per-character rectangle → `ffmpeg -i keyed/f_%04d.png -vf "scale=iw/4:ih/4:flags=area" small/f_%04d.png` (or `flags=lanczos`; area is the safer choice for large reductions since it doesn't ring). Downscaling must happen on *premultiplied* or alpha-bled images, or transparent pixels' (green/black) RGB bleeds into the edge — apply despill/alpha-bleed before scaling, or use a tool that handles alpha correctly.
- Pixel-art path: (1) key + fix alignment at full res; (2) downscale to a coarse intermediate (e.g. 4–8× target) with area; (3) run proper-pixel-art in *animation mode* (feed an assembled GIF/MP4 of the cycle so it samples frames to lock one grid + palette) or unfake with a *fixed palette* shared by every frame; (4) binarize alpha (no semi-transparency in pixel art); (5) Aseprite cleanup pass (stray pixels, outline continuity, sub-pixel jitter). Per-frame independent quantization is the #1 cause of "boiling"/flicker in converted animations.
- Choose the palette once per character (or game) and reuse it for every animation, so idle/run/attack match; unfake's and proper-pixel-art's fixed-palette options support this.
- Plain nearest-neighbor from 1080p to e.g. 64 px aliases arbitrarily (each output pixel picks one source sample), producing shimmering edges across frames; it is only appropriate *after* the art already sits on a clean grid (e.g. for integer *upscaling* previews).
- Remaining sub-pixel jitter in pixel art (features moving 1 px back and forth) is best fixed manually in Aseprite or by reducing frame count — fewer, held frames read as more "authored".

### Gaps
- Pixel It (pixelit) and Retro Diffusion's standalone "pixelizer" were not verified in this session; no current docs retrieved.
- No source benchmarked proper-pixel-art vs unfake on animated AI sprites.
- PixelLab's current feature set for importing existing animations was not verified from its own site.

---

## 6. Packing: TexturePacker, Aseprite, Free Texture Packer, ShoeBox, ImageMagick, ffmpeg tile — grid vs atlas, trim, padding/extrude, POT, metadata

### Takeaway
Use Aseprite CLI or TexturePacker for production atlases (trim with stored offsets, ≥2 px shape padding, 1 px extrude, max 2048/4096, JSON hash/array or engine-native export); ffmpeg `tile` and ImageMagick `montage` are fine for fixed-grid sheets but produce no metadata and need explicit transparent backgrounds. Avoid very long single-row strips — they exceed max texture sizes fast.

### Cited Findings
**Aseprite CLI** (docs)
- Relevant options: `-b/--batch`; `--sheet <png>`; `--data <json>`; `--format json-hash` (default) or `json-array`; `--sheet-type horizontal|vertical|rows|columns|packed`; `--sheet-pack`; `--sheet-width/--sheet-height`; `--sheet-columns/--sheet-rows`; `--trim`; `--trim-sprite`; `--extrude` (duplicates edge pixels by 1 px); `--shape-padding N`; `--border-padding N`; `--inner-padding N`; `--merge-duplicates`; `--ignore-empty`; `--scale <factor>`; `--split-tags`; `--list-tags`; `--filename-format` with `{title}`, `{tag}`, `{frame}`, `{extension}`. — [Aseprite CLI docs](https://www.aseprite.org/docs/cli/)
- Verbatim examples: `aseprite -b animation.ase --sheet sheet.png --data sheet.json`; `aseprite -b *.ase --sheet-pack --sheet atlas-bestfit.png --data atlas-bestfit.json`; `aseprite -b *.ase --sheet-pack --sheet-width=1024 --sheet-height=1024 --sheet atlas-1024x1024.png --data atlas-1024x1024.json`; `aseprite -b original.png --scale 2 --save-as image-x2.png`; `aseprite -b --oneframe frame1.png --save-as frame1.pcx` (`--oneframe` exists because Aseprite otherwise treats `frame1.png, frame2.png...` as a sequence). — [Aseprite CLI docs](https://www.aseprite.org/docs/cli/)

**TexturePacker** (docs)
- Max size default 2048; size constraints POT / MultipleOf4 / AnySize; for ASTC/PVRTC/ETC1/ETC2 it auto-enforces format constraints. Automatic Multipack (`--multipack`, filename `{n}`/`{n1}`). Extrude "repeats the sprite's pixels at the border. Sprite's size is not changed" (reduces flicker). Shape padding: "Use a value of at least 2 to avoid dragging in pixels from neighbor sprites when using OpenGL rendering." Border padding around the sheet. Alpha: ClearTransparentPixels (improves packing and identical-sprite detection), ReduceBorderArtifacts (alpha bleeding vs dark halos), PremultiplyAlpha. Formats: PNG32, PNG8 (≤256 colors), PVR/KTX/KTX2/ASTC/BASIS/DDS; quality defaults ETC1/2 = 70, ASTC = 2 (0–4), BASIS = 2. Scaling variants with `{v}` and `--force-identical-layout`. Trim modes as in §4. — [TexturePacker texture settings](https://www.codeandweb.com/texturepacker/documentation/texture-settings)

**ffmpeg tile** (FFmpeg 7.1.5 docs)
- Options: `layout` COLSxROWS (default 6x5), `nb_frames` (default 0 = full grid), `margin` (0–1024, default 0), `padding` (gap between frames, default 0), `color` (unused cells; **default black**), `overlap`, `init_padding`. Example: `tile=3x2:nb_frames=5:padding=7:margin=2`; `ffmpeg -skip_frame nokey -i file.avi -vf 'scale=128:72,tile=8x8' -an -vsync 0 keyframes%03d.png`. — [FFmpeg 7.1 tile docs (mirror)](https://ayosec.github.io/ffmpeg-filters-docs/7.1/Filters/Video/tile.html)
- Use `-frames:v 1` to write a single sheet image. — [techearl](https://techearl.com/ffmpeg-contact-sheet-preview)

**ImageMagick montage**
- `magick montage "test/*.png" -geometry +0+0 -tile 3x -background none spritesheet_3x_128.png` (3 columns, rows grow, transparent canvas); in IM7 use `magick montage`, bare `montage` is IM6 syntax; adding `-trim +repage` shrinks cells but misaligns frames needing a shared origin. — [ImageMagick forum](https://magick.imagemagick.org/viewtopic.php?p=153008)
- A Windows montage build was reported to drop transparency regardless of background color (unconfirmed bug) — check version and PNG output. — [Factorio forums: spritesheets with Blender](https://forums.factorio.com/viewtopic.php?p=493410)

### Inferences
- Constructed: transparent ffmpeg grid sheet from 12 keyed RGBA frames (4 columns): `ffmpeg -framerate 12 -i cells/c_%02d.png -vf "tile=4x3:padding=2:margin=2:color=black@0.0,format=rgba" -frames:v 1 sheet.png`. Because tile's `color` defaults to opaque black, always set a zero-alpha color (and keep the pipeline RGBA) or empty cells/padding become black. ffmpeg tile produces no JSON; engines then slice by fixed cell size (Phaser `load.spritesheet`, Godot hframes/vframes, Unity Grid By Cell Size), so padding/margin must be declared there too.
- Constructed Aseprite import of a PNG sequence → sheet + JSON: `aseprite -b frames/f_0001.png --sheet-type rows --sheet-columns 6 --trim --shape-padding 2 --border-padding 2 --extrude --format json-array --sheet hero_walk.png --data hero_walk.json` (Aseprite loads `f_0001.png…f_0012.png` as one sprite when the numbered sequence is passed; verify ordering). To get named animations (tags) into JSON for Phaser `createFromAseprite`/Godot/Unity importers, build a `.aseprite` file with tags per animation (manually or via Lua script) and export from that.
- Grid vs packed atlas: grid (uniform cells, no trim) is simplest to import and debug and keeps the pivot trivially constant, but wastes 40–70% of the texture on transparent margin for a walking character. Packed atlas with trim saves memory but REQUIRES the metadata (original size + offset) to be honored by the importer; TexturePacker "Trim" mode or Aseprite `--trim` with JSON `spriteSourceSize` does this.
- Strip length pitfall: LayrKits' 24-frame horizontal strip at 256 px cells is 6144×256 — wider than TexturePacker's default max (2048) and the 4096 limit common on mobile GPUs. Prefer `rows`/`columns`/`packed` layouts.
- Free Texture Packer and ShoeBox are viable free alternatives (both export JSON hash/array-style atlases), but I did not verify their current versions/docs in this session.
- Shared atlas per character: put all of one character's animations in one atlas (or multipack set) so the engine binds one texture per draw; padding ≥2 px + extrude 1 px prevents bilinear/mipmap bleeding; for pixel art with point filtering and no mipmaps, 1–2 px padding is enough but extrusion still helps at fractional camera positions.

### Gaps
- TexturePacker's current version number and its JSON hash vs array schema details were not fetched (data-format page not retrieved). Free Texture Packer, ShoeBox and ezgif's sprite-sheet maker were not verified.
- No authoritative recommendation found on padding values for compressed (ASTC block) atlases beyond Unity's "padding rounded up to a multiple of four when compressed" (see §8).

---

## 7. Engine import: Unity, Godot 4, Phaser 3/4 — recommended formats

### Takeaway
Easiest paths: Unity → keep a `.aseprite` file and use the 2D Aseprite Importer (generates sprites, clips and a read-only Animator Controller), or PNG sheet + Sprite Editor slicing + Sprite Atlas; Godot 4 → SpriteFrames "Add frames from a Sprite Sheet" on AnimatedSprite2D (or Aseprite Wizard / dot Aseprite Importer plugins); Phaser → texture atlas JSON (TexturePacker/Aseprite) + `anims.create` or `createFromAseprite`.

### Cited Findings
**Unity**
- 2D Aseprite Importer imports `.ase/.aseprite` as an asset; generates an Animator Controller when the file has >1 frame, Import Mode = Animated Sprite and Animation Clip is checked; the controller is read-only (FAQ explains modification). Package 1.2.x supports Unity 6.1; 1.1.x/1.0.x support Unity 6.0, 2022.3, 2021.3 (needs 2021.3.15f1+); included in recent 2D / 2D URP templates. — [Unity 2D Aseprite Importer manual](https://docs.unity3d.com/Packages/com.unity.2d.aseprite@1.1/manual/index.html)
- Unity atlas packing (`Texture2D.PackTextures`, Unity 6.x docs): supported compressed inputs ARGB4444, ETC, ETC2, DXT1, DXT5, BC7, ASTC 4x4; mixing unrelated formats (e.g. BC7 with ASTC 4x4) falls back to RGBA32; mipmaps + padding > 0 → uncompressed atlas; compressed atlas padding rounded up to a multiple of 4; PVRTC deprecated — use ASTC or ETC. — [Unity 6 Texture2D.PackTextures](https://docs.unity.cn/6000.0/Documentation/ScriptReference/Texture2D.PackTextures.html)

**Godot 4** (docs are Godot 4.7 stable)
- AnimatedSprite2D: SpriteFrames → "Add frames from a Sprite Sheet" → set horizontal/vertical grid (example 4×2) → select frames → rename animation → set Speed (FPS) (example uses 10 because the default was too slow). Alternative: Sprite2D with `Hframes`/`Vframes`/`Frame` + AnimationPlayer keyframing `frame` (example 6 frames, 0.6 s length, loop on). `play()` applies on next process; call `advance(0)` after `play()` to avoid a one-frame glitch when also changing flip etc. — [Godot 4.7 docs: 2D sprite animation](https://docs.godotengine.org/en/stable/tutorials/2d/2d_sprite_animation.html)
- Aseprite Wizard (Godot 4): imports to AnimationPlayer, AnimatedSprite2D/3D or SpriteFrames; each Aseprite tag → animation; ms frame durations converted; layer regex filtering; slices; only needed during development. — [Godot Asset Library: Aseprite Wizard](https://godotengine.org/asset-library/asset/edit/16988)
- dot Aseprite Importer (DRS90; Godot 4.7 + Aseprite 1.3+; MIT): turns `.aseprite` into SpriteFrames with one animation per tag; tags ending `_loop` loop; frames packed into one lossless trimmed texture with duplicates stored once; drag onto AnimatedSprite2D's Sprite Frames and `play("run")`. — [Godot Asset Store: dot Aseprite Importer](https://store.godotengine.org/asset/drs90/dot-aseprite-importer/)
- Godot 4 Aseprite Importers (jwthomp-experiments) for Aseprite 1.3+, requires setting the Aseprite executable path in Project Settings. — [GitHub: jwthomp-experiments](https://github.com/jwthomp-experiments/ClickerFunTime)

**Phaser** (site lists v4.1.0 as current API docs)
- `this.anims.create({ key: "walk", frames: this.anims.generateFrameNames("hero", { prefix: "walk-", start: 1, end: 4, zeroPad: 2 }), frameRate: 8, repeat: -1 })` (frameRate default 24; repeat −1 = forever); spritesheet-style `generateFrameNumbers("mummy", { start: 0, end: 2 })`; Aseprite: `this.anims.createFromAseprite("hero")` or with tag list `["idle","run"]`, optionally scoped to a sprite. Aseprite JSON loaded as an atlas works with `createFromAseprite`. — [Phaser docs: Animations](https://docs.phaser.io/phaser/concepts/animations)
- TexturePacker supports Pixi/Phaser cache busting (`--enable-cache-busting`). — [TexturePacker texture settings](https://www.codeandweb.com/texturepacker/documentation/texture-settings)

### Inferences
- Recommended per engine (synthesis):
  - **Unity 6.x**: Option A — author/collect frames into a tagged `.aseprite` and let the 2D Aseprite Importer generate clips (fastest iteration, re-import on change). Option B — PNG grid sheet → Texture Type Sprite (2D and UI), Sprite Mode Multiple, Sprite Editor → Slice → Grid By Cell Size with matching padding/offset, custom pivot at the feet; add a Sprite Atlas per character; Filter Mode Point + Compression None/high-quality for pixel art. TexturePacker also exports a Unity-specific format (via its importer) that preserves trimmed pivots.
  - **Godot 4.7**: PNG grid sheet → SpriteFrames "Add frames from a Sprite Sheet" is zero-dependency; for many animations use Aseprite Wizard or dot Aseprite Importer to avoid manual frame picking. For pixel art set the project's default canvas texture filter to Nearest.
  - **Phaser 3/4**: TexturePacker "Phaser" JSON (hash) or Aseprite JSON via `load.atlas(key, png, json)`/`load.aseprite`, then `anims.create` / `createFromAseprite`; a uniform grid can use `load.spritesheet(key, png, { frameWidth, frameHeight, margin, spacing })`.
- Set playback fps from the selection, not the source: if 12 frames were picked from a 1.0 s cycle, play at 12 fps; if 8 frames, 8 fps (or vary per-frame durations in Aseprite to restore the original timing of uneven AI motion).

### Gaps
- Unity's Sprite Editor/Sprite Atlas manual pages and the default Sprite Atlas max size were not fetched; Unity specifics in the Inferences (Grid By Cell Size, Point filter, Sprite Mode Multiple) are from general knowledge, not verified this session.
- Phaser's loader docs (`load.atlas`, `load.multiatlas`, `load.aseprite`, `load.spritesheet` options) were not on the fetched page; the loader calls above are from general knowledge.
- Godot texture-filter guidance for pixel art was not on the fetched page.

---

## 8. File size and performance: memory budgets, compression (ASTC/ETC2/BC7), atlas limits, mobile, frame-count ceilings

### Takeaway
Texture memory is width × height × bytes-per-pixel regardless of PNG file size: a 2048² RGBA32 sheet is 16 MiB in VRAM; ASTC 4x4 or ETC2 RGBA8 cut that to 4 MiB (8 bpp). Keep atlases at ≤2048² for broad mobile safety (4096² on modern devices/desktop), use ASTC on mobile (ETC2 fallback), BC7 on desktop, and treat frame count × cell area as the budget lever — AI video tempts teams to ship 24+ frames per cycle at HD, which is usually unnecessary.

### Cited Findings
- ETC2 RGBA8 is 8 bits/pixel (256×256 = 64 KB); ETC2 RGB is 4 bpp (256×256 = 32 KB). — [Unity 2017.1 Android texture docs](https://docs.unity.cn/ru/2017.1/Manual/class-TextureImporterAndroid.html)
- ASTC uses a fixed 128-bit block: 4x4 = 8 bpp (256×256 = 64 KB) down to 12x12 ≈ 0.89 bpp. — [Unity iOS texture docs](https://docs.unity3d.com/es/2018.4/Manual/class-TextureImporterIos.html)
- Unity Learn: on mobile, ASTC is generally recommended; 5x5 or 6x6 is "a good starting point"; ETC/ETC2 for older iOS A7 devices; Max Size can be overridden per platform; Fast compression during development, Best for release. — [Unity Learn: Texture Size, Color Space, and Compression](https://learn.unity.com/tutorial/texture-size-color-space-and-compression-6266)
- If a device doesn't support the texture format, Unity decompresses to RGBA32 and keeps both in memory. — [Unity Learn](https://learn.unity.com/tutorial/texture-size-color-space-and-compression-6266)
- Most modern Android GPUs with OpenGL ES 3.1 or Vulkan support ASTC; ETC2 is available on any device with Vulkan or GLES 3.0; for sprites Unity can split into two ETC1 textures (RGB + alpha) for devices without ETC2 alpha. — [Unity 2022.2 texture import overrides](https://docs.unity3d.com/cn/2022.2/Manual/class-TextureImporterOverride.html)
- Atlas compression constraints in Unity (mixed formats → RGBA32 fallback; mipmaps + padding → uncompressed; compressed padding rounded to multiple of 4). — [Unity 6 Texture2D.PackTextures](https://docs.unity.cn/6000.0/Documentation/ScriptReference/Texture2D.PackTextures.html)
- TexturePacker default max texture size 2048; auto-enforces ASTC/ETC/PVRTC dimension constraints; ASTC quality default 2 (0–4). — [TexturePacker texture settings](https://www.codeandweb.com/texturepacker/documentation/texture-settings)
- matheusobf/video-to-spritesheet advertises "memory safety constraints" and 4K support, and extracts at 5/10/15/24/30/60 fps — indicating practitioners hit sheet-size limits when converting video directly. — [matheusobf/video-to-spritesheet](https://github.com/matheusobf/video-to-spritesheet)

### Inferences
- Worked budget examples (arithmetic): 2048×2048 = 4,194,304 px → RGBA32 16 MiB; ASTC 4x4 / ETC2 RGBA8 4 MiB; ASTC 6x6 ≈ 1.8 MiB (3.56 bpp). Mipmaps add ~33% (sprites in 2D usually disable mipmaps). A 12-frame walk in 512×512 cells = 12 MiB RGBA32 (fits a 2048×2048 sheet as 4×3 = 16 cells, leaving room for 4 more frames); the same walk at 256×256 cells = 3 MiB RGBA32 / 0.75 MiB ASTC 4x4.
- A character with idle (8) + walk (12) + run (10) + attack (10) + hurt/death (12) ≈ 52 frames at 256² fits one 2048² atlas (64 cells) — a practical target "one atlas per character". At 512² cells that becomes ~4 sheets (16 cells each) → reduce cell size or frame count.
- When frame count is too high: if a cycle needs >16 frames at the target playback rate to look smooth, it's usually better to (a) lower cell resolution, (b) drop to 8–12 frames with authored per-frame durations, or (c) for very large hero animations consider skeletal (Spine / Unity 2D Animation) instead of flipbook. Mobile 2D games commonly budget a handful of 2048² atlases resident at once; exact budgets are device- and game-specific.
- Compression choice for sprites: ASTC 4x4 (8 bpp) is the quality choice for sharp-edged sprites with alpha; 6x6 can blur outlines and create block artifacts at alpha edges — test. For pixel art, prefer uncompressed RGBA32 (or lossless) with point filtering because block compression smears hard pixel edges; pixel sheets are small enough that this is affordable. Desktop: BC7 (8 bpp, high quality) for RGBA.
- PNG file size on disk/download is not the runtime cost; ship PNG (or KTX2/Basis for web/download size) but budget VRAM by the GPU format.

### Gaps
- No authoritative, current (2026) per-device memory budget figures for 2D sprite atlases on mobile were found; the "one 2048 atlas per character" heuristic is my synthesis.
- BC7 specifics were not retrieved from a primary source in this session.
- Max texture size support statistics (share of devices supporting 4096/8192) were not found.

---

## 9. Existing end-to-end open-source tools / scripts for "video to sprite sheet"

### Takeaway
Several 2025–2026 projects cover the whole chain, the most complete being LayrKits Sprite-Pipeline (scripted, agent-oriented, with validation reports) and agent-sprite-forge (generation incl. Veo 3.1 + post-processing); simpler GUI converters (duyngha, matheusobf, framekit-web, itch.io tools) handle extraction/keying/packing but not loop finding, pivot normalization or pixel-art cleanup. None found does everything (loop detection + temporally stable matting + feet alignment + engine metadata) out of the box.

### Cited Findings
- **LayrKits/Sprite-Pipeline** — "turns AI-generated motion into reviewable game sprite sheets"; folders `Videos/` → `work/extracted` → `work/matted` → sheet build via `tools/animation_pipeline.py` (`--background-mode chroma --layout-mode preserve-canvas --frames 12`), JSON validation report, browser viewer (`node tools/serve_sprite_viewer.mjs`), promote to `Final Sprite Sheets/<Game>/<Character>/<animation>/`; requires ffmpeg separately; no releases/license shown on the landing page. Companion guide uses GPT Image 2 or Nano Banana 2 for the first pose and Kling for video. — [GitHub](https://github.com/LayrKits/Sprite-Pipeline); [LayrKits guide](https://www.layrkits.com/guides/sprite-sheet); [X article](https://x.com/LayrKits/article/2050277473116619240)
- **0x0funky/agent-sprite-forge** — agent skill generating 2D sprite sheets/maps, transparent PNG frames and GIFs; fal.ai route lists Veo 3.1, Kling, Luma; pins the last frame; local route via signed-in Codex/Grok; code-drawn fallback. — [GitHub](https://github.com/0x0funky/agent-sprite-forge)
- **TamerinTECH/claude-skill-klingai-animation** — static image → Kling video (2–5 s) → ffmpeg at 12 fps → chroma key → single PNG sheet + CSS/React playback. — [GitHub](https://github.com/TamerinTECH/claude-skill-klingai-animation)
- **duyngha/video-to-spritesheet** — Python/Flet desktop app; configurable extraction, scaling; background removal via chroma key, magic wand or AI; exports PNG frames, sheet, GIF. — [GitHub](https://github.com/duyngha/video-to-spritesheet)
- **matheusobf/video-to-spritesheet** — OpenCV + CustomTkinter; 5–60 fps extraction; resolution auto-fill; memory-safety constraints; 4K. — [GitHub](https://github.com/matheusobf/video-to-spritesheet)
- **tylertroy/video2sprites** — older tutorial: ffmpeg extract → ImageMagick chroma key → `montage` sheet; useful for scripting. — [GitHub](https://github.com/tylertroy/video2sprites)
- **framekit-web (joepUI)** — browser-based, local: AI video → sprite sheet / GIF / APNG / animated WebP with chroma key and frame extraction (described in search summary; repo not fetched). — [GitHub topic: ai-animation](https://github.com/topics/ai-animation)
- **itch.io tools**: "Video to Sprite sheet" (agemar, dosprite); mp4tosprite (yewlark, paid). — [agemar.itch.io/dosprite](https://agemar.itch.io/dosprite); [yewlark.itch.io/mp4tosprite](https://yewlark.itch.io/mp4tosprite)
- **looplab** — loop-candidate finder CLI (see §2). — [skills.cat](https://skills.cat/skills/shihanqu/looplab)
- **proper-pixel-art** (animated input with locked grid/palette) and **unfake.js** — pixel-art cleanup stage (see §5). — [proper-pixel-art](https://github.com/KennethJAllen/proper-pixel-art); [unfake.js](https://github.com/jenissimo/unfake.js)
- **Sprite-DX dataset** (HF: sprited/sprite-dx-data) — tagged animation/sprites/image-matting/loop-detection; documents a loop-segment-detection approach. — [Hugging Face](https://huggingface.co/datasets/sprited/sprite-dx-data/blob/main/docs/video_loop_segment_detection.md)

### Inferences
- For a small studio the pragmatic stack is: generation discipline (LayrKits prompt/background rules) → ffmpeg dump → a ~100-line Python script for loop finding + frame picking (§2) → ffmpeg colorkey/despill or LayrKits' chroma rule → fixed scale/offset normalization → (pixel art: proper-pixel-art animation mode) → Aseprite CLI to sheet + JSON with tags → engine importer. LayrKits' repo is the closest ready-made skeleton to fork; its validation-report idea (scale/paste identical across frames, edge-contact and motion-pop warnings, sheet-size check) is worth copying regardless of tooling.
- None of the surveyed tools handles temporally stable AI matting; if the studio can't guarantee flat green backgrounds, budget time for a MatAnyone2/SAM2-based pass (check licenses) or regeneration.

### Gaps
- License, maintenance activity and exact versions of duyngha, matheusobf, framekit-web, agent-sprite-forge and the itch.io tools were not verified (only search summaries for most).
- No Reddit (r/gamedev, r/aigamedev, r/godot, r/Unity2D) threads specifically about Veo → sprite sheet workflows surfaced in searches; practitioner evidence here comes mainly from LayrKits and GitHub READMEs. YouTube tutorials were not reviewed.
- ezgif's sprite-sheet tool was not checked.
