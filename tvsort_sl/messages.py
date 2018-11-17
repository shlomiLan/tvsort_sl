import os

from sendgrid import sendgrid, Email
from sendgrid.helpers.mail import Content, Mail, MailSettings, SandBoxMode


def Send_email(subject, content):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get("SENDGRID_API_KEY"))
    from_email = Email(name="TV sort", email="tvsortsl@gmail.com")
    to_email = Email(name="TV sort", email="tvsortsl@gmail.com")
    content = Content("text/plain", content)
    mail = Mail(from_email, subject, to_email, content)
    sand_box = os.environ.get("SAND_BOX")

    if sand_box == "true":
        mail_settings = MailSettings()
        mail_settings.sandbox_mode = SandBoxMode(True)
        mail.mail_settings = mail_settings

    return sg.client.mail.send.post(request_body=mail.get())
