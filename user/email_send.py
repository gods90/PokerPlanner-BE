from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings


def send_welcome_mail(first_name, last_name, recipient):
    """
    Function to send welcome email to new user.
    """
    context = {
        'first_name': first_name,
        'last_name': last_name,
        'domain_name': settings.DOMAIN_NAME
    }
    email_subject = 'Welcome!'
    html_body = render_to_string(
        'welcome_email.html', context
    )
    plain_text_body = strip_tags(html_body)
    send_mail(
        subject=email_subject, message=plain_text_body, from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient, html_message=html_body, fail_silently=True
    )
