from django.db.models.aggregates import Max

from rest_framework import serializers, status

from pokerplanner import settings

from pokerboard.models import Pokerboard, PokerboardUserGroup, Ticket
from pokerboard import constants
from pokerboard.utils import ticket_responses

from user.models import User


class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer for tickets stored in database.
    Sending response, update tickets etc.
    """

    class Meta:
        model = Ticket
        fields = ['pokerboard_id', 'ticket_id', 'order', 'estimation_date', 'status']


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
    role = serializers.CharField(read_only=True, source='get_role_display')
    name = serializers.CharField(read_only=True, source='user.full_name')
    email = serializers.CharField(read_only=True, source='user')
    manager = serializers.CharField(read_only=True, source='user.getId')

    class Meta:
        model = PokerboardUserGroup
        fields = ['id', 'pokerboard', 'user', 'role', 'manager', 'name', 'email', 'group']
        extra_kwargs = {
            'pokerboard': {'read_only': True},
            'user': {'read_only': True},
            'group': {'read_only': True}
        }


class PokerboardGroupSerializer(serializers.Serializer):
    """
    Pokerboard Group Serializer
    """
    group = serializers.PrimaryKeyRelatedField(queryset=PokerboardUserGroup.objects.all())
    group_name = serializers.CharField(read_only=True, source='group')
    creator_email = serializers.CharField(read_only=True, source='group.created_by')

class PokerboardSerializer(serializers.ModelSerializer):
    """
    Pokerboard serializer
    """
    role = serializers.SerializerMethodField()
    manager_email = serializers.CharField(source='manager')

    class Meta:
        model = Pokerboard
        fields = ['id', 'title', 'game_duration', 'description', 'manager', 'estimation_type', 'role', 'manager_email']

    def get_role(self, instance):
        user = self._kwargs['context']['request'].user
        if user.id == instance.manager_id:
            return 'MANAGER'
        role = PokerboardUserGroup.objects.get(pokerboard_id=instance.id, user_id=user.id).role
        return constants.ROLE_CHOICES[role][1]

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
        fields = [
            'id', 'manager', 'ticket_responses', 'title', 'description', 'game_duration', 'jql', 'tickets', 'sprint_id'
        ]

    def get_ticket_responses(self,instance):
        return ticket_responses(instance)
        
    def create(self, validated_data):
        """
        Imported tickets from JIRA and created pokerboard only if 
        atleast one valid ticket was found.
        """
        validated_data.pop('sprint_id', None)
        validated_data.pop('tickets', None)
        validated_data.pop('jql', None)
        ticket_responses = self.data['ticket_responses']
        new_pokerboard = {key: val for key, val in self.data.items() if key not in [
            'sprint_id', 'tickets', 'jql']}
        ticket_responses = new_pokerboard.pop('ticket_responses')
        
        valid_tickets = 0
        for ticket_response in ticket_responses:
            valid_tickets += ticket_response['status_code'] == status.HTTP_200_OK

        if valid_tickets == 0:
            raise serializers.ValidationError('Invalid tickets!')

        manager = User.objects.get(id=new_pokerboard["manager"])
        new_pokerboard["manager"] = manager

        ticket_responses = [
            (
                ticket_response
            ) for ticket_response in ticket_responses if ticket_response['status_code'] == 200
        ]

        if len(ticket_responses) == 0:
            raise serializers.ValidationError('Invalid tickets!')

        pokerboard = Pokerboard.objects.create(**validated_data)
        
        Ticket.objects.bulk_create(
            [
                Ticket(
                    pokerboard=pokerboard, ticket_id=ticket_response['key'], order=ind
                ) for ind, ticket_response in enumerate(ticket_responses)
            ]
        )
        return pokerboard


class PokerboardTicketAddSerializer(serializers.Serializer):
    sprint_id = serializers.CharField(required=False, write_only=True)
    tickets = TicketsSerializer(required=False, write_only=True)
    jql = serializers.CharField(required=False, write_only=True)
    ticket_responses = serializers.SerializerMethodField()
    pokerboard = serializers.PrimaryKeyRelatedField(queryset=Pokerboard.objects.all())
    
    class Meta:
        fields = ['sprint_id', 'tickets', 'jql', 'ticket_responses','pokerboard']

    def get_ticket_responses(self,instance):
        return ticket_responses(instance)
    
    def create(self, validated_data):
        ticket_responses = self.data['ticket_responses']
        pokerboard = validated_data['pokerboard']
        ticket_responses = [
            (
                ticket_response
            ) for ticket_response in ticket_responses if ticket_response['status_code'] == 200
        ]

        if len(ticket_responses) == 0:
            raise serializers.ValidationError('Invalid Query')
        
        count = Ticket.objects.filter(pokerboard_id=pokerboard.id).aggregate(Max('order'))
        Ticket.objects.bulk_create(
            [
                Ticket(
                    pokerboard=pokerboard, ticket_id=ticket_response['key'], order=count['order__max']+ind
                ) for ind, ticket_response in enumerate(ticket_responses)
            ]
        )
        return validated_data


class PokerboardUserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer to display pokerboard details on user profile
    """

    class Meta:
        model = Pokerboard
        fields = ['id', 'title']
