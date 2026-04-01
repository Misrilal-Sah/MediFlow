# Code Conventions

**Analysis Date:** 2026-04-02

---

## Python Style

**Naming:**
- Functions: `snake_case` — `query_one`, `login_required`, `book_appointment`
- Private/internal helpers: prefixed with `_` — `_send_email`, `_reset_token`, `_verify_reset_token`, `_email_verify_html`
- Classes: `PascalCase` — `Config` in `config.py`
- Variables: `snake_case` — `password_hash`, `total_pages`, `smtp_email`
- Constants: inline uppercase not used; config values accessed via `app.config.get()`

**File Organization:**
- Single-file application: all routes, helpers, and email templates live in `app.py`
- Config isolated to `config.py` via a `Config` class loaded with `app.config.from_object(Config)`
- No packages or submodules — flat structure

**Docstrings:**
- Minimal: only `_send_email` has a one-line docstring
- No function-level docstrings on route handlers
- Section dividers use `# -- Section Name --` comments in `app.py`

**Type Annotations:** Not used anywhere in the codebase.

**Helper Function Pattern:**
Three shared DB helpers defined at module level, used by all routes:
```python
def query_one(sql, params=()):   # Returns single row or None
def query_all(sql, params=()):   # Returns list of rows
def execute(sql, params=()):     # INSERT/UPDATE/DELETE, auto-commits
```

---

## Route Naming

**URL Pattern:** kebab-case for multi-word paths
- `/forgot-password`, `/verify-email/<token>`, `/book-appointment`, `/verify-pending`, `/resend-verification`, `/confirm-email-change/<token>`

**Resource Sub-paths:** nested under resource name with verb suffix
- `/doctors/add`, `/doctors/edit/<int:doctor_id>`, `/doctors/delete/<int:doctor_id>`
- `/patients/add`, `/patients/edit/<int:patient_id>`, `/patients/delete/<int:patient_id>`
- `/appointments/book`, `/appointments/status/<int:appointment_id>`, `/appointments/delete/<int:appointment_id>`

**Route Function Names:** match resource names in `snake_case`
- `add_doctor`, `edit_doctor`, `delete_doctor`, `book_appointment`, `update_appointment_status`

**HTTP Methods:**
- `GET`-only routes: listing pages, dashboard, verify-email link handler
- `GET`+`POST` on same route: all forms (add, edit, login, signup, settings, forgot/reset password)
- `POST`-only: all delete and status-update actions (use `<form method="POST">` in templates)

**Auth Guard:** `@login_required` decorator applied to every protected route; unauthenticated requests are redirected to `/login` with a flash warning.

---

## Error Handling

**User-facing errors:** `flash()` with Bootstrap-style categories — `"danger"`, `"warning"`, `"info"`, `"success"` — followed by `redirect(url_for(...))`.

**Validation pattern:** check required fields with `if not all([...])`, flash and redirect immediately:
```python
if not all([name, specialty, available_days, phone]):
    flash("All fields are required.", "danger")
    return redirect(url_for("add_doctor"))
```

**Record not found:** query result is `None`-checked, then flash + redirect:
```python
doctor = query_one("SELECT * FROM doctors WHERE id=%s", (doctor_id,))
if not doctor:
    flash("Doctor not found.", "danger")
    return redirect(url_for("doctors"))
```

**Email errors:** logged via `app.logger.error(f"Email send failed: {exc}")` inside `_send_email`; caller receives `True/False` return value and flashes accordingly.

**Token errors:** `SignatureExpired` and `BadSignature` from `itsdangerous` are caught in `_verify_*_token` helpers, which return `None` on failure; callers check for `None` before proceeding.

**No custom error pages:** `@app.errorhandler` is not used; Flask's default 404/500 pages are shown.

**Email enumeration prevention:** `forgot_password` and `resend_verification` routes always show a generic success message regardless of whether the email exists.

---

## Template Conventions

**Inheritance:** All pages extend `base.html` via `{% extends "base.html" %}`.

**Defined blocks in `base.html`:**
- `{% block title %}` — page `<title>` tag
- `{% block topbar %}` — optional top bar (overridden to empty on auth pages)
- `{% block page_title %}` — heading shown inside the layout
- `{% block content %}` — main page body

**Macros:** A `render_pagination` macro is defined at the top of `base.html` and used inline on listing pages (`doctors.html`, `patients.html`, `appointments.html`):
```jinja
{{ render_pagination(page, total_pages, 'doctors', total) }}
```

**URL Generation:** Always use `url_for()` — never hardcoded paths:
```jinja
<a href="{{ url_for('forgot_password') }}">Forgot password?</a>
```

**Flash Messages:** Rendered in `base.html` as `.flash` elements with category-based CSS classes; JS in `script.js` auto-dismisses them and mirrors as toasts.

**Auth-conditional layout:** The sidebar, topbar, and nav are wrapped in `{% if session.get('user_id') %}` in `base.html` — unauthenticated pages render only the content block without navigation chrome.

**CSS classes:** BEM-influenced custom classes (`.auth-card`, `.form-grid`, `.btn-primary`, `.glass`, `.reveal`, `.ripple`); no external CSS framework.

---

## SQL Conventions

**Parameterization:** All queries use `%s` placeholders — never string formatting or f-strings in SQL:
```python
query_one("SELECT id FROM users WHERE email=%s", (email,))
execute("UPDATE doctors SET name=%s, specialty=%s WHERE id=%s", (name, specialty, doctor_id))
```

**Query helper selection:**
- `query_one()` for lookups expecting at most one row (existence checks, fetches by PK)
- `query_all()` for listing queries
- `execute()` for all writes (INSERT/UPDATE/DELETE)

**Column naming:** `snake_case` — `first_name`, `password_hash`, `appointment_date`, `available_days`, `email_verified`

**Table naming:** lowercase singular — `users`, `doctors`, `patients`, `appointments`

**Schema conventions (`schema.sql`):**
- All PKs: `INT AUTO_INCREMENT PRIMARY KEY`
- All tables include `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP`
- Foreign keys named explicitly: `fk_apt_patient`, `fk_apt_doctor` with `ON DELETE CASCADE`
- Character set: `utf8mb4` / `utf8mb4_unicode_ci` throughout
- ENUMs for bounded value sets: `gender ENUM('Male','Female','Other')`, `status ENUM('Scheduled','Completed','Cancelled')`

---

## Security Practices

**Password Hashing:** bcrypt via the `bcrypt` library with `bcrypt.gensalt()`:
```python
bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
```
Minimum password length of 8 characters enforced in reset and settings routes.

**SQL Injection Prevention:** All SQL uses parameterized queries — no raw user input ever interpolated into SQL strings.

**Signed Tokens:** `itsdangerous.URLSafeTimedSerializer` for all email tokens (password reset 1 hour, email verify 24 hours, email change 24 hours). Each token type uses a distinct `salt` string.

**Email Verification:** Users cannot log in until `email_verified = 1`; checked at login time.

**Email Enumeration Prevention:** Both `/forgot-password` and `/resend-verification` return identical responses regardless of whether the email exists.

**Secrets via Environment:** All credentials loaded from `.env` via `python-dotenv`; `config.py` never hardcodes real values. `SECRET_KEY` has a fallback of `"change_this_secret_key"` — this **must** be overridden in production.

**CSRF Protection:** **Not implemented.** Flask-WTF or a manual CSRF token is absent. All POST forms are vulnerable to cross-site request forgery. This is a gap.

**Session Security:** Flask's signed cookie session is used (`app.config["SECRET_KEY"]`). Session is cleared on logout via `session.clear()`.

**Input Sanitization:** `.strip()` on all `request.form.get()` calls; `.lower()` on email fields. No HTML sanitization (not needed currently as no user-generated HTML is rendered).

---

## JavaScript Conventions

**Module Pattern:** Single `DOMContentLoaded` listener in `static/js/script.js` wraps all initialization — no ES modules, no bundler.

**Variable Declarations:** `const` / `let` throughout — no `var`.

**DOM Access:** `document.getElementById()` and `document.querySelectorAll()` with optional chaining (`?.`) for safe null access:
```js
loader?.classList.add("hide");
themeToggle?.addEventListener("click", ...);
```

**Event Handling:**
- `addEventListener` only — no inline `onclick` attributes in HTML
- Event delegation used for delete confirmation modal (listens on `.delete-form` collection)
- Outside-click dismissal using `document.addEventListener("click", ...)` with `picker.contains(e.target)` guard

**State Persistence:** `localStorage` used for theme (`"theme"`) and sidebar state (`"sidebar-collapsed"`); read on page load, written on toggle.

**UI Patterns:**
- Toast notifications via a `pushToast()` function (called for flash mirrors and theme changes)
- Ripple effect on `.ripple` buttons via dynamically appended `<span class="ripple-wave">`
- Global confirm modal (`#globalModal`) for all delete actions — intercepts `.delete-form` submits
- Table column sorting on `.sortable-th` headers — client-side, handles both numeric and string comparison
- Custom day-picker widget (`.day-picker`) with checkbox dropdown and chip display
- Password visibility toggle on `.pwd-eye` buttons

**Chart.js Integration:** Dashboard doughnut chart initialized from `data-labels` / `data-values` attributes on `<canvas id="statusChart">` — data is server-rendered into the DOM, JS only reads it.
