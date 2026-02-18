import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.responses import Response

from app.metrics import ERROR_COUNTER, REQUEST_COUNTER, REQUEST_LATENCY, WARNING_COUNTER

logger = logging.getLogger(__name__)


async def telemetry_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Record request-level metrics and structured logs."""

    start = time.perf_counter()
    path = request.url.path
    method = request.method

    try:
        response = await call_next(request)
    except Exception:
        ERROR_COUNTER.labels(endpoint=path, method=method).inc()
        raise

    latency = time.perf_counter() - start
    REQUEST_COUNTER.labels(endpoint=path, method=method, status_code=response.status_code).inc()
    REQUEST_LATENCY.labels(endpoint=path, method=method).observe(latency)

    if response.status_code >= 500:
        ERROR_COUNTER.labels(endpoint=path, method=method).inc()

    if latency > 1.0:
        WARNING_COUNTER.labels(endpoint=path, method=method, reason="high_latency").inc()
        logger.warning(
            "high_latency_detected",
            extra={
                "path": path,
                "method": method,
                "status_code": response.status_code,
                "latency_ms": round(latency * 1000, 2),
            },
        )

    logger.info(
        "request_completed",
        extra={
            "path": path,
            "method": method,
            "status_code": response.status_code,
            "latency_ms": round(latency * 1000, 2),
        },
    )
    return response
