import requests
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from pokerboard.models import Pokerboard,Ticket
from pokerboard.serializers import PokerBoardSerializer, PokerBoardCreationSerializer, SprintSerializer, TicketsSerializer

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
        pokerboard = Pokerboard.objects.create(manager=request.user,**serializer.data)
        serializer = PokerBoardSerializer(instance=pokerboard)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
        

    def update(self, request, *args, **kwargs):
        """
        Update pokerboard details - title,description,config
        Request : 
            Required params : pokerboard_id
            Add new sprint  -
                param_name : sprint_id
                type : string
                example : 3
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
        if 'sprint_id' in request.data.keys():
            sprint_serializer = SprintSerializer(data=request.data)
            sprint_serializer.is_valid(raise_exception=True)
            sprint_id = sprint_serializer.validated_data['sprint_id']
            try:
                issues = jira.get_sprint_issues(sprint_id,0,50)['issues']
                request.data['tickets'] = []
                for issue in issues:
                    request.data['tickets'].append(issue['key'])
            except requests.exceptions.RequestException as e:
                return Response({'error' : str(e)},status=status.HTTP_404_NOT_FOUND)

        #Adding tickets
        if 'tickets' in request.data.keys():
            tickets = request.data['tickets']
            serializer = TicketsSerializer(data=tickets)
            serializer.is_valid(raise_exception=True)
            ticket_responses = []
            for ticket in tickets:
                ticket_response = {}   
                try:
                    #Check if ticket is already part of another pokerboard
                    obj = Ticket.objects.filter(ticket_id=ticket)
                    if obj.exists():
                        if pokerboard != obj[0].pokerboard:
                            raise Exception('Ticket part of another pokerboard.')
                        if pokerboard == obj[0].pokerboard:
                            raise Exception('Ticket already part of pokerboard')
                    #Checking with JIRA
                    jira_response = jira.issue(key=ticket)['fields']
                    ticket_response['estimate'] = jira_response['customfield_10016']
                    ticket_response['status_code'] = status.HTTP_200_OK
                except Exception as e:
                    ticket_response['message'] = str(e)
                    ticket_response['status_code'] = status.HTTP_404_NOT_FOUND

                ticket_response['key'] = ticket
                ticket_responses.append(ticket_response)

            count = pokerboard.ticket_set.count()
            
            for ticket_response in ticket_responses:
                if ticket_response['status_code'] != 200:
                    continue
                new_ticket_data = {}
                new_ticket_data['pokerboard'] = pokerboard
                new_ticket_data['ticket_id'] = ticket_response['key']
                count += 1
                new_ticket_data['order'] = count
                ticket_id = ticket_response['key']
                ticket_response.pop('key')
                Ticket.objects.get_or_create(ticket_id=ticket_id,defaults={**new_ticket_data})
                ticket_response['key'] = ticket_id
            response.data['ticket_responses'] = ticket_responses
        return response


