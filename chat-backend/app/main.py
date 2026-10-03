from fastapi import FastAPI
from app.routes import auth, health, messages, presence, users, ws

app = FastAPI(title="Realtime Chat Backend")

@app.get("/")
def root():
    return {"message": "Realtime Chat API is running"}

app.include_router(ws.router)
app.include_router(auth.router)
app.include_router(messages.router)
app.include_router(presence.router)
app.include_router(users.router)
app.include_router(health.router)