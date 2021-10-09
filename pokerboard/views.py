from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from pokerboard.models import Pokerboard
from pokerboard.serializers import PokerBoardCreationSerializer, PokerBoardSerializer


class PokerBoardViewSet(viewsets.ModelViewSet):
    """
    Pokerboard View for CRUD operations
    """
    queryset = Pokerboard.objects.all()
    serializer_class = PokerBoardCreationSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PokerBoardCreationSerializer
        return PokerBoardSerializer

    def create(self, request, *args, **kwargs):
        """
        Create new pokerboard
        Required : Token in header, Title, Description
        Optional : Configuration
        """
        request.data['manager_id'] = request.user.id
        return super().create(request, *args, **kwargs)


