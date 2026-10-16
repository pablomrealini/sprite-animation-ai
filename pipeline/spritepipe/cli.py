"""spritepipe: de clips image-to-video a sprite sheets.

  spritepipe clean-concepts a.png b.png --out dir/  concepts sobre blanco a un plantel RGBA del mismo tamaño
  spritepipe pad-pose concept.png pose.png         pose 16:9 de color plano para el modelo de video
  spritepipe run personaje.toml                    pipeline completo (pasos 4-10 y 12 del reporte)
  spritepipe remove-flash shoot.mp4 out.mp4        clip de disparo sin fogonazo, sin config
  spritepipe clean raw.mp4 out.mp4 [--cut-muzzle]  limpieza previa de un clip (fondo, sombra, efectos), sin config
  spritepipe check clip.mp4 [...]                  QA + loop de uno o varios clips, sin config
  spritepipe bakeoff bakeoff.toml [--dry-run]      misma pose y prompt en varios modelos por API, con QA
  spritepipe gen-images gen.toml [--dry-run]       fondos por API de imagen (varios modelos) y su post sin IA
  spritepipe bg-post imagen.png salida.png         post de un fondo suelto: key, transparencia, costura, recorte
  spritepipe synth carpeta/                        clips sintéticos de prueba con su config
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from . import align, bakeoff, bgpost, chroma, clean, concept, config, decimate, flash, imgio, key, pack, pose, preview, qa, reduce, select
from .analysis import analyze

ICON = {"ok": "✓", "warn": "!", "fail": "✗"}


def _sha256(path: Path | None) -> str | None:
    if not path or not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _print_qa(res: dict, indent: str = "    ") -> None:
    m = res["metrics"]
    print(f"{indent}QA {ICON[res['verdict']]} {res['verdict']}  ·  fondo {m.get('bg_color')}  ·  personaje "
          f"{m.get('char_height_pct')}% del alto  ·  deriva {m.get('drift_pct')}%  ·  zoom {m.get('zoom_pct')}%"
          + (f"  ·  pose MAD {m['pose_mad_region']}" if "pose_mad_region" in m else ""))
    for f in res["flags"]:
        print(f"{indent}  {ICON[f['level']]} {f['msg']}")


def _print_flash(res: dict, indent: str = "    ") -> None:
    g = res["geometry"]
    how = f"medida en el frame 0: {', '.join(res['measured'])}" if res["measured"] else "geometría de la config"
    xs, ys = res["muzzle_x"], res["muzzle_y"]
    print(f"{indent}fogonazo borrado: boca en x {xs[0]}–{xs[1]}, y {ys[0]}–{ys[1]} px del video "
          f"(franja {g['band_y'][0]}–{g['band_y'][1]}, halo desde x {g['halo_x0']}; {how})" if xs else
          f"{indent}! no encontré la boca del cañón en ningún frame: revisá la geometría de remove_flash")
    if xs and res["missed_frames"]:
        print(f"{indent}! sin boca en {len(res['missed_frames'])} frames (quedaron con fogonazo): "
              f"{res['missed_frames'][:10]}")


def _print_clean(res: dict, indent: str = "    ") -> None:
    opts = [k for k, v in res["params"].items() if v]
    print(f"{indent}limpieza{' (' + ', '.join(opts) + ')' if opts else ''}: fondo {res['bg']}"
          + (f", boca en x {res['muzzle_x']}" if res.get("muzzle_x") is not None else "")
          + (f", corte por detrás en x {res['cut_left_x']}" if res.get("cut_left_x") is not None else "")
          + f", {res['removed_px']} px de efectos y utilería sacados"
          + (" (del cache)" if res.get("cached") else ""))


SCALE_SOURCE = {"body_height_px": "body_height_px", "pose": "pose", "scale_pose": "pose y scale_pose",
                "pose_body_height_px": "pose y pose_body_height_px"}


def _print_scales(ch: config.Character, al: dict) -> None:
    """La escala de cada clip contra la referencia, salvo los ×1 sin declarar, más los avisos."""
    ref = ch.scale_reference
    for name, a in al["animations"].items():
        c = a["clip_scale"]
        for kind in ("note", "warning"):
            if c.get(kind):
                print(f"    ! {name}: {c[kind]}")
        if not c["source"]:
            continue
        how = SCALE_SOURCE[c["source"]]
        if c["source"] != "body_height_px":
            how += (f": frame 0 de {c['frame0_px']:g} px contra {c['pose_px']:g} px en la pose"
                    + (f", parado {c['standing_pose_px']:g} px" if c["source"] != "pose" else ""))
        if name == ref:
            print(f"    {name}: referencia, cuerpo de {c['body_px']:g} px del video ({how})")
        elif c.get("same_pose_as") and c["scale"] == 1 and "measured_scale" not in c and c["body_px"] == \
                al["animations"][ref]["clip_scale"].get("body_px"):
            print(f"    {name}: misma pose y resolución que {ref}, misma escala")
        elif "measured_scale" in c:
            print(f"    {name}: misma escala que {ref} (×{c['measured_scale']:.3f} medido, dentro del "
                  f"{100 * align.SCALE_TOLERANCE:g}%; {how})")
        else:
            shared = f"; comparte escala con {', '.join(c['same_pose_as'])}" if c.get("same_pose_as") else ""
            print(f"    {name}: escala del clip ×{c['scale']:.3f}, cuerpo de {c['body_px']:g} px del video "
                  f"({how}{shared}) → {c['final_body_px']:.0f} px")


def _select(anim: config.Animation, an, fps: float, K: int) -> dict:
    if anim.kind == "cycle":
        if anim.loop_start is not None and anim.loop_length:
            sel = {"start": anim.loop_start, "length": anim.loop_length, "manual": True}
        else:
            sel = select.find_loop(an, fps, K, anim.loop_seconds, anim.skip_seconds)
        if sel["length"] % K:
            print(f"    ! el loop ({sel['length']} frames) no es múltiplo de K={K}: la costura va a tartamudear")
    else:
        sel = select.trim_oneshot(an, anim.trim, anim.trim_static_tail, anim.reverse)
    if anim.reverse:
        sel["reverse"] = True
    return sel


def anim_key(ch: config.Character, anim: config.Animation) -> config.Character:
    """El personaje con el método de key que pide la animación (o su [[clip]]), si pide uno."""
    return dataclasses.replace(ch, key_method=anim.key_method) if anim.key_method else ch


def run_character(cfg_path: Path, strict: bool) -> int:
    ch = config.load(cfg_path)
    missing = [a for a in ch.animations if not a.clip.exists()]
    if missing:
        for a in missing:
            print(f"✗ falta el clip de {a.name}: {a.clip}")
        print("  Guardalo ahí o comentá esa [[animation]] en la config.")
        return 1
    print(f"● {ch.name}  ({ch.style}, {ch.game_fps} fps, {len(ch.animations)} animaciones)")
    fixed_key = None if ch.key_color == "auto" else chroma.parse_hex(ch.key_color)
    records, key_dirs, kinds, drifts, muzzles, bodies = {}, {}, {}, {}, {}, {}
    cleaned: dict[tuple, dict] = {}  # un clip limpio por clip y parámetros, compartido entre animaciones
    failed = False

    for anim in ch.animations:
        w = ch.anim_work(anim)
        src = f"{anim.source} ({anim.clip.name})" if anim.source else anim.clip.name
        print(f"  ▸ {anim.name}  ←  {src}" + ("  al revés" if anim.reverse else ""))
        clip, cinfo = anim.clip, None
        if anim.clean:
            ck = (anim.clip, anim.clean, anim.color_matrix)
            if ck in cleaned:
                cinfo = cleaned[ck]
            else:
                cinfo = cleaned[ck] = clean.ensure(anim.clip, anim.clean, ch.work_dir / "00_clean",
                                                   anim.source or anim.clip.stem, anim.color_matrix)
                _print_clean(cinfo)
            clip = cinfo["path"]
        info = imgio.probe(clip)
        raw_dir = w / "01_raw"
        n = imgio.extract(clip, raw_dir, info, None if anim.clean else anim.color_matrix)
        print(f"    {n} frames a {info['fps']:g} fps, {info['width']}×{info['height']}")
        finfo = None
        if anim.remove_flash:
            finfo = flash.run(raw_dir, w / "01_noflash", anim.remove_flash)
            raw_dir = w / "01_noflash"
            muzzles[anim.name] = finfo["muzzle"]
            _print_flash(finfo)
        raw = imgio.frames(raw_dir)
        an = analyze(raw, fixed_key)
        qres = qa.run(an, raw[0], anim.kind, info["fps"], anim.pose)
        _print_qa(qres)
        bodies[anim.name] = align.clip_body(anim_key(ch, anim), anim, imgio.load(raw[0]), qres["metrics"].get("pose_mad_region"),
                                            fixed_key)
        if ch.anchor == "clip":  # el frame 0 del clip es la pose parada: de ahí sale el ancla de todas sus animaciones
            bodies[anim.name]["frame0_anchor_x"] = align.image_anchor_x(imgio.load(raw[0]), anim_key(ch, anim), fixed_key)
        if qres["verdict"] == "fail":
            failed = True
            if strict:
                print("    ✗ --strict: corto acá. Regenerá el clip o ajustá la config.")
                return 1

        K, eff, warn = decimate.factor(info["fps"], ch.game_fps)
        if warn:
            print(f"    ! {warn}")
        sel = _select(anim, an, info["fps"], K)
        if anim.kind == "cycle":
            how = "manual" if sel.get("manual") else f"score {sel['score']} ({sel['quality']})"
            print(f"    loop: frames {sel['start']}–{sel['start'] + sel['length'] - 1} ({sel['length']} nativos), {how}")
        else:
            print(f"    acción: frames {sel['start']}–{sel['start'] + sel['length'] - 1}"
                  + (f", cola quieta recortada ({sel['static_tail_trimmed']})" if sel.get("static_tail_trimmed") else ""))
        indices = list(range(sel["start"], sel["start"] + sel["length"]))
        if anim.reverse:
            indices.reverse()
        timing = decimate.run(raw_dir, w / "02_fps", indices, K, eff, anim.pick, anim.kind, anim.holds)
        bodies[anim.name]["native_indices"] = timing["native_indices"]
        if anim.kind == "cycle":
            dx, dy = select.periodic_drift(an, sel["length"], round(anim.skip_seconds * info["fps"]))
            bodies[anim.name]["camera_drift_x"] = dx  # px del clip por frame nativo
            sign = -K if anim.reverse else K
            drifts[anim.name] = (dx * sign, dy * sign)  # por frame de salida
            sel["camera_drift_px_per_native_frame"] = [round(dx, 4), round(dy, 4)]
        print(f"    {len(timing['native_indices'])} frames a {timing['effective_fps']:g} fps (K={K}, {anim.pick})")
        kinfo = key.run(w / "02_fps", w / "03_key", anim_key(ch, anim))
        print(f"    key {kinfo['key_color']}: " + ", ".join(f"{m} ({mode})" for m, mode in kinfo["method"]))
        key_dirs[anim.name], kinds[anim.name] = w / "03_key", anim.kind
        records[anim.name] = {
            "clip": str(anim.clip), "clip_sha256": _sha256(anim.clip), "video": info,
            **({"source": anim.source} if anim.source else {}),
            **({"color_matrix": anim.color_matrix} if anim.color_matrix else {}),
            **({"clean": {"file": str(cinfo["path"]), **{k: v for k, v in cinfo.items() if k not in ("path", "cached")}}}
               if cinfo else {}),
            **({"reverse": True} if anim.reverse else {}),
            "model": anim.model, "prompt": anim.prompt.read_text(encoding="utf-8") if anim.prompt and anim.prompt.exists() else None,
            "pose": str(anim.pose) if anim.pose else None, "pose_sha256": _sha256(anim.pose),
            "qa": qres, "selection": sel, "timing": timing, "key": kinfo, "loop": anim.loop,
        }
        if finfo:
            records[anim.name]["remove_flash"] = {k: v for k, v in finfo.items() if k != "muzzle"}

    print("  ▸ alineación (canvas, pivot y escala comunes)")
    aligned_dirs = {name: ch.work_dir / "04_aligned" / name for name in key_dirs}
    al = align.run(ch, key_dirs, kinds, aligned_dirs, drifts, bodies)
    print(f"    canvas {al['canvas']['w']}×{al['canvas']['h']} a resolución de video, pivot "
          f"({al['pivot_px']['x']}, {al['pivot_px']['y']}), alto de referencia {al['reference_height_px']} px "
          f"→ escala {al['scale']:.4f}" + (f" (pixel factor {al['pixel_factor']})" if al["pixel_factor"] else ""))
    _print_scales(ch, al)
    for name, a in al["animations"].items():
        records[name]["scale"] = a["clip_scale"]
        dx, dy = a["drift_removed_px_per_frame"]
        if abs(dx) + abs(dy) > 0.01:
            print(f"    {name}: deriva lineal removida ({dx:+.2f}, {dy:+.2f}) px/frame")

    final_root = ch.work_dir / "05_final"
    if ch.style == "pixel":
        variants = reduce.run_pixel(ch, aligned_dirs, final_root, al["pixel_factor"], al["canvas"])
    else:
        variants = reduce.run_hd(ch, aligned_dirs, final_root, al["scale"], al["canvas"])

    out = ch.out_dir
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    pivot_norm = (0.5, al["pivot_px"]["y"] / al["canvas"]["h"])
    index = {"character": ch.name, "style": ch.style, "fps": ch.game_fps, "pivot": {"x": pivot_norm[0], "y": round(pivot_norm[1], 5)},
             "variants": {}}
    html = {"style": ch.style, "variants": {}}
    cleanup_dir = ch.root / "cleanup"
    overridden = 0

    for tag, v in variants.items():
        sprites, durations, anim_frames, frame_paths = [], {}, {}, {}
        for anim in ch.animations:
            src = imgio.frames(final_root / tag / anim.name)
            paths = []
            for p in src:
                cp = cleanup_dir / anim.name / p.name
                if tag == "1x" and cp.exists():
                    p, overridden = cp, overridden + 1
                paths.append(p)
            frame_paths[anim.name] = paths
            names = []
            for j, p in enumerate(paths):
                fname = f"{anim.name}/{j:04d}"
                sprites.append(pack.sprite_from(fname, imgio.load(p)))
                durations[fname] = records[anim.name]["timing"]["durations_ms"][j]
                names.append(fname)
            anim_frames[anim.name] = names

        base = f"{ch.name}_{tag}"
        pages = pack.build_atlas(sprites, out, base, ch.atlas_max_size, ch.padding, ch.border_padding,
                                 ch.extrude, ch.power_of_two, durations, anim_frames, pivot_norm)
        page_of = {name: pi for pi, pg in enumerate(pages) for name in pg["frames"]}
        entry = {"canvas": {"w": v["w"], "h": v["h"]},
                 "pivot_px": {"x": v["w"] * pivot_norm[0], "y": round(v["h"] * pivot_norm[1], 2)},
                 "atlas": [{"image": p["image"], "data": p["data"], "w": p["w"], "h": p["h"]} for p in pages],
                 "animations": {}}
        hv = {"canvas": entry["canvas"], "pivot": entry["pivot_px"], "pages": [p["image"] for p in pages], "animations": {}}
        for anim in ch.animations:
            names = anim_frames[anim.name]
            entry["animations"][anim.name] = {
                "loop": anim.loop,
                "frames": [{"page": page_of[nm], "name": nm, "duration": durations[nm]} for nm in names],
                "sheet": f"sheets/{tag}/{anim.name}.png",
            }
            hv["animations"][anim.name] = {"loop": anim.loop, "frames": [
                {"page": page_of[nm], **{k: pages[page_of[nm]]["frames"][nm]["frame"][k] for k in "xywh"},
                 "ox": pages[page_of[nm]]["frames"][nm]["spriteSourceSize"]["x"],
                 "oy": pages[page_of[nm]]["frames"][nm]["spriteSourceSize"]["y"],
                 "duration": durations[nm]} for nm in names]}
            imgs = [imgio.load(p) for p in frame_paths[anim.name]]
            grid = pack.build_grid(imgs, out / "sheets" / tag / f"{anim.name}.png", ch.atlas_max_size)
            imgio.write_json(out / "sheets" / tag / f"{anim.name}.json", {
                **grid, "fps": ch.game_fps, "loop": anim.loop, "pivot": index["pivot"],
                "durations_ms": [durations[nm] for nm in names]})
            if grid["oversize"]:
                print(f"    ! la grilla de {anim.name} ({tag}) pasa de {ch.atlas_max_size} px")
            imgio.write_apng(frame_paths[anim.name], [durations[nm] for nm in names],
                             out / "previews" / tag / f"{anim.name}.png")
        index["variants"][tag] = entry
        html["variants"][tag] = hv
        uniq = sum(p["unique_sprites"] for p in pages)
        print(f"  ▸ {tag}: celda {v['w']}×{v['h']}, {len(sprites)} frames ({uniq} únicos) en "
              + ", ".join(f"{p['w']}×{p['h']}" for p in pages))

    for name, muzzle in muzzles.items():
        fx = flash.anchors(name, muzzle, records[name]["timing"]["native_indices"], al["animations"][name]["shifts"],
                           al["canvas"], al["pivot_px"], variants, pivot_norm[1],
                           al["animations"][name]["clip_scale"].get("scale_xy"))
        imgio.write_json(out / "fx" / f"{name}_muzzle.json", fx)
        index.setdefault("fx", {})[name] = {"muzzle": f"fx/{name}_muzzle.json"}
        f1 = [f for f in fx["variants"][next(iter(variants))]["frames"] if f["x"] is not None]
        if f1:
            print(f"  ▸ anclaje del fogonazo de {name}: fx/{name}_muzzle.json (a {next(iter(variants))}, dx "
                  f"{min(f['dx'] for f in f1):+g}…{max(f['dx'] for f in f1):+g}, dy "
                  f"{min(f['dy'] for f in f1):+g}…{max(f['dy'] for f in f1):+g} desde el pivot)")
    if ch.style == "pixel":
        shutil.copyfile(final_root / "palette.png", out / "palette.png")
    imgio.write_json(out / f"{ch.name}.json", index)
    preview.write(out / "preview.html", ch.name, html)
    imgio.write_json(out / "provenance.json", {
        "character": ch.name, "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tool": "spritepipe 0.1", "ffmpeg": imgio.ffmpeg_version(),
        "config": cfg_path.read_text(encoding="utf-8"), "align": {k: v for k, v in al.items() if k != "animations"},
        "variants": variants, "cleanup_frames_overridden": overridden, "animations": records,
        "human_cleanup": "registrar en pilot/cleanup_log.csv quién limpió qué y cuánto tardó",
    })
    if overridden:
        print(f"  ▸ {overridden} frames reemplazados por la limpieza manual (cleanup/)")
    print(f"  ✓ listo: {out}/preview.html")
    return 2 if failed else 0


def check(clips: list[Path], pose: Path | None, kind: str, game_fps: int) -> int:
    """QA y loop de cada clip, sin config: para comparar modelos en el bake-off."""
    rows = []
    for clip in clips:
        c = qa.check_clip(clip, pose, kind, game_fps)
        res, loop, info = c["qa"], c["loop"], c["video"]
        print(f"\n{clip.name}  ({c['frames']} frames, {info['fps']:g} fps, {info['width']}×{info['height']})")
        _print_qa(res, "  ")
        if loop and "error" not in loop:
            print(f"  loop {loop['start']}+{loop['length']} score {loop['score']} ({loop['quality']})")
        rows.append((clip.name, res["verdict"], res["metrics"], loop))
    if len(rows) > 1:
        print("\nclip                               QA    deriva%  zoom%  pose  mov.   loop")
        for name, verdict, m, loop in rows:
            ls = f"{loop['score']}" if loop and "score" in loop else "-"
            print(f"{name[:34]:34} {verdict:5} {m.get('drift_pct', 0):7} {m.get('zoom_pct', 0):6} "
                  f"{m.get('pose_mad_region', '-')!s:>5} {m.get('motion', 0):5}  {ls}")
    return 0


def clean_clip(clip: Path, out: Path, params: config.Clean, matrix: str | None) -> int:
    """Limpieza previa de un clip suelto (H.264 sin pérdida), para mirarla o usarla fuera del pipeline."""
    res = clean.clean_clip(clip, out, params, matrix)
    _print_clean({**res, "params": vars(params)}, "")
    print(f"✓ {out} ({res['frames']} frames)")
    return 0


def remove_flash(clip: Path, out: Path, params: config.FlashRemoval) -> int:
    """Clip de disparo sin fogonazo (H.264 sin pérdida) más la boca por frame en <out>.muzzle.json."""
    tmp = Path(tempfile.mkdtemp(prefix="spritepipe_"))
    try:
        info = imgio.probe(clip)
        imgio.extract(clip, tmp / "raw", info)
        res = flash.run(tmp / "raw", tmp / "noflash", params)
        _print_flash(res, "")
        frames = imgio.frames(tmp / "noflash")
        imgio.encode_rgb_video((imgio.load(p) for p in frames), out, info["fps"], crf=0, pix_fmt="yuv444p")
        meta = out.with_suffix(".muzzle.json")
        shutil.copyfile(tmp / "noflash" / "muzzle.json", meta)
        print(f"✓ {out} ({len(frames)} frames) y {meta.name}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


def bg_post(args) -> int:
    """Post de un fondo suelto, por ejemplo después de retocarlo a mano."""
    split = args.split.split(",") if args.split else []
    spec = bgpost.PostSpec(expect=args.alpha, key=args.key, tile={"": args.tile} if args.tile and not split else
                           {p: args.tile for p in split} if args.tile else {}, seam=args.seam, seam_px=args.seam_px,
                           trim=not args.no_trim, split=split, same_height=args.same_height,
                           height=args.height)
    rep = bgpost.process(args.image, args.out, spec)
    a = rep["alpha"]
    print(f"{ICON[a['verdict']]} transparencia {a['verdict']}: {100 * a['transparent']:.1f}% transparente"
          + (f", key {rep['key']['key_color']}" if "key" in rep else ""))
    for f in a["flags"] + rep["notes"]:
        print(f"  ! {f}")
    for k, v in rep.get("seam", {}).items():
        b = v["before"]
        print(f"  costura {k}: {b['score']} ({b['verdict']}, pico {b['peak']})"
              + (f" → {v['after']['score']} con {v['fix']['method']}, {v['fix']['overlap_px']} px menos"
                 if "after" in v else "") + (f"; para editar: {', '.join(v['mask'])}" if "mask" in v else "")
              + (" (el arreglo no mejoraba: descartado)" if "fix_discarded" in v else ""))
    for name, f in rep["files"].items():
        print(f"  ✓ {name}: {f['file']} ({f['w']}×{f['h']})")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="spritepipe", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="pipeline completo para un personaje")
    r.add_argument("config", type=Path)
    r.add_argument("--strict", action="store_true", help="cortar si algún clip falla el QA")
    c = sub.add_parser("check", help="QA y loop de clips sueltos (bake-off)")
    c.add_argument("clips", type=Path, nargs="+")
    c.add_argument("--pose", type=Path)
    c.add_argument("--kind", choices=["cycle", "oneshot"], default="cycle")
    c.add_argument("--game-fps", type=int, default=12)
    b = sub.add_parser("bakeoff", help="misma pose y prompt en varios modelos image-to-video, con QA")
    b.add_argument("config", type=Path, help="TOML del bake-off (ver characters/comando/bakeoff.toml)")
    b.add_argument("--dry-run", action="store_true", help="mostrar los pedidos y el costo sin llamar a ninguna API")
    b.add_argument("--yes", action="store_true", help="no pedir confirmación antes de gastar")
    b.add_argument("--models", help="sólo estos modelos de la config, separados por coma")
    b.add_argument("--skip-qa", action="store_true", help="bajar los clips sin correr el QA")
    g = sub.add_parser("gen-images", help="gráficos de fondo por API de imagen, varios modelos, con post sin IA")
    g.add_argument("config", type=Path, help="TOML del set (ver backgrounds/ranger_base/gen.toml)")
    g.add_argument("--dry-run", action="store_true", help="mostrar pedidos, prompts y costo sin llamar a ninguna API")
    g.add_argument("--yes", action="store_true", help="no pedir confirmación antes de gastar")
    g.add_argument("--models", help="sólo estos modelos de la config, separados por coma")
    g.add_argument("--assets", help="sólo estos assets de la config, separados por coma")
    g.add_argument("--post-only", action="store_true", help="rehacer el post de lo ya bajado, sin llamar a ninguna API")
    bp = sub.add_parser("bg-post", help="post de un fondo suelto: key, transparencia, piezas, costura y recorte")
    bp.add_argument("image", type=Path)
    bp.add_argument("out", type=Path, help="PNG de salida; con --split, una carpeta con el nombre de out sin .png")
    bp.add_argument("--alpha", choices=["opaque", "layer", "cutout"], default="cutout",
                    help="opaque: cielo o style frame; layer: capa con aire arriba; cutout: prop o pieza suelta")
    bp.add_argument("--key", help="color plano del fondo a sacar, #RRGGBB (los modelos sin alfa)")
    bp.add_argument("--tile", choices=["x", "y", "xy"], help="ejes en que la imagen se repite")
    bp.add_argument("--seam", choices=["cut", "crossfade", "mask", "none"], default="cut")
    bp.add_argument("--seam-px", type=float, default=0.12, help="franja de la costura: px, o fracción si es < 1")
    bp.add_argument("--split", help="nombres de las piezas de una hoja, en orden de lectura, separados por coma")
    bp.add_argument("--same-height", action="store_true", help="en una hoja: las piezas a una misma altura (un kit)")
    bp.add_argument("--height", type=int, help="alto final en px (en una hoja, el de la pieza más alta o el común)")
    bp.add_argument("--no-trim", action="store_true", help="no recortar al contenido")
    s = sub.add_parser("synth", help="generar clips sintéticos de prueba")
    s.add_argument("out", type=Path)
    k = sub.add_parser("clean-concepts", help="concepts sobre blanco a un plantel RGBA del mismo tamaño")
    k.add_argument("concepts", type=Path, nargs="+", help="un PNG o JPG por personaje, sobre fondo blanco")
    k.add_argument("--out", type=Path, required=True, help="carpeta del plantel: <nombre>.png y magenta/<nombre>.png")
    k.add_argument("--size", default="512x512", help="canvas común, ANCHOxALTO")
    k.add_argument("--feet", type=float, default=0.94, help="línea de pies, fracción del alto del canvas")
    k.add_argument("--no-magenta", action="store_true", help="no armar las poses 16:9 para el modelo de video")
    p = sub.add_parser("pad-pose", help="pose 16:9 de color plano desde un concept RGBA")
    p.add_argument("concept", type=Path, help="PNG o WebP con transparencia (el concept de ChatGPT)")
    p.add_argument("out", type=Path)
    p.add_argument("--feet", type=float, default=0.72, help="línea de pies, fracción del alto (0.92 para saltos)")
    p.add_argument("--height", type=float, default=0.48, help="alto del personaje, fracción del alto del canvas")
    p.add_argument("--bg", default="FF00FF", help="color del fondo, RRGGBB")
    p.add_argument("--size", default="1920x1080", help="canvas, ANCHOxALTO")
    p.add_argument("--shadow-from", type=float, default=0.94,
                   help="desde qué fracción del bbox (desde arriba) se borra la sombra semitransparente")
    cl = sub.add_parser("clean", help="limpieza previa de un clip: fondo plano, sin sombra ni efectos")
    cl.add_argument("clip", type=Path)
    cl.add_argument("out", type=Path, help=".mp4 de salida (H.264 sin pérdida, yuv444p, BT.709)")
    cl.add_argument("--cut-muzzle", action="store_true", help="borrar lo que queda delante de la boca del arma")
    cl.add_argument("--cut-left", action="store_true", help="borrar lo que cruza por detrás del personaje")
    cl.add_argument("--prop-rows", action="store_true", help="borrar utilería que cruza el cuadro (una barra)")
    cl.add_argument("--color-matrix", choices=config.COLOR_MATRICES, help="matriz de color del clip, si no la trae")
    f = sub.add_parser("remove-flash", help="borrar el fogonazo de un clip de disparo")
    f.add_argument("clip", type=Path)
    f.add_argument("out", type=Path, help=".mp4 de salida; la boca por frame va a <out>.muzzle.json")
    for name, help_ in (("--band-y", "filas donde se busca el contorno del cañón"),
                        ("--search-x", "columnas donde puede estar la boca"),
                        ("--flash-y", "filas que puede ocupar el fogonazo")):
        f.add_argument(name, type=int, nargs=2, metavar=("DESDE", "HASTA"), help=f"{help_} (px del clip)")
    f.add_argument("--halo-x0", type=int, help="desde qué columna hasta la boca sólo hay cañón (px del clip)")
    args = ap.parse_args(argv)

    if args.cmd == "run":
        return run_character(args.config, args.strict)
    if args.cmd == "check":
        return check(args.clips, args.pose, args.kind, args.game_fps)
    if args.cmd == "bakeoff":
        return bakeoff.run(args.config, dry_run=args.dry_run, yes=args.yes, skip_qa=args.skip_qa,
                           models=args.models.split(",") if args.models else None)
    if args.cmd == "gen-images":
        from . import genimages
        return genimages.run(args.config, dry_run=args.dry_run, yes=args.yes, post_only=args.post_only,
                             models=args.models.split(",") if args.models else None,
                             assets=args.assets.split(",") if args.assets else None)
    if args.cmd == "bg-post":
        return bg_post(args)
    if args.cmd == "clean-concepts":
        w, h = (int(v) for v in args.size.lower().split("x"))
        for info in concept.roster(args.concepts, args.out, (w, h), args.feet, magenta=not args.no_magenta):
            print(f"✓ {info['out']}: {info['height']} px de alto, botas de {info['feet_width']} px, "
                  f"{info['shadow_px']} px de sombra y hueco borrados"
                  + (f"  ·  pose {info['magenta']}" if "magenta" in info else ""))
        return 0
    if args.cmd == "pad-pose":
        w, h = (int(v) for v in args.size.lower().split("x"))
        res = pose.pad(args.concept, args.out, (w, h), args.height, args.feet, args.bg, args.shadow_from)
        print(f"✓ {args.out}: personaje {res['sprite'][0]}×{res['sprite'][1]} en ({res['at'][0]}, {res['at'][1]}), "
              f"canvas {w}×{h}")
        return 0
    if args.cmd == "clean":
        return clean_clip(args.clip, args.out, config.Clean(args.cut_muzzle, args.cut_left, args.prop_rows),
                          args.color_matrix)
    if args.cmd == "remove-flash":
        params = config.FlashRemoval(
            band_y=tuple(args.band_y) if args.band_y else None, search_x=tuple(args.search_x) if args.search_x else None,
            flash_y=tuple(args.flash_y) if args.flash_y else None, halo_x0=args.halo_x0)
        return remove_flash(args.clip, args.out, params)
    from . import synth
    synth.make(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
