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


def _floor_frame():
    # un "personaje" rojo grueso parado sobre una raya de sombra fina y oscura que sale a la izquierda, sobre magenta apagado
    img = np.zeros((120, 120, 3), np.uint8); img[:] = (196, 45, 125)
    img[30:100, 50:80] = (220, 40, 40)       # cuerpo y botas
    img[97:99, 20:52] = (25, 20, 30)         # la raya: 2 px de alto, pegada a la bota
    return img


def test_floor_streak_removes_the_thin_dark_shadow_line_and_keeps_the_boots(tmp_path):
    img = _floor_frame()
    cfg = tmp_path / "character.toml"
    cfg.write_text('[character]\nname = "t"\ntarget_height = 64\n[key]\ncolor = "#C42D7D"\nmethod = "distance"\nfloor_streak = true\n'
                   '[[animation]]\nname = "idle"\nclip = "idle.mp4"\n', encoding="utf-8")
    ch = config.load(cfg)
    rgba, *_ = key.key_frame(img, ch, chroma.parse_hex("#C42D7D"))
    assert rgba[98, 25:45, 3].max() == 0          # la raya, fuera
    assert rgba[60:99, 55:75, 3].min() == 255     # el cuerpo y las botas, enteros


def test_floor_streak_is_off_by_default(tmp_path):
    img = _floor_frame()
    cfg = tmp_path / "character.toml"
    cfg.write_text('[character]\nname = "t"\ntarget_height = 64\n[key]\ncolor = "#C42D7D"\nmethod = "distance"\n'
                   '[[animation]]\nname = "idle"\nclip = "idle.mp4"\n', encoding="utf-8")
    ch = config.load(cfg)
    rgba, *_ = key.key_frame(img, ch, chroma.parse_hex("#C42D7D"))
    assert rgba[98, 25:45, 3].min() > 0           # sin la opción, la raya queda


def _rim_frame():
    # un arma gris oscura sobre magenta apagado, con el halo claro del render pegado por afuera (lila, 1 px) y una mira
    # roja de 3 px en el borde de arriba, que es un detalle de verdad
    img = np.zeros((120, 120, 3), np.uint8); img[:] = (196, 45, 125)
    img[40:80, 30:90] = (70, 70, 76)          # el arma
    img[40:80, 90] = (210, 140, 205)          # el halo lila, a la derecha
    img[79, 30:90] = (120, 50, 85)            # abajo, una fila mezclada con el fondo (más o menos mitad y mitad)
    img[37:40, 50:60] = (220, 40, 40)         # la mira roja, arriba
    return img


def _rim_cfg(tmp_path, extra=""):
    cfg = tmp_path / "character.toml"
    cfg.write_text('[character]\nname = "t"\ntarget_height = 64\n[key]\ncolor = "#C42D7D"\nmethod = "distance"\n' + extra +
                   '[[animation]]\nname = "idle"\nclip = "idle.mp4"\n', encoding="utf-8")
    return config.load(cfg)


def test_edge_unmix_removes_the_light_rim_and_the_mixed_row_and_keeps_details(tmp_path):
    img = _rim_frame()
    before, *_ = key.key_frame(img, _rim_cfg(tmp_path), chroma.parse_hex("#C42D7D"))
    rgba, *_ = key.key_frame(img, _rim_cfg(tmp_path, "edge_unmix = true\n"), chroma.parse_hex("#C42D7D"))
    assert before[45:75, 90, 3].min() > 200                  # sin la opción, el halo queda opaco
    assert rgba[45:75, 90, 3].max() < 140                     # con la opción, casi transparente
    assert np.abs(rgba[45:75, 90, :3].astype(int) - (70, 70, 76)).max() < 25   # y del color del arma
    row = rgba[79, 40:80]
    assert 60 < row[:, 3].mean() < 200                        # la fila mezclada: semitransparente
    assert row[:, 2].astype(int).mean() < 110                 # y sin el azul del fondo
    assert rgba[38, 52:58, 3].min() == 255                    # la mira roja queda entera
    assert rgba[38, 52:58, 0].min() > 190 and rgba[38, 52:58, 2].max() < 70
    assert rgba[45:75, 35:85, 3].min() == 255                 # adentro, nada


def test_edge_unmix_is_off_by_default(tmp_path):
    img = _rim_frame()
    rgba, *_ = key.key_frame(img, _rim_cfg(tmp_path), chroma.parse_hex("#C42D7D"))
    assert rgba[45:75, 90, 3].min() > 200


def _holes_frame():
    # un cuerpo rojo con un casco blanco arriba, sobre magenta apagado: un bolsillo de fondo entre partes rojas y una
    # mota del mismo tamaño en el casco (los dos, 0,2% del personaje)
    img = np.zeros((200, 200, 3), np.uint8); img[:] = (196, 45, 125)
    img[40:90, 50:150] = (235, 235, 235)       # casco
    img[90:180, 50:150] = (220, 40, 40)        # cuerpo
    img[60:64, 90:94] = (196, 45, 125)         # la mota en el casco: 16 px
    img[130:134, 90:94] = (196, 45, 125)       # el bolsillo entre el brazo y el pecho: 16 px
    return img


def test_low_hole_max_frac_opens_pockets_but_keeps_specks_in_white_and_inpaints_them(tmp_path):
    img = _holes_frame()
    ch = _rim_cfg(tmp_path, "hole_max_frac = 0.001\nhole_inpaint = true\n")
    rgba, *_ = key.key_frame(img, ch, chroma.parse_hex("#C42D7D"))
    assert rgba[131:133, 91:93, 3].max() == 0                 # el bolsillo, transparente
    assert rgba[61:63, 91:93, 3].min() == 255                 # la mota del casco, rellena
    assert rgba[61:63, 91:93, :3].min() > 200                 # y blanca como el casco, no magenta


def test_hole_fill_keeps_the_background_color_without_inpaint(tmp_path):
    img = _holes_frame()
    rgba, *_ = key.key_frame(img, _rim_cfg(tmp_path), chroma.parse_hex("#C42D7D"))   # 1% de siempre: los dos rellenos
    assert rgba[131:133, 91:93, 3].min() == 255 and rgba[61:63, 91:93, 3].min() == 255
    assert rgba[61:63, 91:93, 1].max() < 80                   # del color del fondo (sin hole_inpaint)
