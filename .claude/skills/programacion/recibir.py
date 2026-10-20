"""Recibe capturas del lienzo del juego (el panel del navegador integrado oculto saca capturas viejas y chicas): POST
/save?name=x.png con el data: URL en el cuerpo; las guarda en la carpeta del argumento (por defecto, caps/ al lado).

uso: python3 .claude/skills/programacion/recibir.py <carpeta> [puerto]   (en segundo plano; escucha en 127.0.0.1:8799 o el
puerto dado). Ojo: otras sesiones del estudio usan el mismo receptor; si el 8799 está ocupado, usar otro puerto (y
window.RECIBIR = puerto en la página) y no matar procesos de otros (pkill por nombre mata los de todas las sesiones).
En la página: await guardar("nombre.png") de pruebas.js."""
import base64, re, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "caps"
OUT.mkdir(parents=True, exist_ok=True)
class H(BaseHTTPRequestHandler):
    def do_POST(self):
        q = parse_qs(urlparse(self.path).query); name = re.sub(r"[^A-Za-z0-9_.-]", "_", q.get("name", ["cap.png"])[0])
        body = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode()
        (OUT / name).write_bytes(base64.b64decode(body.split(",", 1)[1]))
        self.send_response(200); self.send_header("Access-Control-Allow-Origin", "*"); self.end_headers(); self.wfile.write(b"ok")
    def log_message(self, *a): pass
HTTPServer(("127.0.0.1", int(sys.argv[2]) if len(sys.argv) > 2 else 8799), H).serve_forever()
