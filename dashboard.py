
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

from datetime import datetime, timezone
from html import escape

# ==========================================
# NEXUS GUARD AI FINAL
# ADVANCED SECURITY OPERATIONS CENTER
# ==========================================

API_URL = os.getenv(
    "NEXUS_API_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

st.set_page_config(
    page_title="NEXUS GUARD AI | SOC",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM UI
# ==========================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stApp {
    background: linear-gradient(135deg,#07111f,#101e34,#091525);
    color: #eaf2ff;
    font-family: 'Inter', sans-serif;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1500px;
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}

h1,h2,h3 {
    color: #f1f6ff !important;
    font-weight: 800 !important;
}

p,label {
    color: #c3d3e9;
}

[data-testid="stSidebar"] {
    background: #0a1526;
    border-right: 1px solid #263d59;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg,#172b46,#102039);
    border: 1px solid #294968;
    padding: 18px;
    border-radius: 15px;
    box-shadow: 0 5px 18px rgba(0,0,0,.2);
}

[data-testid="stMetricLabel"] {
    color: #a9c0df !important;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 800;
}

.stButton > button {
    background: linear-gradient(90deg,#1267c5,#168acb);
    color: white;
    border: 1px solid #328bd7;
    border-radius: 9px;
    font-weight: 700;
}

.stButton > button:hover {
    background: #168acb;
    color: white;
    border-color: #62dcff;
}

div[data-baseweb="select"] > div {
    background: #14263e;
    border-color: #345477;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(19,39,65,.65);
    border: 1px solid #294968;
    border-radius: 14px;
}

.stTabs [aria-selected="true"] {
    color: #45d7ff !important;
}

.hero {
    padding: 26px;
    border-radius: 18px;
    background: linear-gradient(110deg,#102b4b,#124064,#172c50);
    border: 1px solid #2876a6;
    margin-bottom: 22px;
}

.hero-title {
    color: white;
    font-size: 30px;
    font-weight: 800;
}

.hero-subtitle {
    color: #b7d8f2;
    font-size: 13px;
}

.section-label {
    color: #49d9ff;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
}

.online {
    color: #42e5a5;
    background: #103d34;
    border: 1px solid #209c75;
    border-radius: 20px;
    padding: 5px 12px;
    font-weight: 800;
    font-size: 12px;
}

.offline {
    color: #ff7777;
    background: #451e2a;
    border: 1px solid #bd4358;
    border-radius: 20px;
    padding: 5px 12px;
    font-weight: 800;
    font-size: 12px;
}

.threat-normal {
    background: linear-gradient(120deg,#103b35,#145747);
    border: 1px solid #24b78b;
    border-radius: 15px;
    padding: 19px;
}

.threat-warning {
    background: linear-gradient(120deg,#49331a,#63431b);
    border: 1px solid #f2a93b;
    border-radius: 15px;
    padding: 19px;
}

.threat-critical {
    background: linear-gradient(120deg,#481d2b,#692334);
    border: 1px solid #ef5365;
    border-radius: 15px;
    padding: 19px;
}

.timeline-item {
    background: #14263e;
    border-left: 4px solid #35bdf2;
    padding: 12px 16px;
    margin-bottom: 10px;
    border-radius: 8px;
}

.footer {
    color: #829bb9;
    text-align: center;
    font-size: 12px;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER
# ==========================================

st.markdown("""
<div class="hero">
    <div class="section-label">INTELLIGENT AIOPS PLATFORM</div>
    <div class="hero-title">🛡️ NEXUS GUARD AI</div>
    <div class="hero-subtitle">
        Advanced Security Operations Center |
        Real-Time Observability |
        AI-Powered Anomaly Detection
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.markdown("## 🛡️ NEXUS GUARD")
    st.caption("SECURITY OPERATIONS CENTER")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Executive Overview",
            "Collector Monitoring",
            "Security Alerts",
            "Telemetry Analytics",
            "Alert Analytics",
            "Predictive Intelligence",
            "Event Investigation"
        ]
    )

    st.divider()
    st.markdown("### SYSTEM INFORMATION")
    st.caption(f"Backend: {API_URL}")
    st.caption("Refresh: Every 5 seconds")
    st.caption("Version: FINAL")
    st.caption("Environment: Local prototype")

# ==========================================
# API FUNCTIONS
# ==========================================

def api_get(endpoint, params=None):

    try:
        response = requests.get(
            f"{API_URL}{endpoint}",
            params=params,
            timeout=5
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException:
        return None


def fetch_telemetry():

    result = api_get(
        "/telemetry",
        {"limit": 100}
    )

    if result is None:
        return None

    records = result.get("telemetry", [])

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)

    df["timestamp_utc"] = pd.to_datetime(
        df["timestamp_utc"],
        utc=True,
        errors="coerce"
    )

    df = df.dropna(subset=["timestamp_utc"])

    return df.sort_values("timestamp_utc")


def fetch_collectors():

    result = api_get("/collectors")

    if result is None:
        return None

    return result.get("collectors", [])


def fetch_alerts():

    result = api_get(
        "/alerts",
        {"limit": 100}
    )

    if result is None:
        return None

    return result.get("alerts", [])


def fetch_alert_summary():
    return api_get("/alerts/summary")


def fetch_predictive_summary():
    return api_get("/predictive/summary", {"samples": 30, "horizon_steps": 3})


def perform_alert_action(alert_id, action):

    try:
        response = requests.post(
            f"{API_URL}/alerts/{alert_id}/{action}",
            timeout=5
        )

        response.raise_for_status()
        return response.json()

    except requests.RequestException as error:
        st.error(f"Alert action failed: {error}")
        return None

# ==========================================
# CHART CONFIGURATION
# ==========================================

def style_chart(fig, height=350):

    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(12,27,47,.5)",
        font=dict(
            family="Inter",
            color="#dceaff"
        ),
        margin=dict(
            l=20,
            r=20,
            t=55,
            b=20
        ),
        xaxis=dict(gridcolor="#263d59"),
        yaxis=dict(gridcolor="#263d59")
    )

    return fig


# ==========================================
# CIRCULAR GAUGE FUNCTION
# ==========================================

def create_gauge(title, value, color):

    value = max(0, min(100, float(value)))

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={
                "suffix": "%",
                "font": {
                    "size": 31,
                    "color": "#ffffff"
                }
            },
            title={
                "text": title,
                "font": {
                    "size": 17,
                    "color": "#c8ddf5"
                }
            },
            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickcolor": "#9bb2cf",
                    "tickfont": {
                        "color": "#9bb2cf"
                    }
                },
                "bar": {
                    "color": color,
                    "thickness": 0.25
                },
                "bgcolor": "#14263e",
                "bordercolor": "#294968",
                "borderwidth": 2,
                "steps": [
                    {
                        "range": [0, 60],
                        "color": "#153b39"
                    },
                    {
                        "range": [60, 85],
                        "color": "#59451f"
                    },
                    {
                        "range": [85, 100],
                        "color": "#542634"
                    }
                ],
                "threshold": {
                    "line": {
                        "color": "#ffffff",
                        "width": 3
                    },
                    "thickness": 0.8,
                    "value": value
                }
            }
        )
    )

    fig.update_layout(
        height=250,
        margin=dict(l=20,r=20,t=55,b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )

    return fig


# ==========================================
# AI THREAT LEVEL
# ==========================================

def get_threat_level(latest):

    status = str(latest.get("status", "UNKNOWN")).upper()
    severity = str(latest.get("severity", "INFO")).upper()

    if status == "ANOMALY" or severity == "CRITICAL":
        return "CRITICAL", "threat-critical"

    if severity in ["HIGH", "MEDIUM"]:
        return "WARNING", "threat-warning"

    if status == "NORMAL":
        return "NORMAL", "threat-normal"

    return "UNKNOWN", "threat-warning"


# ==========================================
# LIVE DASHBOARD
# ==========================================

@st.fragment(run_every="5s")
def live_dashboard():

    df = fetch_telemetry()
    collectors = fetch_collectors()
    alerts = fetch_alerts()
    summary = fetch_alert_summary()

    if df is None:
        st.error("Backend disconnected. Check FastAPI.")
        return

    online = sum(
        c.get("status") == "ONLINE"
        for c in (collectors or [])
    )

    offline = sum(
        c.get("status") == "OFFLINE"
        for c in (collectors or [])
    )

    # CONNECTION STATUS

    st.markdown("""
    <span style="color:#42e5a5;font-weight:800;">
    ● BACKEND CONNECTED
    </span>
    <span style="float:right;color:#8fa9c7;font-size:12px;">
    LIVE MONITORING • 5 SECOND REFRESH
    </span>
    """, unsafe_allow_html=True)

    st.write("")

    # ======================================
    # EXECUTIVE OVERVIEW
    # ======================================

    if page == "Executive Overview":

        st.markdown("## 📊 Executive Overview")

        a, b, c, d = st.columns(4)

        a.metric("Collectors Online", online)
        b.metric("Collectors Offline", offline)
        d.metric("Telemetry Records", len(df))

        if df.empty:
            st.info("Waiting for telemetry. Start your collector.")
            return

        latest = df.iloc[-1]

        c.metric("AI Detection", str(latest["status"]))

        cpu = latest["cpu_usage"]
        ram = latest["memory_usage"]
        disk = latest["disk_usage"]

        threat, threat_class = get_threat_level(latest)

        st.divider()

        st.markdown("## 🧠 AI Security Assessment")

        st.markdown(
            f"""
            <div class="{threat_class}">
                <div style="font-size:12px;font-weight:800;
                letter-spacing:2px;color:#dceaff;">
                    CURRENT AI DETECTION STATE
                </div>
                <div style="font-size:32px;font-weight:800;
                color:white;margin-top:7px;">
                    {escape(threat)}
                </div>
                <div style="font-size:13px;color:#dceaff;">
                    Model status: {escape(str(latest['status']))}
                    &nbsp; | &nbsp;
                    Telemetry severity: {escape(str(latest.get('severity', 'UNKNOWN')))}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption(
            "This indicator reflects the model status and severity "
            "reported by your collector. It is not a complete security "
            "threat assessment."
        )

        st.divider()

        st.markdown("## ⚡ System Resource Monitoring")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.plotly_chart(
                create_gauge("CPU Usage", cpu, "#38bdf8"),
                width="stretch"
            )

        with col2:
            st.plotly_chart(
                create_gauge("Memory Usage", ram, "#a78bfa"),
                width="stretch"
            )

        with col3:
            st.plotly_chart(
                create_gauge("Disk Usage", disk, "#34d399"),
                width="stretch"
            )

        st.divider()

        st.markdown("## 🌐 Network Performance")

        a, b = st.columns(2)

        a.metric(
            "Upload Speed",
            f"{latest['upload_mbps']:.4f} Mbps"
        )

        b.metric(
            "Download Speed",
            f"{latest['download_mbps']:.4f} Mbps"
        )

        st.divider()

        st.markdown("## 📈 Live Performance Trends")

        chart1, chart2 = st.columns(2)

        with chart1:

            fig = px.line(
                df,
                x="timestamp_utc",
                y="cpu_usage",
                title="CPU Usage History",
                markers=True,
                color_discrete_sequence=["#38bdf8"]
            )

            st.plotly_chart(
                style_chart(fig),
                width="stretch"
            )

        with chart2:

            fig = px.line(
                df,
                x="timestamp_utc",
                y="memory_usage",
                title="Memory Usage History",
                markers=True,
                color_discrete_sequence=["#a78bfa"]
            )

            st.plotly_chart(
                style_chart(fig),
                width="stretch"
            )

        if summary:

            counts = summary.get("status_counts", {})

            st.divider()
            st.markdown("## 🚨 Alert Overview")

            a, b, c = st.columns(3)

            a.metric("Open", counts.get("OPEN", 0))
            b.metric("Acknowledged", counts.get("ACKNOWLEDGED", 0))
            c.metric("Resolved", counts.get("RESOLVED", 0))

    # ======================================
    # COLLECTOR MONITORING
    # ======================================

    elif page == "Collector Monitoring":

        st.markdown("## 🖥️ Collector Health Center")

        a, b, c = st.columns(3)

        a.metric("Total Collectors", len(collectors or []))
        b.metric("Online", online)
        c.metric("Offline", offline)

        st.divider()

        if collectors is None:
            st.error("Collector API unavailable.")

        elif not collectors:
            st.info("No collectors registered yet.")

        else:

            for collector in collectors:

                status = collector.get("status", "UNKNOWN")

                badge = (
                    "online"
                    if status == "ONLINE"
                    else "offline"
                )

                collector_id = escape(
                    str(collector.get("collector_id", ""))
                )

                last_seen = escape(
                    str(collector.get("last_seen", ""))
                )

                age = collector.get(
                    "seconds_since_last_seen", 0
                )

                with st.container(border=True):

                    st.markdown(
                        f"""
                        <div style="display:flex;
                        justify-content:space-between;
                        align-items:center;">
                            <div>
                                <div style="color:#45d7ff;
                                font-size:12px;font-weight:800;">
                                    COLLECTOR ID
                                </div>
                                <div style="font-size:21px;
                                font-weight:800;color:white;">
                                    {collector_id}
                                </div>
                            </div>
                            <span class="{badge}">
                                {escape(str(status))}
                            </span>
                        </div>
                        <hr style="border-color:#294968;">
                        <div style="color:#c1d4e9;">
                            Last telemetry: {last_seen}
                        </div>
                        <div style="color:#c1d4e9;">
                            Seconds since last heartbeat: {age}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    # ======================================
    # SECURITY ALERTS
    # ======================================

    elif page == "Security Alerts":

        st.markdown("## 🚨 Security Alert Center")

        if alerts is None or summary is None:

            st.error("Unable to retrieve alerts.")

        else:

            counts = summary.get("status_counts", {})

            a, b, c = st.columns(3)

            a.metric("🔴 Open", counts.get("OPEN", 0))
            b.metric("🟠 Acknowledged", counts.get("ACKNOWLEDGED", 0))
            c.metric("🟢 Resolved", counts.get("RESOLVED", 0))

            st.divider()

            status_filter = st.selectbox(
                "Filter by status",
                ["ALL", "OPEN", "ACKNOWLEDGED", "RESOLVED"]
            )

            severity_filter = st.selectbox(
                "Filter by severity",
                ["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
            )

            filtered = alerts

            if status_filter != "ALL":
                filtered = [
                    x for x in filtered
                    if x["status"] == status_filter
                ]

            if severity_filter != "ALL":
                filtered = [
                    x for x in filtered
                    if x["severity"] == severity_filter
                ]

            if not filtered:
                st.success("No alerts match your filters.")

            for alert in filtered:

                alert_id = alert["id"]
                status = alert["status"]
                severity = alert["severity"]

                with st.container(border=True):

                    st.markdown(
                        f"### {escape(str(alert['title']))}"
                    )

                    st.write(alert["description"])

                    # V4.4: Display intelligence generated by alert_engine.py
                    explanation = alert.get("explanation") or "No explanation is available for this alert yet."
                    possible_impact = alert.get("possible_impact") or "No impact assessment is available yet."
                    recommended_action = alert.get("recommended_action") or "Review the metric and investigate the source of the alert."

                    with st.expander("🧠 AI Alert Intelligence", expanded=True):
                        st.markdown("**Why was this alert triggered?**")
                        st.write(explanation)

                        st.markdown("**Possible impact**")
                        st.write(possible_impact)

                        st.markdown("**Recommended action**")
                        st.info(recommended_action)

                    st.caption(
                        f"Severity: {severity} | "
                        f"Status: {status} | "
                        f"Metric: {alert['metric']}"
                    )

                    a, b, c = st.columns(3)

                    a.write(f"Alert ID: {alert_id}")
                    b.write(f"Occurrences: {alert['occurrence_count']}")
                    c.write(f"Collector: {alert['collector_id']}")

                    st.caption(
                        f"First seen: {alert['first_seen']} | "
                        f"Last seen: {alert['last_seen']}"
                    )

                    a, b = st.columns(2)

                    if status == "OPEN":

                        with a:

                            if st.button(
                                "✓ Acknowledge",
                                key=f"ack_{alert_id}",
                                width="stretch"
                            ):

                                result = perform_alert_action(
                                    alert_id,
                                    "acknowledge"
                                )

                                if result:
                                    st.success("Alert acknowledged.")
                                    st.rerun()

                    if status in ["OPEN", "ACKNOWLEDGED"]:

                        with b:

                            if st.button(
                                "✓ Resolve",
                                key=f"resolve_{alert_id}",
                                width="stretch"
                            ):

                                result = perform_alert_action(
                                    alert_id,
                                    "resolve"
                                )

                                if result:
                                    st.success("Alert resolved.")
                                    st.rerun()

    # ======================================
    # TELEMETRY ANALYTICS
    # ======================================

    elif page == "Telemetry Analytics":

        st.markdown("## 📈 Advanced Telemetry Analytics")

        if df.empty:
            st.info("No telemetry records available.")

        else:

            st.metric("Samples Available", len(df))

            metrics = st.multiselect(
                "Select metrics to compare",
                [
                    "cpu_usage",
                    "memory_usage",
                    "disk_usage",
                    "upload_mbps",
                    "download_mbps"
                ],
                default=["cpu_usage", "memory_usage"]
            )

            if metrics:

                fig = px.line(
                    df,
                    x="timestamp_utc",
                    y=metrics,
                    title="Performance Comparison",
                    markers=True
                )

                st.plotly_chart(
                    style_chart(fig, 450),
                    width="stretch"
                )

            a, b = st.columns(2)

            with a:

                fig = px.area(
                    df,
                    x="timestamp_utc",
                    y="upload_mbps",
                    title="Upload Throughput",
                    color_discrete_sequence=["#f59e0b"]
                )

                st.plotly_chart(
                    style_chart(fig),
                    width="stretch"
                )

            with b:

                fig = px.area(
                    df,
                    x="timestamp_utc",
                    y="download_mbps",
                    title="Download Throughput",
                    color_discrete_sequence=["#34d399"]
                )

                st.plotly_chart(
                    style_chart(fig),
                    width="stretch"
                )

    # ======================================
    # V4.5 ALERT ANALYTICS
    # ======================================

    elif page == "Alert Analytics":

        st.markdown("## 📊 Advanced Alert Analytics")
        st.caption("Trends and resolution metrics calculated from the alert records currently returned by the backend.")

        if alerts is None:
            st.error("Alert API unavailable. Check the FastAPI backend.")
        elif not alerts:
            st.info("No alert records are available yet. Analytics will appear when alerts are generated.")
        else:
            alert_df = pd.DataFrame(alerts)

            for column in ["first_seen", "last_seen", "resolved_at"]:
                if column in alert_df.columns:
                    alert_df[column] = pd.to_datetime(alert_df[column], utc=True, errors="coerce")

            # Summary metrics
            total_alert_records = len(alert_df)
            total_occurrences = int(pd.to_numeric(alert_df.get("occurrence_count", 0), errors="coerce").fillna(0).sum())
            critical_count = int((alert_df.get("severity", pd.Series(dtype=str)) == "CRITICAL").sum())
            high_count = int((alert_df.get("severity", pd.Series(dtype=str)) == "HIGH").sum())

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Alert types recorded", total_alert_records)
            m2.metric("Recorded occurrences", total_occurrences)
            m3.metric("Critical alert types", critical_count)
            m4.metric("High alert types", high_count)

            st.divider()
            left, right = st.columns(2)

            with left:
                st.markdown("### 🚨 Alert severity distribution")
                severity_counts = alert_df.groupby("severity").size().reset_index(name="alert_types")
                if not severity_counts.empty:
                    fig = px.pie(severity_counts, names="severity", values="alert_types", hole=0.55)
                    st.plotly_chart(style_chart(fig, 360), width="stretch")

            with right:
                st.markdown("### 🧩 Most frequent alert categories")
                if "metric" in alert_df.columns:
                    category_counts = (alert_df.assign(occurrence_count=pd.to_numeric(alert_df["occurrence_count"], errors="coerce").fillna(0))
                                       .groupby("metric", as_index=False)["occurrence_count"].sum()
                                       .sort_values("occurrence_count", ascending=False))
                    if not category_counts.empty:
                        fig = px.bar(category_counts, x="metric", y="occurrence_count", text="occurrence_count")
                        st.plotly_chart(style_chart(fig, 360), width="stretch")

            st.divider()
            st.markdown("### 📈 Alert activity trend")
            if "last_seen" in alert_df.columns:
                trend = alert_df.dropna(subset=["last_seen"]).copy()
                if not trend.empty:
                    trend["date"] = trend["last_seen"].dt.floor("D")
                    trend_data = trend.groupby("date").size().reset_index(name="alert_types_last_seen")
                    fig = px.line(trend_data, x="date", y="alert_types_last_seen", markers=True,
                                  title="Alert records by last-seen date")
                    st.plotly_chart(style_chart(fig, 350), width="stretch")
                    st.caption("This chart counts alert records by their latest detection date; it is not a count of every individual occurrence.")
                else:
                    st.info("No valid alert timestamps are available for the trend chart.")

            st.divider()
            st.markdown("### ⏱️ Mean time to resolve (MTTR)")
            if "resolved_at" in alert_df.columns and "first_seen" in alert_df.columns:
                resolved_rows = alert_df[
                    (alert_df["status"] == "RESOLVED")
                    & alert_df["resolved_at"].notna()
                    & alert_df["first_seen"].notna()
                ].copy()
                if not resolved_rows.empty:
                    resolved_rows["resolution_minutes"] = (
                        resolved_rows["resolved_at"] - resolved_rows["first_seen"]
                    ).dt.total_seconds() / 60
                    resolved_rows = resolved_rows[resolved_rows["resolution_minutes"] >= 0]
                    if not resolved_rows.empty:
                        mttr = resolved_rows["resolution_minutes"].mean()
                        st.metric("Mean time to resolve", f"{mttr:.1f} minutes", help="Average first-seen to latest resolution duration for resolved alerts with recorded resolution timestamps.")
                        st.dataframe(
                            resolved_rows[["title", "severity", "first_seen", "resolved_at", "resolution_minutes"]]
                            .rename(columns={"resolution_minutes": "Resolution minutes"}),
                            width="stretch",
                            hide_index=True
                        )
                    else:
                        st.info("No valid resolution durations are available yet.")
                else:
                    st.info("MTTR will populate as alerts are resolved after the V4.5 backend is installed. Older resolved alerts do not have resolution timestamps.")
            else:
                st.info("Install the V4.5 backend to record resolution timestamps and calculate MTTR.")

            st.divider()
            st.markdown("### 🖥️ Collector health snapshot")
            collector_rows = collectors or []
            if collector_rows:
                health_df = pd.DataFrame(collector_rows)
                health_counts = health_df.groupby("status").size().reset_index(name="collectors")
                fig = px.bar(health_counts, x="status", y="collectors", text="collectors")
                st.plotly_chart(style_chart(fig, 300), width="stretch")
                st.dataframe(health_df, width="stretch", hide_index=True)
            else:
                st.info("No collector heartbeat records are available.")

    # ======================================
    # EVENT INVESTIGATION
    # ======================================



    # ======================================
    # V4.6 PREDICTIVE INTELLIGENCE
    # ======================================

    elif page == "Predictive Intelligence":

        st.markdown("## 🔮 Predictive Intelligence")
        st.caption("Experimental short-term resource trend estimates from recent collector telemetry.")

        prediction_data = fetch_predictive_summary()

        if prediction_data is None:
            st.error("Predictive API unavailable. Check the V4.6 FastAPI backend.")
        elif not prediction_data.get("results"):
            st.info("Not enough telemetry has been collected yet. Keep the collector running.")
        else:
            st.info(
                "These are transparent trend-based estimates, not trained-model forecasts "
                "or probabilities. They should support investigation, not replace it."
            )

            for result in prediction_data["results"]:
                with st.container(border=True):
                    st.markdown(f"### 🖥️ Collector: {escape(str(result['collector_id']))}")

                    score = result.get("risk_score", 0)
                    level = result.get("risk_level", "UNKNOWN")
                    a, b, c = st.columns(3)
                    a.metric("Operational risk score", f"{score}/100")
                    b.metric("Risk band", level)
                    c.metric("Samples analyzed", result.get("samples_used", 0))

                    risk_gauge = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=max(0, min(100, float(score))),
                        title={"text": "Operational risk score"},
                        gauge={
                            "axis": {"range": [0, 100]},
                            "bar": {"color": "#f59e0b"},
                            "steps": [
                                {"range": [0, 40], "color": "#153b39"},
                                {"range": [40, 70], "color": "#59451f"},
                                {"range": [70, 100], "color": "#542634"},
                            ],
                        },
                    ))
                    risk_gauge.update_layout(
                        template="plotly_dark",
                        height=220,
                        margin=dict(l=20, r=20, t=45, b=10),
                        paper_bgcolor="rgba(0,0,0,0)",
                    )
                    st.plotly_chart(
                        risk_gauge,
                        width="stretch",
                        key=f"risk_gauge_{result['collector_id']}",
                    )

                    metric_rows = []
                    chart_rows = []
                    for key, label in (
                        ("cpu_usage", "CPU"),
                        ("memory_usage", "Memory"),
                        ("disk_usage", "Disk"),
                    ):
                        item = result.get("metrics", {}).get(key, {})
                        current_value = item.get("current")
                        projected_value = item.get("projected")
                        metric_rows.append({
                            "Resource": label,
                            "Current (%)": current_value,
                            "Projected (%)": projected_value,
                            "Trend per sample": item.get("slope_per_sample"),
                        })
                        if current_value is not None:
                            chart_rows.append({
                                "Resource": label,
                                "Stage": "Current",
                                "Usage (%)": current_value,
                            })
                        if projected_value is not None:
                            chart_rows.append({
                                "Resource": label,
                                "Stage": "Projected",
                                "Usage (%)": projected_value,
                            })

                    st.markdown("#### 📈 Current vs short-horizon projection")
                    if chart_rows:
                        projection_df = pd.DataFrame(chart_rows)
                        fig = px.bar(
                            projection_df,
                            x="Resource",
                            y="Usage (%)",
                            color="Stage",
                            barmode="group",
                            text_auto=".1f",
                            title="Resource utilization: current vs projected",
                            color_discrete_map={
                                "Current": "#38bdf8",
                                "Projected": "#f59e0b",
                            },
                        )
                        fig.update_yaxes(range=[0, 100], title="Usage (%)")
                        st.plotly_chart(
                            style_chart(fig, 360),
                            width="stretch",
                            key=f"prediction_chart_{result['collector_id']}",
                        )
                    st.dataframe(
                        pd.DataFrame(metric_rows),
                        width="stretch",
                        hide_index=True
                    )

                    warnings = result.get("early_warnings", [])
                    st.markdown("#### ⚠️ Early warnings")
                    if warnings:
                        for warning in warnings:
                            st.warning(warning)
                    else:
                        st.success("No early-warning conditions were identified in the latest sample window.")

                    st.caption(
                        f"Method: {result.get('method', 'Trend heuristic')} | "
                        f"Latest sample: {result.get('latest_timestamp_utc', 'Unknown')}"
                    )
                    st.caption(result.get("disclaimer", ""))

    elif page == "Event Investigation":

        st.markdown("## 🔎 Security Event Investigation")

        if df.empty:

            st.info("No telemetry records available.")

        else:

            st.markdown("### Recent Telemetry Records")

            columns = [
                "timestamp_utc",
                "collector_id",
                "cpu_usage",
                "memory_usage",
                "disk_usage",
                "upload_mbps",
                "download_mbps",
                "status",
                "severity"
            ]

            available = [
                col for col in columns if col in df.columns
            ]

            st.dataframe(
                df[available].sort_values(
                    "timestamp_utc",
                    ascending=False
                ),
                width="stretch",
                hide_index=True
            )

        st.divider()

        st.markdown("### 🕒 Security Activity Timeline")

        timeline = []

        if not df.empty:

            for _, row in df.tail(20).iterrows():

                timeline.append({
                    "time": row["timestamp_utc"],
                    "event": (
                        f"Telemetry received from "
                        f"{row.get('collector_id', 'unknown collector')}"
                    ),
                    "category": str(row.get("status", "UNKNOWN")),
                    "severity": str(row.get("severity", "INFO"))
                })

        if alerts:

            for alert in alerts:

                timeline.append({
                    "time": pd.to_datetime(
                        alert["last_seen"],
                        utc=True,
                        errors="coerce"
                    ),
                    "event": alert["title"],
                    "category": alert["status"],
                    "severity": alert["severity"]
                })

        if timeline:

            timeline_df = pd.DataFrame(timeline)

            timeline_df = timeline_df.dropna(
                subset=["time"]
            ).sort_values(
                "time",
                ascending=False
            )

            for _, event in timeline_df.head(25).iterrows():

                event_time = event["time"].strftime(
                    "%Y-%m-%d %H:%M:%S UTC"
                )

                st.markdown(
                    f"""
                    <div class="timeline-item">
                        <div style="font-size:11px;color:#8eb5d9;">
                            {event_time}
                        </div>
                        <div style="font-weight:700;color:#ffffff;
                        margin-top:4px;">
                            {escape(str(event['event']))}
                        </div>
                        <div style="font-size:12px;color:#a8c4df;">
                            {escape(str(event['category']))}
                            &nbsp; | &nbsp;
                            {escape(str(event['severity']))}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:

            st.info("No security activity available yet.")

    # ======================================
    # FOOTER
    # ======================================

    st.markdown(
        f"""
        <div class="footer">
            NEXUS GUARD AI FINAL |
            Last refresh:
            {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}
            <br>
            Local AIOps prototype • Monitoring and analytics
        </div>
        """,
        unsafe_allow_html=True
    )


live_dashboard()
