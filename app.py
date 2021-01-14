from flask import Flask, render_template, request, flash, redirect, url_for, session, Blueprint
from flask_login import current_user
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from auth.auth import auth

# configure app
app = Flask(__name__)
app.register_blueprint(auth, url_prefix="/user")

s_key = os.urandom(24)
app.config['SECRET_KEY'] = str(s_key)



def db_connection():
    try:
        c = sqlite3.connect("fit_app")
        return c

    except sqlite3.Error as e:
        return e


def user_check():
    # check if user is logged in
    if session.get('logged_in'):
        return True


@app.route('/')
def main():
    home = True
    return render_template("index.html", user=user_check(), home=home)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        e_mail = request.form.get("e-mail")
        s_psw = generate_password_hash(request.form.get("psw"), method="sha256")
        c_psw = request.form.get("c_psw")
        f_name = request.form.get("f_name")
        l_name = request.form.get("l_name")
        b_day = request.form.get("b_day")
        if not e_mail or not s_psw or not c_psw or not f_name or not l_name or not b_day:
            flash("you must fill all boxes", "danger")
            return redirect(url_for("register"))
        elif not check_password_hash(s_psw, c_psw):
            flash("password dont match", "danger")
            return redirect(url_for("register"))
        else:
            con = db_connection()
            try:
                c = con.cursor()
                c.execute('''INSERT INTO users (psw, email, f_name, l_name, b_day)
                                     VALUES (?, ?, ?, ?, ?)''', (s_psw, e_mail, f_name, l_name, b_day))
                con.commit()
                result = "sucess"
            except sqlite3.IntegrityError:
                flash("account connected to this email already exist", "danger")
                return redirect(url_for("register"))
            except:
                con.rollback()
                result = "failure in database operations"
            finally:
                con.close()
        return render_template("result.html", result=result, f_name=f_name)
    else:
        return render_template("register.html", user=user_check())



@app.route('/log-in', methods=['POST', 'GET'])
def log_in():
    if request.method == 'POST':
        con = db_connection()
        c = con.cursor()
        user = request.form.get("email")

        email_from_form = c.execute('''SELECT email FROM users WHERE email=?''', (user,)).fetchone()
        psw_from_form = c.execute('''SELECT psw FROM users WHERE email=?''', (user,)).fetchone()

        if email_from_form is None:
            flash("wrong email", "danger")
            return redirect(url_for("log_in"))

        if check_password_hash(psw_from_form[0], request.form.get("psw")):
            if "user" not in session:
                session["user"] = user
                session["logged_in"] = True
                return redirect(url_for("auth.user"))
            else:
                return redirect(url_for("auth.user"))
        else:
            flash("wrong password", "danger")
            return redirect(url_for("log_in"))
    else:
        return render_template("log_in.html", user=user_check())



@app.route('/basic_training')
def basic():
    return render_template("basic.html", user=user_check())


@app.route('/BMI_form')
def bmi_form():
    return render_template("BMI-form.html", user=user_check())


@app.route('/BMI', methods=['POST', 'GET'])
def bmi():
    if request.method == "POST" :
        weight = request.form.get("weight")
        height = request.form.get("height")
        bmi = float(weight) / ((float(height) / 100) ** 2)
        bmi = round(bmi, 2)
        return render_template("BMI.html", bmi=bmi, user=user_check())
    else:
        return render_template("BMI-form.html", user=user_check() )

@app.route('/diets')
def diets():
    user = True if session.get('logged_in') else False
    return render_template("diets.html", user=user_check())


@app.route('/fit_brownie')
def brownie():
    user = True if session.get('logged_in') else False
    return render_template("brownie.html", user=user_check())


@app.route('/orm-form')
def orm_form():
    return render_template("orm-form.html", user=user_check())


@app.route('/orm', methods=['POST', 'GET'])
def orm():
    if request.method == "POST":
        lift = request.form.get("lift")
        reps = request.form.get("reps")
        orm = (float(lift)) * (1 + (float(reps) / 30))
        orm = round(orm * 2) / 2
        return render_template("orm.html", orm=orm, user=user_check())
    else:
        return render_template("orm-form.html", user=user_check())


if __name__ == '__main__':
    app.run(port=3000, debug=True)
    app.register_blueprint(auth, url_prefix="/user")





