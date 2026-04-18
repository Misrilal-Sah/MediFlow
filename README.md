<div align="center">
  <img src="https://res.cloudinary.com/ddrlxvnsh/image/upload/v1775064288/logo_kyqvgv.png" alt="MediFlow Logo" height="80">

  # MediFlow
  ### Hospital Management System

  ![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
  ![Flask](https://img.shields.io/badge/Flask-3.0.3-black?logo=flask&logoColor=white)
  ![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-orange?logo=mysql&logoColor=white)
  ![License](https://img.shields.io/badge/License-MIT-green)
</div>

---

MediFlow is a full-stack web application for managing hospital operations â€” doctors, patients, and appointments â€” built with Flask and MySQL. It features a modern dark/light-mode UI, email-verified authentication, and a responsive collapsible sidebar.

## Features

- **Authentication** â€” Signup with email verification, login, forgot/reset password via secure tokenized email links
- **Doctors** â€” Add, edit, delete doctors with specialization, availability days, and fee
- **Patients** â€” Full patient records with contact details and history
- **Appointments** â€” Book, manage, and track appointments with status (Scheduled / Completed / Cancelled)
- **Dashboard** â€” Stats overview with charts, recent appointments timeline, and quick-access cards
- **Settings** â€” Update profile, change password, email change with confirmation link
- **Theme** â€” Dark / Light mode toggle, persisted per browser
- **Responsive UI** â€” Collapsible sidebar with SVG icons, glass morphism design
- **Email notifications** â€” Welcome email on signup, email verification, password reset, email change confirmation

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, Flask 3.0 |
| Database | MySQL 8.0+ |
| ORM/Driver | Flask-MySQLdb |
| Auth | bcrypt (password hashing), itsdangerous (signed tokens) |
| Email | smtplib + MIME (SMTP via Gmail) |
| Frontend | Vanilla JS, CSS3 (custom design system, no framework) |
| Templating | Jinja2 |

## Project Structure

```
mediflow/
â”œâ”€â”€ app.py              # Main Flask application & all routes
â”œâ”€â”€ config.py           # Config loaded from .env
â”œâ”€â”€ requirements.txt    # Python dependencies
â”œâ”€â”€ schema.sql          # Database schema (CREATE TABLE statements)
â”œâ”€â”€ seed.sql            # Optional seed data
â”œâ”€â”€ .env.example        # Environment variable template
â”œâ”€â”€ static/
â”‚   â”œâ”€â”€ css/style.css   # Full custom design system
â”‚   â””â”€â”€ js/script.js    # Theme toggle, sidebar, modals, toasts
â””â”€â”€ templates/
    â”œâ”€â”€ base.html               # Base layout (sidebar, topbar, loader)
    â”œâ”€â”€ dashboard.html
    â”œâ”€â”€ doctors.html / add_doctor.html / edit_doctor.html
    â”œâ”€â”€ patients.html / add_patient.html / edit_patient.html
    â”œâ”€â”€ appointments.html / book_appointment.html
    â”œâ”€â”€ settings.html
    â”œâ”€â”€ login.html / signup.html
    â”œâ”€â”€ forgot_password.html / reset_password.html
    â””â”€â”€ verify_email_pending.html
```

## Getting Started

### Prerequisites

- Python 3.10+
- MySQL 8.0+

### 1. Clone the repository

```bash
git clone https://github.com/Misrilal-Sah/MediFlow.git
cd MediFlow
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
SECRET_KEY=your_random_secret_key

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=hospital_management

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_DISPLAY_NAME=MediFlow
```

### 5. Set up the database

```bash
mysql -u root -p
```

```sql
CREATE DATABASE hospital_management;
USE hospital_management;
SOURCE schema.sql;
-- Optional: SOURCE seed.sql;
```

### 6. Run the application

```bash
python app.py
```

Visit `http://127.0.0.1:5000` in your browser.


## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask session secret | *(required)* |
| `MYSQL_HOST` | MySQL host | `127.0.0.1` |
| `MYSQL_PORT` | MySQL port | `3306` |
| `MYSQL_USER` | MySQL username | `root` |
| `MYSQL_PASSWORD` | MySQL password | *(required)* |
| `MYSQL_DB` | Database name | `hospital_management` |
| `SMTP_HOST` | SMTP server host | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_EMAIL` | Sender email address | *(required for email features)* |
| `SMTP_PASSWORD` | SMTP App Password | *(required for email features)* |
| `SMTP_DISPLAY_NAME` | Display name in emails | `MediFlow` |



## Screenshots

The dashboard features live stats, a doughnut chart for appointment status distribution, and a timeline of upcoming appointments.

> UI screenshots coming soon. Run the app locally to preview.

## Roadmap

- [ ] Role-based access control (Admin / Doctor / Receptionist)
- [ ] Patient medical history & prescription records
- [ ] Appointment reminders via email
- [ ] Invoice & billing module
- [ ] REST API for mobile integration
- [ ] Docker support for easy deployment

### v1.0.0
- Initial release: doctors, patients, appointments, dashboard
- Email verification flow with tokenized links
- Dark / Light mode toggle


## License

MIT Â© Misrilal Sah


