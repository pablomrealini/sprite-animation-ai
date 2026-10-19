"""La boca del arma en las animaciones de disparo que traen el destello del video (out/fx/<anim>_muzzle.json).

En esos cuadros, lo más adelante del personaje es la punta del rayo, no la boca: la arena (y measure) pondría ahí la
salida de la bala. Acá la boca se mide en el último cuadro de cada tiro (apuntando, apagado, sin rayo): lo más adelante
del personaje, a media altura de la punta del arma. En los otros cuadros (el retroceso) se sigue el arma con template
matching de la punta (silueta y luminancia, que no cambian con la luz cian del cañón prendido) y la boca se corre lo
mismo. Antes se seguía la franja roja del arma: eran 4–26 px rojos sueltos y la medida saltaba hasta 13 px de 1x con
cambios chicos del key (2026-10-18). Mismo formato que el que escribe remove_flash, que la arena ya lee.

Uso (desde la raíz del repo, después de `spritepipe run characters/lowpoly/character.toml`):

    uv run --project pipeline python characters/lowpoly/boca_disparos.py
"""

from __future__ import annotations

import json
from pathlib import Path

import cv2
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


def track(rest: np.ndarray, cell: np.ndarray, mx: int, my: int, gh: int) -> tuple[int, int]:
    """Cuánto se corrió el arma de `cell` contra la de `rest`: template matching de la punta (3 alturas del cañón hacia
    atrás de la boca y media hacia adelante, 2 de alto), en alfa y luminancia, buscando hasta 1,5 alturas alrededor."""
    feat = lambda c: np.dstack([c[..., 3] / 255.0, (c[..., :3].astype(np.float32) @ [0.3, 0.59, 0.11]) / 255.0  # noqa: E731
                                * (c[..., 3] / 255.0)]).astype(np.float32)
    x0, x1, y0, y1 = mx - 3 * gh, mx + gh // 2, my - gh, my + gh
    r = int(1.5 * gh)
    tpl = feat(rest)[y0:y1, x0:x1]
    win = feat(cell)[y0 - r:y1 + r, x0 - r:x1 + r]
    res = cv2.matchTemplate(win, tpl, cv2.TM_SQDIFF)
    _, _, (bx, by), _ = cv2.minMaxLoc(res)
    return bx - r, by - r


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
            # el arma en reposo: lo más adelante del personaje, a media altura de la punta
            tip_x = int(xs.max())
            gun_rows = np.nonzero(a[:, tip_x - 2:tip_x + 1].any(1))[0]
            g0, g1 = int(gun_rows.min()), int(gun_rows.max()) + 1
            my = (g0 + g1) / 2
            frames = []
            for i, c in enumerate(cs):
                dx, dy = track(rest, c, tip_x, round(my), g1 - g0)
                x, y = tip_x + dx + 0.5, my + dy
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
