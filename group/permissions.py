from rest_framework.permissions import BasePermission

from group.models import Group


class CustomPermissions(BasePermission):

    def has_permission(self, request, view):
        if request.method in ['PATCH', 'DELETE']:
            group_id = view.kwargs['pk']
            try:
                group = Group.objects.get(id=group_id)
            except:
                return True
            return request.user == group.created_by
        return super().has_permission(request, view)
