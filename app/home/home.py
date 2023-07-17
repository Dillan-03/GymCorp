"""General page routes"""
from flask import Blueprint, render_template, url_for, request, session, redirect, current_app as app
from app.user.forms import Contact_Us
from app.bookings.models import FacilityModel, DiscountModel
from app.utils.send_email import send_email
from app import db
import math

# Blueprint configuration
home_bp = Blueprint(
    "home_bp",  __name__, template_folder="templates", static_folder="static", static_url_path="/home/static"
)

# Website title
title = app.config["TITLE"]


# Initialize user as a guest
@home_bp.before_request
def set_role():
    if "user_role" not in session:
        session["user_role"] = "guest"


# Home page
@home_bp.route("/", methods=["GET", "POST"])
def index():
    form = Contact_Us()
    # Send email to user
    if form.validate_on_submit():
        name = request.form['full_name']
        email = request.form['email']
        selected_option = request.form['select_option']
        message = request.form['message']
        body = "This is an automated message to let you know that your email has been sent successfully. We appreciate your communication and will respond to your email as soon as possible.If you have any further questions or concerns, please do not hesitate to reach out to us. We are here to help you.\n\nName: {}\nEmail: {}\nSubject: {}\nMessage: {}\n\n\nThank you for choosing GymCorp.".format(
            name, email, selected_option, message)
        send_email(email, "Automated Email", body)
        return redirect(url_for("home_bp.index"))
    # Retrieve discount from database
    discount = DiscountModel.query.first().discount
    discount_percentage = math.floor((1 - discount) * 100)
    return render_template("index.html", title=title, form=form, discount_percentage=discount_percentage)


# Facilities page
@home_bp.route("/facilities", methods=["GET"])
def facilities():

    # Retrieve data from facility model
    data = FacilityModel.query.all()

    return render_template("facilities.html", title=title, data=data)
