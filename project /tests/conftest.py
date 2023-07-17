"""Conftest setup"""
# all the fixtures will be made in here and will need to be imported into their associated test files
import contextlib, pytest
from config import Config
# Import the app and db
from app import create_app
from app.utils.extensions import bcrypt, db as test_db
from app.user.models import CustomerModel, EmployeeModel
# Preload function
from app.utils.load_data import load_activities
from flask_login import login_user, logout_user
# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name


class TestConfig(Config):
    """ Test configuration class """
    # In memory DB
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True
    DEBUG = True
    # Disable login and CSRF from endpoints
    WTF_CSRF_ENABLED = False
    LOGIN_DISABLED = True


@pytest.fixture(scope="session")
def app():  # creating our test client
    # creating the flask app
    test_app = create_app(config_class=TestConfig)
    # Push app context
    ctx = test_app.test_request_context()
    ctx.push()
    # "yield" the test client to the function which takes test_client as a parameter, then the testing happens
    yield test_app
    # Pop the app context
    ctx.pop()


# Test client
@pytest.fixture
def client(app):
    return app.test_client()


# DB fixture for function
@pytest.fixture(scope='function')
def db(app):
    with db_impl(app) as result:
        yield result


# DB fixture for module
@pytest.fixture(scope='module')
def db_module(app):
    with db_impl(app) as result:
        yield result


# Create DB fixture implementation for tests
@contextlib.contextmanager
def db_impl(app):
    # Create the DB
    test_db.create_all()
    yield test_db
    # Explicitly close DB connection
    test_db.session.close()
    test_db.drop_all()


# Preload fixture for function
@pytest.fixture(scope='function')
def preload(app, db):
    with preload_impl(app, db) as result:
        yield result


# Preload fixture for module
@pytest.fixture(scope='module')
def preload_module(app, db_module):
    with preload_impl(app, db_module) as result:
        yield result

# Preload the DB implementation
@contextlib.contextmanager
def preload_impl(app, db):
    yield load_activities(db)



# User login fixture
@pytest.fixture(scope="function", autouse=True)
def user_login(client, app, db):
    # Create a customer user
    customer = CustomerModel(first_name="John", last_name="Doe", email="johndoe@email.com", phone_number="1234567890",
                             date_of_birth="2000-01-01", gender="Male", password=bcrypt.generate_password_hash("password").decode("utf-8"), membership=False)
    db.session.add(customer)
    db.session.commit()
    login_user(customer)
    # Store in session
    with client.session_transaction() as session:
        session["user_role"] = "customer"


# Employee login fixture
@pytest.fixture(scope="function")
def employee_login(client, app, db, user_login):
    # Logout customer user
    logout_user()
    # Create a employee user
    employee = EmployeeModel(first_name="John", last_name="Doe", email="johndoe@email.com",
                             phone_number="1234567890", password=bcrypt.generate_password_hash("password").decode("utf-8"))
    db.session.add(employee)
    db.session.commit()
    login_user(employee)
    # Store in session
    with client.session_transaction() as session:
        session["user_role"] = "employee"