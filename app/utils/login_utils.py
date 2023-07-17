"""Login utilities for Flask-Login"""
from flask import abort, session
from functools import wraps
from app.user.models import CustomerModel, EmployeeModel
from app.utils.extensions import db


# Login loaders for retrieving data
# From session determines if customer to employee
def loaders(login_manager):
    @login_manager.user_loader
    def load_user(user_id):
        if session["user_role"] == "customer":
            return db.session.get(CustomerModel, user_id)
        return db.session.get(EmployeeModel, user_id)


# Login required decorator
# This is function is to ensure the session has the specified role
# Called when there is an attempt to access a page
def role_required(roles):
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            user_role = session.get("user_role")
            if user_role not in roles:
                abort(403)  # Error for forbidden access
            return func(*args, **kwargs)
        return wrapped
    return decorator


# Manager required decorator
# Specifically used for managers who have elevated priviledges and above priority
def manager_required(required: bool):
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if required is False:
                return func(*args, **kwargs)
            if "manager" not in session:
                abort(403)  # Error for forbidden access
            manager = session.get("manager")
            if manager is not required:
                abort(403)
            return func(*args, **kwargs)
        return wrapped
    return decorator
