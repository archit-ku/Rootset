from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from . import db
import json

views = Blueprint("views", __name__)

@views.route("/", methods=["GET","POST"])
@login_required #this route can only be accessed by a logged in user
def home():
    if request.method == "POST":
        #check which button user clicked
        if request.form.get("openOauth") == "true":
            return redirect(url_for("oauth.verify"))
        elif request.form.get("openTwt") == "true":
            return redirect(url_for("seeData.twitter"))
        elif request.form.get("openWeather") == "true":
            return redirect(url_for("seeData.weather"))
        elif request.form.get("openNews") == "true":
            return redirect(url_for("seeData.news"))
        elif request.form.get("openHelp") == "true":
            return redirect(url_for("auth.help"))
    return render_template("home.html", user=current_user)