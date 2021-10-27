from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings


def send_invite_mail(manager_email, recipient):
    context = {
        'manager_email' : manager_email 
    }
    email_subject = 'Invitation to pokerboard',
    email_text_body = render_to_string('invite_pokerboard_email_msg.txt', context)
    email = EmailMessage(email_subject, email_text_body, settings.DEFAULT_FROM_EMAIL,
                                   [recipient, ], )
    return email.send(fail_silently=False)
