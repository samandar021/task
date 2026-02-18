# FastAPI Observability Test Project

## Submission Summary
- Assignment scope completed: backend API + observability + containerized local stack.
- FastAPI endpoints implemented: `GET /health`, `GET /message/{id}`, `POST /process`, `GET /metrics`.
- Database layer: SQLAlchemy + PostgreSQL with startup seed of 10 mock messages.
- Metrics/logs: Prometheus instrumentation + custom app metrics + structured JSON logs.
- Observability stack: Prometheus, Node Exporter, Loki, Promtail, Grafana with provisioning.
- Grafana dashboard JSON export included: `grafana/dashboards/observability-dashboard.json`.
- Bottleneck simulation included (`/message/10` slow path) with detection guidance in this README.
- Prometheus alert rule included: high latency (`p95 > 1s`) in `prometheus/alerts.yml`.
- Test coverage included: unit endpoint tests + integration metrics tests.
- Docker-first run flow documented with environment files for portable local setup.

This project demonstrates a FastAPI backend service with a full observability stack:
- API + PostgreSQL (SQLAlchemy)
- Prometheus metrics (including custom Counter/Histogram)
- Node Exporter system metrics
- Structured JSON logging
- Loki + Promtail for log aggregation
- Grafana dashboard provisioning
- Pytest unit/integration tests

## Stack
- Python 3.11 (compatible with the 3.10+ requirement)
- FastAPI
- SQLAlchemy + PostgreSQL
- Prometheus + Node Exporter
- Loki + Promtail
- Grafana
- Docker Compose

## Endpoints
- `GET /health` -> `{"status":"healthy"}`
- `GET /message/{id}` -> returns a message from the `messages` table
- `POST /process` -> accepts `{"data": "..."}`, simulates processing for ~0.5s
- `GET /metrics` -> Prometheus metrics endpoint

## Observability Implementation
- FastAPI auto-instrumentation via `prometheus-fastapi-instrumentator`
- Custom metrics:
  - `app_requests_total{endpoint,method,status_code}`
  - `app_request_latency_seconds_bucket{endpoint,method}`
  - `app_errors_total{endpoint,method}`
  - `app_warnings_total{endpoint,method,reason}`
- Structured JSON logs to stdout and `/app/logs/app.log`
- Promtail reads `/var/log/app/*.log` and pushes logs to Loki
- Grafana provisions datasources and dashboard from repository files

## Bottleneck Simulation
In `GET /message/{id}`, request `id=10` intentionally uses `sleep(1.2)` to simulate a slow path.
This is used to demonstrate latency degradation detection in p95 and warning metric increments.

Useful Prometheus queries:
- RPS: `sum(rate(app_requests_total[1m]))`
- p95 latency: `histogram_quantile(0.95, sum(rate(app_request_latency_seconds_bucket[2m])) by (le))`
- Errors: `sum(app_errors_total)`
- Warnings: `sum(app_warnings_total)`

## Alert Rule
Configured alert: `HighRequestLatency`
- Condition: `p95 > 1s`
- For: 1 minute
- File: `prometheus/alerts.yml`

## Seed Data
On startup, the app creates the `messages` table and seeds at least 10 mock messages.

## Local Run
This repository includes default service env files:
- `env/app.env`
- `env/db.env`
- `env/grafana.env`

If you want custom values, edit those files directly. `.env.example` shows all expected variables.

```bash
docker compose up --build -d
docker compose ps
```

Services:
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Loki: http://localhost:3100
- Node Exporter: http://localhost:9100/metrics

Grafana credentials (from `env/grafana.env` by default):
- Username: `admin`
- Password: `admin`

## End-to-End Verification Order
1. Start stack
```bash
docker compose up --build -d
docker compose ps
```
2. Verify API endpoints
```bash
curl -i http://localhost:8000/health
curl -i http://localhost:8000/message/1
curl -i http://localhost:8000/message/10
curl -i -X POST http://localhost:8000/process -H "Content-Type: application/json" -d '{"data":"hello"}'
```
3. Verify custom metrics
```bash
curl -s http://localhost:8000/metrics | grep -E "app_requests_total|app_request_latency_seconds|app_errors_total|app_warnings_total"
```
4. Verify Prometheus targets and queries
- Open `http://localhost:9090/targets` and confirm `UP` for app + node-exporter.
- Example query: `sum(rate(app_requests_total[1m]))`
- Example query: `histogram_quantile(0.95, sum(rate(app_request_latency_seconds_bucket[2m])) by (le))`
5. Verify Grafana dashboard
- Login at `http://localhost:3000` with credentials above.
- Open dashboard: `FastAPI Observability Overview` (auto-provisioned).
- Confirm panels: RPS, p95 latency, CPU, memory, errors, warnings, logs.
6. Verify logs in Loki
- In Grafana Explore, select Loki datasource and run:
  - `{job="app"}`
7. Stop stack when finished
```bash
docker compose down
```

## Tests
Local run (without Docker):
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

Run by test level:
```bash
pytest -m unit -q
pytest -m integration -q
```

## Style and Lint
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
ruff check .
black --check .
```

Coverage includes:
- Unit (`tests/unit/test_endpoints.py`):
  - endpoint status/body validation
  - input validation and not-found behavior
  - latency simulation check for `/process`
- Integration (`tests/integration/test_metrics.py`):
  - `/metrics` format and custom metric exposure
  - request counter sample checks after generated traffic
  - warning metric increment check for slow path (`/message/10`)

## Key Files
- `app/main.py` - API bootstrap, middleware wiring, startup lifecycle
- `app/api/routes.py` - route handlers
- `app/services/` - business logic layer
- `app/repositories/` - data access layer
- `app/core/middleware.py` - request telemetry middleware
- `app/metrics.py` - custom Prometheus metrics
- `app/logging_config.py` - structured JSON logging
- `docker-compose.yml` - full local infrastructure
- `env/app.env` - FastAPI container variables
- `env/db.env` - PostgreSQL container variables
- `env/grafana.env` - Grafana container variables
- `.env.example` - complete variable template
- `prometheus/prometheus.yml` - scrape configuration
- `prometheus/alerts.yml` - alert rules
- `grafana/dashboards/observability-dashboard.json` - dashboard JSON export

## Trade-offs
- Synchronous SQLAlchemy is used for simplicity and clarity in this test task.
- Logs are collected from a shared volume file for stable local ingestion.
- Bottleneck is intentionally simulated (`sleep`) to make observability behavior reproducible.
