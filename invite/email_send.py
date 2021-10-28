from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings

import jwt


def send_invite_mail(manager_email, recipient, invite_id):
    token = jwt.encode(
        {'invite_id': invite_id},
        settings.SECRET_KEY, settings.JWT_HASHING_ALGORITHM
    )
    context = {
        'manager_email': manager_email,
        'token': token,
        'domain_name': 'http://127.0.0.1:5500/#!/signup'
    }
    email_subject = 'Invitation to pokerboard',
    html_body = render_to_string(
        'invite_pokerboard_email_msg.html', context
    )
    plain_text_body = strip_tags(html_body)
    send_mail(email_subject, plain_text_body, settings.DEFAULT_FROM_EMAIL,
              [recipient, ], html_message=html_body)
