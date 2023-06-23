from flask import Blueprint, render_template, request, flash, redirect, url_for, Markup
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, hashingAlg
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        #find user email in db
        user = User.query.filter_by(email=email).first()
        if user:
            #if the hash of the input password matches the hash of the user's stored password hash
            if user.password == hashingAlg.customHash(password):
                flash("Logged in successfully", category="success")
                #login user
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                #email match, but password hashes do not match
                flash("Incorrect password, try again", category="error")
        else:
            #could not find email in db
            flash(Markup(f"Email does not exist. <a href={url_for('auth.signUp')}>Sign up instead?</a>"), category="error")
    #show login page
    return render_template("login.html", user=current_user)

@auth.route("/sign-up", methods=["GET", "POST"])
def signUp():
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("firstName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        
        user = User.query.filter_by(email=email).first()
        if user:
            #if user attemps to sign up with an email that already exists in db
            flash("Email already exists", category="error")

        #checking if input parameters are invalid
        elif len(first_name) < 2:
            flash("First name must be at least 2 characters", category="error")
        elif password1 != password2:
            flash("Passwords don't match", category="error")
        elif len(password1) <8:
            flash("Password must be at least 8 characters", category="error")
        
        #if all input parameters are valid
        else:
            #store email, first name, hash of the password
            new_user = User(email=email, first_name=first_name, password=hashingAlg.customHash(password1))
            db.session.add(new_user)

            #commit to db
            db.session.commit()

            #log in user with their new account
            login_user(new_user, remember=True)
            flash("Account created", category="success")

            #show help page upon successful sign up
            return redirect(url_for("auth.help"))
    
    return render_template("sign_up.html", user=current_user)

#log user out of current session
@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

#instructions explaining how to use the website
@auth.route("/help")
def help():
    return render_template("help.html", user=current_user)