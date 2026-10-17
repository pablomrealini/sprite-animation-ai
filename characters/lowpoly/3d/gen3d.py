"""Vía 3D del personaje low-poly: modelo, rig y animaciones por API de fal (lo pago) y nada más.

Dos pedidos:

- **personaje**: Meshy 7.1 multi-image-to-3d con las cuatro vistas en T-pose (frente, tres cuartos, espalda y el
  espejo de tres cuartos, que vale porque el personaje es simétrico). Meshy no pide rotular las vistas, así que no
  hay que adivinar qué llama "izquierda" cada modelo. En el mismo pedido: textura, auto-rig, el idle de la
  biblioteca (id 0) y, de yapa, caminar y correr (vienen con el rig).
- **arma**: Hunyuan 3D 3.1 Pro con el lateral del arma de frente y su espejo de espalda (frente y espalda no son
  ambiguos; el arma es simétrica de lado a lado).

Uso (desde la raíz del repo):

    uv run --project pipeline python characters/lowpoly/3d/gen3d.py --dry-run
    eval "$(grep '^export FAL_KEY=' ~/.zshrc | tail -1)" && \\
        uv run --project pipeline python characters/lowpoly/3d/gen3d.py personaje arma

`--dry-run` sólo arma las entradas (copias congeladas en `entradas/`) y muestra qué se manda y cuánto sale. Sin
`--dry-run` sube las vistas al CDN de fal (se borran solas al día), espera el resultado y baja todo a
`out/<pedido>/` con la respuesta tal cual (`respuesta.json`) y la procedencia (`pedido.json`).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

AQUI = Path(__file__).resolve().parent
VISTAS = AQUI.parent / "refs" / "vistas"
ENTRADAS = AQUI / "entradas"
OUT = AQUI / "out"

FAL_QUEUE = "https://queue.fal.run"
FAL_UPLOAD = "https://rest.fal.ai/storage/upload/initiate?storage_type=fal-cdn-v3"
UPLOAD_TTL_S = 86400

# Precios de las docs de fal del 2026-10-17 (copias en el scratchpad de la sesión 4ac2d916, docs/3d/).
PEDIDOS = {
    "personaje": {
        "endpoint": "fal-ai/meshy/v7.1/multi-image-to-3d",
        "imagenes": {"image_urls": ["tpose_frente", "tpose_tres_cuartos", "tpose_espalda", "tpose_tres_cuartos~espejo"]},
        "payload": {
            "topology": "triangle",
            "target_polycount": 10000,  # low-poly de verdad; el rig necesita aristas en las articulaciones
            "should_remesh": True,
            "should_texture": True,
            "enable_pbr": False,
            "pose_mode": "t-pose",
            "enable_rigging": True,
            "rigging_height_meters": 1.7,
            "enable_animation": True,
            "animation_action_id": 0,  # "Idle" de la biblioteca; caminar y correr vienen con el rig
        },
        "costo": [("modelo con textura", 1.20), ("auto-rig", 0.20), ("animación (idle)", 0.12)],
    },
    "arma": {
        "endpoint": "fal-ai/hunyuan-3d/v3.1/pro/image-to-3d",
        "imagenes": {"input_image_url": "arma_lateral", "back_image_url": "arma_lateral~espejo"},
        "payload": {"generate_type": "Normal", "enable_pbr": False},
        "costo": [("generación", 0.375), ("multivista", 0.15)],
    },
}


def preparar(nombre: str) -> Path:
    """Copia congelada de la vista en entradas/ (las de refs/vistas las rehace otra sesión); `~espejo` la da vuelta."""
    base, _, mod = nombre.partition("~")
    dest = ENTRADAS / f"{base}{'_' + mod if mod else ''}.png"
    if not dest.exists():
        ENTRADAS.mkdir(parents=True, exist_ok=True)
        im = Image.open(VISTAS / f"{base}.png").convert("RGB")
        if mod == "espejo":
            im = ImageOps.mirror(im)
        im.save(dest)
    return dest


class Fal:
    def __init__(self, key: str):
        self.h = {"Authorization": f"Key {key}"}

    def _json(self, method: str, url: str, body: dict | None = None, extra: dict | None = None) -> dict:
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method,
                                     headers={"Content-Type": "application/json", **self.h, **(extra or {})})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read()
        except urllib.error.HTTPError as e:
            raise SystemExit(f"{method} {url} → {e.code}: {e.read()[:800].decode(errors='replace')}") from None
        return json.loads(raw) if raw else {}

    def subir(self, p: Path) -> str:
        r = self._json("POST", FAL_UPLOAD, {"file_name": p.name, "content_type": "image/png"},
                       {"X-Fal-Object-Lifecycle-Preference": json.dumps({"expiration_duration_seconds": UPLOAD_TTL_S})})
        req = urllib.request.Request(r["upload_url"], data=p.read_bytes(), method="PUT",
                                     headers={"Content-Type": "image/png"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            resp.read()
        return r["file_url"]

    def correr(self, endpoint: str, payload: dict, log) -> tuple[dict, dict]:
        h = self._json("POST", f"{FAL_QUEUE}/{endpoint}", payload)
        log(f"  request_id {h['request_id']}")
        t0, ultimo = time.time(), None
        while True:
            s = self._json("GET", h["status_url"])
            st = s.get("status")
            if st != ultimo:
                log(f"  {st} ({time.time() - t0:.0f} s)")
                ultimo = st
            if st == "COMPLETED":
                break
            if time.time() - t0 > 3600:
                raise SystemExit(f"más de una hora esperando {h['request_id']}")
            time.sleep(10)
        if s.get("error"):
            raise SystemExit(f"falló: {s.get('error_type')}: {s.get('error')}")
        return h, self._json("GET", h["response_url"])


def archivos(obj, ruta=()):
    """Todos los {url: ...} de la respuesta, con la ruta de claves para nombrarlos."""
    if isinstance(obj, dict):
        if isinstance(obj.get("url"), str):
            yield ruta, obj
        for k, v in obj.items():
            yield from archivos(v, ruta + (str(k),))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from archivos(v, ruta + (str(i),))


def bajar(url: str, dest: Path) -> None:
    # fal.media y los assets de Meshy son públicos: la key no viaja a otro host.
    part = dest.with_name(dest.name + ".part")
    with urllib.request.urlopen(urllib.request.Request(url), timeout=600) as r, open(part, "wb") as f:
        shutil.copyfileobj(r, f)
    part.replace(dest)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("pedidos", nargs="*", choices=list(PEDIDOS), help="por defecto, todos")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    a.pedidos = a.pedidos or list(PEDIDOS)

    total = 0.0
    for n in a.pedidos:
        p = PEDIDOS[n]
        costo = sum(c for _, c in p["costo"])
        total += costo
        imgs = {k: ([preparar(x) for x in v] if isinstance(v, list) else preparar(v)) for k, v in p["imagenes"].items()}
        print(f"[{n}] {p['endpoint']}  US${costo:.3f}  ({', '.join(f'{d} {c:.3f}' for d, c in p['costo'])})")
        for k, v in imgs.items():
            print(f"  {k}: {', '.join(x.name for x in v) if isinstance(v, list) else v.name}")
        print(f"  {json.dumps(p['payload'], ensure_ascii=False)}")
    print(f"total US${total:.3f}")
    if a.dry_run:
        return

    key = os.environ.get("FAL_KEY")
    if not key:
        raise SystemExit("falta FAL_KEY en el entorno: eval \"$(grep '^export FAL_KEY=' ~/.zshrc | tail -1)\"")
    fal = Fal(key)
    for n in a.pedidos:
        p = PEDIDOS[n]
        dest = OUT / n
        if (dest / "respuesta.json").exists():
            print(f"[{n}] ya está en {dest.relative_to(AQUI)}; borrar la carpeta para repetirlo (y pagarlo de nuevo)")
            continue
        dest.mkdir(parents=True, exist_ok=True)
        log = lambda m: print(m, flush=True)  # noqa: E731
        log(f"[{n}] subiendo vistas")
        payload = dict(p["payload"])
        for k, v in p["imagenes"].items():
            payload[k] = [fal.subir(preparar(x)) for x in v] if isinstance(v, list) else fal.subir(preparar(v))
        log(f"[{n}] {p['endpoint']}")
        h, r = fal.correr(p["endpoint"], payload, log)
        (dest / "respuesta.json").write_text(json.dumps(r, indent=1, ensure_ascii=False))
        (dest / "pedido.json").write_text(json.dumps({
            "endpoint": p["endpoint"], "request_id": h["request_id"], "imagenes": p["imagenes"],
            "payload": p["payload"], "costo_usd": sum(c for _, c in p["costo"]), "costo": p["costo"],
            "fecha": time.strftime("%Y-%m-%d %H:%M:%S")}, indent=1, ensure_ascii=False))
        for ruta, f in archivos(r):
            nombre = "__".join(ruta)
            ext = Path(urllib.parse.urlparse(f["url"]).path).suffix or Path(f.get("file_name") or "").suffix
            log(f"  bajando {nombre}{ext}")
            bajar(f["url"], dest / f"{nombre}{ext}")
    print("listo")


if __name__ == "__main__":
    sys.exit(main())
