from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.routes import auth, health, messages, presence, users, ws

app = FastAPI(title="Realtime Chat Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Realtime Chat API is running"}

app.include_router(ws.router)
app.include_router(auth.router)
app.include_router(messages.router)
app.include_router(presence.router)
app.include_router(users.router)
app.include_router(health.router)