from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(tags=["users"])


@router.get("/users", response_model=list[UserResponse])
def list_users(exclude: Optional[int] = Query(default=None), db: Session = Depends(get_db)):
    """List users, optionally excluding the current user's ID.

    This endpoint is currently unauthenticated, so anyone can list usernames.
    """
    query = db.query(User)
    if exclude is not None:
        query = query.filter(User.id != exclude)
    return query.order_by(User.username.asc()).all()
