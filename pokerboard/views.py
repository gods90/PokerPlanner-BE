from rest_framework import serializers, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from pokerboard.models import Pokerboard,Ticket
from pokerboard.serializers import PokerBoardSerializer, PokerBoardCreationSerializer, TicketUpdateSerializer

from django.conf import settings

class PokerBoardViewSet(viewsets.ModelViewSet):
    """
    Pokerboard View for CRUD operations
    """
    queryset = Pokerboard.objects.all()
    serializer_class = PokerBoardSerializer
    permission_classes = [IsAuthenticated]

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

        jira = settings.JIRA
        pokerboard_id = kwargs['pk']
        pokerboard = Pokerboard.objects.get(pk=pokerboard_id)
        
        #If sprint, then fetch all tickets in sprint and add
        if 'sprint' in request.data.keys():
            sprint_id = request.data['sprint']
            issues = jira.get_sprint_issues(sprint_id,0,50)['issues']
            request.data['tickets'] = []
            for issue in issues:
                request.data['tickets'].append(issue['key'])

        #Adding tickets
        if 'tickets' in request.data.keys():
            tickets = request.data['tickets']
            
            ticket_responses = []
            for ticket in tickets:
                ticket_response = {}
                        
                try:
                    #Check if ticket is already part of another pokerboard
                    obj = Ticket.objects.filter(ticket_id=ticket)
                    if obj.exists():
                        if pokerboard != obj[0].pokerboard:
                            raise Exception('Ticket part of another pokerboard.')
                    
                    jira_response = jira.issue(key=ticket)['fields']
                    ticket_response = {**jira_response['status']}
                    ticket_response['estimate'] = jira_response['customfield_10016']
                    ticket_response['status_code'] = status.HTTP_200_OK
                except Exception as e:
                    ticket_response['message'] = str(e)
                    ticket_response['status_code'] = status.HTTP_400_BAD_REQUEST

                ticket_response['key'] = ticket
                ticket_responses.append(ticket_response)

            for ticket_response in ticket_responses:
                if ticket_response['status_code'] == 400:
                    continue
                new_ticket_data = {}
                new_ticket_data['pokerboard'] = pokerboard_id
                new_ticket_data['ticket_id'] = ticket_response['key']
                new_ticket_data['order'] = pokerboard.ticket_set.count()
                serializer = TicketUpdateSerializer(data=new_ticket_data)
                serializer.is_valid(raise_exception=True)
                try:
                    obj = Ticket.objects.get(ticket_id=ticket_response['key'])
                except Exception:
                    obj = Ticket.objects.create(**serializer.validated_data)

            response.data['ticket_responses'] = ticket_responses
        return response


