import time

from app.schemas import ProcessRequest, ProcessResponse


class ProcessService:
    """Application logic for payload processing endpoint."""

    @staticmethod
    def process(payload: ProcessRequest) -> ProcessResponse:
        time.sleep(0.5)
        return ProcessResponse(processed=payload.data)
