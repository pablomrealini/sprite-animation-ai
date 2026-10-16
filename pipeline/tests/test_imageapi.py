"""Los pedidos que arma cada modelo de imagen, contra los campos de la doc de cada proveedor (2026-10-16)."""

import json
from pathlib import Path

import pytest

from spritepipe import imageapi

REF, REF2 = Path("refs/ranger.png"), Path("refs/blockout.png")

# Campos de entrada de cada endpoint, del schema OpenAPI de fal o de la referencia de la Image API
FIELDS = {
    "openai/images": {"model", "prompt", "images", "mask", "n", "size", "quality", "background", "output_format",
                      "output_compression", "input_fidelity", "moderation", "stream", "partial_images", "user",
                      "safety_identifier"},
    "openai/gpt-image-2.5/sunburst/edit": {"num_images", "quality", "prompt", "enable_safety_checker", "output_format",
                                           "background", "image_size", "output_compression", "image_urls",
                                           "sync_mode", "mask_url"},
    "google/nano-banana-2.1/edit": {"output_format", "resolution", "pdf_url", "thinking_level", "enable_web_search",
                                    "image_urls", "seed", "safety_tolerance", "video_url", "aspect_ratio", "prompt",
                                    "system_prompt", "sync_mode", "limit_generations", "num_images"},
    "fal-ai/nano-banana-pro/edit": {"aspect_ratio", "num_images", "seed", "system_prompt", "sync_mode",
                                    "limit_generations", "output_format", "enable_web_search", "safety_tolerance",
                                    "prompt", "image_urls", "resolution"},
    "bytedance/seedream/v5/pro/edit": {"enhance_prompt_mode", "prompt", "sync_mode", "enable_safety_checker",
                                       "image_size", "image_urls", "num_images", "output_format"},
    "blackforestlabs/flux-3/edit-image": {"resolution", "output_format", "image_urls", "sync_mode", "prompt",
                                          "aspect_ratio", "enable_prompt_expansion", "safety_tolerance", "version"},
    "fal-ai/flux-pro/kontext": {"sync_mode", "image_url", "seed", "enhance_prompt", "output_format", "aspect_ratio",
                                "num_images", "safety_tolerance", "guidance_scale", "prompt"},
}


def _req(**kw):
    base = dict(prompt="p", refs=[REF], aspect="16:9", transparent=False, quality="high", resolution="2K", seed=7)
    return imageapi.ImageRequest(**{**base, **kw})


def _call(name, **kw):
    return imageapi.MODELS[name].call(_req(**kw), lambda p: f"ref:{p.name}")


@pytest.mark.parametrize("name", list(imageapi.MODELS))
def test_every_model_builds_a_clean_json_payload(name):
    spec = imageapi.MODELS[name]
    call = _call(name)
    text = json.dumps(call.body)
    assert "ref:ranger.png" in text and "null" not in text
    assert spec.price(_req()) > 0 and spec.docs.startswith("https://")
    key = "openai/images" if spec.provider == "openai" else call.url.split("queue.fal.run/")[1]
    if key in FIELDS:
        assert set(call.body) <= FIELDS[key], set(call.body) - FIELDS[key]
    t2i = spec.call(_req(refs=[]), lambda p: "")
    assert "ref:" not in json.dumps(t2i.body) and t2i.url != call.url


def test_openai_edit_sends_references_as_data_urls_in_json(tmp_path):
    ref = tmp_path / "r.png"
    ref.write_bytes(b"\x89PNG fake")
    client = imageapi.OpenAIClient("sk-x")
    call = imageapi.MODELS["gpt-image-2.5-sunburst"].call(_req(refs=[ref], transparent=True), client.image_ref)
    assert call.url == "https://api.openai.com/v1/images/edits"
    assert call.body["images"] == [{"image_url": "data:image/png;base64,iVBORyBmYWtl"}]
    assert call.body["background"] == "transparent" and call.body["output_format"] == "png"
    assert call.body["size"] == "2560x1440" and "seed" not in call.body
    call = imageapi.MODELS["gpt-image-2.5-sunburst"].call(_req(refs=[]), client.image_ref)
    assert call.url == "https://api.openai.com/v1/images/generations" and call.body["background"] == "opaque"


@pytest.mark.parametrize("aspect", ["16:9", "3:1", "21:9", "1:1", "2:3", "4:1", "1:5"])
@pytest.mark.parametrize("res", ["1K", "2K", "4K"])
def test_openai_sizes_follow_the_rules(aspect, res):
    w, h = (int(v) for v in imageapi.openai_size(_req(aspect=aspect, resolution=res))[0].split("x"))
    assert w % 16 == 0 and h % 16 == 0 and 1 / 3 <= w / h <= 3 and max(w, h) <= 3840
    assert 655_360 <= w * h <= 8_294_400
    if res == "2K":
        assert max(w, h) <= 2560 and min(w, h) <= 1440  # sin entrar en lo experimental


@pytest.mark.parametrize("quality, size, usd", [
    ("low", (1024, 1024), 0.006), ("medium", (1024, 1024), 0.053), ("high", (1024, 1024), 0.211),
    ("low", (1536, 1024), 0.005), ("medium", (1536, 1024), 0.041), ("high", (1024, 1536), 0.165),
])
def test_openai_token_formula_reproduces_the_gpt_image_2_table(quality, size, usd):
    tokens = imageapi.openai_output_tokens("gpt-image-2", quality, *size)
    assert tokens * 30 / 1e6 == pytest.approx(usd, abs=0.0006)


@pytest.mark.parametrize("quality, usd", [("low", 0.00588), ("medium", 0.01317), ("high", 0.05268),
                                          ("xhigh", 0.09366), ("max", 0.21072)])
def test_gpt_image_2_5_at_1024_matches_fals_table(quality, usd):
    assert imageapi.openai_output_tokens("gpt-image-2.5", quality, 1024, 1024) * 30 / 1e6 == pytest.approx(usd, abs=1e-5)


def test_openai_rejects_a_quality_the_model_does_not_have():
    with pytest.raises(ValueError, match="gpt-image-2 no acepta quality 'max'"):
        imageapi.openai_output_tokens("gpt-image-2", "max", 1024, 1024)


def test_gpt_on_fal_uses_image_size_and_transparency():
    call = _call("gpt-image-2.5-sunburst-fal", transparent=True, aspect="3:1")
    assert call.url == "https://queue.fal.run/openai/gpt-image-2.5/sunburst/edit"
    assert call.body == {"prompt": "p", "image_urls": ["ref:ranger.png"], "image_size": {"width": 2544, "height": 848},
                         "quality": "high", "background": "transparent", "output_format": "png", "num_images": 1}
    assert imageapi.MODELS["gpt-image-2.5-sunburst-fal"].transparent


def test_nano_banana_picks_the_closest_aspect_and_its_price():
    call = _call("nano-banana-2.1", aspect="3:1")
    assert call.url == "https://queue.fal.run/google/nano-banana-2.1/edit"
    assert call.body == {"prompt": "p", "image_urls": ["ref:ranger.png"], "aspect_ratio": "21:9", "resolution": "2K",
                         "output_format": "png", "num_images": 1, "seed": 7}
    assert _call("nano-banana-2.1", aspect="4:1").body["aspect_ratio"] == "4:1"  # Pro no la tiene
    assert _call("nano-banana-pro", aspect="4:1").body["aspect_ratio"] == "21:9"
    spec = imageapi.MODELS["nano-banana-2.1"]
    assert spec.price(_req()) == pytest.approx(0.059 + 0.002)
    assert spec.size_label(_req(resolution="4K")) == "16:9 4K"
    assert imageapi.MODELS["nano-banana-pro"].price(_req(resolution="4K")) == 0.30


def test_seedream_stays_in_the_cheap_area_tier():
    spec = imageapi.MODELS["seedream-5-pro"]
    for aspect in ("16:9", "3:1", "1:1"):
        size = spec.call(_req(aspect=aspect), lambda p: "").body["image_size"]
        assert 1024 * 1024 <= size["width"] * size["height"] <= 1536 * 1536
    assert spec.price(_req()) == 0.0675
    assert spec.price(_req(refs=[REF, REF2])) == pytest.approx(0.072)
    assert spec.price(_req(resolution="4K")) == 0.135
    assert "seed" not in _call("seedream-5-pro").body


def test_flux_3_is_always_1k_without_seed():
    body = _call("flux-3", aspect="3:1").body
    assert body == {"prompt": "p", "image_urls": ["ref:ranger.png"], "aspect_ratio": "21:9", "resolution": "1k",
                    "output_format": "png"}


def test_kontext_routes_one_or_many_references():
    one = _call("flux-kontext-pro")
    assert one.url.endswith("/fal-ai/flux-pro/kontext") and one.body["image_url"] == "ref:ranger.png"
    many = _call("flux-kontext-pro", refs=[REF, REF2])
    assert many.url.endswith("/fal-ai/flux-pro/kontext/multi") and many.body["image_urls"] == ["ref:ranger.png",
                                                                                                "ref:blockout.png"]
    assert _call("flux-kontext-pro", refs=[]).url.endswith("/kontext/text-to-image")


def test_too_many_references_is_an_error():
    with pytest.raises(ValueError, match="hasta 4 referencias"):
        _call("flux-kontext-pro", refs=[REF] * 5)


def test_openai_errors():
    e = imageapi.HttpError(400, {"error": {"type": "image_generation_user_error", "code": "moderation_blocked",
                                           "message": "x", "moderation_details": {"moderation_stage": "output",
                                                                                  "categories": ["sexual"]}}}, "u")
    r = imageapi.openai_error(e)
    assert r.state == "blocked" and "output: sexual" in r.detail
    r = imageapi.openai_error(imageapi.HttpError(401, {"error": {"code": "invalid_api_key", "message": "bad"}}, "u"))
    assert r.state == "error" and "invalid_api_key" in r.detail


def test_nearest_aspect():
    assert imageapi.nearest("3:1", dict.fromkeys(("21:9", "16:9", "4:1"))) == "21:9"
    assert imageapi.nearest("3.5:1", dict.fromkeys(("21:9", "4:1"))) == "4:1"
    with pytest.raises(ValueError):
        imageapi.parse_aspect("16x9")
