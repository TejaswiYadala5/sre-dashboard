import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
from generate_data import (
    generate_metrics, generate_incidents,
    generate_slo, generate_deployments, SERVICES
)

st.set_page_config(
    page_title="SRE Operations Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .metric-card {
    background: #1e1e2e; border-radius: 10px; padding: 16px 20px;
    border-left: 4px solid #7c3aed; margin-bottom: 8px;
  }
  .metric-card.green  { border-left-color: #10b981; }
  .metric-card.red    { border-left-color: #ef4444; }
  .metric-card.yellow { border-left-color: #f59e0b; }
  .metric-value { font-size: 28px; font-weight: 700; color: #f1f5f9; margin: 4px 0; }
  .metric-label { font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
  .metric-delta { font-size: 12px; }
  .section-title { font-size: 18px; font-weight: 600; color: #e2e8f0; margin: 12px 0 8px; }
  .badge-healthy  { background:#10b981; color:#fff; padding:2px 8px; border-radius:12px; font-size:11px; }
  .badge-at-risk  { background:#f59e0b; color:#fff; padding:2px 8px; border-radius:12px; font-size:11px; }
  .badge-breached { background:#ef4444; color:#fff; padding:2px 8px; border-radius:12px; font-size:11px; }
  .badge-open     { background:#ef4444; color:#fff; padding:2px 8px; border-radius:12px; font-size:11px; }
  .badge-resolved { background:#10b981; color:#fff; padding:2px 8px; border-radius:12px; font-size:11px; }
  body { background-color: #0f0f1a; }
</style>
""", unsafe_allow_html=True)

PLOTLY_THEME = dict(
    paper_bgcolor="#1e1e2e",
    plot_bgcolor="#1e1e2e",
    font=dict(color="#e2e8f0", size=11),
    margin=dict(l=40, r=20, t=30, b=30),
)

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.shields.io/badge/SRE-Dashboard-7c3aed?style=for-the-badge", use_container_width=True)
    st.markdown("---")
    st.markdown("### Filters")
    selected_service = st.selectbox("Service", ["All Services"] + SERVICES)
    time_window = st.selectbox("Time Window", ["Last 6 hours", "Last 12 hours", "Last 24 hours"])
    st.markdown("---")
    st.markdown("### Quick Stats")
    st.markdown(f"🕐 **Refreshed:** {datetime.now().strftime('%H:%M:%S')}")
    st.markdown("📍 **Region:** us-east-1")
    st.markdown("🔁 **On-Call:** Tejaswi Yadala")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

hours = {"Last 6 hours": 6, "Last 12 hours": 12, "Last 24 hours": 24}[time_window]

# ── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_all(hrs):
    df_metrics = generate_metrics(hrs)
    df_incidents = generate_incidents()
    df_slo = generate_slo()
    df_deploys = generate_deployments()
    return df_metrics, df_incidents, df_slo, df_deploys

df_metrics, df_incidents, df_slo, df_deploys = load_all(hours)

if selected_service != "All Services":
    df_metrics = df_metrics[df_metrics["service"] == selected_service]
    df_incidents = df_incidents[df_incidents["service"] == selected_service]
    df_slo = df_slo[df_slo["service"] == selected_service]

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("# 🛡️ SRE Operations Dashboard")
st.markdown(f"*{selected_service} · {time_window} · {datetime.now().strftime('%A, %B %d %Y')}*")
st.markdown("---")

# ── Top KPI Cards ─────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

avg_uptime = df_slo["slo_actual"].mean()
open_incidents = len(df_incidents[df_incidents["status"] == "Open"])
avg_error_rate = df_metrics["error_rate"].mean()
avg_p99 = df_metrics["latency_p99"].mean()
avg_throughput = df_metrics["throughput"].mean()

with col1:
    color = "green" if avg_uptime >= 99.9 else ("yellow" if avg_uptime >= 99.5 else "red")
    st.markdown(f"""<div class="metric-card {color}">
        <div class="metric-label">Avg Uptime</div>
        <div class="metric-value">{avg_uptime:.2f}%</div>
        <div class="metric-delta">SLO Target: 99.9%</div>
    </div>""", unsafe_allow_html=True)

with col2:
    color = "red" if open_incidents > 0 else "green"
    st.markdown(f"""<div class="metric-card {color}">
        <div class="metric-label">Open Incidents</div>
        <div class="metric-value">{open_incidents}</div>
        <div class="metric-delta">Total: {len(df_incidents)}</div>
    </div>""", unsafe_allow_html=True)

with col3:
    color = "red" if avg_error_rate > 2 else ("yellow" if avg_error_rate > 1 else "green")
    st.markdown(f"""<div class="metric-card {color}">
        <div class="metric-label">Avg Error Rate</div>
        <div class="metric-value">{avg_error_rate:.2f}%</div>
        <div class="metric-delta">Threshold: 1%</div>
    </div>""", unsafe_allow_html=True)

with col4:
    color = "red" if avg_p99 > 500 else ("yellow" if avg_p99 > 300 else "green")
    st.markdown(f"""<div class="metric-card {color}">
        <div class="metric-label">P99 Latency</div>
        <div class="metric-value">{avg_p99:.0f}ms</div>
        <div class="metric-delta">Threshold: 500ms</div>
    </div>""", unsafe_allow_html=True)

with col5:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">Avg Throughput</div>
        <div class="metric-value">{avg_throughput:.0f}</div>
        <div class="metric-delta">req/s</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── SLO Compliance ─────────────────────────────────────────────────────────
st.markdown('<div class="section-title">SLO Compliance & Error Budget</div>', unsafe_allow_html=True)
col_slo1, col_slo2 = st.columns([1.2, 1])

with col_slo1:
    fig_slo = go.Figure()
    colors = ["#10b981" if s == "Healthy" else ("#f59e0b" if s == "At Risk" else "#ef4444")
              for s in df_slo["status"]]
    fig_slo.add_trace(go.Bar(
        x=df_slo["service"], y=df_slo["slo_actual"],
        marker_color=colors, name="Actual SLO",
        text=[f"{v:.3f}%" for v in df_slo["slo_actual"]], textposition="outside",
    ))
    fig_slo.add_hline(y=99.9, line_dash="dash", line_color="#f59e0b",
                      annotation_text="99.9% Target", annotation_position="top right")
    fig_slo.update_layout(title="SLO Attainment by Service", yaxis_range=[99.0, 100.05],
                          yaxis_title="Uptime %", **PLOTLY_THEME)
    st.plotly_chart(fig_slo, use_container_width=True)

with col_slo2:
    fig_budget = go.Figure()
    budget_colors = ["#10b981" if v < 50 else ("#f59e0b" if v < 80 else "#ef4444")
                     for v in df_slo["error_budget_used_pct"]]
    fig_budget.add_trace(go.Bar(
        x=df_slo["error_budget_used_pct"], y=df_slo["service"],
        orientation="h", marker_color=budget_colors,
        text=[f"{v:.1f}%" for v in df_slo["error_budget_used_pct"]], textposition="outside",
    ))
    fig_budget.add_vline(x=80, line_dash="dash", line_color="#ef4444",
                         annotation_text="Alert 80%")
    fig_budget.update_layout(title="Error Budget Consumed", xaxis_range=[0, 115],
                             xaxis_title="Budget Used %", **PLOTLY_THEME)
    st.plotly_chart(fig_budget, use_container_width=True)

# ── Latency & Error Rate ──────────────────────────────────────────────────
st.markdown('<div class="section-title">Latency & Error Rate Over Time</div>', unsafe_allow_html=True)
col_lat, col_err = st.columns(2)

agg = df_metrics.groupby("timestamp").agg(
    p50=("latency_p50", "mean"),
    p95=("latency_p95", "mean"),
    p99=("latency_p99", "mean"),
    error_rate=("error_rate", "mean"),
).reset_index()

with col_lat:
    fig_lat = go.Figure()
    fig_lat.add_trace(go.Scatter(x=agg["timestamp"], y=agg["p50"], name="P50",
                                  line=dict(color="#10b981", width=1.5)))
    fig_lat.add_trace(go.Scatter(x=agg["timestamp"], y=agg["p95"], name="P95",
                                  line=dict(color="#f59e0b", width=1.5)))
    fig_lat.add_trace(go.Scatter(x=agg["timestamp"], y=agg["p99"], name="P99",
                                  line=dict(color="#ef4444", width=1.5)))
    fig_lat.add_hrect(y0=500, y1=agg["p99"].max() * 1.05,
                      fillcolor="rgba(239,68,68,0.08)", line_width=0, annotation_text="SLO Breach Zone")
    fig_lat.update_layout(title="Latency Percentiles (ms)", yaxis_title="ms", **PLOTLY_THEME)
    st.plotly_chart(fig_lat, use_container_width=True)

with col_err:
    fig_err = go.Figure()
    fig_err.add_trace(go.Scatter(
        x=agg["timestamp"], y=agg["error_rate"],
        fill="tozeroy", fillcolor="rgba(239,68,68,0.15)",
        line=dict(color="#ef4444", width=2), name="Error Rate",
    ))
    fig_err.add_hline(y=1, line_dash="dash", line_color="#f59e0b",
                      annotation_text="Threshold 1%")
    fig_err.update_layout(title="Error Rate (%)", yaxis_title="%", **PLOTLY_THEME)
    st.plotly_chart(fig_err, use_container_width=True)

# ── Throughput & Infrastructure ──────────────────────────────────────────
st.markdown('<div class="section-title">Throughput & Infrastructure Health</div>', unsafe_allow_html=True)
col_thr, col_inf = st.columns(2)

agg2 = df_metrics.groupby(["timestamp", "service"]).agg(
    throughput=("throughput", "mean"),
    cpu=("cpu_pct", "mean"),
    memory=("memory_pct", "mean"),
).reset_index()

with col_thr:
    fig_thr = px.line(agg2, x="timestamp", y="throughput", color="service",
                      title="Throughput by Service (req/s)",
                      color_discrete_sequence=px.colors.qualitative.Bold)
    fig_thr.update_layout(**PLOTLY_THEME)
    st.plotly_chart(fig_thr, use_container_width=True)

with col_inf:
    latest = agg2.sort_values("timestamp").groupby("service").tail(1)
    fig_inf = make_subplots(rows=1, cols=2, subplot_titles=("CPU %", "Memory %"))
    cpu_colors = ["#ef4444" if v > 80 else ("#f59e0b" if v > 60 else "#10b981")
                  for v in latest["cpu"]]
    mem_colors = ["#ef4444" if v > 80 else ("#f59e0b" if v > 60 else "#10b981")
                  for v in latest["memory"]]
    fig_inf.add_trace(go.Bar(x=latest["service"], y=latest["cpu"], marker_color=cpu_colors,
                              name="CPU"), row=1, col=1)
    fig_inf.add_trace(go.Bar(x=latest["service"], y=latest["memory"], marker_color=mem_colors,
                              name="Memory"), row=1, col=2)
    fig_inf.update_layout(title="Current Infrastructure Utilization", showlegend=False, **PLOTLY_THEME)
    st.plotly_chart(fig_inf, use_container_width=True)

# ── Incident Log ──────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Incident Log</div>', unsafe_allow_html=True)
col_inc1, col_inc2 = st.columns([2, 1])

with col_inc1:
    sev_order = {"P1": 0, "P2": 1, "P3": 2}
    df_display = df_incidents.head(10).copy()
    df_display["severity_order"] = df_display["severity"].map(sev_order)
    df_display = df_display.sort_values(["status", "severity_order"])

    def fmt_status(s):
        cls = "badge-open" if s == "Open" else "badge-resolved"
        return f'<span class="{cls}">{s}</span>'

    def fmt_sev(s):
        cls = {"P1": "badge-open", "P2": "badge-at-risk", "P3": "badge-resolved"}[s]
        return f'<span class="{cls}">{s}</span>'

    table_rows = ""
    for _, row in df_display.iterrows():
        mttr = f"{int(row['mttr_min'])} min" if pd.notna(row["mttr_min"]) else "—"
        table_rows += f"""<tr>
            <td style='padding:6px 8px;color:#e2e8f0'>{row['id']}</td>
            <td style='padding:6px 8px;color:#e2e8f0'>{row['title']}</td>
            <td style='padding:6px 8px;color:#94a3b8'>{row['service']}</td>
            <td style='padding:6px 8px'>{fmt_sev(row['severity'])}</td>
            <td style='padding:6px 8px;color:#94a3b8'>{row['started_at']}</td>
            <td style='padding:6px 8px'>{fmt_status(row['status'])}</td>
            <td style='padding:6px 8px;color:#94a3b8'>{mttr}</td>
        </tr>"""

    st.markdown(f"""
    <table style='width:100%;border-collapse:collapse;background:#1e1e2e;border-radius:8px;'>
      <thead>
        <tr style='background:#2d2d3f;'>
          <th style='padding:8px;text-align:left;color:#94a3b8;font-size:11px;'>ID</th>
          <th style='padding:8px;text-align:left;color:#94a3b8;font-size:11px;'>Title</th>
          <th style='padding:8px;text-align:left;color:#94a3b8;font-size:11px;'>Service</th>
          <th style='padding:8px;text-align:left;color:#94a3b8;font-size:11px;'>Sev</th>
          <th style='padding:8px;text-align:left;color:#94a3b8;font-size:11px;'>Started</th>
          <th style='padding:8px;text-align:left;color:#94a3b8;font-size:11px;'>Status</th>
          <th style='padding:8px;text-align:left;color:#94a3b8;font-size:11px;'>MTTR</th>
        </tr>
      </thead>
      <tbody>{table_rows}</tbody>
    </table>
    """, unsafe_allow_html=True)

with col_inc2:
    sev_counts = df_incidents["severity"].value_counts().reset_index()
    fig_sev = px.pie(sev_counts, names="severity", values="count",
                     color="severity",
                     color_discrete_map={"P1": "#ef4444", "P2": "#f59e0b", "P3": "#10b981"},
                     title="Incidents by Severity", hole=0.5)
    fig_sev.update_layout(**PLOTLY_THEME)
    st.plotly_chart(fig_sev, use_container_width=True)

    resolved = df_incidents[df_incidents["mttr_min"].notna()]
    avg_mttr = resolved["mttr_min"].mean()
    st.markdown(f"""<div class="metric-card yellow">
        <div class="metric-label">Avg MTTR</div>
        <div class="metric-value">{avg_mttr:.0f} min</div>
        <div class="metric-delta">Mean Time to Resolve</div>
    </div>""", unsafe_allow_html=True)

# ── Deployment Tracker ────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="section-title">Deployment Tracker (Last 14 Days)</div>', unsafe_allow_html=True)
col_dep1, col_dep2 = st.columns([2, 1])

with col_dep1:
    dep_display = df_deploys.head(8)
    dep_rows = ""
    for _, row in dep_display.iterrows():
        color = "#10b981" if row["result"] == "Success" else "#ef4444"
        icon = "✅" if row["result"] == "Success" else "🔄"
        dep_rows += f"""<tr>
            <td style='padding:6px 8px;color:#e2e8f0'>{row['timestamp']}</td>
            <td style='padding:6px 8px;color:#94a3b8'>{row['service']}</td>
            <td style='padding:6px 8px;color:#7c3aed'>{row['version']}</td>
            <td style='padding:6px 8px;color:#94a3b8'>{row['environment']}</td>
            <td style='padding:6px 8px;color:{color}'>{icon} {row['result']}</td>
            <td style='padding:6px 8px;color:#94a3b8'>{row['duration_min']} min</td>
        </tr>"""
    st.markdown(f"""
    <table style='width:100%;border-collapse:collapse;background:#1e1e2e;border-radius:8px;'>
      <thead>
        <tr style='background:#2d2d3f;'>
          <th style='padding:8px;text-align:left;color:#94a3b8;font-size:11px;'>Time</th>
          <th style='padding:8px;text-align:left;color:#94a3b8;font-size:11px;'>Service</th>
          <th style='padding:8px;text-align:left;color:#94a3b8;font-size:11px;'>Version</th>
          <th style='padding:8px;text-align:left;color:#94a3b8;font-size:11px;'>Env</th>
          <th style='padding:8px;text-align:left;color:#94a3b8;font-size:11px;'>Result</th>
          <th style='padding:8px;text-align:left;color:#94a3b8;font-size:11px;'>Duration</th>
        </tr>
      </thead>
      <tbody>{dep_rows}</tbody>
    </table>
    """, unsafe_allow_html=True)

with col_dep2:
    result_counts = df_deploys["result"].value_counts().reset_index()
    fig_dep = px.pie(result_counts, names="result", values="count", hole=0.5,
                     color="result",
                     color_discrete_map={"Success": "#10b981", "Rollback": "#ef4444"},
                     title="Deployment Success Rate")
    fig_dep.update_layout(**PLOTLY_THEME)
    st.plotly_chart(fig_dep, use_container_width=True)

    success_rate = (df_deploys["result"] == "Success").mean() * 100
    st.markdown(f"""<div class="metric-card {'green' if success_rate >= 90 else 'red'}">
        <div class="metric-label">Deploy Success Rate</div>
        <div class="metric-value">{success_rate:.1f}%</div>
        <div class="metric-delta">Change Failure Rate: {100 - success_rate:.1f}%</div>
    </div>""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#475569;font-size:11px;'>"
    "SRE Operations Dashboard · Built with Streamlit & Plotly · "
    "<a href='https://github.com/tejaswiyadala' style='color:#7c3aed;'>github.com/tejaswiyadala</a>"
    "</p>",
    unsafe_allow_html=True,
)
