from rest_framework import serializers, status
from pokerboard import constants

from pokerboard.models import Invite, Pokerboard, PokerboardUserGroup, Ticket

from user.models import User
from user.serializers import UserSerializer

from group.models import Group

from django.conf import settings

import requests


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['pokerboard', 'ticket_id',
                  'order', 'estimation_date', 'status']


class TicketsSerializer(serializers.ListSerializer):
    child = serializers.CharField()


class PokerboardUserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = PokerboardUserGroup
        fields = ['id', 'user', 'group', 'role', 'pokerboard']


class PokerboardUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(
        choices=constants.ROLE_CHOICES, required=False)
    

    def validate_email(self, attrs):
        pokerboard_id = self.context['pk']
        user = User.objects.filter(email=self.context['email'])
        pokerboard_user = PokerboardUserGroup.objects.filter(
                          pokerboard_id=pokerboard_id, user_id=user[0].id)

        if not user.exists():
            raise serializers.ValidationError('Invalid user!')
        if not pokerboard_user.exists():
            raise serializers.ValidationError('User not a member of pokerboard!')

        return attrs

class PokerBoardSerializer(serializers.ModelSerializer):
    manager = UserSerializer()
    ticket = TicketSerializer(source='ticket_set', many=True)

    class Meta:
        model = Pokerboard
        fields = ['id', 'manager', 'title', 'description',
                  'configuration', 'status', 'ticket']


class PokerBoardCreationSerializer(serializers.ModelSerializer):
    manager_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all())
    sprint_id = serializers.CharField(required=False)
    tickets = TicketsSerializer(required=False)
    ticket_responses = serializers.SerializerMethodField()

    class Meta:
        model = Pokerboard
        fields = ['manager_id', 'title', 'description',
                  'configuration', 'tickets', 'sprint_id', 'ticket_responses']

    def get_ticket_responses(self, instance):
        jira = settings.JIRA
        data = dict(instance)
        ticket_responses = []
        start = 0
        limit = 300
        # If sprint, then fetch all tickets in sprint and add
        if 'sprint_id' in data.keys():
            sprint_id = data['sprint_id']
            while True:
                try:
                    issues = jira.get_sprint_issues(
                        sprint_id, start*limit, limit)['issues']
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
                    raise serializers.ValidationError("Invalid string_id")
                start += 1
                if len(issues) < limit:
                    break

        # Adding tickets
        elif 'tickets' in data.keys():
            tickets = data['tickets']
            serializer = TicketsSerializer(data=tickets)
            serializer.is_valid(raise_exception=True)

            for ticket in tickets:
                ticket_response = {}
                try:
                    # Check if ticket is already part of another pokerboard
                    obj = Ticket.objects.filter(ticket_id=ticket)
                    if obj.exists():
                        ticket_response['message'] = 'Ticket part of another pokerboard.'
                        ticket_response['status_code'] = status.HTTP_400_BAD_REQUEST
                    else:
                        # Checking with JIRA
                        jira_response = jira.issue(key=ticket)['fields']
                        ticket_response['estimate'] = jira_response['customfield_10016']
                        ticket_response['status_code'] = status.HTTP_200_OK
                except requests.exceptions.RequestException as e:
                    ticket_response['message'] = str(e)
                    ticket_response['status_code'] = status.HTTP_404_NOT_FOUND

                ticket_response['key'] = ticket
                ticket_responses.append(ticket_response)
        return ticket_responses


    def create(self, validated_data):
        count = 0
        new_pokerboard = {key: val for key, val in self.data.items() if key not in [
            'sprint_id', 'tickets']}
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


class InviteSerializer(serializers.ModelSerializer):
    class Meta :
        model = Invite
        fields = '__all__'
        extra_kwargs = {
            'is_accepted': {'read_only': True}
        }


class InviteCreateSerializer(serializers.Serializer):
    group_id = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(),required=False)
    email = serializers.EmailField(required=False)
    user_role = serializers.ChoiceField(choices=constants.ROLE_CHOICES,required=False)

    def validate(self, attrs):
        pokerboard_id = self.context['pokerboard_id']
        users = []

        if 'group_id' in attrs.keys():
            group = attrs['group_id']
            users = group.users.all()
        elif 'email' in attrs.keys():
            try:
                user = User.objects.get(email=attrs['email'])
                users.append(user)
            except User.DoesNotExist as e:
                #TODO Send mail to user
                raise serializers.ValidationError(e)
        else:
            raise serializers.ValidationError('Invalid group/email!')

        for user in users:
            invite = Invite.objects.filter(user=user.id,pokerboard=pokerboard_id)
            if invite.exists():
                if invite[0].is_accepted:
                    raise serializers.ValidationError('Already part of pokerboard') 
                else:   
                    raise serializers.ValidationError('Invite already sent!')
    
        return super().validate(attrs)

