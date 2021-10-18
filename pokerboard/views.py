from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response

from group.models import Group
from pokerboard.models import Invite, Pokerboard, PokerboardUserGroup
from pokerboard.permissions import CustomPermissions
from pokerboard.serializers import InviteCreateSerializer, InviteSerializer, PokerBoardCreationSerializer, PokerboardUserGroupSerializer, PokerboardMembersSerializer
from user.models import User


class PokerBoardViewSet(viewsets.ModelViewSet):
    """
    Pokerboard View for CRUD operations
    """
    queryset = Pokerboard.objects.all()
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

    @action(detail=True, methods=['post', 'patch', 'delete'], permission_classes=[IsAuthenticated, CustomPermissions])
    def invite(self, request, pk=None):
        """
        /pokerboard/108/invite/ - manager - create invite
                                - user - accept invite
        Method to invite user/group to pokerboard
        Route: /pokerboard/{pk}/invite/ 
        Method : post - Create invitation
                 patch - Accept invite
        params : 
            Required : Either email or group_id
            Optional : role - 0/1
        """
        pokerboard_id = self.kwargs['pk']
        context = {
            'pokerboard_id': pokerboard_id,
            'method': request.method
        }
        if request.method in ['POST', 'DELETE']:
            users = []
            group_id = None

            serializer = InviteCreateSerializer(
                data=request.data, context=context)
            serializer.is_valid(raise_exception=True)

            if 'email' in request.data.keys():
                user = User.objects.get(email=request.data['email'])
                users.append(user)
            elif 'group_id' in request.data.keys():
                group_id = request.data['group_id']
                group = Group.objects.get(id=group_id)
                users = group.users.all()

        if request.method == 'POST':
            # TODO : Send mail for signup if doesnt exist
            for user in users:
                serializer = InviteSerializer(
                    data={**request.data, 'pokerboard': pokerboard_id, 'user': user.id, 'group': group_id})
                serializer.is_valid(raise_exception=True)
                serializer.save()
            return Response({'msg': '{choice} successfully invited'.format(choice='Group' if group_id is not None else 'User')})

        if request.method == 'PATCH':
            user = request.user
            serializer = InviteCreateSerializer(
                data=request.data, context={**context, 'user': user})
            serializer.is_valid(raise_exception=True)
            invite = Invite.objects.get(
                user_id=user.id, pokerboard_id=pokerboard_id)

            pokerboard_user_data = {
                'user': user.id,
                'group': invite.group_id,
                'pokerboard': pokerboard_id,
                'role': invite.user_role
            }
            serializer = PokerboardUserGroupSerializer(
                data=pokerboard_user_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            invite.is_accepted = True
            invite.save()

            return Response(data={'msg': 'Welcome to the pokerboard!'})

        if request.method == 'DELETE':
            for user in users:
                invite = Invite.objects.get(
                    user_id=user.id, pokerboard_id=pokerboard_id)
                invite.delete()
            return Response(data={'msg': 'Invite successfully revoked.'})

    @action(detail=True, methods=['delete', 'patch'], permission_classes=[IsAuthenticated, CustomPermissions])
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
                    user_id=pokerboard_user.user_id, pokerboard_id=pokerboard_id)
                pokerboard_user.delete()
                invite.delete()
            return Response(data={'msg': 'Successfully removed from pokerboard'}, status=status.HTTP_200_OK)

        if request.method == 'PATCH':
            pokerboard_user = PokerboardUserGroup.objects.get(
                user_id=pokerboard_users[0].user_id, pokerboard_id=pokerboard_id)
            pokerboard_user.role = serializer.validated_data['role']
            pokerboard_user.save()
            serializer = PokerboardUserGroupSerializer(
                instance=pokerboard_user)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
