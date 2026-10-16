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
