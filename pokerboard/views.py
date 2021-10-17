from rest_framework import serializers, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response

from pokerboard.models import Invite, Pokerboard, PokerboardUserGroup
from pokerboard.permissions import CustomPermissions
from pokerboard.serializers import InviteCreateSerializer, InviteSerializer, PokerBoardCreationSerializer, PokerBoardSerializer, PokerboardUserGroupSerializer, PokerboardUserSerializer

from user.models import User

from group.models import Group


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
        request.data['manager_id'] = request.user.id
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post', 'patch'], permission_classes=[IsAuthenticated, CustomPermissions])
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
        if request.method == 'POST':
            # TODO : Send mail for signup if doesnt exist
            users = []
            group_id = None

            serializer = InviteCreateSerializer(data=request.data, context={
                                                'pokerboard_id': pokerboard_id})
            serializer.is_valid(raise_exception=True)

            if 'email' in request.data.keys():
                user = User.objects.get(email=request.data['email'])
                users.append(user)
            elif 'group_id' in request.data.keys():
                group_id = request.data['group_id']
                group = Group.objects.get(id=group_id)
                users = group.users.all()

            for user in users:
                serializer = InviteSerializer(
                    data={**request.data, 'pokerboard': pokerboard_id, 'user': user.id, 'group': group_id})
                serializer.is_valid(raise_exception=True)
                serializer.save()
            return Response()

        if request.method == 'PATCH':
            user = request.user
            try:
                invite = Invite.objects.get(
                    user_id=user.id, pokerboard_id=pokerboard_id)
                invite.is_accepted = True
                invite.save()
            except Invite.DoesNotExist:
                raise serializers.ValidationError('User not invited!')
            return Response()

    @action(detail=True, methods=['delete', 'patch'])
    def user(self, request, pk=None):
        """
        Method to remove/patch user from pokerboard
        Route: /pokerboard/{pk}/user/ 
        Method : delete - Remove user
                patch  - Change user role
        """
        pokerboard_id = self.kwargs['pk']
        serializer = PokerboardUserSerializer(data={**request.data, 'pokerboard': pokerboard_id}, context={
                                              'method': request.method, 'pk': pokerboard_id, 'email': request.data['email']})
        serializer.is_valid(raise_exception=True)

        user = User.objects.get(email=serializer.validated_data['email'])
        pokerboard_user = PokerboardUserGroup.objects.get(
            pokerboard_id=pokerboard_id, user_id=user.id)

        if request.method == 'DELETE':
            pokerboard_user.delete()
            return Response(status=status.HTTP_200_OK)

        if request.method == 'PATCH':
            pokerboard_user.role = serializer.validated_data['role']
            pokerboard_user.save()
            serializer = PokerboardUserGroupSerializer(
                instance=pokerboard_user)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
