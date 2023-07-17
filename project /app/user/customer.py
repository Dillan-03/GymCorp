"""Customer page routes"""
from flask import Blueprint, render_template, request, url_for, flash, redirect, abort, jsonify, session as user_session, current_app as app
from flask_login import current_user, login_user, login_required, logout_user
from app.user.models import CustomerModel, EmployeeModel
from app.user.forms import SignupForm, LoginForm, MembershipForm, ChangePasswordForm, ResetPasswordForm
from app.bookings.models import BookingModel, SessionModel, ActivityModel, FacilityModel, DiscountModel
from app.utils.login_utils import role_required
from app.utils.extensions import bcrypt, db
from urllib.parse import urlparse, urljoin, urlencode, parse_qs
from sqlalchemy import asc
from sqlalchemy.exc import IntegrityError
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import datetime
import stripe
import ast
import time
import json
import re
import math

# pylint: disable=unused-variable

# Blueprint configuration
customer_bp = Blueprint(
    "customer_bp",  __name__, template_folder="templates", static_folder="static", static_url_path="/user/static"
)

# Website title
title = app.config["TITLE"]


# Verify email code
def verify_email_code(twilio_client, email, email_verification_code):
    try:
        email_verification_check = twilio_client.verify.v2.services(
            app.config["TWILIO_SERVICE_SID"]).verification_checks.create(to=email, code=email_verification_code)

        if email_verification_check.status != "approved":
            return "Invalid email verification code"
    except Exception as e:
        return "Please try sending a new email verification code"
    return True


# Verify phone number code
def verify_number_code(twilio_client, phone_number, phone_number_verification_code):
    try:
        phone_number_verification_check = twilio_client.verify.v2.services(
            app.config["TWILIO_SERVICE_SID"]).verification_checks.create(to="+44" + phone_number, code=phone_number_verification_code)

        if phone_number_verification_check.status != "approved":
            return "Invalid phone number verification code"
    except Exception as e:
        return "Please try sending a new SMS verification code"
    return True


# Subroutine that takes arguments and creates an account with the arguments
def add_account(first_name, last_name, email, email_verification_code, phone_number, phone_number_verification_code, date_of_birth, gender, password, role):
    # if role == "guest":
        # twilio_client = Client(
        # app.config["TWILIO_ACCOUNT_SID"], app.config["TWILIO_AUTH_TOKEN"])
        # return
        # email_status = verify_email_code(
        #     twilio_client, email, email_verification_code)
        # if email_verification_code != 123456:
        #     return flash("Incorrect Email Verification Code", "error")

        # if phone_number_verification_code != 123456:
        #     return flash("Incorrect Phone Number Verification Code", "error")

        # phone_status = verify_number_code(
        #     twilio_client, phone_number, phone_number_verification_code)
        # if phone_status != True:
        #     return flash(phone_status, "error")

    # Hash password
    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    # Add data to the DB
    row = CustomerModel(
        first_name, last_name, email, phone_number, date_of_birth, gender, password_hash, False)
    db.session.add(row)
    try:
        db.session.commit()
        if role == "guest":
            flash("Signed up", "success")
        else:
            flash("Created account", "success")
        return True
    except IntegrityError as error:
        db.session.rollback()
        if "email" in str(error.orig):
            flash("Email address is already taken.", "error")
        else:
            flash("Phone number is already taken.", "error")
    return False


# Validate URL to prevent Open Redirect Vulnerabilities
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and \
        ref_url.netloc == test_url.netloc


@customer_bp.route("/signup", methods=["GET", "POST"])
@role_required(["guest"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # Call suborutine to add account to database
        if (add_account(form.first_name.data, form.last_name.data, form.email.data, form.email_verification_code.data,
                        form.phone_number.data, form.phone_number_verification_code.data, form.date_of_birth.data, form.gender.data, form.password.data, "guest")):
            return redirect(url_for("customer_bp.login", login_type="customer"))
    return render_template("signup.html", title=title, form=form)


# Verify email endpoint
@customer_bp.route("/verify_email", methods=["POST"])
@role_required(["guest"])
def verify_email():
    # Parse JSON data from the request
    data = json.loads(request.data)
    if "email" not in data:
        abort(400)
    email_regex = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    email = data.get("email")
    if re.match(email_regex, email) is None:
        abort(400)
    twilio_client = Client(
        app.config["TWILIO_ACCOUNT_SID"], app.config["TWILIO_AUTH_TOKEN"])
    try:
        # Create verification request
        verification = twilio_client.verify.v2.services(app.config["TWILIO_SERVICE_SID"]).verifications.create(
            to=email, channel="email")
    except TwilioRestException as e:
        return jsonify({"status": "Max attempts reached, please try again later", "error": str(e)}), 500
    return jsonify({"status": verification.status})


# Verify SMS endpoint
@customer_bp.route("/verify_sms", methods=["POST"])
@role_required(["guest"])
def verify_sms():
    # Parse JSON data from the request
    data = json.loads(request.data)
    if "phone_number" not in data:
        abort(400)
    phone_number_regex = r"^[0-9]+$"
    phone_number = data.get("phone_number")
    if re.match(phone_number_regex, phone_number) is None or len(phone_number) != 10:
        abort(400)
    twilio_client = Client(
        app.config["TWILIO_ACCOUNT_SID"], app.config["TWILIO_AUTH_TOKEN"])
    try:
        # Create verification request
        verification = twilio_client.verify.v2.services(app.config["TWILIO_SERVICE_SID"]).verifications.create(
            to="+44" + phone_number, channel="sms")
    except TwilioRestException as e:
        return jsonify({"status": "Max attempts reached, please try again later", "error": str(e)}), 500
    return jsonify({"status": verification.status})


# Universal endpoint for logins
@customer_bp.route("/login", defaults={"login_type": "customer"}, methods=["GET", "POST"])
@customer_bp.route("/login/<string:login_type>", methods=["GET", "POST"])
@role_required(["guest"])
def login(login_type):
    form = LoginForm()
    reset_form = ResetPasswordForm()
    if form.validate_on_submit():
        remember_me = True if request.form.get("remember_me") else False

        # Check if user exists
        if login_type == "customer":
            user = CustomerModel.query.filter_by(email=form.email.data).first()
            user_session["user_role"] = "customer"
        else:
            user = EmployeeModel.query.filter_by(email=form.email.data).first()
            user_session["user_role"] = "employee"
        # Ensure password is correct
        if not user or not bcrypt.check_password_hash(user.password, form.password.data):
            user_session["user_role"] = "guest"
            flash("Please check your login details and try again.", "error")
            return redirect(url_for("customer_bp.login", login_type=login_type))

        # Login the user
        login_user(user, remember=bool(remember_me))

        # Redirect
        url_next = request.args.get("next")
        if not is_safe_url(url_next):
            return abort(400)

        return redirect(url_next or url_for("home_bp.index"))
    return render_template("login.html", title=title, form=form, login_type=login_type, reset_form=reset_form)


# Ajax route to reset the password
@customer_bp.route("/login/reset", methods=["POST"])
@role_required("guest")
def reset_password():
    form = ResetPasswordForm()
    message = ""
    if form.validate_on_submit():
        # Get customer with this email and check they exist
        customer = CustomerModel.query.filter_by(email=form.email.data).first()
        if customer:
            # Verify email code
            twilio_client = Client(
                app.config["TWILIO_ACCOUNT_SID"], app.config["TWILIO_AUTH_TOKEN"])
            status = verify_email_code(
                twilio_client, form.email.data, form.email_verification_code.data)
            if status is True:
                # Generate hash and ensure it is not the same as the old password
                password_hash = bcrypt.generate_password_hash(
                    form.password.data).decode("utf-8")
                if bcrypt.check_password_hash(password_hash, customer.password):
                    message = "New password cannot be old password"
                else:
                    # Save to the database
                    customer.password = password_hash
                    try:
                        db.session.commit()
                        message = "Password changed"
                        return jsonify(success=True, message=message)
                    except IntegrityError:
                        db.session.rollback()
                        message = "Error in database"
            else:
                message = status
        else:
            message = "No account with that email"
    else:
        message = "Passwords must match"
    return jsonify(success=False, message=message)


# Logout user
@customer_bp.route("/logout")
@login_required
@role_required(["customer", "employee", "manager"])
def logout():
    logout_user()
    user_session["user_role"] = "guest"
    return redirect(url_for("home_bp.index"))


# Membership subscribe page
@customer_bp.route("/subscribe", methods=["GET", "POST"])
@login_required
@role_required(["customer"])
def subscribe():
    try:
        flash(request.args["message"], request.args["type"])
    except:  # pylint: disable=bare-except
        pass
    form = MembershipForm()

    discount = DiscountModel.query.first().discount
    discount_percentage = math.floor((1 - discount) * 100)
    # If a form gets submitted, to buy a new membership
    if form.validate_on_submit():
        # Create product object
        # Send request to payment endpoint with product object send success and failure urls
        product = {
            "price": form.get_price()*100,
            "name": form.get_name(),
            "interval": form.get_interval(),
        }
        # If payment is successful, redirect to success url which will update the user as subscribed in the db and redirect to the subscribe page with a success message
        success_url = url_for("customer_bp.subscribe", _external=True)
        # if payment fails, redirect to failure url which will redirect to the subscribe page with an error message
        failure_url = url_for("customer_bp.subscribe",  _external=True)
        data = {"product": product, "successUrl": success_url,
                "failureUrl": failure_url}
        return redirect(url_for("customer_bp.payment", data=urlencode(data)), code=307)
        # redirect to payment page
    else:
        # A form is not submitted, check if user is already subscribed
        if current_user.membership_checkout:
            # check if subscription is being cancelled
            stripe.api_key = app.config["STRIPE_SECRET_KEY"]
            checkout_session = stripe.checkout.Session.retrieve(
                current_user.membership_checkout)
            if not checkout_session["subscription"]:
                # failed to complete checkout
                return render_template("subscribe.html", title=title, form=form, discount_percentage=discount_percentage)
            subscription = stripe.Subscription.retrieve(
                checkout_session["subscription"])
            if subscription["cancel_at_period_end"]:
                # if subscription is being cancelled, render the page with a message saying that they have been cancelled.
                return render_template("cancelled.html", title=title)
            # if subscribed, render the page with a message saying that they are already subscribed and the cancel button
            return render_template("cancel.html", title=title)
        else:
            # if not subscribed, render the page with the form
            return render_template("subscribe.html", title=title, form=form, discount_percentage=discount_percentage)


# Urlify string
def urlify(in_string):
    return "%20".join(in_string.split())


# Process the payment
@customer_bp.route("/payment", methods=["GET", "POST"])
@login_required
@role_required(["customer"])
def payment():
    data = parse_qs(request.args["data"])
    product = ast.literal_eval(data["product"][0])
    message = "Payment successful! Thank you for becoming a member, your status will soon be updated with our membership."
    success_url = data["successUrl"][0] + \
        f"?type=success&message={urlify(message)}"
    failure_url = data["failureUrl"][0]+"?type=error&message=" + \
        urlify("Payment failed, please try again.")
    try:
        stripe.api_key = app.config["STRIPE_SECRET_KEY"]
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "gbp",
                        "unit_amount": product["price"],
                        "product_data": {
                            "name": product["name"],
                        },
                        "recurring": {"interval": product["interval"], "interval_count": 1}
                    },
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=success_url,
            cancel_url=failure_url,
            locale="en",
            # set expiration in 30 minutes from now
            expires_at=int(time.time()) + (30 * 60)
        )
        customer = db.session.get(CustomerModel, current_user.id)
        customer.membership_checkout = checkout_session.id
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return abort(404, str(e))
    finally:
        db.session.close()
    return redirect(checkout_session.url, code=303)


# Cancel a membership
@customer_bp.route("/cancel_subscription", methods=["POST"])
@login_required
@role_required(["customer"])
def cancel_subscription():
    # update user as unsubscribed in db
    if not current_user.membership_checkout:
        return abort(404, "No subscription found")
    stripe.api_key = app.config["STRIPE_SECRET_KEY"]
    checkout_session = stripe.checkout.Session.retrieve(
        current_user.membership_checkout)
    stripe.Subscription.modify(
        checkout_session["subscription"],
        cancel_at_period_end=True
    )
    message = "We are sad to see you go. Your subscription has been cancelled"
    return jsonify({"url": url_for("customer_bp.subscribe", message=message, type="success")})


# Renew a membership
@customer_bp.route("/renew_subscription", methods=["POST"])
@login_required
@role_required(["customer"])
def renew_subscription():
    # update user as unsubscribed in db
    if not current_user.membership_checkout:
        return abort(404, "No subscription found")
    stripe.api_key = app.config["STRIPE_SECRET_KEY"]
    checkout_session = stripe.checkout.Session.retrieve(
        current_user.membership_checkout)
    stripe.Subscription.modify(
        checkout_session["subscription"],
        cancel_at_period_end=False
    )
    message = "Thanks for joining! Your subscription has been renewed"
    return jsonify({"url": url_for("customer_bp.subscribe", message=message, type="success")})


# Customer dashboard to view bookings
@customer_bp.route("/dashboard", methods=["GET"])
@login_required
@role_required(["customer"])
def dashboard():
    booking_data = []
    bookings = BookingModel.query.filter_by(
        customer_id=current_user.id).order_by(asc(BookingModel.id)).all()
    for booking in bookings:
        session_data = db.session.get(SessionModel, booking.session_id)
        # Session has already started
        date_time = datetime.datetime.fromisoformat(session_data.date)
        if (date_time.date() == datetime.date.today() and session_data.start_time <= datetime.datetime.now().hour) or date_time.date() < datetime.date.today():
            continue
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
    return render_template("dashboard.html", booking_data=booking_data, title=title)


# Customer deletes booking
@customer_bp.route("/customer/delete_booking/<int:booking_id>", methods=["GET", "POST"])
@login_required
@role_required(["customer"])
def delete_booking(booking_id):
    booking = db.session.get(BookingModel, booking_id)
    if booking is None:
        abort(404)
    if booking.customer_id != current_user.id:
        abort(404)
    session = db.session.get(SessionModel, booking.session_id)
    if session is not None:
        session.number_of_people -= booking.number_of_people
        if session.number_of_people <= 0:
            db.session.delete(session)
    db.session.delete(booking)
    db.session.commit()
    return redirect(url_for("customer_bp.dashboard"))


# Route for customer settings page
@customer_bp.route("/settings", methods=["GET", "POST"])
@login_required
@role_required("customer")
def settings():
    password_form = ChangePasswordForm()
    return render_template("settings.html", title=title, password_form=password_form)


# Ajax route to update the password
@customer_bp.route("/settings/update", methods=["POST"])
@login_required
@role_required("customer")
def update_password():
    form = ChangePasswordForm()
    message = ""
    if form.validate_on_submit():
        user = CustomerModel.query.get(current_user.id)
        password_hash = bcrypt.generate_password_hash(
            form.new_password.data).decode("utf-8")
        # If current password is correct
        if bcrypt.check_password_hash(user.password, form.password.data):
            # Check to make sure new password isn't the same as current
            if bcrypt.check_password_hash(user.password, form.new_password.data):
                message = "New password cannot be current password"
            else:
                # Add changes to database
                user.password = password_hash
                try:
                    db.session.commit()
                    message = "Password changed"
                    return jsonify(success=True, message=message)
                except IntegrityError as error:
                    message = "An error occured when saving to database"
                    db.session.rollback()
        else:
            message = "Incorrect password"
    else:
        message = "Passwords must match"
    return jsonify(success=False, message=message)


# Ajax route to confirm password modal
@customer_bp.route("/settings/confirm", methods=["POST"])
@login_required
@role_required("customer")
def confirm_password():
    password = json.loads(request.data)
    user = CustomerModel.query.get(current_user.id)
    # If password is correct
    if bcrypt.check_password_hash(user.password, password):
        return jsonify({"success": True}), 200
    return jsonify({"success": False}), 500


# Gets current user details into ajax to keep hidden from HTML source code
@customer_bp.route("/settings/get-current-user-details", methods=["GET"])
@login_required
@role_required("customer")
def get_details():
    return jsonify(email=current_user.email, phone_number=current_user.phone_number)
