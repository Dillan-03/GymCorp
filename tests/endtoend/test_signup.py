"""Test the signup page."""

from flask import url_for
from playwright.sync_api import Page, expect
import datetime

class TestSignup:

    def test_non_alphabet_first_name(self, preload_module, live_server, page: Page):
        page.goto(url_for("home_bp.index", _external=True))
        page.get_by_role("link", name="Sign up").click()
        page.get_by_label("First name").click()
        page.get_by_label("First name").fill("John35")
        page.get_by_label("Last name").click()
        page.get_by_label("Last name").fill("Doe")
        page.get_by_label("Date of birth").fill("2002-06-13")
        page.get_by_label("Male", exact=True).check()
        page.get_by_label("Email", exact=True).click()
        page.get_by_label("Email", exact=True).fill("johndoe@email.com")
        page.get_by_label("Email verification code").click()
        page.get_by_label("Email verification code").fill("000000")
        page.get_by_label("SMS verification code").click()
        page.get_by_label("SMS verification code").fill("000000")
        page.get_by_label("Phone number").click()
        page.get_by_label("Phone number").fill("1234567891")
        page.get_by_label("Password", exact=True).click()
        page.get_by_label("Password", exact=True).fill("password")
        page.get_by_label("Confirm password").click()
        page.get_by_label("Confirm password").fill("password")
        page.get_by_role("button", name="Create").click()
        assert page.get_by_text("First name can only contain letters", exact=True).is_visible()

    def test_non_alphabet_second_name(self, preload_module, live_server, page: Page):
        page.goto(url_for("home_bp.index", _external=True))
        page.get_by_role("link", name="Sign up").click()
        page.get_by_label("First name").click()
        page.get_by_label("First name").fill("John")
        page.get_by_label("Last name").click()
        page.get_by_label("Last name").fill("Doe56")
        page.get_by_label("Date of birth").fill("2002-06-13")
        page.get_by_label("Male", exact=True).check()
        page.get_by_label("Email", exact=True).click()
        page.get_by_label("Email", exact=True).fill("johndoe@email.com")
        page.get_by_label("Email verification code").click()
        page.get_by_label("Email verification code").fill("000000")
        page.get_by_label("SMS verification code").click()
        page.get_by_label("SMS verification code").fill("000000")
        page.get_by_label("Phone number").click()
        page.get_by_label("Phone number").fill("1234567891")
        page.get_by_label("Password", exact=True).click()
        page.get_by_label("Password", exact=True).fill("password")
        page.get_by_label("Confirm password").click()
        page.get_by_label("Confirm password").fill("password")
        page.get_by_role("button", name="Create").click()
        assert page.get_by_text("Last name can only contain letters", exact=True).is_visible()


    def test_too_young(self, preload_module, live_server, page: Page):
        page.goto(url_for("home_bp.index", _external=True))
        page.get_by_role("link", name="Sign up").click()
        page.get_by_label("First name").click()
        page.get_by_label("First name").fill("John")
        page.get_by_label("Last name").click()
        page.get_by_label("Last name").fill("Doe")
        too_young_date = datetime.datetime.now() - datetime.timedelta(days=365 * 17)
        page.get_by_label("Date of birth").fill(
            too_young_date.strftime("%Y-%m-%d"))
        page.get_by_label("Male", exact=True).check()
        page.get_by_label("Email", exact=True).click()
        page.get_by_label("Email", exact=True).fill("johndoe@email.com")
        page.get_by_label("Email verification code").click()
        page.get_by_label("Email verification code").fill("000000")
        page.get_by_label("SMS verification code").click()
        page.get_by_label("SMS verification code").fill("000000")
        page.get_by_label("Phone number").click()
        page.get_by_label("Phone number").fill("1234567891")
        page.get_by_label("Password", exact=True).click()
        page.get_by_label("Password", exact=True).fill("password")
        page.get_by_label("Confirm password").click()
        page.get_by_label("Confirm password").fill("password")
        page.get_by_role("button", name="Create").click()
        assert page.get_by_text("You must be at least 18 years old to sign up", exact=True).is_visible()

    
    def test_wrong_confirm_password(self, preload_module, live_server, page: Page):
        page.goto(url_for("home_bp.index", _external=True))
        page.get_by_role("link", name="Sign up").click()
        page.get_by_label("First name").click()
        page.get_by_label("First name").fill("John")
        page.get_by_label("Last name").click()
        page.get_by_label("Last name").fill("Doe")
        page.get_by_label("Date of birth").fill("2002-06-13")
        page.get_by_label("Male", exact=True).check()
        page.get_by_label("Email", exact=True).click()
        page.get_by_label("Email", exact=True).fill("johndoe@email.com")
        page.get_by_label("Email verification code").click()
        page.get_by_label("Email verification code").fill("000000")
        page.get_by_label("SMS verification code").click()
        page.get_by_label("SMS verification code").fill("000000")
        page.get_by_label("Phone number").click()
        page.get_by_label("Phone number").fill("1234567891")
        page.get_by_label("Password", exact=True).click()
        page.get_by_label("Password", exact=True).fill("password")
        page.get_by_label("Confirm password").click()
        page.get_by_label("Confirm password").fill("password1")
        page.get_by_role("button", name="Create").click()
        assert page.get_by_text("Passwords must match", exact=True).is_visible()
