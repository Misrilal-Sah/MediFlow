# Tech Stack

**Analysis Date:** 2026-04-02

## Runtime & Language

- **Python** — primary language (version not pinned in requirements.txt; standard library used throughout)
- No `.python-version` or `runtime.txt` detected

## Web Framework

- **Flask 3.0.3** — core web framework (`app.py`)
  - Application factory: `app = Flask(__name__)` with `app.config.from_object(Config)`
  - Routing: function-based views with `@app.route` decorators
  - Templates: Jinja2 (Flask built-in) via `render_template()`
  - Flash messaging: `flash()` / `get_flashed_messages()` pattern throughout
  - Session: server-side Flask sessions (`session["user_id"]`, `session["user_name"]`)
  - Auth guard: custom `@login_required` decorator using `functools.wraps`

## Database

- **MySQL** — relational database engine
- **Flask-MySQLdb 2.0.0** — MySQL adapter (`flask_mysqldb.MySQL`)
- **No ORM** — raw SQL via parameterized queries (`%s` placeholders) using cursor-based helpers:
  - `query_one(sql, params)` — returns single row
  - `query_all(sql, params)` — returns all rows
  - `execute(sql, params)` — write operations with `mysql.connection.commit()`
- Schema defined in `schema.sql`; seed data in `seed.sql`
- Database: `hospital_management` (utf8mb4 / utf8mb4_unicode_ci)

**Tables:**
| Table | Purpose |
|---|---|
| `users` | Admin/staff accounts with email verification |
| `doctors` | Doctor records with specialty and availability |
| `patients` | Patient demographic records |
| `appointments` | Appointments linking patients ↔ doctors with status |

**Relationships:**
- `appointments.patient_id` → `patients.id` (CASCADE DELETE)
- `appointments.doctor_id` → `doctors.id` (CASCADE DELETE)

## Authentication

- **Custom session-based auth** — no third-party auth library
- **Password hashing:** `bcrypt 4.1.3` — `bcrypt.hashpw()` / `bcrypt.checkpw()` with `bcrypt.gensalt()`
- **Email verification required at signup** — `email_verified` column on `users` table
- **Token signing:** `itsdangerous 2.2.0` — `URLSafeTimedSerializer` with separate salts per operation:
  - `"pw-reset"` — password reset tokens (1 hour expiry)
  - `"email-verify"` — signup email verification (24 hour expiry)
  - `"email-change"` — email address change confirmation (24 hour expiry)
- **Session stores:** `user_id`, `user_name` keys
- **Auth guard:** `@login_required` decorator redirects unauthenticated users to `/login`
- **Email enumeration protection:** resend-verification endpoint always returns the same message

## Frontend

- **CSS framework:** None — fully custom CSS in `static/css/style.css`
  - CSS custom properties (`:root` variables) for theming
  - Dark/light theme via `html[data-theme]` attribute
  - Glassmorphism design: `backdrop-filter: blur`, `rgba` backgrounds
  - Custom sidebar, cards, tables, buttons, modals — no utility framework
- **Fonts:** Google Fonts (`Inter`, `Outfit`) loaded via CDN in `templates/base.html`
- **Charting:** `Chart.js` loaded via jsDelivr CDN (`cdn.jsdelivr.net/npm/chart.js`) — deferred
- **JavaScript:** Vanilla JS in `static/js/script.js`
  - Theme toggle with `localStorage` persistence
  - Sidebar collapse/expand with `localStorage` persistence
  - App loader animation (fade out after 900ms)
  - Flash message auto-dismiss with toast mirroring
  - Global confirm modal for delete actions
- **Templating engine:** Jinja2 (Flask built-in)
  - Base template: `templates/base.html` (includes pagination macro, sidebar, topbar)
  - Template inheritance via `{% extends "base.html" %}` / `{% block %}` pattern
- **Pagination:** Custom paginator macro in `base.html`, server-side with `LIMIT`/`OFFSET`; 10 records per page

## Key Dependencies (from requirements.txt)

| Package | Version | Purpose |
|---|---|---|
| `Flask` | 3.0.3 | Web framework, routing, templating, sessions |
| `Flask-MySQLdb` | 2.0.0 | MySQL database connector for Flask |
| `bcrypt` | 4.1.3 | Secure password hashing and verification |
| `python-dotenv` | 1.0.1 | Load environment variables from `.env` file |
| `itsdangerous` | 2.2.0 | Cryptographically signed tokens for email workflows |

## Dev/Build Tooling

- No build pipeline detected (no Webpack, Vite, or similar)
- No task runner (no Makefile, Procfile, or `scripts` section)
- Static files served directly by Flask (`url_for('static', filename=...)`)
- Database setup: manual SQL execution (`mysql -u root -p < schema.sql`)
- Application entry point: `python app.py` (Flask dev server via `app.run()` implied)
- Environment config: `.env` file loaded via `python-dotenv` at startup in `config.py`

---

*Stack analysis: 2026-04-02*
