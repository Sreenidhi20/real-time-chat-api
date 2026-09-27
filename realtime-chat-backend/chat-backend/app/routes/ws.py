import json

import jwt
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.connection_manager import manager
from app.core.security import decode_access_token
from app.database import get_db
from app.services import message_service

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db),
) -> None:
    try:
        claims = decode_access_token(token)
        user_id = int(claims["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        await websocket.close(code=1008)
        return

    await manager.connect(user_id, websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)  # expects {"to": <user_id>, "message": "..."}

            recipient_id = data["to"]
            content = data["message"]

            # Save first, regardless of whether the recipient is online.
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
