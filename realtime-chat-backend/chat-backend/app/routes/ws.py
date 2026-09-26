from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/ws/echo")
async def websocket_echo(websocket: WebSocket):
    # Must accept before you can send/receive — skipping this silently
    # fails the handshake.
    await websocket.accept()
    await websocket.send_text("Connected to chat backend")

    try:
        while True:
            # Blocks until the client sends something. 
            # The loop keeps the connection open — unlike HTTP, we don't return after one message.
            message = await websocket.receive_text()
            await websocket.send_text(f"echo: {message}")
    except WebSocketDisconnect:
        # Client closed the tab / dropped the connection. Later this is where we'll mark the user offline.
        print("Client disconnected")