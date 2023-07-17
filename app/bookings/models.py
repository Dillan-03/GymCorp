""" Bookings Database models """
from decimal import Decimal
from app.utils.extensions import db
import enum


class BookingTypes(enum.Enum):
    BOOKING = 1
    SESSION = 2
    TEAMEVENT = 3


class FacilityModel(db.Model):
    """
    DB Model for the facilities table
        - Each facility can have multiple activities
    """

    def __init__(self, name, capacity):
        self.name = name
        self.capacity = int(capacity)  # Convert to integer

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            "id": self.id,
            "name": self.name,
            "capacity": self.capacity
        }

    __tablename__ = "Facilities"

    id = db.Column(db.Integer, nullable=False, primary_key=True, index=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    # Facilities can have multiple activities
    activities = db.relationship(
        "ActivityModel", backref="Facilities", lazy=True)


class ActivityModel(db.Model):  # type: ignore
    """
    DB Model for the activities table
        - Each activity has foreign key for the facility it resides in
        - May be a team event
    """

    def __init__(self, name, booking_type, price, duration, times, facility_id):
        self.name = name
        self.booking_type = booking_type
        self.price = Decimal(price)
        self.duration = duration
        self.times = times
        self.facility_id = facility_id

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            "id": self.id,
            "name": self.name,
            "booking_type": str(self.booking_type),
            "price": self.price,
            "duration": self.duration,
            "times": self.times,
            "facility_id": self.facility_id
        }

    __tablename__ = "Activities"

    id = db.Column(db.Integer, nullable=False, primary_key=True, index=True)
    name = db.Column(db.String(255), nullable=False)
    booking_type = db.Column(db.Enum(BookingTypes), nullable=False)
    price = db.Column(db.DECIMAL(scale=2), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    times = db.Column(db.String(255), nullable=False)
    facility_id = db.Column(db.Integer, db.ForeignKey(
        "Facilities.id"), nullable=False)

    # Activities have multiple bookings and sessions
    bookings = db.relationship("BookingModel", backref="Activities", lazy=True)
    sessions = db.relationship("SessionModel", backref="Activities", lazy=True)


class BookingMixin(object):
    """
    Mixin for the booking models
    """

    def __init__(self, customer_id, session_id, activity_id, number_of_people, cost, employee_id=None, checkout_session=None, paid=False):
        self.number_of_people = number_of_people
        self.customer_id = customer_id
        self.employee_id = employee_id
        self.session_id = session_id
        self.activity_id = activity_id
        self.cost = cost
        self.checkout_session = checkout_session
        self.paid = paid

    id = db.Column(db.Integer, nullable=False, primary_key=True, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey(
        "Customers.id"), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey("Employees.id"))
    activity_id = db.Column(db.Integer, db.ForeignKey(
        "Activities.id"), nullable=False)
    number_of_people = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.DECIMAL(scale=2), nullable=False)
    checkout_session = db.Column(db.String(255))
    paid = db.Column(db.Boolean, nullable=False)


class SessionMixin(object):
    """
    Mixin for the session models
    """

    def __init__(self, date, start_time, number_of_people, activity_id):
        self.date = date
        self.start_time = start_time
        self.number_of_people = number_of_people
        self.activity_id = activity_id

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            "id": self.id,
            "date": self.date,
            "start_time": self.start_time,
            "number_of_people": self.number_of_people,
            "activity_id": self.activity_id
        }

    id = db.Column(db.Integer, nullable=False, primary_key=True, index=True)
    date = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.Integer, nullable=False)
    number_of_people = db.Column(db.Integer, nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey(
        "Activities.id"), nullable=False)


class BookingModel(BookingMixin, db.Model):  # type: ignore
    """
    DB Model for the bookings table
        - Each booking has foreign keys for the customers, employees, session and the activity
    """

    __tablename__ = "Bookings"
    session_id = db.Column(db.Integer, db.ForeignKey(
        "Sessions.id"), nullable=False)
    pass


class SessionModel(SessionMixin, db.Model):  # type: ignore
    """
    DB Model for the sessions table
        - Each session is related to multiple bookings
        - It is related to a single activity
    """

    __tablename__ = "Sessions"
    bookings = db.relationship("BookingModel", backref="Sessions", lazy=True)
    pass


class ArchivedBookingModel(BookingMixin, db.Model):  # type: ignore
    """
    DB Model for the archived bookings table
        - Inherits from BookingMixin
    """
    __tablename__ = "ArchivedBookings"
    session_id = db.Column(db.Integer, db.ForeignKey(
        "ArchivedSessions.id"), nullable=False)
    pass


class ArchivedSessionModel(SessionMixin, db.Model):  # type: ignore
    """
    DB Model for the archived sessions table
        - Inherits from SessionMixin
    """

    __tablename__ = "ArchivedSessions"
    bookings = db.relationship(
        "ArchivedBookingModel", backref="ArchivedSessions", lazy=True)
    pass


class DiscountModel(db.Model):

    def __init__(self, discount):
        self.discount = discount

    __tablename__ = "Discount"

    discount = db.Column(db.DECIMAL(scale=2), nullable=True, primary_key=True)
