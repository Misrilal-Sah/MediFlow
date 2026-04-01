# Integrations & External Services

**Analysis Date:** 2026-04-02

## Email / SMTP

- **Provider:** Generic SMTP — defaults to Gmail (`smtp.gmail.com:587`)
- **Protocol:** STARTTLS via Python stdlib `smtplib` + `ssl.create_default_context()`
- **Implementation:** `_send_email(to_addr, subject, html_body)` helper in `app.py`
  - Returns `True` on success, `False` on failure (logs error, never raises)
  - Skips silently if `SMTP_EMAIL` or `SMTP_PASSWORD` not configured
- **Message format:** `MIMEMultipart("alternative")` with HTML body (`MIMEText` utf-8)
- **Display name:** Configurable via `SMTP_DISPLAY_NAME` (defaults to `"MediFlow"`)

**Email workflows triggered:**

| Event | Subject | Token Type |
|---|---|---|
| New signup | `MediFlow – Please Confirm Your Email` | `email-verify` (24h) |
| Resend verification | `MediFlow – Confirm Your Email (Resent)` | `email-verify` (24h) |
| Forgot password | `MediFlow – Password Reset Request` | `pw-reset` (1h) |
| Email address change | `MediFlow – Confirm Your New Email` | `email-change` (24h) |
| Welcome (post-verify) | `MediFlow – Welcome` | None |

**Email HTML templates** (inline in `app.py`):
- `_email_reset_html(reset_url)` — password reset CTA
- `_email_welcome_html(first_name)` — welcome after email verification
- `_email_verify_html(first_name, verify_url)` — signup email confirmation
- `_email_change_confirm_html(first_name, confirm_url, new_email)` — email change confirmation

## Third-party APIs

- **No external REST/API calls** detected beyond SMTP
- **Cloudinary** — used passively for logo image hosting only (no SDK, no upload):
  - Logo URL: `https://res.cloudinary.com/ddrlxvnsh/image/upload/v1775064288/logo_kyqvgv.png`
  - Referenced in inline email HTML templates and `templates/base.html` app loader
  - No Cloudinary SDK or API credentials required by the application

## CDN Resources (Frontend)

| Resource | CDN | Usage |
|---|---|---|
| Google Fonts (`Inter`, `Outfit`) | `fonts.googleapis.com` / `fonts.gstatic.com` | Typography — loaded in `templates/base.html` |
| Chart.js | `cdn.jsdelivr.net/npm/chart.js` | Dashboard charts — deferred script in `templates/base.html` |

## Environment Variables

All variables loaded via `.env` file using `python-dotenv` in `config.py`.

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | `"change_this_secret_key"` | Flask session signing + itsdangerous token signing |
| `MYSQL_HOST` | `"127.0.0.1"` | MySQL server hostname |
| `MYSQL_USER` | `"root"` | MySQL username |
| `MYSQL_PASSWORD` | `"root"` | MySQL password |
| `MYSQL_DB` | `"hospital_management"` | MySQL database name |
| `MYSQL_PORT` | `3306` | MySQL server port |
| `SMTP_HOST` | `"smtp.gmail.com"` | SMTP server hostname |
| `SMTP_PORT` | `587` | SMTP server port |
| `SMTP_EMAIL` | `""` | Sender email address (empty = email disabled) |
| `SMTP_PASSWORD` | `""` | Sender email password / app password |
| `SMTP_DISPLAY_NAME` | `"MediFlow"` | From display name in sent emails |

**Security note:** `SECRET_KEY` default must be overridden in production. If left as `"change_this_secret_key"`, session cookies and all signed tokens are compromised.

## File Storage

- **No file upload functionality** detected
- No local filesystem write operations beyond application startup
- Static assets served directly from `static/` folder via Flask

## Security Integrations

**CSRF Protection:**
- No CSRF protection library detected (e.g., no Flask-WTF)
- Forms use plain HTML `<form method="POST">` without CSRF tokens
- Risk: all state-changing POST endpoints are vulnerable to cross-site request forgery

**Rate Limiting:**
- No rate limiting detected (no Flask-Limiter or similar)
- Risk: login, signup, password reset, and resend-verification endpoints are unprotected against brute-force

**Token-based security (itsdangerous):**
- Password reset tokens: 1-hour expiry, salt `"pw-reset"`
- Email verification tokens: 24-hour expiry, salt `"email-verify"`
- Email change tokens: 24-hour expiry, salt `"email-change"`
- Tokens are invalidated server-side on use (single-use by marking `email_verified=1` or updating email)

**Password Security:**
- bcrypt hashing with `bcrypt.gensalt()` (default cost factor ~12)
- Minimum password length: 8 characters (enforced on password change in settings)
- No minimum length enforced on initial signup

**Session Security:**
- Flask server-side sessions (cookie stores signed session ID)
- `session.clear()` on logout
- No `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`, or `SESSION_COOKIE_SAMESITE` explicitly configured — relies on Flask defaults

**OAuth / SSO:**
- Not implemented

---

*Integration audit: 2026-04-02*
