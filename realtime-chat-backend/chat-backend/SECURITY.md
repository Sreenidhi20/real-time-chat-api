# Authentication and Security

## Scope

This document describes the lightweight JWT identity layer currently implemented in this FastAPI chat backend. It demonstrates how an identity is created and passed to a WebSocket connection; it is not a complete user-authentication system.

## Files and responsibilities

### `app/config.py`

Loads values from the backend `.env` using `python-dotenv` and reads:

- `DATABASE_URL`, required by the database layer.
- `JWT_SECRET`, required to sign and verify tokens.
- `ALGORITHM`, currently the fixed value `HS256`.

Importing the configuration raises `RuntimeError` if either required environment value is missing. The secret must be private and strong. Keep the real `.env` out of Git; `.env.example` only documents the required variables and contains placeholder values.

### `app/core/security.py`

This module has two functions:

- `create_access_token(user_id: int) -> str` converts the ID to a string claim named `sub`, sets `exp` to 30 minutes in the future, and signs the claims with PyJWT using `JWT_SECRET` and `HS256`.
- `decode_access_token(token: str) -> dict[str, Any]` verifies the signature and expiration with PyJWT and returns the decoded claims. PyJWT raises its own exceptions, including `ExpiredSignatureError` and `InvalidTokenError`, when verification fails.

The WebSocket route converts the verified `sub` claim back to an integer before using it as the chat user ID.

### `app/models/user.py`

There was no existing user model/table in this project when this layer was added. The new SQLAlchemy model is:

```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, unique=True, index=True)
```

The table stores only an integer primary key and a required username, limited to 100 characters. The username has a unique index, so two rows cannot have the same username. There is no password field.

### `app/routes/auth.py`

Defines the `LoginRequest` Pydantic schema and `POST /login`:

1. Validates a username between 1 and 100 characters and trims surrounding whitespace.
2. Rejects a whitespace-only username with HTTP `400`.
3. Looks up the user by username; if no row exists, inserts and commits a new `User`.
4. Creates a JWT for that row's ID and returns `{"access_token": "...", "user_id": <id>}`.

This endpoint deliberately has no password. Anyone able to call it can claim any username, including a username another person already uses. The token proves only that the server issued a token for that database ID; it does not prove ownership of the username.

### `app/routes/ws.py`

The WebSocket endpoint is now `GET /ws?token=<jwt>` rather than `/ws/{user_id}`. It:

1. Decodes the query token and reads the `sub` claim.
2. Converts `sub` to an integer. Invalid, expired, malformed, or unusable claims are caught and the socket is closed with code `1008`.
3. Calls `manager.connect(user_id, websocket)` only after successful token decoding and ID conversion. An invalid token is not registered as an online user.
4. Uses the token-derived ID as the sender for the existing message-saving and delivery flow.

The database dependency is resolved by FastAPI for the route, but the connection manager is not told about the user until token validation succeeds.

### `app/main.py`, requirements, and migration

`app/main.py` registers the auth router. `requirements.txt` includes PyJWT. The Alembic migration `9c2d7a4e1f63_add_users_table.py` creates the `users` table and its indexes after the existing messages-table migration.

Apply migrations from the `chat-backend` directory before using login on a database that has not already been migrated:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

## Example flow

Request a token:

```http
POST /login
Content-Type: application/json

{"username": "alex"}
```

Example response:

```json
{"access_token": "<jwt>", "user_id": 1}
```

Connect from a browser:

```js
const ws = new WebSocket(
  `ws://localhost:8000/ws?token=${encodeURIComponent(accessToken)}`
);
```

In production, use `wss://` so the token and messages are encrypted in transit.

## Why the token is in the query string

The browser's native `WebSocket` constructor does not provide a way to set arbitrary HTTP headers for the WebSocket handshake. In particular, browser code cannot attach an `Authorization: Bearer ...` header the way it can with `fetch`. A query parameter is therefore used by this implementation to pass the token during connection setup.

Query-string credentials have a tradeoff: URLs may be recorded by reverse proxies, access logs, monitoring, or diagnostics. Do not log full WebSocket request URLs, use TLS (`wss://`) outside local development, and consider short token lifetimes. A first-message authentication protocol or a same-site secure cookie could be alternatives if the deployment needs to avoid query credentials.

## Verification status

The implemented modules were syntax-checked, the application imported with the required settings, JWT creation/decoding was tested, and Alembic recognized the users-table migration. A live end-to-end test with multiple WebSocket clients and explicit malformed/expired-token close-code assertions has not been performed yet; those behaviors should be covered before relying on the feature in production.

## Limitations and production work

This layer does not implement password verification or hashing, account ownership proof, signup abuse controls, rate limiting, token refresh or revocation, logout, role/permission checks, or protection against username impersonation. Add a real identity-verification flow before exposing this login endpoint to untrusted users. Also consider handling concurrent first logins for the same username and database errors in the login route.
