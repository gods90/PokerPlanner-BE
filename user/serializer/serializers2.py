from user.models import User
from rest_framework import serializers

class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']