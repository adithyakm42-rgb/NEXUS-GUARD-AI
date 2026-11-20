from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Literal
from datetime import datetime, timezone
import sqlite3
import json

from alert_engine import evaluate_alerts

# ==========================================
# NEXUS GUARD AI - CENTRAL BACKEND
# FINAL VERSION - PREDICTIVE INTELLIGENCE
# ==========================================

DB_FILE = "nexus_guard.db"

app = FastAPI(
    title="NEXUS GUARD AI",
    description="AIOps Telemetry, Persistent Alerts, and Alert Intelligence API",
    version="FINAL"
)


# ==========================================
# DATABASE INITIALIZATION + SAFE MIGRATION
# ==========================================

def initialize_database():
    with sqlite3.connect(DB_FILE) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collector_id TEXT NOT NULL,
                timestamp_utc TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                UNIQUE(collector_id, timestamp_utc)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_key TEXT NOT NULL UNIQUE,
                collector_id TEXT NOT NULL,
                metric TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                value REAL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'OPEN',
                first_seen TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                occurrence_count INTEGER NOT NULL DEFAULT 1,
                explanation TEXT NOT NULL DEFAULT '',
                possible_impact TEXT NOT NULL DEFAULT '',
                recommended_action TEXT NOT NULL DEFAULT '',
                resolved_at TEXT
            )
        """)

        # Upgrade an existing V3 database without deleting old records.
        existing_columns = {
            row[1] for row in connection.execute("PRAGMA table_info(alerts)")
        }

        new_columns = {
            "explanation": "TEXT NOT NULL DEFAULT ''",
            "possible_impact": "TEXT NOT NULL DEFAULT ''",
            "recommended_action": "TEXT NOT NULL DEFAULT ''",
            "resolved_at": "TEXT",
        }

        for column_name, column_type in new_columns.items():
            if column_name not in existing_columns:
                connection.execute(
                    f"ALTER TABLE alerts ADD COLUMN {column_name} {column_type}"
                )

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_status
            ON alerts(status)
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_alerts_collector
            ON alerts(collector_id)
        """)


initialize_database()


# ==========================================
# TELEMETRY DATA VALIDATION
# ==========================================

class Telemetry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timestamp_utc: datetime

    collector_id: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$"
    )

    cpu_usage: float = Field(ge=0, le=100)
    memory_usage: float = Field(ge=0, le=100)
    disk_usage: float = Field(ge=0, le=100)

    upload_mbps: float = Field(ge=0)
    download_mbps: float = Field(ge=0)

    status: Literal["NORMAL", "ANOMALY", "UNKNOWN"]

    event_category: str = Field(
        min_length=1,
        max_length=50,
        pattern=r"^[A-Z][A-Z0-9_]*$"
    )

    severity: Literal["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]

    @field_validator("timestamp_utc")
    @classmethod
    def require_utc(cls, value):
        if (
            value.tzinfo is None
            or value.utcoffset() != timezone.utc.utcoffset(value)
        ):
            raise ValueError("Timestamp must use UTC")
        return value


# ==========================================
# PERSISTENT ALERT ENGINE
# ==========================================

def update_persistent_alerts(connection, data):
    detected_alerts = evaluate_alerts(data)
    collector_id = data["collector_id"]
    current_time = data["timestamp_utc"]
    active_keys = []

    for alert in detected_alerts:
        alert_key = (
            f"{collector_id}:"
            f"{alert['metric']}:"
            f"{alert['title']}"
        )
        active_keys.append(alert_key)

        # Defaults keep the backend compatible with alert rules that
        # have not yet been given the three intelligence fields.
        explanation = alert.get("explanation", "")
        possible_impact = alert.get("possible_impact", "")
        recommended_action = alert.get("recommended_action", "")

        connection.execute("""
            INSERT INTO alerts (
                alert_key,
                collector_id,
                metric,
                title,
                description,
                value,
                severity,
                status,
                first_seen,
                last_seen,
                occurrence_count,
                explanation,
                possible_impact,
                recommended_action
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'OPEN', ?, ?, 1, ?, ?, ?)

            ON CONFLICT(alert_key) DO UPDATE SET
                description = excluded.description,
                value = excluded.value,
                severity = excluded.severity,
                explanation = excluded.explanation,
                possible_impact = excluded.possible_impact,
                recommended_action = excluded.recommended_action,
                status = CASE
                    WHEN alerts.status = 'RESOLVED' THEN 'OPEN'
                    ELSE alerts.status
                END,
                resolved_at = CASE
                    WHEN alerts.status = 'RESOLVED' THEN NULL
                    ELSE alerts.resolved_at
                END,
                first_seen = CASE
                    WHEN alerts.status = 'RESOLVED' THEN excluded.first_seen
                    ELSE alerts.first_seen
                END,
                last_seen = excluded.last_seen,
                occurrence_count = alerts.occurrence_count + 1
        """, (
            alert_key,
            collector_id,
            alert["metric"],
            alert["title"],
            alert["description"],
            alert["value"],
            alert["severity"],
            current_time,
            current_time,
            explanation,
            possible_impact,
            recommended_action
        ))

    # Automatically resolve alerts that are no longer detected.
    if active_keys:
        placeholders = ",".join("?" for _ in active_keys)
        connection.execute(f"""
            UPDATE alerts
            SET status = 'RESOLVED', resolved_at = ?
            WHERE collector_id = ?
              AND status IN ('OPEN', 'ACKNOWLEDGED')
              AND alert_key NOT IN ({placeholders})
        """, [current_time, collector_id] + active_keys)
    else:
        connection.execute("""
            UPDATE alerts
            SET status = 'RESOLVED', resolved_at = ?
            WHERE collector_id = ?
              AND status IN ('OPEN', 'ACKNOWLEDGED')
        """, (current_time, collector_id))


# ==========================================
# HOME + HEALTH
# ==========================================

@app.get("/")
def home():
    return {
        "project": "NEXUS GUARD AI",
        "backend": "Central Telemetry and Alert Intelligence API",
        "version": "FINAL",
        "status": "RUNNING"
    }


@app.get("/health")
def health():
    with sqlite3.connect(DB_FILE) as connection:
        connection.execute("SELECT 1")
    return {
        "status": "HEALTHY",
        "database": "CONNECTED",
        "version": "FINAL"
    }


# ==========================================
# TELEMETRY INGESTION
# ==========================================

@app.post("/ingest")
def ingest_telemetry(data: Telemetry):
    payload = data.model_dump(mode="json")

    try:
        with sqlite3.connect(DB_FILE) as connection:
            connection.execute("""
                INSERT INTO telemetry (
                    collector_id,
                    timestamp_utc,
                    payload_json
                )
                VALUES (?, ?, ?)
            """, (
                data.collector_id,
                data.timestamp_utc.isoformat(),
                json.dumps(payload)
            ))

            update_persistent_alerts(connection, payload)

        return {
            "status": "ACCEPTED",
            "collector_id": data.collector_id,
            "message": "Telemetry and intelligent alerts processed successfully"
        }

    except sqlite3.IntegrityError:
        return {
            "status": "DUPLICATE",
            "message": "Telemetry record already exists"
        }


# ==========================================
# TELEMETRY RETRIEVAL
# ==========================================

@app.get("/telemetry")
def get_telemetry(limit: int = 20):
    limit = max(1, min(limit, 100))

    with sqlite3.connect(DB_FILE) as connection:
        rows = connection.execute("""
            SELECT payload_json
            FROM telemetry
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

    records = [json.loads(row[0]) for row in rows]

    return {
        "total_records": len(records),
        "telemetry": records
    }


# ==========================================
# PERSISTENT ALERT RETRIEVAL
# ==========================================

@app.get("/alerts")
def get_alerts(limit: int = 100, status: str | None = None):
    limit = max(1, min(limit, 500))
    allowed_statuses = ["OPEN", "ACKNOWLEDGED", "RESOLVED"]

    if status is not None and status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Invalid alert status")

    with sqlite3.connect(DB_FILE) as connection:
        connection.row_factory = sqlite3.Row

        if status:
            rows = connection.execute("""
                SELECT *
                FROM alerts
                WHERE status = ?
                ORDER BY last_seen DESC
                LIMIT ?
            """, (status, limit)).fetchall()
        else:
            rows = connection.execute("""
                SELECT *
                FROM alerts
                ORDER BY last_seen DESC
                LIMIT ?
            """, (limit,)).fetchall()

    alerts = [dict(row) for row in rows]

    return {
        "total_alerts": len(alerts),
        "alerts": alerts
    }


# ==========================================
# ALERT SUMMARY
# ==========================================

@app.get("/alerts/summary")
def alert_summary():
    with sqlite3.connect(DB_FILE) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("""
            SELECT status, severity, COUNT(*) AS total
            FROM alerts
            GROUP BY status, severity
        """).fetchall()

    status_counts = {
        "OPEN": 0,
        "ACKNOWLEDGED": 0,
        "RESOLVED": 0
    }
    severity_counts = {
        "INFO": 0,
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0,
        "CRITICAL": 0
    }

    for row in rows:
        status_counts[row["status"]] += row["total"]
        severity_counts[row["severity"]] += row["total"]

    return {
        "total_alerts": sum(status_counts.values()),
        "status_counts": status_counts,
        "severity_counts": severity_counts
    }


# ==========================================
# ACKNOWLEDGE ALERT
# ==========================================

@app.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int):
    with sqlite3.connect(DB_FILE) as connection:
        cursor = connection.execute("""
            UPDATE alerts
            SET status = 'ACKNOWLEDGED'
            WHERE id = ? AND status = 'OPEN'
        """, (alert_id,))

        if cursor.rowcount == 0:
            existing = connection.execute("""
                SELECT status FROM alerts WHERE id = ?
            """, (alert_id,)).fetchone()

            if existing is None:
                raise HTTPException(status_code=404, detail="Alert not found")

            raise HTTPException(
                status_code=409,
                detail=f"Alert cannot be acknowledged: {existing[0]}"
            )

    return {
        "alert_id": alert_id,
        "status": "ACKNOWLEDGED",
        "message": "Alert acknowledged successfully"
    }


# ==========================================
# MANUALLY RESOLVE ALERT
# ==========================================

@app.post("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: int):
    with sqlite3.connect(DB_FILE) as connection:
        cursor = connection.execute("""
            UPDATE alerts
            SET status = 'RESOLVED', resolved_at = ?
            WHERE id = ? AND status IN ('OPEN', 'ACKNOWLEDGED')
        """, (datetime.now(timezone.utc).isoformat(), alert_id))

        if cursor.rowcount == 0:
            existing = connection.execute("""
                SELECT status FROM alerts WHERE id = ?
            """, (alert_id,)).fetchone()

            if existing is None:
                raise HTTPException(status_code=404, detail="Alert not found")

            raise HTTPException(
                status_code=409,
                detail=f"Alert cannot be resolved: {existing[0]}"
            )

    return {
        "alert_id": alert_id,
        "status": "RESOLVED",
        "message": "Alert resolved successfully"
    }


# ==========================================
# COLLECTOR HEALTH MONITORING
# ==========================================

@app.get("/collectors")
def get_collectors():
    with sqlite3.connect(DB_FILE) as connection:
        rows = connection.execute("""
            SELECT t.payload_json
            FROM telemetry t
            INNER JOIN (
                SELECT collector_id, MAX(id) AS latest_id
                FROM telemetry
                GROUP BY collector_id
            ) latest
            ON t.id = latest.latest_id
        """).fetchall()

    collectors = []
    current_time = datetime.now(timezone.utc)

    for row in rows:
        data = json.loads(row[0])
        last_seen = datetime.fromisoformat(
            data["timestamp_utc"].replace("Z", "+00:00")
        )

        age_seconds = max(
            0,
            (current_time - last_seen).total_seconds()
        )

        status = "ONLINE" if age_seconds <= 60 else "OFFLINE"

        collectors.append({
            "collector_id": data["collector_id"],
            "status": status,
            "last_seen": data["timestamp_utc"],
            "seconds_since_last_seen": round(age_seconds, 2)
        })

    return {
        "total_collectors": len(collectors),
        "online": sum(c["status"] == "ONLINE" for c in collectors),
        "offline": sum(c["status"] == "OFFLINE" for c in collectors),
        "collectors": collectors
    }


# ==========================================
# V4.6 PREDICTIVE INTELLIGENCE
# ==========================================

def _linear_projection(values, horizon_steps=3):
    """Project a short trend using least-squares over sequential samples."""
    clean = [float(v) for v in values if v is not None]
    if len(clean) < 3:
        return None, 0.0

    n = len(clean)
    xs = list(range(n))
    x_mean = sum(xs) / n
    y_mean = sum(clean) / n
    denominator = sum((x - x_mean) ** 2 for x in xs)

    if denominator == 0:
        return clean[-1], 0.0

    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, clean)) / denominator
    projected = clean[-1] + slope * horizon_steps
    return max(0.0, min(100.0, projected)), slope


@app.get("/predictive/summary")
def predictive_summary(samples: int = 30, horizon_steps: int = 3):
    """
    Experimental short-horizon trend estimate based on the latest samples.
    horizon_steps=3 means three collector sampling intervals ahead.
    This is a heuristic projection, not a trained forecasting model.
    """
    samples = max(3, min(samples, 100))
    horizon_steps = max(1, min(horizon_steps, 12))

    with sqlite3.connect(DB_FILE) as connection:
        rows = connection.execute("""
            SELECT collector_id, payload_json
            FROM telemetry
            ORDER BY id DESC
            LIMIT ?
        """, (samples * 20,)).fetchall()

    grouped = {}
    for collector_id, payload_json in rows:
        grouped.setdefault(collector_id, []).append(json.loads(payload_json))

    results = []
    for collector_id, records in grouped.items():
        # SQL returns newest first; retain the latest requested samples only.
        records = list(reversed(records[:samples]))
        if not records:
            continue
        latest = records[-1]
        metrics = {}
        slopes = {}

        for field in ("cpu_usage", "memory_usage", "disk_usage"):
            values = [r.get(field) for r in records if r.get(field) is not None]
            projected, slope = _linear_projection(values, horizon_steps)
            metrics[field] = {
                "current": round(float(values[-1]), 2) if values else None,
                "projected": round(projected, 2) if projected is not None else None,
                "slope_per_sample": round(slope, 3),
            }
            slopes[field] = slope

        current_values = [
            float(latest.get("cpu_usage", 0)),
            float(latest.get("memory_usage", 0)),
            float(latest.get("disk_usage", 0)),
        ]
        peak = max(current_values)

        # Explainable operational-risk heuristic; not a probability.
        risk_score = min(100, round(
            max(0, peak - 50) * 0.9
            + sum(max(0, slope) * 4 for slope in slopes.values())
        ))
        if peak >= 95 or risk_score >= 70:
            risk_level = "HIGH"
        elif peak >= 85 or risk_score >= 40:
            risk_level = "ELEVATED"
        else:
            risk_level = "LOW"

        warnings = []
        for field, label in (
            ("cpu_usage", "CPU"),
            ("memory_usage", "Memory"),
            ("disk_usage", "Disk"),
        ):
            current = metrics[field]["current"]
            projected = metrics[field]["projected"]
            slope = metrics[field]["slope_per_sample"]
            if current is not None and current >= 80:
                warnings.append(f"{label} is already high ({current:.1f}%).")
            elif projected is not None and projected >= 85 and slope > 0:
                warnings.append(f"{label} is trending toward a high level.")

        if len(records) < 3:
            warnings.append("Not enough samples for a reliable trend estimate.")

        results.append({
            "collector_id": collector_id,
            "samples_used": len(records),
            "latest_timestamp_utc": latest.get("timestamp_utc"),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "metrics": metrics,
            "early_warnings": warnings,
            "method": "Least-squares trend projection over recent telemetry",
            "disclaimer": "Experimental heuristic, not a probability, diagnosis, or guarantee."
        })

    return {
        "collectors_analyzed": len(results),
        "horizon_steps": horizon_steps,
        "results": results
    }

