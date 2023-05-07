from app import app
from database_calls import *
from flask import render_template
from cache import cache
from flask import url_for, render_template, request, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash


@app.route("/")
def index():
    result = get_all()
    return render_template("index.html", conversations=result)


# Main, thread , and user pages
@app.route("/newconversation")
def newconversation():
    errormessage = cache["errormessage"]
    cache["errormessage"] = ""
    message_content = cache["content"]
    cache["content"] = ""
    message_header = cache["header"]
    cache["header"] = ""
    categories = get_categories()
    return render_template(
        "newconversation.html",
        errormessage=errormessage,
        content=message_content,
        categories=categories,
        header=message_header,
    )


@app.route("/thread/<int:thread_id>")
def thread(thread_id):
    errormessage = cache["errormessage"]
    cache["errormessage"] = ""
    message = get_thread(thread_id)
    replies = get_replies(thread_id)
    reply_to_edit = cache["reply_to_edit"]
    cache["reply_to_edit"] = 0
    content = cache["content"]
    cache["content"] = ""
    return render_template(
        "thread.html",
        message=message,
        errormessage=errormessage,
        replies=replies,
        reply_to_edit=reply_to_edit,
        content=content,
    )


@app.route("/category/<int:category_id>")
def category(category_id):
    conversations = get_by_category(category_id)
    category_name = get_category_name(category_id)
    return render_template("category.html",
                           conversations=conversations,
                           category=category_name)


@app.route("/user/<string:username>")
def user(username):
    this_user = get_user(username)
    this_userinfo = get_userinfo(this_user.id)
    this_about_me = this_userinfo.about_me.replace("\r", "<br>")
    return render_template("user.html", user=this_user, userinfo=this_userinfo, about_me=this_about_me)


@app.route("/editprofile/<string:username>")
def profile_edit(username):
    this_user = get_user(username)
    this_userinfo = get_userinfo(this_user.id)
    return render_template("editprofile.html", username=username, userinfo=this_userinfo)


# Login, signup, logout routes
@app.route("/login")
def login():
    errormessage = cache["errormessage"]
    cache["errormessage"] = ""
    return render_template("login.html", errormessage=errormessage)


@app.route("/signupsuccess")
def signupsuccess():
    return render_template("signupsuccess.html")


@app.route("/signup")
def signup():
    errormessage = cache["errormessage"]
    cache["errormessage"] = ""
    return render_template("signup.html", errormessage=errormessage)


@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")


# Submit form routes
@app.route("/userinfosubmit", methods=["POST"])
def userinfosubmit():
    display_name = request.form.get("display-name", "")
    email = request.form.get("email", "")
    email_is_public = False
    if request.form.get("email-is-public"):
        email_is_public = True
    about_me = request.form.get("about-me", "")
    edit_profile(session["username"], display_name,
                 email, email_is_public, about_me)
    return redirect(url_for("user", username=session["username"]))


@app.route("/loginsubmit", methods=["POST"])
def loginsubmit():
    username = request.form["username"]
    password = request.form["password"]
    user = get_user_login_info(username)
    if not user:
        cache["errormessage"] = "Käyttäjänimeä ei löydy"
        return redirect("/login")
    hash_value = user.password
    if check_password_hash(hash_value, password):
        session["username"] = username
    else:
        cache["errormessage"] = "Väärä salasana"
        return redirect("/login")
    return redirect("/")


@app.route("/signupsubmit", methods=["POST"])
def signupsubmit():
    username = request.form["username"]
    password = request.form["password"]
    user_level = "user"
    hash_value = generate_password_hash(password)
    found_user = get_user_login_info(username)
    if not found_user:
        create_user(username, hash_value, user_level)
        return redirect("/signupsuccess")
    cache["errormessage"] = "Käyttäjänimi {} on jo olemassa. Valitse toinen käyttäjänimi.".format(
        username)
    return redirect("/signup")


@app.route("/newconversationsubmit", methods=["POST"])
def newconversationsubmit():
    header = request.form.get("convo-header", "")
    content = request.form.get("convo-content", "")
    convo_category = int(request.form.get("convo-category", 0))
    if header == "":
        cache["content"] = content
        cache["errormessage"] = "Otsikko on pakollinen"
        return redirect("/newconversation")
    if convo_category == 0:
        cache["content"] = content
        cache["header"] = header
        cache["errormessage"] = "Valitse kategoria"
        return redirect("/newconversation")
    username = session["username"]
    submit_conversation(username, header, content, convo_category)
    return redirect("/")


@app.route("/replysubmit/<int:thread_id>", methods=["POST"])
def replysubmit(thread_id):
    content = request.form.get("reply-content", "")
    if content == "":
        cache["content"] = content
        cache["errormessage"] = "Kirjoita vastaus"
        return redirect(url_for("thread", thread_id=thread_id))
    username = session["username"]
    content_with_linebreaks = content  # .replace("<br>", "\r")
    submit_reply(username, content_with_linebreaks, thread_id)
    return redirect(url_for("thread", thread_id=thread_id))


@app.route("/replyeditsubmit/<int:id>", methods=["POST"])
def replyeditsubmit(id):
    content = request.form.get("reply-content", "")
    reply = get_reply(id)
    thread_id = reply.thread_id
    if content == "":
        cache["content"] = reply.content
        cache["reply_to_edit"] = id
        cache["errormessage"] = "Et voi muokata vastausta tyhjäksi"
        return redirect(url_for("thread", thread_id=thread_id))
    content_with_linebreaks = content  # .replace("<br>", "\r")
    edit_reply(id, content_with_linebreaks)
    return redirect(url_for("thread", thread_id=thread_id))


@app.route("/deletereply/<int:reply_id>")
def reply_delete(reply_id):
    reply = get_reply(reply_id)
    if not reply:
        cache["errormessage"] = "Tapahtui virhe. Yritä myöhemmin uudelleen."
        return redirect("/")
    if reply.username != session["username"]:
        cache["errormessage"] = "Tapahtui virhe. Yritä myöhemmin uudelleen."
        thread_id = reply.thread_id
        return redirect(url_for("thread", thread_id=thread_id))
    thread_id = reply.thread_id
    delete_reply(reply_id)
    return redirect(url_for("thread", thread_id=thread_id))


@app.route("/editreply/<int:id>")
def reply_edit(id):
    reply = get_reply(id)
    if not reply:
        cache["errormessage"] = "Tapahtui virhe. Yritä myöhemmin uudelleen."
        return redirect("/")
    if reply.username != session["username"]:
        cache["errormessage"] = "Tapahtui virhe. Yritä myöhemmin uudelleen."
        thread_id = reply.thread_id
        return redirect(url_for("thread", thread_id=thread_id))
    cache["content"] = reply.content
    reply_id = reply.id
    thread_id = reply.thread_id
    cache["reply_to_edit"] = reply_id
    return redirect(url_for("thread", thread_id=thread_id))
