
import psutil
import platform
import time
from collections import deque
from datetime import datetime, timezone
import json

# Keep the latest 180 readings (15 minutes)
window = deque(maxlen=180)

def collect_metrics():

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("C:\\")
    network = psutil.net_io_counters()

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hostname": platform.node(),
        "cpu_usage": psutil.cpu_percent(interval=None),
        "memory_usage": memory.percent,
        "disk_usage": disk.percent,
        "network_sent_mb": round(network.bytes_sent / (1024 ** 2), 2),
        "network_received_mb": round(network.bytes_recv / (1024 ** 2), 2)
    }


if __name__ == "__main__":

    print("NEXUS GUARD AI - ROLLING WINDOW ENGINE")

    psutil.cpu_percent(interval=None)

    try:
        while True:

            metrics = collect_metrics()

            # Add latest reading
            window.append(metrics)

            # Calculate average CPU
            avg_cpu = sum(
                item["cpu_usage"] for item in window
            ) / len(window)

            avg_memory = sum(
                item["memory_usage"] for item in window
            ) / len(window)

            print(json.dumps({
                "latest_cpu": metrics["cpu_usage"],
                "average_cpu": round(avg_cpu, 2),
                "average_memory": round(avg_memory, 2),
                "stored_frames": len(window)
            }, indent=2))

            print("-" * 40)

            time.sleep(5)

    except KeyboardInterrupt:
        print("\nRolling Window Engine stopped.")
