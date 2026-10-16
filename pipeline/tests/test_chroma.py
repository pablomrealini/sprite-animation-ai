import numpy as np
import pytest

from spritepipe import chroma, config, key


@pytest.mark.parametrize("color", ["#FFFFFF", "#FAFAFA", "#808080", "#000000"])
def test_white_or_gray_background_has_no_key_strength(color):
    # Sin canal dominante no hay "cantidad de pantalla": sin el guard, screen() reducía un array
    # vacío y el key se caía con un ValueError en el primer frame de fondo blanco.
    k = chroma.parse_hex(color)
    assert chroma.key_strength(k) == 0.0
    assert chroma.method_for(k) == "distance"


def test_tinted_white_measured_on_a_real_clip_uses_distance():
    assert chroma.method_for(chroma.parse_hex("#FCFAFA")) == "distance"  # el fondo del run del comando


@pytest.mark.parametrize("color", ["#00FF00", "#FF00FF", "#F828F4"])
def test_green_and_magenta_use_chroma(color):
    k = chroma.parse_hex(color)
    assert chroma.key_strength(k) >= chroma.CHROMA_MIN_STRENGTH
    assert chroma.method_for(k) == "chroma"


def _character(tmp_path, color="auto"):
    cfg = tmp_path / "character.toml"
    cfg.write_text(f'[character]\nname = "t"\ntarget_height = 64\n[key]\ncolor = "{color}"\n'
                   '[[animation]]\nname = "idle"\nclip = "idle.mp4"\n', encoding="utf-8")
    return config.load(cfg)


@pytest.mark.parametrize("color", ["auto", "#FFFFFF"])
def test_key_frame_on_exact_white_background(tmp_path, color):
    img = np.full((64, 64, 3), 255, np.uint8)
    img[16:48, 16:48] = 20  # contorno oscuro
    img[18:46, 18:46] = (200, 60, 40)
    ch = _character(tmp_path, color)
    fixed = None if color == "auto" else chroma.parse_hex(color)
    rgba, k, method, mode = key.key_frame(img, ch, fixed)
    assert (method, mode) == ("distance", "connected")
    assert np.allclose(k, 1.0)
    assert rgba[0, 0, 3] == 0 and rgba[63, 63, 3] == 0
    assert rgba[32, 32, 3] == 255 and rgba[17, 17, 3] == 255


def test_forced_distance_keeps_a_red_character_on_dull_magenta(tmp_path):
    # El fondo del run del ranger (#BB3772) tiene rojo dominante: con chroma, el rojo de la armadura
    # se toma como pantalla y se pierde. Con method = "distance" el personaje queda opaco y rojo.
    bg = (187, 55, 114)
    img = np.empty((64, 64, 3), np.uint8); img[:] = bg
    img[16:48, 16:48] = 20                 # contorno oscuro
    img[18:46, 18:46] = (225, 30, 30)      # armadura roja
    cfg = tmp_path / "character.toml"
    cfg.write_text('[character]\nname = "t"\ntarget_height = 64\n[key]\ncolor = "auto"\nmethod = "distance"\n'
                   '[[animation]]\nname = "run"\nclip = "run.mp4"\n', encoding="utf-8")
    ch = config.load(cfg)
    assert chroma.method_for(chroma.parse_hex("#BB3772")) == "chroma"   # lo que elegiría solo
    rgba, k, method, mode = key.key_frame(img, ch, None)
    assert (method, mode) == ("distance", "connected")
    assert rgba[0, 0, 3] == 0
    assert rgba[32, 32, 3] == 255 and rgba[32, 32, 0] > 200 and rgba[32, 32, 2] < 60
