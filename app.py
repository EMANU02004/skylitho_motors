from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secretkey"

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    db = get_db()
    cars = db.execute("SELECT * FROM cars WHERE status='available'").fetchall()
    return render_template('index.html', cars=cars)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        db = get_db()
        db.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
        (request.form["name"], request.form["email"], request.form["password"], "user"))
        db.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (request.form["email"], request.form["password"])
        ).fetchone()
        if user:
            session["user_id"] = user["id"]
            session["user_role"] = user["role"]
            return redirect(url_for("index"))
        else:
            return "Invalid credentials"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/car/<int:car_id>")
def car_details(car_id):
    db = get_db()
    car = db.execute("SELECT * FROM cars WHERE id=?", (car_id,)).fetchone()
    return render_template("car_details.html", car=car)

@app.route("/rent/<int:car_id>", methods=["POST"])
def rent_car(car_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    db = get_db()
    db.execute(
        "INSERT INTO rentals (user_id, car_id, rent_date) VALUES (?, ?, ?, ?)",
        (session["user_id"], car_id, datetime.now())
    )
    db.execute(
        "UPDATE cars SET status='rented' WHERE id=?",
        (car_id,)
    )
    db.commit()
    return redirect(url_for("index"))

@app.route("/admin")
def admin():
    db = get_db()
    cars = db.execute("SELECT * FROM cars").fetchall()
    return render_template("admin.html", cars=cars)

if __name__ == "__main__":
    app.run(debug=True)