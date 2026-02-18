import re

import pytest

pytestmark = pytest.mark.integration


def _metric_value(metrics_text: str, metric_name: str, labels: str) -> float:
    pattern = rf"^{re.escape(metric_name)}\\{{{re.escape(labels)}\\}}\\s+([0-9.eE+-]+)$"
    match = re.search(pattern, metrics_text, flags=re.MULTILINE)
    assert match is not None, f"Metric sample not found: {metric_name}{{{labels}}}"
    return float(match.group(1))


def test_metrics_endpoint_exposes_custom_metrics(client) -> None:
    client.get("/health")
    client.get("/message/1")
    client.get("/message/11")
    client.post("/process", json={"data": "metrics-check"})

    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")

    body = response.text
    assert "app_requests_total" in body
    assert "app_request_latency_seconds_bucket" in body
    assert "app_errors_total" in body
    assert "app_warnings_total" in body

    health_count = _metric_value(
        body,
        "app_requests_total",
        'endpoint="/health",method="GET",status_code="200"',
    )
    process_count = _metric_value(
        body,
        "app_requests_total",
        'endpoint="/process",method="POST",status_code="200"',
    )

    assert health_count >= 1
    assert process_count >= 1


def test_slow_path_increments_warning_metric(client) -> None:
    client.get("/message/10")
    response = client.get("/metrics")

    assert response.status_code == 200

    warning_count = _metric_value(
        response.text,
        "app_warnings_total",
        'endpoint="/message/10",method="GET",reason="high_latency"',
    )
    assert warning_count >= 1
