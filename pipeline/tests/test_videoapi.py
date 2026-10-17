"""Los pedidos que arma cada modelo del registro, contra los campos de la doc de cada proveedor."""

import base64
import json
from pathlib import Path

import pytest

from spritepipe import videoapi

POSE, LAST = Path("poses/pose.png"), Path("poses/last.png")


def _req(**kw):
    base = dict(prompt="p", image=POSE, last_image=None, duration=5, aspect_ratio="16:9", resolution="720p",
                audio=False, negative_prompt=None, seed=None)
    return videoapi.Request(**{**base, **kw})


def _build(name, **kw):
    spec = videoapi.MODELS[name]
    req = _req(**kw)
    req.duration = spec.pick_duration(req.duration, req.resolution)
    return spec.build(req, lambda p: f"ref:{p.name}"), spec.endpoint_for(req)


@pytest.mark.parametrize("name", list(videoapi.MODELS))
def test_every_model_builds_a_clean_json_payload(name):
    spec = videoapi.MODELS[name]
    body, _ = _build(name)
    json.dumps(body)
    assert "ref:pose.png" in json.dumps(body) and "null" not in json.dumps(body)
    assert spec.pick_duration(5) in spec.durations
    assert spec.price(spec.pick_duration(5), False, "720p") > 0
    assert spec.docs.startswith("https://")


def test_seedance_fields():
    body, ep = _build("seedance-2.0", last_image=LAST)
    assert ep == "bytedance/seedance-2.0/image-to-video"
    assert body == {"prompt": "p", "image_url": "ref:pose.png", "end_image_url": "ref:last.png", "duration": "5",
                    "resolution": "720p", "aspect_ratio": "16:9", "generate_audio": False}
    body, _ = _build("seedance-2.5")
    assert "aspect_ratio" not in body  # en 2.5 image-to-video es siempre auto


def test_kling_uses_start_image_and_keeps_its_default_negative_prompt():
    body, _ = _build("kling-3.0-pro")
    assert body == {"prompt": "p", "start_image_url": "ref:pose.png", "duration": "5", "generate_audio": False}
    body, _ = _build("kling-3.0-pro", negative_prompt="zoom")
    assert body["negative_prompt"] == "zoom"


def test_minimax_h3_asks_768p_for_720p_and_an_integer_duration():
    body, _ = _build("minimax-h3", seed=7)
    assert body == {"prompt": "p", "image_url": "ref:pose.png", "duration": 5, "resolution": "768P", "seed": 7}


def test_wan_has_no_duration_field_and_bills_video_seconds_at_16_fps():
    body, _ = _build("wan-2.2")
    assert "duration" not in body and body["num_frames"] == 81 and body["frames_per_second"] == 16
    assert videoapi.MODELS["wan-2.2"].price(5, False, "720p") == pytest.approx(81 / 16 * 0.08)


def test_veo_on_fal_switches_endpoint_for_a_last_frame():
    body, ep = _build("veo-3.1-fast-fal")
    assert ep == "fal-ai/veo3.1/fast/image-to-video" and body["image_url"] == "ref:pose.png"
    assert body["duration"] == "6s" and body["generate_audio"] is False
    body, ep = _build("veo-3.1-fast-fal", last_image=LAST)
    assert ep == "fal-ai/veo3.1/fast/first-last-frame-to-video"
    assert body["first_frame_url"] == "ref:pose.png" and body["last_frame_url"] == "ref:last.png"
    assert "image_url" not in body


def test_veo_on_gemini_allows_adults_and_drops_the_seed():
    body, ep = _build("veo-3.1-fast-gemini", seed=3, last_image=LAST)
    assert ep == "veo-3.1-fast-generate-preview"
    inst = body["instances"][0]
    assert inst["image"] == {"inlineData": {"mimeType": "image/png", "data": "ref:pose.png"}}
    assert inst["lastFrame"]["inlineData"]["data"] == "ref:last.png"
    assert body["parameters"] == {"aspectRatio": "16:9", "resolution": "720p", "durationSeconds": 6,
                                  "personGeneration": "allow_adult"}


def test_veo_on_gemini_1080p_only_comes_in_8_seconds():
    body, _ = _build("veo-3.1-fast-gemini", resolution="1080p")
    assert body["parameters"]["durationSeconds"] == 8


def test_omni_sends_the_pose_as_first_frame_through_the_interactions_api():
    body, ep = _build("gemini-omni-1.1-flash", seed=3, negative_prompt="zoom")
    assert ep == "gemini-omni-1.1-flash"
    assert body == {
        "model": "gemini-omni-1.1-flash",
        "input": [{"type": "image", "data": "ref:pose.png", "mime_type": "image/png"}, {"type": "text", "text": "p"}],
        "response_format": {"type": "video", "aspect_ratio": "16:9", "resolution": "720p", "duration": "5s"},
        "generation_config": {"video_config": {"task": "image_to_video"}, "seed": 3},
        "background": True,
    }  # sin negative_prompt: Omni no lo soporta


def test_omni_last_frame_is_the_second_image():
    body, _ = _build("gemini-omni-1.1-flash", last_image=LAST, duration=12)
    assert [c.get("data") for c in body["input"]] == ["ref:pose.png", "ref:last.png", None]
    assert body["response_format"]["duration"] == "10s"  # 3 a 10 s
    assert body["generation_config"] == {"video_config": {"task": "image_to_video"}}


def test_omni_price_is_5792_video_tokens_per_second_at_720p():
    spec = videoapi.MODELS["gemini-omni-1.1-flash"]
    assert spec.price(5, False, "720p") == spec.price(5, True, "720p") == pytest.approx(5 * 5792 * 17.50 / 1e6, abs=1e-4)
    with pytest.raises(ValueError):
        spec.price(5, False, "1080p")  # sin precio documentado


def test_unsupported_resolution_is_an_error():
    with pytest.raises(ValueError, match="kling-3.0-pro no acepta 480p"):
        videoapi.MODELS["kling-3.0-pro"].price(5, False, "480p")


def test_audio_changes_the_price_only_where_documented():
    kling, h3 = videoapi.MODELS["kling-3.0-pro"], videoapi.MODELS["minimax-h3"]
    assert kling.price(5, True, "720p") == pytest.approx(5 * 0.168)
    assert h3.price(5, True, "720p") == h3.price(5, False, "720p")


def test_fal_moderation_by_the_model_provider_is_a_block():
    e = videoapi.HttpError(422, {"detail": [{"loc": ["body", "prompt"], "msg": "Rejected by the provider",
                                             "type": "content_policy_violation", "categories": ["model_moderated"]}]}, "u")
    p = videoapi.fal_error(e)
    assert p.state == "blocked" and "model_moderated" in p.detail


class Script:
    """Devuelve respuestas fijas por URL."""

    def __init__(self, routes):
        self.routes = routes

    def json(self, method, url, headers, body=None):
        r = self.routes[url]
        if isinstance(r, Exception):
            raise r
        return r


def test_fal_failed_request_completes_with_error_type():
    handle = {"status_url": "s", "response_url": "r"}
    fal = videoapi.FalClient("k", Script({
        "s": {"status": "COMPLETED", "error": "flagged", "error_type": "content_policy_violation"}, "r": {}}))
    assert fal.poll(handle).state == "blocked"


def test_gemini_operation_error_with_support_codes_is_a_block():
    g = videoapi.GeminiClient("k", Script({f"{videoapi.GEMINI_API}/op": {"done": True, "error": {
        "code": 3, "message": "Your request was blocked. Support codes: 61493863"}}}))
    p = g.poll({"operation": "op"})
    assert p.state == "blocked" and "61493863" in p.detail


class OmniHttp:
    """La Interactions API en memoria: guarda los pedidos y devuelve las interacciones por id."""

    def __init__(self, interactions):
        self.interactions, self.calls, self.downloads = interactions, [], []

    def json(self, method, url, headers, body=None):
        self.calls.append((method, url, dict(headers), body))
        if method == "POST":
            return {"id": "v1_abc", "status": "in_progress", "object": "interaction"}
        r = self.interactions[url.rsplit("/", 1)[1]]
        if isinstance(r, Exception):
            raise r
        return r

    def download(self, url, dest, headers=None):
        self.downloads.append((url, headers))


def test_omni_client_submits_with_the_key_in_a_header_only():
    http = OmniHttp({})
    omni = videoapi.OmniClient("gk", http)
    body, _ = _build("gemini-omni-1.1-flash")
    assert omni.submit("gemini-omni-1.1-flash", body) == {"interaction": "v1_abc"}
    method, url, headers, sent = http.calls[0]
    assert (method, url) == ("POST", "https://generativelanguage.googleapis.com/v1beta/interactions")
    assert headers == {"x-goog-api-key": "gk", "Api-Revision": "2026-05-20"} and "key=" not in url
    assert sent == body and sent["background"] is True


def test_omni_poll_runs_until_completed_and_writes_the_inline_video(tmp_path):
    video = b"\x00\x00\x00 ftypisom-bytes"
    http = OmniHttp({
        "q": {"id": "q", "status": "queued"},
        "r": {"id": "r", "status": "in_progress"},
        "ok": {"id": "ok", "status": "completed", "steps": [
            {"type": "user_input", "content": [{"type": "image", "data": "cG9zZQ==", "mime_type": "image/png"},
                                               {"type": "text", "text": "p"}]},
            {"type": "thought", "summary": [{"type": "text", "text": "pensando"}]},
            {"type": "model_output", "content": [
                {"type": "video", "mime_type": "video/mp4", "data": base64.b64encode(video).decode()}]}]},
    })
    omni = videoapi.OmniClient("gk", http)
    assert omni.poll({"interaction": "q"}).state == "running"
    assert omni.poll({"interaction": "r"}).state == "running"
    assert http.calls[-1][:2] == ("GET", f"{videoapi.INTERACTIONS}/r")
    p = omni.poll({"interaction": "ok"})
    assert p.state == "done" and p.video_url.startswith("data:video/mp4;base64,")
    omni.download(p.video_url, tmp_path / "out" / "clip.mp4")
    assert (tmp_path / "out" / "clip.mp4").read_bytes() == video
    assert not list((tmp_path / "out").glob("*.part")) and not http.downloads


def test_omni_uri_delivery_downloads_with_the_key_only_from_google():
    uri = "https://generativelanguage.googleapis.com/v1beta/files/abc:download?alt=media"
    http = OmniHttp({"u": {"id": "u", "status": "completed", "steps": [
        {"type": "model_output", "content": [{"type": "video", "mime_type": "video/mp4", "uri": uri}]}]}})
    omni = videoapi.OmniClient("gk", http)
    p = omni.poll({"interaction": "u"})
    assert p.state == "done" and p.video_url == uri
    omni.download(uri, Path("x.mp4"))
    omni.download("https://storage.example.com/x.mp4", Path("y.mp4"))
    assert http.downloads == [(uri, {"x-goog-api-key": "gk"}), ("https://storage.example.com/x.mp4", None)]


@pytest.mark.parametrize("errors, state", [
    ([{"code": "safety", "message": "Safety violations blocked the request."}], "blocked"),
    ([{"code": "https://example.googleapis.com/errors/prohibited_content", "message": "no"}], "blocked"),
    ([{"code": "content_blocked", "message": ""}], "blocked"),
    ([{"code": "language", "message": "An unsupported language blocked the request."}], "error"),
    ([{"code": "api_error", "message": "boom"}], "error"),
])
def test_omni_failed_interaction_is_a_block_only_with_a_blocked_code(errors, state):
    omni = videoapi.OmniClient("gk", OmniHttp({"f": {"id": "f", "status": "failed", "errors": errors}}))
    p = omni.poll({"interaction": "f"})
    assert p.state == state and errors[0]["code"].rsplit("/", 1)[-1] in p.detail


def test_omni_completed_without_video_is_an_error_with_the_model_text():
    omni = videoapi.OmniClient("gk", OmniHttp({"t": {"id": "t", "status": "completed", "steps": [
        {"type": "user_input", "content": [{"type": "image", "data": "A" * 5000, "mime_type": "image/png"}]},
        {"type": "model_output", "content": [{"type": "text", "text": "No puedo hacer ese video."}]}]}}))
    p = omni.poll({"interaction": "t"})
    assert p.state == "error" and "No puedo hacer ese video." in p.detail and "AAAA" not in p.detail


def test_omni_http_errors_use_the_interactions_error_codes():
    blocked = videoapi.omni_error(videoapi.HttpError(400, {"error": {
        "code": "prohibited_content", "message": "Prohibited content guidelines blocked the request."}}, "u"))
    assert blocked.state == "blocked" and blocked.detail.startswith("HTTP 400 prohibited_content")
    bad = videoapi.omni_error(videoapi.HttpError(400, {"error": {"code": "invalid_request", "message": "duration"}}, "u"))
    assert bad.state == "error" and "invalid_request" in bad.detail


@pytest.fixture
def server():
    """Servidor HTTP local: el transporte real (urllib) sin salir de la máquina."""
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    seen = []

    class H(BaseHTTPRequestHandler):
        def _reply(self, code, body, ctype="application/json"):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            data = self.rfile.read(int(self.headers["Content-Length"]))
            seen.append(("POST", self.path, self.headers.get("Authorization"), json.loads(data)))
            if self.path == "/blocked":
                self._reply(422, json.dumps({"detail": [{"type": "content_policy_violation", "msg": "no"}]}).encode())
            else:
                self._reply(200, b'{"ok": true}')

        def do_PUT(self):
            seen.append(("PUT", self.path, self.headers.get("Content-Type"),
                         self.rfile.read(int(self.headers["Content-Length"]))))
            self._reply(200, b"")

        def do_GET(self):
            self._reply(200, b"video-bytes", "video/mp4")

        def log_message(self, *a):
            pass

    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_port}", seen
    srv.shutdown()


def test_http_transport_round_trips_json_bytes_and_errors(server, tmp_path):
    base, seen = server
    http = videoapi.Http(timeout=5)
    assert http.json("POST", f"{base}/q", {"Authorization": "Key k"}, {"a": 1}) == {"ok": True}
    http.put(f"{base}/up", b"\x89PNG", {"Content-Type": "image/png"})
    http.download(f"{base}/v.mp4", tmp_path / "out" / "v.mp4")
    assert (tmp_path / "out" / "v.mp4").read_bytes() == b"video-bytes"
    assert not list((tmp_path / "out").glob("*.part"))
    assert seen == [("POST", "/q", "Key k", {"a": 1}), ("PUT", "/up", "image/png", b"\x89PNG")]
    with pytest.raises(videoapi.HttpError) as e:
        http.json("POST", f"{base}/blocked", {}, {})
    assert e.value.status == 422 and videoapi.fal_error(e.value).state == "blocked"


def _ref_req(refs=(), last=True):
    from pathlib import Path
    return videoapi.Request(prompt="idle", image=Path("pose.png"), last_image=Path("pose.png") if last else None,
                            duration=5, aspect_ratio="16:9", resolution="720p", audio=False, negative_prompt=None,
                            seed=3, refs=tuple(Path(r) for r in refs))


def test_h3_max_sends_refs_to_reference_to_video_with_first_and_last_frame():
    spec = videoapi.MODELS["minimax-h3-max"]
    name = lambda p: p.name  # noqa: E731
    plain, withrefs = _ref_req(), _ref_req(["a.png", "b.png"])
    assert spec.endpoint_for(plain) == "minimax/h3-max/image-to-video"
    assert "reference_image_urls" not in spec.build(plain, name)
    body = spec.build(withrefs, name)
    assert spec.endpoint_for(withrefs) == "minimax/h3-max/reference-to-video"
    assert body["image_url"] == body["end_image_url"] == "pose.png"
    assert body["reference_image_urls"] == ["a.png", "b.png"]
    assert body["resolution"] == "768P" and body["prompt_expansion_mode"] == "disabled"
    # 0,052/s sin referencias; 0,08/s con, más los tokens de lo que pasa de 4 imágenes cuadradas
    assert spec.price(5, False, "720p") == 0.26
    assert spec.price(5, False, "720p", refs=4) == 0.4
    assert spec.price(5, False, "720p", refs=6) == round(0.4 + 2048 * 0.02 / 1000, 4)


def test_kling_o3_groups_refs_into_elements():
    spec = videoapi.MODELS["kling-o3-std"]
    name = lambda p: p.name  # noqa: E731
    plain = spec.build(_ref_req(), name)
    assert plain["image_url"] == "pose.png" and "elements" not in plain and plain["generate_audio"] is False
    req = _ref_req(["f.png", "q.png", "e.png", "x.png", "arma.png", "arma2.png"])
    body = spec.build(req, name)
    assert spec.endpoint_for(req) == "fal-ai/kling-video/o3/standard/reference-to-video"
    assert body["start_image_url"] == body["end_image_url"] == "pose.png"
    assert body["elements"] == [
        {"frontal_image_url": "f.png", "reference_image_urls": ["q.png", "e.png", "x.png"]},
        {"frontal_image_url": "arma.png", "reference_image_urls": ["arma2.png"]}]
    with pytest.raises(ValueError, match="element"):
        spec.build(_ref_req(["f.png", "q.png", "solo.png"][:1] + ["q.png", "e.png", "x.png", "suelta.png"]), name)
    assert spec.price(5, False, "720p", refs=6) == spec.price(5, False, "720p") == 0.42
