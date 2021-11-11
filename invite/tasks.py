from invite.email_send import send_invite_mail
from pokerplanner.celery import app


@app.task(name='send_invite_to_pokerboard_mail')
def send_invite_email_task(manager_email, to_email, invite):
    return send_invite_mail(manager_email, to_email, invite)
