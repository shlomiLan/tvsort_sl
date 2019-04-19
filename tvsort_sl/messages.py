import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, MailSettings, SandBoxMode


def send_email(subject, content):
    sendgrid_client = SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    message = Mail(
        from_email='tvsortsl@gmail.com',
        to_emails='tvsortsl@gmail.com',
        subject=subject,
        plain_text_content=content,
    )
    sand_box = os.environ.get('SAND_BOX')

    if sand_box == 'true':
        mail_settings = MailSettings()
        mail_settings.sandbox_mode = SandBoxMode(True)
        message.mail_settings = mail_settings

    return sendgrid_client.send(message)
