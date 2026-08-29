import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock

workers = {}
lock = Lock()


class Handler(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self.send_json(200, {
                "status": "online",
                "service": "Mining Monitor"
            })
            return

        if self.path == "/workers":
            with lock:
                data = dict(workers)

            total = sum(data.values())

            self.send_json(200, {
                "workers": data,
                "total_hashrate": total
            })
            return

        self.send_json(404, {
            "error": "Not found"
        })

    def do_POST(self):
        if self.path != "/hashrate":
            self.send_json(404, {
                "error": "Not found"
            })
            return

        try:
            length = int(self.headers.get("Content-Length", 0))

            if length <= 0 or length > 10000:
                self.send_json(400, {
                    "error": "Invalid request"
                })
                return

            raw_data = self.rfile.read(length)
            data = json.loads(raw_data.decode("utf-8"))

            worker_id = str(data["worker_id"])
            hashrate = float(data["hashrate"])

            if hashrate < 0:
                raise ValueError("Invalid hashrate")

            with lock:
                workers[worker_id] = hashrate

            print(
                f"Worker {worker_id}: {hashrate:,.0f} H/s",
                flush=True
            )

            self.send_json(200, {
                "success": True
            })

        except Exception as e:
            print(f"Fehler: {e}", flush=True)

            self.send_json(400, {
                "success": False,
                "error": "Invalid data"
            })

    def log_message(self, format, *args):
        pass


port = int(os.environ.get("PORT", "8080"))

server = ThreadingHTTPServer(
    ("0.0.0.0", port),
    Handler
)

print("=" * 50)
print("       MINING MONITOR SERVER")
print("=" * 50)
print(f"Server läuft auf Port {port}")
print("=" * 50)

server.serve_forever()
