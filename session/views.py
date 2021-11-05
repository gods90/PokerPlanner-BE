from rest_framework import viewsets, status
from rest_framework.generics import CreateAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers

from pokerboard.models import Ticket

from session.models import Session
from session.serializers import CommentSerializer, SessionSerializer
from pokerplanner.settings import JIRA


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
        session_id = self.kwargs["pk"]
        active_session = get_object_or_404(Session, id=session_id,status=Session.ONGOING)
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
        allComments={}
        allComments["comments"]=[]
        for res in response["comments"]:
            comment={}
            comment["author"]=res["author"]["displayName"]
            comment["created"]=res["created"]
            comment["body"]=res["body"]
            allComments["comments"].append(comment)
        return Response(allComments, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={**request.data,"issue":kwargs["issue_key"]})
        serializer.is_valid(raise_exception=True)
        issue=serializer.validated_data["issue"]
        comment=serializer.validated_data["comment"]
        JIRA.issue_add_comment(issue,comment)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers) 
        

