from flask import Flask, render_template, request, redirect, url_for
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.environ.get("DB_PATH", "students.db")

TASKS_ADDED = Counter("todo_tasks_added_total", "Tasks added")
TASKS_COMPLETED = Counter("todo_tasks_completed_total", "Tasks completed")
TASKS_DELETED = Counter("todo_tasks_deleted_total", "Tasks deleted")


def connect_db():
    return sqlite3.connect(DB_PATH)


def init_db():
    with connect_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
        """)


@app.route("/")
def index():
    with connect_db() as db:
        tasks = db.execute(
            "SELECT id, title, completed FROM tasks ORDER BY id DESC"
        ).fetchall()
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()
    if title:
        with connect_db() as db:
            db.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        TASKS_ADDED.inc()
    return redirect(url_for("index"))


@app.route("/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    with connect_db() as db:
        cursor = db.execute(
            "UPDATE tasks SET completed = 1 WHERE id = ? AND completed = 0",
            (task_id,)
        )
        if cursor.rowcount:
            TASKS_COMPLETED.inc()
    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    with connect_db() as db:
        cursor = db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cursor.rowcount:
            TASKS_DELETED.inc()
    return redirect(url_for("index"))


@app.route("/health")
def health():
    return {"status": "healthy"}, 200


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)