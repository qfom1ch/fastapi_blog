import smtplib
from datetime import timedelta
from email.message import EmailMessage

from celery import Celery

from apps.user import security
from config import (ACCESS_TOKEN_EXPIRE_MINUTES, APP_PORT, REDIS_HOST,
                    REDIS_PORT, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER)

celery = Celery('tasks', broker=f'redis://{REDIS_HOST}:{REDIS_PORT}')


def setup_email_for_verification(username: str, user_email: str):
    token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    verification_token = security.create_access_token(
        data={"sub": username},
        expires_delta=token_expires,
    )

    email = EmailMessage()
    email['Subject'] = 'Подтверждение электронной почты'
    email['From'] = SMTP_USER
    email['To'] = user_email

    email.set_content(
        '<div>'
        f'<h1 style="color: green;">Здравствуйте, {username}, подтвердите ваш '
        f'электронный адрес: '
        f'http://0.0.0.0:{APP_PORT}/users/verification_email/?token='
        f'{verification_token}😊</h1>'
        '-management-dashboard-ui-design-template-suitable-designing'
        '-application-for-android-and-ios-clean-style-apps'
        '-mobile-free-vector.jpg" width="600">'
        '</div>',
        subtype='html'
    )
    return email


@celery.task
def send_email_for_verification(username: str, user_email):
    email = setup_email_for_verification(username, user_email)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(email)
