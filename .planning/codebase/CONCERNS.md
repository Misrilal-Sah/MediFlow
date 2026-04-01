# Codebase Concerns & Technical Debt

**Analysis Date:** 2026-04-02

---

## Security Concerns

### CSRF – No Protection on Any Form (CRITICAL)
- **Issue:** Every POST form (login, signup, add/edit/delete doctor, patient, appointment, settings, password reset) has zero CSRF protection. No Flask-WTF, no manual token.
- **Files:** `app.py` (all POST routes), `templates/login.html`, `templates/signup.html`, `templates/settings.html`, `templates/book_appointment.html`, `templates/add_doctor.html`, `templates/add_patient.html`, etc.
- **Impact:** Any malicious page can forge requests on behalf of authenticated users (OWASP A05).
- **Fix:** Add `Flask-WTF` and `CSRFProtect(app)`. Add `{{ form.hidden_tag() }}` or the raw `{{ csrf_token() }}` macro to every form.

### `debug=True` Hardcoded in Production Entry Point
- **Issue:** `app.run(debug=True)` is the final line of `app.py`. If this file is run directly in any environment, the Werkzeug interactive debugger is exposed, allowing arbitrary code execution via the browser console.
- **Files:** `app.py` line ~870.
- **Fix:** Change to `app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")`.

### Weak Default `SECRET_KEY`
- **Issue:** `Config.SECRET_KEY` falls back to `"change_this_secret_key"` if the env var is not set. This key signs session cookies and all timed tokens (password reset, email verification). A predictable key means sessions and tokens can be forged.
- **Files:** `config.py` line 6.
- **Fix:** Raise a `ValueError` if `SECRET_KEY` is not set rather than supplying a default. Or at minimum generate a warning.

### Default MySQL Credentials Are `root` / `root`
- **Issue:** `MYSQL_USER` and `MYSQL_PASSWORD` both default to `"root"`. Connecting to MySQL as root is a privilege escalation risk, and the default password is trivially guessable.
- **Files:** `config.py` lines 9–10.
- **Fix:** Require explicit env vars with no default. Create a least-privilege DB user for the app.

### No Session Cookie Security Flags
- **Issue:** `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`, and `SESSION_COOKIE_SAMESITE` are not configured in `Config`. Cookies are therefore sent over HTTP, readable by JavaScript, and lack CSRF protection at the cookie layer.
- **Files:** `config.py`.
- **Fix:** Add `SESSION_COOKIE_SECURE = True`, `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = "Lax"` to `Config`.

### No Rate Limiting on Auth Endpoints
- **Issue:** `/login`, `/signup`, `/forgot-password`, and `/resend-verification` have no rate limiting. Brute-force and credential-stuffing attacks are unconstrained.
- **Files:** `app.py` routes `login`, `signup`, `forgot_password`, `resend_verification`.
- **Fix:** Add `Flask-Limiter` and apply `@limiter.limit("5/minute")` to these routes.

### No HTTP Security Headers
- **Issue:** No `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, or `Strict-Transport-Security` headers are set. The app is vulnerable to MIME-sniffing, clickjacking, and resource injection (OWASP A05).
- **Files:** `app.py` – no `@app.after_request` handler exists.
- **Fix:** Add a `@app.after_request` handler or use `Flask-Talisman`.

### Missing Server-Side Validation on Numeric and FK Inputs
- **Issue:** `age` (patient), `patient_id`, and `doctor_id` (appointment booking) are accepted as raw strings from the form and passed directly to SQL. `age` is not validated as a positive integer. `patient_id` and `doctor_id` are not verified to exist before INSERT—a FK violation yields an unhandled 500.
- **Files:** `app.py` `add_patient`, `edit_patient`, `book_appointment`.
- **Fix:** Validate `int(age)` is in `[0, 150]`. Look up both FK records before inserting and return a user-visible error if not found.

### Missing `appointment_date` Past-Date Validation
- **Issue:** Users can book appointments in the past. No server-side check that `appointment_date >= date.today()`.
- **Files:** `app.py` `book_appointment`.
- **Fix:** Add `if appointment_date < date.today().isoformat(): flash(...)`.

### Seed File Documents Plaintext Credentials
- **Issue:** `seed.sql` comments `-- All accounts use password: Password@123` in committed source. While the hashes are stored properly, documenting the plaintext in version-controlled files is a security hygiene failure.
- **Files:** `seed.sql` lines 16–17.
- **Fix:** Remove the password comment from the file header. Note only that bcrypt hashes are `$2b$12$...`.

---

## Performance Concerns

### Dashboard Issues 5 Sequential DB Queries
- **Issue:** `dashboard()` calls `query_one(COUNT doctors)`, `query_one(COUNT patients)`, `query_one(COUNT appointments)`, `query_all(today's appointments JOIN)`, and `query_all(status GROUP BY)` — five separate round trips.
- **Files:** `app.py` `dashboard` route.
- **Fix:** Consolidate the three COUNTs into one query or use a single CTE.

### `book_appointment` Loads All Doctors and Patients Unbounded
- **Issue:** `query_all("SELECT id, name FROM doctors ORDER BY name ASC")` and the equivalent for patients return every row in those tables to render the `<select>` dropdowns. As the tables grow this will be slow and memory-intensive.
- **Files:** `app.py` `book_appointment`.
- **Fix:** Add a search-as-you-type autocomplete (AJAX `/search` endpoint) rather than loading every row.

### No Database Indexes Beyond PKs
- **Issue:** `schema.sql` defines no secondary indexes. Queries filtering on `appointments.appointment_date`, `appointments.status`, or joining `patient_id`/`doctor_id` will do full table scans as data grows.
- **Files:** `schema.sql`.
- **Fix:** Add:
  ```sql
  CREATE INDEX idx_apt_date   ON appointments(appointment_date);
  CREATE INDEX idx_apt_status ON appointments(status);
  CREATE INDEX idx_apt_patient ON appointments(patient_id);
  CREATE INDEX idx_apt_doctor  ON appointments(doctor_id);
  ```

### No DB Connection Pooling Configuration
- **Issue:** `Flask-MySQLdb` wraps `MySQLdb` which creates one persistent connection per worker but has no pool or reconnect logic. Under load or after idle timeouts the connection silently dies.
- **Files:** `config.py`, `app.py`.
- **Fix:** Consider switching to `Flask-SQLAlchemy` with connection pooling, or set `MYSQL_CONNECT_TIMEOUT` and add reconnect handling.

### Cursor Leak on Exception
- **Issue:** `query_one`, `query_all`, and `execute` all do `cur = ...; cur.execute(...); ...; cur.close()`. If an exception is raised between `execute` and `close`, the cursor is never closed. No `try/finally` or context manager is used.
- **Files:** `app.py` lines 28–44.
- **Fix:** Wrap cursor operations in `try/finally: cur.close()` or use a context manager.

---

## Reliability Concerns

### No Error Handling on Any DB Operation
- **Issue:** `query_one`, `query_all`, and `execute` have no `try/except`. Any DB error (connection drop, deadlock, constraint violation, syntax error) raises an unhandled exception and surfaces as a Werkzeug 500 traceback to the user.
- **Files:** `app.py` lines 28–44.
- **Fix:** Add `try/except` in each helper and either raise a custom exception or return `None`/`False` with logging.

### No Custom Error Handlers (404 / 500)
- **Issue:** There are no `@app.errorhandler(404)` or `@app.errorhandler(500)` handlers. Users hitting broken links or triggering exceptions see raw Werkzeug pages that leak framework details.
- **Files:** `app.py`.
- **Fix:** Add error handler functions that render a styled error template.

### Unhandled FK Violation When Booking Appointments
- **Issue:** `book_appointment` inserts `patient_id` and `doctor_id` from the form without verifying they exist. If a user manipulates the hidden form values to reference non-existent IDs, MySQL raises an IntegrityError which is unhandled.
- **Files:** `app.py` `book_appointment` POST handler.
- **Fix:** Query both records before INSERT and flash an error if either is missing.

### No Logging Configuration
- **Issue:** `app.logger.warning` and `app.logger.error` are called inside email helpers, but no logging format, level, or handler is configured. In production (Gunicorn, etc.), application-level logs are discarded unless explicitly configured.
- **Files:** `app.py`, `config.py` – no `logging.basicConfig` or `RotatingFileHandler`.
- **Fix:** Add a logging setup block in `app.py` that configures at minimum a StreamHandler with a timestamped format.

### `seed.sql` TRUNCATE Will Destroy Production Data if Run Accidentally
- **Issue:** The seed file starts with `TRUNCATE TABLE appointments; TRUNCATE TABLE patients; TRUNCATE TABLE doctors; TRUNCATE TABLE users;`. If run against a production DB, all data is permanently lost.
- **Files:** `seed.sql` lines 5–11.
- **Fix:** Add a prominent `-- FOR DEVELOPMENT ONLY` banner and a guard check (e.g., verify `hospital_management` DB name starts with `dev_`), or remove the TRUNCATE statements and use a separate `reset.sql`.

---

## Maintainability Concerns

### Monolithic `app.py` (~870 Lines)
- **Issue:** All routes, helpers, email templates, auth logic, and CRUD operations are in a single file. Adding features or fixing bugs requires scrolling through the entire file. Flask Blueprints are not used.
- **Files:** `app.py`.
- **Fix:** Split into blueprints: `blueprints/auth.py`, `blueprints/doctors.py`, `blueprints/patients.py`, `blueprints/appointments.py`, `blueprints/settings.py`.

### Tuple-Based DB Row Access (`user[0]`, `user[4]`, etc.)
- **Issue:** All DB results are accessed by positional index (e.g., `user[4].encode(...)` for `password_hash`, `user[5]` for `email_verified`). Adding or reordering a column in the schema silently breaks multiple access sites.
- **Files:** `app.py` – every route accessing DB results. `templates/settings.html` uses `{{ user[1] }}`, `{{ user[2] }}`, etc.
- **Fix:** Switch to `MySQLdb.cursors.DictCursor` so rows are accessed by name (`user["password_hash"]`).

### `PER_PAGE = 10` Magic Constant Repeated in Every Paginated Route
- **Issue:** The literal `PER_PAGE = 10` is declared locally inside `doctors()`, `patients()`, and `appointments()` — three separate definitions.
- **Files:** `app.py` routes `doctors`, `patients`, `appointments`.
- **Fix:** Extract to a single module-level constant `PER_PAGE = 10`.

### Email HTML Embedded as Long Python f-Strings
- **Issue:** Four large HTML email templates (`_email_reset_html`, `_email_welcome_html`, `_email_verify_html`, `_email_change_confirm_html`) are multiline f-strings in `app.py`, totalling ~150 lines. They are hard to edit, cannot be previewed, and bloat the route file.
- **Files:** `app.py` lines ~120–250.
- **Fix:** Move to Jinja2 templates under `templates/email/` and render with `render_template()`.

### No `.env.example` File
- **Issue:** There is no documented template of required environment variables. A new developer has no way to know which vars to set without reading config.py carefully.
- **Files:** `config.py` – lists all vars, but no companion `.env.example`.
- **Fix:** Create `.env.example` listing all required keys with placeholder values.

### `requirements.txt` Has No Lockfile / Hash Pinning
- **Issue:** Only 5 direct dependencies are listed. There is no `pip freeze` output, no `requirements-dev.txt`, and no hash pinning (`--hash=sha256:...`). Transitive dependency updates can silently break the app.
- **Files:** `requirements.txt`.
- **Fix:** Generate a full locked requirements file with `pip freeze > requirements-lock.txt` or adopt `pip-tools` / `poetry`.

---

## Missing Features (vs. Typical Hospital Apps)

- **Search / Filter:** No ability to search patients by name, filter appointments by date range or status, or search doctors by specialty.
- **Role-Based Access Control:** All authenticated users are equal. There is no admin/supervisor vs. read-only staff distinction.
- **Appointment Conflict Detection:** The same doctor can be double-booked at the same date+time. No uniqueness constraint exists on `(doctor_id, appointment_date, appointment_time)` in `schema.sql`.
- **Audit Trail:** No logging of who created, edited, or deleted which record and when. `created_at` exists but there is no `updated_at` or `updated_by`.
- **Patient Medical History:** Only name, age, gender, and phone are stored. No diagnoses, allergies, or visit notes.
- **Export / Reporting:** No ability to export records to CSV/PDF.
- **REST API / JSON Endpoints:** The application is fully server-rendered. No JSON API means no mobile client or integration is possible without a full refactor.

---

## Quick Wins

1. **Remove `debug=True`** — change `app.run(debug=True)` to use an env var. One-line fix, eliminates remote code execution risk.
2. **Add session cookie flags** — three lines in `config.py` (`SESSION_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE`).
3. **Add indexes to `schema.sql`** — four `CREATE INDEX` statements, speeds up all appointment queries.
4. **Extract `PER_PAGE` constant** — remove three local definitions, add one module-level constant.
5. **Add `.env.example`** — one file, unblocks new contributors immediately.
6. **Add `try/finally` cursor cleanup** — prevents cursor leaks on DB exceptions with minimal code change.
7. **Validate `age` as positive integer** — one `try/except int(age)` check in `add_patient` and `edit_patient`.
8. **Add past-date guard on appointment booking** — one `if` check against `date.today()`.

---

## Bigger Refactors Needed

1. **Add CSRF protection via Flask-WTF** — Install `Flask-WTF`, initialize `CSRFProtect(app)`, add `{{ csrf_token() }}` to all forms. Touches every template.
2. **Split `app.py` into Flask Blueprints** — Create `blueprints/` directory, separate auth, CRUD modules, register with `app.register_blueprint()`. Improves testability and onboarding.
3. **Switch to `DictCursor` for all DB access** — Remove fragile positional tuple indexing throughout `app.py` and all templates that use `user[n]` syntax.
4. **Move email templates to `templates/email/`** — Extract four inline f-string HTML blocks to Jinja2 files. Removes ~150 lines from `app.py` and makes email content editable without touching Python.
5. **Add rate limiting with Flask-Limiter** — Protect login, signup, forgot-password, and resend-verification routes from brute-force attacks.
6. **Add custom error handlers** — `@app.errorhandler(404)` and `@app.errorhandler(500)` with styled responses and logging.
7. **Add `appointment_date` + `appointment_time` uniqueness constraint per doctor** — `UNIQUE KEY uq_apt (doctor_id, appointment_date, appointment_time)` in `schema.sql` to prevent double-booking at the DB level.
8. **Add structured application logging** — Configure `logging.basicConfig` or a `RotatingFileHandler` so that errors, warnings, and security events are durably recorded.

---

*Concerns audit: 2026-04-02*
