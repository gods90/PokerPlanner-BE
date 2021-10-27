from rest_framework import serializers

from group.models import Group


class GetGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ["name"]
