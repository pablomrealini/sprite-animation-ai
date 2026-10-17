"""Clientes HTTP de los modelos image-to-video del bake-off: la cola de fal.ai, Veo por la Gemini API y
Gemini Omni Flash por la Interactions API de la Gemini API.

Sólo stdlib (urllib). El transporte se inyecta para que los tests no llamen a nada real. Las keys
viajan en headers y nunca se escriben a disco ni se imprimen.

Los IDs, parámetros y precios de MODELS salen de la documentación de cada proveedor leída el
2026-10-15 (el link va en cada modelo). Cambian seguido: antes de gastar, el dry-run muestra el
pedido exacto y el precio que se asumió.
"""

from __future__ import annotations

import base64
import json
import shutil
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


class HttpError(Exception):
    def __init__(self, status: int, body, url: str):
        self.status, self.body, self.url = status, body, url
        super().__init__(f"HTTP {status} en {urlparse(url).netloc}{urlparse(url).path}: {_brief(body)}")


def _brief(body, limit: int = 400) -> str:
    s = body if isinstance(body, str) else json.dumps(body, ensure_ascii=False)
    return s if len(s) <= limit else s[:limit] + "…"


class Http:
    """Transporte mínimo: JSON de ida y vuelta, subida de bytes y descarga a archivo."""

    def __init__(self, timeout: float = 120):
        self.timeout = timeout

    def _open(self, req: urllib.request.Request):
        try:
            return urllib.request.urlopen(req, timeout=self.timeout)
        except urllib.error.HTTPError as e:
            raw = e.read()
            try:
                body = json.loads(raw)
            except ValueError:
                body = raw.decode(errors="replace")
            raise HttpError(e.code, body, req.full_url) from None

    def json(self, method: str, url: str, headers: dict, body: dict | None = None) -> dict:
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method,
                                     headers={"Content-Type": "application/json", **headers})
        with self._open(req) as r:
            raw = r.read()
        return json.loads(raw) if raw else {}

    def put(self, url: str, data: bytes, headers: dict) -> None:
        with self._open(urllib.request.Request(url, data=data, method="PUT", headers=headers)) as r:
            r.read()

    def download(self, url: str, dest: Path, headers: dict | None = None) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        part = dest.with_name(dest.name + ".part")
        with self._open(urllib.request.Request(url, headers=headers or {})) as r, open(part, "wb") as f:
            shutil.copyfileobj(r, f)
        part.replace(dest)


@dataclass
class Poll:
    state: str  # "running" | "done" | "blocked" | "error"
    video_url: str | None = None
    detail: str = ""


def mime(p: Path) -> str:
    return {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}[p.suffix.lower()]


# --- fal.ai ---------------------------------------------------------------------
# https://fal.ai/docs/documentation/model-apis/inference/queue.md
# https://fal.ai/docs/documentation/model-apis/errors.md

FAL_QUEUE = "https://queue.fal.run"
FAL_UPLOAD = "https://rest.fal.ai/storage/upload/initiate?storage_type=fal-cdn-v3"
FAL_UPLOAD_TTL_S = 86400  # la pose subida al CDN se borra sola al día
FAL_MODERATION_TYPES = {"content_policy_violation"}


class FalClient:
    """Cola de fal: POST al endpoint, GET al status_url hasta COMPLETED, GET al response_url."""

    provider = "fal"

    def __init__(self, key: str, http: Http | None = None):
        self._headers = {"Authorization": f"Key {key}"}
        self.http = http or Http()
        self._uploaded: dict[Path, str] = {}

    def image_ref(self, p: Path) -> str:
        """URL de la imagen en el CDN de fal. fal desaconseja data URIs de más de unos KB."""
        if p not in self._uploaded:
            r = self.http.json("POST", FAL_UPLOAD, {
                **self._headers, "X-Fal-Object-Lifecycle-Preference": json.dumps(
                    {"expiration_duration_seconds": FAL_UPLOAD_TTL_S})},
                {"file_name": p.name, "content_type": mime(p)})
            self.http.put(r["upload_url"], p.read_bytes(), {"Content-Type": mime(p)})
            self._uploaded[p] = r["file_url"]
        return self._uploaded[p]

    def submit(self, endpoint: str, payload: dict) -> dict:
        r = self.http.json("POST", f"{FAL_QUEUE}/{endpoint}", self._headers, payload)
        # Se usan las URLs que devuelve la cola tal cual, sin armarlas a mano.
        return {"request_id": r["request_id"], "status_url": r["status_url"], "response_url": r["response_url"]}

    def poll(self, handle: dict) -> Poll:
        s = self.http.json("GET", handle["status_url"], self._headers)
        status = s.get("status")
        if status in ("IN_QUEUE", "IN_PROGRESS"):
            return Poll("running", detail=status.lower())
        if status != "COMPLETED":
            return Poll("error", detail=f"estado desconocido de la cola: {_brief(s)}")
        try:
            r = self.http.json("GET", handle["response_url"], self._headers)
        except HttpError as e:
            return fal_error(e)
        url = (r.get("video") or {}).get("url")
        if url:
            return Poll("done", video_url=url)
        # Un pedido que falla también termina en COMPLETED, con error y error_type en el estado.
        if s.get("error_type") in FAL_MODERATION_TYPES:
            return Poll("blocked", detail=f"{s['error_type']}: {s.get('error', '')}")
        return Poll("error", detail=f"{s.get('error_type') or 'sin video'}: {s.get('error') or _brief(r)}")

    def download(self, url: str, dest: Path) -> None:
        self.http.download(url, dest)  # fal.media es público: la key no viaja a otro host


def fal_error(e: HttpError) -> Poll:
    """Moderación o error. fal responde 422 con detail = [{type, msg, categories, ...}]; si el que
    rechaza es el proveedor del modelo (ByteDance, Google, ...), categories trae model_moderated."""
    items = e.body.get("detail") if isinstance(e.body, dict) else None
    items = items if isinstance(items, list) else [{"msg": _brief(e.body)}]
    items = [i if isinstance(i, dict) else {"msg": str(i)} for i in items]
    types = {str(i.get("type", "")) for i in items}
    msg = "; ".join(str(i.get("msg", "")) + (f" [{', '.join(i['categories'])}]" if i.get("categories") else "")
                    for i in items)
    if types & FAL_MODERATION_TYPES:
        return Poll("blocked", detail=f"{', '.join(sorted(types & FAL_MODERATION_TYPES))}: {msg}")
    return Poll("error", detail=f"HTTP {e.status} {', '.join(sorted(t for t in types if t))}: {msg}".replace("  ", " "))


# --- Gemini API (Veo) ---------------------------------------------------------------
# https://ai.google.dev/gemini-api/docs/veo

GEMINI_API = "https://generativelanguage.googleapis.com/v1beta"


class GeminiClient:
    """Veo por la Gemini API: predictLongRunning devuelve una operación que se consulta hasta done."""

    provider = "gemini"

    def __init__(self, key: str, http: Http | None = None):
        self._headers = {"x-goog-api-key": key}
        self.http = http or Http()

    def image_ref(self, p: Path) -> str:
        return base64.b64encode(p.read_bytes()).decode()

    def submit(self, model: str, payload: dict) -> dict:
        r = self.http.json("POST", f"{GEMINI_API}/models/{model}:predictLongRunning", self._headers, payload)
        return {"operation": r["name"]}

    def poll(self, handle: dict) -> Poll:
        op = self.http.json("GET", f"{GEMINI_API}/{handle['operation']}", self._headers)
        if not op.get("done"):
            return Poll("running", detail="generando")
        if "error" in op:
            err = op["error"]
            msg = f"{err.get('code', '')} {err.get('message', '')}".strip()
            return Poll("blocked" if looks_blocked(msg) else "error", detail=msg)
        resp = (op.get("response") or {}).get("generateVideoResponse") or {}
        samples = resp.get("generatedSamples") or []
        uri = ((samples[0] if samples else {}).get("video") or {}).get("uri")
        if uri:
            return Poll("done", video_url=uri)
        # Campos que lee el SDK python-genai (la doc de la Gemini API no los describe).
        reasons = resp.get("raiMediaFilteredReasons") or []
        if resp.get("raiMediaFilteredCount") or reasons:
            return Poll("blocked", detail="; ".join(reasons) or "raiMediaFilteredCount sin motivo")
        return Poll("error", detail=f"operación terminada sin video: {_brief(resp)}")

    def download(self, url: str, dest: Path) -> None:
        # La doc baja con la key y siguiendo redirects; la key sólo va a la API de Google, nunca a otro host.
        own = urlparse(url).netloc == urlparse(GEMINI_API).netloc
        self.http.download(url, dest, self._headers if own else None)


def looks_blocked(msg: str) -> bool:
    """Los errores de seguridad de Veo traen "Support codes: NNNN" y hablan de safety/policy."""
    m = msg.lower()
    return any(w in m for w in ("safety", "blocked", "responsible ai", "support codes", "policy",
                                "person generation", "persongeneration"))


# --- Gemini API (Omni, Interactions API) ---------------------------------------------
# https://ai.google.dev/gemini-api/docs/omni
# https://ai.google.dev/api/interactions-api
# https://ai.google.dev/gemini-api/docs/background-execution
# https://ai.google.dev/gemini-api/docs/api-errors

INTERACTIONS = f"{GEMINI_API}/interactions"
# Fija el esquema con steps (el viejo, con outputs, se quitó el 2026-06-08); los ejemplos REST de
# background execution lo mandan.
INTERACTIONS_REVISION = "2026-05-20"
OMNI_RUNNING = {"in_progress", "queued"}
# "Generation blocked codes" de api-errors. "language" (idioma no soportado) está en esa lista pero no es
# moderación: queda como error.
OMNI_BLOCK_CODES = {"safety", "recitation", "prohibited_content", "spii", "blocklist", "image_safety",
                    "image_prohibited_content", "image_recitation", "image_other", "content_blocked"}


class OmniClient:
    """Omni por la Interactions API: POST con background=true devuelve el id de la interacción, que se
    consulta con GET hasta que sale de in_progress/queued. El GET trae el video en base64."""

    provider = "omni"

    def __init__(self, key: str, http: Http | None = None):
        # La key va en el header, como en los ejemplos con x-goog-api-key; nunca en la URL (?key=).
        self._headers = {"x-goog-api-key": key, "Api-Revision": INTERACTIONS_REVISION}
        self.http = http or Http()

    def image_ref(self, p: Path) -> str:
        return base64.b64encode(p.read_bytes()).decode()

    def submit(self, model: str, payload: dict) -> dict:
        # El modelo va en el cuerpo, no en la URL. El build ya lo trae para que el dry-run lo muestre.
        r = self.http.json("POST", INTERACTIONS, self._headers, {**payload, "model": model})
        return {"interaction": r["id"]}

    def poll(self, handle: dict) -> Poll:
        r = self.http.json("GET", f"{INTERACTIONS}/{handle['interaction']}", self._headers)
        status = r.get("status", "")
        if status in OMNI_RUNNING:
            return Poll("running", detail=status)
        out = _omni_outputs(r)
        video = next((c for c in out if c.get("type") == "video" and (c.get("data") or c.get("uri"))), None)
        if video:
            url = (f"data:{video.get('mime_type', 'video/mp4')};base64,{video['data']}" if video.get("data")
                   else video["uri"])
            return Poll("done", video_url=url, detail="" if status == "completed" else status)
        # Cómo se ve un bloqueo en una interacción en background no está documentado: se leen los
        # errors de la Interaction ({code, message}) con los códigos de api-errors.
        errors = r.get("errors") or ([r["error"]] if isinstance(r.get("error"), dict) else [])
        text = " ".join(c.get("text", "") for c in out if c.get("type") == "text").strip()
        rest = {k: v for k, v in r.items() if k not in ("steps", "input")}  # sin la pose en base64
        return omni_failure(errors, f"{status or 'sin estado'}, sin video: {_brief(text or rest)}")

    def download(self, url: str, dest: Path) -> None:
        if url.startswith("data:"):
            dest.parent.mkdir(parents=True, exist_ok=True)
            part = dest.with_name(dest.name + ".part")
            part.write_bytes(base64.b64decode(url.split(",", 1)[1]))
            part.replace(dest)
            return
        # Con delivery "uri" el video queda en la Files API de Google. La key sólo va a ese host.
        own = urlparse(url).netloc == urlparse(GEMINI_API).netloc
        self.http.download(url, dest, {"x-goog-api-key": self._headers["x-goog-api-key"]} if own else None)


def _omni_outputs(r: dict) -> list[dict]:
    """El contenido de los steps model_output. La doc dice que output_video es sólo del SDK, pero su
    ejemplo REST de delivery "uri" lo lee del JSON crudo: si aparece, también se mira."""
    out = [c for s in r.get("steps") or [] if s.get("type") == "model_output" for c in s.get("content") or []]
    if isinstance(r.get("output_video"), dict):
        out.append({"type": "video", **r["output_video"]})
    return out


def _omni_code(err: dict) -> str:
    # api-errors da el código en snake_case; la referencia de Interaction.errors lo describe como
    # "a URI that identifies the error type". Se toma el último tramo.
    return str(err.get("code") or "").rstrip("/").rsplit("/", 1)[-1]


def omni_failure(errors: list, fallback: str) -> Poll:
    errors = [e if isinstance(e, dict) else {"message": str(e)} for e in errors]
    codes = {_omni_code(e) for e in errors} - {""}
    msg = "; ".join(f"{_omni_code(e)}: {e.get('message', '')}".strip(": ") for e in errors) or fallback
    if codes & OMNI_BLOCK_CODES or (not codes and looks_blocked(msg)):
        return Poll("blocked", detail=msg)
    return Poll("error", detail=msg)


def omni_error(e: HttpError) -> Poll:
    """Error HTTP de la Interactions API: {"error": {"code", "message"}} (api-errors)."""
    err = e.body.get("error") if isinstance(e.body, dict) else None
    if not isinstance(err, dict):
        return Poll("blocked" if looks_blocked(str(e.body)) else "error", detail=str(e))
    p = omni_failure([err], str(e))
    return Poll(p.state, detail=f"HTTP {e.status} {p.detail}")


# --- Modelos ------------------------------------------------------------------------


@dataclass
class Request:
    """Lo mismo para todos los modelos; cada ModelSpec lo traduce a los campos de su API."""

    prompt: str
    image: Path  # primer frame
    last_image: Path | None
    duration: int  # s, ya ajustada a las que acepta el modelo
    aspect_ratio: str
    resolution: str
    audio: bool
    negative_prompt: str | None
    seed: int | None
    refs: tuple[Path, ...] = ()  # imágenes de referencia (hoja de vistas, arma), aparte del primer frame


@dataclass(frozen=True)
class ModelSpec:
    name: str  # va al nombre del archivo: <name>_<anim>_<n>.mp4
    provider: str  # "fal" | "gemini" (Veo) | "omni" (Interactions API); gemini y omni usan GEMINI_API_KEY
    endpoint: str  # endpoint de fal o modelo de la Gemini API
    durations: tuple[int, ...]  # segundos que acepta
    rates: dict[str, float]  # resolución -> US$/s, sin audio si se puede apagar
    build: Callable[[Request, Callable[[Path], str]], dict]  # (pedido, imagen -> referencia) -> cuerpo
    last_frame: bool  # si acepta último frame
    bills_blocked: bool  # si puede cobrar lo que bloquea la moderación (si la doc no lo aclara: True)
    price_note: str
    docs: str
    audio_rates: dict[str, float] | None = None  # US$/s con audio; None: el audio no cambia el precio
    last_frame_endpoint: str | None = None  # si el último frame va a otro endpoint
    billed_seconds: Callable[[int], float] = float  # duración -> segundos que se cobran
    sunset: str | None = None  # fecha en que el proveedor lo apaga
    longest_only: tuple[str, ...] = ()  # resoluciones que sólo salen con la duración más larga
    max_refs: int = 0  # cuántas imágenes de referencia acepta además del primer frame (0: ninguna)
    refs_endpoint: str | None = None  # si con referencias el pedido va a otro endpoint
    refs_last_frame: bool = True  # si con referencias sigue aceptando último frame
    ref_rates: dict[str, float] | None = None  # US$/s con referencias, si cambia (otro endpoint)
    ref_extra: Callable[[int], float] | None = None  # US$ por pedido según cuántas referencias van

    def pick_duration(self, wanted: float, resolution: str = "720p") -> int:
        """La duración permitida más corta que alcanza; si ninguna alcanza, la más larga."""
        if resolution in self.longest_only:
            return max(self.durations)
        return min((d for d in self.durations if d >= wanted), default=max(self.durations))

    def price(self, duration: int, audio: bool, resolution: str, refs: int = 0) -> float:
        rates = self.audio_rates if audio and self.audio_rates else self.rates
        if refs and self.ref_rates:
            rates = self.ref_rates
        if resolution not in rates:
            raise ValueError(f"{self.name} no acepta {resolution}: {', '.join(rates)}")
        extra = self.ref_extra(refs) if refs and self.ref_extra else 0.0
        return round(self.billed_seconds(duration) * rates[resolution] + extra, 4)

    def endpoint_for(self, req: Request) -> str:
        if req.refs and self.refs_endpoint:
            return self.refs_endpoint
        return self.last_frame_endpoint if req.last_image and self.last_frame_endpoint else self.endpoint


def _drop_none(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


def _seedance(version: str):
    def build(req: Request, img) -> dict:
        return _drop_none({
            "prompt": req.prompt, "image_url": img(req.image),
            "end_image_url": img(req.last_image) if req.last_image else None,
            "duration": str(req.duration), "resolution": req.resolution,
            # 2.0 acepta 16:9; en 2.5 image-to-video es siempre "auto" (sigue a la imagen)
            "aspect_ratio": req.aspect_ratio if version == "2.0" else None,
            "generate_audio": req.audio})  # sin seed ni negative_prompt en el schema
    return build


def _kling_v3(req: Request, img) -> dict:
    # Sin resolution ni aspect_ratio (salen de la imagen) ni seed. negative_prompt tiene default
    # "blur, distort, and low quality": sólo se pisa si la config trae uno.
    return _drop_none({
        "prompt": req.prompt, "start_image_url": img(req.image),
        "end_image_url": img(req.last_image) if req.last_image else None,
        "duration": str(req.duration), "generate_audio": req.audio, "negative_prompt": req.negative_prompt})


H3_RESOLUTION = {"480p": "480P", "720p": "768P", "1080p": "2K"}  # 2K y 4K son 768P escalado


def _minimax_h3(req: Request, img) -> dict:
    # El lienzo sigue a la imagen. Sin aspect_ratio, generate_audio ni negative_prompt.
    return _drop_none({
        "prompt": req.prompt, "image_url": img(req.image),
        "end_image_url": img(req.last_image) if req.last_image else None,
        "duration": req.duration, "resolution": H3_RESOLUTION[req.resolution], "seed": req.seed})


WAN_FPS = 16  # nativo de Wan 2.2; fal interpola a 32 fps por defecto (num_interpolated_frames=1)


def _wan_22(req: Request, img) -> dict:
    # No hay duration: la da num_frames (17-161) a frames_per_second.
    return _drop_none({
        "prompt": req.prompt, "image_url": img(req.image),
        "end_image_url": img(req.last_image) if req.last_image else None,
        "num_frames": WAN_FPS * req.duration + 1, "frames_per_second": WAN_FPS,
        "resolution": req.resolution, "aspect_ratio": req.aspect_ratio,
        "negative_prompt": req.negative_prompt, "seed": req.seed})


def _h3_max(req: Request, img) -> dict:
    # Con referencias va a reference-to-video: "The video opens exactly on this image while the references keep
    # the subjects consistent" (image_url) y "ends exactly on this image" (end_image_url). Las referencias se
    # nombran en el prompt como Image 1, Image 2... Sin campo de audio; el lienzo sigue al primer frame.
    # prompt_expansion_mode es obligatorio: "disabled" para que no reescriba el prompt.
    return _drop_none({
        "prompt": req.prompt, "image_url": img(req.image),
        "end_image_url": img(req.last_image) if req.last_image else None,
        "reference_image_urls": [img(r) for r in req.refs] or None,
        "duration": req.duration, "resolution": H3_RESOLUTION[req.resolution],
        "prompt_expansion_mode": "disabled", "seed": req.seed})


def h3_max_ref_extra(n: int) -> float:
    """4.096 tokens de referencias incluidos por pedido; una imagen cuadrada son 1.024 y el excedente cuesta
    US$0,02 cada 1.000 tokens (supone referencias cuadradas, como las de characters/lowpoly/refs/vistas)."""
    return round(max(0, n * 1024 - 4096) * 0.02 / 1000, 4)


KLING_ELEMENT = 4  # un element de Kling: la vista frontal más 1-3 vistas


def _kling_o3(req: Request, img) -> dict:
    # Sin referencias, image-to-video (image_url). Con referencias, reference-to-video (start_image_url) y las
    # referencias como elements: cada 4 imágenes en orden son un element, la primera es la frontal y las otras
    # sus vistas (@Element1, @Element2 en el prompt). Un element necesita al menos una vista además de la frontal.
    # Sin seed, resolution ni negative_prompt en el schema; generate_audio viene en false.
    if not req.refs:
        return _drop_none({
            "prompt": req.prompt, "image_url": img(req.image),
            "end_image_url": img(req.last_image) if req.last_image else None,
            "duration": str(req.duration), "generate_audio": req.audio})
    groups = [req.refs[i:i + KLING_ELEMENT] for i in range(0, len(req.refs), KLING_ELEMENT)]
    if any(len(g) < 2 for g in groups):
        raise ValueError("kling: cada element necesita la frontal y al menos una vista (grupos de 2 a 4 refs)")
    return _drop_none({
        "prompt": req.prompt, "start_image_url": img(req.image),
        "end_image_url": img(req.last_image) if req.last_image else None,
        "elements": [{"frontal_image_url": img(g[0]), "reference_image_urls": [img(r) for r in g[1:]]}
                     for g in groups],
        "duration": str(req.duration), "aspect_ratio": req.aspect_ratio, "generate_audio": req.audio})


def _veo_fal(req: Request, img) -> dict:
    frames = ({"first_frame_url": img(req.image), "last_frame_url": img(req.last_image)} if req.last_image
              else {"image_url": img(req.image)})
    # safety_tolerance ("1"-"6", default "4") queda en el default de fal.
    return _drop_none({
        "prompt": req.prompt, **frames, "duration": f"{req.duration}s", "resolution": req.resolution,
        "aspect_ratio": req.aspect_ratio, "generate_audio": req.audio,
        "negative_prompt": req.negative_prompt, "seed": req.seed})


def _veo_gemini(req: Request, img) -> dict:
    # Forma del ejemplo REST de primer y último frame de la doc (inlineData); el SDK python-genai
    # manda {"bytesBase64Encoded", "mimeType"} en el mismo lugar. durationSeconds va como número,
    # como lo tipa el SDK. Sin seed (el SDK lo rechaza en la Gemini API) ni generateAudio (siempre on).
    def frame(p):
        return {"inlineData": {"mimeType": mime(p), "data": img(p)}}

    inst = {"prompt": req.prompt, "image": frame(req.image)}
    if req.last_image:
        inst["lastFrame"] = frame(req.last_image)
    params = {"aspectRatio": req.aspect_ratio, "resolution": req.resolution, "durationSeconds": req.duration,
              "personGeneration": "allow_adult",  # en image-to-video es el único valor permitido
              "negativePrompt": req.negative_prompt}  # no figura en la doc actual; el SDK lo manda
    return {"instances": [inst], "parameters": _drop_none(params)}


def _omni(model: str):
    def build(req: Request, img) -> dict:
        # task image_to_video: "the first image defines the starting frame, and the optional second image
        # defines the ending frame" (VideoConfig). Sin task, el modelo decide si la imagen es el primer
        # frame o una referencia. Las imágenes van antes del texto, como en los ejemplos de la doc.
        frames = [req.image] + ([req.last_image] if req.last_image else [])
        return {
            "model": model,
            "input": [*({"type": "image", "data": img(p), "mime_type": mime(p)} for p in frames),
                      {"type": "text", "text": req.prompt}],
            # duration: la referencia de la Gemini API lo tipa como string sin dar el formato; la doc de
            # Omni en Vertex dice "integers between 3 and 10, followed by 's'". Sin campo de audio: Omni
            # siempre genera audio. Sin negative_prompt: la doc dice que Omni no lo soporta.
            "response_format": {"type": "video", "aspect_ratio": req.aspect_ratio, "resolution": req.resolution,
                                "duration": f"{req.duration}s"},
            # seed figura en GenerationConfig de la Interactions API; la doc de Omni no dice si lo respeta.
            "generation_config": _drop_none({"video_config": {"task": "image_to_video"}, "seed": req.seed}),
            # background: se consulta por GET en vez de esperar con la conexión abierta. store queda en su
            # default (true, 7 días): con store=false la interacción dura 24 h, menos que la reanudación.
            "background": True,
        }
    return build


def _fal_docs(endpoint: str) -> str:
    return f"https://fal.ai/models/{endpoint}/api"


FAL_BLOCKED = ("fal no aclara si cobra lo que bloquea la moderación (pricing: \"you pay only for successful "
               "outputs\"; FAQ: un 422 puede cobrarse si ya usó GPU): se cuenta como cobrado")

MODELS: dict[str, ModelSpec] = {m.name: m for m in [
    ModelSpec(
        name="seedance-2.0", provider="fal", endpoint="bytedance/seedance-2.0/image-to-video",
        durations=tuple(range(4, 16)), rates={"720p": 0.3034, "1080p": 0.682},
        build=_seedance("2.0"), last_frame=True, bills_blocked=True,
        price_note="US$0,3034/s a 720p, US$0,682/s a 1080p (por tokens; la página de 2.0 fast dice 0,3024)",
        docs=_fal_docs("bytedance/seedance-2.0/image-to-video")),
    ModelSpec(
        name="seedance-2.5", provider="fal", endpoint="bytedance/seedance-2.5/image-to-video",
        durations=tuple(range(4, 31)), rates={"480p": 0.2205, "720p": 0.4730, "1080p": 1.164},
        build=_seedance("2.5"), last_frame=True, bills_blocked=True,
        price_note="~US$0,473/s a 720p (por tokens, mismo precio con o sin audio)",
        docs=_fal_docs("bytedance/seedance-2.5/image-to-video")),
    ModelSpec(
        name="kling-3.0-pro", provider="fal", endpoint="fal-ai/kling-video/v3/pro/image-to-video",
        durations=tuple(range(3, 16)), rates={"720p": 0.112, "1080p": 0.112},
        audio_rates={"720p": 0.168, "1080p": 0.168},
        build=_kling_v3, last_frame=True, bills_blocked=True,
        price_note="US$0,112/s sin audio, 0,168 con audio según la página del modelo; fal.ai/pricing dice "
                   "0,14/s. La resolución no se elige",
        docs=_fal_docs("fal-ai/kling-video/v3/pro/image-to-video")),
    ModelSpec(
        name="minimax-h3", provider="fal", endpoint="minimax/h3/image-to-video",
        durations=tuple(range(5, 16)), rates={"480p": 0.05, "720p": 0.06, "1080p": 0.13},
        build=_minimax_h3, last_frame=True, bills_blocked=True,
        price_note="US$0,06/s a 768P (lo que se pide por 720p), 0,13 a 2K. El audio no se puede apagar",
        docs=_fal_docs("minimax/h3/image-to-video")),
    ModelSpec(
        name="minimax-h3-max", provider="fal", endpoint="minimax/h3-max/image-to-video",
        refs_endpoint="minimax/h3-max/reference-to-video", max_refs=9,
        durations=tuple(range(1, 16)), rates={"480p": 0.0325, "720p": 0.052, "1080p": 0.104},
        ref_rates={"480p": 0.05, "720p": 0.08, "1080p": 0.16}, ref_extra=h3_max_ref_extra,
        build=_h3_max, last_frame=True, bills_blocked=True,
        price_note="image-to-video US$0,052/s a 768P (promoción hasta el 2026-10-31, después 0,08); con "
                   "referencias (reference-to-video) 0,08/s más US$0,02 cada 1.000 tokens de referencia arriba de "
                   "4.096 por pedido (1.024 por imagen cuadrada). El audio no se apaga ni cambia el precio",
        docs=_fal_docs("minimax/h3-max/reference-to-video")),
    ModelSpec(
        name="kling-o3-std", provider="fal", endpoint="fal-ai/kling-video/o3/standard/image-to-video",
        refs_endpoint="fal-ai/kling-video/o3/standard/reference-to-video", max_refs=3 * KLING_ELEMENT,
        durations=tuple(range(3, 16)), rates={"720p": 0.084}, audio_rates={"720p": 0.112},
        build=_kling_o3, last_frame=True, bills_blocked=True,
        price_note="US$0,084/s sin audio, 0,112 con audio, con o sin referencias. La resolución no se elige "
                   "(standard). Con primer frame acepta hasta 3 elements",
        docs=_fal_docs("fal-ai/kling-video/o3/standard/reference-to-video")),
    ModelSpec(
        name="wan-2.2", provider="fal", endpoint="fal-ai/wan/v2.2-a14b/image-to-video",
        durations=tuple(range(1, 11)), rates={"480p": 0.04, "580p": 0.06, "720p": 0.08},
        build=_wan_22, last_frame=True, bills_blocked=True,
        billed_seconds=lambda d: (WAN_FPS * d + 1) / WAN_FPS,  # "video seconds" a 16 fps
        price_note="US$0,08/s de video a 720p, contados a 16 fps; sin audio",
        docs=_fal_docs("fal-ai/wan/v2.2-a14b/image-to-video")),
    ModelSpec(
        name="veo-3.1-fast-fal", provider="fal", endpoint="fal-ai/veo3.1/fast/image-to-video",
        last_frame_endpoint="fal-ai/veo3.1/fast/first-last-frame-to-video",
        durations=(4, 6, 8), rates={"720p": 0.10, "1080p": 0.10, "4k": 0.30},
        audio_rates={"720p": 0.15, "1080p": 0.15, "4k": 0.35},
        build=_veo_fal, last_frame=True, bills_blocked=True,
        price_note="US$0,10/s sin audio, 0,15 con audio a 720p o 1080p. Sin personGeneration: fal no lo expone",
        docs=_fal_docs("fal-ai/veo3.1/fast/image-to-video")),
    ModelSpec(
        name="veo-3.1-fast-gemini", provider="gemini", endpoint="veo-3.1-fast-generate-preview",
        durations=(4, 6, 8), longest_only=("1080p", "4k"),
        rates={"720p": 0.10, "1080p": 0.12, "4k": 0.30},  # con audio: en la Gemini API va siempre
        build=_veo_gemini, last_frame=True, bills_blocked=False, sunset="2026-10-22",
        price_note="US$0,10/s a 720p, 0,12 a 1080p, con audio siempre (paid tier). Lo bloqueado no se cobra. "
                   "El preview se apaga el 2026-10-22: Google recomienda gemini-omni-1.1-flash",
        docs="https://ai.google.dev/gemini-api/docs/veo"),
    ModelSpec(
        name="gemini-omni-1.1-flash", provider="omni", endpoint="gemini-omni-1.1-flash",
        durations=tuple(range(3, 11)),  # "Output video 3s-10s (360p/720p/1080p/4K, 24 FPS)"
        rates={"720p": 5792 * 17.50 / 1e6},  # 5.792 tokens de video por segundo a US$17,50 el millón
        build=_omni("gemini-omni-1.1-flash"), last_frame=True, bills_blocked=True,
        price_note="US$17,50 por millón de tokens de video, a 5.792 tokens por segundo de 720p: ~US$0,1014/s, "
                   "con audio siempre (paid tier). Suma centavos de tokens de entrada (US$1,50/M) y de "
                   "razonamiento (US$9/M). La doc no da el precio de otras resoluciones ni dice si cobra lo "
                   "bloqueado (cobra por tokens de salida): se cuenta como cobrado",
        docs="https://ai.google.dev/gemini-api/docs/omni"),
]}
