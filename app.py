import datetime
import pytz
from flask import Flask, url_for
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
    errormessage = cache["message"]
    cache["message"] = ""
    return render_template("login.html", errormessage=errormessage)


@app.route("/signup")
def signup():
    errormessage = cache["message"]
    cache["message"] = ""
    return render_template("signup.html", errormessage=errormessage)


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
    errormessage = cache["message"]
    cache["message"] = ""
    message_content = cache["content"]
    cache["content"] = ""
    return render_template("newconversation.html", errormessage=errormessage, content=message_content)


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
    errormessage = cache["message"]
    cache["message"] = ""
    sql = text("SELECT username, header, content, id FROM conversations WHERE id=:id")
    result = db.session.execute(sql, {"id": id})
    message = result.fetchone()
    #message= message.replace("\r", "<br>")
    sql = text("SELECT * from replies where thread_id=:id AND deleted_at IS NULL")
    result = db.session.execute(sql, {"id": id})
    replies = result.fetchall()
    return render_template("thread.html", message=message, errormessage=errormessage, replies=replies)


@app.route("/replysubmit/<int:id>", methods=["POST"])
def replysubmit(id):
    content = request.form.get("reply-content", "")
    if content == "":
        cache["content"] = content
        cache["message"] = "Kirjoita vastaus"
        return redirect(url_for('thread', id=id))
    else:
        username = session["username"]
        content_with_linebreaks = content.replace("\r", "<br>")
        thread_id = id
        sql = text(
            "INSERT INTO replies (username, content, thread_id) VALUES (:username, :content, :thread_id)")
        db.session.execute(
            sql, {"username": username, "content": content_with_linebreaks, "thread_id": thread_id})
        db.session.commit()
        return redirect("/")

@app.route("/deletereply/<int:id>")
def deletereply(id):
    sql = text("SELECT * FROM replies WHERE id=:id")
    result = db.session.execute(sql, {"id": id})
    reply = result.fetchone()
    if not reply:
        cache["message"] = "Tapahtui virhe. Yritä myöhemmin uudelleen."
        return redirect("/")
    if reply.username != session["username"]:
        cache["message"] = "Tapahtui virhe. Yritä myöhemmin uudelleen."
        thread_id = reply.thread_id
        return redirect(url_for('thread', id=thread_id))
    else:
        id = reply.id
        thread_id = reply.thread_id
        sql = text("UPDATE replies SET deleted_at = :timestamp WHERE id=:id")
        timestamp = datetime.datetime.now(pytz.timezone("Europe/Helsinki"))
        db.session.execute(sql, {"id": id, "timestamp": timestamp})
        db.session.commit()
        return redirect(url_for('thread', id=thread_id))


@app.route("/editreply/<int:id>")
def editreply(id):
    return str(id)