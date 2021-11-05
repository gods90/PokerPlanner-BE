from rest_framework.permissions import BasePermission
from rest_framework.generics import get_object_or_404

from pokerboard.models import Pokerboard


class PokerboardCustomPermissions(BasePermission):

    def has_permission(self, request, view):
        pokerboard_id = view.kwargs['pokerboard_id']
        pokerboard = get_object_or_404(Pokerboard, id=pokerboard_id)
        return request.user == pokerboard.manager
