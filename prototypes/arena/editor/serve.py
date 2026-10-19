"""Servidor local del editor de arenas (sólo la librería estándar).

uso (desde la raíz del repo):
    python3 prototypes/arena/editor/serve.py            # http://127.0.0.1:8772/
    python3 prototypes/arena/editor/serve.py --port 9000

Sirve prototypes/arena/ entero: el editor (editor/dist/, que arma editor/build.py si falta), las arenas (arenas/) y el
juego (dist/, el de prototypes/arena/build.py), todo en el mismo origen, así el botón "Probar en el juego" le pasa la
arena al juego por localStorage. Además:
  GET  /api/arenas   las arenas: arenas/<nombre>.json (las del menú del juego) y los borradores arenas/<carpeta>/*.json
                     (sin las carpetas que empiezan con punto ni los kit.json)
  GET  /api/kits     los kits de piezas: arenas/<kit>/kit.json (los arma editor/kit.py)
  POST /api/save     {"key": "refineria", "arena": {...}}: escribe arenas/<key>.json con el formato de siempre. Si ya
                     había uno distinto, antes lo copia a arenas/.respaldo/<key>-<fecha>.json (quedan los últimos 30
                     de cada arena; la carpeta se ignora sola en git)
  GET  /api/game     si el juego está armado (dist/index.html)
  POST /api/build    arma el juego (prototypes/arena/build.py)
  /dist/arenas/<x>   sale siempre de arenas/<x>: Probar muestra las láminas y piezas de ahora aunque el juego no se haya
                     vuelto a armar (dist/arenas/ es la copia del último build: con piezas nuevas del kit quedaba vieja)
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARENA = HERE.parent
ROOT = ARENA.parent.parent
ARENAS = ARENA / "arenas"
KEY = re.compile(r"^(?:[a-z0-9_]+/)?[a-z0-9_]+$")


def compact(v) -> str:
    return json.dumps(v, ensure_ascii=False, separators=(", ", ": "))


def fmt(v, ind: int = 0, depth: int = 0) -> str:
    """El formato de las arenas a mano: una clave por renglón, y cada sólido, objeto o spawn en su renglón."""
    sp, end = "  " * (ind + 1), "  " * ind
    if isinstance(v, dict) and v and depth < 2:
        items = (f"{sp}{json.dumps(k, ensure_ascii=False)}: {fmt(x, ind + 1, depth + 1)}" for k, x in v.items())
        return "{\n" + ",\n".join(items) + "\n" + end + "}"
    if isinstance(v, list) and v and all(isinstance(x, (dict, list)) for x in v):
        return "[\n" + ",\n".join(sp + compact(x) for x in v) + "\n" + end + "]"
    return compact(v)


def arenas() -> dict:
    out = {p.stem: p for p in sorted(ARENAS.glob("*.json"))}
    out.update({f"{p.parent.name}/{p.stem}": p for p in sorted(ARENAS.glob("*/*.json"))
                if not p.parent.name.startswith(".") and p.name != "kit.json"})
    return {k: json.loads(p.read_text(encoding="utf-8")) for k, p in out.items()}


def kits() -> dict:
    return {p.parent.name: json.loads(p.read_text(encoding="utf-8")) for p in sorted(ARENAS.glob("*/kit.json"))}


BACKUP = ARENAS / ".respaldo"
KEEP = 30


def backup(dst: Path, key: str, new_text: str) -> Path | None:
    """La versión que estaba en disco, antes de pisarla: arenas/.respaldo/<key>-<fecha>.json (las últimas KEEP)."""
    if not dst.exists() or dst.read_text(encoding="utf-8") == new_text:
        return None
    BACKUP.mkdir(exist_ok=True)
    ignore = BACKUP / ".gitignore"
    if not ignore.exists():
        ignore.write_text("*\n", encoding="utf-8")
    stem = key.replace("/", "__")
    out = BACKUP / f"{stem}-{time.strftime('%Y%m%d-%H%M%S')}.json"
    shutil.copy2(dst, out)
    for old in sorted(BACKUP.glob(f"{stem}-*.json"))[:-KEEP]:
        old.unlink()
    return out


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt_, *args):
        if "/api/" in str(args[0] if args else ""):
            super().log_message(fmt_, *args)

    def _json(self, data, code: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/editor", "/editor/"):
            self.send_response(302)
            self.send_header("Location", "/editor/dist/index.html")
            self.end_headers()
            return
        if path == "/api/arenas":
            return self._json(arenas())
        if path == "/api/kits":
            return self._json(kits())
        if path == "/api/game":
            game = ARENA / "dist" / "index.html"
            return self._json({"built": game.exists(), "mtime": game.stat().st_mtime if game.exists() else None})
        if path.startswith("/dist/arenas/") and (ARENAS / path[len("/dist/arenas/"):]).exists():
            self.path = path.replace("/dist/arenas/", "/arenas/", 1)
        return super().do_GET()

    def do_POST(self):
        path = self.path.split("?")[0]
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        except ValueError:
            return self._json({"ok": False, "error": "JSON inválido"}, 400)
        if path == "/api/save":
            key, arena = body.get("key", ""), body.get("arena")
            if not KEY.match(key) or not isinstance(arena, dict):
                return self._json({"ok": False, "error": f"nombre inválido: {key!r} (minúsculas, números y _)"}, 400)
            dst = ARENAS / f"{key}.json"
            dst.parent.mkdir(exist_ok=True)
            text = fmt(arena) + "\n"
            old = backup(dst, key, text)
            dst.write_text(text, encoding="utf-8")
            print(f"  guardada {dst.relative_to(ROOT)}" + (f" (la anterior: {old.relative_to(ROOT)})" if old else ""))
            return self._json({"ok": True, "file": str(dst.relative_to(ROOT)),
                               "backup": str(old.relative_to(ROOT)) if old else None})
        if path == "/api/build":
            cmd = ["uv", "run", "--project", str(ROOT / "pipeline"), "python", str(ARENA / "build.py")]
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=600)
            return self._json({"ok": r.returncode == 0, "out": (r.stdout + r.stderr)[-4000:]})
        return self._json({"ok": False, "error": "no existe"}, 404)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--port", type=int, default=8772)
    args = ap.parse_args()
    if not (HERE / "dist" / "index.html").exists():
        print("armando el editor (editor/build.py)…", flush=True)
        subprocess.run(["uv", "run", "--project", str(ROOT / "pipeline"), "python", str(HERE / "build.py")],
                       cwd=ROOT, check=True)
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), partial(Handler, directory=str(ARENA)))
    print(f"editor de arenas: http://127.0.0.1:{args.port}/", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
