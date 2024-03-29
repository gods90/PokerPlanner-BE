from django.db.models.query_utils import Q

from rest_framework import mixins, viewsets, status
from rest_framework.generics import CreateAPIView, get_object_or_404, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers

from pokerboard import constants
from pokerboard.models import Pokerboard, Ticket

from pokerboard import constants
from pokerplanner.settings import JIRA

from session.models import Session
from session.serializers import CommentSerializer, SessionGetSerializer, SessionSerializer


class SessionViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    """
    Session View for CRUD operations
    """
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['list']:
            return SessionGetSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user
        pokerboards = Pokerboard.objects.filter(
                Q(manager=user)| Q(invite__email=user.email,invite__status=constants.ACCEPTED)
            ).distinct()
        sessions = Session.objects.filter(pokerboard__in=pokerboards, status=constants.ONGOING)
        return sessions

    def get_object(self):
        """
        To get the active session of the pokerboard.
        """
        session_id = self.kwargs["pk"]
        active_session = get_object_or_404(Session, id=session_id, status=constants.ONGOING)
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


class CommentView(CreateAPIView,RetrieveAPIView):
    """
    Comment on a Ticket on JIRA
    """ 
    serializer_class = CommentSerializer
    
    def get(self, request, issue_key):
        """
        Get comments on a JIRA ticket
        """
        response = JIRA.get_issue(issue_key)['fields']['comment']
        all_comments = {}
        all_comments["comments"] = []
        for res in response["comments"]:
            comment = {}
            comment["author"] = res["author"]["displayName"]
            comment["created"] = res["created"]
            comment["body"] = res["body"]
            all_comments["comments"].append(comment)
        return Response(all_comments, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Post comment on JIRA Ticket.
        """
        serializer = self.get_serializer(data={**request.data, "issue":kwargs["issue_key"]})
        serializer.is_valid(raise_exception=True)
        issue = serializer.validated_data["issue"]
        comment = serializer.validated_data["comment"]
        JIRA.issue_add_comment(issue, comment)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers) 
