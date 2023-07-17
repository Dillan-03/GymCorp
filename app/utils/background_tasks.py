""" Background tasks to ensure database is updated """
from app.bookings.models import BookingModel, SessionModel, ActivityModel, ArchivedBookingModel, ArchivedSessionModel
from app.user.models import CustomerModel
from app.utils.extensions import db
from sqlalchemy import func, text
import stripe
import time

# pylint: disable=unused-variable
# pylint: disable=broad-exception-caught


def start_tasks(scheduler, app):
    scheduler.add_job(check_payment_status, "interval", args=[app],
                      seconds=30)
    scheduler.add_job(clean_sessions_bookings, "interval", args=[app],
                      minutes=1)
    # scheduler.add_job(archive_bookings, "interval", args=[app], minutes=1)
    scheduler.add_job(check_membership_status, "interval", args=[app],
                      seconds=30)
    scheduler.start()


# Check if membership has expired
def check_membership_status(app):
    with app.app_context():
        customers = db.session.query(CustomerModel).all()
        try:
            stripe.api_key = app.config["STRIPE_SECRET_KEY"]
            for customer in customers:
                if not customer.membership_checkout:
                    customer.membership = False
                    db.session.flush()
                    continue
                checkout_session = stripe.checkout.Session.retrieve(
                    customer.membership_checkout)
                subscription = stripe.Subscription.retrieve(
                    checkout_session["subscription"])
                if subscription["status"] == "active":
                    customer.membership = True
                    db.session.flush()
                else:
                    if subscription["status"] == "incomplete_expired" or subscription["status"] == "canceled":
                        customer.membership_checkout = None
                    customer.membership = False
                    db.session.flush()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
        finally:
            db.session.close()


# Archive old bookings that have passed its duration time
def archive_bookings(app):
    with app.app_context():
        old_bookings = db.session.query(BookingModel, SessionModel, ActivityModel).\
            join(SessionModel, SessionModel.id == BookingModel.session_id).\
            join(ActivityModel, ActivityModel.id == SessionModel.activity_id).filter(
            func.date(SessionModel.date, text("'+' || duration || ' minutes'"),
                      text("'+' || start_time || ' hours'")) < func.datetime()
        ).all()
        try:
            deleted_sessions = []
            session_id_map = {}
            for (booking, session, activity) in old_bookings:
                session_id_map[session.id] = session.serialize
                if session.id not in deleted_sessions:
                    archived_session = ArchivedSessionModel(
                        date=session.date, start_time=session.start_time, number_of_people=session.number_of_people, activity_id=activity.id)
                    db.session.add(archived_session)
                    db.session.flush()
                    session_id_map[session.id]["new_id"] = archived_session.id
                    deleted_sessions.append(session.id)
                    db.session.delete(session)
            for (booking, session, activity) in old_bookings:
                archived_booking = ArchivedBookingModel(customer_id=booking.customer_id, employee_id=booking.employee_id, session_id=session_id_map[booking.session_id]["new_id"], activity_id=activity.id,
                                                        number_of_people=booking.number_of_people, cost=booking.cost, checkout_session=booking.checkout_session, paid=booking.paid)
                db.session.add(archived_booking)
                db.session.delete(booking)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
        finally:
            db.session.close()


# Clean any bookings or sessions that do not have any associated bookings
def clean_sessions_bookings(app):
    with app.app_context():
        sessions = SessionModel.query.all()
        bookings = BookingModel.query.all()
        # Session ids that exist
        session_ids = set()
        # Number of people for each session id
        number_of_people = {}
        for booking in bookings:
            # Add number of people for each session
            if booking.session_id not in number_of_people:
                number_of_people[booking.session_id] = booking.number_of_people
            else:
                number_of_people[booking.session_id] += booking.number_of_people
        for session in sessions:
            # Delete sessions that do not have associated bookings
            if session.id not in number_of_people:
                db.session.delete(session)
            else:
                # Change number of people corresponding to bookings
                session.number_of_people = number_of_people[session.id]
            session_ids.add(session.id)
        for booking in bookings:
            # Check if bookings do not have associated sessions
            if booking.session_id not in session_ids:
                db.session.delete(booking)
        db.session.commit()
        db.session.close()


# Check if payments have been made or not
def check_payment_status(app):
    with app.app_context():
        stripe.api_key = app.config["STRIPE_SECRET_KEY"]
        bookings = BookingModel.query.all()
        for booking in bookings:
            if booking.paid is True:
                continue
            if booking.checkout_session is None:
                continue
            checkout_session = stripe.checkout.Session.retrieve(
                booking.checkout_session)
            if checkout_session is None:
                # Delete booking if checkout session is not real
                db.session.delete(booking)
                continue
            # Check if it has been paid for
            if checkout_session.payment_status == "paid":
                booking.paid = True
            # Check if expired
            elif checkout_session.expires_at < int(time.time()):
                db.session.delete(booking)
            else:
                booking.paid = False
        db.session.commit()
        db.session.close()
