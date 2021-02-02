from flask import Flask, render_template, request, flash, redirect, url_for, session, Blueprint
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash



auth = Blueprint("auth", __name__, template_folder=r"templates", static_folder="static")
# configure app
app = Flask(__name__)

s_key = os.urandom(24)
app.config['SECRET_KEY'] = str(s_key)



def user_check():
    # check if user is logged in
    if session.get('logged_in'):
        return True

@auth.route('/')
def user():
    if "user" in session:
        user = session["user"]
        return render_template("lifts.html", user=user_check())
    else:
        return redirect(url_for("log_in"))


@auth.route('/log-out')
def log_out():
    session.pop("user", None)
    flash("you have log-out successfully", "success")
    return redirect(url_for("log_in"))



