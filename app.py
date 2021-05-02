import os
import sqlite3

from flask import Flask, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from auth.auth import auth

# configure app
app = Flask(__name__)
app.register_blueprint(auth, url_prefix="/user")

s_key = os.urandom(24)

mailgun_secret_key_value = os.environ.get('MAILGUN_SECRET_KEY', s_key)
app.config['SECRET_KEY'] = str(mailgun_secret_key_value)


def db_connection():
    try:
        c = sqlite3.connect("fit_app")
        return c

    except sqlite3.Error as e:
        return e


def user_check():
    # check if user is logged in
    if 'user' in session:
        return True
    else:
        return False


@app.route('/')
def main():
    return render_template("index1.html", user=user_check())


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        e_mail = request.form.get("e-mail")
        s_psw = generate_password_hash(request.form.get("psw"), method="sha256")
        c_psw = request.form.get("c_psw")
        f_name = request.form.get("f_name")
        l_name = request.form.get("l_name")
        if not e_mail or not s_psw or not c_psw or not f_name or not l_name:
            flash("you must fill all boxes", "danger")
            return redirect(url_for("register"))
        elif not check_password_hash(s_psw, c_psw):
            flash("password dont match", "danger")
            return redirect(url_for("register"))
        else:
            con = db_connection()
            try:
                c = con.cursor()
                c.execute('''INSERT INTO users (psw, f_name, l_name, email)
                                     VALUES (?, ?, ?, ?)''', (s_psw, f_name, l_name, e_mail))
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
        register = True
        return render_template("register.html", user=user_check(), register=register)


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
        login = True
        return render_template("log_in.html", user=user_check(), login=login)


@app.route('/basic_training')
def basic():
    return render_template("basic.html", user=user_check())


@app.route('/BMI_form')
def bmi_form():
    return render_template("BMI-form.html", user=user_check())


@app.route('/BMI', methods=['POST', 'GET'])
def bmi():
    if request.method == "POST":
        weight = request.form.get("weight")
        height = request.form.get("height")
        bmi = float(weight) / ((float(height) / 100) ** 2)
        bmi = round(bmi, 2)
        return render_template("BMI.html", bmi=bmi, user=user_check())
    else:
        return render_template("BMI-form.html", user=user_check())


@app.route('/diets', methods=['POST', 'GET'])
def diets():
    if request.method == "POST":
        weight = request.form.get("weight")
        height = request.form.get("height")
        gender = request.form.get("gender")
        age = request.form.get("age")
        active = request.form.get("activity")
        goal = request.form.get("goal")
        g_factor = 5
        if gender == "Female":
            g_factor = -161

        a_factor = 1.2
        if active == "Lightly active - train for 1-3 day a week":
            a_factor = 1.375
        elif active == "Moderately active - train for 3-5 day a week":
            a_factor = 1.55
        elif active == "Very active - train for 6-7 day a week":
            a_factor = 1.725
        elif active == "Extra active - Athlete job":
            a_factor = 1.9

        calories = (10 * float(weight) + 6.25 * float(height) - (5 * float(age)) + g_factor) * a_factor

        if goal == "Loose weight":
            calories -= 300
        elif goal == "Gain weight":
            calories += 300

        return render_template("diets.html", calories=calories, user=user_check())
    else:
        return render_template("diets.html", user=user_check())

@app.route('/diet1500')
def diet1500():
    return render_template("diet1500.html", user=user_check())

@app.route('/diet2000')
def diet2000():
    return render_template("diet2000.html", user=user_check())


@app.route('/diet2500')
def diet2500():
    return render_template("diet2500.html", user=user_check())


@app.route('/diet3000')
def diet3000():
    return render_template("diet3000.html", user=user_check())


@app.route('/diet3500')
def diet3500():
    return render_template("diet3500.html", user=user_check())


@app.route('/fit_brownie')
def brownie():
    return render_template("brownie.html", user=user_check(), info="brownie")


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
