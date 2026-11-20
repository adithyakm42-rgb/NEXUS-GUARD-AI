
import json
from datetime import datetime

timestamps = []

with open("telemetry_data.jsonl", "r", encoding="utf-8") as file:
    for line in file:
        record = json.loads(line)
        timestamps.append(
            datetime.fromisoformat(record["timestamp_utc"])
        )

intervals = [
    (timestamps[i] - timestamps[i - 1]).total_seconds()
    for i in range(1, len(timestamps))
]

print("TOTAL RECORDS:", len(timestamps))
print("TOTAL INTERVALS:", len(intervals))

print("\nLargest time gaps:")

for gap in sorted(intervals, reverse=True)[:10]:
    print(round(gap, 2), "seconds")

print("\nIntervals greater than 10 seconds:")

large_gaps = [gap for gap in intervals if gap > 10]

print("Count:", len(large_gaps))
print("DATA GAP CHECK COMPLETED")
