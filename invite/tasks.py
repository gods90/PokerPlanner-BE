from invite.email_send import send_invite_mail
from celery.decorators import task


@task(name='send_invite_to_pokerboard_mail')
def send_invite_email_task(manager_email, to_email):
    return send_invite_mail(manager_email, to_email)