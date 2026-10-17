import pytest

from spritepipe import config


def _load(tmp_path, extra):
    cfg = tmp_path / "character.toml"
    cfg.write_text('[character]\nname = "t"\ntarget_height = 64\n'
                   '[[animation]]\nname = "shoot"\nclip = "shoot.mp4"\n' + extra, encoding="utf-8")
    return config.load(cfg).animations[0]


def test_remove_flash_is_off_by_default(tmp_path):
    assert _load(tmp_path, "").remove_flash is None
    assert _load(tmp_path, "remove_flash = false\n").remove_flash is None


def test_remove_flash_true_measures_everything(tmp_path):
    assert _load(tmp_path, "remove_flash = true\n").remove_flash == config.FlashRemoval()


def test_remove_flash_table_fixes_part_of_the_geometry(tmp_path):
    rf = _load(tmp_path, "[animation.remove_flash]\nband_y = [235, 275]\nhalo_x0 = 538\n").remove_flash
    assert rf == config.FlashRemoval(band_y=(235, 275), halo_x0=538)


def test_remove_flash_rejects_unknown_keys(tmp_path):
    with pytest.raises(ValueError, match="flash_x"):
        _load(tmp_path, "[animation.remove_flash]\nflash_x = [1, 2]\n")


def test_clip_key_method_reaches_its_animations(tmp_path):
    cfg = tmp_path / "character.toml"
    cfg.write_text('[character]\nname = "t"\ntarget_height = 64\n[key]\nmethod = "distance"\n'
                   '[[clip]]\nname = "c"\nfile = "c.mp4"\nkey_method = "chroma"\n'
                   '[[animation]]\nname = "a"\nclip = "c"\n'
                   '[[animation]]\nname = "b"\nclip = "b.mp4"\n', encoding="utf-8")
    ch = config.load(cfg)
    a, b = ch.animations
    assert ch.key_method == "distance"
    assert a.key_method == "chroma" and b.key_method is None
    from spritepipe import cli
    assert cli.anim_key(ch, a).key_method == "chroma" and cli.anim_key(ch, b).key_method == "distance"


def test_clip_key_method_is_validated(tmp_path):
    import pytest
    cfg = tmp_path / "character.toml"
    cfg.write_text('[character]\nname = "t"\ntarget_height = 64\n'
                   '[[animation]]\nname = "a"\nclip = "a.mp4"\nkey_method = "magic"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="key_method"):
        config.load(cfg)


def test_frames_picks_native_frames_by_hand(tmp_path):
    one = 'kind = "oneshot"\n'
    assert _load(tmp_path, one + "frames = [46, 48, 50, 44]\n").frames == (46, 48, 50, 44)
    for extra, err in (("frames = [1, 2]\ntrim = [0, 4]\n", "trim"), ("frames = []\n", "lista"),
                       ("frames = [-1]\n", "lista")):
        with pytest.raises(ValueError, match=err):
            _load(tmp_path, one + extra)
    with pytest.raises(ValueError, match="oneshot"):
        _load(tmp_path, 'kind = "cycle"\nframes = [1, 2]\n')
