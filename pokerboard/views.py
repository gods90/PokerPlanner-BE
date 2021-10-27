from django import http
from django.db.models import query
from django.db.models.query_utils import Q

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from invite.models import Invite


from pokerboard import constants
from pokerboard.models import Pokerboard, PokerboardUserGroup
from pokerboard.permissions import CustomPermissions
from pokerboard.serializers import (PokerBoardCreationSerializer,
                                    PokerboardMembersSerializer, PokerboardSerializer)


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
                Q(invite__user=self.request.user,invite__status=constants.ACCEPTED)).distinct()
        return user
    
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

     
class PokerboardMemberViewSet(viewsets.ModelViewSet):
    """
    Pokerboard Member view to delete member from pokerboard,get pokerboard members 
    and change pokerboard member role.
    """
    queryset = PokerboardUserGroup.objects.all()
    serializer_class = PokerboardMembersSerializer
    permission_classes=[IsAuthenticated, CustomPermissions]
    http_method_names = ['patch','delete','get']
     

    def list(self, request, *args, **kwargs):
        pokerboard_id = self.kwargs['pokerboard_id']
        pokerboard_member = PokerboardUserGroup.objects.filter(pokerboard_id=pokerboard_id)
        serializer = PokerboardMembersSerializer(pokerboard_member, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
    
    def perform_destroy(self, instance):
        invite = Invite.objects.get(
                    user_id=instance.user.id, pokerboard_id=instance.pokerboard.id
            )
        invite.status = constants.DECLINED
        invite.save()
        instance.delete()
        
