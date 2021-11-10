from django.db.models.expressions import Case, Value, When

from rest_framework import serializers

from pokerboard.models import Pokerboard, Ticket

from session.models import Session

class TicketSerializerSessionCreate(serializers.Serializer):
    """
    Serializer for validating tickets when creating new session
    """
    ticket_id = serializers.CharField()
    order = serializers.IntegerField()


class SessionSerializer(serializers.ModelSerializer):
    """
    Serializer for session
    """
    status = serializers.CharField(source='get_status_display', read_only=True)
    pokerboard = serializers.PrimaryKeyRelatedField(
        queryset=Pokerboard.objects.all()
    )
    tickets = TicketSerializerSessionCreate(many=True, write_only=True)
    
    class Meta:
        model = Session
        fields = ['id', 'pokerboard', 'status', 'title', 'tickets']
    
    def validate_tickets(self, tickets):
        tickets.sort(key=lambda ticket: ticket['order'])
        for ind, ticket in enumerate(tickets):
            if ind > 0 and tickets[ind]['order'] == tickets[ind-1]['order']:
                raise serializers.ValidationError('Invalid ordering!')
        
        tickets.sort(key=lambda ticket: ticket['ticket_id'])
        for ind, ticket in enumerate(tickets):
            if ind > 0 and tickets[ind]['ticket_id'] == tickets[ind-1]['ticket_id']:
                raise serializers.ValidationError('Invalid ticket ID!')
        return super().validate(tickets)
    
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

    def create(self, validated_data):
        """
        Updating ticket orders and creating new session.
        """
        tickets = {ticket['ticket_id']: ticket['order'] for ticket in validated_data['tickets']}
        update_order_when_list = [When(ticket_id=ticket_id, then=Value(tickets[ticket_id])) for ticket_id in tickets.keys()]
        validated_data.pop('tickets')
        Ticket.objects.filter(ticket_id__in=tickets).update(
            order=Case(*update_order_when_list, )
        )
        return super().create(validated_data)

class MethodSerializer(serializers.Serializer):
    """
    Method serializer to check valid method name and method value is dictionary.
    """
    method_name = serializers.ChoiceField(
        choices=["estimate", "start_game", "skip_ticket", "start_timer", "final_estimate"]
    )
    method_value = serializers.DictField()


class CommentSerializer(serializers.Serializer):
    """
    Comment serializer with comment and the issue to comment on
    """
    comment = serializers.CharField()
    issue = serializers.SlugField()
