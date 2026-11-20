
import psutil
import json
import time
import socket
from datetime import datetime, timezone

LOG_FILE = "telemetry_data_v2.jsonl"
INTERVAL = 5

previous_network = psutil.net_io_counters()
previous_time = time.monotonic()

print("NEXUS GUARD AI - TELEMETRY LOGGER V2")
print("Collecting accurate system metrics every 5 seconds.")
print("Press CTRL+C to stop.\n")

try:
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        while True:
            cpu = psutil.cpu_percent(interval=INTERVAL)

            current_network = psutil.net_io_counters()
            current_time = time.monotonic()

            elapsed = current_time - previous_time

            upload_mbps = (
                (current_network.bytes_sent - previous_network.bytes_sent)
                * 8 / (1024 * 1024) / elapsed
            )

            download_mbps = (
                (current_network.bytes_recv - previous_network.bytes_recv)
                * 8 / (1024 * 1024) / elapsed
            )

            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage("C:\\").percent

            record = {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "hostname": socket.gethostname(),
                "cpu_usage": round(cpu, 2),
                "memory_usage": round(memory, 2),
                "disk_usage": round(disk, 2),
                "upload_mbps": round(upload_mbps, 4),
                "download_mbps": round(download_mbps, 4)
            }

            file.write(json.dumps(record) + "\n")
            file.flush()

            print(
                f"CPU: {cpu:.1f}% | "
                f"RAM: {memory:.1f}% | "
                f"DISK: {disk:.1f}% | "
                f"UPLOAD: {upload_mbps:.4f} Mbps | "
                f"DOWNLOAD: {download_mbps:.4f} Mbps"
            )

            previous_network = current_network
            previous_time = current_time

except KeyboardInterrupt:
    print("\nTelemetry collection stopped.")
    print(f"Data saved locally in {LOG_FILE}")
