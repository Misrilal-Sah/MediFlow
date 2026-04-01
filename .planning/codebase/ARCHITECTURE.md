# Architecture Overview

**Analysis Date:** 2026-04-02

## Application Type

Server-side rendered monolith. Single Python process (`app.py`) handles all routing, business logic, and database access. No blueprints, no microservices, no API layer — all responses are Jinja2-rendered HTML pages.

## Request Flow

1. Browser sends HTTP request to Flask dev server (`app.run(debug=True)`)
2. Flask matches URL to a route function in `app.py`
3. `@login_required` decorator checks `session["user_id"]`; redirects to `/login` if missing
4. Route function calls `query_one()` / `query_all()` / `execute()` helpers which open a raw MySQL cursor via `flask_mysqldb`
5. On GET: `render_template()` returns Jinja2 HTML with data injected
6. On POST: form data validated inline, `execute()` writes to DB, `flash()` sets a one-time message, `redirect()` follows PRG (Post/Redirect/Get) pattern
7. Response returned to browser

## Route Groups

| Group | Prefix | Routes |
|---|---|---|
| Auth | `/` | `GET /`, `GET/POST /signup`, `GET /verify-pending`, `POST /resend-verification`, `GET /verify-email/<token>`, `GET/POST /login`, `GET /logout` |
| Dashboard | `/dashboard` | `GET /dashboard` |
| Doctors | `/doctors` | `GET /doctors`, `GET/POST /doctors/add`, `GET/POST /doctors/edit/<id>`, `POST /doctors/delete/<id>` |
| Patients | `/patients` | `GET /patients`, `GET/POST /patients/add`, `GET/POST /patients/edit/<id>`, `POST /patients/delete/<id>` |
| Appointments | `/appointments` | `GET /appointments`, `GET/POST /appointments/book`, `POST /appointments/status/<id>`, `POST /appointments/delete/<id>` |
| Settings | `/settings` | `GET/POST /settings`, `GET /confirm-email-change/<token>` |
| Password Reset | `/forgot-password` | `GET/POST /forgot-password`, `GET/POST /reset-password/<token>` |

No Flask Blueprints are used — all routes are registered directly on the `app` instance.

## Data Model

Defined in `schema.sql`. Four tables:

```
users
  id            INT PK AUTO
  first_name    VARCHAR(80)
  last_name     VARCHAR(80)
  email         VARCHAR(160) UNIQUE
  phone         VARCHAR(20)
  password_hash VARCHAR(255)        — bcrypt hash
  email_verified TINYINT(1)         — 0 = unverified, 1 = verified
  created_at    TIMESTAMP

doctors
  id             INT PK AUTO
  name           VARCHAR(120)
  specialty      VARCHAR(120)
  available_days VARCHAR(120)       — comma-separated weekday list
  phone          VARCHAR(20)
  created_at     TIMESTAMP

patients
  id         INT PK AUTO
  name       VARCHAR(120)
  age        TINYINT UNSIGNED
  gender     ENUM('Male','Female','Other')
  phone      VARCHAR(20)
  created_at TIMESTAMP

appointments
  id               INT PK AUTO
  patient_id       INT FK → patients.id  ON DELETE CASCADE
  doctor_id        INT FK → doctors.id   ON DELETE CASCADE
  appointment_date DATE
  appointment_time TIME
  status           ENUM('Scheduled','Completed','Cancelled')  DEFAULT 'Scheduled'
  symptoms         TEXT (nullable)
  created_at       TIMESTAMP
```

Relationships:
- `appointments.patient_id` → `patients.id` (many-to-one, CASCADE DELETE)
- `appointments.doctor_id` → `doctors.id` (many-to-one, CASCADE DELETE)
- `users` has no FK relationship to other tables; it represents staff/admin accounts only

## Session / State Management

Flask server-side sessions (`flask.session`) backed by a signed cookie (configured via `Config.SECRET_KEY`).

On successful login, two keys are written to session:
- `session["user_id"]` — integer user PK; used as the auth guard
- `session["user_name"]` — `"first_name last_name"` string; used in templates for display

Session is cleared entirely on logout via `session.clear()`. No server-side session store; all state lives in the signed cookie.

Flash messages (`flash()` / `get_flashed_messages()`) are used for one-time success/warning/danger/info notifications rendered in `base.html`.

## Authentication Flow

### Signup
1. POST `/signup` → validate fields, check email uniqueness
2. Password hashed with `bcrypt.hashpw()`, stored in `users.password_hash`
3. User inserted with `email_verified=0`
4. Email verification token generated via `itsdangerous.URLSafeTimedSerializer` (salt: `"email-verify"`, expiry: 24 h)
5. Verification email sent via SMTP; user redirected to `/verify-pending`
6. GET `/verify-email/<token>` → token decoded, `email_verified` set to `1`

### Login
1. POST `/login` → look up user by email, `bcrypt.checkpw()` against stored hash
2. If `email_verified=0` → redirect to `/verify-pending` (cannot log in)
3. If verified + password matches → write `user_id` and `user_name` to session, redirect to `/dashboard`

### Password Reset
1. POST `/forgot-password` → look up email (always shows neutral flash to prevent enumeration)
2. Reset token generated via `URLSafeTimedSerializer` (salt: `"pw-reset"`, expiry: 1 h)
3. Email sent with reset link to `/reset-password/<token>`
4. POST `/reset-password/<token>` → token validated, new password hashed and stored

### Email Change (in Settings)
1. POST `/settings` with `action=profile` and a changed email → token generated (salt: `"email-change"`, expiry: 24 h)
2. Confirmation email sent to the **new** address; non-email fields updated immediately
3. GET `/confirm-email-change/<token>` → token validated, `users.email` updated

## Key Design Patterns

- **PRG (Post/Redirect/Get):** All POST handlers redirect after processing to prevent form re-submission
- **Inline validation:** Field validation is done directly in each route handler — no separate form/schema classes
- **Raw cursor helpers:** `query_one()`, `query_all()`, `execute()` are thin wrappers around `flask_mysqldb` cursors; no ORM
- **`@login_required` decorator:** A `functools.wraps` wrapper that guards all authenticated routes
- **Token-based email flows:** `itsdangerous.URLSafeTimedSerializer` used for all email verification, password reset, and email change tokens — no tokens stored in the database
- **Anti-enumeration responses:** `/forgot-password` and `/resend-verification` always return the same flash message regardless of whether the email exists

---

*Architecture analysis: 2026-04-02*
