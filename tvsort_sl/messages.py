import os

from sendgrid import sendgrid, Email
from sendgrid.helpers.mail import Content, Mail


def send_email(subject, content):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(name='TV sort', email='tvsortsl@gmail.com')
    to_email = Email(name='TV sort', email='tvsortsl@gmail.com')
    content = Content("text/plain", content)
    mail = Mail(from_email, subject, to_email, content)
    return sg.client.mail.send.post(request_body=mail.get())
