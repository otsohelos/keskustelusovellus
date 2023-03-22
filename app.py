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

cache = {}
cache["message"] = ""
cache["content"] = ""


@app.route("/")
def index():
    result = db.session.execute(text("SELECT * FROM conversations"))
    return render_template("index.html", conversations=result)


@app.route("/login")
def login():
    message = cache["message"]
    cache["message"] = ""
    return render_template("login.html", message=message)


@app.route("/signup")
def signup():
    message = cache["message"]
    cache["message"] = ""
    return render_template("signup.html", message=message)


@app.route("/loginsubmit", methods=["POST"])
def loginsubmit():
    username = request.form["username"]
    password = request.form["password"]
    sql = text("SELECT id, password FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()
    if not user:
        # TODO: invalid username
        cache["message"] = "Käyttäjänimeä ei löydy"
        return redirect("/login")
    else:
        hash_value = user.password
    if check_password_hash(hash_value, password):
        session["username"] = username
    else:
        cache["message"] = "Väärä salasana"
        return redirect("/login")
    return redirect("/")


@app.route("/signupsubmit", methods=["POST"])
def signupsubmit():
    username = request.form["username"]
    password = request.form["password"]
    userlevel = "user"
    hash_value = generate_password_hash(password)
    sql = text("SELECT id, password FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()
    if not user:
        sql = text(
            "INSERT INTO users (username, password, userlevel) VALUES (:username, :password, :userlevel)")
        db.session.execute(
            sql, {"username": username, "password": hash_value, "userlevel": userlevel})
        db.session.commit()
        return redirect("/signupsuccess")
    else:
        cache["message"] = "Käyttäjänimi {} on jo olemassa. Valitse toinen käyttäjänimi.".format(
            username)
        return redirect("/signup")


@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")


@app.route("/signupsuccess")
def signupsuccess():
    return render_template("signupsuccess.html")


@app.route("/newconversation")
def newconversation():
    message = cache["message"]
    cache["message"] = ""
    message_content = cache["content"]
    cache["content"] = ""
    return render_template("newconversation.html", message=message, content=message_content)


@app.route("/newconversationsubmit", methods=["POST"])
def newconversationsubmit():
    header = request.form.get("convo-header", "")
    content = request.form.get("convo-content", "")
    if header == "":
        cache["content"] = content
        cache["message"] = "Otsikko on pakollinen"
        return redirect("/newconversation")
    else:
        username = session["username"]
        sql = text(
            "INSERT INTO conversations (username, header, content) VALUES (:username, :header, :content)")
        db.session.execute(
            sql, {"username": username, "header": header, "content": content})
        db.session.commit()
        return redirect("/")


@app.route("/thread/<int:id>")
def thread(id):
    sql = text("SELECT username, header, content FROM conversations WHERE id=:id")
    result = db.session.execute(sql, {"id": id})
    message = result.fetchone()
    return render_template("thread.html", message=message)
