"""Post de los fondos, sin IA: key del fondo plano, transparencia, piezas, costura y recorte."""

import cv2
import numpy as np
import pytest

from spritepipe import bgpost, imgio

GREEN, OUTLINE, WALL = (0, 255, 0), (13, 15, 24), (60, 40, 90)


def _skyline(w=1200, h=400, seed=1, bg=GREEN):
    """Edificios con contorno negro que no empalman: el último no sigue en el primero."""
    rng = np.random.default_rng(seed)
    img = np.zeros((h, w, 3), np.uint8)
    img[:] = bg
    x = 0
    while x < w:
        bw, bh = int(rng.integers(40, 120)), int(rng.integers(80, 300))
        cv2.rectangle(img, (x, h - bh), (x + bw, h), WALL, -1)
        cv2.rectangle(img, (x, h - bh), (x + bw, h), OUTLINE, 4)
        x += bw + int(rng.integers(8, 40))
    return img


def _rgba(img, alpha=None):
    a = np.full(img.shape[:2], 255, np.uint8) if alpha is None else alpha
    return np.dstack([img, a])


def _sky(w=900, h=300):
    """Degradé vertical con una onda que no cierra en x: costura suave pero visible."""
    y = np.linspace(0, 1, h)[:, None]
    x = np.linspace(0, 1, w)[None, :]
    r = 40 + 60 * y + 30 * x
    g = 20 + 30 * y + 0 * x
    b = 90 + 80 * y - 20 * x
    return _rgba(np.dstack([r, g, b]).clip(0, 255).astype(np.uint8))


def test_key_out_finds_the_real_green_and_keeps_the_buildings():
    img = _skyline()
    off = img.copy()
    off[(img == GREEN).all(-1)] = (24, 236, 30)  # el verde que devuelve el modelo nunca es #00FF00
    rgba, info = bgpost.key_out(off, "#00FF00")
    assert info["key_color"] == "#18EC1E"
    bg = (img == GREEN).all(-1)
    assert (rgba[bg, 3] == 0).mean() > 0.99
    inner = cv2.erode((~bg).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
    assert (rgba[inner, 3] == 255).all()
    assert (rgba[rgba[..., 3] == 0, :3] == 0).all()  # RGB en 0 donde no hay alfa


def test_alpha_report_flags_a_painted_checkerboard():
    yy, xx = np.mgrid[:256, :256]
    checker = np.where(((yy // 16 + xx // 16) % 2)[..., None] == 0, 255, 204).repeat(3, -1).astype(np.uint8)
    checker[100:160, 100:160] = OUTLINE
    rep = bgpost.alpha_report(_rgba(checker), "cutout")
    assert rep["verdict"] == "fail" and "damero" in rep["flags"][0]
    rep = bgpost.alpha_report(_rgba(np.full((256, 256, 3), 255, np.uint8)), "cutout")
    assert rep["verdict"] == "fail" and "damero" not in rep["flags"][0]


def test_alpha_report_by_kind():
    sky = _sky()
    assert bgpost.alpha_report(sky, "opaque")["verdict"] == "ok"
    layer, _ = bgpost.key_out(_skyline(), "#00FF00")
    assert bgpost.alpha_report(layer, "layer")["verdict"] == "ok"
    rep = bgpost.alpha_report(layer, "cutout")  # el skyline llega abajo y a los costados
    assert rep["verdict"] == "warn" and "bottom" in rep["flags"][0]
    covered = layer.copy()
    covered[:5, :, 3] = 255
    assert "tapa el cielo" in bgpost.alpha_report(covered, "layer")["flags"][0]


def test_alpha_report_finds_leftover_key():
    layer, _ = bgpost.key_out(_skyline(), "#00FF00")
    layer[300:340, 500:540] = (30, 220, 40, 255)  # un parche verde opaco que no se keyeó
    rep = bgpost.alpha_report(layer, "layer", "#00FF00")
    assert any("color de key" in f for f in rep["flags"])


@pytest.mark.parametrize("method", ["cut", "crossfade"])
def test_fix_seam_makes_the_wrap_invisible(method):
    img = _sky() if method == "crossfade" else bgpost.key_out(_skyline(), "#00FF00")[0]
    before = bgpost.seam_score(img)
    assert before["verdict"] == "fail"
    out, how = bgpost.fix_seam(img, method, 0.12)
    after = bgpost.seam_score(out)
    assert after["verdict"] == "ok" and after["score"] < before["score"] / 4
    assert out.shape[1] == img.shape[1] - how["overlap_px"] and out.shape[0] == img.shape[0]
    # Lo de adentro no cambia: después de la franja, la capa es la original
    w = how["overlap_px"]
    assert np.abs(out[:, w + 1:].astype(int) - img[:, w + 1:img.shape[1] - w].astype(int)).max() <= 1


def test_cut_goes_through_the_air_between_buildings():
    layer, _ = bgpost.key_out(_skyline(), "#00FF00")
    out, how = bgpost.fix_seam(layer, "cut", 0.12)
    assert how["cut_error"] == 0  # hay un camino que sólo pasa por aire en las dos franjas
    vals = set(map(tuple, out[..., :3][out[..., 3] == 255].reshape(-1, 3)))
    assert vals <= {WALL, OUTLINE}  # ningún contorno doble ni color mezclado en lo opaco


def test_vertical_seam_is_the_same_on_the_other_axis():
    img = _sky().transpose(1, 0, 2).copy()
    assert bgpost.seam_score(img, "y")["verdict"] == "fail"
    out, _ = bgpost.fix_seam(img, "crossfade", 40, "y")
    assert bgpost.seam_score(out, "y")["verdict"] == "ok" and out.shape[1] == img.shape[1]


def test_a_tileable_image_scores_low():
    x = np.linspace(0, 2 * np.pi, 600, endpoint=False)
    row = (120 + 80 * np.sin(3 * x)).astype(np.uint8)
    img = _rgba(np.repeat(np.repeat(row[None, :, None], 200, 0), 3, 2))
    assert bgpost.seam_score(img)["verdict"] == "ok"


def test_a_fix_that_does_not_help_is_discarded(tmp_path, monkeypatch):
    imgio.save(tmp_path / "far.png", _skyline())
    real = bgpost.fix_seam

    def worse(img, method, overlap, axis="x"):
        out, how = real(img, method, overlap, axis)
        out = out.copy()
        out[:, 0] = (255, 0, 0, 255)  # una columna roja en la vuelta: peor que antes
        return out, how

    monkeypatch.setattr(bgpost, "fix_seam", worse)
    rep = bgpost.process(tmp_path / "far.png", tmp_path / "out.png", bgpost.PostSpec(expect="layer", key="#00FF00",
                                                                                     tile={"": "x"}))
    assert "fix" not in rep["seam"]["x"] and rep["seam"]["x"]["fix_discarded"]["method"] == "cut"
    assert imgio.load(tmp_path / "out.png").shape[1] == 1200  # la capa queda como estaba


def test_seam_mask_rolls_half_and_marks_the_band():
    img = _sky()
    rolled, mask = bgpost.seam_mask(img, 60)
    assert (rolled[:, 450] == img[:, 0]).all()
    assert (mask[:, 420:480, 3] == 0).all() and (mask[:, :400, 3] == 255).all()


def _sheet(sizes, gap=40, h=300, bg=GREEN):
    w = sum(s[0] for s in sizes) + gap * (len(sizes) + 1)
    img = np.zeros((h, w, 3), np.uint8)
    img[:] = bg
    x = gap
    for sw, sh in sizes:
        cv2.rectangle(img, (x, 60), (x + sw, 60 + sh), (100, 110, 140), -1)
        cv2.rectangle(img, (x, 60), (x + sw, 60 + sh), OUTLINE, 5)
        cv2.circle(img, (x + sw // 2, 60 + sh // 2), 6, (89, 227, 236), -1)  # una luz cian adentro
        x += sw + gap
    return img


def test_split_reads_left_to_right_and_drops_specks():
    img = _sheet([(80, 100), (200, 100), (80, 100)])
    img[10:13, 10:13] = OUTLINE  # una mota
    rgba, _ = bgpost.key_out(img, "#00FF00")
    pieces, notes = bgpost.split(rgba, ["edge_left", "top", "edge_right"])
    assert [p[0] for p in pieces] == ["edge_left", "top", "edge_right"]
    drawn = (img[100] != GREEN).any(-1)  # una fila que cruza las tres piezas
    runs = np.diff(np.r_[0, drawn.astype(int), 0]).nonzero()[0].reshape(-1, 2)
    assert [p[1].shape[1] for p in pieces] == [int(b - a) for a, b in runs]
    assert not notes or "manchas" in notes[0]


def test_split_with_the_wrong_count_numbers_the_pieces():
    rgba, _ = bgpost.key_out(_sheet([(80, 100), (200, 100)]), "#00FF00")
    pieces, notes = bgpost.split(rgba, ["a", "b", "c"])
    assert [p[0] for p in pieces] == ["pieza_1", "pieza_2"] and "se esperaban 3" in notes[0]


def test_split_in_two_rows():
    top = _sheet([(80, 100), (80, 100)], h=200)
    rgba, _ = bgpost.key_out(np.concatenate([top, top[:, ::-1]]), "#00FF00")
    pieces, _ = bgpost.split(rgba, [])
    ys = [p[2][1] for p in pieces]
    assert ys[0] == ys[1] < ys[2] == ys[3]


def test_process_a_kit_sheet(tmp_path):
    imgio.save(tmp_path / "kit.png", _sheet([(80, 100), (200, 100), (80, 100), (150, 110), (180, 50)]))
    spec = bgpost.PostSpec(expect="cutout", key="#00FF00", split=["edge_left", "top", "edge_right", "body", "floating"],
                           tile={"top": "x"}, same_height=True, height=64)
    rep = bgpost.process(tmp_path / "kit.png", tmp_path / "out" / "kit.png", spec)
    files = sorted(p.name for p in (tmp_path / "out" / "kit").iterdir())
    assert files == ["body.png", "edge_left.png", "edge_right.png", "floating.png", "top.png"]
    assert {f["h"] for f in rep["files"].values()} == {64}
    assert rep["alpha"]["verdict"] == "ok"
    assert "top:x" in rep["seam"] and "body:x" not in rep["seam"]
    # body (110) está a menos del 15% de la mediana (100): se escala. floating (50) queda a escala, con aire abajo
    assert rep["height"]["scales"]["body"] < 1 and rep["height"]["scales"]["floating"] == 1
    assert any("floating" in n and "aire abajo" in n for n in rep["notes"])
    floating = imgio.load(tmp_path / "out" / "kit" / "floating.png")
    assert floating[-5:, :, 3].max() == 0 and floating[:5, :, 3].max() > 0


def test_props_keep_their_relative_scale(tmp_path):
    imgio.save(tmp_path / "props.png", _sheet([(80, 60), (60, 160), (100, 120)]))
    spec = bgpost.PostSpec(expect="cutout", key="#00FF00", split=["crate", "sign", "target"], height=83)
    rep = bgpost.process(tmp_path / "props.png", tmp_path / "out" / "props.png", spec)
    hs = {k: f["h"] for k, f in rep["files"].items()}
    assert hs["sign"] == 83 and hs["crate"] < hs["target"] < hs["sign"]  # una sola escala para las tres
    assert "height" not in rep


def test_process_a_layer_keeps_the_width_when_trimming(tmp_path):
    imgio.save(tmp_path / "far.png", _skyline())
    spec = bgpost.PostSpec(expect="layer", key="#00FF00", tile={"": "x"})
    rep = bgpost.process(tmp_path / "far.png", tmp_path / "out.png", spec)
    out = imgio.load(tmp_path / "out.png")
    assert rep["seam"]["x"]["after"]["verdict"] == "ok"
    assert out.shape[1] == 1200 - rep["seam"]["x"]["fix"]["overlap_px"]  # sólo la franja de la costura
    assert rep["trim"]["image"][0] == 0 and rep["trim"]["image"][1] > 0  # recorta el aire de arriba
    assert out.shape[0] == 400 - rep["trim"]["image"][1]


def test_process_an_opaque_sky_does_not_key_or_trim(tmp_path):
    imgio.save(tmp_path / "sky.png", _sky()[..., :3])
    spec = bgpost.PostSpec(expect="opaque", key="#00FF00", tile={"": "x"}, seam="crossfade", height=150)
    rep = bgpost.process(tmp_path / "sky.png", tmp_path / "out.png", spec)
    out = imgio.load(tmp_path / "out.png")
    assert "key" not in rep and "trim" not in rep and (out[..., 3] == 255).all()
    assert out.shape[0] == 150 and rep["seam"]["x"]["after"]["verdict"] == "ok"


def test_process_with_mask_leaves_the_layer_and_writes_the_edit_files(tmp_path):
    imgio.save(tmp_path / "near.png", _skyline())
    spec = bgpost.PostSpec(expect="layer", key="#00FF00", tile={"": "x"}, seam="mask", trim=False)
    rep = bgpost.process(tmp_path / "near.png", tmp_path / "near_post.png", spec)
    assert rep["seam"]["x"]["mask"] == ["near_post.seam_x.png", "near_post.seam_x_mask.png"]
    assert (tmp_path / "near_post.seam_x_mask.png").exists()
    assert imgio.load(tmp_path / "near_post.png").shape[1] == 1200
