# Metal Slug 1, Marco (Carl27's composite rip): own counts and measurements

Source: the sheet the user provided, `refs/metal_slug_1_marco_rip_carl27.png` in this folder. It is a composite (full-body) rip of MS1 Marco with the pistol; the footer credits Carl27. `refs/` is git-ignored: third-party rips are kept for analysis only and never used as assets.

## Resolution
- The file is 400×600 with 41 unique colours, and only 18% of foreground 2×2 blocks are uniform, so it is **native resolution (1:1)**, not a reduced copy. Standing Marco is 38 px tall, matching the split sheet (M11225) and the video measurement in `metal_slug.md`.
- Method: background = most common colour (white); sprites = 8-connected components of ≥40 px; feet span = outer foreground columns in the bottom 3 rows of each frame. Script in the session scratchpad (`scripts/carl27/`).

## Counts (own count)
| Row (ripper's label) | Frames | Notes |
|---|---|---|
| Standing stance | 3 | 29–30 × 38 px; the split sheet has 4 idle torsos over 1 legs piece, so the composite shows a subset |
| Running with handgun | 9 | 27–36 × 37–41 px; the split sheet has 12 torso + 12 legs, so the composite does not capture the full cycle |
| Shooting, reloading and drinking water | 10 + 10 + 11 | 2 level firing frames with the flash drawn in (50–51 px wide), raise/recoil frames, a reload with the magazine dropping, and the canteen idle fidget |
| Jumping | 9 + 4 | 9 airborne frames (pistol held up, legs tucked), then 4 landing/crouch-to-stand frames |
| Throwing bomb | 5 bodies + grenade arc | The grenade arc is drawn as separate small sprites |
| Ducking | 2 transitions + 4 crouch | Crouch is 24 px tall, 33–34 px wide |
| Explosion | effect series | Separate from the character |

## Measurements (own measurement)
- **Feet span:** 21 px (0.55 H) in all 3 standing frames *and* in the 2 level firing frames. The stance does not open to fire.
- **Run stride:** feet span varies from 4 to 29 px across the 9 run frames.
- **Crouch:** feet span 29–32 px.
- **Gun posture:** in the standing stance and the run, the pistol points down-forward ("low ready"); it is level only in the firing frames. On the split sheet the idle torsos measure −29° to −45° (see `metal_slug_sheets.md`), and the HMG idles at −4° to −15° and fires between −12° and +3°.

## Takeaway for the comando
Marco's stance is narrower than the comando's (0.55 H vs 0.63 H, about 13% less), and it stays the same width when firing. His gun is not level at rest either: it is level only while firing. At Marco's scale a 5° droop over a 20 px gun is under 2 px; at the comando's 67 px gun it is about 6 px. So the 5° droop is visible on the comando because of the scale, and because the droop is fixed while the bullets travel straight.
