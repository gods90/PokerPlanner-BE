from django.db.models.query_utils import Q

from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from invite.models import Invite

from pokerboard import constants
from pokerboard.models import Pokerboard, PokerboardUserGroup
from pokerboard.serializers import (PokerBoardCreationSerializer,
                                    PokerboardMembersSerializer, 
                                    PokerboardSerializer, PokerboardGroupSerializer)


class PokerBoardViewSet(viewsets.ModelViewSet):
    """
    Pokerboard View for CRUD operations
    """
    serializer_class = PokerBoardCreationSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return super().get_serializer_class()
        return PokerboardSerializer

    def get_queryset(self):
        user = Pokerboard.objects.filter(Q(manager=self.request.user) |
                                         Q(invite__user=self.request.user,
                                          invite__status=constants.ACCEPTED)).distinct()
        return user

    def create(self, request, *args, **kwargs):
        """
            Create new pokerboard
            Required : Token in header, Title, Description
            Optional : Configuration
        """
        request.data['manager'] = request.user.id
        return super().create(request, *args, **kwargs)


class PokerboardMemberViewSet(viewsets.ModelViewSet):
    """
    Pokerboard Member view to delete member from pokerboard,get pokerboard members 
    and change pokerboard member role.
    """
    queryset = PokerboardUserGroup.objects.all()
    serializer_class = PokerboardMembersSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'delete', 'get']

    def list(self, request, *args, **kwargs):
        pokerboard_id = self.kwargs['pokerboard_id']
        pokerboard_member = PokerboardUserGroup.objects.filter(
            pokerboard_id=pokerboard_id)
        serializer = PokerboardMembersSerializer(pokerboard_member, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def perform_destroy(self, instance):
        invite = Invite.objects.get(
            user_id=instance.user.id, pokerboard_id=instance.pokerboard.id
        )
        invite.status = constants.DECLINED
        invite.save()
        instance.delete()


class PokerboardGroupViewSet(viewsets.ModelViewSet):
    """
    Pokerboard Group view to delete group from pokerboard,
    change pokerboard group role.
    """
    queryset = PokerboardUserGroup.objects.all()
    serializer_class = PokerboardGroupSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch', 'delete', 'get']

    def get_queryset(self):
        pokerboard_id = self.kwargs['pokerboard_id']
        if self.action in ['destroy', 'update']:
            return PokerboardUserGroup.objects.filter(
                pokerboard_id=pokerboard_id, group_id=self.kwargs['pk']
            )
        return PokerboardUserGroup.objects.filter(
            group__isnull=False, pokerboard_id=pokerboard_id
        ).distinct('group')

    def destroy(self, request, *args, **kwargs):
        pokerboard_id = self.kwargs['pokerboard_id']
        group_id = self.kwargs['pk']
        pokerboard_members = self.get_queryset()
        if len(pokerboard_members) == 0:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        invites = Invite.objects.filter(
            pokerboard_id=pokerboard_id, group_id=group_id)
        invites.all().update(status=constants.DECLINED)
        pokerboard_members.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        pokerboard_members = self.get_queryset()
        serializer = PokerboardMembersSerializer(
            pokerboard_members, data=request.data, partial=partial, many=True)
        serializer.is_valid(raise_exception=True)
        pokerboard_members.all().update(user_role=request.data['user_role'])
        return Response(serializer.data)
