"""bakeoff con los proveedores falsos: ningún test llama a una API real."""

import base64
import json

import numpy as np
import pytest
from PIL import Image

from spritepipe import bakeoff, imgio, videoapi

MAGENTA = (255, 0, 255)
FAL_KEY, GEMINI_KEY = "fal-test-key-123", "gemini-test-key-456"
VIDEO_HOST = "https://fal.media/files"
GEMINI_FILE = f"{videoapi.GEMINI_API}/files/abc:download?alt=media"


def _frame(t: int) -> np.ndarray:
    """Personaje (rectángulo con contorno) que respira sobre magenta, con período de 12 frames."""
    a = np.full((180, 320, 3), MAGENTA, np.uint8)
    bob = round(3 * np.sin(2 * np.pi * t / 12))
    a[60 + bob:150, 140:180] = (20, 20, 20)
    a[62 + bob:148, 142:178] = (200, 130, 70)
    a[90 + bob:98, 178:215] = (40, 40, 40)  # arma
    return a


@pytest.fixture(scope="session")
def clip_bytes(tmp_path_factory):
    path = tmp_path_factory.mktemp("clip") / "clip.mp4"
    imgio.encode_rgb_video((_frame(t) for t in range(48)), path, 24)
    return path.read_bytes()


@pytest.fixture
def char(tmp_path):
    """Un personaje con su pose y su prompt, como characters/comando."""
    Image.fromarray(_frame(0)).save(tmp_path / "pose.png")
    (tmp_path / "prompts").mkdir()
    (tmp_path / "prompts" / "idle.txt").write_text("El personaje respira. Cámara fija.\n", encoding="utf-8")
    return tmp_path


def _toml(root, models=("fake-fal", "fake-veo"), clips=2, extra=""):
    cfg = root / "bakeoff.toml"
    cfg.write_text(f"""
[bakeoff]
models = {json.dumps(list(models))}
clips_per_model = {clips}
duration = 5
max_usd = 30
{extra}

[[animation]]
name = "idle"
pose = "pose.png"
prompt = "prompts/idle.txt"
""", encoding="utf-8")
    return cfg


def _fal_build(req, img):
    return {"prompt": req.prompt, "image_url": img(req.image), "duration": str(req.duration)}


def _veo_build(req, img):
    return {"instances": [{"prompt": req.prompt, "image": {"inlineData": {"mimeType": "image/png", "data": img(req.image)}}}],
            "parameters": {"durationSeconds": req.duration, "personGeneration": "allow_adult"}}


@pytest.fixture(autouse=True)
def fake_models(monkeypatch):
    models = {
        "fake-fal": videoapi.ModelSpec("fake-fal", "fal", "fal-ai/fake/v1/image-to-video", (5, 10), {"720p": 0.10},
                                       _fal_build, False, False, "US$0,10/s", "doc"),
        "fake-veo": videoapi.ModelSpec("fake-veo", "gemini", "veo-fake", (4, 6, 8), {"720p": 0.15},
                                       _veo_build, True, False, "US$0,15/s", "doc"),
        # El build real de Omni, con lo bloqueado contado como cobrado (como el modelo de verdad)
        "fake-omni": videoapi.ModelSpec("fake-omni", "omni", "omni-fake", tuple(range(3, 11)), {"720p": 0.10},
                                        videoapi._omni("omni-fake"), True, True, "US$0,10/s", "doc"),
    }
    monkeypatch.setattr(videoapi, "MODELS", models)


class FakeHttp:
    """La cola de fal y las operaciones de la Gemini API, en memoria.

    block: conjunto de proveedores cuya respuesta es un bloqueo de moderación.
    submit_error: si está, el POST a la Interactions API lo levanta.
    pose: los bytes de la pose, para comparar lo que se manda a Omni en base64.
    """

    def __init__(self, clip_bytes, block=(), polls_before_done=1, submit_error=None, pose=None):
        self.clip_bytes, self.block, self.polls_before_done = clip_bytes, set(block), polls_before_done
        self.submit_error, self.pose = submit_error, pose
        self.calls, self.polls, self.n, self.uploads = [], {}, 0, {}

    def json(self, method, url, headers, body=None):
        self.calls.append((method, url, dict(headers), body))
        if url == videoapi.FAL_UPLOAD:
            assert headers["Authorization"] == f"Key {FAL_KEY}"
            assert json.loads(headers["X-Fal-Object-Lifecycle-Preference"]) == {"expiration_duration_seconds": 86400}
            assert body == {"file_name": "pose.png", "content_type": "image/png"}
            return {"upload_url": "https://upload.example/presigned", "file_url": "https://v3b.fal.media/files/b/x/pose.png"}
        if method == "POST" and url.startswith(videoapi.FAL_QUEUE):
            assert headers == {"Authorization": f"Key {FAL_KEY}"}
            assert body["image_url"] == "https://v3b.fal.media/files/b/x/pose.png"
            self.n += 1
            rid = f"r{self.n}"
            base = f"{videoapi.FAL_QUEUE}/fal-ai/fake/requests/{rid}"  # sólo el id de la app, sin el subpath
            return {"request_id": rid, "status_url": f"{base}/status", "response_url": base}
        if method == "POST" and url.endswith(":predictLongRunning"):
            assert headers == {"x-goog-api-key": GEMINI_KEY}
            self.n += 1
            return {"name": f"models/veo-fake/operations/op{self.n}"}
        if url.startswith(videoapi.FAL_QUEUE):
            rid = url.split("/requests/")[1].split("/")[0]
            if url.endswith("/status"):
                self.polls[rid] = self.polls.get(rid, 0) + 1
                done = self.polls[rid] > self.polls_before_done
                return {"status": "COMPLETED" if done else "IN_PROGRESS"}
            if "fal" in self.block:
                raise videoapi.HttpError(422, {"detail": [{
                    "loc": ["body", "image_url"], "type": "content_policy_violation",
                    "msg": "The content could not be processed because it contained material flagged by a content checker."}]},
                    url)
            return {"video": {"url": f"{VIDEO_HOST}/{rid}.mp4"}}
        if url.startswith(f"{videoapi.GEMINI_API}/models/veo-fake/operations/"):
            op = url.rsplit("/", 1)[1]
            self.polls[op] = self.polls.get(op, 0) + 1
            if self.polls[op] <= self.polls_before_done:
                return {"name": op, "done": False}
            if "gemini" in self.block:
                return {"name": op, "done": True, "response": {"@type": "x", "generateVideoResponse": {
                    "raiMediaFilteredCount": 1,
                    "raiMediaFilteredReasons": ["We encountered an issue with the input image. Support codes: 58061214"]}}}
            return {"name": op, "done": True, "response": {"generateVideoResponse": {
                "generatedSamples": [{"video": {"uri": GEMINI_FILE}}]}}}
        if url == videoapi.INTERACTIONS:
            assert method == "POST" and headers == {"x-goog-api-key": GEMINI_KEY, "Api-Revision": "2026-05-20"}
            assert body["model"] == "omni-fake" and body["background"] is True
            assert body["input"][0] == {"type": "image", "data": base64.b64encode(self.pose).decode(),
                                        "mime_type": "image/png"}
            assert body["generation_config"]["video_config"] == {"task": "image_to_video"}
            if self.submit_error:
                raise self.submit_error
            self.n += 1
            return {"id": f"v1_int{self.n}", "status": "in_progress", "object": "interaction"}
        if url.startswith(f"{videoapi.INTERACTIONS}/"):
            assert method == "GET" and headers["x-goog-api-key"] == GEMINI_KEY
            iid = url.rsplit("/", 1)[1]
            self.polls[iid] = self.polls.get(iid, 0) + 1
            if self.polls[iid] <= self.polls_before_done:
                return {"id": iid, "status": "in_progress", "object": "interaction"}
            if "omni" in self.block:
                return {"id": iid, "status": "failed", "object": "interaction", "errors": [
                    {"code": "safety", "message": "Safety violations (harmful content) blocked the request."}]}
            return {"id": iid, "status": "completed", "object": "interaction", "steps": [
                {"type": "user_input", "content": body_input(self.pose)},
                {"type": "thought", "summary": [{"type": "text", "text": "plan"}]},
                {"type": "model_output", "content": [
                    {"type": "video", "mime_type": "video/mp4", "data": base64.b64encode(self.clip_bytes).decode()}]}]}
        raise AssertionError(f"llamada inesperada: {method} {url}")

    def put(self, url, data, headers):
        assert url == "https://upload.example/presigned" and headers == {"Content-Type": "image/png"}
        self.calls.append(("PUT", url, dict(headers), None))
        self.uploads[url] = data

    def download(self, url, dest, headers=None):
        self.calls.append(("DOWNLOAD", url, dict(headers or {}), None))
        if url.startswith(VIDEO_HOST):
            assert not headers  # la key de fal no viaja a fal.media
        else:
            assert url == GEMINI_FILE and headers == {"x-goog-api-key": GEMINI_KEY}
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(self.clip_bytes)


def body_input(pose: bytes) -> list:
    return [{"type": "image", "data": base64.b64encode(pose).decode(), "mime_type": "image/png"},
            {"type": "text", "text": "El personaje respira. Cámara fija."}]


class NoHttp:
    def json(self, *a, **k):
        raise AssertionError("el dry-run no puede llamar a la red")

    put = download = json


def _run(cfg, http, env=None, **kw):
    env = {"FAL_KEY": FAL_KEY, "GEMINI_API_KEY": GEMINI_KEY} if env is None else env
    return bakeoff.run(cfg, env=env, http=http, sleep=lambda s: None, yes=kw.pop("yes", True), **kw)


def test_without_keys_it_is_a_dry_run(char, capsys):
    assert _run(_toml(char), NoHttp(), env={}) == 0
    out = capsys.readouterr().out
    assert "dry-run" in out and "FAL_KEY" in out
    assert "total estimado    2,80" in out  # 2 × 5 s × 0,10 + 2 × 6 s × 0,15
    assert "veo-fake:predictLongRunning" in out and '"personGeneration": "allow_adult"' in out
    assert "pose.png en base64, 1 KB" in out and "idle.txt, 34 caracteres" in out
    assert "<URL de pose.png subida al CDN de fal>" in out
    assert not (char / "clips").exists()


def test_dry_run_flag_wins_over_keys(char, capsys):
    assert _run(_toml(char), NoHttp(), dry_run=True) == 0
    assert "dry-run (--dry-run)" in capsys.readouterr().out


def test_run_downloads_each_clip_and_tables_the_qa(char, clip_bytes, capsys):
    http = FakeHttp(clip_bytes)
    assert _run(_toml(char), http) == 0
    out_dir = char / "clips" / "bakeoff"
    names = sorted(p.name for p in out_dir.glob("*.mp4"))
    assert names == ["fake-fal_idle_1.mp4", "fake-fal_idle_2.mp4", "fake-veo_idle_1.mp4", "fake-veo_idle_2.mp4"]
    ledger = json.loads((out_dir / "bakeoff.json").read_text())
    assert [a["status"] for a in ledger["attempts"]] == ["done"] * 4
    assert set(ledger["qa"]) == set(names)
    assert all(q["qa"] in ("ok", "warn", "fail") and q["pose_mad"] is not None for q in ledger["qa"].values())
    md = (out_dir / "bakeoff.md").read_text()
    assert md.count("| ok |") == 4 and "loop" in md
    assert "Gastado (estimado, a precio de lista): US$ 2,80" in md
    # Las keys no quedan en ningún archivo
    for p in out_dir.iterdir():
        if p.suffix != ".mp4":
            text = p.read_text()
            assert FAL_KEY not in text and GEMINI_KEY not in text
    out = capsys.readouterr().out
    assert FAL_KEY not in out and GEMINI_KEY not in out


def test_moderation_blocks_are_recorded_and_not_billed(char, clip_bytes, capsys):
    assert _run(_toml(char, clips=1), FakeHttp(clip_bytes, block={"fal", "gemini"})) == 0
    out_dir = char / "clips" / "bakeoff"
    assert not list(out_dir.glob("*.mp4"))
    ledger = json.loads((out_dir / "bakeoff.json").read_text())
    by_clip = {a["clip"]: a for a in ledger["attempts"]}
    assert by_clip["fake-fal_idle_1.mp4"]["status"] == "blocked"
    assert "content_policy_violation" in by_clip["fake-fal_idle_1.mp4"]["detail"]
    assert by_clip["fake-veo_idle_1.mp4"]["status"] == "blocked"
    assert "58061214" in by_clip["fake-veo_idle_1.mp4"]["detail"]
    md = (out_dir / "bakeoff.md").read_text()
    assert md.count("| bloqueado |") == 2 and "US$ 0,00" in md


def test_rerun_skips_downloaded_clips_and_resumes_pending_requests(char, clip_bytes):
    cfg = _toml(char, models=("fake-fal",), clips=2)
    _run(cfg, FakeHttp(clip_bytes))
    out_dir = char / "clips" / "bakeoff"
    (out_dir / "fake-fal_idle_2.mp4").unlink()
    ledger = json.loads((out_dir / "bakeoff.json").read_text())
    ledger["attempts"][1]["status"] = "submitted"  # como si el proceso se hubiera cortado esperando
    (out_dir / "bakeoff.json").write_text(json.dumps(ledger))

    http = FakeHttp(clip_bytes)
    assert _run(cfg, http, yes=False, ask=lambda q: pytest.fail("no hay nada nuevo que pagar")) == 0
    assert not [c for c in http.calls if c[0] == "POST"]  # nada se volvió a mandar
    assert http.calls[-1][0] == "DOWNLOAD" and (out_dir / "fake-fal_idle_2.mp4").exists()


def test_budget_cap_refuses_before_any_call(char, capsys):
    cfg = _toml(char)
    cfg.write_text(cfg.read_text().replace("max_usd = 30", "max_usd = 1"))
    assert _run(cfg, NoHttp()) == 1
    assert "pasa el tope max_usd" in capsys.readouterr().out


def test_asks_before_spending(char, clip_bytes, capsys):
    http = FakeHttp(clip_bytes)
    assert _run(_toml(char), http, yes=False, ask=lambda q: "n") == 1
    assert not http.calls
    assert "no se mandó nada" in capsys.readouterr().out


def test_missing_key_skips_only_that_provider(char, clip_bytes, capsys):
    http = FakeHttp(clip_bytes)
    assert _run(_toml(char, clips=1), http, env={"FAL_KEY": FAL_KEY}) == 0
    assert all(not c[1].startswith(videoapi.GEMINI_API) for c in http.calls)
    out = capsys.readouterr().out
    assert "sin GEMINI_API_KEY: salteo fake-veo" in out
    assert (char / "clips" / "bakeoff" / "fake-fal_idle_1.mp4").exists()


def test_models_flag_filters_the_config(char, clip_bytes):
    http = FakeHttp(clip_bytes)
    assert _run(_toml(char, clips=1), http, models=["fake-veo"]) == 0
    assert all(c[1].startswith(videoapi.GEMINI_API) for c in http.calls)


@pytest.mark.parametrize("extra, error", [
    ("modelz = []", "modelz"),
    ("", None),
])
def test_config_rejects_unknown_keys(char, extra, error):
    cfg = _toml(char, extra=extra)
    if error:
        with pytest.raises(ValueError, match=error):
            bakeoff.load(cfg)
    else:
        assert bakeoff.load(cfg).clips_per_model == 2


def test_config_rejects_unknown_models(char):
    with pytest.raises(ValueError, match="nope.*fake-fal"):
        bakeoff.load(_toml(char, models=("nope",)))


def test_last_frame_true_reuses_the_pose_only_where_supported(char):
    cfg = _toml(char)
    cfg.write_text(cfg.read_text() + "last_frame = true\n")
    c = bakeoff.load(cfg)
    reqs = {t.model.name: bakeoff.request(c, t) for t in bakeoff.plan(c)}
    assert reqs["fake-veo"].last_image == c.animations[0].pose
    assert reqs["fake-fal"].last_image is None


def _with_refs(char, monkeypatch, refs_last_frame=True):
    """fake-ref acepta dos referencias por otro endpoint; las refs van a la config del idle."""
    for name in ("vistas.png", "arma.png", "extra.png"):
        Image.fromarray(_frame(3)).save(char / name)
    spec = videoapi.ModelSpec("fake-ref", "fal", "fal-ai/fake/v1/image-to-video", (5, 10), {"720p": 0.10},
                              _fal_build, True, False, "US$0,10/s", "doc", max_refs=2,
                              refs_endpoint="fal-ai/fake/v1/reference-to-video", refs_last_frame=refs_last_frame)
    monkeypatch.setitem(videoapi.MODELS, "fake-ref", spec)
    cfg = _toml(char, models=("fake-fal", "fake-ref"))
    cfg.write_text(cfg.read_text() + 'last_frame = true\nrefs = ["vistas.png", "arma.png", "extra.png"]\n')
    return bakeoff.load(cfg)


def test_refs_go_only_to_models_that_accept_them(char, monkeypatch, capsys):
    c = _with_refs(char, monkeypatch)
    assert [r.name for r in c.animations[0].refs] == ["vistas.png", "arma.png", "extra.png"]
    reqs = {t.model.name: bakeoff.request(c, t) for t in bakeoff.plan(c)}
    assert [r.name for r in reqs["fake-ref"].refs] == ["vistas.png", "arma.png"]  # hasta max_refs
    assert reqs["fake-ref"].last_image == c.animations[0].pose
    assert reqs["fake-fal"].refs == ()
    assert videoapi.MODELS["fake-ref"].endpoint_for(reqs["fake-ref"]) == "fal-ai/fake/v1/reference-to-video"
    assert videoapi.MODELS["fake-fal"].endpoint_for(reqs["fake-fal"]) == "fal-ai/fake/v1/image-to-video"
    bakeoff.print_plan(c, bakeoff.plan(c), {}, {})
    out = capsys.readouterr().out
    assert "refs vistas.png, arma.png, extra.png" in out
    assert "no acepta referencias" in out and "acepta 2 referencias" in out


def test_refs_drop_the_last_frame_where_the_endpoint_cannot_take_both(char, monkeypatch):
    c = _with_refs(char, monkeypatch, refs_last_frame=False)
    req = next(bakeoff.request(c, t) for t in bakeoff.plan(c) if t.model.name == "fake-ref")
    assert len(req.refs) == 2 and req.last_image is None


def test_missing_ref_is_an_error(char):
    cfg = _toml(char)
    cfg.write_text(cfg.read_text() + 'refs = ["no_existe.png"]\n')
    with pytest.raises(FileNotFoundError, match="refs"):
        bakeoff.load(cfg)


def test_animation_models_and_prompts_pick_per_model(char):
    (char / "prompts" / "idle_veo.txt").write_text("Prompt para Veo.\n", encoding="utf-8")
    cfg = _toml(char)
    cfg.write_text(cfg.read_text() + """
[[animation]]
name = "idle_veo"
pose = "pose.png"
prompt = "prompts/idle.txt"
models = ["fake-veo"]
prompts = { fake-veo = "prompts/idle_veo.txt" }
""")
    c = bakeoff.load(cfg)
    tasks = bakeoff.plan(c)
    assert sorted({(t.model.name, t.anim.name) for t in tasks}) == [
        ("fake-fal", "idle"), ("fake-veo", "idle"), ("fake-veo", "idle_veo")]
    req = next(bakeoff.request(c, t) for t in tasks if t.anim.name == "idle_veo")
    assert req.prompt == "Prompt para Veo."
    bad = cfg.read_text().replace('models = ["fake-veo"]', 'models = ["fake-omni"]')
    cfg.write_text(bad)
    with pytest.raises(ValueError, match="fake-omni"):
        bakeoff.load(cfg)


def test_anims_flag_runs_only_those_animations(char, capsys):
    cfg = _toml(char)
    cfg.write_text(cfg.read_text() + '\n[[animation]]\nname = "otra"\npose = "pose.png"\nprompt = "prompts/idle.txt"\n')
    assert bakeoff.run(cfg, dry_run=True, anims=["otra"]) == 0
    out = capsys.readouterr().out
    assert "× 1 animaciones" in out and "  otra: pose" in out and "  idle: pose" not in out
    assert bakeoff.run(cfg, dry_run=True, anims=["nope"]) == 1


def test_pick_duration_rounds_up_to_an_allowed_value():
    spec = videoapi.MODELS["fake-veo"]
    assert [spec.pick_duration(d) for d in (3, 4, 5, 8, 12)] == [4, 4, 6, 8, 8]


def test_gemini_download_sends_the_key_only_to_google():
    sent = []

    class Rec:
        def download(self, url, dest, headers=None):
            sent.append((url, headers))

    g = videoapi.GeminiClient(GEMINI_KEY, Rec())
    g.download(GEMINI_FILE, None)
    g.download("https://storage.example.com/v.mp4", None)
    assert sent == [(GEMINI_FILE, {"x-goog-api-key": GEMINI_KEY}), ("https://storage.example.com/v.mp4", None)]


def test_fal_errors_that_are_not_moderation_are_errors():
    e = videoapi.HttpError(422, {"detail": [{"type": "greater_than_equal", "msg": "duration must be ≥ 5"}]}, "u")
    assert videoapi.fal_error(e).state == "error"


def _omni_http(char, clip_bytes, **kw):
    return FakeHttp(clip_bytes, pose=(char / "pose.png").read_bytes(), **kw)


def test_dry_run_shows_the_omni_request_without_keys(char, capsys):
    assert _run(_toml(char, models=("fake-omni",)), NoHttp(), env={}) == 0
    out = capsys.readouterr().out
    assert f"fake-omni  POST {videoapi.INTERACTIONS}" in out
    assert '"model": "omni-fake"' in out and '"background": true' in out and '"duration": "5s"' in out
    assert '"task": "image_to_video"' in out and "pose.png en base64" in out
    assert "(sin GEMINI_API_KEY)" in out and "no hay FAL_KEY ni GEMINI_API_KEY en el entorno" in out


def test_omni_run_polls_the_interaction_and_writes_the_inline_video(char, clip_bytes, capsys):
    http = _omni_http(char, clip_bytes)
    assert _run(_toml(char, models=("fake-omni",), clips=1), http) == 0
    out_dir = char / "clips" / "bakeoff"
    assert (out_dir / "fake-omni_idle_1.mp4").read_bytes() == clip_bytes
    assert not [c for c in http.calls if c[0] == "DOWNLOAD"]  # el video vino en el GET
    ledger = json.loads((out_dir / "bakeoff.json").read_text())
    rec = ledger["attempts"][0]
    assert rec["status"] == "done" and rec["provider"] == "omni" and rec["handle"] == {"interaction": "v1_int1"}
    assert ledger["qa"]["fake-omni_idle_1.mp4"]["pose_mad"] is not None
    assert all("key=" not in c[1] for c in http.calls)
    for p in out_dir.iterdir():
        if p.suffix != ".mp4":
            assert GEMINI_KEY not in p.read_text()
    assert GEMINI_KEY not in capsys.readouterr().out


def test_omni_block_is_recorded_and_counted_as_billed(char, clip_bytes):
    assert _run(_toml(char, models=("fake-omni",), clips=1), _omni_http(char, clip_bytes, block={"omni"})) == 0
    out_dir = char / "clips" / "bakeoff"
    rec = json.loads((out_dir / "bakeoff.json").read_text())["attempts"][0]
    assert rec["status"] == "blocked" and rec["detail"].startswith("safety: ")
    md = (out_dir / "bakeoff.md").read_text()
    assert "| bloqueado |" in md and "US$ 0,50" in md  # la doc no dice si cobra lo bloqueado


def test_omni_block_at_submit_is_recorded(char, clip_bytes):
    err = videoapi.HttpError(400, {"error": {"code": "prohibited_content",
                                             "message": "Prohibited content guidelines blocked the request."}},
                             videoapi.INTERACTIONS)
    assert _run(_toml(char, models=("fake-omni",), clips=1), _omni_http(char, clip_bytes, submit_error=err)) == 0
    rec = json.loads((char / "clips" / "bakeoff" / "bakeoff.json").read_text())["attempts"][0]
    assert rec["status"] == "blocked" and rec["handle"] is None and "prohibited_content" in rec["detail"]


def test_gemini_key_covers_veo_and_omni_in_one_warning(char, clip_bytes, capsys):
    http = FakeHttp(clip_bytes)
    assert _run(_toml(char, models=("fake-fal", "fake-veo", "fake-omni"), clips=1), http, env={"FAL_KEY": FAL_KEY}) == 0
    out = capsys.readouterr().out
    assert out.count("sin GEMINI_API_KEY: salteo") == 1 and "salteo fake-omni, fake-veo" in out
    assert all(not c[1].startswith(videoapi.GEMINI_API) for c in http.calls)
