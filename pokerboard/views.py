from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db.models.query_utils import Q

from invite.models import Invite
import pokerboard
from pokerboard.models import Pokerboard, PokerboardUserGroup
from pokerboard.permissions import CustomPermissions
from pokerboard.serializers import  PokerBoardCreationSerializer, PokerboardUserGroupSerializer, PokerboardMembersSerializer
from user.models import User
from pokerboard import constants

class PokerBoardViewSet(viewsets.ModelViewSet):
    """
    Pokerboard View for CRUD operations
    """
    # queryset = Pokerboard.objects.all()
    serializer_class = PokerBoardCreationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
            Create new pokerboard
            Required : Token in header, Title, Description
            Optional : Configuration
        """
        serializer = self.get_serializer(
            data={**request.data, 'manager': request.user.id})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


    @action(detail=True, methods=['delete', 'patch','get'], permission_classes=[IsAuthenticated, CustomPermissions])
    def members(self, request, pk=None):
        """
        Method to remove/patch user from pokerboard
        Route: /pokerboard/{pk}/members/ 
        Method : delete - Remove user/group
                 patch  - Change user role
        """
        pokerboard_id = self.kwargs['pk']
        serializer = PokerboardMembersSerializer(data={**request.data, 'pokerboard_id': pokerboard_id}, context={
            'method': request.method})

        serializer.is_valid(raise_exception=True)

        pokerboard_users = []

        if 'email' in request.data.keys():
            user = User.objects.get(email=serializer.validated_data['email'])
            pokerboard_users.append(user)
        if 'group_id' in request.data.keys():
            pokerboard_users = PokerboardUserGroup.objects.filter(
                pokerboard_id=pokerboard_id, group_id=request.data['group_id'])

        if request.method == 'DELETE':
            for pokerboard_user in pokerboard_users:
                invite = Invite.objects.get(
                    user_id=pokerboard_user.id, pokerboard_id=pokerboard_id)
                pokerboard_user.delete()
                invite.status = constants.DECLINED
                invite.save()
            return Response(data={'msg': 'Successfully removed from pokerboard'}, status=status.HTTP_200_OK)

        if request.method == 'PATCH':
            pokerboard_user = PokerboardUserGroup.objects.get(
                user_id=pokerboard_users[0].user_id, pokerboard_id=pokerboard_id)
            pokerboard_user.role = serializer.validated_data['role']
            pokerboard_user.save()
            serializer = PokerboardUserGroupSerializer(
                instance=pokerboard_user)
            return Response(status=status.HTTP_200_OK, data=serializer.data)

        if request.method == 'GET':
            pokerboard_member = PokerboardUserGroup.objects.filter(pokerboard_id=pokerboard_id)
            serializer = PokerboardUserGroupSerializer(pokerboard_member, many=True)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
            
    def get_queryset(self):
        user = Pokerboard.objects.filter(Q(manager=self.request.user) | 
                                         Q(invite__user=self.request.user,invite__status=constants.ACCEPTED)).distinct()
        return user