import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

SERVICES = ["payments-api", "auth-service", "user-service", "notification-svc", "gateway"]

def generate_latency(n, base_p50=120, spike_prob=0.05):
    data = []
    for _ in range(n):
        if random.random() < spike_prob:
            p50 = base_p50 + random.randint(200, 800)
        else:
            p50 = base_p50 + random.randint(-30, 50)
        p95 = p50 * random.uniform(1.8, 2.5)
        p99 = p95 * random.uniform(1.4, 2.0)
        data.append({"p50": round(p50), "p95": round(p95), "p99": round(p99)})
    return data

def generate_metrics(hours=24):
    now = datetime.now()
    timestamps = [now - timedelta(hours=hours - i) for i in range(hours * 12)]  # every 5 min
    records = []
    for ts in timestamps:
        for svc in SERVICES:
            latency = generate_latency(1)[0]
            error_base = 0.5 if svc == "payments-api" else 0.2
            spike = random.random() < 0.03
            error_rate = round(random.uniform(error_base, error_base + (5 if spike else 0.8)), 2)
            throughput = random.randint(800, 3500) if not spike else random.randint(200, 600)
            cpu = round(random.uniform(20, 75) + (20 if spike else 0), 1)
            memory = round(random.uniform(40, 70) + (15 if spike else 0), 1)
            records.append({
                "timestamp": ts,
                "service": svc,
                "latency_p50": latency["p50"],
                "latency_p95": latency["p95"],
                "latency_p99": latency["p99"],
                "error_rate": min(error_rate, 100),
                "throughput": throughput,
                "cpu_pct": min(cpu, 99),
                "memory_pct": min(memory, 99),
            })
    return pd.DataFrame(records)

def generate_incidents(days=30):
    now = datetime.now()
    severities = ["P1", "P2", "P3"]
    weights = [0.1, 0.3, 0.6]
    statuses = ["Resolved", "Resolved", "Resolved", "Open"]
    incident_titles = [
        "High latency on payments-api",
        "Elevated error rate in auth-service",
        "Memory leak in user-service pods",
        "Gateway timeout spike",
        "Database connection pool exhausted",
        "SSL certificate expiry alert",
        "Disk I/O saturation on worker nodes",
        "Notification service queue backlog",
        "Deployment rollback triggered",
        "Upstream dependency degraded",
    ]
    incidents = []
    for i in range(18):
        sev = random.choices(severities, weights=weights)[0]
        start = now - timedelta(days=random.randint(0, days), hours=random.randint(0, 23))
        duration = random.randint(5, 240) if sev == "P1" else random.randint(3, 90)
        status = "Open" if (now - start).total_seconds() < 3600 and random.random() < 0.2 else "Resolved"
        incidents.append({
            "id": f"INC-{1000 + i}",
            "title": random.choice(incident_titles),
            "service": random.choice(SERVICES),
            "severity": sev,
            "started_at": start.strftime("%Y-%m-%d %H:%M"),
            "duration_min": duration,
            "status": status,
            "mttr_min": duration if status == "Resolved" else None,
        })
    return pd.DataFrame(incidents).sort_values("started_at", ascending=False)

def generate_slo():
    rows = []
    for svc in SERVICES:
        target = 99.9
        actual = round(random.uniform(99.2, 99.98), 3)
        error_budget_used = round((target - actual) / (100 - target) * 100, 1)
        rows.append({
            "service": svc,
            "slo_target": target,
            "slo_actual": actual,
            "error_budget_used_pct": min(error_budget_used, 100),
            "status": "Healthy" if actual >= target else ("At Risk" if actual >= 99.5 else "Breached"),
        })
    return pd.DataFrame(rows)

def generate_deployments(days=14):
    now = datetime.now()
    envs = ["production", "staging"]
    results = ["Success", "Success", "Success", "Rollback"]
    records = []
    for i in range(20):
        svc = random.choice(SERVICES)
        ts = now - timedelta(days=random.randint(0, days), hours=random.randint(0, 23))
        result = random.choices(results, weights=[0.8, 0.8, 0.8, 0.1])[0]
        records.append({
            "timestamp": ts.strftime("%Y-%m-%d %H:%M"),
            "service": svc,
            "version": f"v{random.randint(1,5)}.{random.randint(0,9)}.{random.randint(0,20)}",
            "environment": random.choice(envs),
            "result": result,
            "duration_min": random.randint(3, 25),
        })
    return pd.DataFrame(records).sort_values("timestamp", ascending=False)
