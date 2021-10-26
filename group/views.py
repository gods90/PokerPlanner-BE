from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from group.models import Group
from group.permissions import CustomPermissions
from group.serializer.serializers import (GroupDeleteSerializer,
                                          GroupSerializer,
                                          GroupUpdateSerializer)
from user.models import User


class GroupViewSet(viewsets.ModelViewSet):
    """
    Group View for Performing CRUD operations.
    """

    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated, CustomPermissions]

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method in ['PATCH']:
            return GroupUpdateSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data={**request.data, 'created_by': request.user.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        return Group.objects.filter(users=self.request.user)

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated, CustomPermissions])
    def removemembers(self, request, pk=None):
        """
        /group/108/removemembers/ - creator-can delete from group
        Method to delete user from group
        Route: /pokerboard/{pk}/removemembers/ 
        Method : delete - delete from group
        params : 
        Required : email
        """
        group_id = self.kwargs['pk']
        context = {
            "group_id": group_id
        }
        email = self.request.query_params.get('email')
        serializer = GroupDeleteSerializer(
            data={"email": email}, context=context)
        serializer.is_valid(raise_exception=True)
        group = Group.objects.get(id=group_id)
        user = User.objects.get(email=email)
        group.users.remove(user)
        return Response(data={'msg': 'User removed from the group.'})
