""" Init app """
import click
import flask
import atexit
from config import Config
from app.utils.extensions import db, bcrypt, babel, migrate, login_manager, csrf, limiter
from app.utils.login_utils import loaders
from app.utils.load_data import load_activities
from app.utils.background_tasks import start_tasks
from apscheduler.schedulers.background import BackgroundScheduler


# pylint: disable=import-outside-toplevel


def create_app(config_class=Config):
    app = flask.Flask(__name__)
    app.config.from_object(config_class)

    # Initialize flask extensions
    babel.init_app(app)
    bcrypt.init_app(app)
    db.init_app(app)
    migrate.init_app(app)
    login_manager.init_app(app)
    loaders(login_manager)
    csrf.init_app(app)
    limiter.init_app(app)

    # Preload command to load CSV data
    # Only ran when "flask preload" is ran
    @click.command(name="preload")
    @flask.cli.with_appcontext
    def preload():
        load_activities(db)
    app.cli.add_command(preload)

    with app.app_context():
        # Import blueprint paths
        from app.home import home  # noqa
        from app.user import customer, employee  # noqa
        from app.bookings import bookings  # noqa
        from app.manager import manager  # noqa
        # Register blueprints
        app.register_blueprint(home.home_bp)
        app.register_blueprint(customer.customer_bp)
        app.register_blueprint(employee.employee_bp)
        app.register_blueprint(bookings.bookings_bp)
        app.register_blueprint(manager.manager_bp)

        # Start background tasks
        scheduler = BackgroundScheduler()
        start_tasks(scheduler, app)

        # Register a function to stop the scheduler when the Python interpreter is exited
        atexit.register(lambda: scheduler.shutdown())

        return app
