""" Preload CSV data """
import pandas as pd
from app.bookings.models import FacilityModel, ActivityModel, DiscountModel
from flask import current_app as app


#  Load csv file from path
def csv_load(file_name):
    csv_data = pd.read_csv(file_name, delimiter="|", header=0)
    return csv_data.to_numpy()


# Preload activities
def load_activities(db):
    try:
        # Delete all old data
        FacilityModel.query.delete()
        ActivityModel.query.delete()
        DiscountModel.query.delete()

        # Create basic discount
        discount = DiscountModel(discount=1-(app.config["BASE_DISCOUNT"] / 100))
        db.session.add(discount)

        facilities = csv_load("./csvdata/facilities.csv")
        activities = csv_load("./csvdata/activities.csv")
        # Add facilities sequentially
        for i in facilities:  # type: ignore
            facility_record = FacilityModel(
                name=i[0],
                capacity=i[1]
            )
            db.session().add(facility_record)
            db.session().flush()
            # For each facility, find appropriate activities
            for j in activities:  # type: ignore
                # Add the activities that match with the correct foreign key
                if j[0] == i[0]:
                    activity_record = ActivityModel(
                        name=j[1],
                        booking_type=j[2],
                        price=j[3],
                        duration=j[4],
                        times=j[5],
                        facility_id=facility_record.id
                    )
                    db.session().add(activity_record)
        db.session().commit()
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(str(e))
        db.session().rollback()
    finally:
        db.session().close()
