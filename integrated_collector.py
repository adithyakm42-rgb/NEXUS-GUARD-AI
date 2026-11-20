
import psutil
import joblib
import pandas as pd
import time
import socket
import json
import requests

from datetime import datetime, timezone
from privacy_engine import prepare_secure_payload

# ==========================================
# NEXUS GUARD AI - LIVE INTEGRATED COLLECTOR
# ==========================================

MODEL_FILE = "nexus_model_real.pkl"
OUTPUT_FILE = "approved_payloads.jsonl"
COLLECTOR_ID = "collector-001"
API_URL = "http://127.0.0.1:8000/ingest"
INTERVAL = 5

print("\n==========================================")
print("          NEXUS GUARD AI")
print("       LIVE COLLECTOR V2.0")
print("==========================================")

# 1. Load trained AI model
bundle = joblib.load(MODEL_FILE)
model = bundle["model"]
features = bundle["features"]

# 2. Initialize network counters
previous_network = psutil.net_io_counters()
previous_time = time.monotonic()

print("\nAI model loaded successfully.")
print("Privacy Engine connected.")
print("API endpoint configured.")
print("Live monitoring started.")
print("\nPress CTRL+C to stop.\n")

try:
    with open(OUTPUT_FILE, "a", encoding="utf-8") as output:

        while True:

            # 3. Collect system metrics
            cpu = psutil.cpu_percent(interval=INTERVAL)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage("C:\\").percent

            # 4. Calculate network throughput
            current_network = psutil.net_io_counters()
            current_time = time.monotonic()

            elapsed = current_time - previous_time

            upload = (
                (current_network.bytes_sent - previous_network.bytes_sent)
                * 8 / (1024 * 1024) / elapsed
            )

            download = (
                (current_network.bytes_recv - previous_network.bytes_recv)
                * 8 / (1024 * 1024) / elapsed
            )

            # 5. Run AI anomaly detection
            model_input = pd.DataFrame([{
                "cpu_usage": cpu,
                "memory_usage": memory,
                "disk_usage": disk,
                "upload_mbps": upload,
                "download_mbps": download
            }])

            model_input = model_input[features]

            prediction = model.predict(model_input)[0]
            score = model.decision_function(model_input)[0]

            status = "NORMAL" if prediction == 1 else "ANOMALY"
            severity = "INFO" if status == "NORMAL" else "HIGH"

            # 6. Build raw local telemetry
            raw_data = {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "collector_id": COLLECTOR_ID,
                "cpu_usage": round(cpu, 2),
                "memory_usage": round(memory, 2),
                "disk_usage": round(disk, 2),
                "upload_mbps": round(upload, 4),
                "download_mbps": round(download, 4),
                "status": status,
                "event_category": "SYSTEM_HEALTH",
                "severity": severity,

                # These fields must remain local
                "hostname": socket.gethostname(),
                "anomaly_score": round(float(score), 4)
            }

            # 7. Apply Privacy Engine
            safe_payload = prepare_secure_payload(raw_data)

            if safe_payload is not None:

                # 8. Save approved payload locally
                output.write(json.dumps(safe_payload) + "\n")
                output.flush()

                # 9. Send ONLY privacy-approved payload
                try:
                    response = requests.post(
                        API_URL,
                        json=safe_payload,
                        timeout=3
                    )

                    response.raise_for_status()
                    result = response.json()

                    print("------------------------------------------")
                    print(f"CPU: {cpu:.2f}%")
                    print(f"RAM: {memory:.2f}%")
                    print(f"DISK: {disk:.2f}%")
                    print(f"UPLOAD: {upload:.4f} Mbps")
                    print(f"DOWNLOAD: {download:.4f} Mbps")
                    print(f"AI STATUS: {status}")
                    print(f"ANOMALY SCORE: {score:.4f}")
                    print("PRIVACY: VALIDATED")
                    print("LOCAL PAYLOAD: SAVED")
                    print(f"API RESPONSE: {result['status']}")

                except requests.RequestException as error:
                    print("------------------------------------------")
                    print("LOCAL PAYLOAD: SAVED")
                    print("API TRANSMISSION: FAILED")
                    print(f"REASON: {error}")

            else:
                print("WARNING: Payload rejected by Privacy Engine.")

            previous_network = current_network
            previous_time = current_time

except KeyboardInterrupt:
    print("\n==========================================")
    print("NEXUS GUARD AI monitoring stopped.")
    print("Approved payloads saved locally.")
    print("==========================================")
