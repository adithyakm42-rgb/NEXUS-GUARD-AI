
import unittest
from datetime import datetime, timezone

from privacy_engine import validate_payload


def valid_payload():
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "collector_id": "collector-001",
        "cpu_usage": 25.0,
        "memory_usage": 70.0,
        "disk_usage": 60.0,
        "upload_mbps": 1.5,
        "download_mbps": 2.5,
        "status": "NORMAL",
        "event_category": "SYSTEM_HEALTH",
        "severity": "INFO"
    }


class TestPrivacyValidation(unittest.TestCase):

    def test_valid_payload(self):
        self.assertEqual(validate_payload(valid_payload()), [])

    def test_cpu_above_100_rejected(self):
        data = valid_payload()
        data["cpu_usage"] = 500
        self.assertTrue(validate_payload(data))

    def test_negative_network_speed_rejected(self):
        data = valid_payload()
        data["upload_mbps"] = -10
        self.assertTrue(validate_payload(data))

    def test_missing_collector_id_rejected(self):
        data = valid_payload()
        del data["collector_id"]
        self.assertTrue(validate_payload(data))

    def test_invalid_timestamp_rejected(self):
        data = valid_payload()
        data["timestamp_utc"] = "not-a-timestamp"
        self.assertTrue(validate_payload(data))

    def test_invalid_status_rejected(self):
        data = valid_payload()
        data["status"] = ["NORMAL"]
        self.assertTrue(validate_payload(data))

    def test_nan_value_rejected(self):
        data = valid_payload()
        data["cpu_usage"] = float("nan")
        self.assertTrue(validate_payload(data))


if __name__ == "__main__":
    unittest.main(verbosity=2)
