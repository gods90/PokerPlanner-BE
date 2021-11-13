from user.email_send import send_welcome_mail
from pokerplanner.celery import app


@app.task(name='send_welcome_mail')
def send_welcome_mail_task(first_name, last_name, to_email):
    return send_welcome_mail(first_name, last_name, to_email)
