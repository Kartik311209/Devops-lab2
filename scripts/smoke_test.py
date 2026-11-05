"""Run an in-process HTTP smoke test against the actual application handler."""
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import urlopen
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
import server

transcript = []
def report(line):
    print(line)
    transcript.append(line)

httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
thread = Thread(target=httpd.serve_forever, daemon=True)
thread.start()
base = f"http://127.0.0.1:{httpd.server_port}"
try:
    for path in ("/healthz", "/readyz", "/api/info"):
        with urlopen(base + path, timeout=5) as response:
            payload = response.read().decode("utf-8")
            assert response.status == 200, (path, response.status)
            if path == "/api/info":
                data = json.loads(payload)
                assert data["student"]["name"] == "Kartik Kumar"
                assert data["student"]["roll_number"] == "2301730205"
                assert data["student"]["email"] == "kartikjangra5366@gmail.com"
            report(f"PASS GET {path} HTTP {response.status}")
            report(payload)
finally:
    httpd.shutdown()
    httpd.server_close()
    log = Path(__file__).resolve().parents[1] / "evidence" / "logs" / "local-verification.txt"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text("\n".join(transcript) + "\n", encoding="utf-8")
