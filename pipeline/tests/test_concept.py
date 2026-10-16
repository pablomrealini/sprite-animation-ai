import numpy as np
import pytest
from PIL import Image

from spritepipe import concept

WHITE = (254, 254, 254)
INK = (12, 12, 12)


def _box(a, x0, y0, x1, y1, fill, sole=True, t=4):
    """Rectángulo con contorno negro de `t` px; sin `sole`, abajo no lleva contorno."""
    a[y0:y1, x0:x1] = INK
    a[y0 + t:y1 - (t if sole else 0), x0 + t:x1 - t] = fill


def _concept(path, dx=0, boots=(200, 40, 40), sole=True):
    """Cabeza con casco blanco, torso, dos botas separadas por un hueco blanco, la línea de sombra
    por debajo (más ancha que las botas) y una mancha suelta pegada al borde derecho."""
    a = np.full((300, 220, 3), WHITE, np.uint8)
    _box(a, 70 + dx, 20, 130 + dx, 64, (250, 248, 244))  # casco: blanco cálido, encerrado
    _box(a, 60 + dx, 60, 140 + dx, 200, (60, 60, 60))
    _box(a, 64 + dx, 196, 96 + dx, 262, boots, sole)
    _box(a, 104 + dx, 196, 136 + dx, 262, boots, sole)
    a[262:268, 30 + dx:170 + dx] = INK  # sombra: une las botas y encierra el hueco
    a[100:116, 208:220] = INK  # basura en el borde
    Image.fromarray(a).save(path)


def test_clean_drops_shadow_gap_and_junk(tmp_path):
    _concept(tmp_path / "c.png")
    rgba, info = concept.clean(np.asarray(Image.open(tmp_path / "c.png")))
    alpha = rgba[..., 3]
    assert alpha[40, 100] == 255  # el casco blanco queda opaco
    assert alpha[230, 100] == 0  # el hueco entre las botas es fondo
    assert alpha[265, 100] == 0  # y la línea que lo cerraba también
    assert alpha[265, 40] == 0 and alpha[265, 160] == 0  # la línea a los costados de las botas
    assert alpha[260, 80] == 255 and alpha[260, 120] == 255  # las botas llegan al piso
    assert (alpha[:, 200:] == 0).all()  # la basura del borde
    assert info["background"] == 254
    assert (rgba[alpha == 0] == 0).all()


def test_clean_keeps_white_boots_whose_sole_is_the_shadow(tmp_path):
    _concept(tmp_path / "c.png", boots=(245, 245, 245), sole=False)
    rgba, _ = concept.clean(np.asarray(Image.open(tmp_path / "c.png")))
    alpha = rgba[..., 3]
    assert alpha[240, 80] == 255 and alpha[240, 120] == 255  # el relleno blanco de las botas
    assert alpha[265, 80] == 255  # la línea debajo de la bota es la suela
    assert alpha[230, 100] == 0  # el hueco del medio igual se va


def test_roster_shares_canvas_floor_and_pivot(tmp_path):
    _concept(tmp_path / "a.png")
    _concept(tmp_path / "b.png", dx=-25)
    infos = concept.roster([tmp_path / "a.png", tmp_path / "b.png"], tmp_path / "out", size=(256, 320), feet=0.9,
                           magenta=True)
    for info in infos:
        alpha = np.asarray(Image.open(info["out"]))[..., 3]
        assert alpha.shape == (320, 256)
        ys, xs = np.nonzero(alpha > 127)
        assert ys.max() == round(320 * 0.9) - 1  # mismo piso
        feet = xs[ys >= ys.max() - concept.FEET_PX]
        assert (feet.min() + feet.max() + 1) / 2 == pytest.approx(128, abs=0.5)  # botas centradas
        assert Image.open(info["magenta"]).size == (1920, 1080)
    assert infos[0]["height"] == infos[1]["height"]  # escala nativa, sin re-muestrear


def test_roster_refuses_a_canvas_too_small(tmp_path):
    _concept(tmp_path / "a.png")
    with pytest.raises(ValueError, match="no entra"):
        concept.roster([tmp_path / "a.png"], tmp_path / "out", size=(60, 320))
