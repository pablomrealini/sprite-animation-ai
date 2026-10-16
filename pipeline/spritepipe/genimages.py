"""Gráficos de fondo por API de imagen: style frame, capas de parallax, kit de plataformas y props.

Lee una config TOML (backgrounds/<set>/gen.toml), arma un pedido por asset, modelo e imagen, los manda
(OpenAI o fal.ai) y les corre el post sin IA de bgpost: key del fondo plano, transparencia, piezas,
costura y recorte. Varios modelos en la misma config dan la comparación, como el bake-off de video.

Las keys salen sólo del entorno (OPENAI_API_KEY, FAL_KEY). Sin ninguna corre en dry-run: muestra los
pedidos, los prompts y cuánto costarían.

En la carpeta de salida:
  raw/<asset>/<modelo>_<n>.png   lo que devolvió el modelo, tal cual
  raw/<asset>/<modelo>_<n>.json  procedencia: modelo, endpoint, prompt, referencias (con sha256), pedido,
                                 costo estimado, uso que informa el proveedor y el reporte del post
  post/<asset>/<modelo>_<n>.png  después del post; con piezas, post/<asset>/<modelo>_<n>/<pieza>.png
  gen.json                       cada pedido con su estado (para retomar y para la tabla), sin keys
  compare.md, compare.html       la comparación por asset y modelo
"""

from __future__ import annotations

import dataclasses
import hashlib
import html
import json
import os
import threading
import time
import tomllib
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from PIL import Image

from . import bgpost, imageapi
from .bakeoff import Ledger, _age_hours, _now, _show, _usd
from .config import _path
from .pose import parse_rgb

KEYS = {"openai": "OPENAI_API_KEY", "fal": "FAL_KEY"}  # proveedor -> variable de entorno
RESUME_HOURS = 24  # un pedido de fal enviado y no bajado se retoma sin pagarlo de nuevo
STATUS = {"done": "ok", "blocked": "bloqueado", "error": "error", "submitted": "enviado", None: "pendiente"}
ALPHA_KINDS = ("opaque", "layer", "cutout")
SEAMS = ("cut", "crossfade", "mask", "none")

REF_CLAUSE = {
    "character": "The character in the reference image is the hero of this game: draw the character exactly as "
                 "shown there (same design, colors and proportions).",
    "style": "Use the reference image only as a style guide for line weight, outline color, flat colors and "
             "rendering; do not draw the character or any element of the reference.",
    "level": "The reference images are the art direction of this game: the hero character and a full style frame "
             "of this level. Match their line weight, outline color, flat colors and palette, and make this element "
             "look like the matching part of the style frame. Do not draw the character.",
}
BACKGROUND_CLAUSE = {
    "native": "Transparent background: only the described elements, everything else fully transparent.",
    "key": "Background: a perfectly flat, uniform pure chroma key color {key} everywhere that is not part of "
           "the described elements, with no gradient, shadow, glow, floor or texture on it, and never use that "
           "color inside the artwork.",
}


@dataclass
class Asset:
    name: str
    prompt: str
    styles: list[str]
    refs: list[Path]
    ref_role: str  # "character" | "style" | "level": cómo se le pide al modelo que use las referencias
    aspect: str
    alpha: str  # "opaque" | "layer" | "cutout"
    tile: dict[str, str]
    seam: str
    seam_px: float
    trim: bool
    split: list[str]
    same_height: bool
    height: int | None
    n: int
    models: list[str]  # si no está vacía, sólo estos modelos de [gen] generan el asset


@dataclass
class GenConfig:
    root: Path
    out_dir: Path
    set_name: str
    models: list[str]
    images_per_asset: int
    max_usd: float
    max_parallel: int
    key_color: str
    quality: str
    resolution: str
    seed: int | None
    ref_bg: str | None
    styles: dict[str, str]
    assets: list[Asset]


@dataclass
class Task:
    model: imageapi.ImageModelSpec
    asset: Asset
    k: int
    dest: Path  # raw/<asset>/<modelo>_<k>.png
    usd: float
    seed: int | None
    size: str

    @property
    def id(self) -> str:
        return f"{self.asset.name}/{self.dest.stem}"

    @property
    def post(self) -> Path:
        return self.dest.parent.parent.parent / "post" / self.asset.name / self.dest.name


GEN_KEYS = {"models", "images_per_asset", "max_usd", "max_parallel", "key_color", "quality", "resolution", "seed",
            "ref_bg", "out_dir", "set"}
ASSET_KEYS = {"name", "prompt", "style", "refs", "ref_role", "aspect", "alpha", "tile", "seam", "seam_px", "trim",
              "split", "same_height", "height", "n", "models"}


def load(path: str | Path) -> GenConfig:
    path = Path(path).resolve()
    root = path.parent
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    g = data.get("gen", {})
    if unknown := set(g) - GEN_KEYS:
        raise ValueError(f"[gen] no conoce {', '.join(sorted(unknown))}")
    models = list(g.get("models", []))
    if not models:
        raise ValueError("[gen] necesita una lista models")
    if unknown := [m for m in models if m not in imageapi.MODELS]:
        raise ValueError(f"modelos desconocidos: {', '.join(unknown)}. Los que hay: {', '.join(imageapi.MODELS)}")
    if len(set(models)) != len(models):
        raise ValueError("hay modelos repetidos en models")
    styles = {k: v.strip() for k, v in data.get("styles", {}).items()}

    assets = []
    for a in data.get("asset", []):
        name = a.get("name")
        if not name:
            raise ValueError("un [[asset]] no tiene name")
        if unknown := set(a) - ASSET_KEYS:
            raise ValueError(f"{name}: [[asset]] no conoce {', '.join(sorted(unknown))}")
        st = a.get("style", [])
        st = [st] if isinstance(st, str) else list(st)
        if missing := [s for s in st if s not in styles]:
            raise ValueError(f"{name}: no hay [styles] {', '.join(missing)}")
        refs = [_path(root, r) for r in a.get("refs", [])]
        for r in refs:
            if not r.exists():
                raise FileNotFoundError(f"{name}: no existe la referencia {r}")
        alpha = a.get("alpha", "cutout")
        if alpha not in ALPHA_KINDS:
            raise ValueError(f"{name}: alpha tiene que ser {', '.join(ALPHA_KINDS)}")
        tile = a.get("tile", {})
        tile = {"": tile} if isinstance(tile, str) else dict(tile)
        if bad := [v for v in tile.values() if v not in ("x", "y", "xy")]:
            raise ValueError(f"{name}: tile tiene que ser x, y o xy, no {bad[0]!r}")
        split = list(a.get("split", []))
        if extra := [p for p in tile if p and p not in split]:
            raise ValueError(f"{name}: tile nombra piezas que no están en split: {', '.join(extra)}")
        seam = a.get("seam", "cut")
        if seam not in SEAMS:
            raise ValueError(f"{name}: seam tiene que ser {', '.join(SEAMS)}")
        role = a.get("ref_role", "style")
        if role not in REF_CLAUSE:
            raise ValueError(f"{name}: ref_role tiene que ser {' o '.join(REF_CLAUSE)}")
        assets.append(Asset(
            name=name, prompt=a["prompt"].strip(), styles=st, refs=refs, ref_role=role,
            aspect=a.get("aspect", "1:1"), alpha=alpha, tile=tile, seam=seam, seam_px=float(a.get("seam_px", 0.12)),
            trim=bool(a.get("trim", True)), split=split, same_height=bool(a.get("same_height", False)),
            height=a.get("height"), n=int(a.get("n", 0)), models=list(a.get("models", []))))
    if not assets:
        raise ValueError("la config no tiene ningún [[asset]]")
    if len({a.name for a in assets}) != len(assets):
        raise ValueError("hay assets repetidos")
    for a in assets:
        imageapi.parse_aspect(a.aspect)
        if extra := [m for m in a.models if m not in models]:
            raise ValueError(f"{a.name}: models nombra modelos que no están en [gen] models: {', '.join(extra)}")

    images = int(g.get("images_per_asset", 1))
    if images < 1:
        raise ValueError("images_per_asset tiene que ser 1 o más")
    out_dir = _path(root, g.get("out_dir", "."))
    ref_bg = g.get("ref_bg", "#FFFFFF")
    if ref_bg:
        parse_rgb(ref_bg)
    return GenConfig(
        root=root, out_dir=out_dir, set_name=g.get("set", out_dir.name), models=models, images_per_asset=images,
        max_usd=float(g.get("max_usd", 5)), max_parallel=int(g.get("max_parallel", 4)),
        key_color=g.get("key_color", "#00FF00"), quality=g.get("quality", "medium"),
        resolution=g.get("resolution", "1K"), seed=g.get("seed"), ref_bg=ref_bg or None, styles=styles,
        assets=assets)


def mode(asset: Asset, spec: imageapi.ImageModelSpec) -> str:
    """Cómo sale el fondo: "opaque", "native" (el modelo devuelve alfa) o "key" (color plano que se keyea)."""
    if asset.alpha == "opaque":
        return "opaque"
    return "native" if spec.transparent else "key"


def prompt_for(cfg: GenConfig, asset: Asset, spec: imageapi.ImageModelSpec) -> str:
    parts = [cfg.styles[s] for s in asset.styles] + [asset.prompt]
    if asset.refs:
        parts.append(REF_CLAUSE[asset.ref_role])
    m = mode(asset, spec)
    if m != "opaque":
        parts.append(BACKGROUND_CLAUSE[m].format(key=f"{cfg.key_color.upper()} ({_color_name(cfg.key_color)})"))
    return "\n\n".join(parts)


def _color_name(hex_: str) -> str:
    return {"#00FF00": "pure green", "#FF00FF": "magenta", "#0000FF": "pure blue"}.get(hex_.upper(), "solid color")


def request(cfg: GenConfig, t: Task, refs: list[Path] | None = None) -> imageapi.ImageRequest:
    return imageapi.ImageRequest(
        prompt=prompt_for(cfg, t.asset, t.model), refs=refs if refs is not None else t.asset.refs,
        aspect=t.asset.aspect, transparent=mode(t.asset, t.model) == "native", quality=cfg.quality,
        resolution=cfg.resolution, seed=t.seed)


def plan(cfg: GenConfig, every: bool = False) -> list[Task]:
    """Un pedido por modelo, asset e imagen. Con every, también los modelos que el asset no elige (para la
    comparación, que muestra todo lo que se generó en el set)."""
    tasks = []
    for name in cfg.models:
        spec = imageapi.MODELS[name]
        for asset in cfg.assets:
            if asset.models and name not in asset.models and not every:
                continue
            n = asset.n or cfg.images_per_asset
            for k in range(1, n + 1):
                seed = cfg.seed + k - 1 if cfg.seed is not None else None
                t = Task(spec, asset, k, cfg.out_dir / "raw" / asset.name / f"{name}_{k}.png", 0.0, seed, "")
                req = request(cfg, t)
                t.size = spec.size_label(req)
                t.usd = spec.price(req)
                tasks.append(t)
    return tasks


# --- referencias ----------------------------------------------------------------------


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _has_alpha(p: Path) -> bool:
    with Image.open(p) as im:
        return "A" in im.getbands()


def flat_refs(cfg: GenConfig, refs: list[Path]) -> list[Path]:
    """Las referencias RGBA se aplanan sobre ref_bg: con el alfa en 0 y el RGB en negro, varios modelos ven
    un fondo negro. Quedan en refs/ de la salida, con el hash del original en el nombre."""
    if not cfg.ref_bg:
        return refs
    out = []
    for r in refs:
        if not _has_alpha(r):
            out.append(r)
            continue
        im = Image.open(r)
        dest = cfg.out_dir / "refs" / f"{r.stem}_{_sha256(r)[:8]}_{cfg.ref_bg.lstrip('#').upper()}.png"
        if not dest.exists():
            bg = Image.new("RGBA", im.size, parse_rgb(cfg.ref_bg) + (255,))
            bg.alpha_composite(im.convert("RGBA"))
            dest.parent.mkdir(parents=True, exist_ok=True)
            bg.convert("RGB").save(dest)
        out.append(dest)
    return out


# --- dry-run ----------------------------------------------------------------------------


def print_plan(cfg: GenConfig, tasks: list[Task], keys: dict, resumable: dict) -> None:
    used = dict.fromkeys(t.model.name for t in tasks)
    print(f"● gen-images {cfg.set_name}: {len(cfg.assets)} assets, {len(used)} modelos ({', '.join(used)}) → "
          f"{_show(cfg.out_dir)}")
    for a in cfg.assets:
        tile = ", ".join(f"{k or 'imagen'} en {v}" for k, v in a.tile.items())
        print(f"  {a.name}: {a.aspect}, {a.alpha}"
              + (f", refs {', '.join(r.name for r in a.refs)} ({a.ref_role})" if a.refs else "")
              + (f", piezas {', '.join(a.split)}" if a.split else "")
              + (" a la misma altura" if a.split and a.same_height else "")
              + (f", se repite ({tile}, costura {a.seam})" if a.tile else "")
              + (f", alto {a.height} px" if a.height else "")
              + (f", sólo {', '.join(a.models)}" if a.models else ""))
    print(f"\n  {'modelo':26} {'proveedor':9} {'asset':14} {'tamaño':>11} {'fondo':7} {'US$/img':>8} {'imgs':>5} "
          f"{'faltan':>6} {'US$':>6}")
    total = 0.0
    for name in cfg.models:
        spec = imageapi.MODELS[name]
        key = "" if keys.get(spec.provider) else f"  (sin {KEYS[spec.provider]})"
        for a in cfg.assets:
            ts = [t for t in tasks if t.model.name == name and t.asset is a]
            if not ts:
                continue
            todo = [t for t in ts if not t.dest.exists() and t.id not in resumable]
            sub = sum(t.usd for t in todo)
            total += sub
            print(f"  {name:26} {spec.provider:9} {a.name[:14]:14} {ts[0].size:>11} {mode(a, spec):7} "
                  f"{_usd(ts[0].usd):>8} {len(ts):>5} {len(todo):>6} {_usd(sub):>6}{key}")
            key = ""
        if spec.sunset:
            left = (date.fromisoformat(spec.sunset) - date.today()).days
            print(f"  {'':26} " + (f"✗ {spec.endpoint} se apagó el {spec.sunset}" if left <= 0 else
                                   f"! {spec.endpoint} se apaga el {spec.sunset} (en {left} días)"))
    print(f"  {'total estimado':>83} {_usd(total):>6}   (tope max_usd {_usd(cfg.max_usd)})")
    if resumable:
        print(f"  {len(resumable)} pedidos ya enviados se retoman sin volver a pagarlos")


def _placeholder(provider: str) -> Callable[[Path], str]:
    if provider == "fal":
        return lambda p: f"<URL de {_show(p)} subida al CDN de fal>"
    return lambda p: f"<{_show(p)}>"


def print_prompts(cfg: GenConfig, tasks: list[Task]) -> None:
    seen = set()
    for t in tasks:
        key = (t.asset.name, mode(t.asset, t.model))
        if key in seen:
            continue
        seen.add(key)
        how = {"native": "con alfa nativo", "key": f"sobre {cfg.key_color}", "opaque": "opaco"}[key[1]]
        print(f"\n  ── prompt de {t.asset.name} ({how}) ──")
        for line in prompt_for(cfg, t.asset, t.model).splitlines():
            print(f"    {line}")


def print_payloads(cfg: GenConfig, tasks: list[Task]) -> None:
    seen = set()
    for t in tasks:
        if t.model.name in seen:
            continue
        seen.add(t.model.name)
        req = request(cfg, t)  # sin aplanar las referencias: el dry-run no escribe nada
        req = dataclasses.replace(req, prompt=f"<prompt de {t.asset.name}, {len(req.prompt)} caracteres>")
        call = t.model.call(req, _placeholder(t.model.provider))
        print(f"\n  {t.model.name} ({t.asset.name})  POST {call.url}")
        print(f"    {json.dumps(call.body, ensure_ascii=False)}")
        print(f"    precio: {t.model.price_note}  ·  doc: {t.model.docs}")
    if cfg.ref_bg and any(_has_alpha(r) for t in tasks for r in t.asset.refs):
        print(f"\n  Las referencias con transparencia se mandan aplanadas sobre {cfg.ref_bg} (quedan en refs/).")
    notes = {imageapi.PROVIDER_NOTES[t.model.provider] for t in tasks if t.model.provider in imageapi.PROVIDER_NOTES}
    for n in sorted(notes):
        print(f"\n  {n}")


# --- ejecución --------------------------------------------------------------------------


def _record(t: Task, call: imageapi.Call, refs: list[Path]) -> dict:
    return {"id": t.id, "asset": t.asset.name, "model": t.model.name, "provider": t.model.provider,
            "endpoint": call.url, "k": t.k, "seed": t.seed, "size": t.size, "usd_estimate": t.usd,
            "refs": [str(r) for r in refs], "status": "submitted", "handle": None, "submitted": _now()}


def execute(cfg: GenConfig, tasks: list[Task], clients: dict, ledger: Ledger, resumable: dict,
            sleep: Callable[[float], None] = time.sleep, poll_s: float = 3.0, timeout_s: float = 900.0) -> None:
    """Hasta max_parallel pedidos a la vez, cada uno en su hilo: manda, espera, baja y corre el post."""
    lock = threading.Lock()

    def say(msg: str) -> None:
        with lock:
            print(msg, flush=True)

    def one(t: Task) -> None:
        client = clients[t.model.provider]
        refs = flat_refs(cfg, t.asset.refs) if t.asset.refs else []
        req = request(cfg, t, refs)
        if t.id in resumable:
            rec = resumable[t.id]
            say(f"  ▸ {t.id}: retomo el pedido {rec['handle'].get('request_id', '')}")
            res = client.wait(rec["handle"], sleep, poll_s, timeout_s)
        else:
            call = t.model.call(req, client.image_ref)  # sube las referencias al CDN de fal
            with lock:
                rec = ledger.add(_record(t, call, refs))

            def submitted(handle: dict) -> None:
                with lock:
                    ledger.update(rec, handle=handle)

            say(f"  ▸ {t.id}: enviado")
            res = client.run(call, submitted, sleep, poll_s, timeout_s)
        if res.state == "done":
            try:
                client.fetch(res.images[0], t.dest)
            except (imageapi.HttpError, OSError, ValueError) as e:
                res = imageapi.Result("error", detail=f"no pude bajar la imagen: {e}", usage=res.usage)
        with lock:
            ledger.update(rec, status=res.state, detail=res.detail, usage=res.usage, finished=_now())
        if res.state == "done":
            post = run_post(cfg, t, rec, req)
            say(f"  ✓ {t.id} ({t.dest.stat().st_size / 1e6:.1f} MB) · post {_post_summary(post)}")
        elif res.state == "blocked":
            say(f"  ✗ {t.id}: bloqueado por el proveedor — {res.detail}")
        elif res.state == "running":
            say(f"  ! {t.id}: sigue en el proveedor después de {timeout_s / 60:.0f} min; volvé a correr el "
                "comando para retomarlo")
        else:
            say(f"  ✗ {t.id}: {res.detail}")

    with ThreadPoolExecutor(max_workers=max(1, cfg.max_parallel)) as ex:
        futures = {ex.submit(one, t): t for t in tasks}
        try:
            for f in as_completed(futures):
                if err := f.exception():
                    say(f"  ✗ {futures[f].id}: {type(err).__name__}: {err}")
        except KeyboardInterrupt:
            ex.shutdown(wait=False, cancel_futures=True)
            raise


def post_spec(cfg: GenConfig, t: Task) -> bgpost.PostSpec:
    a = t.asset
    return bgpost.PostSpec(expect=a.alpha, key=cfg.key_color if mode(a, t.model) == "key" else None, tile=a.tile,
                           seam=a.seam, seam_px=a.seam_px, trim=a.trim, split=a.split,
                           same_height=a.same_height, height=a.height)


def run_post(cfg: GenConfig, t: Task, rec: dict | None, req: imageapi.ImageRequest | None = None) -> dict:
    """Post de una imagen bajada y su .json de procedencia."""
    if t.post.exists():
        t.post.unlink()
    folder = t.post.parent / t.post.stem
    if folder.exists():
        for p in folder.glob("*.png"):
            p.unlink()
    rep = bgpost.process(t.dest, t.post, post_spec(cfg, t))
    req = req or request(cfg, t)
    rec = rec or {}
    refs = [Path(r) for r in rec.get("refs", [])] or flat_refs(cfg, t.asset.refs)
    with Image.open(t.dest) as im:
        size = list(im.size)
    imgio_json(t.dest.with_suffix(".json"), {
        "set": cfg.set_name, "asset": t.asset.name, "model": t.model.name, "provider": t.model.provider,
        "endpoint": rec.get("endpoint") or t.model.call(req, lambda p: "").url, "model_docs": t.model.docs,
        "prompt": req.prompt, "styles": t.asset.styles,
        "refs": [{"file": _show(r), "sha256": _sha256(r)} for r in refs if r.exists()],
        "refs_source": [{"file": _show(r), "sha256": _sha256(r)} for r in t.asset.refs],
        "background": mode(t.asset, t.model), "size_requested": t.size, "size": size, "seed": t.seed,
        "quality": cfg.quality if t.model.provider == "openai" else None,
        "usd_estimate": t.usd, "price_note": t.model.price_note, "usage": rec.get("usage"),
        "request_id": (rec.get("handle") or {}).get("request_id"), "created": rec.get("finished") or _now(),
        "sha256": _sha256(t.dest), "post": {"file": _show(t.post if not t.asset.split else folder), **rep},
    })
    return rep


def imgio_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


# --- comparación ------------------------------------------------------------------------


def rows(cfg: GenConfig, tasks: list[Task], ledger: Ledger) -> list[dict]:
    out = []
    for t in tasks:
        rec = next((a for a in reversed(ledger.data["attempts"]) if a["id"] == t.id), None)
        status = "done" if t.dest.exists() else rec["status"] if rec else None
        billed = status == "done" or (status == "blocked" and t.model.bills_blocked)
        meta = json.loads(t.dest.with_suffix(".json").read_text(encoding="utf-8")) if (
            t.dest.exists() and t.dest.with_suffix(".json").exists()) else {}
        post = meta.get("post", {})
        out.append({"task": t, "status": STATUS[status], "detail": (rec or {}).get("detail", "") if status != "done"
                    else "", "usd": t.usd if billed else 0.0, "size": meta.get("size"), "post": post})
    return out


def _post_summary(post: dict) -> str:
    if not post:
        return "-"
    bits = [post.get("alpha", {}).get("verdict", "-")]
    for k, v in post.get("seam", {}).items():
        b = v["before"]["verdict"]
        bits.append(f"costura {k} {b}→{v['after']['verdict']}" if "after" in v else f"costura {k} {b}")
    return ", ".join(bits)


def print_table(rs: list[dict]) -> None:
    print(f"\n  {'imagen':40} {'estado':9} {'tamaño':>11} {'post':40} {'US$':>5}")
    for r in rs:
        t = r["task"]
        size = "×".join(map(str, r["size"])) if r["size"] else "-"
        print(f"  {t.id[:40]:40} {r['status']:9} {size:>11} {_post_summary(r['post'])[:40]:40} {_usd(r['usd']):>5}")
        for f in r["post"].get("alpha", {}).get("flags", []) + r["post"].get("notes", []):
            print(f"  {'':40} ! {f[:150]}")
        if r["detail"]:
            print(f"  {'':40} {r['detail'][:150]}")
    print(f"\n  gastado (estimado, a precio de lista): US$ {_usd(sum(r['usd'] for r in rs))}")


def write_markdown(path: Path, cfg: GenConfig, rs: list[dict]) -> None:
    lines = [f"# {cfg.set_name}: comparación de modelos ({date.today().isoformat()})", "",
             f"Modelos: {', '.join(cfg.models)}. Abrí `compare.html` para verlas lado a lado.", "",
             "| asset | modelo | estado | tamaño | post | notas | US$ |", "|---|---|---|---|---|---|---:|"]
    for r in rs:
        t = r["task"]
        notes = r["detail"] or "; ".join(r["post"].get("alpha", {}).get("flags", []) + r["post"].get("notes", []))
        size = "×".join(map(str, r["size"])) if r["size"] else "-"
        lines.append(f"| {t.asset.name} | {t.model.name} #{t.k} | {r['status']} | {size} | "
                     f"{_post_summary(r['post'])} | {notes.replace('|', '/')} | {_usd(r['usd'])} |")
    lines += ["", f"Gastado (estimado, a precio de lista): US$ {_usd(sum(r['usd'] for r in rs))}."]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_html(path: Path, cfg: GenConfig, rs: list[dict]) -> None:
    """Grilla asset × modelo, cada imagen post sobre damero y sobre el violeta de la base."""
    def rel(p: Path) -> str:
        return html.escape(os.path.relpath(p, path.parent))

    cells: dict[tuple[str, str], list[str]] = {}
    for r in rs:
        t = r["task"]
        if r["status"] != "ok":
            body = f'<p class="bad">{html.escape(r["status"])}: {html.escape(r["detail"][:200])}</p>'
        else:
            folder = t.post.parent / t.post.stem
            imgs = sorted(folder.glob("*.png")) if t.asset.split else [t.post]
            body = "".join(f'<figure><img src="{rel(p)}" loading="lazy"><figcaption>{html.escape(p.stem)}'
                           f'</figcaption></figure>' for p in imgs if p.exists())
            body += (f'<p>{html.escape(_post_summary(r["post"]))} · US$ {_usd(r["usd"])} · '
                     f'<a href="{rel(t.dest)}">original</a> · <a href="{rel(t.dest.with_suffix(".json"))}">json</a></p>')
            flags = r["post"].get("alpha", {}).get("flags", []) + r["post"].get("notes", [])
            body += "".join(f'<p class="warn">{html.escape(f)}</p>' for f in flags)
        cells.setdefault((t.asset.name, t.model.name), []).append(body)
    head = "".join(f"<th>{html.escape(m)}</th>" for m in cfg.models)
    trs = []
    for a in cfg.assets:
        tds = "".join(f'<td>{"".join(cells.get((a.name, m), ["-"]))}</td>' for m in cfg.models)
        trs.append(f'<tr><th>{html.escape(a.name)}</th>{tds}</tr>')
    path.write_text(f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(cfg.set_name)}: modelos</title>
<style>
:root {{ --bg: #121522; --fg: #eef0f6; --muted: #9aa3bd; --line: #2f3750; --warn: #f2c230; --bad: #e8392e; }}
body {{ background: var(--bg); color: var(--fg); font: 14px/1.4 system-ui, sans-serif; margin: 16px; }}
.wrap {{ overflow-x: auto; }}
table {{ border-collapse: collapse; }}
th, td {{ border: 1px solid var(--line); padding: 8px; vertical-align: top; }}
td {{ min-width: 280px; max-width: 520px; }}
figure {{ margin: 0 0 8px; }}
img {{ max-width: 100%; display: block; background: repeating-conic-gradient(#3a4060 0 25%, #2a2f48 0 50%) 0 0 / 16px 16px; }}
body.violet img {{ background: #3d2563; }}
figcaption, p {{ color: var(--muted); margin: 2px 0; font-size: 12px; }}
.warn {{ color: var(--warn); }} .bad {{ color: var(--bad); }}
a {{ color: var(--fg); }}
</style></head><body>
<h1>{html.escape(cfg.set_name)}</h1>
<p><label><input type="checkbox" onchange="document.body.classList.toggle('violet', this.checked)"> fondo violeta en vez de damero</label></p>
<div class="wrap"><table><tr><th></th>{head}</tr>{''.join(trs)}</table></div>
</body></html>
""", encoding="utf-8")


# --- comando ----------------------------------------------------------------------------


def run(cfg_path: Path, dry_run: bool = False, yes: bool = False, models: list[str] | None = None,
        assets: list[str] | None = None, post_only: bool = False, env: dict | None = None,
        http: imageapi.Http | None = None, sleep: Callable[[float], None] = time.sleep,
        ask: Callable[[str], str] = input, poll_s: float = 3.0) -> int:
    cfg = load(cfg_path)
    full = load(cfg_path)  # la comparación muestra todo el set, no sólo lo que se eligió con --models o --assets
    for what, chosen, have in (("models", models, cfg.models), ("assets", assets, [a.name for a in cfg.assets])):
        if chosen and (unknown := [c for c in chosen if c not in have]):
            print(f"✗ {', '.join(unknown)} no está en {what} de la config")
            return 1
    if models:
        cfg.models = [m for m in cfg.models if m in models]
    if assets:
        cfg.assets = [a for a in cfg.assets if a.name in assets]
    env = os.environ if env is None else env
    keys = {p: bool(env.get(var)) for p, var in KEYS.items()}
    tasks = plan(cfg)
    ledger = Ledger(cfg.out_dir / "gen.json")
    ledger.data.setdefault("attempts", [])
    resumable = {}
    for t in tasks:
        rec = next((a for a in reversed(ledger.data["attempts"]) if a["id"] == t.id), None)
        if (not t.dest.exists() and rec and rec["status"] == "submitted" and rec.get("handle")
                and _age_hours(rec["submitted"]) < RESUME_HOURS):
            resumable[t.id] = rec

    if post_only:
        done = [t for t in tasks if t.dest.exists()]
        print(f"● post de {len(done)} imágenes ya bajadas de {cfg.set_name}")
        for t in done:
            rec = next((a for a in reversed(ledger.data["attempts"]) if a["id"] == t.id), None)
            rep = run_post(cfg, t, rec)
            print(f"  ✓ {t.id}: {_post_summary(rep)}")
    else:
        print_plan(cfg, tasks, keys, resumable)
        dry = dry_run or not any(keys.values())
        if dry:
            print_prompts(cfg, tasks)
            print_payloads(cfg, tasks)
            why = "--dry-run" if dry_run else f"no hay {' ni '.join(KEYS.values())} en el entorno"
            print(f"\n  dry-run ({why}): no se llamó a ninguna API.")
            return 0
        runnable = [t for t in tasks if not t.dest.exists() and keys[t.model.provider]]
        for p, var in KEYS.items():
            skipped = {t.model.name for t in tasks if t.model.provider == p and not t.dest.exists()}
            if skipped and not keys[p]:
                print(f"  ! sin {var}: salteo {', '.join(sorted(skipped))}")
        new = [t for t in runnable if t.id not in resumable]
        cost = sum(t.usd for t in new)
        if cost > cfg.max_usd:
            print(f"✗ la estimación (US$ {_usd(cost)}) pasa el tope max_usd (US$ {_usd(cfg.max_usd)}): "
                  "elegí menos assets o modelos (--assets, --models) o subí max_usd")
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
            if keys["openai"]:
                clients["openai"] = imageapi.OpenAIClient(env["OPENAI_API_KEY"], http)
            if keys["fal"]:
                clients["fal"] = imageapi.FalImageClient(env["FAL_KEY"], http)
            print()
            try:
                execute(cfg, runnable, clients, ledger, resumable, sleep=sleep, poll_s=poll_s)
            except KeyboardInterrupt:
                print("\n  cortado. Lo enviado a fal sigue en el proveedor: volvé a correr el comando en menos de "
                      f"{RESUME_HOURS} h para bajarlo sin pagarlo de nuevo.")
                return 130

    if not any(t.dest.exists() for t in tasks) and not ledger.data["attempts"]:
        return 0
    print_table(rows(cfg, tasks, ledger))
    tried = {a["id"] for a in ledger.data["attempts"]}
    shown = [t for t in plan(full, every=True) if t.dest.exists() or t.id in tried]
    full.models = [m for m in full.models if any(t.model.name == m for t in shown)]
    full.assets = [a for a in full.assets if any(t.asset.name == a.name for t in shown)]
    rs = rows(full, shown, ledger)
    write_markdown(full.out_dir / "compare.md", full, rs)
    write_html(full.out_dir / "compare.html", full, rs)
    print(f"\n  comparación en {_show(cfg.out_dir / 'compare.html')} y {_show(cfg.out_dir / 'compare.md')}, "
          f"detalle por pedido en {_show(ledger.path)}")
    return 0
