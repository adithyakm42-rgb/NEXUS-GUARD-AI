
# ==========================================
# NEXUS GUARD AI - ALERT ENGINE V2.0
# INTELLIGENT ALERT EXPLANATION ENGINE
# ==========================================

from datetime import datetime, timezone


def create_alert(
    timestamp,
    collector_id,
    title,
    description,
    metric,
    value,
    severity,
    explanation,
    possible_impact,
    recommended_action
):

    return {
        "timestamp_utc": timestamp,
        "collector_id": collector_id,
        "title": title,
        "description": description,
        "metric": metric,
        "value": value,
        "severity": severity,

        # V4.2 INTELLIGENCE FIELDS
        "explanation": explanation,
        "possible_impact": possible_impact,
        "recommended_action": recommended_action
    }


def evaluate_alerts(data):

    alerts = []

    timestamp = data.get(
        "timestamp_utc",
        datetime.now(timezone.utc).isoformat()
    )

    collector_id = data.get(
        "collector_id",
        "unknown"
    )

    # ======================================
    # 1. CPU ALERT RULES
    # ======================================

    cpu = float(data.get("cpu_usage", 0))

    if cpu >= 90:

        alerts.append(create_alert(
            timestamp,
            collector_id,
            "Critical CPU Usage",
            f"CPU usage reached {cpu:.2f}%.",
            "CPU",
            cpu,
            "CRITICAL",
            "CPU utilization has crossed the critical threshold of 90%.",
            "Sustained high CPU utilization may cause slow application response and reduced system performance.",
            "Open Windows Task Manager, inspect CPU-intensive processes, and investigate whether the load is expected."
        ))

    elif cpu >= 80:

        alerts.append(create_alert(
            timestamp,
            collector_id,
            "High CPU Usage",
            f"CPU usage reached {cpu:.2f}%.",
            "CPU",
            cpu,
            "HIGH",
            "CPU utilization has crossed the high threshold of 80%.",
            "If sustained, high CPU utilization may affect application responsiveness.",
            "Monitor CPU-intensive applications and check whether the elevated usage continues."
        ))

    # ======================================
    # 2. MEMORY ALERT RULES
    # ======================================

    memory = float(data.get("memory_usage", 0))

    if memory >= 95:

        alerts.append(create_alert(
            timestamp,
            collector_id,
            "Critical Memory Usage",
            f"RAM usage reached {memory:.2f}%.",
            "RAM",
            memory,
            "CRITICAL",
            "Memory utilization has crossed the critical threshold of 95%.",
            "Very high memory utilization may cause application slowdowns, paging, or memory allocation failures.",
            "Open Windows Task Manager, sort processes by memory usage, and investigate applications consuming excessive RAM."
        ))

    elif memory >= 90:

        alerts.append(create_alert(
            timestamp,
            collector_id,
            "High Memory Usage",
            f"RAM usage reached {memory:.2f}%.",
            "RAM",
            memory,
            "HIGH",
            "Memory utilization has crossed the high threshold of 90%.",
            "Limited available memory may affect application performance if usage continues increasing.",
            "Check Task Manager for memory-intensive processes and monitor whether memory usage returns to normal."
        ))

    # ======================================
    # 3. DISK ALERT RULES
    # ======================================

    disk = float(data.get("disk_usage", 0))

    if disk >= 95:

        alerts.append(create_alert(
            timestamp,
            collector_id,
            "Critical Disk Usage",
            f"Disk usage reached {disk:.2f}%.",
            "DISK",
            disk,
            "CRITICAL",
            "Disk utilization has crossed the critical threshold of 95%.",
            "Very low remaining storage may prevent applications from saving files or operating correctly.",
            "Check available disk space, identify large files, and review safe cleanup options."
        ))

    elif disk >= 90:

        alerts.append(create_alert(
            timestamp,
            collector_id,
            "High Disk Usage",
            f"Disk usage reached {disk:.2f}%.",
            "DISK",
            disk,
            "HIGH",
            "Disk utilization has crossed the high threshold of 90%.",
            "Limited storage capacity may affect future file creation and application operations.",
            "Review disk usage and identify unnecessary files or large storage consumers."
        ))

    # ======================================
    # 4. AI ANOMALY DETECTION
    # ======================================

    if data.get("status") == "ANOMALY":

        alerts.append(create_alert(
            timestamp,
            collector_id,
            "AI Anomaly Detected",
            "The machine learning model detected unusual system behaviour.",
            "AI",
            None,
            "HIGH",
            "The Isolation Forest model classified the observed telemetry pattern as unusual compared with its learned baseline.",
            "Unusual resource or network activity may indicate an unexpected workload or system behaviour. This detection alone does not establish a security incident.",
            "Review CPU, RAM, disk and network telemetry around the detection timestamp. Compare the readings with normal workload patterns and investigate unexpected processes."
        ))

    return alerts
