# Testing State

**Analysis Date:** 2026-04-02

---

## Test Files

**None found.** There are no test files in the project:
- No `test_*.py` or `*_test.py` files
- No `tests/` or `test/` directory
- No pytest, unittest, or any testing library in `requirements.txt`

```
requirements.txt contents:
  Flask==3.0.3
  Flask-MySQLdb==2.0.0
  bcrypt==4.1.3
  python-dotenv==1.0.1
  itsdangerous==2.2.0
```

The codebase has **zero test coverage**.

---

## Test Coverage

| Area | Files | Covered |
|------|-------|---------|
| Auth routes (signup, login, logout) | `app.py` | None |
| Email verification flow | `app.py` | None |
| Password reset flow | `app.py` | None |
| Doctor CRUD routes | `app.py` | None |
| Patient CRUD routes | `app.py` | None |
| Appointment CRUD routes | `app.py` | None |
| Settings / profile update | `app.py` | None |
| Email change confirmation | `app.py` | None |
| DB helpers (`query_one`, `query_all`, `execute`) | `app.py` | None |
| Token helpers (`_reset_token`, `_verify_reset_token`, etc.) | `app.py` | None |
| `_send_email` helper | `app.py` | None |
| `login_required` decorator | `app.py` | None |
| Config loading | `config.py` | None |
| SQL schema correctness | `schema.sql` | None |

---

## Testing Gaps

**Critical (security-sensitive flows with no tests):**
- Password hashing and verification logic in signup/login/settings
- Token generation and expiry for password reset (1-hour window)
- Token generation and expiry for email verification (24-hour window)
- Email enumeration prevention — `forgot_password` and `resend_verification` must always return the same response
- Email change confirmation token ownership check (`user_id != session["user_id"]`)
- `login_required` decorator — unauthenticated requests must redirect to `/login`
- Status validation in `update_appointment_status` — only `Scheduled`, `Completed`, `Cancelled` are valid

**Functional gaps:**
- All CRUD routes: create, read, update, delete for doctors, patients, appointments
- Pagination logic — `LIMIT`/`OFFSET` boundary conditions
- Form validation — all required-field checks across every POST handler
- `query_one` returns `None` path in routes like `edit_doctor`, `edit_patient` (record not found)
- Session management: session is set on login and cleared on logout

**Integration gaps:**
- Database interaction — all `query_one`, `query_all`, `execute` calls
- SMTP email sending — `_send_email` failure path (missing credentials, connection refused)
- End-to-end auth flow: signup → verify email → login → logout

---

## Recommended Testing Approach

### Setup

Add to `requirements.txt`:
```
pytest==8.x
pytest-flask==1.x
pytest-mock==3.x
```

Create `conftest.py` at project root:
```python
import pytest
from app import app as flask_app

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "MYSQL_HOST": "127.0.0.1",      # use a test DB
        "MYSQL_DB": "hospital_test",
        "SECRET_KEY": "test-secret-key",
    })
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()
```

### File Structure

```
python-project/
├── tests/
│   ├── conftest.py
│   ├── test_auth.py          # signup, login, logout, email verify, password reset
│   ├── test_doctors.py       # CRUD for doctors
│   ├── test_patients.py      # CRUD for patients
│   ├── test_appointments.py  # CRUD + status update
│   ├── test_settings.py      # profile update, password change, email change
│   └── test_helpers.py       # token helpers, query helpers, _send_email
```

### Run Commands

```bash
pytest                        # Run all tests
pytest -v                     # Verbose output
pytest tests/test_auth.py     # Run single file
pytest --tb=short             # Short traceback on failures
```

### Priority Test Patterns

**Auth route (POST form):**
```python
def test_login_invalid_credentials(client):
    rv = client.post("/login", data={"email": "x@x.com", "password": "wrong"})
    assert rv.status_code == 302
    assert b"Invalid email" in client.get("/login").data  # flash shown on redirect

def test_login_requires_email_verified(client, mocker):
    mocker.patch("app.query_one", return_value=(1, "First", "Last", "x@x.com", hashed_pw, 0))
    rv = client.post("/login", data={"email": "x@x.com", "password": "password"})
    assert "/verify-pending" in rv.headers["Location"]
```

**`login_required` decorator:**
```python
@pytest.mark.parametrize("path", ["/dashboard", "/doctors", "/patients", "/appointments"])
def test_protected_routes_redirect_unauthenticated(client, path):
    rv = client.get(path)
    assert rv.status_code == 302
    assert "/login" in rv.headers["Location"]
```

**Token helpers:**
```python
def test_reset_token_roundtrip():
    from app import _reset_token, _verify_reset_token
    token = _reset_token("user@test.com")
    assert _verify_reset_token(token) == "user@test.com"

def test_reset_token_expired(freezegun_or_mock):
    # Use freezegun to advance time past max_age=3600
    ...
```

**`_send_email` SMTP failure:**
```python
def test_send_email_returns_false_when_unconfigured(app):
    with app.app_context():
        app.config["SMTP_EMAIL"] = ""
        from app import _send_email
        result = _send_email("a@b.com", "Subject", "<p>body</p>")
        assert result is False
```

### Mocking Strategy

- **Database calls:** mock `app.query_one`, `app.query_all`, `app.execute` with `mocker.patch` to avoid requiring a live MySQL instance in unit tests
- **Email sending:** mock `app._send_email` to return `True`/`False` without SMTP
- **Token time expiry:** use `freezegun` library or mock `itsdangerous` internals to test expired token paths
- **Use a real test DB** for integration tests — apply `schema.sql` to a `hospital_test` database and tear down between test runs

### What NOT to Mock in Integration Tests

- `query_one`, `query_all`, `execute` — test these against a real MySQL test database to catch SQL syntax errors and constraint violations
- `bcrypt` hashing — always test the real hash/verify cycle; never mock security primitives
