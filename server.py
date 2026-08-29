import os
from flask import Flask, request, jsonify

app = Flask(__name__)

worker_hashrates = {}

@app.route("/")
def home():
    return "Mining Monitor läuft"

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

    output = []
    output.append("MINING MONITOR")
    output.append("=" * 40)
    output.append(f"Worker aktiv: {len(worker_hashrates)}")
    output.append(f"Gesamthashrate: {total:,.0f} H/s")
    output.append("")

    for worker_id, hashrate in worker_hashrates.items():
        output.append(
            f"Worker {worker_id}: {hashrate:,.0f} H/s"
        )

    return "<pre>" + "\n".join(output) + "</pre>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
