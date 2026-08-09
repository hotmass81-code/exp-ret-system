# Matumizi System — Makongo Juu SDA Church Finance Department

A full-featured Django web application for managing expense requests and retirement forms with a multi-level approval workflow.

---

## Features

- **Expense Request Module** — Create, edit, submit, and track expense requests with itemized line items
- **Retirement Form Module** — Submit and track retirement/accountability forms
- **3-Level Approval Workflow** — First Approver → Second Approver → Admin final approval
- **Notification System** — Real-time in-app notifications at each approval stage
- **Reports Dashboard** — Filter, search, and download PDF reports for expenses and retirements
- **Admin Panel** — Manage departments, approvers, registration codes, announcements, and users
- **PDF Download** — Professional SDA Church-branded PDF forms for each request
- **Role-Based Access** — Users, First Approvers, Second Approvers, and Admins

---

## Quick Start

### Requirements
- Python 3.10+
- pip

Open http://127.0.0.1:8000 in your browser.

---

## Deploying to Render

This project includes a `render.yaml` file for Render deployment.

### Render build command
```bash
pip install -r requirements.txt
```

### Render release command
```bash
cd matoleo_system && python manage.py collectstatic --noinput --clear
```

### Render start command
```bash
cd matoleo_system && gunicorn matoleo_system.wsgi:application --bind 0.0.0.0:$PORT
```

### Required Render environment variables
- `SECRET_KEY` — a strong random secret key
- `DJANGO_DEBUG` — `False`
- `ALLOWED_HOSTS` — e.g. `your-service.onrender.com`
- `CSRF_TRUSTED_ORIGINS` — e.g. `https://your-service.onrender.com`
- `DATABASE_URL` — Render Postgres connection string (or use the provided managed database service)

### Optional Render environment variables
- `EMAIL_HOST` — e.g. `smtp.gmail.com`
- `EMAIL_PORT` — `587`
- `EMAIL_USE_TLS` — `True`
- `EMAIL_HOST_USER` — SMTP username
- `EMAIL_HOST_PASSWORD` — SMTP password
- `DEFAULT_FROM_EMAIL` — sender email address
- `ADMIN_USERNAME` — admin username for auto-create/update
- `ADMIN_PASSWORD` — admin password for auto-create/update
- `ADMIN_EMAIL` — admin email for auto-create/update

### One-time deploy steps
After deploy, run:
```bash
cd matoleo_system
python manage.py migrate
python manage.py ensure_admin
```

---

## User Roles

| Role | Capabilities |
|------|-------------|
| **User** | Create/edit/submit expense & retirement forms, view own forms |
| **First Approver** | View and approve submitted forms for their department |
| **Second Approver** | View and approve first-approved forms |
| **Admin (Staff)** | Final approval, manage all users/departments/approvers, view all reports |

---

## Approval Workflow

```
User submits form
      ↓
First Approver (department-specific) approves
      ↓
Second Approver approves
      ↓
Admin gives final approval
      ↓
Form marked as APPROVED ✓
```

At each step, the next approver receives an in-app notification.

---

## Technology Stack

- **Backend**: Django 4.x, SQLite (easily switchable to PostgreSQL/MySQL)
- **Frontend**: Custom CSS (dark blue gradient), Bootstrap 5 grid, Font Awesome 6
- **PDF Generation**: ReportLab
- **Forms**: django-widget-tweaks, crispy-bootstrap5

---

*Developed for Makongo Juu SDA Church Finance Department — Matumizi System*
