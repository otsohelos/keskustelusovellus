from sqlalchemy import text
from db import db
import datetime
import pytz


def get_categories():
    categories = db.session.execute(text("SELECT * from CATEGORIES"))
    return categories


def get_all():
    result = db.session.execute(
        text("SELECT conversations.id as thread_id, username, header, content, deleted_at, categories.display_name as display_name, category FROM conversations LEFT JOIN categories ON conversations.category=categories.id ORDER BY conversations.id"))
    return result


def get_thread(thread_id):
    sql = text(
        "SELECT * FROM conversations LEFT JOIN categories ON conversations.category=categories.id WHERE conversations.id=:thread_id")
    result = db.session.execute(sql, {"thread_id": thread_id})
    message = result.fetchone()
    return message


def get_replies(thread_id):
    sql = text(
        "SELECT * from replies where thread_id=:thread_id AND deleted_at IS NULL ORDER BY id"
    )
    result = db.session.execute(sql, {"thread_id": thread_id})
    replies = result.fetchall()
    return replies


def get_by_category(category_id):
    sql = text(
        "SELECT * FROM conversations LEFT JOIN categories ON conversations.category=categories.id WHERE category=:category_id ORDER BY conversations.id"
    )
    result = db.session.execute(sql, {"category_id": category_id})
    conversations = result.fetchall()
    return conversations


def get_category_name(category_id):
    sql = text("SELECT display_name FROM categories WHERE id=:category_id")
    result = db.session.execute(sql, {"category_id": category_id})
    category_name = result.fetchone().display_name
    return category_name


def get_current_user(username):
    sql = text("SELECT * FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username": username})
    current_user = result.fetchone()
    return current_user


def get_user(username):
    sql = text("SELECT id, password FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()
    return user


def create_user(username, hash_value, user_level):
    sql = text(
        "INSERT INTO users (username, password, userlevel) VALUES (:username, :password, :userlevel)"
    )
    db.session.execute(sql, {
        "username": username,
        "password": hash_value,
        "userlevel": user_level
    })
    db.session.commit()


def submit_conversation(username, header, content, convo_category):
    sql = text(
        "INSERT INTO conversations (username, header, content, category) VALUES (:username, :header, :content, :category)"
    )
    db.session.execute(
        sql,
        {
            "username": username,
            "header": header,
            "content": content,
            "category": convo_category,
        },
    )
    db.session.commit()

def submit_reply(username, content_with_linebreaks, thread_id):
    sql = text(
        "INSERT INTO replies (username, content, thread_id) VALUES (:username, :content, :thread_id)"
    )
    db.session.execute(
        sql,
        {
            "username": username,
            "content": content_with_linebreaks,
            "thread_id": thread_id,
        },
    )
    db.session.commit()

def get_reply(reply_id):
    sql = text("SELECT * from replies where id=:id AND deleted_at IS NULL")
    result = db.session.execute(sql, {"id": reply_id})
    reply = result.fetchone()
    return reply

def edit_reply(reply_id, content_with_linebreaks):
    sql = text("UPDATE replies SET content = :content WHERE id = :id")
    db.session.execute(sql, {"content": content_with_linebreaks, "id": reply_id})
    db.session.commit()

def delete_reply(reply_id):
    sql = text("UPDATE replies SET deleted_at = :timestamp WHERE id=:id")
    timestamp = datetime.datetime.now(pytz.timezone("Europe/Helsinki"))
    db.session.execute(sql, {"id": reply_id, "timestamp": timestamp})
    db.session.commit()
