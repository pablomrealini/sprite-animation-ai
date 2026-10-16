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
