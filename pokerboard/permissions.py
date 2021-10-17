from rest_framework.permissions import BasePermission

from pokerboard.models import Pokerboard


class CustomPermissions(BasePermission):

    def has_permission(self, request, view):
        pokerboard_id = view.kwargs['pk']
        pokerboard = Pokerboard.objects.get(id=pokerboard_id)
        if request.method in ['POST','DELETE']:  # only manager can create/delete
            return request.user == pokerboard.manager
        return super().has_permission(request, view)
