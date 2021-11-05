import requests

from rest_framework import serializers, status


from pokerboard.models import Pokerboard, PokerboardUserGroup, Ticket

from pokerplanner import settings

from user.models import User


class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer for tickets stored in database.
    Sending response, update tickets etc.
    """

    class Meta:
        model = Ticket
        fields = ['session', 'ticket_id', 'order', 'estimation_date', 'status']


class TicketsSerializer(serializers.ListSerializer):
    """
    Serializer to validate array of jira-id provided by user.
    Example - ['MP-1', 'MP-2']
    """
    child = serializers.CharField()


class PokerboardUserGroupSerializer(serializers.ModelSerializer):
    """
    Pokerboard user group serializer for adding new user in a pokerboard 
    """

    class Meta:
        model = PokerboardUserGroup
        fields = ['id', 'user', 'group', 'role', 'pokerboard']


class PokerboardMembersSerializer(serializers.ModelSerializer):
    """
    Pokerboard members serializer
    """
    role = serializers.CharField(source='get_role_display')

    class Meta:
        model = PokerboardUserGroup
        fields = ['pokerboard', 'user', 'role']
        extra_kwargs = {
            'pokerboard': {'read_only': True},
            'user': {'read_only': True},
            'group': {'read_only': True}
        }


class PokerboardGroupSerializer(serializers.ModelSerializer):
    """
    Pokerboard Group Serializer
    """

    class Meta:
        model = PokerboardUserGroup
        fields = ['group']


class PokerboardSerializer(serializers.ModelSerializer):
    """
    Pokerboard serializer
    """

    class Meta:
        model = Pokerboard
        fields = ['id', 'title', 'game_duration', 'description', 'manager']


class PokerBoardCreationSerializer(serializers.ModelSerializer):
    """
    Serializer to create pokerboard.
    """
    manager = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    sprint_id = serializers.CharField(required=False, write_only=True)
    tickets = TicketsSerializer(required=False, write_only=True)
    jql = serializers.CharField(required=False, write_only=True)
    ticket_responses = serializers.SerializerMethodField()

    class Meta:
        model = Pokerboard
        fields = ['id', 'manager', 'ticket_responses', 'title', 
                                'description', 'game_duration' ]

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

            if len(myJql) != 0:
                myJql += " OR "
            myJql += "issueKey in ("
            for ticket in tickets:
                myJql = myJql + ticket + ','
            myJql = myJql[:-1] + ')'

        # Adding jql
        if 'jql' in data.keys():
            if len(myJql) != 0:
                myJql += " OR "
            myJql += data['jql']

        jql = myJql
        try:
            if len(jql) == 0:
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
        """
        Imported tickets from JIRA and created pokerboard only if 
        atleast one valid ticket was found.
        """
        new_pokerboard = {key: val for key, val in validated_data.items() if key not in [
            'sprint_id', 'tickets', 'jql']}
        ticket_responses = self.data['ticket_responses']

        valid_tickets = 0
        for ticket_response in ticket_responses:
            valid_tickets += ticket_response['status_code'] == status.HTTP_200_OK

        if valid_tickets == 0:
            raise serializers.ValidationError('Invalid tickets!')

        pokerboard = Pokerboard.objects.create(**new_pokerboard)
        
        ticket_responses = [
            (
                ticket_response
            ) for ticket_response in ticket_responses if ticket_response['status_code'] == 200
        ]

        Ticket.objects.bulk_create(
            [
                Ticket(
                    pokerboard=pokerboard, ticket_id=ticket_response['key'], order=ind
                ) for ind, ticket_response in enumerate(ticket_responses)
            ]
        )
        return pokerboard
