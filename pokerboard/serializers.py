import requests

from rest_framework import serializers, status

from django.conf import settings

from pokerboard.models import Pokerboard, Ticket
from user.models import User
from user.serializers import UserSerializer


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['pokerboard', 'ticket_id', 'order', 'estimation_date', 'status']


class TicketsSerializer(serializers.ListSerializer):
    child = serializers.CharField()


class PokerBoardSerializer(serializers.ModelSerializer):
    manager = UserSerializer()
    ticket = TicketSerializer(source='ticket_set', many=True)

    class Meta:
        model = Pokerboard
        fields = ['id', 'manager', 'title', 'description',
                  'configuration', 'status', 'ticket']


class PokerBoardCreationSerializer(serializers.ModelSerializer):
    manager_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    sprint_id = serializers.CharField(required=False,write_only=True)
    tickets = TicketsSerializer(required=False,write_only=True)
    jql = serializers.CharField(required=False,write_only=True)
    ticket_responses = serializers.SerializerMethodField()

    class Meta:
        model = Pokerboard
        fields = ['manager_id', 'title', 'description','configuration', 'tickets', 'sprint_id', 'ticket_responses', 'jql']
        
    def get_ticket_responses(self, instance):
        jira = settings.JIRA
        data = dict(instance)
        ticket_responses = []

        myJql=""
        # If sprint, then fetch all tickets in sprint and add
        if 'sprint_id' in data.keys():
            myJql = "Sprint = "+ data['sprint_id']

        # Adding tickets
        if 'tickets' in data.keys():
            tickets = data['tickets']
            serializer = TicketsSerializer(data=tickets)
            serializer.is_valid(raise_exception=True)

            if(len(myJql) != 0):
                myJql+=" OR "
            myJql += "issueKey in ("
            for ticket in tickets:
                myJql = myJql + ticket + ','
            myJql = myJql[:-1] +')'

        # Adding jql
        if 'jql' in data.keys():
            if(len(myJql) != 0):
                myJql+=" OR "
            myJql += data['jql']
            
        jql=myJql
        try:
            issues = jira.jql(jql)['issues']
            for issue in issues:
                ticket_response = {}
                key = issue['key']
                obj = Ticket.objects.filter(ticket_id=key)
                if obj.exists():
                    ticket_response['message'] = 'Ticket part of another pokerboard.'
                    ticket_response['status_code'] = status.HTTP_400_BAD_REQUEST
                else:
                    ticket_response['estimate'] = issue['fields']['customfield_10016']
                    ticket_response['status_code'] = status.HTTP_200_OK
                ticket_response['key'] = key
                ticket_responses.append(ticket_response)
        except requests.exceptions.RequestException as e:
            raise serializers.ValidationError("Invalid Query")
        return ticket_responses

    def create(self, validated_data):
        count = 0
        new_pokerboard = {key: val for key, val in self.data.items() if key not in [
            'sprint_id', 'tickets', 'jql']}
        ticket_responses = new_pokerboard.pop('ticket_responses')

        valid_tickets = 0
        for ticket_response in ticket_responses:
            valid_tickets += ticket_response['status_code'] == 200

        if valid_tickets == 0:
            raise serializers.ValidationError('Invalid tickets!')

        pokerboard = Pokerboard.objects.create(**new_pokerboard)

        for ticket_response in ticket_responses:
            if ticket_response['status_code'] != 200:
                continue
            new_ticket_data = {}
            new_ticket_data['pokerboard'] = pokerboard
            new_ticket_data['ticket_id'] = ticket_response['key']
            new_ticket_data['order'] = count
            Ticket.objects.create(**new_ticket_data)
            count += 1
        return pokerboard


