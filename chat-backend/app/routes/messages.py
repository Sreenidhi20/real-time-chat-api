from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.message import MessageResponse
from app.services import message_service

router = APIRouter(tags=["messages"])


@router.get("/messages/{user_id}/{other_user_id}", response_model=list[MessageResponse])
def get_conversation(
    user_id: int,
    other_user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="You can only fetch your own chat history")

    return message_service.get_conversation(db, user_id, other_user_id)