import requests
from rest_framework import serializers, status

from pokerboard.models import Pokerboard
from pokerplanner import settings
from session.models import Session


class SessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Session
        fields = '__all__'
        extra_kwargs = {
            'status': {'read_only': True}
        }

    