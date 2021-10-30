from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from pokerboard.models import Ticket

from session.models import Session
from session.serializers import SessionSerializer


class SessionViewSet(viewsets.ModelViewSet):
    """
    Session View for CRUD operations
    """
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]

    http_method_names = ['get', 'post']
    
    def get_object(self):
        """
        To get the active session of the pokerboard.
        """
        pokerboard_id = self.kwargs["pk"]
        active_session = get_object_or_404(
            Session, pokerboard_id=pokerboard_id, status=Session.ONGOING
        )
        return active_session

    def create(self, request, *args, **kwargs):
        tickets = request.data['tickets']
        tickets.sort(key = lambda x : x['order'])
        for ind, ticket in enumerate(tickets):
            if ind > 0 and tickets[ind]['order'] == tickets[ind-1]['order']:
                raise serializers.ValidationError('Invalid ordering!')
        
        ticket_queryset = []
        for ticket in tickets:
            ticket_ = get_object_or_404(Ticket, ticket_id=ticket['ticket_id'])
            ticket_.order = ticket['order']
            ticket_queryset.append(ticket_)
        
        res = super().create(request, *args, **kwargs)
        Ticket.objects.bulk_update(ticket_queryset, ['order'])
        return res
