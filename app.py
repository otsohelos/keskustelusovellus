from os import getenv
from flask import Flask, url_for
from flask import render_template, request, redirect, session
#from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy import text
#from werkzeug.security import check_password_hash, generate_password_hash

# initialize database
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
from db import db

app.secret_key = getenv("SECRET_KEY")

import routes

# Initialize cache
from cache import cache
