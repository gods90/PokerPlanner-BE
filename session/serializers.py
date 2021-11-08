from rest_framework import serializers

from pokerboard.models import Pokerboard

from session.models import Session


class SessionSerializer(serializers.ModelSerializer):
    """
    Serializer for session
    """
    status = serializers.CharField(source='get_status_display', required=False)
    pokerboard = serializers.PrimaryKeyRelatedField(
        queryset=Pokerboard.objects.all()
    )
    class Meta:
        model = Session
        fields = '__all__'
    
    def validate_pokerboard(self, attrs):
        """
        To validate only one session active at a time of pokerboard.
        """
        active_session = Session.objects.filter(
            pokerboard_id=attrs.id, status=Session.ONGOING
        )
        if active_session.exists():
            raise serializers.ValidationError(
                "An active session already exists for this pokerboard."
            )
        return attrs


class MethodSerializer(serializers.Serializer):
    method_name = serializers.ChoiceField(choices=["estimate", "start_game", "skip_ticket", "start_timer", "final_estimate", "get_ticket_details"])
    method_value = serializers.DictField()


class CommentSerializer(serializers.Serializer):
    """
    Comment serializer with comment and the issue to comment on
    """
    comment = serializers.CharField()
    issue = serializers.SlugField()

