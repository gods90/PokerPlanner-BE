from rest_framework.permissions import BasePermission
from rest_framework.generics import get_object_or_404

from group.models import Group


class GroupCustomPermissions(BasePermission):
    """
    Permission class to allow only group admin to add members
    and delete group.
    """
    def has_permission(self, request, view):
        if request.method in ['PATCH', 'DELETE']:
            group = get_object_or_404(Group, pk=view.kwargs['pk'])
            return request.user == group.created_by
        return super().has_permission(request, view)
