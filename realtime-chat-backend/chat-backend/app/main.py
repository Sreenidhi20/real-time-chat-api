from fastapi import FastAPI
from app.routes import ws
from app.routes import ws, messages, health

app = FastAPI(title="Realtime Chat Backend")

app.include_router(ws.router)
app.include_router(messages.router)
app.include_router(health.router)