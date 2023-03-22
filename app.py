from flask import Flask
from flask import render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash
from os import getenv

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)
app.secret_key = getenv("SECRET_KEY")


@app.route("/")
def index():
    result = db.session.execute(text("SELECT * FROM users"))
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/loginsubmit", methods=["POST"])
def loginsubmit():
    username = request.form["username"]
    password = request.form["password"]
    session["username"] = username
    return redirect("/")

@app.route("/signupsubmit", methods=["POST"])
def signupsubmit():
    username = request.form["username"]
    password = request.form["password"]
    userlevel="user"
    hash_value = generate_password_hash(password)
    sql = text("INSERT INTO users (username, password, userlevel) VALUES (:username, :password, :userlevel)")
    db.session.execute(sql, {"username":username, "password":hash_value, "userlevel":userlevel})
    db.session.commit()
    return redirect("/success")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/success")
def success():
    return render_template("success.html")