from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from pokerboard.models import Pokerboard,Ticket
from pokerboard.serializers import PokerBoardSerializer,PokerBoardCreationSerializer


class PokerBoardViewSet(viewsets.ModelViewSet):
    """
    Pokerboard View for CRUD operations
    """
    queryset = Pokerboard.objects.all()
    serializer_class = PokerBoardSerializer
    permission_classes = [IsAuthenticated]


    def create(self, request, *args, **kwargs):
        serializer = PokerBoardCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        manager = request.user
        pokerboard = Pokerboard.objects.create(manager=manager,**serializer.data)
        pokerboard.save()
        serializer = PokerBoardSerializer(instance=pokerboard)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
        

