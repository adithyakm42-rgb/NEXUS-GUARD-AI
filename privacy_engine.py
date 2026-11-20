
import json
import math
import re
from datetime import datetime, timezone

AUDIT_FILE = "egress_audit.jsonl"

ALLOWED_FIELDS = {
    "timestamp_utc", "collector_id",
    "cpu_usage", "memory_usage", "disk_usage",
    "upload_mbps", "download_mbps",
    "status", "event_category", "severity"
}

REQUIRED_FIELDS = {"timestamp_utc", "collector_id"}

NUMERIC_RANGES = {
    "cpu_usage": (0, 100),
    "memory_usage": (0, 100),
    "disk_usage": (0, 100),
    "upload_mbps": (0, float("inf")),
    "download_mbps": (0, float("inf"))
}

ALLOWED_STATUS = {"NORMAL", "ANOMALY", "UNKNOWN"}
ALLOWED_SEVERITY = {"INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"}


def filter_payload(raw_data):
    approved = {}
    blocked = []

    for key, value in raw_data.items():
        if key in ALLOWED_FIELDS:
            approved[key] = value
        else:
            blocked.append(key)

    return approved, blocked


def validate_payload(data):
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    for field, (minimum, maximum) in NUMERIC_RANGES.items():
        if field in data:
            value = data[field]

            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or not minimum <= value <= maximum
            ):
                errors.append(f"Invalid value: {field}")

    if "collector_id" in data:
        collector_id = data["collector_id"]

        if (
            not isinstance(collector_id, str)
            or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", collector_id)
        ):
            errors.append("Invalid collector_id")

    if "timestamp_utc" in data:
        timestamp = data["timestamp_utc"]

        try:
            if not isinstance(timestamp, str):
                raise ValueError()

            parsed = datetime.fromisoformat(
                timestamp.replace("Z", "+00:00")
            )

            if (
                parsed.tzinfo is None
                or parsed.utcoffset() != timezone.utc.utcoffset(parsed)
            ):
                raise ValueError()

        except (ValueError, TypeError):
            errors.append("Invalid UTC timestamp")

    if "status" in data:
        if (
            not isinstance(data["status"], str)
            or data["status"] not in ALLOWED_STATUS
        ):
            errors.append("Invalid status")

    if "severity" in data:
        if (
            not isinstance(data["severity"], str)
            or data["severity"] not in ALLOWED_SEVERITY
        ):
            errors.append("Invalid severity")

    if "event_category" in data:
        category = data["event_category"]

        if (
            not isinstance(category, str)
            or not re.fullmatch(r"[A-Z][A-Z0-9_]{0,49}", category)
        ):
            errors.append("Invalid event_category")

    return errors


def write_audit_log(approved, blocked, errors):
    audit_record = {
        "audit_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "allowed_fields": list(approved.keys()),
        "blocked_fields": blocked,
        "validation_errors": errors,
        "transmission_status": (
            "REJECTED_INVALID" if errors else "FILTERED_NOT_SENT"
        )
    }

    with open(AUDIT_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(audit_record) + "\n")


def prepare_secure_payload(raw_data):
    if not isinstance(raw_data, dict):
        raise TypeError("Payload must be a dictionary")

    approved, blocked = filter_payload(raw_data)
    errors = validate_payload(approved)

    write_audit_log(approved, blocked, errors)

    if errors:
        return None

    return approved


if __name__ == "__main__":
    print("\n===================================")
    print("       NEXUS GUARD AI")
    print("       PRIVACY ENGINE V2.0")
    print("===================================")

    sample_data = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "collector_id": "collector-001",
        "cpu_usage": 15.5,
        "memory_usage": 80.4,
        "disk_usage": 88.0,
        "upload_mbps": 0.02,
        "download_mbps": 0.05,
        "status": "NORMAL",
        "event_category": "SYSTEM_HEALTH",
        "severity": "INFO",
        "hostname": "MY-COMPUTER",
        "password": "sample-secret",
        "raw_log": "Sensitive internal log",
        "access_token": "sample-token"
    }

    safe_payload = prepare_secure_payload(sample_data)

    if safe_payload is not None:
        print("\nVALIDATED APPROVED PAYLOAD:")
        print(json.dumps(safe_payload, indent=4))
        print("\nVALIDATION: PASSED")
    else:
        print("\nPAYLOAD REJECTED")

    print("\nAudit file:", AUDIT_FILE)
    print("Transmission: NOT SENT")
