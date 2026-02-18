from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import MessageResponse, ProcessRequest, ProcessResponse
from app.services.message import MessageService
from app.services.process import ProcessService

router = APIRouter()


@router.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    """Liveness endpoint for probes and smoke checks."""

    return {"status": "healthy"}


@router.get("/message/{id}", response_model=MessageResponse, tags=["Messages"])
def get_message(
    id: int = Path(..., ge=1, le=100000),
    db: Session = Depends(get_db),
) -> MessageResponse:
    """Return a message by id from the database."""

    return MessageService(db).get_message(id)


@router.post("/process", response_model=ProcessResponse, tags=["Processing"])
def process(payload: ProcessRequest) -> ProcessResponse:
    """Validate input and simulate a medium-latency processing step."""

    return ProcessService.process(payload)
