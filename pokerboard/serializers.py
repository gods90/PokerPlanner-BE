from django.db.models import fields, manager
from rest_framework import serializers, status

from pokerboard.models import Pokerboard,Ticket
from user.serializers import UserSerializer

class PokerBoardSerializer(serializers.ModelSerializer):
    manager = UserSerializer()
    class Meta:
        model = Pokerboard
        fields = ['manager','title','description','configuration','status']
    

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['pokerboard','ticket_id','order','estimation_date','status']


class PokerBoardCreationSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField()
    configuration = serializers.IntegerField(required=False, allow_null=True)

