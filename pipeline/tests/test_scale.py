"""Escala por clip: clips de poses y resoluciones distintas llevados al mismo cuerpo (align.py)."""

import json

import cv2
import numpy as np
import pytest

from spritepipe import align, cli, config, imgio, key

BG = (250, 30, 245)  # magenta como el que devuelve Seedance, no #FF00FF exacto
OUTLINE, BODY, SKIN, LEGS = (25, 22, 28), (60, 110, 170), (240, 200, 155), (90, 62, 43)
SS = 4


def _figure(size, h, feet_y, cx=None, arms_up=False, noise_seed=None):
    """Personaje de frente de `h` px de alto parado, con los pies en la fila feet_y.

    Con arms_up, los brazos levantados (colgado de una cornisa) suben el bbox 25% por encima de la cabeza.
    """
    W, H = size
    big = np.full((H * SS, W * SS, 3), BG, np.uint8)
    cx = W / 2 if cx is None else cx
    u, top = h / 100, feet_y - h

    def rect(x0, y0, x1, y1, color):
        cv2.rectangle(big, (round(x0 * SS), round(y0 * SS)), (round(x1 * SS) - 1, round(y1 * SS) - 1), color, -1)

    if arms_up:
        rect(cx - 22 * u, top - 25 * u, cx - 12 * u, top + 40 * u, OUTLINE)
        rect(cx + 12 * u, top - 25 * u, cx + 22 * u, top + 40 * u, OUTLINE)
    rect(cx - 14 * u, top + 60 * u, cx + 14 * u, feet_y, OUTLINE)
    rect(cx - 11 * u, top + 60 * u, cx + 11 * u, feet_y - 3 * u, LEGS)
    rect(cx - 18 * u, top + 30 * u, cx + 18 * u, top + 64 * u, OUTLINE)
    rect(cx - 15 * u, top + 33 * u, cx + 15 * u, top + 61 * u, BODY)
    cv2.circle(big, (round(cx * SS), round((top + 16 * u) * SS)), round(16 * u * SS), OUTLINE, -1)
    cv2.circle(big, (round(cx * SS), round((top + 16 * u) * SS)), round(13 * u * SS), SKIN, -1)
    img = cv2.resize(big, (W, H), interpolation=cv2.INTER_AREA)
    if noise_seed is not None:
        rng = np.random.default_rng(noise_seed)
        img = np.clip(img + rng.normal(0, 1.5, img.shape), 0, 255).astype(np.uint8)
    return img


def _character(tmp_path, anims, target=64):
    cfg = tmp_path / "character.toml"
    cfg.write_text(f'[character]\nname = "t"\ntarget_height = {target}\nscale_reference = "idle"\n'
                   + "".join(f'[[animation]]\nname = "{n}"\nclip = "clips/{n}.mp4"\n{extra}\n' for n, extra in anims),
                   encoding="utf-8")
    return cfg


def _keyed(ch, frames, d):
    for i, f in enumerate(frames):
        imgio.save(d / imgio.frame_name(i), key.key_frame(f, ch, None)[0])
    return d


def _body(alpha):
    return align.body_height(alpha)


# --- config -------------------------------------------------------------------


def test_config_reads_clip_scale(tmp_path):
    ch = config.load(_character(tmp_path, [
        ("idle", ""),
        ("jump", 'pose = "jump.png"\nbody_height_px = 238'),
        ("climb", 'pose = "hang.png"\nscale_pose = "stand.png"'),
        ("hang", 'pose = "hang.png"\npose_body_height_px = 437'),
    ]))
    assert ch.get("idle").body_height_px is None and ch.get("idle").scale_pose is None
    assert ch.get("jump").body_height_px == 238.0
    assert ch.get("climb").scale_pose == (tmp_path / "stand.png").resolve()
    assert ch.get("hang").pose_body_height_px == 437.0


@pytest.mark.parametrize("extra, match", [
    ('scale_pose = "stand.png"', "scale_pose necesita"),
    ("pose_body_height_px = 437", "pose_body_height_px necesita"),
    ('pose = "hang.png"\nscale_pose = "stand.png"\npose_body_height_px = 437', "no los dos"),
    ("body_height_px = 0", "body_height_px"),
    ('body_height_px = "238"', "body_height_px"),
])
def test_config_rejects_bad_clip_scale(tmp_path, extra, match):
    with pytest.raises(ValueError, match=match):
        config.load(_character(tmp_path, [("idle", extra)]))


# --- medición y escala -----------------------------------------------------------


def test_clip_body_from_a_standing_pose(tmp_path):
    ch = config.load(_character(tmp_path, [("idle", ""), ("jump", 'pose = "pose.png"')]))
    pose = _figure((640, 360), 0.48 * 360, 0.72 * 360)
    imgio.save(tmp_path / "pose.png", pose)
    frame0 = cv2.resize(pose, (432, 243), interpolation=cv2.INTER_AREA)  # el modelo lo devolvió más chico
    b = align.clip_body(ch, ch.get("jump"), frame0, pose_mad=8.0)
    assert b["source"] == "pose" and b["video"] == [432, 243] and b["pose_size"] == [640, 360]
    assert abs(b["pose_px"] - 0.48 * 360) <= 1
    assert abs(b["body_px"] - 0.48 * 243) <= 1 and b["body_px"] == b["frame0_px"]


def test_clip_body_from_a_hanging_pose_uses_scale_pose(tmp_path):
    ch = config.load(_character(tmp_path, [("idle", ""),
                                           ("climb", 'pose = "hang.png"\nscale_pose = "stand.png"')]))
    # Pose de trepar: el personaje más chico (36% parado) y colgado, con los brazos arriba
    imgio.save(tmp_path / "hang.png", _figure((640, 360), 0.36 * 360, 0.9 * 360, arms_up=True))
    imgio.save(tmp_path / "stand.png", _figure((640, 360), 0.36 * 360, 0.9 * 360))
    frame0 = cv2.resize(imgio.load(tmp_path / "hang.png"), (432, 243), interpolation=cv2.INTER_AREA)
    b = align.clip_body(ch, ch.get("climb"), frame0, pose_mad=8.0)
    assert b["source"] == "scale_pose"
    assert abs(b["frame0_px"] - 1.25 * 0.36 * 243) <= 1  # lo que mide colgado, con los brazos
    assert abs(b["body_px"] - 0.36 * 243) <= 1  # lo que mediría parado en px de este video


def test_clip_body_from_a_hanging_pose_with_its_standing_height(tmp_path):
    ch = config.load(_character(tmp_path, [("idle", ""), ("climb", 'pose = "hang.png"\npose_body_height_px = 129.6')]))
    imgio.save(tmp_path / "hang.png", _figure((640, 360), 0.36 * 360, 0.9 * 360, arms_up=True))
    frame0 = cv2.resize(imgio.load(tmp_path / "hang.png"), (432, 243), interpolation=cv2.INTER_AREA)
    b = align.clip_body(ch, ch.get("climb"), frame0, pose_mad=8.0)
    assert b["source"] == "pose_body_height_px" and b["standing_pose_px"] == 129.6
    assert abs(b["body_px"] - 0.36 * 243) <= 1


def test_clip_body_override_and_pose_that_does_not_match(tmp_path):
    ch = config.load(_character(tmp_path, [("idle", ""), ("a", 'pose = "pose.png"\nbody_height_px = 300'),
                                           ("b", 'pose = "pose.png"')]))
    imgio.save(tmp_path / "pose.png", _figure((640, 360), 170, 260))
    frame0 = _figure((640, 360), 170, 260)
    assert align.clip_body(ch, ch.get("a"), frame0, pose_mad=8.0)["body_px"] == 300.0
    b = align.clip_body(ch, ch.get("b"), frame0, pose_mad=60.0)  # el modelo re-renderizó el frame 0
    assert b["source"] is None and b["body_px"] is None and "no coincide con la pose" in b["note"]


def _bodies(**kw):
    out = {}
    for name, (f0, source, body) in kw.items():
        out[name] = {"video": [864, 496], "frame0_px": f0, "source": source, "body_px": body}
        if source in ("pose", "scale_pose"):
            out[name].update(pose_size=[1920, 1080], pose_px=518.0, standing_pose_px=518.0)
    return out


def test_clip_scales(tmp_path):
    ch = config.load(_character(tmp_path, [("idle", "")]))
    bodies = _bodies(idle=(518.0, None, None), jump=(238.0, "pose", 238.0), shoot=(240.0, "body_height_px", 240.0),
                     crouch=(519.0, None, None))
    bodies["jump"]["video"] = [560, 752]  # otra resolución: no comparte escala con nadie
    sc = align.clip_scales(ch, list(bodies), bodies, ref_h=505.0, scale=128 / 505)
    assert sc["idle"]["scale"] == 1.0 and sc["idle"]["reference_body_px"] == 505.0  # sin declarar: la mediana
    assert sc["jump"]["scale"] == round(505 / 238, 4) and sc["jump"]["final_body_px"] == 128.0
    assert sc["shoot"]["scale"] == round(505 / 240, 4)
    assert sc["crouch"]["scale"] == 1.0 and "warning" not in sc["crouch"]  # misma escala que la referencia


def test_clip_scales_warns_when_undeclared_heights_differ(tmp_path):
    ch = config.load(_character(tmp_path, [("idle", "")]))
    bodies = _bodies(idle=(518.0, None, None), small=(238.0, None, None), close=(470.0, None, None),
                     declared=(238.0, "body_height_px", 238.0))
    sc = align.clip_scales(ch, list(bodies), bodies, ref_h=505.0, scale=128 / 505)
    assert "-54%" in sc["small"]["warning"] and "~60 px" in sc["small"]["warning"]
    assert sc["small"]["scale"] == 1.0
    assert "warning" not in sc["close"]  # 9% de diferencia
    assert "warning" not in sc["declared"]


def test_same_pose_and_resolution_share_the_scale(tmp_path):
    ch = config.load(_character(tmp_path, [("idle", "")]))
    # El frame 0 re-renderizado mide distinto en cada clip aunque la pose y la resolución sean las mismas
    bodies = _bodies(idle=(236.0, "pose", 236.0), shoot=(231.0, "pose", 231.0), jump=(234.0, "pose", 234.0))
    sc = align.clip_scales(ch, list(bodies), bodies, ref_h=235.0, scale=0.5)
    assert sc["shoot"]["scale"] == 1.0 and sc["jump"]["scale"] == 1.0
    assert sc["shoot"]["measured_body_px"] == 231.0 and sc["shoot"]["same_pose_as"] == ["idle", "jump"]
    # Sin la referencia en el grupo, el grupo usa la mediana de sus clips
    bodies = _bodies(idle=(518.0, None, None), shoot=(231.0, "pose", 231.0), jump=(234.0, "pose", 234.0),
                     run=(233.0, "pose", 233.0))
    sc = align.clip_scales(ch, list(bodies), bodies, ref_h=505.0, scale=128 / 505)
    assert sc["shoot"]["scale"] == sc["jump"]["scale"] == sc["run"]["scale"] == round(505 / 233, 4)


def test_pose_scale_close_to_one_is_measurement_noise(tmp_path):
    ch = config.load(_character(tmp_path, [("idle", "")]))
    bodies = _bodies(idle=(240.0, None, None), walk=(237.0, "pose", 237.0), attack=(237.0, "body_height_px", 237.0))
    bodies["walk"]["pose_size"] = [720, 1280]
    sc = align.clip_scales(ch, list(bodies), bodies, ref_h=240.0, scale=0.5)
    assert sc["walk"]["scale"] == 1.0 and sc["walk"]["measured_scale"] == round(240 / 237, 4)
    assert sc["attack"]["scale"] == round(240 / 237, 4)  # lo declarado a mano se aplica siempre


# --- alineación ------------------------------------------------------------------


def test_align_scales_each_clip_before_the_common_canvas(tmp_path):
    """Referencia en un clip vertical y un salto en uno 16:9 con el personaje a la mitad de px."""
    ch = config.load(_character(tmp_path, [("idle", ""), ("jump", "body_height_px = 100")]))
    ch.body_height_px = 200.0  # el alto de referencia exacto, para que la escala del salto dé 2
    idle = [_figure((300, 400), 200, 350 - (i % 2), noise_seed=i) for i in range(4)]
    jump = [_figure((400, 225), 100, 200 - 30 * np.sin(np.pi * i / 5), noise_seed=10 + i) for i in range(6)]
    key_dirs = {"idle": _keyed(ch, idle, tmp_path / "k" / "idle"), "jump": _keyed(ch, jump, tmp_path / "k" / "jump")}
    out = {n: tmp_path / "aligned" / n for n in key_dirs}
    bodies = {"idle": {"video": [300, 400], "frame0_px": 200.0, "source": None, "body_px": None},
              "jump": {"video": [400, 225], "frame0_px": 100.0, "source": "body_height_px", "body_px": 100.0}}
    al = align.run(ch, key_dirs, {"idle": "cycle", "jump": "oneshot"}, out, {}, bodies)

    assert al["animations"]["jump"]["clip_scale"]["scale"] == 2.0
    assert al["animations"]["jump"]["clip_scale"]["scale_xy"] == [2.0, 2.0]
    assert al["animations"]["idle"]["clip_scale"]["scale"] == 1.0
    assert len(imgio.frames(tmp_path / "work" / "jump" / "03_scaled")) == 6
    assert al["scale"] == 64 / 200
    W, H = al["canvas"]["w"], al["canvas"]["h"]
    piv = al["pivot_px"]["y"]
    for name in ("idle", "jump"):
        a0 = imgio.load(imgio.frames(out[name])[0])
        assert a0.shape[:2] == (H, W)  # una sola celda
        m = align._measure(a0[..., 3])
        assert abs(m["ground"] - piv) <= 1  # misma línea de piso
        assert abs(_body(a0[..., 3]) - 200) <= 2  # mismo cuerpo, en px de la referencia
    peak = imgio.load(imgio.frames(out["jump"])[3])[..., 3]
    assert piv - align._measure(peak)["ground"] > 50  # la subida del salto (30 px del clip) quedó escalada


def test_align_without_bodies_keeps_one_scale(tmp_path):
    ch = config.load(_character(tmp_path, [("idle", ""), ("jump", "")]))
    key_dirs = {"idle": _keyed(ch, [_figure((300, 400), 200, 350)], tmp_path / "k" / "idle"),
                "jump": _keyed(ch, [_figure((400, 225), 100, 200)], tmp_path / "k" / "jump")}
    out = {n: tmp_path / "aligned" / n for n in key_dirs}
    al = align.run(ch, key_dirs, {"idle": "oneshot", "jump": "oneshot"}, out, {})
    assert al["animations"]["jump"]["clip_scale"]["scale"] == 1.0
    assert abs(_body(imgio.load(imgio.frames(out["jump"])[0])[..., 3]) - 100) <= 1
    assert not (tmp_path / "work" / "jump" / "03_scaled").exists()


# --- de punta a punta, con clips de dos resoluciones ----------------------------------


def _clips(root):
    """idle: clip vertical de 360×480 con el personaje a 240 px. jump: desde una pose 16:9 de 1280×720
    (personaje al 48%, pies al 92%) que el modelo devolvió a 448×252, con el personaje a ~121 px."""
    clips = root / "clips"
    imgio.encode_rgb_video((_figure((360, 480), 240, 440 - 3 * (1 - np.cos(2 * np.pi * t / 16)) / 2,
                                    cx=180 + 2 * np.sin(2 * np.pi * t / 16), noise_seed=t)
                            for t in range(40)), clips / "idle.mp4", 24)
    pose = _figure((1280, 720), 0.48 * 720, 0.92 * 720)
    imgio.save(root / "jump_pose.png", pose)
    up = [0, 0, 0, 10, 25, 40, 50, 55, 50, 40, 25, 10, 0, 0, 0, 0]
    imgio.encode_rgb_video((_figure((448, 252), 0.48 * 252, 0.92 * 252 - up[min(t, 15)], noise_seed=50 + t)
                            for t in range(24)), clips / "jump.mp4", 24)


def _run_config(root, jump_extra):
    cfg = root / "character.toml"
    cfg.write_text(f"""[character]
name = "t"
target_height = 64
scale_reference = "idle"

[[animation]]
name = "idle"
clip = "clips/idle.mp4"
kind = "cycle"
loop_start = 8
loop_length = 16

[[animation]]
name = "jump"
clip = "clips/jump.mp4"
kind = "oneshot"
loop = false
trim = [0, 16]
{jump_extra}
""", encoding="utf-8")
    return cfg


def _sheet_bodies(out, name):
    g = json.loads((out / "sheets" / "1x" / f"{name}.json").read_text(encoding="utf-8"))
    img = imgio.load(out / "sheets" / "1x" / f"{name}.png")
    w, h = g["cell"]["w"], g["cell"]["h"]
    cells = [img[r * h:(r + 1) * h, c * w:(c + 1) * w, 3] for r, c in (divmod(i, g["cols"]) for i in range(g["count"]))]
    return [align._measure(a) for a in cells]


@pytest.fixture(scope="module")
def two_resolutions(tmp_path_factory):
    root = tmp_path_factory.mktemp("two_res")
    _clips(root)
    return root


def test_run_brings_a_clip_from_a_16x9_pose_to_the_reference_size(two_resolutions, capsys):
    cfg = _run_config(two_resolutions, 'pose = "jump_pose.png"')
    assert cli.run_character(cfg, strict=False) in (0, 2)
    log = capsys.readouterr().out
    assert "jump: escala del clip ×" in log and "→ 64 px" in log
    assert "! jump" not in log
    out = two_resolutions / "out"
    idle = _sheet_bodies(out, "idle")
    jump = _sheet_bodies(out, "jump")
    assert abs(np.median([m["ground"] - m["bbox"][1] for m in idle]) - 64) <= 1
    assert abs((jump[0]["ground"] - jump[0]["bbox"][1]) - 64) <= 1  # el frame 0 del salto, parado
    assert abs(jump[0]["ground"] - np.median([m["ground"] for m in idle])) <= 1  # misma línea de piso
    prov = json.loads((out / "provenance.json").read_text(encoding="utf-8"))
    assert prov["animations"]["jump"]["scale"]["source"] == "pose"
    assert prov["animations"]["jump"]["scale"]["scale"] > 1.9


def test_run_warns_when_clips_differ_and_nothing_is_declared(two_resolutions, capsys):
    cfg = _run_config(two_resolutions, "")
    assert cli.run_character(cfg, strict=False) in (0, 2)
    log = capsys.readouterr().out
    assert "! jump: el frame 0 mide" in log and "no declara escala" in log
    jump = _sheet_bodies(two_resolutions / "out", "jump")
    assert abs((jump[0]["ground"] - jump[0]["bbox"][1]) - 32) <= 2  # con la escala única, a la mitad
