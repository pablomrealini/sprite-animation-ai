"""Paletas de las arenas: un cambio de color sacado de dos imágenes con la misma composición.

Pablo trae la imagen de una arena con otro color (por ejemplo, refs/refineria_paleta_pablo.webp, la referencia con el fondo
más apagado y las plataformas en un tono más bajo). Como las dos tienen la misma composición, se puede medir qué color
pasó a qué color: `fit_lut` arma una tabla de 17 × 17 × 17 colores (un LUT 3D) que lleva los de la original a los de la
nueva, y `apply_lut` la aplica a cualquier imagen (la lámina, las piezas pintadas, las del kit), con una fuerza de 0 a 1.
Sin scipy: sólo numpy y PIL, como el resto del build.

uso (desde la raíz del repo), para ver cómo queda:
    uv run --project pipeline python prototypes/arena/paleta.py ORIGINAL NUEVA LAMINA SALIDA

`lut_payload` deja la tabla lista para meterla en la página (base64, n³ × 3 bytes, r mayor, después g, después b):
el juego la puede aplicar al prearmar cada capa, mezclada con la fuerza que diga el panel de color.
"""
import base64
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

N = 17


def _blur3(v: np.ndarray, s: float = 1.2) -> np.ndarray:
    r = int(3 * s)
    k = np.exp(-np.arange(-r, r + 1) ** 2 / (2 * s * s))
    k /= k.sum()
    for ax in range(3):
        v = np.apply_along_axis(lambda x: np.convolve(np.pad(x, r, mode="edge"), k, mode="valid"), ax, v)
    return v


def fit_lut(src: Path, dst: Path, n: int = N) -> np.ndarray:
    """La tabla (n, n, n, 3), de 0 a 1, que lleva los colores de `src` a los de `dst` (misma composición)."""
    a = Image.open(src).convert("RGB")
    b = Image.open(dst).convert("RGB").resize(a.size, Image.LANCZOS)
    # un poco borrosas las dos: no coinciden píxel a píxel, y así cada color se compara con su zona
    A = np.asarray(a.filter(ImageFilter.GaussianBlur(2))).astype(float) / 255
    B = np.asarray(b.filter(ImageFilter.GaussianBlur(2))).astype(float) / 255
    idx = np.clip(np.rint(A * (n - 1)).astype(int), 0, n - 1)
    flat = ((idx[..., 0] * n + idx[..., 1]) * n + idx[..., 2]).ravel()
    cnt = np.bincount(flat, minlength=n ** 3).astype(float)
    grid = np.stack(np.meshgrid(*[np.linspace(0, 1, n)] * 3, indexing="ij"), -1).reshape(-1, 3)
    sums = np.stack([np.bincount(flat, weights=B[..., c].ravel(), minlength=n ** 3) for c in range(3)], -1)
    # el corrimiento medio de cada celda, suavizado y pesado por cuántos píxeles cayeron en ella: las celdas sin
    # píxeles toman el de sus vecinas, y lejos de todo queda el color sin tocar
    delta = np.where(cnt[:, None] > 0, sums / np.maximum(cnt[:, None], 1) - grid, 0)
    w = cnt.reshape(n, n, n)
    den = _blur3(w)
    num = np.stack([_blur3(delta[:, c].reshape(n, n, n) * w) for c in range(3)], -1)
    d = np.where(den[..., None] > 1e-6, num / np.maximum(den[..., None], 1e-6), 0)
    return np.clip(grid.reshape(n, n, n, 3) + d, 0, 1)


def apply_lut(im: Image.Image, lut: np.ndarray, strength: float = 1.0) -> Image.Image:
    """`im` con la tabla aplicada (interpolación trilineal), mezclada con la original según `strength`. Respeta el alfa."""
    n = lut.shape[0]
    rgba = im.convert("RGBA")
    X0 = np.asarray(rgba).astype(float)
    X = X0[..., :3] / 255 * (n - 1)
    i0 = np.clip(np.floor(X).astype(int), 0, n - 2)
    f = X - i0
    out = 0
    for dr in (0, 1):
        for dg in (0, 1):
            for db in (0, 1):
                wgt = ((f[..., 0] if dr else 1 - f[..., 0]) * (f[..., 1] if dg else 1 - f[..., 1])
                       * (f[..., 2] if db else 1 - f[..., 2]))
                out = out + wgt[..., None] * lut[i0[..., 0] + dr, i0[..., 1] + dg, i0[..., 2] + db]
    rgb = X0[..., :3] + (out * 255 - X0[..., :3]) * strength
    res = np.concatenate([rgb, X0[..., 3:]], -1)
    res = Image.fromarray(np.clip(res + 0.5, 0, 255).astype(np.uint8), "RGBA")
    return res if im.mode == "RGBA" else res.convert("RGB")


def lut_payload(lut: np.ndarray) -> dict:
    """La tabla para la página: {"n": 17, "data": base64 de n³ × 3 bytes}."""
    q = np.clip(np.rint(lut * 255), 0, 255).astype(np.uint8)
    return {"n": int(lut.shape[0]), "data": base64.b64encode(q.tobytes()).decode()}


def main() -> None:
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    src, dst, plate, out = map(Path, sys.argv[1:])
    lut = fit_lut(src, dst)
    a = Image.open(src).convert("RGB")
    b = np.asarray(Image.open(dst).convert("RGB").resize(a.size, Image.LANCZOS)).astype(float)
    err0 = np.abs(np.asarray(a).astype(float) - b).mean()
    err1 = np.abs(np.asarray(apply_lut(a, lut)).astype(float) - b).mean()
    apply_lut(Image.open(plate), lut).save(out)
    print(f"✓ {out}  (diferencia media con la imagen nueva: {err0:.1f} sin la paleta, {err1:.1f} con la paleta)")


if __name__ == "__main__":
    main()
