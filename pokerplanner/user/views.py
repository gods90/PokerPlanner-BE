from pokerplanner.user.models import User
from rest_framework import viewsets
from pokerplanner.user.serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    """
    User View for Performing CRUD   
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
