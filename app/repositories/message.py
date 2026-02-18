from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Message


class MessageRepository:
    """Data access for Message entities."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, message_id: int) -> Message | None:
        return self.db.scalar(select(Message).where(Message.id == message_id))

    def count(self) -> int:
        return int(self.db.scalar(select(func.count()).select_from(Message)) or 0)

    def add_many(self, start_id: int, end_id: int) -> None:
        for idx in range(start_id, end_id + 1):
            self.db.add(Message(id=idx, text=f"Mock message #{idx}"))
        self.db.commit()
