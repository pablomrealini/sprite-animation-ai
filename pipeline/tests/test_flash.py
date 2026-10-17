import numpy as np
import pytest

from spritepipe import config, flash, imgio

BG = (240, 40, 240)
YELLOW = (255, 240, 120)
GLOW = (244, 90, 210)  # amarillo al 25% sobre el fondo: el halo real es suave (suma < 120 contra el fondo)
OUTLINE = (25, 25, 25)


def _frame(recoil=0, fire=True):
    """Personaje que mira a la derecha con un arma; con fire, fogonazo delante de la boca y halo."""
    a = np.full((160, 240, 3), BG, np.uint8)
    a[20:150, 40:100] = OUTLINE  # cuerpo
    a[21:149, 41:99] = (210, 140, 90)
    x1 = 160 - recoil  # la boca es la columna x1 - 1
    a[70:84, 60 - recoil:x1] = OUTLINE  # cañón con contorno
    a[71:83, 61 - recoil:x1 - 1] = (90, 90, 100)
    a[62:92, 95 - recoil:110 - recoil] = (220, 160, 110)  # mano, arriba y abajo del cañón
    a[60:70, 120 - recoil:126 - recoil] = OUTLINE  # mira
    if fire:
        a[55:100, x1 + 1:215] = YELLOW  # fogonazo
        a[62:70, x1 - 12:x1] = GLOW  # halo arriba del cañón, cerca de la boca
        a[84:90, x1 - 12:x1] = GLOW  # y abajo
    return a


def test_detect_geometry_on_the_pose_without_flash():
    geo = flash.detect_geometry(_frame(fire=False))
    assert geo["search_x"][0] < 159 < geo["search_x"][1]
    assert geo["band_y"][0] < 70 and geo["band_y"][1] > 83
    assert geo["flash_y"][0] <= 55 and geo["flash_y"][1] >= 100
    assert 126 <= geo["halo_x0"] < 159  # después de la mira, antes de la boca


@pytest.mark.parametrize("recoil", [0, 3])
def test_remove_paints_the_flash_and_keeps_the_gun(recoil):
    geo = flash.detect_geometry(_frame(fire=False))
    clean = _frame(recoil, fire=False)
    out, m = flash.remove(_frame(recoil), geo)
    assert m == {"x": 159 - recoil, "y": 76.5}
    margin = np.zeros(out.shape[:2], bool)
    margin[[69, 84], 148 - recoil:160 - recoil] = True  # la fila pegada al contorno se conserva: es su antialias
    flashy = (out == YELLOW).all(2) | (out == GLOW).all(2)
    assert not (flashy & ~margin).any()  # no queda fogonazo ni halo
    keep = np.zeros(out.shape[:2], bool)
    keep[:, :159 - recoil + flash.TIP_GAP] = True
    keep &= ~margin
    assert (out[keep] == clean[keep]).all()  # el cañón, la mira y la mano no se tocan


def test_remove_reports_frames_without_a_muzzle():
    out, m = flash.remove(np.full((160, 240, 3), BG, np.uint8), flash.detect_geometry(_frame(fire=False)))
    assert m is None and (out == BG).all()


def test_run_uses_fixed_geometry_and_measures_the_rest(tmp_path):
    raw = tmp_path / "raw"
    for i, img in enumerate([_frame(fire=False), _frame(2), _frame(1)]):
        imgio.save(raw / imgio.frame_name(i), img)
    res = flash.run(raw, tmp_path / "noflash", config.FlashRemoval(halo_x0=140))
    assert res["geometry"]["halo_x0"] == 140
    assert res["measured"] == ["band_y", "flash_y", "search_x"]
    assert [m["x"] for m in res["muzzle"]] == [159, 157, 158]
    assert res["missed_frames"] == [] and res["muzzle_x"] == [157, 159]
    assert (tmp_path / "noflash" / "muzzle.json").exists()
    assert len(imgio.frames(tmp_path / "noflash")) == 3


def test_anchors_map_video_px_to_cell_px_relative_to_pivot():
    # Canvas de 200×150 con pivot en (100, 140); celda a la mitad. El frame 0 del video cae en
    # pivot + shift, y se usa el centro del píxel de la boca.
    fx = flash.anchors("shoot", [{"frame": 0, "x": None, "y": None}, {"frame": 1, "x": 100, "y": 50.0}],
                       native_indices=[1, 0], shifts=[[-80, -110], [-80, -110]],
                       canvas={"w": 200, "h": 150}, pivot_px={"x": 100, "y": 140},
                       variants={"1x": {"w": 100, "h": 75}}, pivot_norm_y=140 / 150)
    v = fx["variants"]["1x"]
    assert v["pivot_px"] == {"x": 50.0, "y": 70.0}
    assert v["frames"][0] == {"frame": 0, "name": "shoot/0000", "native_frame": 1,
                              "x": 60.25, "y": 40.25, "dx": 10.25, "dy": -29.75}
    assert v["frames"][1]["x"] is None and v["frames"][1]["native_frame"] == 0


# --- method = "shape": personaje sin contorno (low-poly), boca con disco cian -----------------------------------
LP_BG = (196, 45, 125)
CYAN = (60, 230, 240)


def _lowpoly(dx=0, dy=0, beam=False):
    """Cuerpo rojo y arma gris oscuro sin contorno, con la tapa de la boca y su disco cian; con beam, un rayo cian
    pegado al disco que llega al borde. dx, dy corren todo el personaje."""
    a = np.full((200, 320, 3), LP_BG, np.uint8)
    a[30 + dy:190 + dy, 60 + dx:130 + dx] = (231, 38, 33)  # cuerpo (alto 160): se mueve con el arma, como en el clip
    a[90 + dy:104 + dy, 120 + dx:170 + dx] = (62, 62, 68)  # cuerpo del arma
    a[94 + dy:100 + dy, 140 + dx:160 + dx] = (220, 30, 30)  # la franja roja (sin ella, un gris liso se desliza)
    a[86 + dy:108 + dy, 170 + dx:176 + dx] = (45, 45, 50)  # tapa de la boca
    a[91 + dy:103 + dy, 176 + dx:179 + dx] = CYAN  # disco cian
    a[108 + dy:122 + dy, 128 + dx:136 + dx] = (62, 62, 68)  # empuñadura
    if beam:
        a[92 + dy:102 + dy, 179 + dx:] = (200, 250, 255)  # rayo: centro casi blanco pegado al disco
        a[88 + dy:92 + dy, 179 + dx:300] = CYAN
    return a


def test_shape_geometry_finds_the_cyan_muzzle():
    geo = flash.shape_geometry(_lowpoly())
    assert geo["front"] == 178 and geo["disk_y"] == [91, 103]


def test_shape_removes_the_beam_and_keeps_the_muzzle(tmp_path):
    raw = tmp_path / "raw"
    shots = [(0, 0, False), (3, -2, True), (-4, 2, True), (1, 0, False)]
    for i, (dx, dy, beam) in enumerate(shots):
        imgio.save(raw / imgio.frame_name(i), _lowpoly(dx, dy, beam))
    res = flash.run(raw, tmp_path / "out", config.FlashRemoval(method="shape"))
    assert [m["x"] for m in res["muzzle"]] == [178 + dx for dx, _, _ in shots]
    for i, (dx, dy, beam) in enumerate(shots):
        out = imgio.load(tmp_path / "out" / imgio.frame_name(i))
        clean = _lowpoly(dx, dy, beam=False)
        assert (out == clean).all()  # sin rayo y con la tapa y el disco enteros
    assert (tmp_path / "out" / "muzzle.json").exists()


def test_shape_rejects_fixed_geometry():
    with pytest.raises(ValueError, match="shape"):
        config._flash("shoot", {"method": "shape", "band_y": [1, 2]})
    assert config._flash("shoot", {"method": "shape"}).method == "shape"


def test_shape_holds_the_gun_when_the_flash_hides_it(tmp_path):
    """Un frame donde el arma no se parece a la del frame 0 (el fogonazo la ilumina): no se va a la deriva."""
    raw = tmp_path / "raw"
    frames = [_lowpoly(), _lowpoly(1, 0), _lowpoly(2, 0), _lowpoly(2, 1), _lowpoly(3, 1, beam=True)]
    lit = _lowpoly(3, 1, beam=True)
    lit[80:130, 110:180] = (255, 250, 240)  # el arma tapada por el destello
    frames.append(lit)
    frames.append(_lowpoly(4, 1))
    for i, img in enumerate(frames):
        imgio.save(raw / imgio.frame_name(i), img)
    res = flash.run(raw, tmp_path / "out", config.FlashRemoval(method="shape"))
    xs = [m["x"] for m in res["muzzle"]]
    assert xs[:5] == [178, 179, 180, 180, 181]
    assert res["held_frames"] == [5] and xs[5] == 181  # quedó donde estaba
    assert xs[6] == 182  # y se recupera
