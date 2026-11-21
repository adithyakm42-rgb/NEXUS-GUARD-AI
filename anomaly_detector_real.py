
import psutil
import joblib
import time
import pandas as pd

# Load trained model
bundle = joblib.load("nexus_model_real.pkl")
model = bundle["model"]
features = bundle["features"]

previous_network = psutil.net_io_counters()
previous_time = time.monotonic()

print("\n================================")
print("       NEXUS GUARD AI")
print("    LIVE ANOMALY DETECTOR")
print("================================")

try:
    while True:
        cpu = psutil.cpu_percent(interval=5)

        current_network = psutil.net_io_counters()
        current_time = time.monotonic()
        elapsed = max(current_time - previous_time, 0.001)

        upload = (
            (current_network.bytes_sent - previous_network.bytes_sent)
            * 8 / (1024 * 1024) / elapsed
        )

        download = (
            (current_network.bytes_recv - previous_network.bytes_recv)
            * 8 / (1024 * 1024) / elapsed
        )

        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage("C:\\").percent

        data = pd.DataFrame([{
            "cpu_usage": cpu,
            "memory_usage": memory,
            "disk_usage": disk,
            "upload_mbps": upload,
            "download_mbps": download
        }])

        data = data[features]

        prediction = model.predict(data)[0]
        score = model.decision_function(data)[0]

        status = "NORMAL" if prediction == 1 else "ANOMALY"

        # System health warnings
        health_warnings = []

        if cpu > 90:
            health_warnings.append("HIGH CPU USAGE")

        if memory > 85:
            health_warnings.append("HIGH RAM USAGE")

        if disk > 85:
            health_warnings.append("HIGH DISK USAGE")

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
                print("SYSTEM HEALTH WARNING:", warning)
        else:
            print("SYSTEM HEALTH: GOOD")

        previous_network = current_network
        previous_time = current_time

except KeyboardInterrupt:
    print("\nMonitoring stopped.")
