""" Manager interface forms """
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Regexp, NumberRange
from wtforms import StringField, SubmitField, SelectField, TextAreaField, RadioField, DecimalField, EmailField, PasswordField, IntegerField, SelectMultipleField
from wtforms.widgets import ListWidget, CheckboxInput


class Manager(FlaskForm):
    """ Manager will sign up using this form"""

    email = EmailField("email", validators=[DataRequired()])
    password = PasswordField("password", [
        DataRequired(),
        Length(min=3, max=32),
    ])

    # Submit button with text
    submit = SubmitField("submit")


class EmployeeForm(FlaskForm):
    """ Employee signs up using this form """
    first_name = StringField("first_name", validators=[DataRequired(), Regexp(
        r"^[a-zA-Z]+$", message="First name can only contain letters"), Length(min=1, max=25)])
    last_name = StringField("last_name", validators=[DataRequired(), Regexp(
        r"^[a-zA-Z]+$", message="Last name can only contain letters"), Length(min=1, max=25)])
    email = EmailField("email", validators=[DataRequired()])
    phone_number = StringField("phone_number", validators=[
        DataRequired(), Length(min=10, max=10), Regexp(r"^[0-9]+$", message="Phone number can only consist of digits")])
    password = PasswordField("password", [
        DataRequired(),
        Length(min=8, max=32)
    ])

    # Submit button with text
    submit = SubmitField("submit")


class FacilityForm(FlaskForm):
    """ Create new facility using this form """

    name = StringField("name", validators=[DataRequired()])
    capacity = IntegerField("capacity", validators=[DataRequired(),
                                                    NumberRange(min=1, max=999, message="Invalid Capacity")])

    # Submit button with text
    submit = SubmitField("submit")


class ChangeCapacity(FlaskForm):
    """ Change capacity using this form """

    amend_name = StringField("name", validators=[DataRequired()])
    amend_capacity = IntegerField("capacity", validators=[DataRequired(),
                                                          NumberRange(min=1, max=999, message="Invalid Capacity")])

    # Submit button with text
    amend_submit = SubmitField("submit")

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()
    
class ActivityForm(FlaskForm):
    """ Create a new activity """

    def __init__(self, facility_names):
        super(ActivityForm, self).__init__()
        self.facility_name.choices = [(name, name) for name in facility_names]

    name = StringField("name", validators=[
        DataRequired(), Length(min=1, max=100)])
    booking_type = RadioField("booking_type", choices=[
                              "BOOKING", "SESSION", "TEAMEVENT"], validators=[DataRequired()])
    price = DecimalField("price", validators=[DataRequired(), NumberRange(
        min=0, message='Price must greater than 0')])
    duration = IntegerField("duration", validators=[
        NumberRange(min=0, max=999), DataRequired()])

    options = [('Monday', 'Monday'),
               ('Tuesday', 'Tuesday'),
               ('Wednesday', 'Wednesday'),
               ('Thursday', 'Thursday'),
               ('Friday', 'Friday'),
               ('Saturday', 'Saturday'),
               ('Sunday', 'Sunday')]
    days = MultiCheckboxField('Choices', choices=options)
    times = IntegerField("time", validators=[NumberRange(8, 21), DataRequired()])
    facility_name = SelectField(
        "facility_name", validators=[DataRequired()])
    # # Submit button with text
    add_activity = SubmitField("Submit")


class AmendActivityForm(FlaskForm):
    """ Amend an activity """

    def __init__(self, facility_names):
        super(AmendActivityForm, self).__init__()
        self.amend_facility_name.choices = [
            (name, name) for name in facility_names]

    amend_name = StringField("name", validators=[
        DataRequired(), Length(min=1, max=100)])
    amend_price = DecimalField("price", validators=[DataRequired()])
    amend_facility_name = SelectField(
        "amend_facility_name", validators=[DataRequired()])

    # Submit button with text
    amend_activity_submit = SubmitField("Submit")


class DiscountAmount(FlaskForm):
    discount = IntegerField("discount", validators=[DataRequired(),
                                                    NumberRange(min=1, max=50, message="Discount")])

    # Submit button with text
    submit = SubmitField("submit")
