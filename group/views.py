from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from group.models import Group
from group.permissions import GroupCustomPermissions
from group.serializers import (GroupMemberDeleteSerializer,
                                          GroupSerializer,
                                          GroupUpdateSerializer)
from user.models import User


class GroupViewSet(viewsets.ModelViewSet):
    """
    Group View for Performing CRUD operations.
    """
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated, GroupCustomPermissions]

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method in ['PATCH']:
            return GroupUpdateSerializer
        return GroupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data={**request.data, 'created_by': request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        return Group.objects.filter(users__in=[self.request.user])

    @action(
        detail=True, methods=['delete'], permission_classes=[IsAuthenticated, GroupCustomPermissions]
    )
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
        group = get_object_or_404(Group, id=group_id)
        context = {
            "group": group
        }
        email = self.request.query_params.get('email')
        serializer = GroupMemberDeleteSerializer(
            data={"email": email}, context=context
        )
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=email)
        group.users.remove(user)
        return Response(data={'msg': 'User removed from the group.'})
