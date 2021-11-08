from rest_framework.permissions import BasePermission
from invite.serializer import PokerboardCheckInviteCreate


class PokerboardInviteCustomPermissions(BasePermission):
    """
    Permission so that only manager can send invites to join pokerboard.
    """
    def has_permission(self, request, view):
        serializer = PokerboardCheckInviteCreate(data=view.request.data)
        serializer.is_valid(raise_exception=True)
        return request.user == serializer.validated_data['pokerboard'].manager
