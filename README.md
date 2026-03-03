# Office Hours API (FastAPI)

Lightweight API for office-hours triage with role-based auth.

## Data Flow

1. Student submits a help request (`/student/request`) and enters the arrival queue.
2. Staff runs triage (`/staff/triage`) to move students into skill-based priority queues.
3. TA claims the next student (`/ta/claim`) by priority + skill match.
4. TA completes session (`/ta/complete`), and the system updates queue/TA state.

Priority rules:
- In a skill queue, higher severity is helped first.
- If severity ties, earlier arrival time is helped first.
- Priority is evaluated within each skill queue (not globally across all skills).
- For TA claim, `preferred_skill` is checked first; otherwise skills are checked in TA skill-list order.

## Quick Start 

1. From the API folder:
   ```bash
   cd Office-Hours/api
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start server:
   ```bash
   python main.py
   ```
   Or:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## Docs & Health

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health: `http://localhost:8000/health`

## Default Accounts (for local dev)

- Staff: `admin` / `admin123`
- TA: `ta_demo` / `ta123456`
- Student: `student_demo` / `student123`

Change these for production.

## Core Endpoints

### Public
- `POST /student/request` — submit a help request
- `GET /student/{student_id}` — fetch student request status
- `GET /stats` — system stats
- `GET /health` — health check

### Authentication
- `POST /auth/login` — get JWT token
- `GET /auth/me` — current user from token

### Staff
- `GET /staff/triage` — process arrival queue into triage queues
- `POST /staff/ta` — add a TA profile
- `POST /portal/staff/users` — create user account
- `GET /portal/staff/users` — list users
- `POST /portal/staff/students` — create student request from staff portal

### TA
- `POST /ta/claim` — claim next student
- `POST /ta/complete` — complete active student session
- `GET /ta/all` — list all TAs
- `GET /portal/ta/upcoming` — view upcoming assigned students

### Student Portal
- `GET /portal/student/line/{student_id}` — line position + status

## Auth Usage

Pass JWT in `Authorization` header:

```http
Authorization: Bearer <token>
```

## Optional Environment Settings

Use a `.env` file in `Office-Hours/api`:

```env
SECRET_KEY=change-me
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=sqlite:///./office_hours.db
```

Also configurable: `ALLOWED_ORIGINS`, `MAX_SEVERITY`, `MIN_SEVERITY`.
