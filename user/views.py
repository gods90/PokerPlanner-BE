from rest_framework import generics

from user.models import User
from user.serializer.serializers import UserSerializer


class UserViewSet(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    """
    User View for Performing CRUD operations.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


