from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from functools import wraps
import bcrypt
from datetime import date
from config import Config
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)


# ------------------ Helpers ------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def query_one(sql, params=()):
    cur = mysql.connection.cursor()
    cur.execute(sql, params)
    row = cur.fetchone()
    cur.close()
    return row


def query_all(sql, params=()):
    cur = mysql.connection.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    return rows


def execute(sql, params=()):
    cur = mysql.connection.cursor()
    cur.execute(sql, params)
    mysql.connection.commit()
    cur.close()


# ------------------ Email helpers ------------------
def _send_email(to_addr, subject, html_body):
    """Send an HTML email via SMTP. Returns True on success, False on failure."""
    smtp_email = app.config.get("SMTP_EMAIL", "")
    smtp_password = app.config.get("SMTP_PASSWORD", "")
    if not smtp_email or not smtp_password:
        app.logger.warning("SMTP not configured – skipping email send.")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{app.config.get('SMTP_DISPLAY_NAME', 'MediFlow')} <{smtp_email}>"
        msg["To"] = to_addr
        msg.attach(MIMEText(html_body, "html", "utf-8"))
        ctx = ssl.create_default_context()
        with smtplib.SMTP(app.config["SMTP_HOST"], app.config["SMTP_PORT"]) as srv:
            srv.ehlo()
            srv.starttls(context=ctx)
            srv.login(smtp_email, smtp_password)
            srv.sendmail(smtp_email, to_addr, msg.as_string())
        return True
    except Exception as exc:
        app.logger.error(f"Email send failed: {exc}")
        return False


def _reset_token(email):
    s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    return s.dumps(email, salt="pw-reset")


def _verify_reset_token(token, max_age=3600):
    s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    try:
        return s.loads(token, salt="pw-reset", max_age=max_age)
    except (SignatureExpired, BadSignature):
        return None


def _email_verify_token(email):
    s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    return s.dumps(email, salt="email-verify")


def _verify_email_token(token, max_age=86400):  # 24 hours
    s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    try:
        return s.loads(token, salt="email-verify", max_age=max_age)
    except (SignatureExpired, BadSignature):
        return None


def _email_change_token(user_id, new_email):
    s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    return s.dumps({"user_id": user_id, "new_email": new_email}, salt="email-change")


def _verify_email_change_token(token, max_age=86400):  # 24 hours
    s = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    try:
        return s.loads(token, salt="email-change", max_age=max_age)
    except (SignatureExpired, BadSignature):
        return None


def _email_reset_html(reset_url):
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#070b14;font-family:Arial,Helvetica,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:48px 16px">
<table width="560" cellpadding="0" cellspacing="0" style="background:#0f172a;border-radius:18px;border:1px solid rgba(255,255,255,.14);overflow:hidden">
  <tr><td style="background:linear-gradient(135deg,#7c3aed,#2563eb);padding:28px 32px;text-align:center">
    <img src="https://res.cloudinary.com/ddrlxvnsh/image/upload/v1775064288/logo_kyqvgv.png" alt="MediFlow" style="height:48px;display:block;margin:0 auto 8px">
    <p style="margin:6px 0 0;color:rgba(255,255,255,.7);font-size:.88rem">Hospital Management System</p>
  </td></tr>
  <tr><td style="padding:32px">
    <h2 style="margin:0 0 14px;color:#ebf2ff;font-size:1.35rem">Reset Your Password</h2>
    <p style="margin:0 0 24px;color:#9fb1d1;line-height:1.65;font-size:.95rem">
      We received a request to reset the password for your MediFlow account.
      Click the button below to set a new password. <strong style="color:#ebf2ff">This link expires in 1 hour.</strong>
    </p>
    <div style="text-align:center;margin:28px 0">
      <a href="{reset_url}" style="display:inline-block;padding:14px 36px;border-radius:12px;
         background:linear-gradient(135deg,#7c3aed,#2563eb);color:#fff;text-decoration:none;
         font-weight:700;font-size:.97rem;letter-spacing:.01em">Reset Password</a>
    </div>
    <p style="margin:24px 0 0;color:#9fb1d1;font-size:.83rem;line-height:1.55">
      If you did not request this, you can safely ignore this email — your password will not change.
    </p>
  </td></tr>
  <tr><td style="padding:16px 32px;border-top:1px solid rgba(255,255,255,.08);text-align:center">
    <p style="margin:0;color:#9fb1d1;font-size:.78rem">© 2026 MediFlow · Hospital Management System</p>
  </td></tr>
</table>
</td></tr></table>
</body></html>"""


def _email_welcome_html(first_name):
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#070b14;font-family:Arial,Helvetica,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:48px 16px">
<table width="560" cellpadding="0" cellspacing="0" style="background:#0f172a;border-radius:18px;border:1px solid rgba(255,255,255,.14);overflow:hidden">
  <tr><td style="background:linear-gradient(135deg,#7c3aed,#2563eb);padding:28px 32px;text-align:center">
    <img src="https://res.cloudinary.com/ddrlxvnsh/image/upload/v1775064288/logo_kyqvgv.png" alt="MediFlow" style="height:48px;display:block;margin:0 auto 8px">
    <p style="margin:6px 0 0;color:rgba(255,255,255,.7);font-size:.88rem">Hospital Management System</p>
  </td></tr>
  <tr><td style="padding:32px">
    <h2 style="margin:0 0 14px;color:#ebf2ff;font-size:1.35rem">Welcome, {first_name}! 🎉</h2>
    <p style="margin:0 0 16px;color:#9fb1d1;line-height:1.65;font-size:.95rem">
      Your MediFlow account has been created successfully. You can now manage doctors, patients,
      and appointments from your dashboard.
    </p>
    <div style="background:rgba(124,58,237,.12);border:1px solid rgba(124,58,237,.3);border-radius:12px;padding:16px;margin:20px 0">
      <p style="margin:0;color:#a78bfa;font-size:.9rem;font-weight:600">MediFlow · Hospital Management · Elegant Experience</p>
    </div>
    <p style="margin:20px 0 0;color:#9fb1d1;font-size:.83rem">
      If you did not create this account, please contact support immediately.
    </p>
  </td></tr>
  <tr><td style="padding:16px 32px;border-top:1px solid rgba(255,255,255,.08);text-align:center">
    <p style="margin:0;color:#9fb1d1;font-size:.78rem">© 2026 MediFlow · Hospital Management System</p>
  </td></tr>
</table>
</td></tr></table>
</body></html>"""


def _email_verify_html(first_name, verify_url):
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#070b14;font-family:Arial,Helvetica,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:48px 16px">
<table width="560" cellpadding="0" cellspacing="0" style="background:#0f172a;border-radius:18px;border:1px solid rgba(255,255,255,.14);overflow:hidden">
  <tr><td style="background:linear-gradient(135deg,#7c3aed,#2563eb);padding:28px 32px;text-align:center">
    <img src="https://res.cloudinary.com/ddrlxvnsh/image/upload/v1775064288/logo_kyqvgv.png" alt="MediFlow" style="height:48px;display:block;margin:0 auto 8px">
    <p style="margin:6px 0 0;color:rgba(255,255,255,.7);font-size:.88rem">Hospital Management System</p>
  </td></tr>
  <tr><td style="padding:32px">
    <h2 style="margin:0 0 14px;color:#ebf2ff;font-size:1.35rem">Confirm Your Email, {first_name}!</h2>
    <p style="margin:0 0 24px;color:#9fb1d1;line-height:1.65;font-size:.95rem">
      Thanks for signing up to MediFlow! Please click the button below to verify your email address
      and activate your account. <strong style="color:#ebf2ff">This link expires in 24 hours.</strong>
    </p>
    <div style="text-align:center;margin:28px 0">
      <a href="{verify_url}" style="display:inline-block;padding:14px 36px;border-radius:12px;
         background:linear-gradient(135deg,#7c3aed,#2563eb);color:#fff;text-decoration:none;
         font-weight:700;font-size:.97rem;letter-spacing:.01em">Verify My Email</a>
    </div>
    <p style="margin:24px 0 0;color:#9fb1d1;font-size:.83rem;line-height:1.55">
      If you did not create a MediFlow account, you can safely ignore this email.
    </p>
  </td></tr>
  <tr><td style="padding:16px 32px;border-top:1px solid rgba(255,255,255,.08);text-align:center">
    <p style="margin:0;color:#9fb1d1;font-size:.78rem">© 2026 MediFlow · Hospital Management System</p>
  </td></tr>
</table>
</td></tr></table>
</body></html>"""


def _email_change_confirm_html(first_name, confirm_url, new_email):
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#070b14;font-family:Arial,Helvetica,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:48px 16px">
<table width="560" cellpadding="0" cellspacing="0" style="background:#0f172a;border-radius:18px;border:1px solid rgba(255,255,255,.14);overflow:hidden">
  <tr><td style="background:linear-gradient(135deg,#7c3aed,#2563eb);padding:28px 32px;text-align:center">
    <img src="https://res.cloudinary.com/ddrlxvnsh/image/upload/v1775064288/logo_kyqvgv.png" alt="MediFlow" style="height:48px;display:block;margin:0 auto 8px">
    <p style="margin:6px 0 0;color:rgba(255,255,255,.7);font-size:.88rem">Hospital Management System</p>
  </td></tr>
  <tr><td style="padding:32px">
    <h2 style="margin:0 0 14px;color:#ebf2ff;font-size:1.35rem">Confirm Your New Email, {first_name}!</h2>
    <p style="margin:0 0 10px;color:#9fb1d1;line-height:1.65;font-size:.95rem">
      You requested to change your MediFlow account email to <strong style="color:#ebf2ff">{new_email}</strong>.
      Click the button below to confirm this change. <strong style="color:#ebf2ff">This link expires in 24 hours.</strong>
    </p>
    <div style="text-align:center;margin:28px 0">
      <a href="{confirm_url}" style="display:inline-block;padding:14px 36px;border-radius:12px;
         background:linear-gradient(135deg,#7c3aed,#2563eb);color:#fff;text-decoration:none;
         font-weight:700;font-size:.97rem;letter-spacing:.01em">Confirm Email Change</a>
    </div>
    <p style="margin:24px 0 0;color:#9fb1d1;font-size:.83rem;line-height:1.55">
      If you did not request this change, you can safely ignore this email — your current email will remain unchanged.
    </p>
  </td></tr>
  <tr><td style="padding:16px 32px;border-top:1px solid rgba(255,255,255,.08);text-align:center">
    <p style="margin:0;color:#9fb1d1;font-size:.78rem">© 2026 MediFlow · Hospital Management System</p>
  </td></tr>
</table>
</td></tr></table>
</body></html>"""


# ------------------ Auth ------------------
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")

        if not all([first_name, last_name, email, phone, password]):
            flash("All fields are required.", "danger")
            return redirect(url_for("signup"))

        existing = query_one("SELECT id FROM users WHERE email=%s", (email,))
        if existing:
            flash("Email already exists. Please login.", "warning")
            return redirect(url_for("login"))

        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        execute("""
            INSERT INTO users (first_name, last_name, email, phone, password_hash, email_verified)
            VALUES (%s, %s, %s, %s, %s, 0)
        """, (first_name, last_name, email, phone, password_hash))

        token = _email_verify_token(email)
        verify_url = url_for("verify_email", token=token, _external=True)
        _send_email(
            email,
            "MediFlow – Please Confirm Your Email",
            _email_verify_html(first_name, verify_url)
        )

        return redirect(url_for("verify_pending", email=email))

    return render_template("signup.html")


@app.route("/verify-pending")
def verify_pending():
    email = request.args.get("email", "")
    return render_template("verify_email_pending.html", email=email)


@app.route("/resend-verification", methods=["POST"])
def resend_verification():
    email = request.form.get("email", "").strip().lower()
    user = query_one("SELECT id, first_name, email_verified FROM users WHERE email=%s", (email,))
    if user and not user[2]:
        token = _email_verify_token(email)
        verify_url = url_for("verify_email", token=token, _external=True)
        _send_email(
            email,
            "MediFlow – Confirm Your Email (Resent)",
            _email_verify_html(user[1], verify_url)
        )
    # Always show same message to prevent email enumeration
    flash("If that address is registered and unverified, a new link has been sent.", "info")
    return redirect(url_for("verify_pending", email=email))


@app.route("/verify-email/<token>")
def verify_email(token):
    email = _verify_email_token(token)
    if not email:
        flash("This verification link is invalid or has expired. Please request a new one.", "danger")
        return redirect(url_for("login"))
    user = query_one("SELECT id, email_verified FROM users WHERE email=%s", (email,))
    if not user:
        flash("Account not found.", "danger")
        return redirect(url_for("login"))
    if user[1]:
        flash("Your email is already verified. Please log in.", "info")
        return redirect(url_for("login"))
    execute("UPDATE users SET email_verified=1 WHERE email=%s", (email,))
    flash("Email verified successfully! You can now log in.", "success")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = query_one("""
            SELECT id, first_name, last_name, email, password_hash, email_verified
            FROM users
            WHERE email=%s
        """, (email,))

        if user and bcrypt.checkpw(password.encode("utf-8"), user[4].encode("utf-8")):
            if not user[5]:
                return redirect(url_for("verify_pending", email=email))
            session["user_id"] = user[0]
            session["user_name"] = f"{user[1]} {user[2]}"
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))


# ------------------ Dashboard ------------------
@app.route("/dashboard")
@login_required
def dashboard():
    doctors_count = query_one("SELECT COUNT(*) FROM doctors")[0]
    patients_count = query_one("SELECT COUNT(*) FROM patients")[0]
    appointments_count = query_one("SELECT COUNT(*) FROM appointments")[0]

    today = date.today().isoformat()
    today_appointments = query_all("""
        SELECT a.id, p.name, d.name, a.appointment_time, a.status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        WHERE a.appointment_date = %s
        ORDER BY a.appointment_time ASC
    """, (today,))

    status_data = query_all("""
        SELECT status, COUNT(*) as count
        FROM appointments
        GROUP BY status
    """)

    return render_template(
        "dashboard.html",
        doctors_count=doctors_count,
        patients_count=patients_count,
        appointments_count=appointments_count,
        today_appointments=today_appointments,
        status_data=status_data
    )


# ------------------ Doctors ------------------
@app.route("/doctors")
@login_required
def doctors():
    PER_PAGE = 10
    page = max(1, request.args.get("page", 1, type=int))
    offset = (page - 1) * PER_PAGE
    total = query_one("SELECT COUNT(*) FROM doctors")[0]
    rows = query_all("SELECT * FROM doctors ORDER BY id DESC LIMIT %s OFFSET %s", (PER_PAGE, offset))
    total_pages = (total + PER_PAGE - 1) // PER_PAGE
    return render_template("doctors.html", doctors=rows, page=page, total_pages=total_pages, total=total)


@app.route("/doctors/add", methods=["GET", "POST"])
@login_required
def add_doctor():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        specialty = request.form.get("specialty", "").strip()
        available_days = ",".join(request.form.getlist("available_days"))
        phone = request.form.get("phone", "").strip()

        if not all([name, specialty, available_days, phone]):
            flash("All fields are required.", "danger")
            return redirect(url_for("add_doctor"))

        execute("""
            INSERT INTO doctors (name, specialty, available_days, phone)
            VALUES (%s, %s, %s, %s)
        """, (name, specialty, available_days, phone))

        flash("Doctor added successfully.", "success")
        return redirect(url_for("doctors"))

    return render_template("add_doctor.html")


@app.route("/doctors/edit/<int:doctor_id>", methods=["GET", "POST"])
@login_required
def edit_doctor(doctor_id):
    doctor = query_one("SELECT * FROM doctors WHERE id=%s", (doctor_id,))
    if not doctor:
        flash("Doctor not found.", "danger")
        return redirect(url_for("doctors"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        specialty = request.form.get("specialty", "").strip()
        available_days = ",".join(request.form.getlist("available_days"))
        phone = request.form.get("phone", "").strip()

        if not all([name, specialty, available_days, phone]):
            flash("All fields are required.", "danger")
            return redirect(url_for("edit_doctor", doctor_id=doctor_id))

        execute("""
            UPDATE doctors
            SET name=%s, specialty=%s, available_days=%s, phone=%s
            WHERE id=%s
        """, (name, specialty, available_days, phone, doctor_id))

        flash("Doctor updated successfully.", "success")
        return redirect(url_for("doctors"))

    return render_template("edit_doctor.html", doctor=doctor)


@app.route("/doctors/delete/<int:doctor_id>", methods=["POST"])
@login_required
def delete_doctor(doctor_id):
    execute("DELETE FROM doctors WHERE id=%s", (doctor_id,))
    flash("Doctor deleted successfully.", "info")
    return redirect(url_for("doctors"))


# ------------------ Patients ------------------
@app.route("/patients")
@login_required
def patients():
    PER_PAGE = 10
    page = max(1, request.args.get("page", 1, type=int))
    offset = (page - 1) * PER_PAGE
    total = query_one("SELECT COUNT(*) FROM patients")[0]
    rows = query_all("SELECT * FROM patients ORDER BY id DESC LIMIT %s OFFSET %s", (PER_PAGE, offset))
    total_pages = (total + PER_PAGE - 1) // PER_PAGE
    return render_template("patients.html", patients=rows, page=page, total_pages=total_pages, total=total)


@app.route("/patients/add", methods=["GET", "POST"])
@login_required
def add_patient():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()
        phone = request.form.get("phone", "").strip()

        if not all([name, age, gender, phone]):
            flash("All fields are required.", "danger")
            return redirect(url_for("add_patient"))

        execute("""
            INSERT INTO patients (name, age, gender, phone)
            VALUES (%s, %s, %s, %s)
        """, (name, age, gender, phone))

        flash("Patient added successfully.", "success")
        return redirect(url_for("patients"))

    return render_template("add_patient.html")


@app.route("/patients/edit/<int:patient_id>", methods=["GET", "POST"])
@login_required
def edit_patient(patient_id):
    patient = query_one("SELECT * FROM patients WHERE id=%s", (patient_id,))
    if not patient:
        flash("Patient not found.", "danger")
        return redirect(url_for("patients"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        gender = request.form.get("gender", "").strip()
        phone = request.form.get("phone", "").strip()

        if not all([name, age, gender, phone]):
            flash("All fields are required.", "danger")
            return redirect(url_for("edit_patient", patient_id=patient_id))

        execute("""
            UPDATE patients
            SET name=%s, age=%s, gender=%s, phone=%s
            WHERE id=%s
        """, (name, age, gender, phone, patient_id))

        flash("Patient updated successfully.", "success")
        return redirect(url_for("patients"))

    return render_template("edit_patient.html", patient=patient)


@app.route("/patients/delete/<int:patient_id>", methods=["POST"])
@login_required
def delete_patient(patient_id):
    execute("DELETE FROM patients WHERE id=%s", (patient_id,))
    flash("Patient deleted successfully.", "info")
    return redirect(url_for("patients"))


# ------------------ Appointments ------------------
@app.route("/appointments")
@login_required
def appointments():
    PER_PAGE = 10
    page = max(1, request.args.get("page", 1, type=int))
    offset = (page - 1) * PER_PAGE
    total = query_one("SELECT COUNT(*) FROM appointments")[0]
    rows = query_all("""
        SELECT a.id, p.name, d.name, a.appointment_date, a.appointment_time, a.status, a.symptoms
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
        LIMIT %s OFFSET %s
    """, (PER_PAGE, offset))
    total_pages = (total + PER_PAGE - 1) // PER_PAGE
    return render_template("appointments.html", appointments=rows, page=page, total_pages=total_pages, total=total)


@app.route("/appointments/book", methods=["GET", "POST"])
@login_required
def book_appointment():
    doctors = query_all("SELECT id, name FROM doctors ORDER BY name ASC")
    patients = query_all("SELECT id, name FROM patients ORDER BY name ASC")

    if request.method == "POST":
        patient_id = request.form.get("patient_id", "").strip()
        doctor_id = request.form.get("doctor_id", "").strip()
        appointment_date = request.form.get("appointment_date", "").strip()
        appointment_time = request.form.get("appointment_time", "").strip()
        symptoms = request.form.get("symptoms", "").strip()

        if not all([patient_id, doctor_id, appointment_date, appointment_time]):
            flash("Please fill all required fields.", "danger")
            return redirect(url_for("book_appointment"))

        execute("""
            INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, symptoms)
            VALUES (%s, %s, %s, %s, %s)
        """, (patient_id, doctor_id, appointment_date, appointment_time, symptoms))

        flash("Appointment booked successfully.", "success")
        return redirect(url_for("appointments"))

    return render_template("book_appointment.html", doctors=doctors, patients=patients)


@app.route("/appointments/status/<int:appointment_id>", methods=["POST"])
@login_required
def update_appointment_status(appointment_id):
    status = request.form.get("status", "Scheduled")
    if status not in ["Scheduled", "Completed", "Cancelled"]:
        flash("Invalid status.", "danger")
        return redirect(url_for("appointments"))

    execute("UPDATE appointments SET status=%s WHERE id=%s", (status, appointment_id))
    flash("Appointment status updated.", "success")
    return redirect(url_for("appointments"))


@app.route("/appointments/delete/<int:appointment_id>", methods=["POST"])
@login_required
def delete_appointment(appointment_id):
    execute("DELETE FROM appointments WHERE id=%s", (appointment_id,))
    flash("Appointment deleted successfully.", "info")
    return redirect(url_for("appointments"))


# ------------------ Settings / Profile ------------------
@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    user = query_one("SELECT * FROM users WHERE id=%s", (session["user_id"],))
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "profile":
            first_name = request.form.get("first_name", "").strip()
            last_name = request.form.get("last_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            phone = request.form.get("phone", "").strip()

            if not all([first_name, last_name, email, phone]):
                flash("All profile fields are required.", "danger")
                return redirect(url_for("settings"))

            # Handle email change via confirmation
            if email != user[3]:
                existing = query_one(
                    "SELECT id FROM users WHERE email=%s AND id != %s",
                    (email, session["user_id"])
                )
                if existing:
                    flash("That email is already in use by another account.", "warning")
                    return redirect(url_for("settings"))

                # Send confirmation email to the NEW address
                token = _email_change_token(session["user_id"], email)
                confirm_url = url_for("confirm_email_change", token=token, _external=True)
                sent = _send_email(
                    email,
                    "MediFlow – Confirm Your New Email",
                    _email_change_confirm_html(first_name, confirm_url, email)
                )
                if sent:
                    flash(f"A confirmation link has been sent to {email}. Please verify to complete the email change.", "info")
                else:
                    flash("Could not send confirmation email. Check your SMTP settings.", "warning")

                # Update everything except email
                execute(
                    "UPDATE users SET first_name=%s, last_name=%s, phone=%s WHERE id=%s",
                    (first_name, last_name, phone, session["user_id"])
                )
                session["user_name"] = f"{first_name} {last_name}"
                return redirect(url_for("settings"))

            execute(
                "UPDATE users SET first_name=%s, last_name=%s, email=%s, phone=%s WHERE id=%s",
                (first_name, last_name, email, phone, session["user_id"])
            )
            session["user_name"] = f"{first_name} {last_name}"
            flash("Profile updated successfully.", "success")
            return redirect(url_for("settings"))

        if action == "password":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            if not bcrypt.checkpw(current_password.encode("utf-8"), user[5].encode("utf-8")):
                flash("Current password is incorrect.", "danger")
                return redirect(url_for("settings"))

            if new_password != confirm_password:
                flash("New passwords do not match.", "danger")
                return redirect(url_for("settings"))

            if len(new_password) < 8:
                flash("New password must be at least 8 characters.", "danger")
                return redirect(url_for("settings"))

            new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            execute("UPDATE users SET password_hash=%s WHERE id=%s", (new_hash, session["user_id"]))
            flash("Password updated successfully.", "success")
            return redirect(url_for("settings"))

    return render_template("settings.html", user=user)


# ------------------ Email Change Confirmation ------------------
@app.route("/confirm-email-change/<token>")
@login_required
def confirm_email_change(token):
    data = _verify_email_change_token(token)
    if not data:
        flash("The email confirmation link is invalid or has expired.", "danger")
        return redirect(url_for("settings"))

    user_id = data.get("user_id")
    new_email = data.get("new_email")

    if user_id != session["user_id"]:
        flash("This confirmation link does not belong to your account.", "danger")
        return redirect(url_for("settings"))

    # Check the new email is not taken by someone else
    existing = query_one("SELECT id FROM users WHERE email=%s AND id != %s", (new_email, user_id))
    if existing:
        flash("That email is already in use by another account.", "warning")
        return redirect(url_for("settings"))

    execute("UPDATE users SET email=%s WHERE id=%s", (new_email, user_id))
    flash("Your email address has been updated successfully.", "success")
    return redirect(url_for("settings"))


# ------------------ Forgot / Reset Password ------------------
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = query_one("SELECT id, first_name FROM users WHERE email=%s", (email,))

        # Always show success to prevent email enumeration
        if user:
            token = _reset_token(email)
            reset_url = url_for("reset_password", token=token, _external=True)
            _send_email(email, "MediFlow – Reset Your Password", _email_reset_html(reset_url))

        flash("If an account with that email exists, a reset link has been sent.", "info")
        return redirect(url_for("forgot_password"))

    return render_template("forgot_password.html")


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    email = _verify_reset_token(token)
    if not email:
        flash("This reset link is invalid or has expired. Please request a new one.", "danger")
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("reset_password", token=token))

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "danger")
            return redirect(url_for("reset_password", token=token))

        new_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        execute("UPDATE users SET password_hash=%s WHERE email=%s", (new_hash, email))
        flash("Password reset successfully. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html", token=token)


if __name__ == "__main__":
    app.run(debug=True)