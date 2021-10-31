from rest_framework import serializers

from pokerboard.models import Pokerboard
from session.models import Session


class SessionSerializer(serializers.ModelSerializer):

    pokerboard = serializers.PrimaryKeyRelatedField(queryset=Pokerboard.objects.all())
    
    class Meta:
        model = Session
        fields = '__all__'

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["status"] =  Session.STATUS_CHOICES[repr["status"]][1]
        return repr
    
    def validate_pokerboard(self, attrs):
        """
        To validate only one session active at a time of pokerboard.
        """
        active_session = Session.objects.filter(pokerboard_id=attrs.id,status=Session.ONGOING)
        if active_session.exists():
            raise serializers.ValidationError("An active session already exists for this pokerboard.")
        return attrs


class MethodSerializer(serializers.Serializer):
    method_name = serializers.ChoiceField(choices=["estimate", "start_game", "skip_ticket", "start_timer"])
    method_value = serializers.DictField()


class CommentSerializer(serializers.Serializer):
    """
    Comment serializer with comment and the issue to comment on
    """
    comment = serializers.CharField()
    issue = serializers.SlugField()

