from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)

    async def send_to_user(self, user_id: int, message: str) -> bool:
        connection = self.active_connections.get(user_id)
        if connection is None:
            return False
        await connection.send_text(message)
        return True

    def is_online(self, user_id: int) -> bool:
        return user_id in self.active_connections

    def online_user_ids(self) -> list[int]:
        return list(self.active_connections.keys())


manager = ConnectionManager()
