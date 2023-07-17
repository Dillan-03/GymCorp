""" Customer Database model """
from app.utils.extensions import db
from flask_login import UserMixin


class CustomerModel(UserMixin, db.Model):  # type: ignore
    """ DB Model for the customers table """

    def __init__(self, first_name, last_name, email, phone_number, date_of_birth, gender, password, membership, membership_checkout=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.password = password
        self.membership = membership
        self.membership_checkout = membership_checkout

    __tablename__ = "Customers"

    id = db.Column(db.Integer, primary_key=True, index=True)
    first_name = db.Column(db.String(25), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(320), unique=True, nullable=False)
    phone_number = db.Column(db.String(10), unique=True, nullable=False)
    date_of_birth = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    membership = db.Column(db.Boolean, nullable=False)
    membership_checkout = db.Column(db.String(20), nullable=True)

    # Customer can have multiple bookings
    bookings = db.relationship("BookingModel", backref="Customers", lazy=True)


class EmployeeModel(UserMixin, db.Model):  # type: ignore
    """
    DB Model for the employees table
        - Each employee can handle many customers
        - Can create multiple bookings for different customers
    """

    def __init__(self, first_name, last_name, email, phone_number, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.password = password

    __tablename__ = "Employees"

    id = db.Column(db.Integer, primary_key=True, index=True)
    first_name = db.Column(db.String(25), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(320), unique=True, nullable=False)
    phone_number = db.Column(db.String(10), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    # Employees can have multiple bookings, each with different customers
    bookings = db.relationship("BookingModel", backref="Employees", lazy=True)
