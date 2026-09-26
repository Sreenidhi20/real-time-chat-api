from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

from app.core.connection_manager import manager

router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    # NOTE: taking user_id straight from the URL is not secure in a real app.
    await manager.connect(user_id, websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)  # expects {"to": <user_id>, "message": "..."}

            recipient_id = data["to"]
            message = data["message"]

            delivered = await manager.send_to_user(
                recipient_id,
                json.dumps({"from": user_id, "message": message}),
            )

            if not delivered:
                # Recipient isn't online right now. This is exactly where,in the next step, we'd save the message to Postgres instead of silently dropping it.
                await websocket.send_text(
                    json.dumps({"info": f"User {recipient_id} is offline, message not delivered"})
                )
    except WebSocketDisconnect:
        manager.disconnect(user_id)
