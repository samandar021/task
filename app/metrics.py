from prometheus_client import Counter, Histogram

REQUEST_COUNTER = Counter(
    "app_requests_total",
    "Total number of requests by endpoint and method",
    ["endpoint", "method", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Request latency by endpoint",
    ["endpoint", "method"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0),
)

ERROR_COUNTER = Counter(
    "app_errors_total",
    "Total number of server errors",
    ["endpoint", "method"],
)

WARNING_COUNTER = Counter(
    "app_warnings_total",
    "Total number of warning events",
    ["endpoint", "method", "reason"],
)
