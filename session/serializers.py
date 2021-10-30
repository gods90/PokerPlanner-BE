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

