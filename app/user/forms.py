""" Customer forms """
from flask import current_app as app
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, EqualTo, Length, Regexp, ValidationError
from wtforms import StringField, DateField, SubmitField, EmailField, BooleanField, PasswordField, RadioField, HiddenField, SelectField
from wtforms.widgets import TextArea
from dateutil.relativedelta import relativedelta
import datetime


def validate_date_of_birth(form, field):  # pylint: disable=unused-argument
    min_age = datetime.datetime.now() - relativedelta(years=18)
    if field.data > min_age.date():
        raise ValidationError("You must be at least 18 years old to sign up")


class SignupForm(FlaskForm):
    """ Customer signs up using this form """
    first_name = StringField("first_name", validators=[DataRequired(), Regexp(
        r"^[a-zA-Z]+$", message="First name can only contain letters"), Length(min=1, max=25)])
    last_name = StringField("last_name", validators=[DataRequired(), Regexp(
        r"^[a-zA-Z]+$", message="Last name can only contain letters"), Length(min=1, max=25)])
    email = EmailField("email", validators=[DataRequired()])
    email_verification_code = StringField(
        "email_verification_code", validators=[Length(min=6, max=6), Regexp(r"^[0-9]+$", message="Verfication code can only consist of digits")])
    phone_number = StringField("phone_number", validators=[
        DataRequired(), Length(min=10, max=10), Regexp(r"^[0-9]+$", message="Phone number can only consist of digits")])
    phone_number_verification_code = StringField(
        "phone_number_verification_code", validators=[Length(min=6, max=6), Regexp(r"^[0-9]+$", message="Verfication code can only consist of digits")])
    date_of_birth = DateField("date_of_birth", validators=[
                              DataRequired(), validate_date_of_birth])
    gender = RadioField("gender", choices=[
                        "Male", "Female", "Other"], validators=[DataRequired()])
    password = PasswordField("password", [
        DataRequired(),
        Length(min=8, max=32),
        EqualTo("confirm_password", message="Passwords must match")
    ])
    confirm_password = PasswordField("confirm_password")

    # Submit button with text
    submit = SubmitField("submit")


class LoginForm(FlaskForm):
    """ Customer logs in using this form """
    email = EmailField("email", validators=[DataRequired()])
    password = PasswordField("password", [
        DataRequired(),
        Length(min=8, max=32),
    ])
    remember_me = BooleanField("remember_me")

    # Submit button with text
    submit = SubmitField("submit")


class MembershipForm(FlaskForm):
    """ Membership form for user membership """
    pricing = app.config["MEMBERSHIP_PRICING"]
    plan = HiddenField("Plan", default="monthly")
    plan_text = {
        "monthly": f"£{pricing['monthly']}/Month",
        "annual": f"£{pricing['annual']}/Annum"
    }
    submit = SubmitField("Purchase")

    def calculate_price(self):
        if self.plan.data == "monthly":
            return self.pricing["monthly"]
        else:
            return self.pricing["annual"]

    def get_interval(self):
        if self.plan.data == "monthly":
            return "month"
        else:
            return "year"

    def get_price(self):
        return self.calculate_price()

    def get_name(self):
        return f"Gymcorp {self.plan.data} Membership"

    def set_annual(self, value):
        self.pricing["annual"] = value

    def set_monthly(self, value):
        self.pricing["monthly"] = value


class ChangePasswordForm(FlaskForm):
    """ Change password form for customer """
    password = PasswordField("password", [
        DataRequired(),
        Length(min=8, max=32),
    ])
    new_password = PasswordField("new_password", [
        DataRequired(),
        Length(min=8, max=32),
        EqualTo("confirm_password", message="Passwords must match")
    ])
    confirm_password = PasswordField("confirm_password")
    submit = SubmitField("submit")


class ResetPasswordForm(FlaskForm):
    """ Reset password form for user """
    email = EmailField("email", validators=[DataRequired()])
    email_verification_code = StringField(
        "email_verification_code", validators=[DataRequired(), Length(min=6, max=6), Regexp(r"^[0-9]+$", message="Verfication code can only consist of digits")])
    password = PasswordField("new_password", [
        DataRequired(),
        Length(min=8, max=32),
        EqualTo("confirm_password", message="Passwords must match")
    ])
    confirm_password = PasswordField("confirm_password")
    submit = SubmitField("submit")


class Contact_Us(FlaskForm):
    """ User can use this form to contact the gym for any enquiries"""

    full_name = StringField("full_name", validators=[DataRequired()])
    email = EmailField("email", validators=[DataRequired()])

    options = [("pricingQuery", "Pricing Query"), ("sessionQuery", "Session Query"),
               ("facilityQuery", "Facility Query"), ("otherQuery", "Other Query")]

    message = StringField("message", validators=[
                          DataRequired()],  widget=TextArea())

    # Submit button with text
    submit = SubmitField("submit")
