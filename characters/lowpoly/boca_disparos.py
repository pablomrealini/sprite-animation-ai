"""La boca del arma en las animaciones de disparo que traen el destello del video (out/fx/<anim>_muzzle.json).

En esos cuadros, lo más adelante del personaje es la punta del rayo, no la boca: la arena (y measure) pondría ahí la
salida de la bala. Acá la boca sale de la franja roja del arma: en el último cuadro de cada tiro (apuntando, apagado,
sin rayo) se mide la distancia de la punta de la franja a la boca, y en cada cuadro la boca es la punta de la franja más
esa distancia. Mismo formato que el que escribe remove_flash, que la arena ya lee.

Uso (desde la raíz del repo, después de `spritepipe run characters/lowpoly/character.toml`):

    uv run --project pipeline python characters/lowpoly/boca_disparos.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
ANIMS = ["shoot", "shoot2h", "crouch_shoot"]  # los tiros con destello del video; el último cuadro es apuntar apagado


def cells(variant: str, anim: str) -> tuple[list[np.ndarray], dict]:
    meta = json.loads((OUT / "sheets" / variant / f"{anim}.json").read_text(encoding="utf-8"))
    im = np.array(Image.open(OUT / "sheets" / variant / f"{anim}.png").convert("RGBA"))
    cw, ch, cols = meta["cell"]["w"], meta["cell"]["h"], meta["cols"]
    out = [im[(i // cols) * ch:(i // cols + 1) * ch, (i % cols) * cw:(i % cols + 1) * cw] for i in range(meta["count"])]
    return out, meta


def stripe(cell: np.ndarray, rows: tuple[int, int], x_min: int) -> tuple[int, float] | None:
    """Punta derecha y centro de la franja roja del arma, en las filas del arma y a la derecha del cuerpo."""
    c = cell.astype(int)
    r, g, b, a = c[..., 0], c[..., 1], c[..., 2], c[..., 3]
    red = (a > 200) & (r > 150) & (g < 90) & (b < 90)
    red[: rows[0]] = red[rows[1]:] = False
    red[:, :x_min] = False
    ys, xs = np.nonzero(red)
    if not len(xs):
        return None
    tip = int(xs.max())
    return tip, float(ys[xs >= tip - 3].mean())


def main() -> None:
    idx = json.loads((OUT / "lowpoly.json").read_text(encoding="utf-8"))
    (OUT / "fx").mkdir(exist_ok=True)
    for anim in ANIMS:
        variants = {}
        for variant in idx["variants"]:
            cs, meta = cells(variant, anim)
            cw, ch = meta["cell"]["w"], meta["cell"]["h"]
            px, py = cw * 0.5, ch * meta["pivot"]["y"]
            rest = cs[-1]
            a = rest[..., 3] > 128
            ys, xs = np.nonzero(a)
            # el arma en reposo: lo más adelante del personaje, y su franja roja detrás de la boca
            tip_x = int(xs.max())
            gun_rows = np.nonzero(a[:, tip_x - 2:tip_x + 1].any(1))[0]
            g0, g1 = int(gun_rows.min()), int(gun_rows.max()) + 1
            band = (max(0, g0 - (g1 - g0)), min(ch, g1 + (g1 - g0)))
            x_min = int(px)  # la franja del arma está adelante del pivot (el personaje mira a la derecha)
            s0 = stripe(rest, band, x_min)
            if s0 is None:
                raise SystemExit(f"{anim} ({variant}): no encuentro la franja roja del arma en el último cuadro")
            off_x, off_y = tip_x - s0[0], (g0 + g1) / 2 - s0[1]
            frames = []
            for i, c in enumerate(cs):
                s = stripe(c, (max(0, band[0] - 10), min(ch, band[1] + 10)), x_min) or s0
                x, y = s[0] + off_x + 0.5, s[1] + off_y + 0.5
                frames.append({"frame": i, "name": f"{anim}/{i:04d}", "x": round(x, 2), "y": round(y, 2),
                               "dx": round(x - px, 2), "dy": round(y - py, 2)})
            variants[variant] = {"cell": {"w": cw, "h": ch}, "pivot_px": {"x": px, "y": round(py, 2)}, "frames": frames}
            print(f"  {anim} {variant}: boca dx {[f['dx'] for f in frames]}")
        (OUT / "fx" / f"{anim}_muzzle.json").write_text(json.dumps({
            "note": (f"Boca del arma por frame de {anim}, medida por la franja roja del arma (boca_disparos.py): en los "
                     "cuadros con el destello del video, lo más adelante es la punta del rayo. x,y en px de la celda; "
                     "dx,dy relativos al pivot (y hacia abajo). Con flipX, invertí dx."),
            "animation": anim, "variants": variants}, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"✓ {OUT / 'fx'}: {', '.join(ANIMS)}")


if __name__ == "__main__":
    main()
