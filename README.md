# Real-Time Chat Backend

A FastAPI backend for one-to-one chat. HTTP endpoints handle login, health, user discovery, and message history. A WebSocket connection carries live chat messages in both directions over one long-lived connection.

## WebSocket role and request flow

HTTP is used for requests that start and finish independently, such as login or loading conversation history. Chat needs a continuous, low-latency path: after a WebSocket handshake succeeds, the same connection remains open so either side can send data without opening a new HTTP request for every message.

The sender's identity is taken from a signed JWT, not from a user ID in the WebSocket URL. First call `POST /login` to get a token. Then connect to `/ws?token=<access_token>`. The browser's built-in `WebSocket` API cannot set arbitrary handshake headers, which is why this implementation sends the token as a query parameter.

```mermaid
sequenceDiagram
		autonumber
		actor Sender as Sender browser
		participant API as FastAPI backend
		participant JWT as JWT validation
		participant Connections as Connection manager
		participant DB as PostgreSQL
		actor Recipient as Recipient browser

		Sender->>API: POST /login with username
		API->>DB: Find user or create user
		DB-->>API: User ID
		API-->>Sender: access_token and user_id

		Note over Recipient,API: Recipient logs in and opens its own authenticated WebSocket in the same way
		Sender->>API: WebSocket handshake /ws?token=...
		API->>JWT: Verify signature and expiration
		alt Token invalid or expired
				API-->>Sender: Close with code 1008
		else Token valid
				JWT-->>API: Verified user ID from sub claim
				API->>Connections: Accept socket and register user ID
				API-->>Sender: WebSocket connection is open
				loop For each message while connected
						Sender->>API: {"to": recipient_id, "message": content}
						API->>DB: Save message first
						DB-->>API: Saved message ID and timestamp
						API->>Connections: Send message to recipient ID
						alt Recipient is connected
								Connections-->>Recipient: {"id", "from", "message", "sent_at"}
						else Recipient is offline
								API-->>Sender: Message saved, recipient is offline
						end
				end
				Sender-->>API: Close connection or disconnect
				API->>Connections: Remove sender from online connections
		end
```

### WebSocket message format

Send a JSON text frame with a recipient ID and message text:

```json
{ "to": 2, "message": "Hello!" }
```

The backend persists the message before attempting delivery. When the recipient is connected, the recipient gets:

```json
{
  "id": 42,
  "from": 1,
  "message": "Hello!",
  "sent_at": "2026-09-27T12:34:56+00:00"
}
```

When the recipient is offline, the message is still saved and the sender gets an informational frame. The recipient can retrieve saved conversation history later through the messages endpoint.

On a normal disconnect, the connection is removed from the in-memory online-user map. Invalid, malformed, or expired tokens are closed with WebSocket code `1008` before the connection is registered. The connection manager is in-memory and process-local, so online presence and direct delivery do not coordinate across multiple backend workers or instances.

### Browser connection example

```js
const ws = new WebSocket(
  `ws://localhost:8000/ws?token=${encodeURIComponent(accessToken)}`,
);

ws.onopen = () => {
  ws.send(JSON.stringify({ to: recipientUserId, message: "Hello!" }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log(message);
};
```

Use `wss://` in production. Query-string tokens may be captured in proxy, server, and monitoring logs; do not log full WebSocket request URLs. The current implementation does not add heartbeat/ping management, client reconnection, or cross-instance message routing.

## Prerequisites

- Python 3.12
- PostgreSQL
- A generated JWT signing secret

## Local setup

Run these commands from the repository root in PowerShell:

```powershell
cd realtime-chat-backend\chat-backend
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set a valid PostgreSQL URL and a private JWT secret. Generate a strong secret with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Example environment variable names (replace the example values):

```env
DATABASE_URL=postgresql://username:password@host:5432/database_name
JWT_SECRET=use-a-generated-random-value
```

Keep `.env` private and out of Git. `JWT_SECRET` must be configured before starting the app or running Alembic because application configuration requires it at import time.

Apply database migrations and start the development server:

```powershell
.\.venv\Scripts\alembic.exe -c alembic.ini upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`; interactive OpenAPI documentation is at `http://localhost:8000/docs`.

## HTTP endpoints

| Method    | Endpoint                              | Purpose                                                                                |
| --------- | ------------------------------------- | -------------------------------------------------------------------------------------- |
| `POST`    | `/login`                              | Find or create a username and return a 30-minute JWT. This demo login has no password. |
| `GET`     | `/health`                             | Check API and database availability. Returns `503` if the database check fails.        |
| `GET`     | `/users`                              | List users ordered by username.                                                        |
| `GET`     | `/users?exclude=1`                    | List users except the supplied user ID.                                                |
| `GET`     | `/messages/{user_id}/{other_user_id}` | Get the conversation in either direction, oldest first.                                |
| WebSocket | `/ws?token=<jwt>`                     | Authenticate a user and exchange live chat messages.                                   |
| `GET`     | `/online-users`                       | Return IDs currently connected to this process.                                        |
| `GET`     | `/online-users/{user_id}`             | Check whether a user is connected to this process.                                     |

### Login request

```http
POST /login
Content-Type: application/json

{"username": "alex"}
```

The response contains `access_token` and `user_id`. A repeated request with the same username returns the existing user.

## Security limitations

The login endpoint accepts only a username and does not verify account ownership. Anyone can claim a username and receive a token for that user. The users list, message history, and presence endpoints are also currently unauthenticated. This is suitable only as a lightweight demo; add real identity verification and authorization before exposing it to untrusted users. See [`chat-backend/SECURITY.md`](chat-backend/SECURITY.md) for the authentication details.
