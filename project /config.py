""" Config module """
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """ The configuration class """
    SECRET_KEY = os.environ.get("SECRET_KEY") or "a-very-secret-key"
    WTF_CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URI") or "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Page title
    TITLE = "GymCorp"
    OPENING_TIME = 8
    CLOSING_TIME = 22
    # How many days in advance we can book
    DAYS_ADVANCE = 14
    # Base discount
    BASE_DISCOUNT = 15
    # Membership pricing
    MEMBERSHIP_PRICING = {
        "monthly": 35,
        "annual": 300
    }
    # Keys for stripe
    STRIPE_PUBLIC_KEY = os.environ.get(
        "STRIPE_PUBLIC_KEY") or "pk_test_51MksyJKqVel0EiFXMBezLX7HOOUgCPhMmlH47GV3wK0qxnbWpQ8ZXYWrsxh8oH3iRNJQ3A9eiMJy7TIJg7KpkOQy00I3uf41HR"
    STRIPE_SECRET_KEY = os.environ.get(
        "STRIPE_SECRET_KEY") or "sk_test_51MksyJKqVel0EiFX1jM0yPVcGCcCH0vqpRQbDFRdVGZF6dOYq8pNBCliztzNVK81FvDp7s6r75MVDyuqoK18naq6004qVCifjK"
    # Admin details
    MANAGER_EMAIL = os.environ.get("MANAGER_EMAIL") or "admin@admin.com"
    MANAGER_PASSWORD = os.environ.get("MANAGER_PASSWORD") or "admin123"
    # Mail details
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME") or "gymcorp@inbox.lv"
    SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
    # Twilio details
    TWILIO_ACCOUNT_SID = os.environ.get(
        "TWILIO_ACCOUNT_SID") or "AC3dc7f671351305e2e72952f3185bb0f0"
    TWILIO_AUTH_TOKEN = os.environ.get(
        "TWILIO_AUTH_TOKEN") or "e449813828fdf004b40409274495d24f"
    TWILIO_SERVICE_SID = os.environ.get(
        "TWILIO_SERVICE_SID") or "VA6e32ca36b8962cfff728cb3aef542bd8"
