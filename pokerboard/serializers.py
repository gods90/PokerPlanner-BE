from django.db.models import fields
from rest_framework import serializers

from pokerboard.models import Pokerboard,Ticket
from user.serializers import UserSerializer
    

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['pokerboard','ticket_id','order','estimation_date','status']

class PokerBoardSerializer(serializers.ModelSerializer):
    manager = UserSerializer()
    ticket = TicketSerializer(source='ticket_set',many=True)
    class Meta:
        model = Pokerboard
        fields = ['id', 'manager', 'title', 'description', 'configuration', 'status', 'ticket']


class PokerBoardCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pokerboard
        fields = ['title','description','configuration']

class SprintSerializer(serializers.Serializer):
    sprint_id = serializers.CharField()

class TicketsSerializer(serializers.ListSerializer):
    child = serializers.CharField()


    