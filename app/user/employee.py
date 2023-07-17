"""Employee page routes"""
from flask import current_app as app, Blueprint, render_template, request, url_for, redirect, jsonify, abort
from flask_login import login_required
from app.user.models import CustomerModel
from app.bookings.models import BookingModel, SessionModel, ActivityModel, FacilityModel, BookingTypes, DiscountModel
from app.bookings.bookings import get_team_event_times
from app.utils.login_utils import role_required
from app.utils.extensions import db
from app.utils.send_email import send_email
from app.user.forms import SignupForm
from app.user.customer import add_account
from sqlalchemy import asc, or_
import random
import datetime
import string
import json
import ast

# Blueprint configuration
employee_bp = Blueprint(
    "employee_bp",  __name__, template_folder="employee_templates", static_folder="static", static_url_path="/user/static"
)

# pylint: disable=broad-exception-caught

# Website title
title = app.config["TITLE"]


# Subroutine to email password to new customer
def email_password(email, password):
    body = "Your temporary password is: " + password + "\n\nPlease change your password as soon as possible."
    send_email(email, "GymCorp: You signed up!", body)


# Ajax response when employee searches for customer
@employee_bp.route("/respond_search", methods=["GET"])
@login_required
@role_required(["employee"])
def respond_search():
    query = request.args.get("query")
    results = CustomerModel.query.filter(
        or_(CustomerModel.email.like(f"%{query}%"),)).all()
    # Only renders the search result to prevent entire page being rendered onto results
    return render_template("search_result.html", data=results)


# Ajax response when date time is changed
@employee_bp.route("/change_date_time", methods=["POST"])
@login_required
@role_required(["employee"])
def change_date_time():
    data = json.loads(request.data)
    if "booking_id" not in data or "date" not in data or "time" not in data:
        abort(400)
    booking_id = data.get("booking_id")
    date = data.get("date")
    time = data.get("time")
    # Check if date and time are valid
    try:
        date_time = datetime.datetime.fromisoformat(date + " " + time)
    except ValueError:
        abort(400)
    # Check if date is in the past
    if date_time.date() < datetime.date.today():
        abort(400)
    # If date is today, make sure time is in the future
    if date_time.date() == datetime.date.today() and date_time.hour <= datetime.datetime.now().hour:
        abort(400)
    # Check if date is within a certain amount of days in advance
    if date_time.date() >= (datetime.date.today() + datetime.timedelta(days=app.config["DAYS_ADVANCE"])):
        abort(400)
    booking = db.session.get(BookingModel, booking_id)
    if booking is None:
        abort(400)
    activity = db.session.get(ActivityModel, booking.activity_id)
    if activity.booking_type == BookingTypes.BOOKING:
        abort(400)
    facility = db.session.get(FacilityModel, activity.facility_id)
    # Check if number of people is valid
    if booking.number_of_people <= 0 or booking.number_of_people > facility.capacity:
        abort(400)
    # Time must be times array
    times = ast.literal_eval(activity.times)
    weekday = date_time.weekday()
    # Check if time is in times array
    if date_time.hour not in times[weekday]:
        abort(400)
    # If it is not a team event, then we must make sure it does not occur at the same time as them
    if activity.booking_type != BookingTypes.TEAMEVENT:
        # Get team event times
        team_event_times = get_team_event_times(activity.facility_id)
        # Check if time is in team event times
        if date_time.hour in team_event_times[weekday]:
            abort(400)
    # Check if session is full
    session = SessionModel.query.filter_by(
        activity_id=activity.id, date=date, start_time=date_time.hour).first()
    if session is not None:
        # If session capacity cannot hold number of people
        if (facility.capacity - session.number_of_people) < booking.number_of_people:
            abort(400)
    # If session does not exist, create it
    if session is None:
        # Create session
        session = SessionModel(activity_id=activity.id, date=date,
                               start_time=date_time.hour, number_of_people=booking.number_of_people)
        db.session.add(session)
        db.session.flush()
    else:
        # Update number of people in the session
        session.number_of_people += booking.number_of_people
    # Update booking
    prev_session = db.session.get(SessionModel, booking.session_id)
    booking.session_id = session.id
    db.session.flush()
    prev_session.number_of_people -= booking.number_of_people
    if prev_session.number_of_people <= 0:
        db.session.delete(prev_session)
    try:
        db.session().commit()
    except Exception as e:
        db.session().rollback()
        db.session().close()
        abort(500, str(e))
    db.session().close()
    return jsonify({"success": True}), 200


# Ajax response when employee changes number of people
@employee_bp.route("/change_people", methods=["POST"])
@login_required
@role_required(["employee"])
def change_people():
    data = json.loads(request.data)
    if "booking_id" not in data or "increment" not in data:
        abort(400)
    booking_id = data.get("booking_id")
    increment = data.get("increment")
    if not isinstance(increment, bool):
        abort(400)
    booking = db.session.get(BookingModel, booking_id)
    if booking is None:
        abort(400)
    activity = db.session.get(ActivityModel, booking.activity_id)
    if activity.booking_type == BookingTypes.BOOKING:
        abort(400)
    facility = db.session.get(FacilityModel, activity.facility_id)
    session = db.session.get(SessionModel, booking.session_id)
    if increment is True:
        if session.number_of_people >= facility.capacity:
            return jsonify({"number_of_people": facility.capacity}), 200
        booking.number_of_people += 1
        session.number_of_people += 1
    else:
        if booking.number_of_people <= 1:
            return jsonify({"number_of_people": 1}), 200
        booking.number_of_people -= 1
        session.number_of_people -= 1
    booking.cost = booking.number_of_people * activity.price
    if db.session.get(CustomerModel, booking.customer_id).membership is True:
        booking.cost *= DiscountModel.query.all()[0].discount
    db.session.commit()
    db.session.close()
    return jsonify({"number_of_people": booking.number_of_people, "cost": booking.cost})


# Page for employee to create an account with a random generated password
@employee_bp.route("/employee_dashboard", methods=["GET", "POST"])
@login_required
@role_required(["employee"])
def employee_dashboard():
    characters = string.ascii_letters + string.digits + string.punctuation
    password = "".join(random.choice(characters) for i in range(8))
    form = SignupForm(password=password, confirm_password=password,
                      email_verification_code='000000', phone_number_verification_code='000000')
    data = CustomerModel.query.order_by(asc(CustomerModel.id))
    if form.validate_on_submit():
        if (add_account(form.first_name.data, form.last_name.data, form.email.data, 0,
                        form.phone_number.data, 0, form.date_of_birth.data, form.gender.data, password, "employee")):
            email_password(form.email.data, password)
            customer = CustomerModel.query.filter_by(
                email=form.email.data).first()
            return redirect(url_for("employee_bp.customer_bookings", user_id=customer.id))
    return render_template("employee_dashboard.html", form=form, title=title, data=data)


# Page which shows customers bookings
@employee_bp.route("/customer_bookings/<int:user_id>", methods=["GET", "POST"])
@login_required
@role_required(["employee"])
def customer_bookings(user_id):
    customer = CustomerModel.query.get(user_id)
    if customer is None:
        abort(404)
    booking_data = []
    activities = []
    bookings = BookingModel.query.filter_by(
        customer_id=user_id).order_by(asc(BookingModel.id)).all()
    for booking in bookings:
        session_data = db.session.get(SessionModel, booking.session_id)
        activity = db.session.get(ActivityModel, session_data.activity_id)
        facility = db.session.get(FacilityModel, activity.facility_id)
        booking_data.append({
            "id": booking.id,
            "date": session_data.date,
            "time": datetime.time(hour=session_data.start_time).strftime("%H:%M"),
            "activity_name": activity.name,
            "facility_name": facility.name,
            "number_of_people": booking.number_of_people,
            "price": f"{activity.price:.2f}",
            "cost": f"£{booking.cost:.2f}",
            "paid": booking.paid
        })
        activities.append(activity)
    return render_template("customer_bookings.html", booking_data=booking_data, customer=customer, title=title, activities=activities)


# Ensures booking is deleted before refreshing page
@employee_bp.route("/delete_booking", methods=["POST"])
@login_required
@role_required(["employee"])
def delete_booking():
    data = json.loads(request.data)
    if "booking_id" not in data:
        abort(404)
    booking_id = data.get("booking_id")
    booking = db.session.get(BookingModel, booking_id)
    if booking is None:
        abort(404)
    customer_id = booking.customer_id
    session = db.session.get(SessionModel, booking.session_id)
    if session is not None:
        session.number_of_people -= booking.number_of_people
        if session.number_of_people <= 0:
            db.session.delete(session)
    db.session.delete(booking)
    db.session.commit()
    return jsonify({"url": url_for("employee_bp.customer_bookings", user_id=customer_id)}), 200


# Deletes customer account then redirects to customer search
@employee_bp.route("/delete_account", methods=["POST"])
@login_required
@role_required(["employee"])
def delete_account():
    data = json.loads(request.data)
    if "customer_id" not in data:
        abort(404)
    customer_id = data.get("customer_id")
    customer = db.session.get(CustomerModel, customer_id)
    if customer is None:
        abort(404)
    bookings = BookingModel.query.filter_by(customer_id=customer.id).all()
    for booking in bookings:
        session = SessionModel.query.filter_by(id=booking.session_id).first()
        session.number_of_people -= booking.number_of_people
        if session.number_of_people == 0:
            db.session.delete(session)
        db.session.delete(booking)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"url": url_for("employee_bp.employee_dashboard")}), 200


@employee_bp.route("/confirm_membership/<int:user_id>", methods=["POST"])
@login_required
@role_required(["employee"])
def confirm_membership(user_id):
    option = request.form["membership"]
    customer = CustomerModel.query.get(user_id)
    if option == "1":
        customer.membership = True
    elif option == "2":
        customer.membership = False
    db.session.commit()
    return redirect(url_for("employee_bp.customer_bookings", user_id=user_id))
