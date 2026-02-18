import time

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.message import MessageRepository
from app.schemas import MessageResponse


class MessageService:
    """Application logic for message read operations and seed."""

    def __init__(self, db: Session) -> None:
        self.repository = MessageRepository(db)

    def seed_messages(self) -> None:
        existing_count = self.repository.count()
        if existing_count >= 10:
            return
        self.repository.add_many(existing_count + 1, 10)

    def get_message(self, message_id: int) -> MessageResponse:
        if message_id == 10:
            # Simulated bottleneck for observability demonstration.
            time.sleep(1.2)

        message = self.repository.get_by_id(message_id)
        if message is None:
            raise HTTPException(status_code=404, detail="Message not found")
        return MessageResponse(id=message.id, text=message.text)
