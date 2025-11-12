
# Simple IT Ticket System (Flask + SQLite)

A tiny, self-hosted helpdesk your team can open in a browser.

## Features
- New ticket form (name, email, department, subject, description)
- 6‑digit PIN to track status
- Status page for employees
- Admin dashboard to view & close tickets
- SQLite database file `tickets.db`

## Quick Start
```bash
# 1) Create and activate a virtualenv (optional but recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Set admin password (recommended)
# Windows PowerShell:
$env:ADMIN_PASS="YourStrongPassword"
# macOS/Linux:
export ADMIN_PASS="YourStrongPassword"

# 4) Run
python app.py
```

Open http://localhost:5000

- `/` New ticket
- `/track` Track with PIN
- `/admin` Admin dashboard (enter ADMIN_PASS once to set cookie)

## Deploy
- Office PC (Windows/macOS/Linux)
- VPS (Ubuntu + `pip install -r requirements.txt` + `python app.py`)
- For production, run via Gunicorn or a WSGI server behind Nginx (optional)

## Backup
Back up `tickets.db` in the project folder periodically.
