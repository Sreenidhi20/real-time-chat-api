# Real-Time Chat API

This repository contains a production-oriented FastAPI backend for real-time one-to-one messaging. The project is organized around an authenticated chat flow: users register and log in with a password, receive a JWT, and then use that token for protected user lookup, conversation history, and live WebSocket messaging.

## Repository layout

- `chat-backend/` — active backend project
- `chat-backend/app/` — FastAPI app, routes, models, schemas, and services
- `chat-backend/alembic/` — database migrations
- `chat-backend/tests/` — regression tests for auth and API security
- `FRONTEND_PLAN.md` — API contract and frontend integration plan

## Core features

- Password-based registration and login
- JWT-based auth via `Authorization: Bearer <token>`
- Protected user listing, message retrieval, and presence endpoints
- WebSocket authentication with token validation and connection tracking
- Offline message persistence before delivery to active recipients

## Quick start

```powershell
cd chat-backend
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set environment values in `.env`:

```env
DATABASE_URL=postgresql://username:password@host:5432/database_name
JWT_SECRET=replace-with-a-long-random-secret
```

Then run the app:

```powershell
.\.venv\Scripts\alembic.exe -c alembic.ini upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000` and the Swagger UI is at `http://localhost:8000/docs`.

## Main endpoints

- `POST /register` — create a user with a username and password
- `POST /login` — authenticate and receive an access token
- `GET /users` — list other users while excluding the authenticated user
- `GET /messages/{user_id}/{other_user_id}` — fetch chat history for the authenticated user
- `GET /online-users` — see currently connected user IDs
- `WS /ws?token=<jwt>` — send and receive live chat messages

## Security notes

- Passwords are hashed with `bcrypt` before storage.
- JWTs are required for user lookup and message access.
- WebSocket clients must provide a valid token in the query string.
- Production deployments should keep `JWT_SECRET` in a secure secret manager and use HTTPS/WSS.
