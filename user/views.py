from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken

from user.models import User
from user.serializers import (ChangePasswordSerializer,
                                         UserSerializer)


class UserViewSet(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    """
    User View for Performing CRUD operations.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    """
    View to change user password
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user


class LoginView(ObtainAuthToken):
    """
    Login view to send token and id of the user.
    """
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        response.data['user_id'] = token.user_id 
        return response


class LogoutView(generics.DestroyAPIView):
    """
    Logout view to delete token of the user.
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        token = self.request.auth
        return token
