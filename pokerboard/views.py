from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from pokerboard.models import Pokerboard,Ticket
from pokerboard.serializers import PokerBoardSerializer, PokerBoardCreationSerializer, TicketSerializer

from django.conf import settings

class PokerBoardViewSet(viewsets.ModelViewSet):
    """
    Pokerboard View for CRUD operations
    """
    queryset = Pokerboard.objects.all()
    serializer_class = PokerBoardSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    def create(self, request, *args, **kwargs):
        """
        Create new pokerboard
        Required : Token in header, Title, Description
        Optional : Configuration
        """
        serializer = PokerBoardCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        manager = request.user
        pokerboard = Pokerboard.objects.create(manager=manager,**serializer.data)
        pokerboard.save()
        serializer = PokerBoardSerializer(instance=pokerboard)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
        

    def update(self, request, *args, **kwargs):
        """
        Update pokerboard details - title,description,config
        Request : 
            Required params : pokerboard_id
            Add new tickets - 
                param_name : tickets 
                type : array
                example : [MT-1,MT-2,MT-3]
        
        Response : 
        type : [{
            status_code : 200/404
            if status_code == 200, then id,summary,description,comments etc
            else error message
        }]

        """

        response = super().update(request, *args, **kwargs)
        if response.status_code != 200:
            return response

        pokerboard_id = kwargs['pk']
        pokerboard = Pokerboard.objects.get(pk=pokerboard_id)
        #Adding tickets
        if 'tickets' in request.data.keys():
            tickets = request.data['tickets']
            jira = settings.JIRA
            ticket_responses = []
            for ticket in tickets:
                ticket_response = {}
                try:
                    jira_response = jira.issue(key=ticket)['fields']
                    ticket_response = {**jira_response['status']}
                    ticket_response['estimate'] = jira_response['customfield_10016']
                    ticket_response['status_code'] = status.HTTP_200_OK
                except Exception as e:
                    ticket_response['message'] = str(e)
                    ticket_response['status_code'] = status.HTTP_400_BAD_REQUEST

                ticket_response['key'] = ticket
                ticket_responses.append(ticket_response)

        response.data['ticket_responses'] = ticket_responses
        return response


