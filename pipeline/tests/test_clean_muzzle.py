from spritepipe import clean


def test_muzzle_limit_with_arm_extended_uses_the_extended_frames():
    # los primeros frames con el brazo abajo (borde 100) y después extendido (~140)
    rights = [100] * 5 + [140, 141, 139, 140, 160, 140]
    assert clean.muzzle_limit(rights) == 140 + clean.MUZZLE_GAP


def test_muzzle_limit_when_the_arm_never_moves_cuts_at_the_usual_edge():
    # idle con el arma siempre al frente: el borde típico es la boca y los picos son destellos
    rights = [137] * 20 + [148, 147, 146]
    assert clean.muzzle_limit(rights) == 137 + clean.MUZZLE_GAP


def test_muzzle_limit_steady_ignores_spark_frames():
    # idle con destellos en 1 de cada 4 frames: sin steady, los destellos pasan por "brazo extendido"
    rights = [753] * 5 + ([753] * 3 + [795]) * 25
    assert clean.muzzle_limit(rights) > 780
    assert clean.muzzle_limit(rights, steady=True) == 753 + clean.MUZZLE_GAP
