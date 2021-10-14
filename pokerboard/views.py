from rest_framework import serializers, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from pokerboard.models import Pokerboard, PokerboardUserGroup
from pokerboard.serializers import PokerBoardCreationSerializer, PokerBoardSerializer, PokerboardUserGroupSerializer, PokerboardUserSerializer

from user.models import User


class PokerBoardViewSet(viewsets.ModelViewSet):
    """
    Pokerboard View for CRUD operations
    """
    queryset = Pokerboard.objects.all()
    serializer_class = PokerBoardCreationSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PokerBoardCreationSerializer
        if self.request.method == 'PATCH':
            return
        return PokerBoardSerializer

    def create(self, request, *args, **kwargs):
        """
        Create new pokerboard
        Required : Token in header, Title, Description
        Optional : Configuration
        """
        request.data['manager_id'] = request.user.id
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post', 'delete', 'patch'])
    def user(self, request, pk=None):
        """
        Method to add/remove user from pokerboard
        Route: /pokerboard/{pk}/user/ 
        Method : post - Add user
                delete - Remove user
                patch  - Change user role
        """
        pokerboard_id = self.kwargs['pk']
        request.data['pokerboard'] = pokerboard_id
        serializer = PokerboardUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.method == 'POST':
            user = User.objects.get(email=serializer.data['email'])
            request.data['user'] = user.id
            if PokerboardUserGroup.objects.filter(pokerboard_id=pokerboard_id, user_id=user.id).exists():
                raise serializers.ValidationError(
                    {'error': 'User already member of pokerboard!'})
            serializer = PokerboardUserGroupSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            pokerboard_user = PokerboardUserGroup.objects.create(
                **serializer.validated_data)
            serializer = PokerboardUserGroupSerializer(
                instance=pokerboard_user)
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)

        user = User.objects.get(email=serializer.validated_data['email'])
        pokerboard_user = PokerboardUserGroup.objects.filter(
            pokerboard_id=pokerboard_id, user_id=user.id)
        if not pokerboard_user.exists():
            raise serializers.ValidationError(
                {'error': 'User not a member of pokerboard!'})

        elif request.method == 'DELETE':
            pokerboard_user[0].delete()
            return Response(status=status.HTTP_200_OK)

        elif request.method == 'PATCH':
            pokerboard_user = PokerboardUserGroup.objects.get(
                pokerboard_id=pokerboard_id, user_id=user.id)
            if 'role' not in serializer.validated_data.keys():
                raise serializers.ValidationError('Invalid role')
            pokerboard_user.role = serializer.validated_data['role']
            pokerboard_user.save()
            serializer = PokerboardUserGroupSerializer(
                instance=pokerboard_user)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
