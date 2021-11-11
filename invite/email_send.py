from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings

from smtplib import SMTPException

import jwt

from invite.models import Invite


def send_invite_mail(manager_email, recipient, invite_id):
    """
    Function to send invitation to join pokerboard on email.
    """
    token = jwt.encode(
        {'invite_id': invite_id},
        settings.SECRET_KEY, settings.JWT_HASHING_ALGORITHM
    )
    context = {
        'manager_email': manager_email,
        'token': token,
        'domain_name': settings.DOMAIN_NAME + '/signup'
    }
    email_subject = 'Invitation to pokerboard',
    html_body = render_to_string(
        'invite_pokerboard_email_msg.html', context
    )
    plain_text_body = strip_tags(html_body)
    try:
        send_mail(
            email_subject, plain_text_body, settings.DEFAULT_FROM_EMAIL, recipient, html_message=html_body
        )
    except SMTPException:
        invite = Invite.objects.get(id=invite_id)
        invite.delete()
