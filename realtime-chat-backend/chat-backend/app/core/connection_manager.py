from fastapi import WebSocket


class ConnectionManager:
    """Tracks currently-connected users and lets you send a message to a
    specific user by id, or broadcast to everyone."""

    def __init__(self):
        # user_id -> WebSocket. In-memory only — resets if the server restarts, and won't work across multiple server instances without something like Redis
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)

    async def send_to_user(self, user_id: int, message: str) -> bool:
        """Returns True if the user was online and the message was sent,
        False if they weren't connected (caller should persist to DB instead)."""
        connection = self.active_connections.get(user_id)
        if connection is None:
            return False
        await connection.send_text(message)
        return True

    def is_online(self, user_id: int) -> bool:
        return user_id in self.active_connections

    def online_user_ids(self) -> list[int]:
        return list(self.active_connections.keys())


# Single shared instance — every route imports this same object, so they're all looking at the same set of active connections.
manager = ConnectionManager()
