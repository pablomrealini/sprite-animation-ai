"""Lectura y escritura de frames PNG (RGB/RGBA, uint8) y llamadas a ffmpeg."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import cv2
import numpy as np


def load(path: Path) -> np.ndarray:
    """Devuelve HxWx3 (RGB) o HxWx4 (RGBA) uint8. imdecode evita problemas con rutas no ASCII."""
    buf = np.fromfile(str(path), dtype=np.uint8)
    img = cv2.imdecode(buf, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise IOError(f"no pude leer {path}")
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if img.dtype != np.uint8:
        img = (img / 257).astype(np.uint8)
    code = cv2.COLOR_BGRA2RGBA if img.shape[2] == 4 else cv2.COLOR_BGR2RGB
    return cv2.cvtColor(img, code)


def save(path: Path, img: np.ndarray, compression: int = 1) -> None:
    code = cv2.COLOR_RGBA2BGRA if img.shape[2] == 4 else cv2.COLOR_RGB2BGR
    ok, buf = cv2.imencode(".png", cv2.cvtColor(img, code), [cv2.IMWRITE_PNG_COMPRESSION, compression])
    if not ok:
        raise IOError(f"no pude codificar {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    buf.tofile(str(path))


def frames(directory: Path) -> list[Path]:
    return sorted(directory.glob("f_*.png"))


def frame_name(i: int) -> str:
    return f"f_{i:04d}.png"


def reset_dir(directory: Path) -> Path:
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(parents=True)
    return directory


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


# --- ffmpeg -------------------------------------------------------------------


def _run(cmd: list[str]) -> str:
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"falló: {' '.join(cmd)}\n{res.stderr[-2000:]}")
    return res.stdout


def probe(clip: Path) -> dict:
    out = _run([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,avg_frame_rate,nb_frames,"
        "color_space,color_range,pix_fmt,codec_name:format=duration",
        "-of", "json", str(clip),
    ])
    info = json.loads(out)
    s = info["streams"][0]
    num, den = (int(x) for x in s["r_frame_rate"].split("/"))
    return {
        "width": int(s["width"]),
        "height": int(s["height"]),
        "fps": num / den,
        "nb_frames": int(s["nb_frames"]) if s.get("nb_frames", "N/A").isdigit() else None,
        "duration": float(info.get("format", {}).get("duration", 0) or 0),
        "codec": s.get("codec_name"),
        "pix_fmt": s.get("pix_fmt"),
        "color_space": s.get("color_space"),
        "color_range": s.get("color_range"),
    }


def _to_rgb(info: dict, matrix: str | None) -> str:
    """Filtro de ffmpeg a RGB con la matriz de color explícita: la que se pase, la del tag del video
    o BT.709 si no tiene tag. Sin matriz explícita, swscale asume BT.601 en video sin tag."""
    if matrix is None:
        matrix = {"bt470bg": "bt601", "smpte170m": "bt601", "bt709": "bt709"}.get(info.get("color_space") or "", "bt709")
    rng = "full" if info.get("color_range") == "pc" else "limited"
    return f"scale=in_color_matrix={matrix}:in_range={rng}:flags=lanczos+accurate_rnd+full_chroma_int,format=rgb24"


def extract(clip: Path, out_dir: Path, info: dict, matrix: str | None = None) -> int:
    """Vuelca todos los frames nativos a PNG sin pérdida, con la matriz de color explícita.

    matrix ("bt601" | "bt709") pisa la del video: los clips sin tag de algunos servicios vienen en BT.601.
    """
    reset_dir(out_dir)
    _run([
        "ffmpeg", "-v", "error", "-i", str(clip), "-vf", _to_rgb(info, matrix),
        "-fps_mode", "passthrough", "-start_number", "0",
        str(out_dir / "f_%04d.png"),
    ])
    return len(frames(out_dir))


def read_video(clip: Path, info: dict, matrix: str | None = None) -> np.ndarray:
    """Todos los frames nativos en memoria (N×H×W×3 RGB), con la misma conversión que extract."""
    res = subprocess.run([
        "ffmpeg", "-v", "error", "-i", str(clip), "-vf", _to_rgb(info, matrix),
        "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
    ], capture_output=True)
    if res.returncode != 0:
        raise RuntimeError(f"falló la lectura de {clip}\n{res.stderr.decode()[-2000:]}")
    return np.frombuffer(res.stdout, np.uint8).reshape(-1, info["height"], info["width"], 3)


def encode_rgb_video(frames_rgb, out: Path, fps: float, crf: int = 18, pix_fmt: str = "yuv420p") -> None:
    """Codifica frames RGB a H.264 BT.709. Con crf 0 el códec no pierde nada y con yuv444p tampoco
    se submuestrea el color: sólo queda el redondeo de RGB a YUV."""
    frames_rgb = list(frames_rgb)
    h, w = frames_rgb[0].shape[:2]
    out.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
        "-r", str(fps), "-i", "-",
        "-vf", f"scale=out_color_matrix=bt709:out_range=tv,format={pix_fmt}",
        "-c:v", "libx264", "-crf", str(crf), "-preset", "medium",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
        str(out),
    ], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    for f in frames_rgb:
        proc.stdin.write(np.ascontiguousarray(f, dtype=np.uint8).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(proc.stderr.read().decode()[-2000:])


def write_apng(frame_paths: list[Path], durations_ms: list[float], out: Path) -> None:
    """APNG en loop infinito respetando la duración de cada frame (concat demuxer)."""
    out.parent.mkdir(parents=True, exist_ok=True)
    lst = out.with_suffix(".txt")
    lines = []
    for p, d in zip(frame_paths, durations_ms):
        lines += [f"file '{p.resolve()}'", f"duration {d / 1000:.4f}"]
    lines.append(f"file '{frame_paths[-1].resolve()}'")  # el concat demuxer ignora la duración del último
    lst.write_text("\n".join(lines) + "\n")
    try:
        _run([
            "ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
            "-fps_mode", "vfr", "-plays", "0", "-f", "apng", str(out),
        ])
    finally:
        lst.unlink(missing_ok=True)


def ffmpeg_version() -> str:
    return _run(["ffmpeg", "-version"]).splitlines()[0]
