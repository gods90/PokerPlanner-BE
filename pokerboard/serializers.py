import requests

from rest_framework import serializers, status
from group.models import Group

from pokerboard import constants
from pokerboard.models import Pokerboard, PokerboardUserGroup, Ticket
from pokerplanner import settings
from user.models import User


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['session', 'ticket_id', 'order', 'estimation_date', 'status']


class TicketsSerializer(serializers.ListSerializer):
    child = serializers.CharField()


class PokerboardUserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = PokerboardUserGroup
        fields = ['id', 'user', 'group', 'role', 'pokerboard']


class PokerboardMembersSerializer(serializers.ModelSerializer):
    """
    Pokerboard members serializer
    """
    class Meta:
        model = PokerboardUserGroup
        fields = "__all__"
        extra_kwargs = {
            'pokerboard': {'read_only': True},
            'user': {'read_only': True},
            'group': {'read_only': True}
        }

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["role"] = constants.ROLE_CHOICES[repr["role"]][1]
        return repr


class PokerboardGroupSerializer(serializers.ModelSerializer):
    """
    Pokerboard Group Serializer
    """
    class Meta:
        model = PokerboardUserGroup
        fields = ['group']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        group = Group.objects.get(id=rep['group'])
        rep['group'] =group.name
        rep['group_id'] = group.id
        return rep


class PokerboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pokerboard
        fields = ['id', 'title', 'game_duration', 'description', 'manager', 'estimation_type']


class PokerBoardCreationSerializer(serializers.ModelSerializer):
    manager = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all())
    sprint_id = serializers.CharField(required=False, write_only=True)
    tickets = TicketsSerializer(required=False, write_only=True)
    jql = serializers.CharField(required=False, write_only=True)
    ticket_responses = serializers.SerializerMethodField()

    class Meta:
        model = Pokerboard
        fields = '__all__'

    def get_ticket_responses(self, instance):
        jira = settings.JIRA
        data = dict(instance)
        ticket_responses = []

        myJql = ""
        # If sprint, then fetch all tickets in sprint and add
        if 'sprint_id' in data.keys():
            myJql = "Sprint = " + data['sprint_id']

        # Adding tickets
        if 'tickets' in data.keys():
            tickets = data['tickets']
            serializer = TicketsSerializer(data=tickets)
            serializer.is_valid(raise_exception=True)

            if(len(myJql) != 0):
                myJql += " OR "
            myJql += "issueKey in ("
            for ticket in tickets:
                myJql = myJql + ticket + ','
            myJql = myJql[:-1] + ')'

        # Adding jql
        if 'jql' in data.keys():
            if(len(myJql) != 0):
                myJql += " OR "
            myJql += data['jql']

        jql = myJql
        try:
            if(len(jql) == 0):
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
        count = 1
        new_pokerboard = {key: val for key, val in self.data.items() if key not in [
            'sprint_id', 'tickets', 'jql']}
        ticket_responses = new_pokerboard.pop('ticket_responses')

        valid_tickets = 0
        for ticket_response in ticket_responses:
            valid_tickets += ticket_response['status_code'] == 200

        if valid_tickets == 0:
            raise serializers.ValidationError('Invalid tickets!')

        manager = User.objects.get(id=new_pokerboard["manager"])
        new_pokerboard["manager"] = manager
        pokerboard = Pokerboard(**new_pokerboard)
        pokerboard.save()
        
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
