"""Limpieza previa (clean.py) con clips sintéticos como los de Davinci: fondo en degradé, sombra de piso,
rayos, humo y una barra que cruza el cuadro. También [[clip]], reverse y color_matrix en la config."""

import json

import cv2
import numpy as np
import pytest

from spritepipe import cli, clean, config, imgio, select

TOP, BOTTOM = np.array([185, 40, 112]), np.array([236, 92, 158])  # magenta apagado en degradé
OUTLINE, RED, WHITE, SKIN, GUN = (18, 14, 16), (228, 32, 36), (245, 244, 238), (240, 196, 150), (62, 60, 64)
GLOVE = (220, 30, 30)
CORE, HALO = (250, 255, 255), (70, 225, 255)  # rayo: centro blanco y halo cian
BAR = (58, 56, 62)


def _bg(W, H):
    t = np.linspace(0, 1, H)[:, None, None]
    return np.broadcast_to(TOP + (BOTTOM - TOP) * t, (H, W, 3)).round().astype(np.uint8).copy()


def _scene(W=1280, H=720, aim=True, beam=False, beam_behind=False, smoke=False, shadow=True, bar=False,
           glow=False):
    """Personaje de ~470 px (a 720p) que mira a la derecha. Devuelve el frame y la geometría en px.

    bar: True cruza todo el cuadro; "right" arranca en la mano y llega sólo al borde derecho."""
    s = H / 720
    img = _bg(W, H)
    cx, feet = 500 * s, 600 * s
    top = feet - 470 * s

    def rect(x0, y0, x1, y1, color, pad=0):
        p = round(pad * s)
        cv2.rectangle(img, (round(x0 * s) - p, round(y0 * s) - p), (round(x1 * s) + p, round(y1 * s) + p), color, -1)

    g = {"cx": cx, "feet": feet, "top": top}
    if shadow:  # mismo tono que el fondo de su fila, más oscura
        cv2.ellipse(img, (round(cx), round(feet + 4 * s)), (round(170 * s), round(16 * s)), 0, 0, 360,
                    (img[round(feet), 5] * 0.5).round().tolist(), -1)
    if bar:  # barra gris, con los guantes encima
        x0 = 440 if bar == "right" else 0
        rect(x0, 118, W / s, 136, OUTLINE)
        rect(x0, 121, W / s, 133, BAR)
        top = 160 * s
        for x in (450, 550):
            rect(x - 14, 120, x + 14, 290, OUTLINE)  # brazos levantados, con contorno
            rect(x - 10, 124, x + 10, 286, RED)
            rect(x - 18, 112, x + 18, 142, GLOVE)
        g.update(bar_y=(118 * s, 136 * s), gloves=[(432 * s, 468 * s), (532 * s, 568 * s)])
    T = top / s
    rect(430, T + 230, 570, 600, OUTLINE)  # piernas
    rect(440, T + 240, 560, 596, (70, 80, 110))
    rect(420, T + 110, 580, T + 250, OUTLINE)  # torso
    rect(430, T + 120, 570, T + 240, RED)
    cv2.circle(img, (round(cx), round(top + 60 * s)), round(62 * s), OUTLINE, -1)  # casco
    cv2.circle(img, (round(cx), round(top + 60 * s)), round(54 * s), WHITE, -1)
    rect(470, T + 6, 530, T + 30, RED)
    gy = T + 150
    if aim and not bar:  # brazo extendido con la pistola; la boca en x = 780
        rect(560, gy - 18, 700, gy + 18, OUTLINE)
        rect(565, gy - 13, 695, gy + 13, SKIN)
        rect(690, gy - 16, 780, gy + 12, OUTLINE)
        rect(694, gy - 12, 776, gy + 8, GUN)
        rect(776, gy - 4, 780, gy + 2, HALO)  # la punta cian de la pistola
        if glow:  # disparando, el cuerpo del arma brilla cian
            rect(700, gy - 8, 770, gy + 4, HALO)
        g.update(muzzle_x=780 * s, gun_y=gy * s)
    elif not bar:  # brazo bajo, pegado al cuerpo
        rect(560, T + 120, 600, T + 260, OUTLINE)
        rect(565, T + 125, 595, T + 255, SKIN)
    if beam and aim and not bar:  # rayo pegado a la boca hasta el borde: el centro blanco toca el arma
        rect(780, gy - 12, W / s, gy + 8, HALO)
        rect(778, gy - 4, W / s, gy + 1, CORE)
    if beam_behind:  # un rayo que cruza por detrás: sale desde el borde izquierdo y toca la espalda
        rect(0, T + 180, 425, T + 196, HALO)
        rect(0, T + 185, 425, T + 191, CORE)
        g["back_x"] = 420 * s
    if smoke:  # humo suelto arriba a la derecha y chispas cian
        cv2.circle(img, (round(950 * s), round(170 * s)), round(45 * s), (150, 138, 146), -1)
        for x, y in ((880, 330), (1010, 420), (1100, 260)):
            cv2.circle(img, (round(x * s), round(y * s)), round(5 * s), HALO, -1)
        g["smoke"] = (950 * s, 170 * s)
    return img, g


def _is_bg(out, bg):
    return (np.abs(out.astype(np.int16) - bg).max(2) == 0)


def _bg_color(res):
    return np.array([int(res["bg"][i:i + 2], 16) for i in (1, 3, 5)])


# --- fondo --------------------------------------------------------------------


def test_background_follows_a_gradient_and_takes_the_floor_shadow():
    img, g = _scene()
    bg = clean.bg_mask(img, clean.bg_rows(img))
    plain = _bg(1280, 720)
    char_free = np.ones(bg.shape, bool)
    char_free[round(g["top"]) - 70:round(g["feet"]) + 30, 380:820] = False
    assert bg[char_free].mean() > 0.999  # el degradé entero es fondo, arriba y abajo
    shadow = (np.abs(img.astype(np.int16) - plain).sum(2) > 30)
    shadow[:round(g["feet"]) + 1] = False  # sólo lo que la sombra oscurece debajo de los pies
    assert shadow.sum() > 1000 and bg[shadow].all()
    torso = img[round(g["top"] + 150), 440:560]
    assert not clean.bg_mask(torso[None], clean.bg_rows(img)[[round(g["top"] + 150)]]).any()


@pytest.mark.parametrize("scene", [{"bar": True}, {"bar": "right"}, {"beam": True}])
def test_rows_crossed_by_a_bar_or_a_beam_keep_the_background_color(scene):
    """Una barra que cruza el cuadro se interpola; si llega a un solo borde, o es un rayo, se mide del otro."""
    img, g = _scene(**scene)
    rows = clean.bg_rows(img)
    plain = clean.bg_rows(_bg(1280, 720))
    y0, y1 = (round(v) for v in g["bar_y"]) if "bar" in scene else (round(g["gun_y"]) - 12, round(g["gun_y"]) + 8)
    assert np.abs(rows[y0:y1] - plain[y0:y1]).max() < 6


# --- efectos ------------------------------------------------------------------


def _clean_one(img, **params):
    out, res = clean.run(np.stack([img]), config.Clean(**params))
    return out[0], res


def test_smoke_sparks_and_shadow_are_painted_with_one_flat_color():
    img, g = _scene(smoke=True)
    out, res = _clean_one(img)
    bg = _bg_color(res)
    flat = _is_bg(out, bg)
    sx, sy = (round(v) for v in g["smoke"])
    assert flat[sy - 40:sy + 40, sx - 40:sx + 40].all()  # humo
    assert flat[round(g["feet"]) + 3:round(g["feet"]) + 15, 340:660].all()  # sombra de piso
    assert flat[:, :300].all() and flat[:, 1000:].all()  # degradé y chispas
    y = round(g["gun_y"])
    assert (out[y, 700:770] == img[y, 700:770]).all()  # el arma queda como estaba
    assert (out[y - 2, 776:780] == img[y - 2, 776:780]).all()  # y la punta cian, que toca el arma


def test_a_beam_that_touches_the_gun_needs_cut_muzzle():
    lowered = [_scene(aim=False)[0] for _ in range(5)]
    aiming = [_scene(beam=i % 2 == 0)[0] for i in range(8)]
    _, g = _scene()
    frames = np.stack(lowered + aiming)
    y, mx = round(g["gun_y"]), round(g["muzzle_x"])

    out, res = clean.run(frames, config.Clean())
    assert res["muzzle_x"] is None
    assert not _is_bg(out[5][y - 2:y + 1], _bg_color(res))[:, mx + 50:].all()  # el centro blanco sobrevive

    out, res = clean.run(frames, config.Clean(cut_muzzle=True))
    assert mx <= res["muzzle_x"] <= mx + clean.MUZZLE_GAP + 2
    for f, src in zip(out[5:], frames[5:]):
        flat = _is_bg(f, _bg_color(res))
        assert flat[:, res["muzzle_x"] + 1:].all()
        assert flat[:, :400].all()  # el rayo llega al borde derecho: esas filas se miden del izquierdo
        assert (f[y - 12:y + 9, 560:mx - 3] == src[y - 12:y + 9, 560:mx - 3]).all()  # brazo y arma enteros


def test_cut_muzzle_brings_back_the_glow_of_the_gun():
    frames = np.stack([_scene(aim=False)[0] for _ in range(5)] + [_scene(glow=True, beam=i % 2 == 0)[0] for i in range(6)])
    _, g = _scene()
    y = round(g["gun_y"])
    out, res = clean.run(frames, config.Clean())
    assert _is_bg(out[6], _bg_color(res))[y - 2:y + 1, 710:760].all()  # sin cut_muzzle, el arma queda hueca
    out, res = clean.run(frames, config.Clean(cut_muzzle=True))
    for f, src in zip(out[5:], frames[5:]):
        assert (f[y - 12:y + 9, 694:770] == src[y - 12:y + 9, 694:770]).all()  # el arma, sólida
        assert _is_bg(f, _bg_color(res))[:, res["muzzle_x"] + 1:].all()


def test_cut_left_takes_the_beam_behind_the_back():
    frames = np.stack([_scene(beam_behind=i == 0)[0] for i in range(3)])  # el rayo pasa en un frame
    _, g = _scene(beam_behind=True)
    out, res = clean.run(frames, config.Clean())
    assert not _is_bg(out[0], _bg_color(res))[:, :200].all()  # pegado a la espalda, cuenta como personaje
    out, res = clean.run(frames, config.Clean(cut_left=True))
    assert _is_bg(out[0], _bg_color(res))[:, :res["cut_left_x"]].all()
    assert 0 < res["cut_left_x"] < g["back_x"] - 10  # el corte no toca el cuerpo
    torso_y = round(g["top"] + 200)
    assert (out[0][torso_y, 440:560] == frames[0][torso_y, 440:560]).all()


@pytest.mark.parametrize("bar", [True, "right"])
def test_prop_rows_erase_a_bar_but_keep_the_gloves_and_helmet(bar):
    img, g = _scene(bar=bar)
    out, res = _clean_one(img)
    y0, y1 = (round(v) for v in g["bar_y"])
    assert not _is_bg(out, _bg_color(res))[y0:y1, 600:].all()  # sin prop_rows la barra queda: toca el guante

    out, res = _clean_one(img, prop_rows=True)
    flat = _is_bg(out, _bg_color(res))
    (a0, a1), (b0, b1) = ((round(x0), round(x1)) for x0, x1 in g["gloves"])
    assert flat[y0:y1, :a0 - 10].all() and flat[y0:y1, b1 + 10:].all()  # la barra afuera de los guantes
    for x0, x1 in g["gloves"]:
        gx = round((x0 + x1) / 2)
        assert (out[y0 + 4:y1 - 4, gx] == img[y0 + 4:y1 - 4, gx]).all()  # los guantes
    hy = round(g["top"] + 60)
    assert (out[hy, 470:530] == img[hy, 470:530]).all()  # el casco


def test_distances_scale_with_the_clip_height():
    img, g = _scene(W=640, H=360, smoke=True)
    out, res = _clean_one(img)
    flat = _is_bg(out, _bg_color(res))
    assert flat[:, :150].all() and flat[:, 500:].all()
    y = round(g["gun_y"])
    assert (out[y, 350:385] == img[y, 350:385]).all()


# --- caché --------------------------------------------------------------------


def _clip(path, n=12, W=640, H=360):
    frames = [_scene(W, H, aim=t >= 5, beam=t >= 5 and t % 2 == 1, smoke=t % 3 == 0)[0] for t in range(n)]
    imgio.encode_rgb_video(frames, path, 24, crf=0, pix_fmt="yuv444p")
    return path


def test_ensure_caches_by_clip_and_parameters(tmp_path):
    raw = _clip(tmp_path / "raw.mp4")
    a = clean.ensure(raw, config.Clean(), tmp_path / "c", "shoot")
    assert not a["cached"] and a["path"].exists() and a["frames"] == 12
    b = clean.ensure(raw, config.Clean(), tmp_path / "c", "shoot")
    assert b["cached"] and b["path"] == a["path"]
    c = clean.ensure(raw, config.Clean(cut_muzzle=True), tmp_path / "c", "shoot")
    assert not c["cached"] and c["path"] != a["path"] and c["muzzle_x"] is not None
    d = clean.ensure(raw, config.Clean(), tmp_path / "c", "shoot", matrix="bt601")
    assert not d["cached"] and d["path"] != a["path"]
    meta = json.loads(a["path"].with_suffix(".json").read_text(encoding="utf-8"))
    assert meta["params"] == {"cut_muzzle": False, "cut_left": False, "prop_rows": False}


def test_color_matrix_overrides_the_untagged_default(tmp_path):
    raw = tmp_path / "raw.mp4"
    imgio.encode_rgb_video([np.full((64, 64, 3), RED, np.uint8)] * 2, raw, 24, crf=0, pix_fmt="yuv444p")
    info = imgio.probe(raw)
    tagged = imgio.read_video(raw, info)[0, 32, 32]
    assert np.abs(tagged.astype(int) - RED).max() <= 2
    as601 = imgio.read_video(raw, info, "bt601")[0, 32, 32]
    assert np.abs(as601.astype(int) - tagged).max() > 10  # el rojo se corre con la matriz equivocada


# --- config -------------------------------------------------------------------


def _cfg(tmp_path, body):
    p = tmp_path / "character.toml"
    p.write_text('[character]\nname = "t"\ntarget_height = 64\n' + body, encoding="utf-8")
    return p


CLIP = """
[[clip]]
name = "shoot2h"
file = "clips/raw/r02.mp4"
color_matrix = "bt601"
clean = { cut_muzzle = true }
body_height_px = 606
model = "seedance-2.0"
prompt = "prompts/shoot2h.txt"
"""


def test_animations_inherit_their_clip(tmp_path):
    ch = config.load(_cfg(tmp_path, CLIP + """
[[animation]]
name = "shoot2h_in"
clip = "shoot2h"
kind = "oneshot"
trim = [6, 14]

[[animation]]
name = "shoot2h_out"
clip = "shoot2h"
kind = "oneshot"
trim = [6, 14]
reverse = true
body_height_px = 600
clean = false
"""))
    a, b = ch.animations
    assert a.clip == (tmp_path / "clips/raw/r02.mp4").resolve() and a.source == "shoot2h"
    assert a.clean == config.Clean(cut_muzzle=True) and a.color_matrix == "bt601"
    assert a.body_height_px == 606 and a.model == "seedance-2.0" and a.prompt.name == "shoot2h.txt"
    assert not a.reverse and b.reverse
    assert b.body_height_px == 600 and b.clean is None  # la animación pisa lo del clip


def test_clean_as_a_table_in_the_animation(tmp_path):
    ch = config.load(_cfg(tmp_path, '[[animation]]\nname = "hang"\nclip = "clips/hang.mp4"\n'
                                    '[animation.clean]\nprop_rows = true\n'))
    assert ch.animations[0].clean == config.Clean(prop_rows=True) and ch.animations[0].source is None
    ch = config.load(_cfg(tmp_path, '[[animation]]\nname = "run"\nclip = "clips/run.mp4"\nclean = true\n'))
    assert ch.animations[0].clean == config.Clean()


@pytest.mark.parametrize("body, match", [
    ('[[animation]]\nname = "a"\nclip = "x.mp4"\nclean = { scale = 0.8 }\n', "body_height_px"),
    ('[[animation]]\nname = "a"\nclip = "x.mp4"\nclean = { cut_mussle = true }\n', "cut_mussle"),
    ('[[animation]]\nname = "a"\nclip = "x.mp4"\nclean = { cut_muzzle = 1 }\n', "true o false"),
    ('[[animation]]\nname = "a"\nclip = "x.mp4"\nclean = "yes"\n', "true o una tabla"),
    ('[[animation]]\nname = "a"\nclip = "x.mp4"\ncolor_matrix = "srgb"\n', "bt601"),
    ('[[animation]]\nname = "a"\nclip = "x.mp4"\nreverse = 1\n', "reverse"),
    ('[[clip]]\nname = "s"\nfile = "s.mp4"\n[[animation]]\nname = "a"\nclip = "shot"\n', "ni un .*clip.*s"),
    ('[[clip]]\nname = "s"\n[[animation]]\nname = "a"\nclip = "s"\n', "name y file"),
    ('[[clip]]\nname = "s"\nfile = "s.mp4"\n[[clip]]\nname = "s"\nfile = "t.mp4"\n', "dos"),
    ('[[clip]]\nname = "s"\nfile = "s.mp4"\nloop_start = 3\n', "loop_start"),
])
def test_config_rejects(tmp_path, body, match):
    with pytest.raises(ValueError, match=match):
        config.load(_cfg(tmp_path, body))


# --- reverse ------------------------------------------------------------------


class _An:
    def __init__(self, diff):
        self.diff_char = np.array(diff, float)
        self.n = len(diff) + 1


def test_reverse_trims_the_still_frames_at_the_start_of_the_range():
    an = _An([0, 0, 5, 5, 5, 5, 0.1, 0.1, 0.1, 0])  # quieto, se mueve, queda quieto
    fwd = select.trim_oneshot(an, (2, 10), True)
    assert (fwd["start"], fwd["length"]) == (2, 5)  # la cola quieta se va
    assert select.trim_oneshot(an, (0, 7), True) == {"start": 0, "length": 7, "static_tail_trimmed": 0}
    rev = select.trim_oneshot(an, (0, 7), True, reverse=True)
    assert (rev["start"], rev["length"]) == (2, 5)  # al revés, la cola es el principio: se van 0 y 1


# --- punta a punta ------------------------------------------------------------


def test_run_cleans_once_per_clip_and_plays_a_range_backwards(tmp_path, capsys):
    _clip(tmp_path / "clips" / "raw" / "s01.mp4", n=24)
    cfg = _cfg(tmp_path, """
[[clip]]
name = "shoot"
file = "clips/raw/s01.mp4"
clean = { cut_muzzle = true }

[[animation]]
name = "aim"
clip = "shoot"
kind = "oneshot"
trim = [2, 10]
pick = "first"
trim_static_tail = false

[[animation]]
name = "lower"
clip = "shoot"
kind = "oneshot"
trim = [2, 10]
pick = "first"
trim_static_tail = false
reverse = true

[[animation]]
name = "fire"
clip = "shoot"
kind = "cycle"
loop_start = 10
loop_length = 8
""")
    assert cli.run_character(cfg, strict=False) in (0, 2)
    log = capsys.readouterr().out
    assert log.count("limpieza (cut_muzzle)") == 1 and "lower  ←  shoot (s01.mp4)  al revés" in log
    cleaned = list((tmp_path / "work" / "00_clean").glob("shoot-*.mp4"))
    assert len(cleaned) == 1

    prov = json.loads((tmp_path / "out" / "provenance.json").read_text(encoding="utf-8"))
    aim, lower = prov["animations"]["aim"], prov["animations"]["lower"]
    assert aim["timing"]["native_indices"] == [2, 4, 6, 8, 9]
    assert lower["timing"]["native_indices"] == [9, 7, 5, 3, 2] and lower["reverse"]
    assert aim["clean"]["file"] == str(cleaned[0]) and aim["clip"].endswith("s01.mp4")
    mx = aim["clean"]["muzzle_x"]
    for name in ("aim", "fire"):  # fondo plano y nada delante de la boca, frame por frame
        for p in imgio.frames(tmp_path / "work" / name / "01_raw"):
            f = imgio.load(p).astype(np.int16)
            assert np.abs(f[:, mx + 2:] - _bg_color(aim["clean"])).max() <= 2
            assert np.abs(f[:, :40] - _bg_color(aim["clean"])).max() <= 2

    assert cli.run_character(cfg, strict=False) in (0, 2)
    assert "(del cache)" in capsys.readouterr().out
