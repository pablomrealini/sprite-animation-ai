"""Configuración de un personaje: un archivo TOML con el personaje, sus clips y sus animaciones.

Las rutas del TOML son relativas a la carpeta del archivo. Un `[[clip]]` describe un video del que
salen varias animaciones (archivo, limpieza, pose, modelo, prompt, escala): la animación que lo nombra
en `clip` hereda todo eso y puede pisar cualquier valor. `clip` también puede ser la ruta del video.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FlashRemoval:
    """Geometría del arma en px del clip. Lo que falta se mide en el frame 0 (ver flash.py)."""

    band_y: tuple[int, int] | None = None  # filas donde se busca el contorno oscuro del cañón
    search_x: tuple[int, int] | None = None  # columnas donde puede estar la boca
    flash_y: tuple[int, int] | None = None  # filas que puede ocupar el fogonazo
    halo_x0: int | None = None  # desde acá hasta la boca sólo hay cañón (ni mano ni mira)
    method: str = "outline"  # "outline": la boca es el contorno oscuro; "shape": se sigue la forma del arma (sin contorno)


@dataclass(frozen=True)
class Clean:
    """Limpieza previa del clip, frame por frame y antes del key (ver clean.py)."""

    cut_muzzle: bool = False  # borra lo que queda delante de la boca del arma (rayos, fogonazo)
    cut_left: bool = False  # borra lo que cruza por detrás del personaje
    prop_rows: bool = False  # borra utilería dibujada que cruza el cuadro (una barra)
    muzzle_steady: bool = False  # con cut_muzzle: el arma no se mueve (un idle), la boca es el borde derecho típico


COLOR_MATRICES = ("bt601", "bt709")
# Lo que un [[clip]] le pasa a las animaciones que lo usan, además del archivo
CLIP_KEYS = ("clean", "color_matrix", "model", "prompt", "pose", "scale_pose", "pose_body_height_px",
             "body_height_px", "key_method")
KEY_METHODS = ("auto", "chroma", "distance")


@dataclass
class Animation:
    name: str
    clip: Path
    kind: str  # "cycle" (walk, run, idle) | "oneshot" (attack, hit, death)
    loop: bool  # si el engine la reproduce en loop
    pose: Path | None = None  # pose que se le pasó al modelo como primer frame (QA y escala del clip)
    # Escala del clip (ver align.py): alto del cuerpo parado en px del video de este clip. Si `pose` no es
    # de cuerpo parado (colgado, agachado): una pose parada a su misma escala, o el alto parado en px de la pose
    body_height_px: float | None = None
    scale_pose: Path | None = None
    pose_body_height_px: float | None = None
    model: str | None = None  # para el registro de procedencia
    prompt: Path | None = None
    # Búsqueda de loop (sólo cycle)
    loop_seconds: tuple[float, float] = (0.5, 2.0)
    skip_seconds: float = 0.25  # ignorar el arranque, donde el modelo "se acomoda"
    loop_start: int | None = None  # override manual, en frames nativos
    loop_length: int | None = None
    # Recorte manual (sólo oneshot), en frames nativos [inicio, fin)
    trim: tuple[int, int] | None = None
    trim_static_tail: bool = True
    # Decimación
    pick: str = "first"  # "first" | "sharpest" (el más nítido de cada grupo de K)
    holds: dict[int, float] = field(default_factory=dict)  # frame de salida -> multiplicador de duración
    # Borrar el fogonazo antes del key y exportar dónde está la boca del cañón
    remove_flash: FlashRemoval | None = None
    clean: Clean | None = None  # limpieza previa del clip; el limpio se cachea en work/00_clean/
    color_matrix: str | None = None  # pisa la matriz de color del video ("bt601" | "bt709")
    reverse: bool = False  # el tramo elegido (trim o loop, en frames del clip) se reproduce al revés
    source: str | None = None  # el [[clip]] del que sale, si sale de uno
    key_method: str | None = None  # pisa [key].method para este clip (p. ej. "chroma" con fondo magenta puro)


@dataclass
class Character:
    name: str
    root: Path
    work_dir: Path
    out_dir: Path
    style: str  # "hd" | "pixel"
    game_fps: int
    target_height: int  # alto del cuerpo en la animación de referencia, en px finales
    scale_reference: str
    body_height_px: float | None
    # Key
    key_color: str  # "auto" o "#RRGGBB"
    key_mode: str  # "auto" | "global" | "connected"
    key_method: str  # "auto" | "chroma" | "distance": forzar distancia si el personaje comparte tono con el fondo
    hole_max_frac: float
    key_tolerance: tuple[float, float]
    despill: float
    despill_band_px: int
    min_island_px: int
    # Alineación y reducción
    margin_px: int
    anchor: str  # ancla horizontal: "centroid" (centroide por animación) | "clip" (el frame 0 de cada clip)
    pixel_factor: int | None
    palette_colors: int
    palette: Path | None
    sharpen: float
    extra_scales: list[float]
    # Atlas
    atlas_max_size: int
    padding: int
    border_padding: int
    extrude: int
    power_of_two: bool
    animations: list[Animation]

    def anim_work(self, anim: Animation) -> Path:
        return self.work_dir / anim.name

    def get(self, name: str) -> Animation:
        for a in self.animations:
            if a.name == name:
                return a
        raise KeyError(f"no hay una animación llamada {name!r}")


def _path(root: Path, value: str | None) -> Path | None:
    if not value:
        return None
    p = Path(value).expanduser()
    return p if p.is_absolute() else (root / p).resolve()


def _flash(anim: str, value) -> FlashRemoval | None:
    """remove_flash = true, o una tabla [animation.remove_flash] con la geometría fija."""
    if value is None or value is False:
        return None
    if value is True:
        return FlashRemoval()
    if not isinstance(value, dict):
        raise ValueError(f"{anim}: remove_flash tiene que ser true o una tabla")
    unknown = set(value) - {"band_y", "search_x", "flash_y", "halo_x0", "method"}
    if unknown:
        raise ValueError(f"{anim}: remove_flash no conoce {', '.join(sorted(unknown))}")
    method = value.get("method", "outline")
    if method not in ("outline", "shape"):
        raise ValueError(f"{anim}: remove_flash.method tiene que ser 'outline' o 'shape'")
    if method == "shape" and set(value) - {"method"}:
        raise ValueError(f"{anim}: con method = 'shape' la geometría se mide sola; sacá {', '.join(sorted(set(value) - {'method'}))}")

    def pair(k):
        return tuple(int(v) for v in value[k]) if k in value else None

    return FlashRemoval(band_y=pair("band_y"), search_x=pair("search_x"), flash_y=pair("flash_y"),
                        halo_x0=int(value["halo_x0"]) if "halo_x0" in value else None, method=method)


def _clean(anim: str, value) -> Clean | None:
    """clean = true, o una tabla [animation.clean] / clean = { ... } con las opciones."""
    if value is None or value is False:
        return None
    if value is True:
        return Clean()
    if not isinstance(value, dict):
        raise ValueError(f"{anim}: clean tiene que ser true o una tabla")
    if "scale" in value:
        raise ValueError(f"{anim}: clean no re-escala; declará body_height_px en el [[clip]] o en la animación "
                         "(ver Escala por clip en pipeline/README.md)")
    unknown = set(value) - set(Clean.__dataclass_fields__)
    if unknown:
        raise ValueError(f"{anim}: clean no conoce {', '.join(sorted(unknown))}")
    for k, v in value.items():
        if not isinstance(v, bool):
            raise ValueError(f"{anim}: clean.{k} tiene que ser true o false")
    return Clean(**value)


def _anchor(value: str) -> str:
    if value not in ("centroid", "clip"):
        raise ValueError(f"[character] anchor tiene que ser \"centroid\" o \"clip\", no {value!r}")
    return value


def _clips(data: dict) -> dict[str, dict]:
    clips = {}
    for c in data.get("clip", []):
        name = c.get("name")
        if not name or not c.get("file"):
            raise ValueError("cada [[clip]] necesita name y file")
        if name in clips:
            raise ValueError(f"hay dos [[clip]] llamados {name!r}")
        unknown = set(c) - {"name", "file", *CLIP_KEYS}
        if unknown:
            raise ValueError(f"[[clip]] {name}: no conoce {', '.join(sorted(unknown))}")
        clips[name] = c
    return clips


def load(path: str | Path) -> Character:
    path = Path(path).resolve()
    root = path.parent
    data = tomllib.loads(path.read_text(encoding="utf-8"))

    ch = data.get("character", {})
    key = data.get("key", {})
    out = data.get("output", {})
    atlas = data.get("atlas", {})

    name = ch["name"]
    style = ch.get("style", "hd")
    if style not in ("hd", "pixel"):
        raise ValueError(f"style tiene que ser 'hd' o 'pixel', no {style!r}")

    clips = _clips(data)
    anims = []
    for a in data.get("animation", []):
        source = clips.get(a.get("clip"))
        if source:
            a = {**{k: source[k] for k in CLIP_KEYS if k in source}, **a, "clip": source["file"]}
        elif not Path(a.get("clip", "")).suffix:
            raise ValueError(f"{a['name']}: clip {a.get('clip')!r} no es un archivo ni un [[clip]]"
                             + (f" ({', '.join(clips)})" if clips else ""))
        kind = a.get("kind", "cycle")
        if kind not in ("cycle", "oneshot"):
            raise ValueError(f"{a['name']}: kind tiene que ser 'cycle' u 'oneshot'")
        trim = a.get("trim")
        for k in ("body_height_px", "pose_body_height_px"):
            v = a.get(k)
            if v is not None and not (isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0):
                raise ValueError(f"{a['name']}: {k} tiene que ser un número de px mayor que 0")
        for k in ("scale_pose", "pose_body_height_px"):
            if a.get(k) and not a.get("pose"):
                raise ValueError(f"{a['name']}: {k} necesita `pose`, la imagen que el modelo recibió como frame 0")
        if a.get("scale_pose") and a.get("pose_body_height_px"):
            raise ValueError(f"{a['name']}: scale_pose o pose_body_height_px, no los dos")
        if a.get("color_matrix") not in (None, *COLOR_MATRICES):
            raise ValueError(f"{a['name']}: color_matrix tiene que ser {' o '.join(COLOR_MATRICES)}")
        if a.get("key_method") not in (None, *KEY_METHODS):
            raise ValueError(f"{a['name']}: key_method tiene que ser uno de {', '.join(KEY_METHODS)}")
        if not isinstance(a.get("reverse", False), bool):
            raise ValueError(f"{a['name']}: reverse tiene que ser true o false")
        anims.append(
            Animation(
                name=a["name"],
                clip=_path(root, a["clip"]),
                kind=kind,
                loop=a.get("loop", kind == "cycle"),
                pose=_path(root, a.get("pose")),
                body_height_px=float(a["body_height_px"]) if "body_height_px" in a else None,
                scale_pose=_path(root, a.get("scale_pose")),
                pose_body_height_px=float(a["pose_body_height_px"]) if "pose_body_height_px" in a else None,
                model=a.get("model"),
                prompt=_path(root, a.get("prompt")),
                loop_seconds=tuple(a.get("loop_seconds", (0.5, 2.0))),
                skip_seconds=a.get("skip_seconds", 0.25),
                loop_start=a.get("loop_start"),
                loop_length=a.get("loop_length"),
                trim=tuple(trim) if trim else None,
                trim_static_tail=a.get("trim_static_tail", True),
                pick=a.get("pick", "sharpest" if kind == "oneshot" else "first"),
                holds={int(k): float(v) for k, v in a.get("holds", {}).items()},
                remove_flash=_flash(a["name"], a.get("remove_flash")),
                clean=_clean(a["name"], a.get("clean")),
                color_matrix=a.get("color_matrix"),
                reverse=a.get("reverse", False),
                source=source["name"] if source else None,
                key_method=a.get("key_method"),
            )
        )
    if not anims:
        raise ValueError("el personaje no tiene ninguna [[animation]]")

    scale_reference = ch.get("scale_reference", anims[0].name)
    if scale_reference not in [a.name for a in anims]:
        raise ValueError(f"scale_reference {scale_reference!r} no es una animación del personaje")

    return Character(
        name=name,
        root=root,
        work_dir=_path(root, out.get("work_dir", "work")),
        out_dir=_path(root, out.get("out_dir", "out")),
        style=style,
        game_fps=int(ch.get("game_fps", 12 if style == "hd" else 8)),
        target_height=int(ch["target_height"]),
        scale_reference=scale_reference,
        body_height_px=ch.get("body_height_px"),
        key_color=key.get("color", "auto"),
        key_mode=key.get("mode", "auto"),
        key_method=key.get("method", "auto"),
        hole_max_frac=float(key.get("hole_max_frac", 0.01)),
        key_tolerance=tuple(key.get("tolerance", (0.12, 0.80))),
        despill=float(key.get("despill", 1.0)),
        despill_band_px=int(key.get("despill_band_px", 3)),
        min_island_px=int(key.get("min_island_px", 64)),
        margin_px=int(ch.get("margin_px", 8)),
        anchor=_anchor(ch.get("anchor", "centroid")),
        pixel_factor=ch.get("pixel_factor"),
        palette_colors=int(ch.get("palette_colors", 24)),
        palette=_path(root, ch.get("palette")),
        sharpen=float(ch.get("sharpen", 0.0)),
        extra_scales=[float(s) for s in out.get("extra_scales", [])],
        atlas_max_size=int(atlas.get("max_size", 2048)),
        padding=int(atlas.get("padding", 2)),
        border_padding=int(atlas.get("border_padding", 2)),
        extrude=int(atlas.get("extrude", 1)),
        power_of_two=bool(atlas.get("power_of_two", False)),
        animations=anims,
    )
