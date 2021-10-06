from rest_framework import viewsets

from pokerboard.models import Pokerboard,Ticket


class PokerBoardViewSet(viewsets.ModelViewSet):
    """
    Pokerboard View for CRUD operations
    """