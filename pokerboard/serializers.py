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
        fields = ['id','manager','title','description','configuration','status','ticket']


class PokerBoardCreationSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField()
    configuration = serializers.IntegerField(required=False, allow_null=True)

class TicketUpdateSerializer(serializers.Serializer):
    pokerboard = serializers.PrimaryKeyRelatedField(queryset=Pokerboard.objects.all())
    ticket_id = serializers.CharField()
    order = serializers.IntegerField()

