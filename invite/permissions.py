from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission
from pokerboard.models import Pokerboard


class PokerboardInviteCustomPermissions(BasePermission):
    """
    Permission so that only manager can send invites to join pokerboard.
    """
    def has_permission(self, request, view):
        if request.method in ['POST']:
            pokerboard = Pokerboard.objects.select_related('manager').filter(id=view.kwargs['pokerboard_id'])
            if pokerboard.exists():
                return request.user == pokerboard.first().manager
            else:
                raise NotFound('Invalid pokerboard!')
        return True
