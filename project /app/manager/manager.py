"""Manager page routes"""
# import packages

import ast
from flask import (
    Blueprint,
    render_template,
    request,
    url_for,
    flash,
    redirect,
    current_app as app,
    session
)
from flask_login import login_required, current_user, logout_user
from urllib.parse import urlparse, urljoin
from sqlalchemy.exc import IntegrityError, DataError
from app.utils.extensions import db, bcrypt
from app.utils.login_utils import manager_required
from app.bookings.models import ActivityModel, FacilityModel, DiscountModel
from app.manager.forms import ChangeCapacity, Manager, ActivityForm, AmendActivityForm, FacilityForm, EmployeeForm, DiscountAmount
from app.user.models import CustomerModel, EmployeeModel
from app.bookings.models import SessionModel
import decimal
import datetime
import json
import math

# pylint: disable=unused-import disable=wildcard-import disable=unused-wildcard-import

# Blueprint configuration
manager_bp = Blueprint(
    "manager_bp", __name__, template_folder="templates", static_folder="static"
)

# Website title
title = "Manager Dashboard"

# Validate URL to prevent Open Redirect Vulnerabilities


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc

# Login as a manager


@manager_bp.route("/manager_login", methods=["GET", "POST"])
@manager_required(False)
def manager_login():
    form = Manager()
    # Form Validation
    if form.validate_on_submit():
        email = request.form["email"]
        password = request.form["password"]
        # Check if email and password match
        if email == app.config["MANAGER_EMAIL"] and password == app.config["MANAGER_PASSWORD"]:
            session["manager"] = True
            return redirect(url_for("manager_bp.manager_home"))
        else:
            flash("Email/Password Incorrect. Please Try Again", "error")
            return redirect(url_for("manager_bp.manager_login"))

    return render_template("manager_login.html", title="Manager Login", form=form)


# Home page for manager, change discount page if necessary
@manager_bp.route("/manager_home", methods=["GET", "POST"])
@manager_required(True)
def manager_home():
    """ Update Discount Price """

    form = DiscountAmount()
    data = DiscountModel.query.all()  # get current discounts

    discounts = []

    for row in data:
        discounts.append(math.floor((1 - row.discount) * 100))

    if form.validate_on_submit():
        percentage = request.form["discount"]
        discount = 1 - (decimal.Decimal(percentage) / 100)
        row = DiscountModel.query.first()

        if row == None:
            first_row = DiscountModel(discount=discount)
            db.session.add(first_row)
        else:
            row.discount = discount

        # Update Discount to the database
        try:
            db.session.commit()
            flash("Discount Updated", "success")
            return redirect(url_for("manager_bp.manager_home"))

        except DataError as error:
            flash(
                "Discount is out of range (Max Discount can be applied is 50%)", "error")

    return render_template("manager_home.html", title=title, form=form, data=discounts)


# Manager customers page, to view customer information
@manager_bp.route("/manager_customer", methods=["GET", "POST"])
@manager_required(True)
def manager_customer():
    """ Reading all the data from the customer model """

    data = CustomerModel.query.order_by(CustomerModel.id).all()
    return render_template("manager_customer.html", data=data)


# Create and manage employees
@manager_bp.route("/manager_employee", methods=["GET", "POST"])
@manager_required(True)
def manager_employee():
    """ Reading all the data from the employee model """

    data = EmployeeModel.query.order_by(EmployeeModel.first_name).all()
    form = EmployeeForm()
    if form.validate_on_submit():
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        phone_number = request.form["phone_number"]
        password = request.form["password"]

        # Hash password
        password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

        # Add data to the DB
        row = EmployeeModel(
            first_name=first_name, last_name=last_name, email=email, phone_number=phone_number, password=password_hash)
        db.session.add(row)

        try:
            db.session.commit()
            flash("Signed up", "success")
            return redirect(url_for("manager_bp.manager_employee"))

        except IntegrityError as error:
            db.session.rollback()
            flash("Account is already taken. Please Try Again", "error")
            return redirect(url_for("manager_bp.manager_employee"))

    return render_template("manager_employee.html", form=form, data=data)


def toDateTime(s):
    # s will be in the format "YYYY-MM-DD"
    year = int(s[0:4])
    month = int(s[5:7])
    day = int(s[8:10])
    return datetime.date(year, month, day)

# Create and edit activities


@manager_bp.route("/manager_activity", methods=["GET", "POST"])
@manager_required(True)
def manager_activity():
    """ Allows the manager to be able to create and edit activities"""

    # create array of string representations of the last 7 days
    days = ["" for i in range(0, 7)]
    day_x = datetime.date.today() - datetime.timedelta(days=7)
    for i in range(0, 7):
        days[i] = str(day_x.strftime("%Y-%m-%d"))
        day_x = day_x + datetime.timedelta(days=1)

    # Get list of all facility names
    facilities = FacilityModel.query.all()
    names = []

    for facility in facilities:
        names.append(facility.name)

    activity_form = ActivityForm(names)
    amend_activity_form = AmendActivityForm(names)

    # Reading from activity database
    # Get facility_id -> retrieve facility name from facility model
    # Get general use name
    activities = ActivityModel.query.all()
    values = []

    for each_activity in activities:
        facility_name = FacilityModel.query.filter_by(
            id=each_activity.facility_id).first()
        substring = facility_name.name + ": " + each_activity.name
        values.append(substring)

    selected_activity_combined = request.args.get("option")
    if not selected_activity_combined in values:
        selected_activity_combined = values[0]

    # the following section of code is to get the sales over the last 7 days for the selected activity
    # start of section asdf

    # sales for each day in chronological order
    selected_activity_sales = [0 for i in range(7)]
    # get selected activity id
    selected_activity_name = selected_activity_combined.split(": ")[
        1].strip()  # type: ignore
    selected_activity_fname = selected_activity_combined.split(": ")[
        0].strip()  # type: ignore
    # need to get facility entry to be able to filter activity by facility id as well as activity name
    selected_activity_facility = FacilityModel.query.filter_by(
        name=selected_activity_fname).first()
    # get selected activity db entry based on activity name and facility id, in order to get selected activity id
    selected_activity2 = ActivityModel.query.filter_by(
        name=selected_activity_name, facility_id=selected_activity_facility.id).first()
    # relevant sessions = where activity id = selected activity id
    relevant_sessions = SessionModel.query.filter_by(
        activity_id=selected_activity2.id
    )
    # for each session 'cxz' in relevant sessions
    for session in relevant_sessions:
        # for each day's string rep 'dvc' in the last 7 days
        for i in range(0, 7):
            # if cxz.date = dvc
            if session.date == days[i]:
                # add 1 to 'dvc's corresponding array of 7 integers
                selected_activity_sales[i] += 1
    # end of section asdf

    # Add new activity for a facility
    if activity_form.validate_on_submit():
        name = activity_form.name.data
        booking_type = activity_form.booking_type.data
        price = activity_form.price.data
        if price != None:
            # round price to ensure data integrity
            price = round(float(price), 2)
        duration = activity_form.duration.data
        times = activity_form.times.data
        facility_name = activity_form.facility_name.data
        days = activity_form.days.data

        # Define the size of the 2D array
        rows = 7  # array to be range 8 to 21
        cols = 14

        if duration != None:  # ignore duration statement. or else a error is shown
            duration = duration * 60

        # Create the 2D array to store the required times and days in the database
        time = [[0 for j in range(cols)] for i in range(rows)]

        # Set the index to place the number
        index = int(str(times))-8

        # Check to find existing row in db
        facility = FacilityModel.query.filter_by(name=facility_name).first()

        find = ActivityModel.query.filter_by(
            name=name, booking_type=booking_type, price=price, duration=duration, facility_id=facility.id).first()
        if find is None:  # Add new row
            if days != None:
                for each_day in days:
                    if (each_day == "Monday"):
                        day = 0
                    elif (each_day == "Tuesday"):
                        day = 1
                    elif (each_day == "Wednesday"):
                        day = 2
                    elif (each_day == "Thursday"):
                        day = 3
                    elif (each_day == "Friday"):
                        day = 4
                    elif (each_day == "Saturday"):
                        day = 5
                    else:
                        day = 6

                    time[day][index] = times  # type: ignore

                # Removing all zeros in the array
                processed_time = [[times for times in each_day if times != 0]
                                  for each_day in time]

                row = ActivityModel(name=name, booking_type=booking_type,
                                    price=price, duration=duration, times=json.dumps(processed_time), facility_id=facility.id)

                db.session.add(row)
                db.session.commit()
                flash("Entered to the system", "add_success")
                return redirect(url_for("manager_bp.manager_activity"))

        else:

            # Check to see if days array is the same. if not then add new row
            # Get times array and update it

            if days != None:
                for each_day in days:
                    if (each_day == "Monday"):
                        day = 0
                    elif (each_day == "Tuesday"):
                        day = 1
                    elif (each_day == "Wednesday"):
                        day = 2
                    elif (each_day == "Thursday"):
                        day = 3
                    elif (each_day == "Friday"):
                        day = 4
                    elif (each_day == "Saturday"):
                        day = 5
                    else:
                        day = 6

                time[day][index] = times  # type: ignore

            # Removing all zeros in the array
            processed_time = [[times for times in each_day if times != 0]
                              for each_day in time]

            if processed_time != ast.literal_eval(find.times):
                # update time
                old_time = find.times
                old_time = ast.literal_eval(old_time)

                if days != None:
                    for each_day in days:
                        if (each_day == "Monday"):
                            day = 0
                        elif (each_day == "Tuesday"):
                            day = 1
                        elif (each_day == "Wednesday"):
                            day = 2
                        elif (each_day == "Thursday"):
                            day = 3
                        elif (each_day == "Friday"):
                            day = 4
                        elif (each_day == "Saturday"):
                            day = 5
                        else:
                            day = 6

                        if times not in old_time[day]:  # type: ignore
                            old_time[day].append(times)  # type: ignore

                    # old_time = find.times
                    find.times = str(old_time)
                    db.session.commit()

                    flash("Updated the system", "add_success")
                    return redirect(url_for("manager_bp.manager_activity"))
            else:
                flash("Unable to create the activity. Please Try Again", "add_error")
                db.session.rollback()
                return redirect(url_for("manager_bp.manager_activity"))

    # Amend activity information
    if amend_activity_form.validate_on_submit():

        name = amend_activity_form.amend_name.data
        price = amend_activity_form.amend_price.data
        if price != None:
            price = round(float(price), 2)

        facility_name = amend_activity_form.amend_facility_name.data

        # find matching row in the database
        facility = FacilityModel.query.filter_by(name=facility_name).first()
        row = ActivityModel.query.filter_by(
            name=name, facility_id=facility.id).first()

        if row != None:  # row exists
            row.price = price
            db.session.commit()
            flash("Price Changed", "price_success")
            return redirect(url_for("manager_bp.manager_activity"))

        else:
            flash("Incorrect information. Please try again.", "price_error")
            return redirect(url_for("manager_bp.manager_activity"))

    return render_template("manager_activity.html", values=values, activity=selected_activity_combined, activity_form=activity_form, amend_activity_form=amend_activity_form, sales=selected_activity_sales, days=days)


@manager_bp.route("/manager_facility", methods=["GET", "POST"])
@manager_required(True)
def manager_facility():
    """ Add new facility and change the capacity of a facility """

    facilities = FacilityModel.query.order_by(FacilityModel.id).all()
    facility_form = FacilityForm()
    amend_facility_form = ChangeCapacity()

    # create array of string representations of the last 7 days
    days = ["" for i in range(0, 7)]
    day_x = datetime.date.today() - datetime.timedelta(days=7)
    for i in range(0, 7):
        days[i] = str(day_x.strftime("%Y-%m-%d"))
        day_x = day_x + datetime.timedelta(days=1)

    # Get all facilities from the database
    facilities = FacilityModel.query.all()
    values = []

    for facility in facilities:
        values.append(facility.name)

    selected_facility = request.args.get("option")
    if not selected_facility in values:
        selected_facility = values[0]

    # the following section of code is to get the sales over the last 7 days for the selected facility
    # start of section asdf
    # sales for each day in chronological order
    selected_facility_usage = [0 for i in range(7)]
    # need to get facility entry to be able to filter activity by facility id as well as activity name
    selected_facility2 = FacilityModel.query.filter_by(
        name=selected_facility).first()
    # relevant activities = where facility id = selected facility id
    relevant_activities = ActivityModel.query.filter_by(
        facility_id=selected_facility2.id)
    # relevant sessions = where activity id in list of relevant activity id's
    relevant_activities_ids = []
    for activity in relevant_activities:
        relevant_activities_ids.append(activity.id)

    relevant_sessions = []
    for v in range(0, len(relevant_activities_ids)):
        relevant_sessions.append(SessionModel.query.filter_by(
            activity_id=relevant_activities_ids[v]))
    # for each session 'cxz' in relevant
    for f in range(0, len(relevant_activities_ids)):
        for session in relevant_sessions[f]:
            # for each day's string rep 'dvc' in the last 7 days - 1 indent
            for i in range(0, 7):
                # if cxz.date = dvc - 2 indents
                if session.date == days[i]:
                    # get 'dvc's activity
                    session_activity = ActivityModel.query.filter_by(
                        id=session.activity_id).first()
                    # add 'dvc's activity duration to 'dvc's corresponding array of 7 integers - 3 indents
                    selected_facility_usage[i] += session_activity.duration
    # end of section asdf

    # Add a new facility
    if facility_form.validate_on_submit():

        name = facility_form.name.data
        capacity = facility_form.capacity.data

        try:
            row = FacilityModel(name=name, capacity=capacity)
            db.session.add(row)
            db.session.commit()
            flash("Facility added successfully!", "success")
            return redirect(url_for("manager_bp.manager_facility"))
        except IntegrityError:  # facility already exists
            db.session.rollback()
            flash("Facility already exists.", "error")
            return redirect(url_for("manager_bp.manager_facility"))

    # Change capacity of a facility
    if amend_facility_form.validate_on_submit():

        amend_name = amend_facility_form.amend_name.data
        amend_capacity = amend_facility_form.amend_capacity.data  # get capacity

        row = FacilityModel.query.filter_by(name=amend_name).first()
        if row is not None:
            row.capacity = amend_capacity

            db.session.commit()
            flash("Facility capacity changed!", "amend_success")
            return redirect(url_for("manager_bp.manager_facility"))
        else:  # facility does not exist
            flash("Incorrect information. Please try again.", "amend_error")

    return render_template("manager_facility.html", facility_form=facility_form, amend_facility_form=amend_facility_form,  title=title, facilities=facilities, values=values, facility=selected_facility, usage=selected_facility_usage, days=days)


# Logout manager
@manager_bp.route("/manager_logout")
@manager_required(True)
def logout():
    """ Manager Logout """

    logout_user()
    session["user_role"] = "guest"
    session["manager"] = False
    return redirect(url_for("home_bp.index"))
