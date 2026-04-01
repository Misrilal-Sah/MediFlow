# Project Structure

**Analysis Date:** 2026-04-02

## Directory Layout

```
python-project/
├── app.py              # Entire Flask application — all routes, helpers, email templates
├── config.py           # Config class; reads from .env via python-dotenv
├── requirements.txt    # Python dependencies (5 packages)
├── schema.sql          # Database DDL — creates DB + all 4 tables
├── seed.sql            # Sample data — 5 users, 35 doctors, patients, appointments
├── templates/          # Jinja2 HTML templates (15 files)
│   ├── base.html       # Shared layout, nav, loader, pagination macro, CSS/JS links
│   ├── login.html
│   ├── signup.html
│   ├── verify_email_pending.html
│   ├── forgot_password.html
│   ├── reset_password.html
│   ├── dashboard.html
│   ├── doctors.html
│   ├── add_doctor.html
│   ├── edit_doctor.html
│   ├── patients.html
│   ├── add_patient.html
│   ├── edit_patient.html
│   ├── appointments.html
│   ├── book_appointment.html
│   └── settings.html
└── static/
    ├── css/
    │   └── style.css   # All application styles
    ├── js/
    │   └── script.js   # Client-side interactivity
    └── asset/          # Likely image/icon assets (directory present, contents not listed)
```

## Templates Map

| Template | Route(s) That Render It | Purpose |
|---|---|---|
| `base.html` | Extended by all templates | Shared `<html>` shell, sidebar nav, flash messages, app loader, pagination macro |
| `login.html` | `GET /login` | Email + password login form |
| `signup.html` | `GET /signup` | Registration form (first name, last name, email, phone, password) |
| `verify_email_pending.html` | `GET /verify-pending` | Post-signup waiting screen; shows email address and resend button |
| `forgot_password.html` | `GET /forgot-password` | Email input to request a password reset link |
| `reset_password.html` | `GET /reset-password/<token>` | New password + confirm password form |
| `dashboard.html` | `GET /dashboard` | Summary stat cards (doctor/patient/appointment counts), today's appointments table, status chart |
| `doctors.html` | `GET /doctors` | Paginated table of all doctors; links to add/edit/delete |
| `add_doctor.html` | `GET /doctors/add` | Form to create a new doctor record |
| `edit_doctor.html` | `GET /doctors/edit/<id>` | Pre-filled form to update an existing doctor |
| `patients.html` | `GET /patients` | Paginated table of all patients; links to add/edit/delete |
| `add_patient.html` | `GET /patients/add` | Form to create a new patient record |
| `edit_patient.html` | `GET /patients/edit/<id>` | Pre-filled form to update an existing patient |
| `appointments.html` | `GET /appointments` | Paginated table of all appointments with status update and delete actions |
| `book_appointment.html` | `GET /appointments/book` | Dropdown form to book a new appointment (select patient, doctor, date, time, symptoms) |
| `settings.html` | `GET /settings` | Two-panel settings page — profile update and password change |

`base.html` defines a Jinja2 macro `render_pagination(page, total_pages, endpoint, total)` used by `doctors.html`, `patients.html`, and `appointments.html` for server-side pagination.

## Static Assets

All static files are served by Flask's built-in static file handler from `static/`.

**`static/css/style.css`**
- Single stylesheet for the entire application
- Referenced in `base.html` via `url_for('static', filename='css/style.css')`
- Styles for the dark-theme UI (data-theme="dark" on `<html>`), sidebar nav, cards, tables, forms, pagination, app loader, and flash messages

**`static/js/script.js`**
- Client-side interactivity for the application
- Referenced in `base.html` via `url_for('static', filename='js/script.js')`
- Handles themes, sidebar toggling, auto-dismiss flash messages, and any dashboard chart initialization

**`static/asset/`**
- Directory present; intended for images or icon files (logo is loaded externally from Cloudinary in email templates and base.html)

**External CDN dependencies (loaded in `base.html`):**
- Google Fonts: Inter + Outfit typefaces
- Chart.js (jsdelivr CDN) — used for appointment status chart on dashboard

## Configuration

Configuration is handled entirely in `config.py` via a `Config` class.

```python
# config.py
class Config:
    SECRET_KEY    = os.getenv("SECRET_KEY", "change_this_secret_key")
    MYSQL_HOST    = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_USER    = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
    MYSQL_DB      = os.getenv("MYSQL_DB", "hospital_management")
    MYSQL_PORT    = int(os.getenv("MYSQL_PORT", 3306))
    SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT     = int(os.getenv("SMTP_PORT", 587))
    SMTP_EMAIL    = os.getenv("SMTP_EMAIL", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_DISPLAY_NAME = os.getenv("SMTP_DISPLAY_NAME", "MediFlow")
```

- `python-dotenv` loads `.env` from the project root before class attributes are evaluated
- All values have hardcoded fallbacks — the app will start without a `.env` file, but SMTP won't send and `SECRET_KEY` will be insecure
- Applied to Flask via `app.config.from_object(Config)` in `app.py`
- MySQL connection is managed by `flask_mysqldb` using the `MYSQL_*` keys
- SMTP is used only if `SMTP_EMAIL` and `SMTP_PASSWORD` are both non-empty; otherwise email sends are silently skipped with a log warning

**Required `.env` keys for production:**
- `SECRET_KEY` — strong random string
- `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DB`
- `SMTP_EMAIL`, `SMTP_PASSWORD` (Gmail app password recommended)

## Database Files

**`schema.sql`**
- Creates the `hospital_management` database with `utf8mb4` charset if it doesn't exist
- Defines 4 tables: `users`, `doctors`, `patients`, `appointments`
- Enforces referential integrity via `FOREIGN KEY` constraints with `ON DELETE CASCADE` on `appointments`
- Run once to initialize: `mysql -u root -p < schema.sql`

**`seed.sql`**
- Truncates all 4 tables (disabling FK checks temporarily) then inserts sample data
- Inserts: 5 staff user accounts (all with password `Password@123`, `email_verified=1`), 35 doctors across specialties, and a set of patients and appointments
- Intended for development and demo use only
- Run against an already-initialized DB: `mysql -u root -p hospital_management < seed.sql`

---

*Structure analysis: 2026-04-02*
