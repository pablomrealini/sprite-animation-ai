import numpy as np
import pytest
from PIL import Image

from spritepipe import pose

MAGENTA = (255, 0, 255)


def _concept(path):
    """Cuerpo 60×241 y arma 160×20, opacos; sombra de piso semitransparente bajo los pies; ruido."""
    a = np.zeros((300, 200, 4), np.uint8)
    a[250:261, 20:181] = (0, 0, 0, 100)  # sombra, más ancha que las piernas
    a[20:261, 70:130] = (200, 120, 60, 255)  # cuerpo
    a[100:120, 20:181] = (60, 60, 60, 255)  # arma: lleva el bbox a lo ancho de la sombra
    a[2:6, 2:6] = (255, 255, 255, 8)  # ruido de alfa
    Image.fromarray(a, "RGBA").save(path)


def test_pad_places_character_and_drops_floor_shadow(tmp_path):
    src, dst = tmp_path / "concept.png", tmp_path / "pose.png"
    _concept(src)
    info = pose.pad(src, dst, size=(320, 180), height=0.5, feet=0.75)
    out = np.asarray(Image.open(dst))
    assert out.shape == (180, 320, 3)
    assert info["sprite"] == [60, 90]  # 241 px de alto llevados al 50% de 180
    assert info["at"] == [130, 45]  # centrado, con los pies en la fila 135
    assert (out[135:] == MAGENTA).all()  # nada debajo de la línea de pies
    assert (out[134, 155] != MAGENTA).any()  # las piernas llegan a la línea de pies
    assert np.abs(out[133, 133].astype(int) - MAGENTA).max() <= 2  # la sombra al costado de las piernas se fue
    assert (out[:40] == MAGENTA).all()  # el ruido de arriba no agrandó el bbox ni quedó pintado


def test_pad_feet_line_is_configurable(tmp_path):
    src = tmp_path / "concept.png"
    _concept(src)
    info = pose.pad(src, tmp_path / "jump.png", size=(320, 180), height=0.5, feet=0.92)
    assert info["at"][1] == round(180 * 0.92) - 90


def test_pad_rejects_concepts_without_transparency(tmp_path):
    src = tmp_path / "flat.png"
    Image.new("RGB", (50, 50), MAGENTA).save(src)
    with pytest.raises(ValueError, match="transparencia"):
        pose.pad(src, tmp_path / "out.png")


def test_pad_rejects_feet_above_head(tmp_path):
    src = tmp_path / "concept.png"
    _concept(src)
    with pytest.raises(ValueError):
        pose.pad(src, tmp_path / "out.png", height=0.6, feet=0.5)
