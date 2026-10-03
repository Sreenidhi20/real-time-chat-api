from typing import Dict, List, Union

from fastapi import APIRouter, Depends

from app.core.auth_dependencies import get_current_user
from app.core.connection_manager import manager
from app.models.user import User

router = APIRouter(tags=["presence"])


@router.get("/online-users")
def get_online_users(current_user: User = Depends(get_current_user)) -> Dict[str, List[int]]:
    return {"online_user_ids": manager.online_user_ids()}


@router.get("/online-users/{user_id}")
def check_user_online(
    user_id: int,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Union[int, bool]]:
    return {"user_id": user_id, "online": manager.is_online(user_id)}