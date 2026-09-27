from typing import Dict, Union

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.database import get_db
from app.models.user import User

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Dict[str, Union[int, str]]:
    username = payload.username.strip()
    if not username:
        raise HTTPException(status_code=400, detail="Username cannot be blank")

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        user = User(username=username)
        db.add(user)
        db.commit()
        db.refresh(user)

    return {
        "access_token": create_access_token(user.id),
        "user_id": user.id,
    }
