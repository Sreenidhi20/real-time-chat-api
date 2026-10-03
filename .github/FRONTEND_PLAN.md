# Frontend Integration Plan

This document explains what the backend exposes so a frontend can be built around the real API behavior.

## 1. Product overview

The backend is a real-time one-to-one chat platform. Users register with a username and password, receive a JWT, and then use that token to:

- list available users
- fetch chat history with another user
- connect to the WebSocket and send/receive messages in real time
- check whether a contact is online

The design is intentionally simple: a user can chat with any other registered user after authentication.

## 2. Authentication flow

### Register a new user

Endpoint:

- POST /register

Request body:

```json
{
  "username": "alice",
  "password": "StrongPass123!"
}
```

Response:

```json
{
  "id": 1,
  "username": "alice"
}
```

### Login

Endpoint:

- POST /login

Request body:

```json
{
  "username": "alice",
  "password": "StrongPass123!"
}
```

Response:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user_id": 1
}
```

Frontend responsibility:

- store the JWT in local storage or memory
- send it as `Authorization: Bearer <token>` on protected requests
- redirect to the dashboard after successful login

## 3. Protected endpoints

### List users

Endpoint:

- GET /users

Headers:

```http
Authorization: Bearer <jwt>
```

Response:

```json
[
  {
    "id": 2,
    "username": "bob"
  },
  {
    "id": 3,
    "username": "charlie"
  }
]
```

Use case:

- show a contact list on the left side of the UI
- exclude the currently signed-in user from the list

### Get conversation history

Endpoint:

- GET /messages/{user_id}/{other_user_id}

Example:

```http
GET /messages/1/2
Authorization: Bearer <jwt>
```

Response:

```json
[
  {
    "id": 10,
    "sender_id": 1,
    "receiver_id": 2,
    "content": "Hello there",
    "sent_at": "2026-10-03T12:00:00"
  }
]
```

Use case:

- load the chat thread when a user clicks another contact
- render messages left/right based on sender identity

### Online users

Endpoint:

- GET /online-users

Response:

```json
{
  "online_user_ids": [2, 5]
}
```

Use case:

- show online/offline badges next to contacts

## 4. WebSocket real-time channel

Endpoint:

- WS /ws?token=<jwt>

Message format sent by the client to the server:

```json
{
  "to": 2,
  "message": "Hi Bob!"
}
```

Message format sent by the server to the client:

```json
{
  "id": 15,
  "from": 1,
  "message": "Hi Bob!",
  "sent_at": "2026-10-03T12:05:00"
}
```

If a recipient is offline, the backend saves the message and replies with an informational message instead of failing silently.

Use case:

- keep a single persistent socket connection for the authenticated user
- push incoming messages instantly into the chat UI
- maintain a live conversation list without polling

## 5. Suggested frontend state model

The frontend can keep these states:

- `auth`: token, user id, login status
- `users`: contact list from /users
- `selectedChatUser`: currently opened contact
- `messagesByUser`: map of user id to message array
- `onlineUsers`: set of online ids
- `socketStatus`: connected, reconnecting, disconnected

## 6. Suggested UI screens

### Login screen

- username input
- password input
- submit button
- validation and error message display

### Dashboard screen

- left sidebar: user list
- top bar: current user name and logout button
- center pane: active conversation
- bottom composer: message input and send button

### Presence and status

- show contact online/offline status
- highlight active chat conversation
- optionally show unread count

## 7. Recommended implementation order

1. build auth screens and token storage
2. fetch users and render the contact list
3. load current conversation history when a user is selected
4. connect the WebSocket after login
5. display live incoming messages and send outgoing messages
6. add online status and typing/idle polish later

## 8. Notes for the UI team

- All protected endpoints require a valid JWT.
- The backend uses username-based login and not email-based auth.
- The API currently follows a straightforward JSON contract; no complex pagination or RBAC is implemented yet.
- WebSocket messages are not automatically broadcast to all users; they are targeted to a specific recipient user ID.
