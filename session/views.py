from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from session.models import Session
from session.serializers import SessionSerializer, SessionCreateSerializer


class SessionViewSet(viewsets.ModelViewSet):
    """
    Session View for CRUD operations
    """
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if(self.request.method == 'POST'):
            return SessionCreateSerializer
        return super().get_serializer_class()

