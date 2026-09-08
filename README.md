# Django Chat App

A personal learning project exploring real-time messaging with Django Channels and Redis.

## What the source includes

- Room chat with WebSocket group broadcasts and saved message history.
- Direct messaging with attachment support and online-status tracking.
- Registration and login pages with Django session integration.
- An experimental multiplayer question-and-answer game.

## Stack and structure

The project configures Django, Django REST Framework, Channels, Daphne, Redis for channel groups and caching, and SQLite for persistence. Application code lives inside `real_time_chat/`.

| Source | Responsibility |
| --- | --- |
| [ASGI application](real_time_chat/real_time_chat/asgi.py) | HTTP and WebSocket routing; session middleware |
| [Consumers](real_time_chat/chat_app/consumers.py) | Room messages, direct messages and game events |
| [Models](real_time_chat/chat_app/models.py) | Rooms, messages, attachments and game sessions |
| [Views and HTTP routes](real_time_chat/chat_app/urls.py) | Registration, login and chat pages |
| [Settings](real_time_chat/real_time_chat/settings.py) | Redis, SQLite and installed applications |

The ASGI application declares these WebSocket paths:

- `/ws/chat/<room_name>/`
- `/ws/dm/<user_id>/`
- `/ws/game/<game_id>/`

## Development status

This is a prototype. The repository currently has no dependency manifest or verified installation instructions. Redis is configured at `127.0.0.1:6379`; database migrations are included.

Session middleware provides user identity, but WebSocket authentication and authorization checks still need work. The test module is a placeholder. Reproducible setup, access-control checks and automated tests are the next improvements before deployment.
