"""Small dependency-free HTTP service for the DevOps Lab 2 workflow."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from datetime import datetime, timezone


APP_NAME = os.getenv("APP_NAME", "devops-lab2")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
STUDENT_NAME = os.getenv("STUDENT_NAME", "Kartik Kumar")
STUDENT_ROLL = os.getenv("STUDENT_ROLL", "2301730205")
STUDENT_EMAIL = os.getenv("STUDENT_EMAIL", "kartikjangra5366@gmail.com")


class Handler(BaseHTTPRequestHandler):
    def respond(self, code, body, content_type="application/json; charset=utf-8"):
        payload = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path in ("/healthz", "/readyz"):
            return self.respond(200, json.dumps({"status": "ok", "check": self.path[1:]}))
        if self.path == "/" or self.path == "/api/info":
            return self.respond(200, json.dumps({
                "application": APP_NAME,
                "version": APP_VERSION,
                "student": {"name": STUDENT_NAME, "roll_number": STUDENT_ROLL, "email": STUDENT_EMAIL},
                "served_at_utc": datetime.now(timezone.utc).isoformat(),
            }, indent=2))
        return self.respond(404, json.dumps({"error": "not found", "path": self.path}))

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)


if __name__ == "__main__":
    host, port = "0.0.0.0", int(os.getenv("PORT", "8080"))
    print(f"{APP_NAME} {APP_VERSION} listening on {host}:{port}", flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()
