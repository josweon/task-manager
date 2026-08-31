# Task Manager API

A task API built as a project to learn backend. The
goal is not just CRUD: this project practices API hygiene, security, and testing
discipline in a small, explainable backend service.

## Project scope

**Stack:** Python, Flask, SQLite, JWT authentication, and pytest.

The API will let authenticated users create, read, update, and delete only their
own tasks. Tasks include a title, description, category, and completion status.

### Core API

- User signup and login, with securely hashed passwords
- JWT-protected task routes
- Create, list, retrieve, update, and delete user-scoped tasks
- Filter a user's tasks by completion status and category
- Consistent validation and error responses (see [Errors](#errors))

### Errors

All errors are returned as JSON.

**Global responses** (applies to every endpoint):

| Status | When it occurs |
|--------|----------------|
| `401` | JWT token missing, invalid, or expired |
| `404` | Route not found, or a malformed task ID |
| `500` | Unexpected server failure |

**`POST /signup`**

| Status | When it occurs |
|--------|----------------|
| `400` | Body is invalid, missing fields, wrong types, empty fields, password shorter than 8, or invalid email |
| `409` | Email already exists |

**`POST /login`**

| Status | When it occurs |
|--------|----------------|
| `400` | Body is invalid, missing fields, wrong types, empty fields, or invalid email |
| `401` | Incorrect credentials |

**`POST /tasks`**

| Status | When it occurs |
|--------|----------------|
| `400` | Body is invalid, missing/blank/non-string title, or duplicate title |

**`PUT /tasks/<id>` · `DELETE /tasks/<id>`**

| Status | When it occurs |
|--------|----------------|
| `400` | Body is invalid, or `completed` missing / not a boolean |
| `404` | Task does not exist or does not belong to the user |

### Quality and security requirements

- Unit tests for business logic, not only successful HTTP responses
- Integration tests against real API endpoints and a separate test database
- Coverage for empty input, duplicate emails, expired tokens, malformed task IDs,
  and attempts to access another user's task
- Rate limiting on the login endpoint (in-memory first; Redis is an optional
  extension)
- Parameterized SQL queries for every database operation

## Delivery checklist

- [x] `GET /health` returns `{"status": "ok"}`

- [x] Basic in-memory `CRUD`routes

- [x] SQLite schema and migrations/setup for `users` and `tasks`

- [x] Full user-scoped task CRUD

- [x] Signup, login, password hashing, and JWT protection

- [x] Input validation and documented error responses

- [x] Login rate limiter

- [ ] Unit and integration test suites using a test database

- [ ] README decision notes and scale trade-offs

## Suggested build sequence

1. Finish in-memory CRUD so each route's behavior is clear.
2. Move tasks to SQLite using parameterized queries.
3. Add users, password hashing, and `user_id` ownership on tasks.
4. Add JWT issuance and protect every task route.
5. Add filters, validation, and precise error handling.
6. Add rate limiting and tests for normal and failure paths.

## Schema decisions

The planned schema separates `users` from `tasks` and links each task with a
`user_id` foreign key. This keeps ownership enforceable at the query layer and
prevents task data from being shared accidentally between accounts. An index on
`tasks.user_id` supports the main access pattern: listing one user's tasks.

## What I would change at scale

SQLite and an in-memory login limiter are appropriate for learning and local
development. At larger scale, I would move to PostgreSQL, run database migrations
as part of deployment, store rate-limit counters in Redis, add pagination to task
listing, and use structured logging and monitoring.

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Definition of done

From a clean checkout, I can create the database, run the full test suite green,
and explain the schema, authentication flow, validation behavior, and at least one
trade-off I would make differently in production.
