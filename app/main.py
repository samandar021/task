import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routes import router
from app.core.middleware import telemetry_middleware
from app.database import Base, SessionLocal, engine
from app.logging_config import configure_logging
from app.services.message import MessageService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize logging, schema, and seed data on startup."""

    configure_logging()
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        MessageService(db).seed_messages()
    yield


app = FastAPI(
    title="Backend Observability Service",
    version="1.0.0",
    description="Backend test assignment: FastAPI + PostgreSQL + Prometheus + Loki + Grafana.",
    openapi_tags=[
        {"name": "Health", "description": "Service liveness endpoint."},
        {"name": "Messages", "description": "Message read operations from PostgreSQL."},
        {"name": "Processing", "description": "Payload processing endpoint."},
        {"name": "Observability", "description": "Prometheus metrics endpoint."},
    ],
    lifespan=lifespan,
)
app.include_router(router)
app.middleware("http")(telemetry_middleware)

instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=False,
    should_respect_env_var=False,
)
instrumentator.instrument(app)


@app.get("/metrics", tags=["Observability"])
def metrics() -> Response:
    """Expose Prometheus metrics for scraping."""

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Return a sanitized 500 response and keep details in logs."""

    logger.error("unhandled_exception", extra={"error": str(exc)})
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
