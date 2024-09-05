import smtplib
from email.message import EmailMessage

from fastapi import HTTPException
from starlette import status

import config
from celery_app import celery_app

smtp = smtplib.SMTP(host=config.SMTP_HOST, port=config.SMTP_PORT)


def init_smtp(**kwargs):
    if config.SMTP_HOST is None:
        raise RuntimeError("activate .env file before starting celery")
    smtp.starttls()
    smtp.login(config.SMTP_EMAIL, config.SMTP_PASSWORD)


def quit_smtp(**kwargs):
    smtp.quit()


@celery_app.task
def send_email(to: list[str] | str, content: str):
    if isinstance(to, str):
        to = [to]
    if any('\r' in addr or '\n' in addr for addr in to):  # preventing header injection
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='email address can not contain \\r or \\n')
    message = EmailMessage()
    message['From'] = config.SMTP_EMAIL
    message['To'] = ', '.join(to)
    message.set_content(content)
    smtp.send_message(message)
