
import psutil
import platform
import time
import pandas as pd
import joblib

from datetime import datetime, timezone

# Load trained model
model = joblib.load("nexus_model.pkl")

print("NEXUS GUARD AI - AI ANOMALY DETECTOR")
print("Model loaded successfully")


def collect_metrics():

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hostname": platform.node(),
        "cpu_usage": psutil.cpu_percent(interval=None),
        "memory_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage("C:\\").percent
    }


def detect_anomaly(metrics):

    features = pd.DataFrame([{
        "cpu_usage": metrics["cpu_usage"],
        "memory_usage": metrics["memory_usage"],
        "disk_usage": metrics["disk_usage"]
    }])

    prediction = model.predict(features)[0]
    score = model.decision_function(features)[0]

    status = "NORMAL" if prediction == 1 else "ANOMALY"

    return status, round(float(score), 4)


if __name__ == "__main__":

    psutil.cpu_percent(interval=None)

    try:
        while True:

            metrics = collect_metrics()
            status, score = detect_anomaly(metrics)

            print("\n------------------------------")
            print("SERVER:", metrics["hostname"])
            print("CPU:", metrics["cpu_usage"], "%")
            print("RAM:", metrics["memory_usage"], "%")
            print("DISK:", metrics["disk_usage"], "%")
            print("AI STATUS:", status)
            print("ANOMALY SCORE:", score)

            if status == "ANOMALY":
                print("WARNING: Unusual behaviour detected!")

            time.sleep(5)

    except KeyboardInterrupt:
        print("\nAI Detector stopped.")
