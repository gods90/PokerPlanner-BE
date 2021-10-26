from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from invite.models import Invite
from invite.serializer import InviteCreateSerializer, InviteSerializer
from pokerboard import constants
from pokerboard.serializers import PokerboardUserGroupSerializer


class InviteViewSet(viewsets.ModelViewSet):
    """
    Invite View for CRUD operations
    """
    queryset = Invite.objects.all()
    serializer_class = InviteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Invite.objects.filter(user_id=self.request.user.id, status=constants.PENDING)


    def get_serializer_class(self):
        if self.request.method == 'POST':
            return InviteCreateSerializer
        return super().get_serializer_class()
    
    def create(self, request, *args, **kwargs):
        serializer = InviteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pokerboard = serializer.validated_data['pokerboard']
        if pokerboard.manager != request.user:
            raise PermissionDenied()
        return super().create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        invite = self.get_object()
        pokerboard_user_data = {
            'user': request.user.id,
            'group': invite.group_id,
            'pokerboard': invite.pokerboard_id,
            'role': invite.user_role
        }
        serializer = PokerboardUserGroupSerializer(
            data=pokerboard_user_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        invite.status = constants.ACCEPTED
        invite.save()
        serializer = InviteSerializer(instance=invite)
        return Response(data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        invite = self.get_object()
        if invite.status != constants.PENDING:
            return Response(data={'msg' : 'Already accepted'},status=status.HTTP_400_BAD_REQUEST) 
        invite.status = constants.DECLINED
        invite.save()
        serializer = InviteSerializer(instance=invite)
        return Response(data=serializer.data)
    