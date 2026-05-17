# 🛡️ SRE Operations Dashboard

A production-grade **Site Reliability Engineering dashboard** built with Python, Streamlit, and Plotly. Simulates real-world SRE monitoring across multiple microservices — the kind of observability tooling used by SRE teams at companies like Visa, AWS, and Google.

## 📊 Dashboard Features

| Section | Metrics |
|---|---|
| **KPI Overview** | Uptime %, Open Incidents, Error Rate, P99 Latency, Throughput |
| **SLO Compliance** | SLO attainment vs. 99.9% target, error budget consumed |
| **Latency Analysis** | P50 / P95 / P99 percentiles over time, SLO breach zone |
| **Error Rate** | Time-series error % with threshold alerting |
| **Throughput** | Requests/sec per service over time |
| **Infrastructure** | CPU % and Memory % utilization per service |
| **Incident Log** | Severity (P1/P2/P3), MTTR, status tracking |
| **Deployment Tracker** | Version, environment, success/rollback, change failure rate |

## 🛠️ Tech Stack

- **Python** — core logic and data simulation
- **Streamlit** — interactive web dashboard
- **Plotly** — charts and visualizations
- **Pandas / NumPy** — data processing

## 🚀 Run Locally

```bash
# Clone the repo
git clone https://github.com/tejaswiyadala/sre-dashboard.git
cd sre-dashboard

# Install dependencies
pip install -r requirements.txt

# Launch the dashboard
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`

## 📐 SRE Concepts Demonstrated

- **SLO/SLA Monitoring** — tracking service-level objectives against targets
- **Error Budget** — measuring how much reliability margin remains
- **Golden Signals** — latency, traffic, errors, saturation (Google SRE book)
- **MTTR Tracking** — mean time to resolution for incidents
- **Deployment Reliability** — change failure rate and rollback detection
- **Proactive Alerting** — visual thresholds for P99 latency and error rate
- **Multi-service Observability** — payments-api, auth-service, user-service, gateway

## 🖼️ Dashboard Preview

> Dark-themed, real-time-style operations dashboard with sidebar filters for service and time window.

## 📁 Project Structure

```
sre-dashboard/
├── app.py              # Main Streamlit dashboard
├── generate_data.py    # Simulated metrics, incidents, SLO, deployment data
├── requirements.txt    # Python dependencies
└── README.md
```

---

Built by [Tejaswi Yadala](https://www.linkedin.com/in/tejaswi-y-82068b205/) · [GitHub](https://github.com/tejaswiyadala)
