# Real-Time Chat Backend

This backend powers a real-time one-to-one chat service built with FastAPI, SQLAlchemy, PostgreSQL, and WebSockets.

## What is included

- Secure registration and login using a username/password flow
- Password hashing with `bcrypt`
- JWT-based authentication with Bearer tokens
- Protected user directory and message-history routes
- Live WebSocket chat delivery with presence tracking
- Alembic migrations for schema updates

## Local setup

```powershell
cd chat-backend
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Update `.env`:

```env
DATABASE_URL=postgresql://username:password@host:5432/database_name
JWT_SECRET=super-long-random-secret
```

Then initialize the database and start the API:

```powershell
.\.venv\Scripts\alembic.exe -c alembic.ini upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## Auth flow

1. `POST /register` with JSON like `{ "username": "alice", "password": "StrongPass123!" }`
2. `POST /login` with the same credentials to get a JWT
3. Include the token as `Authorization: Bearer <token>` on protected endpoints
4. Connect to the WebSocket via `ws://localhost:8000/ws?token=<jwt>`

## Notes

- The API validates JWTs before allowing access to users, messages, and presence endpoints.
- Messages are persisted before delivery attempts, so offline recipients still receive stored history after reconnecting.
- Production deployments should use HTTPS/WSS and a secret manager for `JWT_SECRET`.
