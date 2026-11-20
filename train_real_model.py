
import json
import joblib
import pandas as pd

from datetime import datetime
from sklearn.ensemble import IsolationForest

DATA_FILE = "telemetry_data_v2.jsonl"
MODEL_FILE = "nexus_model_real.pkl"

FEATURES = [
    "cpu_usage",
    "memory_usage",
    "disk_usage",
    "upload_mbps",
    "download_mbps"
]

records = []
seen_timestamps = set()
invalid_records = 0

print("NEXUS GUARD AI - REAL DATA TRAINING")
print("-----------------------------------")

# 1. Read and validate telemetry
with open(DATA_FILE, "r", encoding="utf-8") as file:
    for line in file:
        try:
            record = json.loads(line)

            timestamp = datetime.fromisoformat(
                record["timestamp_utc"]
            )

            values = {
                feature: float(record[feature])
                for feature in FEATURES
            }

            if timestamp in seen_timestamps:
                invalid_records += 1
                continue

            if any(value < 0 for value in values.values()):
                invalid_records += 1
                continue

            if any(
                values[field] > 100
                for field in [
                    "cpu_usage",
                    "memory_usage",
                    "disk_usage"
                ]
            ):
                invalid_records += 1
                continue

            seen_timestamps.add(timestamp)

            records.append({
                "timestamp_utc": timestamp,
                **values
            })

        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            invalid_records += 1

if len(records) < 100:
    raise SystemExit(
        "Not enough valid records. Collect more telemetry."
    )

# 2. Sort records by timestamp
records.sort(key=lambda row: row["timestamp_utc"])

df = pd.DataFrame(records)

# 3. Prepare training features
X = df[FEATURES]

print("Valid records:", len(X))
print("Invalid or duplicate records:", invalid_records)
print(
    "Collection duration:",
    round(
        (
            df["timestamp_utc"].iloc[-1]
            - df["timestamp_utc"].iloc[0]
        ).total_seconds() / 60,
        2
    ),
    "minutes"
)

# 4. Train Isolation Forest
model = IsolationForest(
    n_estimators=200,
    contamination=0.02,
    random_state=42
)

model.fit(X)

# 5. Save model and feature information
model_bundle = {
    "model": model,
    "features": FEATURES
}

joblib.dump(model_bundle, MODEL_FILE)

# 6. Display training summary
predictions = model.predict(X)

normal_count = int((predictions == 1).sum())
anomaly_count = int((predictions == -1).sum())

print("\nTRAINING COMPLETED")
print("Normal training records:", normal_count)
print("Flagged training records:", anomaly_count)
print("Model saved:", MODEL_FILE)
print("\nREAL DATA MODEL READY FOR TESTING")
