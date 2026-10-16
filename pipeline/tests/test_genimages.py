"""gen-images con los proveedores falsos: ningún test llama a una API real."""

import base64
import io
import json

import cv2
import numpy as np
import pytest
from PIL import Image

from spritepipe import genimages, imageapi, videoapi

OPENAI_KEY, FAL_KEY = "sk-test-openai-123", "fal-test-key-456"
IMAGE_HOST = "https://v3b.fal.media/files/out"
REF_URL = "https://v3b.fal.media/files/b/x/ranger.png"


def _png(img: np.ndarray) -> bytes:
    buf = io.BytesIO()
    Image.fromarray(img).save(buf, format="PNG")
    return buf.getvalue()


def _skyline(h=200, w=600, bg=None):
    """Edificios con contorno abajo; arriba, verde (fal) o transparente (OpenAI con alfa)."""
    rng = np.random.default_rng(3)
    img = np.zeros((h, w, 4), np.uint8)
    if bg is not None:
        img[:] = (*bg, 255)
    x = 0
    while x < w:
        bw, bh = int(rng.integers(30, 80)), int(rng.integers(40, 150))
        cv2.rectangle(img, (x, h - bh), (x + bw, h), (60, 40, 90, 255), -1)
        cv2.rectangle(img, (x, h - bh), (x + bw, h), (13, 15, 24, 255), 3)
        x += bw + int(rng.integers(6, 30))
    return img if bg is None else img[..., :3].copy()


@pytest.fixture
def setdir(tmp_path):
    """Un set como backgrounds/ranger_base: config y una referencia RGBA."""
    ref = np.zeros((120, 80, 4), np.uint8)
    ref[20:100, 20:60] = (230, 40, 40, 255)
    Image.fromarray(ref).save(tmp_path / "ranger.png")
    return tmp_path


def _toml(root, models=("fake-fal", "gpt-image-2.5-sunburst"), extra="", assets=None):
    assets = assets if assets is not None else """
[[asset]]
name = "far"
style = ["game"]
prompt = "A distant city skyline."
refs = ["ranger.png"]
aspect = "3:1"
alpha = "layer"
tile = "x"
"""
    cfg = root / "gen.toml"
    cfg.write_text(f"""
[gen]
models = {json.dumps(list(models))}
max_usd = 5
quality = "medium"
resolution = "1K"
seed = 3
{extra}

[styles]
game = "Thick black outlines, flat colors."
{assets}
""", encoding="utf-8")
    return cfg


def _fal_build(req, img, size):
    return {"prompt": req.prompt, "image_urls": [img(p) for p in req.refs], "image_size": size, "seed": req.seed}


@pytest.fixture(autouse=True)
def fake_models(monkeypatch):
    models = dict(imageapi.MODELS)
    models["fake-fal"] = imageapi.ImageModelSpec(
        name="fake-fal", provider="fal", endpoint="fal-ai/fake/text-to-image", edit_endpoint="fal-ai/fake/edit",
        transparent=False, max_refs=4, size=lambda req: ({"width": 900, "height": 300}, "900×300"),
        build=_fal_build, price=lambda req: 0.04, price_note="US$0,04 por imagen", docs="doc", bills_blocked=True)
    monkeypatch.setattr(imageapi, "MODELS", models)


class FakeHttp:
    """La Image API de OpenAI y la cola de fal, en memoria. block: proveedores que responden moderación."""

    def __init__(self, block=(), polls_before_done=1, openai_status=None):
        self.block, self.polls_before_done, self.openai_status = set(block), polls_before_done, openai_status
        self.calls, self.polls, self.n = [], {}, 0

    def json(self, method, url, headers, body=None):
        self.calls.append((method, url, dict(headers), body))
        if url.startswith(imageapi.OPENAI_API):
            assert method == "POST" and headers == {"Authorization": f"Bearer {OPENAI_KEY}"}
            if self.openai_status:
                status, err = self.openai_status
                raise videoapi.HttpError(status, {"error": err}, url)
            if "openai" in self.block:
                raise videoapi.HttpError(400, {"error": {
                    "type": "image_generation_user_error", "code": "moderation_blocked", "message": "blocked",
                    "moderation_details": {"moderation_stage": "input", "categories": ["violence"]}}}, url)
            png = _png(_skyline())  # con alfa nativo
            return {"created": 1, "data": [{"b64_json": base64.b64encode(png).decode()}], "background": "transparent",
                    "output_format": "png", "size": body["size"], "quality": body["quality"],
                    "usage": {"input_tokens": 7000, "input_tokens_details": {"image_tokens": 6800, "text_tokens": 200},
                              "output_tokens": 300, "total_tokens": 7300}}
        if url == videoapi.FAL_UPLOAD:
            assert headers["Authorization"] == f"Key {FAL_KEY}"
            return {"upload_url": "https://upload.example/presigned", "file_url": REF_URL}
        if method == "POST" and url.startswith(videoapi.FAL_QUEUE):
            assert headers == {"Authorization": f"Key {FAL_KEY}"}
            assert body["image_urls"] == [REF_URL]
            self.n += 1
            base = f"{videoapi.FAL_QUEUE}/fal-ai/fake/requests/r{self.n}"
            return {"request_id": f"r{self.n}", "status_url": f"{base}/status", "response_url": base}
        if url.startswith(videoapi.FAL_QUEUE):
            rid = url.split("/requests/")[1].split("/")[0]
            if url.endswith("/status"):
                self.polls[rid] = self.polls.get(rid, 0) + 1
                return {"status": "COMPLETED" if self.polls[rid] > self.polls_before_done else "IN_PROGRESS"}
            if "fal" in self.block:
                raise videoapi.HttpError(422, {"detail": [{"type": "content_policy_violation", "msg": "flagged"}]}, url)
            return {"images": [{"url": f"{IMAGE_HOST}/{rid}.png", "width": 600, "height": 200,
                                "content_type": "image/png"}], "seed": 3}
        raise AssertionError(f"llamada inesperada: {method} {url}")

    def put(self, url, data, headers):
        self.calls.append(("PUT", url, dict(headers), None))

    def download(self, url, dest, headers=None):
        self.calls.append(("DOWNLOAD", url, dict(headers or {}), None))
        assert url.startswith(IMAGE_HOST) and not headers  # la key de fal no viaja a fal.media
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(_png(_skyline(bg=(20, 240, 30))))  # sobre verde, sin alfa


class NoHttp:
    def json(self, *a, **k):
        raise AssertionError("no puede llamar a la red")

    put = download = json


def _run(cfg, http, env=None, **kw):
    env = {"OPENAI_API_KEY": OPENAI_KEY, "FAL_KEY": FAL_KEY} if env is None else env
    return genimages.run(cfg, env=env, http=http, sleep=lambda s: None, yes=kw.pop("yes", True), poll_s=0, **kw)


def _all_text(root):
    return "".join(p.read_text(encoding="utf-8", errors="ignore") for p in root.rglob("*")
                   if p.is_file() and p.suffix in (".json", ".md", ".html", ".toml"))


def test_without_keys_it_is_a_dry_run_that_writes_nothing(setdir, capsys):
    cfg = _toml(setdir)
    before = set(setdir.rglob("*"))
    assert _run(cfg, NoHttp(), env={}) == 0
    out = capsys.readouterr().out
    assert "dry-run" in out and "OPENAI_API_KEY" in out and "FAL_KEY" in out
    assert "prompt de far (con alfa nativo)" in out and "prompt de far (sobre #00FF00)" in out
    assert "pure green" in out and "Transparent background" in out
    assert "POST https://api.openai.com/v1/images/edits" in out
    assert "POST https://queue.fal.run/fal-ai/fake/edit" in out
    assert "<URL de" in out and "aplanadas sobre #FFFFFF" in out
    assert set(setdir.rglob("*")) == before


def test_dry_run_flag_with_keys_does_not_call(setdir, capsys):
    assert _run(_toml(setdir), NoHttp(), dry_run=True) == 0
    assert "dry-run (--dry-run)" in capsys.readouterr().out


def test_generates_with_both_providers_posts_and_writes_provenance(setdir, capsys):
    http = FakeHttp()
    assert _run(_toml(setdir), http) == 0
    raw, post = setdir / "raw" / "far", setdir / "post" / "far"
    assert {p.name for p in raw.iterdir()} == {"fake-fal_1.png", "fake-fal_1.json", "gpt-image-2.5-sunburst_1.png",
                                               "gpt-image-2.5-sunburst_1.json"}
    for name in ("fake-fal_1.png", "gpt-image-2.5-sunburst_1.png"):
        img = np.array(Image.open(post / name))
        assert img.shape[2] == 4 and (img[0, :, 3] == 0).all()  # arriba, aire

    oa = next(c for c in http.calls if c[1].startswith(imageapi.OPENAI_API))
    assert oa[1] == "https://api.openai.com/v1/images/edits"
    body = oa[3]
    assert body["model"] == "gpt-image-2.5-sunburst" and body["background"] == "transparent"
    assert body["size"] == "1776x592" and body["quality"] == "medium" and body["output_format"] == "png"
    assert body["images"][0]["image_url"].startswith("data:image/png;base64,")
    flat = Image.open(io.BytesIO(base64.b64decode(body["images"][0]["image_url"].split(",", 1)[1])))
    assert flat.mode == "RGB" and flat.getpixel((0, 0)) == (255, 255, 255)  # aplanada sobre blanco
    assert "seed" not in body  # la Image API no tiene seed

    fal = next(c for c in http.calls if c[0] == "POST" and c[1].startswith(videoapi.FAL_QUEUE))
    assert fal[1].endswith("/fal-ai/fake/edit") and fal[3]["seed"] == 3
    assert "pure green" in fal[3]["prompt"] and "Transparent background" not in fal[3]["prompt"]

    meta = json.loads((raw / "fake-fal_1.json").read_text())
    assert meta["model"] == "fake-fal" and meta["background"] == "key" and meta["usd_estimate"] == 0.04
    assert meta["prompt"].startswith("Thick black outlines") and meta["request_id"] == "r1"
    assert meta["refs_source"][0]["file"].endswith("ranger.png") and len(meta["refs"][0]["sha256"]) == 64
    assert meta["post"]["key"]["key_color"] == "#14F01E" and meta["post"]["alpha"]["verdict"] == "ok"
    assert meta["post"]["seam"]["x"]["after"]["verdict"] == "ok"
    meta = json.loads((raw / "gpt-image-2.5-sunburst_1.json").read_text())
    assert meta["background"] == "native" and "key" not in meta["post"]
    assert meta["usage"]["input_tokens_details"]["image_tokens"] == 6800

    out = capsys.readouterr().out
    assert "✓ far/fake-fal_1" in out and "costura x" in out
    assert (setdir / "compare.html").exists() and (setdir / "compare.md").exists()
    html = (setdir / "compare.html").read_text()
    assert 'src="post/far/fake-fal_1.png"' in html
    text = _all_text(setdir)
    assert OPENAI_KEY not in text and FAL_KEY not in text


def test_moderation_is_blocked_not_error(setdir, capsys):
    assert _run(_toml(setdir), FakeHttp(block={"openai", "fal"})) == 0
    out = capsys.readouterr().out
    assert "bloqueado por el proveedor — moderation_blocked (input: violence)" in out
    assert "bloqueado por el proveedor — content_policy_violation" in out
    md = (setdir / "compare.md").read_text()
    assert md.count("| bloqueado |") == 2


def test_openai_org_not_verified_says_so(setdir, capsys):
    http = FakeHttp(openai_status=(403, {"message": "Your organization must be verified to use the model", "code": None}))
    assert _run(_toml(setdir, models=("gpt-image-2.5-sunburst",)), http) == 0
    assert "la organización tiene que estar verificada" in capsys.readouterr().out


def test_openai_rate_limit_is_retried(setdir):
    class Flaky(FakeHttp):
        def json(self, method, url, headers, body=None):
            if url.startswith(imageapi.OPENAI_API) and not getattr(self, "failed", False):
                self.failed = True
                raise videoapi.HttpError(429, {"error": {"code": "rate_limit_exceeded", "message": "slow down"}}, url)
            return super().json(method, url, headers, body)

    http = Flaky()
    assert _run(_toml(setdir, models=("gpt-image-2.5-sunburst",)), http) == 0
    assert (setdir / "raw" / "far" / "gpt-image-2.5-sunburst_1.png").exists()


def test_over_max_usd_sends_nothing(setdir, capsys):
    cfg = _toml(setdir, extra="images_per_asset = 200")
    assert _run(cfg, NoHttp()) == 1
    assert "pasa el tope max_usd" in capsys.readouterr().out


def test_asks_before_spending(setdir, capsys):
    assert genimages.run(_toml(setdir), env={"FAL_KEY": FAL_KEY}, http=NoHttp(), ask=lambda q: "n") == 1
    out = capsys.readouterr().out
    assert "no se mandó nada" in out and "sin OPENAI_API_KEY: salteo gpt-image-2.5-sunburst" in out


def test_only_the_chosen_models_and_assets(setdir):
    cfg = _toml(setdir, assets="""
[[asset]]
name = "far"
prompt = "A distant city skyline."
aspect = "3:1"
alpha = "layer"

[[asset]]
name = "props"
prompt = "A crate."
alpha = "cutout"
""")
    http = FakeHttp()

    class NoRefs(FakeHttp):
        def json(self, method, url, headers, body=None):
            if method == "POST" and url.startswith(videoapi.FAL_QUEUE):
                assert url.endswith("/fal-ai/fake/text-to-image") and body["image_urls"] == []
                body = {**body, "image_urls": [REF_URL]}
            return super().json(method, url, headers, body)

    http = NoRefs()
    assert _run(cfg, http, models=["fake-fal"], assets=["props"]) == 0
    assert [p.name for p in (setdir / "raw").iterdir()] == ["props"]
    assert _run(cfg, NoHttp(), models=["nope"]) == 1


def test_downloaded_images_are_not_requested_again_and_post_only_redoes_the_post(setdir, capsys):
    cfg = _toml(setdir)
    assert _run(cfg, FakeHttp()) == 0
    capsys.readouterr()
    assert _run(cfg, NoHttp()) == 0  # todo bajado: no hay nada que mandar
    (setdir / "post" / "far" / "fake-fal_1.png").unlink()
    assert _run(cfg, NoHttp(), post_only=True) == 0
    assert (setdir / "post" / "far" / "fake-fal_1.png").exists()
    assert "post de 2 imágenes" in capsys.readouterr().out


def test_a_fal_request_cut_short_is_resumed_without_paying_again(setdir, capsys):
    cfg = _toml(setdir, models=("fake-fal",))
    base = f"{videoapi.FAL_QUEUE}/fal-ai/fake/requests/r9"
    ledger = {"attempts": [{"id": "far/fake-fal_1", "status": "submitted", "submitted": genimages._now(),
                            "handle": {"request_id": "r9", "status_url": f"{base}/status", "response_url": base},
                            "refs": [], "usd_estimate": 0.04}]}
    (setdir / "gen.json").write_text(json.dumps(ledger))
    http = FakeHttp()
    assert _run(cfg, http) == 0
    assert not [c for c in http.calls if c[0] == "POST"]
    assert "retomo el pedido r9" in capsys.readouterr().out
    assert (setdir / "raw" / "far" / "fake-fal_1.png").exists()


def test_a_kit_sheet_is_split_into_pieces(setdir):
    sheet = np.zeros((300, 900, 3), np.uint8)
    sheet[:] = (10, 250, 20)
    for i, w in enumerate((80, 200, 80)):
        x = 40 + i * 280
        cv2.rectangle(sheet, (x, 80), (x + w, 180), (100, 110, 140), -1)
        cv2.rectangle(sheet, (x, 80), (x + w, 180), (13, 15, 24), 5)

    class Sheet(FakeHttp):
        def download(self, url, dest, headers=None):
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(_png(sheet))

    cfg = _toml(setdir, models=("fake-fal",), assets="""
[[asset]]
name = "kit"
prompt = "Platform pieces."
refs = ["ranger.png"]
aspect = "16:9"
alpha = "cutout"
split = ["edge_left", "top", "edge_right"]
tile = { top = "x" }
height = 64
""")
    assert _run(cfg, Sheet()) == 0
    pieces = setdir / "post" / "kit" / "fake-fal_1"
    assert sorted(p.name for p in pieces.iterdir()) == ["edge_left.png", "edge_right.png", "top.png"]
    assert {Image.open(p).height for p in pieces.iterdir()} == {64}
    html = (setdir / "compare.html").read_text()
    assert "post/kit/fake-fal_1/top.png" in html


@pytest.mark.parametrize("asset, msg", [
    ('name = "a"\nprompt = "x"\nalpha = "sky"', "alpha tiene que ser"),
    ('name = "a"\nprompt = "x"\ntile = { top = "x" }', "tile nombra piezas que no están en split"),
    ('name = "a"\nprompt = "x"\nseam = "blur"', "seam tiene que ser"),
    ('name = "a"\nprompt = "x"\nstyle = "nope"', "no hay [styles] nope"),
    ('name = "a"\nprompt = "x"\nrefs = ["falta.png"]', "no existe la referencia"),
    ('name = "a"\nprompt = "x"\naspect = "ancho"', "aspect inválido"),
    ('name = "a"\nprompt = "x"\ncolor = "rojo"', "no conoce color"),
])
def test_config_errors(setdir, asset, msg):
    with pytest.raises((ValueError, FileNotFoundError), match=msg.replace("[", r"\[").replace("]", r"\]")):
        genimages.load(_toml(setdir, assets=f"[[asset]]\n{asset}\n"))


def test_the_real_set_config_loads_and_plans():
    from pathlib import Path
    cfg = genimages.load(Path(__file__).parents[2] / "backgrounds" / "ranger_base" / "gen.toml")
    names = [a.name for a in cfg.assets]
    assert names == ["style_frame", "sky", "far", "mid", "near", "platform_kit", "props"]
    kit = cfg.assets[names.index("platform_kit")]
    assert kit.split == ["edge_left", "top", "edge_right", "body", "floating"] and kit.alpha == "cutout"
    assert {a.alpha for a in cfg.assets if a.name in ("far", "mid", "near")} == {"layer"}
    assert cfg.assets[names.index("sky")].alpha == "opaque"
    tasks = genimages.plan(cfg)
    assert sum(t.usd for t in tasks) <= cfg.max_usd


def test_each_asset_can_pick_its_models_and_the_comparison_keeps_everything(setdir, capsys):
    two = """
[[asset]]
name = "far"
prompt = "A distant city skyline."
refs = ["ranger.png"]
aspect = "3:1"
alpha = "layer"
{extra}

[[asset]]
name = "props"
prompt = "A crate."
alpha = "cutout"
models = ["gpt-image-2.5-sunburst"]
"""
    assert _run(_toml(setdir, assets=two.format(extra="")), FakeHttp(), assets=["far"]) == 0
    capsys.readouterr()
    cfg = _toml(setdir, assets=two.format(extra='models = ["fake-fal"]\nn = 2\nref_role = "level"'))
    http = FakeHttp()
    assert _run(cfg, http) == 0
    out = capsys.readouterr().out
    assert "sólo fake-fal" in out and "2 modelos (fake-fal, gpt-image-2.5-sunburst)" in out
    posts = [c for c in http.calls if c[0] == "POST" and c[1] != videoapi.FAL_UPLOAD]
    assert sorted(c[1].rsplit("/", 1)[-1] for c in posts) == ["edit", "generations"]  # far/fake-fal_2 y props
    fal = next(c for c in posts if c[1].startswith(videoapi.FAL_QUEUE))
    assert "art direction of this game" in fal[3]["prompt"] and fal[3]["seed"] == 4  # la segunda opción: seed + 1
    html = (setdir / "compare.html").read_text()
    # far de gpt-image (de la primera corrida) sigue en la comparación aunque el asset ya no lo elija
    assert "post/far/gpt-image-2.5-sunburst_1.png" in html and "post/far/fake-fal_2.png" in html
    md = (setdir / "compare.md").read_text()
    assert md.count("| far |") == 3 and md.count("| props |") == 1


def test_asset_models_must_be_in_gen_models(setdir):
    with pytest.raises(ValueError, match="models nombra modelos que no están"):
        genimages.load(_toml(setdir, models=("fake-fal",), assets='[[asset]]\nname = "a"\nprompt = "x"\n'
                                                                  'models = ["flux-3"]\n'))
