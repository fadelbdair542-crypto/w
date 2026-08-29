
import os
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

worker_hashrates = {}

WORKER_TIMEOUT = 3


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

    worker_hashrates[str(worker_id)] = {
        "hashrate": hashrate,
        "last_seen": time.time()
    }

    return jsonify({
        "ok": True,
        "worker_id": worker_id,
        "hashrate": hashrate
    })


@app.route("/monitor")
def monitor():
    now = time.time()

    # Worker entfernen, wenn länger als 3 Sekunden
    # kein Update angekommen ist
    expired_workers = [
        worker_id
        for worker_id, data in worker_hashrates.items()
        if now - data["last_seen"] > WORKER_TIMEOUT
    ]

    for worker_id in expired_workers:
        del worker_hashrates[worker_id]

    total = sum(
        data["hashrate"]
        for data in worker_hashrates.values()
    )

    lines = [
        "==================================================",
        "             MINING MONITOR",
        "==================================================",
        "",
        f"Worker aktiv:     {len(worker_hashrates)}",
        f"Gesamthashrate:   {total:,.0f} H/s",
        f"Gesamthashrate:   {total / 1000:,.2f} KH/s",
        f"Gesamthashrate:   {total / 1000000:,.2f} MH/s",
        "",
        "--------------------------------------------------"
    ]

    for worker_id, data in sorted(worker_hashrates.items()):
        lines.append(
            f"Worker {worker_id}: {data['hashrate']:,.0f} H/s"
        )

    lines.append("--------------------------------------------------")

    return "<pre>" + "\n".join(lines) + "</pre>"


@app.route("/status")
def status():
    now = time.time()

    expired_workers = [
        worker_id
        for worker_id, data in worker_hashrates.items()
        if now - data["last_seen"] > WORKER_TIMEOUT
    ]

    for worker_id in expired_workers:
        del worker_hashrates[worker_id]

    total = sum(
        data["hashrate"]
        for data in worker_hashrates.values()
    )

    return jsonify({
        "workers": len(worker_hashrates),
        "hashrate": total,
        "workers_data": {
            worker_id: data["hashrate"]
            for worker_id, data in worker_hashrates.items()
        }
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
