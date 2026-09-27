from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.message import MessageResponse
from app.services import message_service

router = APIRouter(tags=["messages"])


@router.get("/messages/{user_id}/{other_user_id}", response_model=list[MessageResponse])
def get_conversation(user_id: int, other_user_id: int, db: Session = Depends(get_db)):
    #NOTE: no auth check yet — I have to wire the JWT auuth on further work. For now, this is just a simple endpoint to fetch the conversation between two users.
    return message_service.get_conversation(db, user_id, other_user_id)