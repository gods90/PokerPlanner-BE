from rest_framework.permissions import BasePermission

from group.models import Group


class CustomPermissions(BasePermission):

    def has_permission(self, request, view):
        group_id = view.kwargs['pk']
        group = Group.objects.get(id=group_id)        
        if request.method in ['PATCH','DELETE']:
            return request.user==group.created_by
        return super().has_permission(request, view)