from rest_framework import serializers

from user.models import User

class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']

