from rest_framework import generics, mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from pokerboard.serializers import InviteSerializer

from user.models import User
from user.serializer.serializers import UserSerializer, ChangePasswordSerializer

from pokerboard.models import Invite

class UserViewSet(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    """
    User View for Performing CRUD operations.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.UpdateAPIView):
    """
    View to change user password
    """
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        return self.request.user

class InviteViewSet(viewsets.GenericViewSet,mixins.ListModelMixin):
    """
    View to get user invites
    """
    queryset = Invite.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = InviteSerializer

    def get_queryset(self):
        return Invite.objects.filter(user_id=self.request.user.id,is_accepted=False)
