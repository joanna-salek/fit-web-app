from flask import Flask, render_template, request, flash, redirect, url_for, session, Blueprint
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash



auth = Blueprint("auth", __name__, template_folder="templates", static_folder="static")
# configure app
app = Flask(__name__)

s_key = os.urandom(24)
app.config['SECRET_KEY'] = str(s_key)


@auth.route('/')
def user():
    if "email" in session:
        email = session["email"]
        return render_template("lifts.html", email=email)
    else:
        return redirect(url_for("go_to_log_in"))


@auth.route('/log-out')
def log_out():
    session.pop("email", None)
    flash("you have log-out successfully", "success")
    return redirect(url_for("go_to_log_in"))



