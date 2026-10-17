"""Apaga el arma de una pose: pinta el disco cian de la boca (y su anillo) del gris oscuro del arma, con el sombreado.

Kling dibuja fogonazo y rayos cuando el arma tiene el disco brillante; con el arma apagada y un prompt que sólo apunta,
el video sale sin fogonazo (reporte_idle.md, "Prueba sin fogonazo"). El disco lo puede volver a pintar el juego, que
sabe dónde está la boca en cada cuadro. Sirve para concepts RGBA y para poses 16:9.

Uso (desde la raíz del repo):

    uv run --project pipeline python characters/lowpoly/apagar_arma.py entrada.png salida.png
"""

import sys

import cv2
import numpy as np
from PIL import Image


def apagar_rgb(rgb_u8: np.ndarray, alpha: np.ndarray | None = None) -> tuple[np.ndarray, int]:
    """El disco cian (y su anillo) pintado del gris del arma, con el sombreado. Devuelve la imagen y los px pintados."""
    rgb = rgb_u8.astype(np.float32)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    core = (g > 120) & (b > 120) & (r < 150) & ((g + b) / 2 - r > 60)
    if alpha is not None:
        core &= alpha > 128
    k = max(3, round(min(rgb.shape[:2]) / 80)) | 1  # radio del anillo, a escala de la imagen
    near = cv2.dilate(core.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    disk = near & ((g + b) / 2 - r > 2) & (b > r + 2)
    gray = np.clip(40 + 0.25 * rgb.mean(-1), 40, 90)
    rgb[disk] = np.stack([gray, gray, gray * 1.08], -1)[disk]
    return rgb.round().astype(np.uint8), int(disk.sum())


def apagar(src: str, dst: str) -> int:
    im = Image.open(src)
    has_alpha = "A" in im.getbands()
    a = np.array(im.convert("RGBA" if has_alpha else "RGB"))
    rgb, n = apagar_rgb(a[..., :3], a[..., 3] if has_alpha else None)
    out = np.dstack([rgb, a[..., 3]]) if has_alpha else rgb
    Image.fromarray(out, "RGBA" if has_alpha else "RGB").save(dst)
    return n


if __name__ == "__main__":
    print(f"✓ {sys.argv[2]}: {apagar(sys.argv[1], sys.argv[2])} px del disco apagados")
