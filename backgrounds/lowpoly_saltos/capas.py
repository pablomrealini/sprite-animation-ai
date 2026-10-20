"""Las dos capas de un cuadro de efecto de salto: lo que va detrás del personaje y lo que va delante.

Regla (en px del juego, con el ancla en los pies: x = 0 al medio, y = 0 en la línea del piso, para arriba negativo):
la ventana del cuerpo es |x| < MEDIO_ANCHO y y < -FRANJA. Lo que cae adentro va detrás del personaje (así nunca le
tapa la cara ni el cuerpo); todo lo demás va delante: lo que está a los costados y la franja de abajo, que pisa las
botas. El borde de la ventana se funde en FUNDIDO px en las dos capas, para que el corte no se vea donde el personaje
no lo tapa. Las dos capas tienen el mismo lienzo y la misma ancla: se dibujan en el mismo lugar, una antes y otra
después del personaje.
"""
import numpy as np

MEDIO_ANCHO = 22   # el personaje mide ~32 de ancho (HALF_W 16) y ~105 de alto
FRANJA = 14        # lo que está a menos de esto sobre el piso va siempre delante (pisa las botas)
FUNDIDO = 6


def split_layers(rgba, ax, ay, medio=MEDIO_ANCHO, franja=FRANJA, fundido=FUNDIDO):
    """rgba: el cuadro (h, w, 4) uint8; (ax, ay): el ancla en px del cuadro. Devuelve (atras, adelante)."""
    h, w = rgba.shape[:2]
    xs = np.abs(np.arange(w) - ax)[None, :].astype(np.float32)
    ys = (np.arange(h) - ay)[:, None].astype(np.float32)     # negativo arriba del piso
    # cuánto de adentro de la ventana está cada px (1 adentro, 0 afuera, rampa de `fundido` px en el borde)
    inx = np.clip((medio - xs) / fundido + 0.5, 0, 1)
    iny = np.clip((-franja - ys) / fundido + 0.5, 0, 1)
    back_w = inx * iny
    a = rgba[..., 3].astype(np.float32)
    atras, adelante = rgba.copy(), rgba.copy()
    atras[..., 3] = (a * back_w).round().astype(np.uint8)
    adelante[..., 3] = (a * (1 - back_w)).round().astype(np.uint8)
    return atras, adelante
