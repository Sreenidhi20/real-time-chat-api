from fastapi import Depends, FastAPI, Response
from sqlalchemy.orm import Session

from app.database import check_db_health, get_db

app = FastAPI(title="Realtime Chat Backend")

@app.get("/health")
def health_check(response : Response, db: Session = Depends(get_db)):
    is_alive = check_db_health(db)
    if is_alive:
        return {"status": "UP", "database": "CONNECTED"}
    else:
        response.status_code = 503
        return {"status": "DOWN", "database": "DISCONNECTED"}