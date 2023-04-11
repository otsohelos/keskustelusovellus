import datetime
import pytz
from flask import Flask, url_for
from flask import render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash
from os import getenv

# initialize database
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)
app.secret_key = getenv("SECRET_KEY")

# Initialize cache
cache = {}
cache["errormessage"] = ""
cache["content"] = ""
cache["header"] = ""
cache["reply_to_edit"] = 0

# Main, thread , and user pages
@app.route("/")
def index():
    result = db.session.execute(
        text("SELECT * FROM conversations LEFT JOIN categories ON conversations.category=categories.id ORDER BY conversations.id"))
    return render_template("index.html", conversations=result)


@app.route("/newconversation")
def newconversation():
    errormessage = cache["errormessage"]
    cache["errormessage"] = ""
    message_content = cache["content"]
    cache["content"] = ""
    message_header = cache["header"]
    cache["header"] = ""
    categories = db.session.execute(text("SELECT * from CATEGORIES"))
    return render_template("newconversation.html", errormessage=errormessage, content=message_content, categories=categories, header = message_header)


@app.route("/thread/<int:id>")
def thread(id):
    errormessage = cache["errormessage"]
    cache["errormessage"] = ""
    sql = text(
        "SELECT username, header, content, id FROM conversations WHERE id=:id")
    result = db.session.execute(sql, {"id": id})
    message = result.fetchone()
    sql = text(
        "SELECT * from replies where thread_id=:id AND deleted_at IS NULL ORDER BY id")
    result = db.session.execute(sql, {"id": id})
    replies = result.fetchall()
    reply_to_edit = cache["reply_to_edit"]
    cache["reply_to_edit"] = 0
    content = cache["content"]
    cache["content"] = ""
    return render_template("thread.html", message=message, errormessage=errormessage, replies=replies, reply_to_edit=reply_to_edit, content=content)


@app.route("/category/<int:category_id>")
def category(category_id):
    sql = text("SELECT * FROM conversations LEFT JOIN categories ON conversations.category=categories.id WHERE category=:category_id ORDER BY conversations.id")
    result = db.session.execute(sql, {"category_id": category_id})
    conversations = result.fetchall()
    sql = text("SELECT display_name FROM categories WHERE id=:category_id")
    result = db.session.execute(sql, {"category_id": category_id})
    category = result.fetchone().display_name
    return render_template("category.html", conversations=conversations, category=category)


@ app.route("/user/<string:username>")
def user(username):
    sql = text("SELECT * FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()
    return render_template("user.html", user=user)


# Login, signup, logout routes
@ app.route("/login")
def login():
    errormessage = cache["errormessage"]
    cache["errormessage"] = ""
    return render_template("login.html", errormessage=errormessage)


@ app.route("/signupsuccess")
def signupsuccess():
    return render_template("signupsuccess.html")


@ app.route("/signup")
def signup():
    errormessage = cache["errormessage"]
    cache["errormessage"] = ""
    return render_template("signup.html", errormessage=errormessage)


@ app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")


# Submit form routes
@ app.route("/loginsubmit", methods=["POST"])
def loginsubmit():
    username = request.form["username"]
    password = request.form["password"]
    sql = text("SELECT id, password FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()
    if not user:
        # TODO: invalid username
        cache["errormessage"] = "Käyttäjänimeä ei löydy"
        return redirect("/login")
    else:
        hash_value = user.password
    if check_password_hash(hash_value, password):
        session["username"] = username
    else:
        cache["errormessage"] = "Väärä salasana"
        return redirect("/login")
    return redirect("/")


@ app.route("/signupsubmit", methods=["POST"])
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
        cache["errormessage"] = "Käyttäjänimi {} on jo olemassa. Valitse toinen käyttäjänimi.".format(
            username)
        return redirect("/signup")


@ app.route("/newconversationsubmit", methods=["POST"])
def newconversationsubmit():
    header = request.form.get("convo-header", "")
    content = request.form.get("convo-content", "")
    category = int(request.form.get("convo-category", 0))
    if header == "":
        cache["content"] = content
        cache["errormessage"] = "Otsikko on pakollinen"
        return redirect("/newconversation")
    if category == 0:
        cache["content"] = content
        cache["header"] = header
        cache["errormessage"] = "Valitse kategoria"
        return redirect("/newconversation")
    else:
        username = session["username"]
        sql = text(
            "INSERT INTO conversations (username, header, content, category) VALUES (:username, :header, :content, :category)")
        db.session.execute(
            sql, {"username": username, "header": header, "content": content, "category": category})
        db.session.commit()
        return redirect("/")


@ app.route("/replysubmit/<int:id>", methods=["POST"])
def replysubmit(id):
    content = request.form.get("reply-content", "")
    if content == "":
        cache["content"] = content
        cache["errormessage"] = "Kirjoita vastaus"
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
        return redirect(url_for('thread', id=id))


@ app.route("/replyeditsubmit/<int:id>", methods=["POST"])
def replyeditsubmit(id):
    content = request.form.get("reply-content", "")
    sql = text(
        "SELECT * from replies where id=:id AND deleted_at IS NULL")
    result = db.session.execute(sql, {"id": id})
    reply = result.fetchone()
    thread_id = reply.thread_id
    if content == "":
        cache["content"] = reply.content
        cache["reply_to_edit"] = id
        cache["errormessage"] = "Et voi muokata vastausta tyhjäksi"
        return redirect(url_for('thread', id=thread_id))
    else:
        content_with_linebreaks = content.replace("\r", "<br>")
        sql = text("UPDATE replies SET content = :content WHERE id = :id")
        db.session.execute(sql, {"content": content_with_linebreaks, "id": id})
        db.session.commit()
        return redirect(url_for('thread', id=thread_id))


@app.route("/deletereply/<int:id>")
def deletereply(id):
    sql = text("SELECT * FROM replies WHERE id=:id")
    result = db.session.execute(sql, {"id": id})
    reply = result.fetchone()
    if not reply:
        cache["errormessage"] = "Tapahtui virhe. Yritä myöhemmin uudelleen."
        return redirect("/")
    if reply.username != session["username"]:
        cache["errormessage"] = "Tapahtui virhe. Yritä myöhemmin uudelleen."
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
    sql = text("SELECT * FROM replies WHERE id=:id")
    result = db.session.execute(sql, {"id": id})
    reply = result.fetchone()
    if not reply:
        cache["errormessage"] = "Tapahtui virhe. Yritä myöhemmin uudelleen."
        return redirect("/")
    if reply.username != session["username"]:
        cache["errormessage"] = "Tapahtui virhe. Yritä myöhemmin uudelleen."
        thread_id = reply.thread_id
        return redirect(url_for('thread', id=thread_id))
    else:
        cache["content"] = reply.content
        reply_id = reply.id
        thread_id = reply.thread_id
        cache["reply_to_edit"] = reply_id
        return redirect(url_for('thread', id=thread_id))
