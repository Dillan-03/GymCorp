"""Bookings page routes"""
from flask import current_app as app, Blueprint, request, render_template, url_for, redirect, abort, jsonify, session as user_session
from flask_login import login_required, current_user
from app.bookings.models import FacilityModel, ActivityModel, SessionModel, BookingTypes, BookingModel, DiscountModel
from app.user.models import CustomerModel
from app.utils.extensions import db
from app.utils.login_utils import role_required
import json
import ast
import datetime
import time as time_module
import stripe
import math

# pylint: disable=broad-exception-caught

# Blueprint configuration
bookings_bp = Blueprint(
    "bookings_bp",  __name__, template_folder="templates", static_folder="static", static_url_path="/bookings/static"
)

# Website title
title = app.config["TITLE"]

# Booking product
product = "prod_Na8L1rl9Cqs0zQ"


# Get team event times
def get_team_event_times(facility_id):
    # Team events book the entire facility out, get a list of the times of team events for this facility
    team_event_response = ActivityModel.query.filter_by(
        facility_id=facility_id,
        booking_type=BookingTypes.TEAMEVENT
    ).all()
    team_event_times = []
    # Populate array with team event times
    for i in range(7):
        # Loop through all the days of the week and add times to a set
        day_times = set()
        # Loop through all the different team events
        for j in range(0, len(team_event_response)):
            # Loop through the times of the day for each team event
            for k in range(0, len(ast.literal_eval(
                    team_event_response[j].times)[i])):
                # Duration of team event may go for multiple hours, loop through duration hours
                for l in range(0, int(team_event_response[j].duration) // 60):
                    # Add each time to the set
                    day_times.add(ast.literal_eval(
                        team_event_response[j].times)[i][k] + l)
        # Add the list of the times of the day to the list
        team_event_times.append(list(day_times))
    return team_event_times


# Endpoint for customer bookings page
@bookings_bp.route("/bookings", methods=["GET"])
@login_required
@role_required(["customer"])
def bookings():
    # Get all facilities and activities data to display in page
    facilities = FacilityModel.query.all()
    activities = ActivityModel.query.all()
    discount = DiscountModel.query.first().discount
    discount_percentage = math.floor((1 - discount) * 100)
    return render_template("bookings.html", title=title, facilities=facilities, activities=activities, employee=False, discount=discount, discount_percentage=discount_percentage, customer=None)


# Endpoint for employee bookings page
@bookings_bp.route("/employee_bookings/<int:user_id>", methods=["GET"])
@login_required
@role_required(["employee"])
def employee_bookings(user_id):
    # Get all facilities and activities data to display in page
    facilities = FacilityModel.query.all()
    activities = ActivityModel.query.all()
    discount = DiscountModel.query.first().discount
    discount_percentage = math.floor((1 - discount) * 100)
    # Send customer data
    customer = db.session.get(CustomerModel, user_id)
    if customer is None:
        abort(404)
    return render_template("bookings.html", title=title, facilities=facilities, activities=activities, employee=True, discount=discount, discount_percentage=discount_percentage, customer=customer)


# Helper function to return what dates are eligible for discount
def discounted_dates(bookings_list, membership):
    booking_dates = []
    for booking in bookings_list:
        booking_dates.append(datetime.datetime.strptime(
            booking.get("date"), "%Y-%m-%d"))
    if membership:
        return booking_dates
    booking_dates.sort()
    # Map dates to array of distances between each date
    day_distances = []
    for i in range(0, len(booking_dates)-1):
        day_distances.append((booking_dates[i+1]-booking_dates[i]).days)
    output = set()
    # Ensure the distances between each one add up to <=7
    for i in range(0, len(day_distances)-2):
        if day_distances[i] + day_distances[i + 1] + day_distances[i + 2] <= 7:
            output.add(booking_dates[i])
            output.add(booking_dates[i + 1])
            output.add(booking_dates[i + 2])
            output.add(booking_dates[i + 3])
    return list(output)


# Check if bookings request is valid
def validate_bookings(bookings_list):
    # Create errors array and sessions array to store each session, number of people for each booking stored
    errors = []
    sessions = []
    number_of_people_list = []
    # Loop through bookings
    for booking in bookings_list:
        # Booking must be a dictionary of items
        if not isinstance(booking, dict):
            errors.append("Invalid booking data type")
            continue
        # Check if we have activity id, date or time
        if "activity_id" not in booking or "date" not in booking or "time" not in booking:
            errors.append("Not all fields received")
            continue
        activity_id = booking.get("activity_id")
        date = booking.get("date")
        time = booking.get("time")
        # Check if they are all strings
        if not isinstance(activity_id, int) or not isinstance(date, str) or not isinstance(time, str):
            errors.append("Invalid fields type")
            continue
        # Check if date and time are valid
        try:
            date_time = datetime.datetime.fromisoformat(date + " " + time)
        except ValueError:
            errors.append("Invalid date or time")
            continue
        # Check if date is in the past
        if date_time.date() < datetime.date.today():
            errors.append("Date in the past")
            continue
        # If date is today, make sure time is in the future
        if date_time.date() == datetime.date.today() and date_time.hour <= datetime.datetime.now().hour:
            errors.append("Session has already started")
            continue
        # Check if date is within a certain amount of days in advance
        if date_time.date() >= (datetime.date.today() + datetime.timedelta(days=app.config["DAYS_ADVANCE"])):
            errors.append("Date is too far ahead")
            continue
        # Check if activity exists
        activity = db.session.get(ActivityModel, activity_id)
        if activity is None:
            errors.append("Activity does not exist")
            continue
        # Get facility of this activity
        facility = db.session.get(FacilityModel, activity.facility_id)
        # If activity is not a booking, we need a number of people field
        if activity.booking_type != BookingTypes.BOOKING:
            # Check if we have a number of people field
            if "number_of_people" not in booking:
                errors.append("Number of people not received")
                continue
            number_of_people = booking.get("number_of_people")
            # Check if number of people is an integer
            if not isinstance(number_of_people, int):
                errors.append("Number of people invalid type")
                continue
            # Check if number of people is valid
            if number_of_people <= 0 or number_of_people > facility.capacity:
                errors.append("Number of people invalid")
                continue
        else:
            # If it is a booking and we don't have a number of people, set it to capacity
            number_of_people = facility.capacity
        number_of_people_list.append(number_of_people)
        # Time must be times array
        times = ast.literal_eval(activity.times)
        weekday = date_time.weekday()
        # Check if time is in times array
        if date_time.hour not in times[weekday]:
            errors.append("Time is not available")
            continue
        # If it is not a team event, then we must make sure it does not occur at the same time as them
        if activity.booking_type != BookingTypes.TEAMEVENT:
            # Get team event times
            team_event_times = get_team_event_times(activity.facility_id)
            # Check if time is in team event times
            if date_time.hour in team_event_times[weekday]:
                errors.append("Time is not available")
                continue
        # Check if session is full
        session = SessionModel.query.filter_by(
            activity_id=activity_id, date=date, start_time=date_time.hour).first()
        sessions.append(session)
        if session is not None:
            # If session capacity cannot hold number of people
            if (facility.capacity - session.number_of_people) < number_of_people:
                errors.append("Session is full")
                continue
    return errors, sessions, number_of_people_list


# Create the booking
def create_booking(session, customer_id, activity_id, date_time, number_of_people, cost, paid, employee_id=None, checkout_session=None):
    try:
        # If session does not exist, create it
        if session is None:
            # Create session
            session = SessionModel(activity_id=activity_id, date=date_time.date(),
                                   start_time=date_time.hour, number_of_people=number_of_people)
            db.session.add(session)
            db.session.flush()
        else:
            # Update number of people in the session
            session.number_of_people += number_of_people
        # Create booking
        new_booking = BookingModel(customer_id=customer_id, session_id=session.id,
                                   activity_id=activity_id, number_of_people=number_of_people, employee_id=employee_id, cost=cost, checkout_session=checkout_session, paid=paid)
        db.session.add(new_booking)
        db.session().commit()
    except Exception as e:
        db.session.rollback()
        print(str(e))
        db.session().close()
        return jsonify({"fail": str(e)}), 500
    # db.session().close()


# Endpoint to book an activity, takes in an array of activity id, number of people, date and time
@bookings_bp.route("/book", methods=["POST"])
@login_required
@role_required(["customer", "employee"])
def book():
    # Parse JSON data from the request
    data = json.loads(request.data)
    # Check we received bookings variable
    if "bookings" not in data:
        return jsonify({"errors": ["No bookings data received"]}), 400
    bookings_list = data.get("bookings")
    # Check we have a list of bookings
    if not isinstance(bookings_list, list):
        return jsonify({"errors": ["Invalid bookings data type"]}), 400
    # Check if the data is valid
    errors, sessions, number_of_people_list = validate_bookings(bookings_list)
    if len(errors) != 0:
        return jsonify({"errors": errors}), 400
    # If employee booking, check they have sent correct customer id
    if user_session["user_role"] == "employee":
        if "customer_id" not in data:
            abort(500)
        customer_id = data.get("customer_id")
        # Check if customer id is valid
        if not isinstance(customer_id, int):
            abort(500)
        # Check customer exists
        customer = db.session.get(CustomerModel, customer_id)
        if customer is None:
            abort(500)
    else:
        customer = db.session.get(CustomerModel, current_user.id)
    # List of dates of discounted bookings
    discounted_dates_result = discounted_dates(
        bookings_list, customer.membership)
    # Get all the costs
    costs = []
    total_cost = 0
    for i in range(0, len(bookings_list)):
        # Get all variables
        booking = bookings_list[i]
        date = booking.get("date")
        time = booking.get("time")
        date_time = datetime.datetime.fromisoformat(date + " " + time)
        activity_id = booking.get("activity_id")
        number_of_people = number_of_people_list[i]
        # Cost of booking
        activity = db.session.get(ActivityModel, activity_id)
        cost = int(activity.price)
        if activity.booking_type != BookingTypes.BOOKING:
            cost = cost * number_of_people
        # If this date is discounted, modify the cost
        if datetime.datetime.strptime(date, "%Y-%m-%d") in discounted_dates_result:
            cost = cost * DiscountModel.query.first().discount
        costs.append(cost)
        total_cost += cost
    # Create payment object for customers
    checkout_session = None
    if user_session["user_role"] == "customer":
        # User checkout
        stripe.api_key = app.config["STRIPE_SECRET_KEY"]
        checkout_session = stripe.checkout.Session.create(
            success_url=url_for("customer_bp.dashboard", _external=True),
            cancel_url=url_for("bookings_bp.bookings", _external=True),
            line_items=[{
                "price_data": {
                    "currency": "gbp",
                    "product_data": {
                        "name": "Custom Booking",
                    },
                    "unit_amount": math.ceil(total_cost * 100),
                },
                "quantity": 1
            }],
            mode="payment",
            expires_at=int(time_module.time()) + (30 * 60)
        )
    # Checks complete, create booking
    for i in range(0, len(bookings_list)):
        # Get all variables
        session = sessions[i]
        booking = bookings_list[i]
        date = booking.get("date")
        time = booking.get("time")
        date_time = datetime.datetime.fromisoformat(date + " " + time)
        activity_id = booking.get("activity_id")
        number_of_people = number_of_people_list[i]
        cost = costs[i]
        # If it is an employee booking, do not take to payment page
        if user_session["user_role"] == "employee":
            create_booking(session=session, customer_id=customer.id, employee_id=current_user.id, activity_id=activity_id,
                           date_time=date_time, number_of_people=number_of_people, cost=cost, paid=True)
        else:
            create_booking(session=session, customer_id=current_user.id, activity_id=activity_id,
                           date_time=date_time, number_of_people=number_of_people, cost=cost, checkout_session=checkout_session.id, paid=False)
    if user_session["user_role"] == "customer":
        return jsonify({"redirect": checkout_session.url}), 200
    return jsonify({"success": True}), 200


# Endpoint to load sessions
@bookings_bp.route("/sessions", methods=["POST"])
@login_required
@role_required(["customer", "employee"])
def sessions():
    # Parse JSON data from the request
    data = json.loads(request.data)
    number_of_people = 1
    try:
        # If we received booking id instead, load data
        if "booking_id" in data and user_session["user_role"] == "employee":
            booking_id = data.get("booking_id")
            booking = db.session.get(BookingModel, booking_id)
            if booking is None:
                abort(500)
            activity_data = db.session.get(
                ActivityModel, booking.activity_id).serialize
            facility_data = db.session.get(
                FacilityModel, activity_data["facility_id"]).serialize
            number_of_people = booking.number_of_people
        else:
            # Request data received
            if "activity_id" not in data or "facility_id" not in data:
                abort(400)
            activity_data = db.session.get(
                ActivityModel, data.get("activity_id")).serialize
            facility_data = db.session.get(
                FacilityModel, data.get("facility_id")).serialize
            if activity_data is None or facility_data is None:
                abort(404)
        # Format the times array
        activity_data["times"] = ast.literal_eval(activity_data["times"])
        # Query sessions
        response = SessionModel.query.filter_by(
            activity_id=activity_data["id"]).all()
        # Get team event times
        team_event_times = get_team_event_times(facility_data["id"])
        # Render sessions, activity, and facilities in a table, pass the team event times for rendering unavailable times, pass datetime to generate session dates, opening and closing times and days booked in advance
        sessions_table = render_template(
            "sessions_table.html", sessions=response, activity=activity_data, facility=facility_data, team_event_times=team_event_times,  datetime=datetime, opening_time=app.config["OPENING_TIME"], closing_time=app.config["CLOSING_TIME"], days_advance=app.config["DAYS_ADVANCE"], number_of_people=number_of_people)
        # Return the table back to the original site as well as the raw sessions object to be stored
        return jsonify({"status": "OK", "rendered": sessions_table, "facility": facility_data, "activity": activity_data, "sessions": [i.serialize for i in response]}), 200
    except Exception as e:
        print(str(e))
        return abort(500)
