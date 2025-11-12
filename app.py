import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, make_response, abort

APP_TITLE = "IT Helpdesk"
ADMIN_PASS = os.getenv("ADMIN_PASS", "changeme")
DB_PATH = os.path.join(os.path.dirname(__file__), "tickets.db")

app = Flask(__name__)

# === Database functions ===
def get_db():
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    with conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            department TEXT,
            subject TEXT,
            description TEXT,
            status TEXT DEFAULT 'open',
            pin TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
        """)
    conn.close()

def gen_pin():
    import random
    return f"{random.randint(100000, 999999)}"

# Initialize DB once (Flask 3.x safe)
init_db()

def render_base(template, **ctx):
    return render_template(template, app_title=APP_TITLE, **ctx)

# === Routes ===
@app.route("/")
def index():
    return render_base("new_ticket.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    department = request.form.get("department", "").strip()
    subject = request.form.get("subject", "").strip()
    description = request.form.get("description", "").strip()

    if not (email and subject and description and name):
        return render_base("new_ticket.html", error="Please fill all required fields."), 400

    pin = gen_pin()
    conn = get_db()
    with conn:
        cur = conn.execute("""
        INSERT INTO tickets (name, email, department, subject, description, pin)
        VALUES (?,?,?,?,?,?)
        """, (name, email, department, subject, description, pin))
        ticket_id = cur.lastrowid
    return render_base("created.html", ticket_id=ticket_id, pin=pin)

@app.route("/track")
def track():
    return render_base("track.html")

@app.route("/status")
def status_query():
    pin = request.args.get("pin")
    if not pin:
        return redirect(url_for("track"))
    return redirect(url_for("status_pin", pin=pin))

@app.route("/status/<pin>")
def status_pin(pin):
    conn = get_db()
    row = conn.execute("SELECT * FROM tickets WHERE pin = ? ORDER BY created_at DESC LIMIT 1", (pin,)).fetchone()
    conn.close()
    if not row:
        return render_base("not_found.html", msg="No ticket found for that PIN."), 404
    return render_base("status.html", t=row)

# === Admin ===
def is_admin():
    key = request.args.get("key") or request.cookies.get("admin_key")
    return key == ADMIN_PASS

@app.route("/admin")
def admin():
    if not is_admin():
        return render_base("admin_login.html")

    key = request.args.get("key")
    resp = make_response()

    conn = get_db()
    rows = conn.execute("SELECT * FROM tickets ORDER BY status != 'open', updated_at DESC").fetchall()
    conn.close()
    html = render_base("admin.html", tickets=rows)
    resp.set_data(html)

    if key == ADMIN_PASS and request.cookies.get("admin_key") != ADMIN_PASS:
        resp.set_cookie("admin_key", ADMIN_PASS, httponly=True, samesite="Lax")

    return resp

@app.post("/admin/close/<int:ticket_id>")
def admin_close(ticket_id):
    if not is_admin():
        abort(401)
    conn = get_db()
    with conn:
        conn.execute("UPDATE tickets SET status='closed', updated_at=datetime('now') WHERE id = ?", (ticket_id,))
    return redirect(url_for("admin"))

@app.get("/health")
def health():
    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
