from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import json

from app.core.connection_manager import manager
from app.database import get_db
from app.services import message_service

router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    await manager.connect(user_id, websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)  # expects {"to": <user_id>, "message": "..."}

            recipient_id = data["to"]
            content = data["message"]

            # Save FIRST, regardless of whether the recipient is online 
            saved = message_service.save_message(db, sender_id=user_id, receiver_id=recipient_id, content=content)

            payload = json.dumps({
                "id": saved.id,
                "from": user_id,
                "message": content,
                "sent_at": saved.sent_at.isoformat(),
            })

            delivered = await manager.send_to_user(recipient_id, payload)

            if not delivered:
                await websocket.send_text(
                    json.dumps({"info": f"User {recipient_id} is offline — message saved, will see it on reconnect"})
                )
    except WebSocketDisconnect:
        manager.disconnect(user_id)
