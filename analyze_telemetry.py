
import json
import statistics
from datetime import datetime

LOG_FILE = "telemetry_data.jsonl"

required_fields = [
    "timestamp_utc",
    "hostname",
    "cpu_usage",
    "memory_usage",
    "disk_usage",
    "upload_mbps",
    "download_mbps"
]

records = []

with open(LOG_FILE, "r", encoding="utf-8") as file:
    for line_number, line in enumerate(file, start=1):
        try:
            record = json.loads(line)

            if not all(field in record for field in required_fields):
                print(f"Missing field on line {line_number}")
                continue

            for field in required_fields[2:]:
                value = float(record[field])
                if value < 0:
                    raise ValueError(f"Negative value in {field}")

            records.append(record)

        except (json.JSONDecodeError, ValueError) as error:
            print(f"Invalid record on line {line_number}: {error}")

if not records:
    print("No valid telemetry records found.")
    raise SystemExit

print("\n===== NEXUS GUARD AI DATA REPORT =====")

print("Total valid records:", len(records))
print("Hostname:", records[-1]["hostname"])

timestamps = [
    datetime.fromisoformat(record["timestamp_utc"])
    for record in records
]

duration = (timestamps[-1] - timestamps[0]).total_seconds()

print("Collection duration:", round(duration, 2), "seconds")

for field in [
    "cpu_usage",
    "memory_usage",
    "disk_usage",
    "upload_mbps",
    "download_mbps"
]:
    values = [float(record[field]) for record in records]

    print(f"\n{field}")
    print("Minimum:", round(min(values), 3))
    print("Maximum:", round(max(values), 3))
    print("Average:", round(statistics.mean(values), 3))

intervals = [
    (timestamps[i] - timestamps[i - 1]).total_seconds()
    for i in range(1, len(timestamps))
]

if intervals:
    print("\nAverage sampling interval:",
          round(statistics.mean(intervals), 2), "seconds")

print("\nDATA VALIDATION COMPLETED")
