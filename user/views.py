from rest_framework import generics, mixins, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from session.models import UserEstimate

from user.models import User
from user.serializers import (ChangePasswordSerializer, EstimateSerializer,
                                         UserSerializer)
from user.tasks import send_welcome_mail_task


class UserViewSet(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    """
    User View for Performing CRUD operations.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == "POST":
            return []
        return super().get_permissions()

    def get_object(self):
        return self.request.user
    
    def get_permissions(self):
        if self.request.method in ['POST']:
            return []
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        res = super().create(request, *args, **kwargs)
        if res.status_code == status.HTTP_201_CREATED:
            send_welcome_mail_task.delay(res.data['first_name'], res.data.get('last_name', ''), [res.data['email']])
        return res



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


class EstimateViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """
    View to get the estimate of a ticket done by user and actual estimate
    """
    serializer_class = EstimateSerializer

    def get_queryset(self):
        user = self.request.user
        return UserEstimate.objects.filter(user_id=user.id)
