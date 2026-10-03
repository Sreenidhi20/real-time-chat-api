from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.health_service import check_db_health

router = APIRouter(tags=["messages"])


@router.get("/health")
def health_check(response: Response, db: Session = Depends(get_db)) -> dict[str, str]:
    is_healthy = check_db_health(db)
    response.status_code = 200 if is_healthy else 503
    return {
        "status": "UP" if is_healthy else "DOWN",
        "database": "CONNECTED" if is_healthy else "DISCONNECTED",
    }