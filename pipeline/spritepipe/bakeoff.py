"""Paso 0 del reporte: bake-off de modelos image-to-video con la misma pose y el mismo prompt.

Lee una config TOML, manda cada pedido por API (fal.ai, o Veo y Omni por la Gemini API), baja cada clip
apenas termina (Veo los borra del servidor a los 2 días) y arma una tabla con el QA de spritepipe,
el costo estimado y si el proveedor lo bloqueó por moderación.

Las keys salen sólo del entorno (FAL_KEY, GEMINI_API_KEY). Sin ninguna, corre en dry-run: muestra
los pedidos, sin las imágenes, y cuánto costarían.
"""

from __future__ import annotations

import dataclasses
import json
import os
import time
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

from . import qa, videoapi
from .config import _path

KEYS = {"fal": "FAL_KEY", "gemini": "GEMINI_API_KEY", "omni": "GEMINI_API_KEY"}  # proveedor -> variable
RESUME_HOURS = 48  # Veo borra el video a los 2 días: un pedido más viejo ya no se puede bajar
STATUS = {"done": "ok", "blocked": "bloqueado", "error": "error", "submitted": "enviado", None: "pendiente"}


@dataclass
class BakeAnim:
    name: str
    pose: Path
    prompt: Path
    kind: str  # "cycle" | "oneshot", para el QA y la búsqueda de loop
    last_frame: Path | None = None


@dataclass
class Bakeoff:
    root: Path
    out_dir: Path
    models: list[str]
    clips_per_model: int
    duration: float  # segundos pedidos; cada modelo usa el permitido más cercano por arriba
    aspect_ratio: str
    resolution: str
    audio: bool
    negative_prompt: str | None
    seed: int | None  # el clip n usa seed + n - 1
    max_usd: float  # tope: si la estimación lo pasa, no se manda nada
    max_parallel: int
    game_fps: int
    animations: list[BakeAnim]


@dataclass
class Task:
    model: videoapi.ModelSpec
    anim: BakeAnim
    n: int
    dest: Path
    duration: int
    usd: float
    seed: int | None

    @property
    def clip(self) -> str:
        return self.dest.name


BAKEOFF_KEYS = {"out_dir", "models", "clips_per_model", "duration", "aspect_ratio", "resolution", "audio",
                "negative_prompt", "seed", "max_usd", "max_parallel", "game_fps"}
ANIM_KEYS = {"name", "pose", "prompt", "kind", "last_frame"}


def load(path: str | Path) -> Bakeoff:
    path = Path(path).resolve()
    root = path.parent
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    b = data.get("bakeoff", {})
    if unknown := set(b) - BAKEOFF_KEYS:
        raise ValueError(f"[bakeoff] no conoce {', '.join(sorted(unknown))}")
    models = list(b.get("models", []))
    if not models:
        raise ValueError("[bakeoff] necesita una lista models")
    if unknown := [m for m in models if m not in videoapi.MODELS]:
        raise ValueError(f"modelos desconocidos: {', '.join(unknown)}. Los que hay: {', '.join(videoapi.MODELS)}")
    if len(set(models)) != len(models):
        raise ValueError("hay modelos repetidos en models")

    anims = []
    for a in data.get("animation", []):
        if unknown := set(a) - ANIM_KEYS:
            raise ValueError(f"{a.get('name')}: [[animation]] no conoce {', '.join(sorted(unknown))}")
        kind = a.get("kind", "cycle")
        if kind not in ("cycle", "oneshot"):
            raise ValueError(f"{a['name']}: kind tiene que ser 'cycle' u 'oneshot'")
        pose, prompt = _path(root, a["pose"]), _path(root, a["prompt"])
        last = a.get("last_frame")
        last = pose if last is True else _path(root, last) if last else None
        for what, p in (("pose", pose), ("prompt", prompt), ("last_frame", last)):
            if p is not None and not p.exists():
                raise FileNotFoundError(f"{a['name']}: no existe {what} {p}")
        anims.append(BakeAnim(a["name"], pose, prompt, kind, last))
    if not anims:
        raise ValueError("el bake-off no tiene ninguna [[animation]]")

    clips = int(b.get("clips_per_model", 1))
    if clips < 1:
        raise ValueError("clips_per_model tiene que ser 1 o más")
    return Bakeoff(
        root=root,
        out_dir=_path(root, b.get("out_dir", "clips/bakeoff")),
        models=models,
        clips_per_model=clips,
        duration=float(b.get("duration", 5)),
        aspect_ratio=b.get("aspect_ratio", "16:9"),
        resolution=b.get("resolution", "720p"),
        audio=bool(b.get("audio", False)),
        negative_prompt=b.get("negative_prompt"),
        seed=b.get("seed"),
        max_usd=float(b.get("max_usd", 30)),
        max_parallel=int(b.get("max_parallel", 4)),
        game_fps=int(b.get("game_fps", 12)),
        animations=anims,
    )


def plan(cfg: Bakeoff) -> list[Task]:
    tasks = []
    for name in cfg.models:
        spec = videoapi.MODELS[name]
        dur = spec.pick_duration(cfg.duration, cfg.resolution)
        usd = spec.price(dur, cfg.audio, cfg.resolution)
        for anim in cfg.animations:
            for n in range(1, cfg.clips_per_model + 1):
                seed = cfg.seed + n - 1 if cfg.seed is not None else None
                tasks.append(Task(spec, anim, n, cfg.out_dir / f"{name}_{anim.name}_{n}.mp4", dur, usd, seed))
    return tasks


def request(cfg: Bakeoff, t: Task) -> videoapi.Request:
    return videoapi.Request(
        prompt=t.anim.prompt.read_text(encoding="utf-8").strip(), image=t.anim.pose,
        last_image=t.anim.last_frame if t.model.last_frame else None, duration=t.duration,
        aspect_ratio=cfg.aspect_ratio, resolution=cfg.resolution, audio=cfg.audio,
        negative_prompt=cfg.negative_prompt, seed=t.seed)


def _show(p: Path) -> str:
    try:
        return str(p.relative_to(Path.cwd()))
    except ValueError:
        return p.name


def _placeholder(provider: str) -> Callable[[Path], str]:
    """En el dry-run, la imagen se muestra por su nombre, no por sus bytes ni se sube."""
    if provider == "fal":
        return lambda p: f"<URL de {_show(p)} subida al CDN de fal>"
    return lambda p: f"<{_show(p)} en base64, {-(-p.stat().st_size * 4 // 3 // 1024)} KB>"


class Ledger:
    """bakeoff.json en la carpeta de salida: cada pedido con su estado, para retomar y para la tabla.

    Guarda el id del pedido en el proveedor, nunca una key ni la imagen.
    """

    def __init__(self, path: Path):
        self.path = path
        self.data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"attempts": [], "qa": {}}

    def last(self, clip: str) -> dict | None:
        return next((a for a in reversed(self.data["attempts"]) if a["clip"] == clip), None)

    def add(self, rec: dict) -> dict:
        self.data["attempts"].append(rec)
        self.save()
        return rec

    def update(self, rec: dict, **kw) -> None:
        rec.update(kw)
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text(json.dumps(self.data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        tmp.replace(self.path)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _age_hours(iso: str) -> float:
    return (datetime.now(timezone.utc) - datetime.fromisoformat(iso)).total_seconds() / 3600


def _usd(x: float) -> str:
    return f"{x:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")


def print_plan(cfg: Bakeoff, tasks: list[Task], keys: dict, resumable: dict) -> None:
    print(f"● bake-off: {len(cfg.models)} modelos × {len(cfg.animations)} animaciones × {cfg.clips_per_model} clips "
          f"→ {_show(cfg.out_dir)}")
    for a in cfg.animations:
        print(f"  {a.name}: pose {a.pose.name}, prompt {a.prompt.name}"
              + (f", último frame {a.last_frame.name}" if a.last_frame else ""))
    print(f"\n  {'modelo':22} {'proveedor':9} {'dur.':>5} {'US$/clip':>9} {'clips':>6} {'faltan':>7} {'US$':>7}")
    total = 0.0
    for name in cfg.models:
        ts = [t for t in tasks if t.model.name == name]
        spec = ts[0].model
        todo = [t for t in ts if not t.dest.exists() and t.clip not in resumable]
        sub = sum(t.usd for t in todo)
        total += sub
        key = "" if keys.get(spec.provider) else f"  (sin {KEYS[spec.provider]})"
        print(f"  {name:22} {spec.provider:9} {ts[0].duration:>4}s {_usd(ts[0].usd):>9} {len(ts):>6} {len(todo):>7} "
              f"{_usd(sub):>7}{key}")
        if any(a.last_frame for a in cfg.animations) and not spec.last_frame:
            print(f"  {'':22} ! no acepta último frame: va sólo el primero")
        if spec.sunset:
            left = (date.fromisoformat(spec.sunset) - date.today()).days
            print(f"  {'':22} " + (f"✗ {spec.endpoint} se apagó el {spec.sunset}" if left <= 0 else
                                   f"! {spec.endpoint} se apaga el {spec.sunset} (en {left} días)"))
    print(f"  {'total estimado':>62} {_usd(total):>7}   (tope max_usd {_usd(cfg.max_usd)})")
    if resumable:
        print(f"  {len(resumable)} pedidos ya enviados se retoman sin volver a pagarlos")


def print_payloads(cfg: Bakeoff, tasks: list[Task]) -> None:
    seen = set()
    for t in tasks:
        if t.model.name in seen:
            continue
        seen.add(t.model.name)
        req = request(cfg, t)
        req = dataclasses.replace(req, prompt=f"<{_show(t.anim.prompt)}, {len(req.prompt)} caracteres>")
        body = t.model.build(req, _placeholder(t.model.provider))
        endpoint = t.model.endpoint_for(req)
        url = {"fal": f"{videoapi.FAL_QUEUE}/{endpoint}", "omni": videoapi.INTERACTIONS,
               "gemini": f"{videoapi.GEMINI_API}/models/{endpoint}:predictLongRunning"}[t.model.provider]
        print(f"\n  {t.model.name}  POST {url}\n    {json.dumps(body, ensure_ascii=False)}")
        print(f"    precio: {t.model.price_note}  ·  doc: {t.model.docs}")
    if any(t.model.provider == "fal" for t in tasks):
        print(f"\n  {videoapi.FAL_BLOCKED}.")


def execute(cfg: Bakeoff, tasks: list[Task], clients: dict, ledger: Ledger, resumable: dict,
            sleep: Callable[[float], None] = time.sleep, poll_s: float = 10.0, timeout_s: float = 1800.0,
            max_waits: int = 60) -> None:
    """Manda hasta max_parallel pedidos a la vez y baja cada clip apenas termina."""
    queue = [t for t in tasks if t.clip not in resumable]
    active = [(t, resumable[t.clip], time.monotonic()) for t in tasks if t.clip in resumable]
    for t, rec, _ in active:
        print(f"  ▸ {t.clip}: retomo el pedido {rec['handle']}")
    waits = 0
    while queue or active:
        while queue and len(active) < cfg.max_parallel:
            t = queue.pop(0)
            client = clients[t.model.provider]
            req = request(cfg, t)
            endpoint = t.model.endpoint_for(req)
            try:
                handle = client.submit(endpoint, t.model.build(req, client.image_ref))
            except (videoapi.HttpError, OSError) as e:
                transient = not isinstance(e, videoapi.HttpError) or e.status == 429
                if transient and waits < max_waits:  # cuota del proveedor o red: reintenta en la próxima vuelta
                    waits += 1
                    queue.insert(0, t)
                    print(f"  … {t.model.provider}: {e}; reintento")
                    break
                if not isinstance(e, videoapi.HttpError):
                    _finish(t, ledger.add(_record(t, endpoint, None)), videoapi.Poll("error", detail=str(e)), ledger)
                    continue
                p = (videoapi.fal_error(e) if t.model.provider == "fal" else videoapi.omni_error(e)
                     if t.model.provider == "omni" else videoapi.Poll(
                         "blocked" if videoapi.looks_blocked(str(e.body)) else "error", detail=str(e)))
                _finish(t, ledger.add(_record(t, endpoint, None)), p, ledger)
                continue
            rec = ledger.add(_record(t, endpoint, handle))
            active.append((t, rec, time.monotonic()))
            print(f"  ▸ {t.clip}: enviado")
        still = []
        for t, rec, t0 in active:
            client = clients[t.model.provider]
            try:
                p = client.poll(rec["handle"])
            except OSError:  # red: se vuelve a consultar en la próxima vuelta
                still.append((t, rec, t0))
                continue
            except videoapi.HttpError as e:
                if e.status in (429, 500, 502, 503, 504):
                    still.append((t, rec, t0))
                    continue
                p = (videoapi.fal_error(e) if t.model.provider == "fal" else videoapi.omni_error(e)
                     if t.model.provider == "omni" else videoapi.Poll("error", detail=str(e)))
            if p.state == "running":
                if time.monotonic() - t0 > timeout_s:
                    print(f"  ! {t.clip}: sigue en el proveedor después de {timeout_s / 60:.0f} min; "
                          "volvé a correr el comando para retomarlo")
                else:
                    still.append((t, rec, t0))
                continue
            if p.state == "done":
                try:
                    client.download(p.video_url, t.dest)
                except (videoapi.HttpError, OSError) as e:
                    p = videoapi.Poll("error", detail=f"no pude bajar el video: {e}")
            _finish(t, rec, p, ledger)
        active = still
        if active or queue:
            sleep(poll_s)


def _record(t: Task, endpoint: str, handle: dict | None) -> dict:
    return {"clip": t.clip, "model": t.model.name, "provider": t.model.provider, "endpoint": endpoint,
            "animation": t.anim.name, "n": t.n, "seed": t.seed, "duration_s": t.duration, "usd_estimate": t.usd,
            "status": "submitted", "handle": handle, "submitted": _now()}


def _finish(t: Task, rec: dict, p: videoapi.Poll, ledger: Ledger) -> None:
    ledger.update(rec, status=p.state, detail=p.detail, finished=_now())
    if p.state == "done":
        print(f"  ✓ {t.clip} ({t.dest.stat().st_size / 1e6:.1f} MB)")
    elif p.state == "blocked":
        print(f"  ✗ {t.clip}: bloqueado por el proveedor — {p.detail}")
    else:
        print(f"  ✗ {t.clip}: {p.detail}")


def report(cfg: Bakeoff, tasks: list[Task], ledger: Ledger, skip_qa: bool = False) -> list[dict]:
    """QA de cada clip bajado con el mismo QA que `spritepipe check`, más estado y costo."""
    rows = []
    for t in tasks:
        rec = ledger.last(t.clip)
        status = "done" if t.dest.exists() else rec["status"] if rec else None
        billed = status == "done" or (status == "blocked" and t.model.bills_blocked)
        row = {"clip": t.clip, "model": t.model.name, "animation": t.anim.name, "n": t.n,
               "status": STATUS[status], "detail": (rec or {}).get("detail", "") if status != "done" else "",
               "usd": t.usd if billed else 0.0}
        if t.dest.exists() and skip_qa:
            row.update(ledger.data["qa"].get(t.clip, {}), usd=row["usd"])
        elif t.dest.exists():
            c = qa.check_clip(t.dest, t.anim.pose, t.anim.kind, cfg.game_fps)
            m, loop = c["qa"]["metrics"], c["loop"] or {}
            row.update(qa=c["qa"]["verdict"], drift_pct=m.get("drift_pct"), zoom_pct=m.get("zoom_pct"),
                       edge_frames=m.get("frames_touching_edge"), pose_mad=m.get("pose_mad_region"),
                       loop_score=loop.get("score"), loop_quality=loop.get("quality") or loop.get("error"),
                       flags=[f["msg"] for f in c["qa"]["flags"]],
                       video=f"{c['video']['width']}×{c['video']['height']} {c['video']['fps']:g} fps {c['frames']} fr")
            ledger.data["qa"][t.clip] = {k: v for k, v in row.items() if k not in ("clip", "status", "detail")}
        rows.append(row)
    ledger.save()
    return rows


COLUMNS = [("clip", "clip", 30), ("estado", "status", 9), ("QA", "qa", 4), ("deriva%", "drift_pct", 7),
           ("zoom%", "zoom_pct", 6), ("borde", "edge_frames", 5), ("pose", "pose_mad", 5),
           ("loop", "loop_score", 5), ("US$", "usd", 5)]


def _cell(row: dict, key: str) -> str:
    v = row.get(key)
    if key == "usd":
        return _usd(v)
    if key == "loop_score" and v is not None and row.get("loop_quality"):
        return f"{v}"
    return "-" if v is None else str(v)


def summarize(rows: list[dict]) -> list[dict]:
    """Por modelo: cuántos clips salieron, cuántos bloqueó, cómo les fue en el QA y cuánto costó."""
    out = []
    for model in dict.fromkeys(r["model"] for r in rows):
        rs = [r for r in rows if r["model"] == model]
        mads = sorted(r["pose_mad"] for r in rs if r.get("pose_mad") is not None)
        loops = [r["loop_score"] for r in rs if r.get("loop_score") is not None]
        out.append({"model": model, "clips": len(rs), **{k: sum(r["status"] == v for r in rs) for k, v in
                    (("ok", "ok"), ("blocked", "bloqueado"), ("error", "error"))},
                    "qa": "/".join(str(sum(r.get("qa") == v for r in rs)) for v in ("ok", "warn", "fail")),
                    "pose_mad": mads[len(mads) // 2] if mads else None, "best_loop": min(loops) if loops else None,
                    "usd": sum(r["usd"] for r in rs)})
    return out


SUMMARY = [("modelo", "model", 22), ("bajados", "ok", 7), ("bloq.", "blocked", 5), ("error", "error", 5),
           ("QA ok/warn/fail", "qa", 15), ("pose med.", "pose_mad", 9), ("mejor loop", "best_loop", 10),
           ("US$", "usd", 6)]


def print_table(rows: list[dict]) -> None:
    print("\n  " + " ".join(f"{h:>{w}}" if i else f"{h:{w}}" for i, (h, _, w) in enumerate(COLUMNS)))
    for r in rows:
        print("  " + " ".join(f"{_cell(r, k):>{w}}" if i else f"{_cell(r, k)[:w]:{w}}"
                              for i, (_, k, w) in enumerate(COLUMNS)))
        if r["detail"]:
            print(f"  {'':30} {r['detail'][:150]}")
    print("\n  " + " ".join(f"{h:>{w}}" if i else f"{h:{w}}" for i, (h, _, w) in enumerate(SUMMARY)))
    for r in summarize(rows):
        print("  " + " ".join(f"{_cell(r, k):>{w}}" if i else f"{_cell(r, k):{w}}" for i, (_, k, w) in enumerate(SUMMARY)))
    print("\n  QA: ok/warn/fail · deriva y zoom en % del alto del personaje · borde: frames que tocan el borde"
          " · pose: MAD del frame 0 contra la pose (más bajo, más fiel) · loop: costura (≤0,6 buena, ≤1 aceptable)")


def write_markdown(path: Path, cfg: Bakeoff, rows: list[dict]) -> None:
    lines = [f"# Bake-off ({date.today().isoformat()})", "",
             f"Modelos: {', '.join(cfg.models)}. Animaciones: "
             + ", ".join(f"{a.name} (pose `{a.pose.name}`, prompt `{a.prompt.name}`)" for a in cfg.animations)
             + f". {cfg.clips_per_model} clips por modelo y animación, {cfg.resolution} {cfg.aspect_ratio}, "
             + ("con" if cfg.audio else "sin") + " audio.", "",
             "| clip | estado | QA | deriva % | zoom % | borde | pose MAD | loop | US$ | notas |",
             "|---|---|---|---:|---:|---:|---:|---|---:|---|"]
    for r in rows:
        loop = f"{r['loop_score']} ({r['loop_quality']})" if r.get("loop_score") is not None else r.get("loop_quality") or "-"
        notes = r["detail"] or "; ".join(r.get("flags", []))
        lines.append(f"| {r['clip']} | {r['status']} | {r.get('qa', '-')} | {r.get('drift_pct', '-')} | "
                     f"{r.get('zoom_pct', '-')} | {r.get('edge_frames', '-')} | {r.get('pose_mad', '-')} | {loop} | "
                     f"{_usd(r['usd'])} | {notes.replace('|', '/')} |")
    lines += ["", "| modelo | bajados | bloqueados | errores | QA ok/warn/fail | pose MAD (mediana) | mejor loop | US$ |",
              "|---|---:|---:|---:|---|---:|---:|---:|"]
    for m in summarize(rows):
        lines.append(f"| {m['model']} | {m['ok']} | {m['blocked']} | {m['error']} | {m['qa']} | "
                     f"{_cell(m, 'pose_mad')} | {_cell(m, 'best_loop')} | {_usd(m['usd'])} |")
    lines += ["", f"Gastado (estimado, a precio de lista): US$ {_usd(sum(r['usd'] for r in rows))}."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(cfg_path: Path, dry_run: bool = False, yes: bool = False, models: list[str] | None = None,
        skip_qa: bool = False, env: dict | None = None, http: videoapi.Http | None = None,
        sleep: Callable[[float], None] = time.sleep, ask: Callable[[str], str] = input, poll_s: float = 10.0) -> int:
    cfg = load(cfg_path)
    if models:
        if unknown := [m for m in models if m not in cfg.models]:
            print(f"✗ {', '.join(unknown)} no está en models de la config")
            return 1
        cfg.models = [m for m in cfg.models if m in models]
    env = os.environ if env is None else env
    keys = {p: bool(env.get(var)) for p, var in KEYS.items()}
    tasks = plan(cfg)
    ledger = Ledger(cfg.out_dir / "bakeoff.json")
    resumable = {}
    for t in tasks:
        rec = ledger.last(t.clip)
        if (not t.dest.exists() and rec and rec["status"] == "submitted" and rec.get("handle")
                and _age_hours(rec["submitted"]) < RESUME_HOURS):
            resumable[t.clip] = rec
    print_plan(cfg, tasks, keys, resumable)

    dry = dry_run or not any(keys.values())
    if dry:
        print_payloads(cfg, tasks)
        why = "--dry-run" if dry_run else f"no hay {' ni '.join(dict.fromkeys(KEYS.values()))} en el entorno"
        print(f"\n  dry-run ({why}): no se llamó a ninguna API.")
    else:
        runnable = [t for t in tasks if not t.dest.exists() and keys[t.model.provider]]
        for var in dict.fromkeys(KEYS.values()):
            skipped = {t.model.name for t in tasks if KEYS[t.model.provider] == var and not t.dest.exists()}
            if skipped and not env.get(var):
                print(f"  ! sin {var}: salteo {', '.join(sorted(skipped))}")
        new = [t for t in runnable if t.clip not in resumable]
        cost = sum(t.usd for t in new)
        if cost > cfg.max_usd:
            print(f"✗ la estimación (US$ {_usd(cost)}) pasa el tope max_usd (US$ {_usd(cfg.max_usd)}): "
                  "bajá clips_per_model, sacá modelos o subí max_usd")
            return 1
        if cost and not yes:
            try:
                ok = ask(f"\n¿Mando {len(new)} pedidos por ~US$ {_usd(cost)}? [s/N] ")
            except EOFError:
                ok = ""
            if ok.strip().lower() not in ("s", "si", "sí", "y", "yes"):
                print("  no se mandó nada (pasá --yes para no preguntar)")
                return 1
        if runnable:
            clients = {}
            if keys["fal"]:
                clients["fal"] = videoapi.FalClient(env["FAL_KEY"], http)
            if keys["gemini"]:
                clients["gemini"] = videoapi.GeminiClient(env["GEMINI_API_KEY"], http)
            if keys["omni"]:
                clients["omni"] = videoapi.OmniClient(env["GEMINI_API_KEY"], http)
            print()
            try:
                execute(cfg, runnable, clients, ledger, resumable, sleep=sleep, poll_s=poll_s)
            except KeyboardInterrupt:
                print("\n  cortado. Lo enviado sigue corriendo en el proveedor: volvé a correr el comando "
                      f"en menos de {RESUME_HOURS} h para bajarlo sin pagarlo de nuevo.")
                return 130

    if not any(t.dest.exists() for t in tasks) and not ledger.data["attempts"]:
        return 0
    rows = report(cfg, tasks, ledger, skip_qa)
    print_table(rows)
    md = cfg.out_dir / "bakeoff.md"
    write_markdown(md, cfg, rows)
    print(f"\n  tabla en {_show(md)}, detalle por pedido en {_show(ledger.path)}")
    return 0
