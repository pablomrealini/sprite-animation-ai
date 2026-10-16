"""Clips sintéticos que imitan un clip de image-to-video, para probar el pipeline sin gastar API.

Un soldado de vista lateral, color plano y contorno grueso, sobre un verde que no es #00FF00
exacto, con gradiente y ruido por frame, cámara que se corre de a poco, un arranque donde el
movimiento "se acomoda" y compresión H.264 4:2:0. La verdad de base es conocida: el walk tiene
período de 24 frames y el idle de 48, así que el loop que encuentre el pipeline se puede verificar.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from . import imgio

W, H, SS, FPS = 720, 1280, 2, 24
GROUND = 930
BG = (16, 232, 18)
OUTLINE = (24, 20, 26)
COLORS = {
    "torso": (59, 110, 168), "belt": (120, 78, 40), "skin": (242, 199, 154), "helmet": (154, 163, 173),
    "leg_near": (90, 62, 43), "leg_far": (58, 40, 28), "arm_near": (59, 110, 168), "arm_far": (38, 72, 112),
    "sword": (217, 222, 227), "boot": (40, 34, 38),
}


def _capsule(d: ImageDraw.ImageDraw, p0, p1, width: float, color, outline: float = 8):
    for w, c in ((width + 2 * outline, OUTLINE), (width, color)):
        w2 = w * SS
        d.line([tuple(v * SS for v in p0), tuple(v * SS for v in p1)], fill=c, width=int(w2))
        for p in (p0, p1):
            x, y = p[0] * SS, p[1] * SS
            d.ellipse([x - w2 / 2, y - w2 / 2, x + w2 / 2, y + w2 / 2], fill=c)


def _rect(d, box, color, radius=18, outline=8):
    x0, y0, x1, y1 = (v * SS for v in box)
    o = outline * SS
    d.rounded_rectangle([x0 - o, y0 - o, x1 + o, y1 + o], radius=(radius + outline) * SS, fill=OUTLINE)
    d.rounded_rectangle([x0, y0, x1, y1], radius=radius * SS, fill=color)


def _circle(d, c, r, color, outline=8):
    x, y = c[0] * SS, c[1] * SS
    for rr, col in ((r + outline, OUTLINE), (r, color)):
        rr *= SS
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col)


def _end(p, length, angle_deg):
    a = math.radians(angle_deg)
    return (p[0] + length * math.sin(a), p[1] + length * math.cos(a))


def draw_pose(pose: dict, offset=(0.0, 0.0), scale=1.0, noise_seed: int | None = None, bg=BG) -> np.ndarray:
    """pose: leg (grados, + hacia adelante), arm_near, arm_far, lean, breathe, sword (bool)."""
    img = Image.new("RGB", (W * SS, H * SS), bg)
    d = ImageDraw.Draw(img)
    s = scale
    cx, gy = W / 2 + offset[0], GROUND + offset[1]
    leg_len = 210 * s
    theta = pose["leg"]
    hip = (cx, gy - leg_len * math.cos(math.radians(theta)) - pose.get("crouch", 0) * s)
    torso_h = 175 * s * (1 + pose.get("breathe", 0))
    lean = pose.get("lean", 0)
    shoulder = (hip[0] + math.sin(math.radians(lean)) * torso_h * 0.85, hip[1] - torso_h * 0.85)

    # lejos
    _capsule(d, shoulder, _end(shoulder, 150 * s, pose["arm_far"]), 40 * s, COLORS["arm_far"])
    foot_far = _end(hip, leg_len, -theta)
    _capsule(d, hip, foot_far, 52 * s, COLORS["leg_far"])
    _capsule(d, foot_far, (foot_far[0] + 34 * s, foot_far[1]), 30 * s, COLORS["boot"], outline=7)
    # cuerpo
    tx = (hip[0] + shoulder[0]) / 2
    _rect(d, (tx - 62 * s, hip[1] - torso_h, tx + 62 * s, hip[1] + 18 * s), COLORS["torso"])
    _rect(d, (tx - 62 * s, hip[1] - 22 * s, tx + 62 * s, hip[1] + 2 * s), COLORS["belt"], radius=4, outline=5)
    head = (shoulder[0] + 10 * s, shoulder[1] - 78 * s)
    _circle(d, head, 64 * s, COLORS["skin"])
    hx, hy, r = head[0] * SS, head[1] * SS, 72 * s * SS
    d.pieslice([hx - r, hy - r, hx + r, hy + r], 180, 360, fill=OUTLINE)
    r2 = 64 * s * SS
    d.pieslice([hx - r2, hy - r2 - 4 * SS, hx + r2, hy + r2 - 4 * SS], 180, 360, fill=COLORS["helmet"])
    ex, ey = (head[0] + 34 * s) * SS, (head[1] + 14 * s) * SS
    d.ellipse([ex - 7 * SS, ey - 9 * SS, ex + 7 * SS, ey + 9 * SS], fill=OUTLINE)
    # cerca
    foot_near = _end(hip, leg_len, theta)
    _capsule(d, hip, foot_near, 54 * s, COLORS["leg_near"])
    _capsule(d, foot_near, (foot_near[0] + 36 * s, foot_near[1]), 32 * s, COLORS["boot"], outline=7)
    hand = _end(shoulder, 150 * s, pose["arm_near"])
    if pose.get("sword"):
        tip = _end(hand, 190 * s, pose["arm_near"] + pose.get("sword_rel", -70))
        _capsule(d, hand, tip, 18 * s, COLORS["sword"], outline=6)
    _capsule(d, shoulder, hand, 44 * s, COLORS["arm_near"])

    out = np.asarray(img.resize((W, H), Image.Resampling.BOX), dtype=np.float32)
    if noise_seed is not None:  # gradiente y ruido por frame: el fondo de IA nunca es plano
        rng = np.random.default_rng(noise_seed)
        grad = np.linspace(-5, 5, H, dtype=np.float32)[:, None, None]
        bgmask = (np.abs(out - np.array(bg, np.float32)).sum(-1) < 6)[..., None]
        out = out + bgmask * grad + rng.normal(0, 1.6, out.shape).astype(np.float32)
    return np.clip(out, 0, 255).astype(np.uint8)


def _ease(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def walk_pose(t: int, period: int = 24) -> dict:
    ramp = 0.35 + 0.65 * _ease(t / 6)  # el modelo arranca desde la pose y "se acomoda"
    ph = 2 * math.pi * t / period
    sw = math.sin(ph) * ramp
    return {"leg": 24 * sw, "arm_near": -22 * sw, "arm_far": 22 * sw, "lean": 4}


def idle_pose(t: int, period: int = 48) -> dict:
    ph = 2 * math.pi * t / period
    return {"leg": 5, "arm_near": 6 + 3 * math.sin(ph), "arm_far": -4 - 3 * math.sin(ph),
            "breathe": 0.018 * math.sin(ph), "crouch": 3 * (1 - math.cos(ph)) / 2, "lean": 2}


def attack_pose(t: int) -> dict:
    keys = [(0, 20, 0), (18, -160, -6), (24, 95, 14), (32, 100, 12), (54, 20, 0), (72, 20, 0)]
    for (t0, a0, l0), (t1, a1, l1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            k = _ease((t - t0) / (t1 - t0)) if t1 > t0 else 1
            return {"leg": 10, "arm_near": a0 + (a1 - a0) * k, "arm_far": -15, "lean": l0 + (l1 - l0) * k,
                    "sword": True, "crouch": 10 * math.sin(math.pi * min(1, t / 32))}
    return {"leg": 10, "arm_near": 20, "arm_far": -15, "lean": 0, "sword": True}


def make(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    clips = root / "clips"
    drift = (0.12, 0.03)
    print("generando clips sintéticos (24 fps, 720×1280)…")
    imgio.encode_rgb_video((draw_pose(walk_pose(t), (drift[0] * t, drift[1] * t), noise_seed=t)
                            for t in range(96)), clips / "walk.mp4", FPS)
    imgio.encode_rgb_video((draw_pose(idle_pose(t), noise_seed=1000 + t) for t in range(96)), clips / "idle.mp4", FPS)
    imgio.encode_rgb_video((draw_pose(attack_pose(t), noise_seed=2000 + t) for t in range(72)), clips / "attack.mp4", FPS)
    # clip "malo": zoom de 12% y paneo, para ver que el QA lo rechace
    imgio.encode_rgb_video((draw_pose(walk_pose(t), (2.0 * t, 0), scale=1 + 0.12 * t / 95, noise_seed=3000 + t)
                            for t in range(96)), clips / "walk_zoom_bad.mp4", FPS)
    # walk sobre fondo blanco, como un concept animado sin pantalla verde
    imgio.encode_rgb_video((draw_pose(walk_pose(t), (drift[0] * t, drift[1] * t), noise_seed=4000 + t, bg=(246, 244, 240))
                            for t in range(96)), clips / "walk_white.mp4", FPS)
    # la pose que se le "pasó" al modelo: frame 0 limpio sobre #00FF00
    pose = draw_pose(walk_pose(0))
    pose[(np.abs(pose.astype(int) - BG).sum(-1) < 6)] = (0, 255, 0)
    imgio.save(root / "poses" / "walk.png", pose)
    imgio.save(root / "poses" / "attack.png", draw_pose(attack_pose(0)))

    common = """
[[animation]]
name = "idle"
clip = "clips/idle.mp4"
kind = "cycle"
loop_seconds = [1.0, 2.5]
model = "sintético"

[[animation]]
name = "walk"
clip = "clips/walk.mp4"
kind = "cycle"
pose = "poses/walk.png"
model = "sintético"

[[animation]]
name = "attack"
clip = "clips/attack.mp4"
kind = "oneshot"
pose = "poses/attack.png"
model = "sintético"
holds = { 3 = 2.0 }   # el impacto dura el doble
"""
    (root / "character.toml").write_text(f"""# Personaje sintético, estilo HD (tipo Kingdom Rush)
[character]
name = "synthetic"
style = "hd"
game_fps = 12
target_height = 128       # alto del cuerpo en idle, en px finales
scale_reference = "idle"

[key]
color = "auto"
tolerance = [0.12, 0.80]

[output]
extra_scales = [0.5]
{common}""", encoding="utf-8")
    (root / "character_pixel.toml").write_text(f"""# El mismo personaje por la rama pixel art
[character]
name = "synthetic_px"
style = "pixel"
game_fps = 8
target_height = 48
palette_colors = 12
scale_reference = "idle"

[output]
work_dir = "work_px"
out_dir = "out_px"
{common}""", encoding="utf-8")
    (root / "character_white.toml").write_text("""# Walk sobre fondo blanco: prueba del key por distancia
[character]
name = "synthetic_white"
style = "hd"
game_fps = 12
target_height = 128

[output]
work_dir = "work_white"
out_dir = "out_white"

[[animation]]
name = "walk"
clip = "clips/walk_white.mp4"
kind = "cycle"
""", encoding="utf-8")
    print(f"listo: {root}/character.toml, character_pixel.toml y character_white.toml")
