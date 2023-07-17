""" Test the /book endpoint """

import json
import datetime
from app.bookings.models import SessionModel, BookingModel
from app.user.models import CustomerModel
from decimal import Decimal

# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name


class TestBookings:
    """Tests for the bookings endpoint"""

    url = "/book"
    mimetype = "application/json"
    headers = {
        "Content-Type": mimetype,
        "Accept": mimetype
    }

    # Given there is no bookings data, return error
    def test_no_bookings_data(self, client):
        data = {}

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 400
        assert response.json["errors"][0] == "No bookings data received"

    # Given the bookings data type is invalid, return error
    def test_invalid_bookings_data_type(self, client):
        data = {
            "bookings": 1
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 400
        assert response.json["errors"][0] == "Invalid bookings data type"

    # Given the booking data type is invalid, return error
    def test_invalid_booking_data_type(self, client):
        data = {
            "bookings": [
                3, 4
            ]
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 400
        assert response.json["errors"][0] == "Invalid booking data type"
        assert response.json["errors"][1] == "Invalid booking data type"

    # Given there is no activity id, return error
    def test_no_activity_id(self, client):
        data = {
            "bookings": [{}]
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 400
        assert response.json["errors"][0] == "Not all fields received"

    # Given there is no date, return error
    def test_no_date(self, client):
        data = {
            "bookings": [{
                "activity_id": 1
            }]
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 400
        assert response.json["errors"][0] == "Not all fields received"

    # Given there is no time, return error
    def test_no_time(self, client):
        data = {
            "bookings": [{
                "activity_id": 1,
                "date": str(datetime.date.today()),
            }]
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 400
        assert response.json["errors"][0] == "Not all fields received"

    # Given the fields are of invalid type, return error
    def test_invalid_fields_type(self, client):
        data = {
            "bookings": [{
                "activity_id": "-3",
                "date": 56,
                "time": -9
            }]
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 400
        assert response.json["errors"][0] == "Invalid fields type"

    # Given the date is invalid, return error
    def test_invalid_date(self, client):
        data = {
            "bookings": [{
                "activity_id": 1,
                "date": "202-4-5",
                "time": "11:00",
            }]
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 400
        assert response.json["errors"][0] == "Invalid date or time"

    # Given the time is invalid, return error
    def test_invalid_time(self, client):
        data = {
            "bookings": [{
                "activity_id": 1,
                "date": str(datetime.date.today() + datetime.timedelta(days=1)),
                "time": "1:75",
            }]
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 400
        assert response.json["errors"][0] == "Invalid date or time"

    # Given the date is in the past, return error
    def test_date_in_past(self, client):
        data = {
            "bookings": [{
                "activity_id": 1,
                "date": "2021-03-03",
                "time": "11:00",
            }]
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 400
        assert response.json["errors"][0] == "Date in the past"

    # Given time is in the past, return error
    def test_time_in_past(self, client):
        data = {
            "bookings": [{
                "activity_id": 1,
                "date": str(datetime.date.today()),
                "time": str(datetime.datetime.now().strftime("%H:%M"))
            }]
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 400
        assert response.json["errors"][0] == "Session has already started"

    # Given the date is too far ahead in future, return error
    def test_date_outside_days_in_advance(self, client, app):
        data = {
            "bookings": [{
                "activity_id": 1,
                "date": str(datetime.date.today() + datetime.timedelta(days=app.config["DAYS_ADVANCE"])),
                "time": "11:00",
            }]
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 400
        assert response.json["errors"][0] == "Date is too far ahead"

    # Given the activity does not exist, return error
    def test_nonexistent_activity(self, client):
        data = {
            "bookings": [{
                "activity_id": 0,
                "date": str(datetime.date.today() + datetime.timedelta(days=1)),
                "time": "11:00",
            }]
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 400
        assert response.json["errors"][0] == "Activity does not exist"

    # Given there is no number of people, return error
    def test_no_number_of_people(self, client, db, preload):
        data = {
            "bookings": [{
                "activity_id": 1,
                "date": str(datetime.date.today() + datetime.timedelta(days=1)),
                "time": "11:00",
            }]
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 400
        assert response.json["errors"][0] == "Number of people not received"

    # Given there is an invalid number of people, return error
    def test_invalid_number_of_people_type(self, client, db, preload):
        data = {
            "bookings": [{
                "activity_id": 1,
                "date": str(datetime.date.today() + datetime.timedelta(days=1)),
                "time": "11:00",
                "number_of_people": "nop",
            }]
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 400
        assert response.json["errors"][0] == "Number of people invalid type"

    # Given there is an invalid number of people, return error
    def test_invalid_number_of_people(self, client, db, preload):
        data = {
            "bookings": [{
                "activity_id": 1,
                "date": str(datetime.date.today() + datetime.timedelta(days=1)),
                "time": "11:00",
                "number_of_people": -34,
            }]
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 400
        assert response.json["errors"][0] == "Number of people invalid"

    # Given time is not in times array, return error
    def test_time_unavailable(self, client, db, preload):
        data = {
            "bookings": [{
                "activity_id": 1,
                "date": str(datetime.date.today() + datetime.timedelta(days=1)),
                "time": "01:00",
                "number_of_people": 1,
            }]
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 400
        assert response.json["errors"][0] == "Time is not available"

    # Given a team event is occuring at the same time, return error
    def test_team_event_same_time(self, client, db, preload):
        # Swimming pool team event is Friday 8am in preload data, lasts for 2 hours
        data = {
            "bookings": [{
                "activity_id": 1,
                "date": str(datetime.date.today() + datetime.timedelta(((4-datetime.date.today().weekday()) % 7) + 7)),
                "time": "09:00",
                "number_of_people": 1,
            }]
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 400
        assert response.json["errors"][0] == "Time is not available"

    # Given the session is is already full, return error
    def test_session_full(self, client, db, preload):
        # Date and time of session defined
        start_time = "12"
        date = str(datetime.date.today() + datetime.timedelta(days=1))
        # Using activity 1
        activity_id = 1
        # Add a full session for a specific time
        session = SessionModel(date=date, start_time=start_time,
                               number_of_people=25, activity_id=activity_id)
        db.session.add(session)
        db.session.commit()

        # Test endpoint
        data = {
            "bookings": [{
                "activity_id": activity_id,
                "date": date,
                "time": start_time + ":00",
                "number_of_people": 6,
            }]
        }
        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 400
        assert response.json["errors"][0] == "Session is full"

    # Given the customer tries to send a customer user id, return success with their own id
    def test_unauthorized_customer_id(self, client, db, preload):
        # Create mock second user
        customer = CustomerModel(first_name="Jane", last_name="Doe", email="janedoe@email.com", phone_number="1234567891",
                                 date_of_birth="2000-01-01", gender="Female", password="mock", membership=False)
        db.session.add(customer)
        db.session.commit()

        date = str(datetime.date.today() + datetime.timedelta(days=1))
        data = {
            "bookings": [{
                "activity_id": 6,
                "date": date,
                "time": "12:00",
            }],
            "customer_id": customer.id
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 200

        # Make sure session created
        session = SessionModel.query.filter_by(
            activity_id=6, date=date, start_time=12, number_of_people=4).first()
        assert session is not None

        # Make sure booking exists with normal customer id
        booking = BookingModel.query.filter_by(
            customer_id=1, session_id=session.id, activity_id=6, number_of_people=4).first()
        assert booking is not None

    # Given the employee tries to book for a customer without a customer id
    def test_employee_without_customer(self, client, employee_login, db, preload):
        date = str(datetime.date.today() + datetime.timedelta(days=1))
        data = {
            "bookings": [{
                "activity_id": 6,
                "date": date,
                "time": "12:00",
            }],
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 500

    # Given the employee tries to book for a customer with an invalid customer id
    def test_employee_invalid_customer(self, client, employee_login, db, preload):
        date = str(datetime.date.today() + datetime.timedelta(days=1))
        data = {
            "bookings": [{
                "activity_id": 6,
                "date": date,
                "time": "12:00",
            }],
            "customer_id": "-4"
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 500

    # Given the employee tries to book for a customer with a customer id that does not exist
    def test_employee_nonexistent_customer(self, client, employee_login, db, preload):
        date = str(datetime.date.today() + datetime.timedelta(days=1))
        data = {
            "bookings": [{
                "activity_id": 6,
                "date": date,
                "time": "12:00",
            }],
            "customer_id": 18
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 500

    # Given the employee tries to book for a customer with a customer id that does not exist
    def test_employee_valid_booking(self, client, employee_login, db, preload):
        date = str(datetime.date.today() + datetime.timedelta(days=1))
        data = {
            "bookings": [{
                "activity_id": 6,
                "date": date,
                "time": "12:00",
            }],
            "customer_id": 1
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 200

        # Make sure session created
        session = SessionModel.query.filter_by(
            activity_id=6, date=date, start_time=12, number_of_people=4).first()
        assert session is not None

        # Make sure booking exists with normal customer id
        booking = BookingModel.query.filter_by(
            customer_id=1, employee_id=1, session_id=session.id, activity_id=6, number_of_people=4).first()
        assert booking is not None

    # Given the data is valid and a session exists, return success
    def test_valid_data_session(self, client, db, preload):
        # Date and time of session defined
        start_time = "14"
        date = str(datetime.date.today() + datetime.timedelta(days=1))
        # Using activity 1
        activity_id = 1
        # Add a not a full session for a specific time
        session = SessionModel(date=date, start_time=start_time,
                               number_of_people=25, activity_id=activity_id)
        db.session.add(session)
        db.session.commit()
        data = {
            "bookings": [{
                "activity_id": activity_id,
                "date": date,
                "time": start_time + ":00",
                "number_of_people": 3,
            }]
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 200

        # Make sure session changed with number of people
        assert session.number_of_people == 28

        # Make sure booking exists
        booking = BookingModel.query.filter_by(
            customer_id=1, session_id=session.id, activity_id=activity_id, number_of_people=3).first()
        assert booking is not None

    # Given the data is valid and a session does not exist, return success
    def test_valid_data_no_session(self, client, db, preload):
        date = str(datetime.date.today() + datetime.timedelta(days=1))
        data = {
            "bookings": [{
                "activity_id": 1,
                "date": date,
                "time": "16:00",
                "number_of_people": 7,
            }]
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 200

        # Make sure session created
        session = SessionModel.query.filter_by(
            activity_id=1, date=date, start_time=16, number_of_people=7).first()
        assert session is not None

        # Make sure booking exists
        booking = BookingModel.query.filter_by(
            customer_id=1, session_id=session.id, activity_id=1, number_of_people=7).first()
        assert booking is not None

    # Given the data is valid and there is an open booking, return success
    def test_valid_booking(self, client, db, preload):
        date = str(datetime.date.today() + datetime.timedelta(days=1))
        data = {
            "bookings": [{
                "activity_id": 6,
                "date": date,
                "time": "12:00",
            }]
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 200

        # Make sure session created
        session = SessionModel.query.filter_by(
            activity_id=6, date=date, start_time=12, number_of_people=4).first()
        assert session is not None

        # Make sure booking exists
        booking = BookingModel.query.filter_by(
            customer_id=1, session_id=session.id, activity_id=6, number_of_people=4).first()
        assert booking is not None

    # Given the data is valid and we are booking multiple sessions, return success
    def test_multiple_bookings(self, client, db, preload):
        date = str(datetime.date.today() + datetime.timedelta(days=1))
        data = {
            "bookings": [{
                "activity_id": 6,
                "date": date,
                "time": "12:00",
            }, {
                "activity_id": 1,
                "date": date,
                "time": "15:00",
                "number_of_people": 7,
            }, {
                "activity_id": 1,
                "date": date,
                "time": "16:00",
                "number_of_people": 7,
            }, {
                "activity_id": 1,
                "date": date,
                "time": "17:00",
                "number_of_people": 7,
            }]
        }

        response = client.post(
            self.url, data=json.dumps(data), headers=self.headers)

        assert response.status_code == 200

        # Make sure session created
        session = SessionModel.query.filter_by(
            activity_id=6, date=date, start_time=12, number_of_people=4).first()
        assert session is not None

        # Make sure booking exists
        booking = BookingModel.query.filter_by(
            customer_id=1, session_id=session.id, activity_id=6, number_of_people=4).first()
        assert booking is not None

        # Make sure second session created
        session = SessionModel.query.filter_by(
            activity_id=1, date=date, start_time=15, number_of_people=7).first()
        assert session is not None

        # Make sure second booking exists
        booking = BookingModel.query.filter_by(
            customer_id=1, session_id=session.id, activity_id=1, number_of_people=7).first()
        assert booking is not None

        # Make sure discount was applied
        assert booking.cost == Decimal("23.80")
