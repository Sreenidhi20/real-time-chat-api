from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.message import MessageResponse
from app.services import message_service

router = APIRouter(tags=["messages"])


@router.get("/messages/{user_id}/{other_user_id}", response_model=list[MessageResponse])
def get_conversation(user_id: int, other_user_id: int, db: Session = Depends(get_db)):
    # NOTE: no auth check yet — same caveat as Step 3, user_id is trusted from the URL for now. Real auth (JWT) replaces this later so someone can only fetch their own conversations.
    return message_service.get_conversation(db, user_id, other_user_id)