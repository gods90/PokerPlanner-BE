from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from session.models import Session
from session.serializers import SessionSerializer


class SessionViewSet(viewsets.ModelViewSet):
    """
    Session View for CRUD operations
    """
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]

    http_method_names = ['get','post']
    
    def get_object(self):
        """
        To get the active session of the pokerboard.
        """
        pokerboard_id = self.kwargs["pk"]
        active_session = get_object_or_404(Session, pokerboard_id=pokerboard_id,status=Session.ONGOING)
        return active_session
