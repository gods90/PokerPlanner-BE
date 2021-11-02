from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework import exceptions

from django.conf import settings
from django.utils import timezone

from datetime import timedelta


class CustomTokenAuthentication(TokenAuthentication):
    model = Token

    def authenticate_credentials(self, key):
        res = super().authenticate_credentials(key)
        token = res[1]
        current_time = timezone.now()
        time_allowed = timedelta(hours=int(settings.TOKEN_EXPIRATION_TIME_IN_HOURS))
        if token.created + time_allowed < current_time:
            token.delete()
            raise exceptions.AuthenticationFailed(
                'Token has been expired. Please login again.'
            )
        return res
