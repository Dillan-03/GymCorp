import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from flask import current_app as app


# Send an HTTP POST request to /mail/send
def send_email(to_email, subject, content):
    sg = sendgrid.SendGridAPIClient(api_key=app.config["SENDGRID_API_KEY"])
    mail = Mail(Email(app.config["MAIL_USERNAME"]), To(
        to_email), subject, Content("text/plain", content))
    mail_json = mail.get()
    response = sg.client.mail.send.post(request_body=mail_json)
