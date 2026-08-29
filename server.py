import os
from flask import Flask, request, jsonify

app = Flask(__name__)

worker_hashrates = {}

@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "service": "Mining Monitor"
    })

@app.route("/hashrate", methods=["POST"])
def hashrate():
    data = request.get_json(silent=True) or {}

    worker_id = data.get("worker_id")
    hashrate = float(data.get("hashrate", 0))

    worker_hashrates[str(worker_id)] = hashrate

    return jsonify({
        "ok": True,
        "worker_id": worker_id,
        "hashrate": hashrate
    })

@app.route("/monitor")
def monitor():
    total = sum(worker_hashrates.values())

    lines = [
        "MINING MONITOR",
        "==============================",
        f"Worker aktiv: {len(worker_hashrates)}",
        f"Gesamthashrate: {total:,.0f} H/s",
        ""
    ]

    for worker_id, hashrate in worker_hashrates.items():
        lines.append(
            f"Worker {worker_id}: {hashrate:,.0f} H/s"
        )

    return "<pre>" + "\n".join(lines) + "</pre>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
