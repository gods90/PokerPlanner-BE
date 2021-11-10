from rest_framework import serializers
from pokerboard import constants

from pokerboard.models import Pokerboard
from pokerboard.constants import SESSION_METHOD_CHOICES
from session.models import Session


class SessionSerializer(serializers.ModelSerializer):
    """
    Serializer for session creation.
    """
    pokerboard = serializers.PrimaryKeyRelatedField(queryset=Pokerboard.objects.all())
    
    class Meta:
        model = Session
        fields = '__all__'

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["status"] =  constants.SESSION_STATUS_CHOICES[repr["status"]][1]
        return repr
    
    def validate_pokerboard(self, attrs):
        """
        To validate only one session active at a time of pokerboard.
        """
        active_session = Session.objects.filter(pokerboard_id=attrs.id, status=Session.ONGOING)
        if active_session.exists():
            raise serializers.ValidationError(
                "An active session already exists for this pokerboard."
            )
        return attrs


class MethodSerializer(serializers.Serializer):
    """
    Method serializer to check valid method name and method value is dictionary.
    """
    method_name = serializers.ChoiceField(choices=SESSION_METHOD_CHOICES)
    method_value = serializers.DictField()


class CommentSerializer(serializers.Serializer):
    """
    Comment serializer with comment and the issue to comment on
    """
    comment = serializers.CharField()
    issue = serializers.SlugField()
