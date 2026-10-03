from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.message import Message


def save_message(db: Session, sender_id: int, receiver_id: int, content: str) -> Message:
    message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_conversation(db: Session, user_id: int, other_user_id: int) -> list[Message]:
    """Returns the full message history between two users, oldest first —
    messages in either direction (A->B and B->A) belong to the same conversation."""
    return (
        db.query(Message)
        .filter(
            or_(
                and_(Message.sender_id == user_id, Message.receiver_id == other_user_id),
                and_(Message.sender_id == other_user_id, Message.receiver_id == user_id),
            )
        )
        .order_by(Message.sent_at.asc())
        .all()
    )