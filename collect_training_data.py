
import psutil
import json
import time
import socket
from datetime import datetime, timezone

LOG_FILE = "telemetry_data.jsonl"
INTERVAL = 5

previous_network = psutil.net_io_counters()

print("NEXUS GUARD AI - TELEMETRY LOGGER")
print("Collecting system data every 5 seconds.")
print("Press CTRL+C to stop.\n")

try:
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        while True:
            start_time = time.time()

            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage("C:\\").percent

            current_network = psutil.net_io_counters()

            upload_speed = (
                current_network.bytes_sent - previous_network.bytes_sent
            ) * 8 / (1024 * 1024)

            download_speed = (
                current_network.bytes_recv - previous_network.bytes_recv
            ) * 8 / (1024 * 1024)

            previous_network = current_network

            record = {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "hostname": socket.gethostname(),
                "cpu_usage": cpu,
                "memory_usage": memory,
                "disk_usage": disk,
                "upload_mbps": round(upload_speed, 3),
                "download_mbps": round(download_speed, 3)
            }

            file.write(json.dumps(record) + "\n")
            file.flush()

            print(
                f"CPU: {cpu}% | RAM: {memory}% | "
                f"DISK: {disk}% | "
                f"UPLOAD: {upload_speed:.3f} Mbps | "
                f"DOWNLOAD: {download_speed:.3f} Mbps"
            )

            time.sleep(max(0, INTERVAL - (time.time() - start_time)))

except KeyboardInterrupt:
    print("\nTelemetry collection stopped.")
    print(f"Data saved locally in {LOG_FILE}")
