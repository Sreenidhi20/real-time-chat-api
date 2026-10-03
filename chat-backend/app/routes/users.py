from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(tags=["users"])


@router.get("/users", response_model=list[UserResponse])
def list_users(
    exclude: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List users, optionally excluding a user ID, while requiring a valid JWT."""
    query = db.query(User).filter(User.id != current_user.id)
    if exclude is not None:
        query = query.filter(User.id != exclude)
    return query.order_by(User.username.asc()).all()
