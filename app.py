from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///otsohelos"
db = SQLAlchemy(app)
1
@app.route("/")
def index():
    result = db.session.execute(text("SELECT * FROM users"))
    names = result.fetchall()
    return render_template("index.html", names=names)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/signupsubmit", methods=["POST"])
def signupsubmit():
    username = request.form["username"]
    password = request.form["password"]
    userlevel="user"
    print(password)
    print(username)
    hash_value = generate_password_hash(password)
    sql = text("INSERT INTO users (username, password, userlevel) VALUES (:username, :password, :userlevel)")
    db.session.execute(sql, {"username":username, "password":hash_value, "userlevel":userlevel})
    db.session.commit()
    return redirect("/success")

@app.route("/success")
def success():
    return render_template("success.html")