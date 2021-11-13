from rest_framework import mixins, status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from group.models import Group
from group.permissions import (GroupCustomPermissions,
                               GroupRemoveMemberCustomPermissions)
from group.serializers import (GroupFindSerializer,
                               GroupMemberDeleteSerializer,
                               GroupSerializer,
                               GroupUpdateSerializer)


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


class GroupMemberDeleteViewSet(viewsets.GenericViewSet, mixins.DestroyModelMixin):
    """
    View to remove user from a group.
    """
    permission_classes = [IsAuthenticated, GroupRemoveMemberCustomPermissions]

    def get_queryset(self):
        group = get_object_or_404(Group, id=self.kwargs['group_id'])
        return group.users.all()

    def destroy(self, request, *args, **kwargs):
        group = Group.objects.select_related('created_by').get(id=self.kwargs['group_id'])
        user = self.get_object()
        context = {
            'group': group,
        }
        serializer = GroupMemberDeleteSerializer(
            data={"user": user.id}, context=context
        )
        serializer.is_valid(raise_exception=True)
        group.users.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GroupFindViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """
    View to find group by name
    """
    queryset = Group.objects.all()
    serializer_class = GroupFindSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.GET.get('search', '')
        return Group.objects.filter(name__startswith=query)
