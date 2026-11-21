
import os
import csv
import time
import psutil
import joblib
import pandas as pd

from datetime import datetime, timezone

# ==========================================
# NEXUS GUARD AI - CONFIGURATION
# ==========================================

MODEL_FILE = "nexus_model_real.pkl"
ANOMALY_LOG_FILE = "anomaly_history.csv"

CPU_THRESHOLD = 90
RAM_THRESHOLD = 85
DISK_THRESHOLD = 85

# ==========================================
# LOAD TRAINED AI MODEL
# ==========================================

if not os.path.exists(MODEL_FILE):
    raise FileNotFoundError(f"Model file not found: {MODEL_FILE}")

bundle = joblib.load(MODEL_FILE)

model = bundle["model"]
features = bundle["features"]

# ==========================================
# INITIALIZE CSV HISTORY
# ==========================================

if not os.path.exists(ANOMALY_LOG_FILE):
    with open(
        ANOMALY_LOG_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "timestamp_utc",
            "cpu_usage",
            "memory_usage",
            "disk_usage",
            "upload_mbps",
            "download_mbps",
            "ai_status",
            "anomaly_score",
            "health_warnings"
        ])

# ==========================================
# INITIALIZE NETWORK MONITORING
# ==========================================

previous_network = psutil.net_io_counters()
previous_time = time.monotonic()

print("\n================================")
print("       NEXUS GUARD AI")
print("    LIVE ANOMALY DETECTOR")
print("================================")

print("AI MODEL: LOADED")
print("NETWORK MONITORING: ACTIVE")
print("HEALTH ALERTS: ACTIVE")
print("HISTORY LOGGING: ACTIVE")

# ==========================================
# LIVE MONITORING
# ==========================================

try:

    while True:

        # CPU monitoring
        cpu = psutil.cpu_percent(interval=5)

        # Network monitoring
        current_network = psutil.net_io_counters()
        current_time = time.monotonic()

        elapsed = max(
            current_time - previous_time,
            0.001
        )

        upload = (
            (current_network.bytes_sent - previous_network.bytes_sent)
            * 8 / (1024 * 1024) / elapsed
        )

        download = (
            (current_network.bytes_recv - previous_network.bytes_recv)
            * 8 / (1024 * 1024) / elapsed
        )

        # Memory and disk monitoring
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage("C:\\").percent

        # Prepare AI input
        data = pd.DataFrame([{
            "cpu_usage": cpu,
            "memory_usage": memory,
            "disk_usage": disk,
            "upload_mbps": upload,
            "download_mbps": download
        }])

        data = data[features]

        # AI anomaly prediction
        prediction = model.predict(data)[0]
        score = model.decision_function(data)[0]

        status = (
            "NORMAL"
            if prediction == 1
            else "ANOMALY"
        )

        # ==================================
        # SYSTEM HEALTH CHECK
        # ==================================

        health_warnings = []

        if cpu > CPU_THRESHOLD:
            health_warnings.append("HIGH CPU USAGE")

        if memory > RAM_THRESHOLD:
            health_warnings.append("HIGH RAM USAGE")

        if disk > DISK_THRESHOLD:
            health_warnings.append("HIGH DISK USAGE")

        # ==================================
        # DISPLAY MONITORING RESULTS
        # ==================================

        print("\n--------------------------------")
        print(f"CPU: {cpu:.2f}%")
        print(f"RAM: {memory:.2f}%")
        print(f"DISK: {disk:.2f}%")
        print(f"UPLOAD: {upload:.4f} Mbps")
        print(f"DOWNLOAD: {download:.4f} Mbps")

        print(f"AI STATUS: {status}")
        print(f"ANOMALY SCORE: {score:.4f}")

        if prediction == -1:
            print("WARNING: Unusual activity detected!")

        if health_warnings:

            for warning in health_warnings:
                print(
                    "SYSTEM HEALTH WARNING:",
                    warning
                )

        else:
            print("SYSTEM HEALTH: GOOD")

        # ==================================
        # SAVE ANOMALY AND WARNING HISTORY
        # ==================================

        if prediction == -1 or health_warnings:

            timestamp = datetime.now(
                timezone.utc
            ).isoformat()

            with open(
                ANOMALY_LOG_FILE,
                "a",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.writer(file)

                writer.writerow([
                    timestamp,
                    round(cpu, 2),
                    round(memory, 2),
                    round(disk, 2),
                    round(upload, 4),
                    round(download, 4),
                    status,
                    round(float(score), 4),
                    "; ".join(health_warnings)
                ])

            print(
                "EVENT SAVED:",
                ANOMALY_LOG_FILE
            )

        # Update previous network values
        previous_network = current_network
        previous_time = current_time

except KeyboardInterrupt:

    print("\n================================")
    print("       MONITORING STOPPED")
    print("================================")

    print(
        "HISTORY FILE:",
        ANOMALY_LOG_FILE
    )
