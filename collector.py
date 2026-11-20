
import psutil
import platform
import time
import json
from datetime import datetime, timezone

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

    print("=" * 50)
    print("NEXUS GUARD AI - REAL-TIME COLLECTOR")
    print("=" * 50)

    psutil.cpu_percent(interval=None)

    try:
        while True:
            metrics = collect_metrics()

            print(json.dumps(metrics, indent=2))

            print("-" * 50)

            time.sleep(5)

    except KeyboardInterrupt:
        print("\nCollector stopped safely.")
