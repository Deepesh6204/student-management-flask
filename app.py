from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "studenthub-change-this-secret"

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "students.db"


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                course TEXT NOT NULL
            )
        """)

        count = conn.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]

        if count == 0:
            conn.executemany(
                """
                INSERT INTO students (name, email, course)
                VALUES (?, ?, ?)
                """,
                [
                    ("Aarav Sharma", "aarav@example.com", "Python"),
                    ("Priya Verma", "priya@example.com", "Data Analytics"),
                    ("Rahul Singh", "rahul@example.com", "DevOps"),
                ],
            )


@app.route("/")
def home():
    with get_db() as conn:
        students = conn.execute(
            "SELECT * FROM students ORDER BY id DESC"
        ).fetchall()

        total = conn.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]

    return render_template(
        "index.html",
        students=students,
        total=total
    )


@app.route("/add", methods=["POST"])
def add_student():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    course = request.form.get("course", "").strip()

    if not name or not email or not course:
        flash("Please fill in all fields.", "error")
        return redirect(url_for("home"))

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO students (name, email, course)
            VALUES (?, ?, ?)
            """,
            (name, email, course),
        )

    flash("Student added successfully!", "success")
    return redirect(url_for("home"))


@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM students WHERE id = ?",
            (student_id,),
        )

    flash("Student deleted successfully!", "success")
    return redirect(url_for("home"))


# Initialize the database when the app starts.
init_db()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
