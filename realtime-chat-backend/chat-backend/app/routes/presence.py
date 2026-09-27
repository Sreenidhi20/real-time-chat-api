from typing import Dict, List, Union

from fastapi import APIRouter

from app.core.connection_manager import manager

router = APIRouter(tags=["presence"])


@router.get("/online-users")
def get_online_users() -> Dict[str, List[int]]:
    return {"online_user_ids": manager.online_user_ids()}


@router.get("/online-users/{user_id}")
def check_user_online(user_id: int) -> Dict[str, Union[int, bool]]:
    return {"user_id": user_id, "online": manager.is_online(user_id)}