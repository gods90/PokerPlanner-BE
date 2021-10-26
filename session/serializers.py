from rest_framework import serializers
from rest_framework import status
import pokerboard

from session.models import Session, Ticket
from pokerboard.models import Pokerboard
from pokerplanner import settings

import requests


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['session', 'ticket_id', 'order', 'estimation_date', 'status']


class TicketsSerializer(serializers.ListSerializer):
    child = serializers.CharField()


class SessionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Session
        fields = '__all__'
        extra_kwargs = {
            'status': {'read_only': True}
        }


class SessionCreateSerializer(serializers.ModelSerializer):
    
    pokerboard = serializers.PrimaryKeyRelatedField(queryset=Pokerboard.objects.all())
    sprint_id = serializers.CharField(required=False,write_only=True)
    tickets = TicketsSerializer(required=False,write_only=True)
    jql = serializers.CharField(required=False,write_only=True)
    ticket_responses = serializers.SerializerMethodField()
    
    class Meta:
        model = Session
        fields = ['title', 'tickets', 'pokerboard', 'sprint_id', 'ticket_responses', 'jql']
    
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
            if(len(jql)==0):
                raise requests.exceptions.RequestException
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
        print(validated_data)
        count = 0
        new_session = {key: val for key, val in self.data.items() if key not in [
            'sprint_id', 'tickets', 'jql']}
        ticket_responses = new_session.pop('ticket_responses')

        valid_tickets = 0
        for ticket_response in ticket_responses:
            valid_tickets += ticket_response['status_code'] == 200

        if valid_tickets == 0:
            raise serializers.ValidationError('Invalid tickets!')
            
        pokerboard = Pokerboard.objects.get(id=new_session['pokerboard'])
        new_session['pokerboard']=pokerboard
        session = Session.objects.create(**new_session)

        for ticket_response in ticket_responses:
            if ticket_response['status_code'] != 200:
                continue
            new_ticket_data = {}
            new_ticket_data['session'] = session
            new_ticket_data['ticket_id'] = ticket_response['key']
            new_ticket_data['order'] = count
            Ticket.objects.create(**new_ticket_data)
            count += 1
        return session
