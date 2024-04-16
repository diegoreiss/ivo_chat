import os
import smtplib
from email.message import EmailMessage


EMAIL_SENDER_SMTP_SSL = os.getenv('EMAIL_SENDER_SMTP_SSL')
EMAIL_SENDER_NAME = os.getenv('EMAIL_SENDER_NAME')
EMAIL_SENDER_PASSWORD = os.getenv('EMAIL_SENDER_PASSWORD')
EMAIL_SENDER_PORT = os.getenv('EMAIL_SENDER_PORT')


def send_email(subject, msg_to, content):
    msg = EmailMessage()
    msg['subject'] = subject
    msg['From'] = EMAIL_SENDER_NAME
    msg['To'] = msg_to
    msg.set_content(content)

    with smtplib.SMTP_SSL(EMAIL_SENDER_SMTP_SSL, EMAIL_SENDER_PORT) as smtp:
       smtp.login(EMAIL_SENDER_NAME, EMAIL_SENDER_PASSWORD)
       smtp.send_message(msg)
       