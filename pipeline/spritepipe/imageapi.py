"""Clientes HTTP de los modelos de imagen: la Image API de OpenAI (GPT Image) y la cola de fal.ai.

Sólo stdlib (urllib), con el mismo transporte inyectable de videoapi para que los tests no llamen a nada
real. Las keys viajan en headers y nunca se escriben a disco ni se imprimen.

Los IDs, parámetros, tamaños y precios de MODELS salen de la documentación de cada proveedor leída el
2026-10-16 (el link va en cada modelo). Cambian seguido: antes de gastar, el dry-run muestra el pedido
exacto y el precio que se asumió.
"""

from __future__ import annotations

import base64
import math
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from . import videoapi
from .videoapi import FAL_QUEUE, HttpError, _brief, _drop_none, mime

Http = videoapi.Http


@dataclass
class ImageRequest:
    """Lo mismo para todos los modelos; cada ImageModelSpec lo traduce a los campos de su API."""

    prompt: str
    refs: list[Path]  # imágenes de referencia (estilo, personaje)
    aspect: str  # "16:9", "3:1", "1:1"...: cada modelo usa el tamaño permitido más parecido
    transparent: bool  # pedir alfa nativo (sólo si el modelo lo soporta)
    quality: str  # OpenAI: low | medium | high | xhigh | max
    resolution: str  # "1K" | "2K" | "4K": escala del tamaño, en los modelos que la eligen
    seed: int | None


@dataclass
class Call:
    url: str
    body: dict


@dataclass
class Result:
    state: str  # "done" | "blocked" | "error" | "running"
    images: list[str] = field(default_factory=list)  # URLs o data: URIs
    detail: str = ""
    usage: dict | None = None


def parse_aspect(aspect: str) -> float:
    try:
        w, h = (float(v) for v in aspect.split(":"))
        if w > 0 and h > 0:
            return w / h
    except ValueError:
        pass
    raise ValueError(f"aspect inválido {aspect!r}: usá ANCHO:ALTO, por ejemplo 16:9")


def nearest(aspect: str, options: dict) -> str:
    """La clave de options ("16:9", "21:9"...) cuya proporción está más cerca de aspect (en log)."""
    want = math.log(parse_aspect(aspect))
    return min(options, key=lambda k: abs(math.log(parse_aspect(k)) - want))


def data_url(p: Path) -> str:
    return f"data:{mime(p)};base64,{base64.b64encode(p.read_bytes()).decode()}"


def save_data_url(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    part.write_bytes(base64.b64decode(url.split(",", 1)[1]))
    part.replace(dest)


# --- OpenAI ----------------------------------------------------------------------------
# https://developers.openai.com/api/docs/guides/image-generation
# https://developers.openai.com/api/reference/resources/images

OPENAI_API = "https://api.openai.com/v1"
OPENAI_TIMEOUT_S = 300  # "Complex prompts may take up to 2 minutes to process"
OPENAI_RETRIES = 3  # 429 de cuota por minuto y 5xx; los errores de crédito no se reintentan
OPENAI_NO_RETRY = {"insufficient_quota", "billing_hard_limit_reached", "credit_balance_exhausted"}


class OpenAIClient:
    """Image API: un POST que devuelve la imagen en base64 (sin cola: no se puede retomar)."""

    provider = "openai"

    def __init__(self, key: str, http: Http | None = None):
        self._headers = {"Authorization": f"Bearer {key}"}
        self.http = http or Http(timeout=OPENAI_TIMEOUT_S)

    def image_ref(self, p: Path) -> str:
        return data_url(p)  # JSON de /images/edits: image_url acepta "a base64 data URL"

    def run(self, call: Call, submitted: Callable[[dict], None], sleep: Callable[[float], None],
            poll_s: float, timeout_s: float) -> Result:
        for attempt in range(OPENAI_RETRIES + 1):
            try:
                r = self.http.json("POST", call.url, self._headers, call.body)
                break
            except HttpError as e:
                err = e.body.get("error") if isinstance(e.body, dict) else None
                code = (err or {}).get("code") or ""
                if e.status in (429, 500, 502, 503) and code not in OPENAI_NO_RETRY and attempt < OPENAI_RETRIES:
                    sleep(10 * (attempt + 1))
                    continue
                return openai_error(e)
            except OSError as e:
                if attempt < OPENAI_RETRIES:
                    sleep(10 * (attempt + 1))
                    continue
                return Result("error", detail=f"red: {e}")
        imgs = [d["b64_json"] for d in r.get("data") or [] if d.get("b64_json")]
        if not imgs:
            return Result("error", detail=f"respuesta sin imagen: {_brief({k: v for k, v in r.items() if k != 'data'})}",
                          usage=r.get("usage"))
        fmt = r.get("output_format") or call.body.get("output_format") or "png"
        return Result("done", [f"data:image/{fmt};base64,{b}" for b in imgs], usage=r.get("usage"))

    def wait(self, handle: dict, sleep, poll_s, timeout_s) -> Result:
        return Result("error", detail="un pedido a OpenAI no se puede retomar: es sincrónico")

    def fetch(self, image: str, dest: Path) -> None:
        save_data_url(image, dest)


def openai_error(e: HttpError) -> Result:
    """{"error": {"type", "code", "message", "moderation_details"}}. code = moderation_blocked es moderación."""
    err = e.body.get("error") if isinstance(e.body, dict) else None
    if not isinstance(err, dict):
        return Result("error", detail=str(e))
    code, msg = err.get("code") or err.get("type") or "", err.get("message") or ""
    if code == "moderation_blocked":
        md = err.get("moderation_details") or {}
        cats = ", ".join(md.get("categories") or [])
        return Result("blocked", detail=f"moderation_blocked ({md.get('moderation_stage', '?')}"
                                        + (f": {cats}" if cats else "") + f") {msg}".rstrip())
    hint = ""
    if e.status == 403 and "verif" in msg.lower():
        hint = " (la organización tiene que estar verificada: platform.openai.com/settings/organization/general)"
    return Result("error", detail=f"HTTP {e.status} {code}: {msg}{hint}".strip())


# --- fal.ai ----------------------------------------------------------------------------
# https://fal.ai/docs/documentation/model-apis/inference/queue.md


class FalImageClient:
    """La cola de fal (la misma que el bake-off de video), leyendo images[] en vez de video."""

    provider = "fal"

    def __init__(self, key: str, http: Http | None = None):
        self._fal = videoapi.FalClient(key, http)
        self.http = self._fal.http

    def image_ref(self, p: Path) -> str:
        return self._fal.image_ref(p)  # al CDN de fal, con expiración de 24 h

    def run(self, call: Call, submitted: Callable[[dict], None], sleep: Callable[[float], None],
            poll_s: float, timeout_s: float) -> Result:
        endpoint = call.url.removeprefix(FAL_QUEUE + "/")
        try:
            handle = self._fal.submit(endpoint, call.body)
        except HttpError as e:
            return fal_result(videoapi.fal_error(e))
        except OSError as e:
            return Result("error", detail=f"red: {e}")
        submitted(handle)
        return self.wait(handle, sleep, poll_s, timeout_s)

    def wait(self, handle: dict, sleep: Callable[[float], None], poll_s: float, timeout_s: float) -> Result:
        t0 = time.monotonic()
        while True:
            try:
                s = self.http.json("GET", handle["status_url"], self._fal._headers)
            except OSError:
                s = {"status": "IN_PROGRESS"}
            except HttpError as e:
                if e.status not in (429, 500, 502, 503, 504):
                    return fal_result(videoapi.fal_error(e))
                s = {"status": "IN_PROGRESS"}
            status = s.get("status")
            if status == "COMPLETED":
                break
            if status not in ("IN_QUEUE", "IN_PROGRESS"):
                return Result("error", detail=f"estado desconocido de la cola: {_brief(s)}")
            if time.monotonic() - t0 > timeout_s:
                return Result("running", detail="sigue en la cola")
            sleep(poll_s)
        try:
            r = self.http.json("GET", handle["response_url"], self._fal._headers)
        except HttpError as e:
            return fal_result(videoapi.fal_error(e))
        urls = [i["url"] for i in r.get("images") or [] if isinstance(i, dict) and i.get("url")]
        # Algunos modelos devuelven la imagen y marcan si su filtro la vio NSFW (y la entregan en negro)
        nsfw = [i for i, f in enumerate(r.get("has_nsfw_concepts") or []) if f]
        if urls and not nsfw:
            return Result("done", urls, detail=r.get("description") or "")
        if nsfw:
            return Result("blocked", detail=f"has_nsfw_concepts en {nsfw}: el filtro de fal tapó la imagen")
        if s.get("error_type") in videoapi.FAL_MODERATION_TYPES:
            return Result("blocked", detail=f"{s['error_type']}: {s.get('error', '')}")
        return Result("error", detail=f"{s.get('error_type') or 'sin imagen'}: {s.get('error') or _brief(r)}")

    def fetch(self, image: str, dest: Path) -> None:
        if image.startswith("data:"):
            save_data_url(image, dest)
        else:
            self.http.download(image, dest)  # fal.media es público: la key no viaja a otro host


def fal_result(p: videoapi.Poll) -> Result:
    return Result(p.state, detail=p.detail)


# --- Modelos ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ImageModelSpec:
    name: str  # va al nombre del archivo: raw/<asset>/<name>_<n>.png
    provider: str  # "openai" | "fal"
    endpoint: str  # modelo de OpenAI, o endpoint de fal sin referencias
    edit_endpoint: str | None  # endpoint de fal con referencias (None: las referencias van al mismo)
    transparent: bool  # si devuelve alfa nativo
    max_refs: int
    size: Callable[[ImageRequest], tuple[object, str]]  # pedido -> (valor del campo de tamaño, etiqueta)
    build: Callable[[ImageRequest, Callable[[Path], str], object], dict]  # (pedido, imagen -> ref, tamaño) -> cuerpo
    price: Callable[[ImageRequest], float]  # US$ por imagen, estimado
    price_note: str
    docs: str
    bills_blocked: bool  # si puede cobrar lo que bloquea la moderación (si la doc no lo aclara: True)
    sunset: str | None = None
    route: Callable[[ImageRequest], str] | None = None  # endpoint de fal según el pedido, si no alcanza con dos

    def url(self, req: ImageRequest) -> str:
        if self.provider == "openai":
            return f"{OPENAI_API}/images/{'edits' if req.refs else 'generations'}"
        if self.route:
            return f"{FAL_QUEUE}/{self.route(req)}"
        return f"{FAL_QUEUE}/{self.edit_endpoint if req.refs and self.edit_endpoint else self.endpoint}"

    def call(self, req: ImageRequest, img: Callable[[Path], str]) -> Call:
        if len(req.refs) > self.max_refs:
            raise ValueError(f"{self.name} acepta hasta {self.max_refs} referencias, no {len(req.refs)}")
        value, _ = self.size(req)
        return Call(self.url(req), self.build(req, img, value))

    def size_label(self, req: ImageRequest) -> str:
        return self.size(req)[1]


# OpenAI GPT Image 2 y 2.5: tamaño libre (lados múltiplos de 16, proporción entre 1:3 y 3:1, lado máximo
# 3840, entre 655.360 y 8.294.400 px; por encima de 2560×1440 es experimental).
# "1K": ~1 Mpx. "2K": lo más grande que entra en 2560×1440 (o 1440×2560), el límite de lo no experimental.
# "4K": lo más grande que entra en 3840×2160, experimental.
OPENAI_BOX = {"2K": (2560, 1440), "4K": (3840, 2160)}
OPENAI_QUALITY_BASE = {"gpt-image-2": {"low": 16, "medium": 48, "high": 96},
                       "gpt-image-2.5": {"low": 16, "medium": 24, "high": 48, "xhigh": 64, "max": 96}}
OPENAI_IMAGE_OUT = 30 / 1e6  # US$ por token de imagen de salida (2, 2.5-sunburst y 2.5-flare)
OPENAI_TEXT_IN = 5 / 1e6
OPENAI_IMAGE_IN = 8 / 1e6
# La doc no da tokens de entrada para las referencias en 2 ni en 2.5 (en gpt-image-2 "processes every image
# input at high fidelity"). Se asume lo de gpt-image-1 con input_fidelity high a 1536×1024: 65 + 129 × 6
# tiles + 6.240. El real queda en usage.input_tokens_details.image_tokens del .json de procedencia.
OPENAI_REF_TOKENS = 65 + 129 * 6 + 6240


def openai_size(req: ImageRequest) -> tuple[str, str]:
    r = min(max(parse_aspect(req.aspect), 1 / 3), 3)
    if req.resolution in OPENAI_BOX:
        long, short = OPENAI_BOX[req.resolution]
        bw, bh = (long, short) if r >= 1 else (short, long)
        w, h = (bw, bw / r) if bw / r <= bh else (bh * r, bh)
        w, h = int(w // 16 * 16), int(h // 16 * 16)
    else:
        w = round(math.sqrt(1024 * 1024 * r) / 16) * 16
        h = round(math.sqrt(1024 * 1024 / r) / 16) * 16
    while max(w, h) > 3 * min(w, h):  # al redondear a 16 la proporción puede pasar apenas de 3:1
        w, h = w - 16 * (w > h), h - 16 * (h > w)
    while w * h < 655_360:
        w, h = w + 16 * (w >= h), h + 16 * (h > w)
    return f"{w}x{h}", f"{w}×{h}"


def openai_output_tokens(family: str, quality: str, w: int, h: int) -> int:
    """La fórmula de la calculadora de tokens de la guía de generación de imágenes."""
    base = OPENAI_QUALITY_BASE[family].get(quality)
    if base is None:
        raise ValueError(f"{family} no acepta quality {quality!r}: {', '.join(OPENAI_QUALITY_BASE[family])}")
    s = base / (max(w, h) / min(w, h))
    low = math.floor(s)
    short = low + low % 2 if s - low == 0.5 else round(s)
    grid = base * short
    return math.ceil(grid * (2e6 + w * h) / 4e6)


def _openai_price(family: str):
    def price(req: ImageRequest) -> float:
        w, h = (int(v) for v in openai_size(req)[0].split("x"))
        out = openai_output_tokens(family, req.quality, w, h) * OPENAI_IMAGE_OUT
        text = len(req.prompt) / 4 * OPENAI_TEXT_IN
        refs = len(req.refs) * OPENAI_REF_TOKENS * OPENAI_IMAGE_IN
        return round(out + text + refs, 4)
    return price


def _openai(model: str):
    def build(req: ImageRequest, img, size) -> dict:
        body = {"model": model, "prompt": req.prompt, "n": 1, "size": size, "quality": req.quality,
                "output_format": "png", "background": "transparent" if req.transparent else "opaque"}
        if req.refs:
            body["images"] = [{"image_url": img(p)} for p in req.refs]
        return body  # sin seed: la Image API no lo tiene; sin input_fidelity: 2 no lo deja tocar, 2.5 no lo documenta
    return build


def _openai_spec(model: str, family: str, note: str, transparent: bool = True) -> ImageModelSpec:
    return ImageModelSpec(
        name=model, provider="openai", endpoint=model, edit_endpoint=None, transparent=transparent, max_refs=16,
        size=openai_size, build=_openai(model), price=_openai_price(family), bills_blocked=True,
        price_note=note, docs=f"https://developers.openai.com/api/docs/models/{model}")


OPENAI_NOTE = ("US$30 por millón de tokens de imagen de salida (con la fórmula de la calculadora de la guía), más "
               "texto a US$5/M e imágenes de entrada a US$8/M. Las referencias se estiman en {}.{:03d} tokens cada "
               "una: la doc no da cuántos usan en este modelo").format(OPENAI_REF_TOKENS // 1000, OPENAI_REF_TOKENS % 1000)

def _fal_docs(endpoint: str) -> str:
    return f"https://fal.ai/models/{endpoint}/api"


def _ratio_size(pixels: int, multiple: int = 16, min_px: int = 0):
    """Tamaño libre {width, height}: la proporción pedida con a lo sumo `pixels` px, lados múltiplos de 16."""
    def size(req: ImageRequest) -> tuple[dict, str]:
        r = parse_aspect(req.aspect)
        w = int(math.sqrt(pixels * r) // multiple * multiple)
        h = int(math.sqrt(pixels / r) // multiple * multiple)
        while w * h < min_px:
            w, h = w + multiple * (w >= h), h + multiple * (h > w)
        return {"width": w, "height": h}, f"{w}×{h}"
    return size


def _aspect_size(options: tuple[str, ...], resolution: Callable[[ImageRequest], str] | None = None):
    """Proporción de una lista fija (la más parecida a la pedida), más la resolución si el modelo la elige."""
    def size(req: ImageRequest) -> tuple[dict, str]:
        a = nearest(req.aspect, dict.fromkeys(options))
        res = resolution(req) if resolution else None
        return _drop_none({"aspect_ratio": a, "resolution": res}), f"{a} {res}" if res else a
    return size


# GPT Image 2.5 en fal: los mismos campos que la Image API, con image_size {width, height} y alfa nativo.
def _gpt_fal(req: ImageRequest, img, size) -> dict:
    return _drop_none({
        "prompt": req.prompt, "image_urls": [img(p) for p in req.refs] or None, "image_size": size,
        "quality": req.quality, "background": "transparent" if req.transparent else "opaque",
        "output_format": "png", "num_images": 1})  # sin seed en el schema


def _gpt_fal_size(req: ImageRequest) -> tuple[dict, str]:
    w, h = (int(v) for v in openai_size(req)[0].split("x"))
    return {"width": w, "height": h}, f"{w}×{h}"


NANO_ASPECTS = ("21:9", "16:9", "3:2", "4:3", "5:4", "1:1", "4:5", "3:4", "2:3", "9:16")
NANO_21_ASPECTS = NANO_ASPECTS + ("4:1", "1:4", "8:1", "1:8")
# Nano Banana 2.1: tokens (imagen de salida a US$35,294/M). La página da el costo con ~100 tokens de prompt y
# thinking medium: 1K 0,040, 2K 0,059, 4K 0,134; dos imágenes de entrada de 1K suman 0,004.
NANO_21_PRICE = {"1K": 0.040, "2K": 0.059, "4K": 0.134}
NANO_21_REF = 0.002
NANO_PRO_PRICE = {"1K": 0.15, "2K": 0.15, "4K": 0.30}  # 4K se cobra doble


def _nano(req: ImageRequest, img, size) -> dict:
    return _drop_none({
        "prompt": req.prompt, "image_urls": [img(p) for p in req.refs] or None, **size,
        "output_format": "png", "num_images": 1, "seed": req.seed})  # safety_tolerance queda en "4", el default


def _nano_res(req: ImageRequest) -> str:
    return req.resolution if req.resolution in ("1K", "2K", "4K") else "1K"


# Seedream 5.0 Pro: image_size libre con área entre 1024² y 2048²; hasta 1536² cuesta la mitad.
SEEDREAM_PIXELS = {"1K": 1024 * 1024, "2K": 1536 * 1536, "4K": 2048 * 2048}


def _seedream_size(req: ImageRequest) -> tuple[dict, str]:
    px = SEEDREAM_PIXELS.get(req.resolution, SEEDREAM_PIXELS["2K"])
    return _ratio_size(px, min_px=1024 * 1024)(req)


def _seedream(req: ImageRequest, img, size) -> dict:
    # Sin seed (no está en el schema de v5). output_format por defecto es jpeg: se pide png.
    return _drop_none({"prompt": req.prompt, "image_urls": [img(p) for p in req.refs] or None, "image_size": size,
                       "output_format": "png", "num_images": 1})


def _seedream_price(req: ImageRequest) -> float:
    w, h = (int(v) for v in _seedream_size(req)[1].split("×"))
    return round((0.0675 if w * h <= 1536 * 1536 else 0.135) + 0.0045 * max(0, len(req.refs) - 1), 4)


FLUX3_ASPECTS = ("21:9", "2:1", "16:9", "3:2", "7:5", "4:3", "5:4", "1:1", "4:5", "3:4", "5:7", "2:3", "9:16", "1:2")


def _flux3(req: ImageRequest, img, size) -> dict:
    # Sin seed ni num_images. safety_tolerance (entero 0-4) queda en 2, el default.
    return _drop_none({"prompt": req.prompt, "image_urls": [img(p) for p in req.refs] or None, **size,
                       "output_format": "png"})


KONTEXT_ASPECTS = ("21:9", "16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16", "9:21")


def _kontext(req: ImageRequest, img, size) -> dict:
    refs = ({"image_url": img(req.refs[0])} if len(req.refs) == 1 else
            {"image_urls": [img(p) for p in req.refs]} if req.refs else {})
    return _drop_none({"prompt": req.prompt, **refs, **size, "output_format": "png", "num_images": 1,
                       "seed": req.seed})  # guidance_scale 3,5 y safety_tolerance "2" quedan en el default


def _kontext_route(req: ImageRequest) -> str:
    return ("fal-ai/flux-pro/kontext" if len(req.refs) == 1 else "fal-ai/flux-pro/kontext/multi" if req.refs
            else "fal-ai/flux-pro/kontext/text-to-image")


FAL_BLOCKED = ("fal: si el filtro bloquea el pedido responde 422 content_policy_violation (con model_moderated si "
               "rechaza el dueño del modelo). No aclara si eso se cobra (pricing: \"you pay only for successful "
               "outputs\"; FAQ: un 422 puede cobrarse si ya usó GPU): se cuenta como cobrado")

PROVIDER_NOTES = {
    "openai": "OpenAI: la guía avisa que puede hacer falta verificar la organización (help.openai.com/en/articles/"
              "10910291) para usar GPT Image; ninguna doc oficial dice qué modelos ni qué error devuelve. Tampoco "
              "dice si cobra lo que bloquea la moderación (moderation_blocked): se cuenta como cobrado.",
    "fal": FAL_BLOCKED + ".",
}

MODELS: dict[str, ImageModelSpec] = {m.name: m for m in [
    _openai_spec("gpt-image-2.5-sunburst", "gpt-image-2.5",
                 "El más capaz para editar con referencias. " + OPENAI_NOTE),
    _openai_spec("gpt-image-2.5-flare", "gpt-image-2.5",
                 "El rápido de la 2.5, mismo precio por token que sunburst. " + OPENAI_NOTE),
    _openai_spec("gpt-image-2", "gpt-image-2",
                 "Fondo transparente \"in preview\". " + OPENAI_NOTE),
    ImageModelSpec(
        name="gpt-image-2.5-sunburst-fal", provider="fal", endpoint="openai/gpt-image-2.5/sunburst/text-to-image",
        edit_endpoint="openai/gpt-image-2.5/sunburst/edit", transparent=True, max_refs=16, size=_gpt_fal_size,
        build=_gpt_fal, price=_openai_price("gpt-image-2.5"), bills_blocked=True,
        price_note="GPT Image 2.5 Sunburst servido por fal, con FAL_KEY: los mismos tokens que en OpenAI (US$30/M "
                   "de imagen de salida, 8/M de entrada, 5/M de texto), redondeado al centésimo de centavo. Las "
                   f"referencias se estiman en {OPENAI_REF_TOKENS // 1000}.{OPENAI_REF_TOKENS % 1000:03d} tokens "
                   "cada una",
        docs=_fal_docs("openai/gpt-image-2.5/sunburst/edit")),
    ImageModelSpec(
        name="gpt-image-2.5-flare-fal", provider="fal", endpoint="openai/gpt-image-2.5/flare/text-to-image",
        edit_endpoint="openai/gpt-image-2.5/flare/edit", transparent=True, max_refs=16, size=_gpt_fal_size,
        build=_gpt_fal, price=_openai_price("gpt-image-2.5"), bills_blocked=True,
        price_note="GPT Image 2.5 Flare servido por fal: los mismos tokens que sunburst",
        docs=_fal_docs("openai/gpt-image-2.5/flare/edit")),
    ImageModelSpec(
        name="nano-banana-2.1", provider="fal", endpoint="google/nano-banana-2.1",
        edit_endpoint="google/nano-banana-2.1/edit", transparent=False, max_refs=14,
        size=_aspect_size(NANO_21_ASPECTS, _nano_res), build=_nano,
        price=lambda req: round(NANO_21_PRICE[_nano_res(req)] + NANO_21_REF * len(req.refs), 4), bills_blocked=True,
        price_note="Por tokens (imagen de salida US$35,294/M, entrada 1,764/M). Según la página: 1K ~0,040, "
                   "2K ~0,059, 4K ~0,134 por imagen, más ~0,002 por referencia. Thinking medium (el default)",
        docs=_fal_docs("google/nano-banana-2.1/edit")),
    ImageModelSpec(
        name="nano-banana-pro", provider="fal", endpoint="fal-ai/nano-banana-pro",
        edit_endpoint="fal-ai/nano-banana-pro/edit", transparent=False, max_refs=14,
        size=_aspect_size(NANO_ASPECTS, _nano_res), build=_nano,
        price=lambda req: NANO_PRO_PRICE[_nano_res(req)], bills_blocked=True,
        price_note="US$0,15 por imagen a 1K o 2K, el doble a 4K",
        docs=_fal_docs("fal-ai/nano-banana-pro/edit")),
    ImageModelSpec(
        name="seedream-5-pro", provider="fal", endpoint="bytedance/seedream/v5/pro/text-to-image",
        edit_endpoint="bytedance/seedream/v5/pro/edit", transparent=False, max_refs=10, size=_seedream_size,
        build=_seedream, price=_seedream_price, bills_blocked=True,
        price_note="Precio \"tentativo\": US$0,0675 por imagen de hasta 1536² px, 0,135 hasta 2048², más 0,0045 por "
                   "cada referencia después de la primera. Sin seed",
        docs=_fal_docs("bytedance/seedream/v5/pro/edit")),
    ImageModelSpec(
        name="flux-3", provider="fal", endpoint="blackforestlabs/flux-3/text-to-image",
        edit_endpoint="blackforestlabs/flux-3/edit-image", transparent=False, max_refs=10,
        size=_aspect_size(FLUX3_ASPECTS, lambda req: "1k"), build=_flux3, price=lambda req: 0.048,
        bills_blocked=True,
        price_note="US$0,048 por imagen de 1K (1 Mpx), con cualquier cantidad de referencias. fal no publica el "
                   "precio de 2k ni de 4k: se pide siempre 1k. Sin seed",
        docs=_fal_docs("blackforestlabs/flux-3/edit-image")),
    ImageModelSpec(
        name="flux-kontext-pro", provider="fal", endpoint="fal-ai/flux-pro/kontext/text-to-image",
        edit_endpoint="fal-ai/flux-pro/kontext", route=_kontext_route, transparent=False, max_refs=4,
        size=_aspect_size(KONTEXT_ASPECTS), build=_kontext, price=lambda req: 0.04, bills_blocked=True,
        price_note="US$0,04 por imagen. Una referencia va a .../kontext (image_url); varias, a .../kontext/multi, "
                   "que no dice cuántas acepta (acá se cortan en 4)",
        docs=_fal_docs("fal-ai/flux-pro/kontext")),
]}
