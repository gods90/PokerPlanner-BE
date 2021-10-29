from django.db import models

from common.models import Timestamp
from group.models import Group
from pokerboard import constants
from pokerboard.models import Pokerboard
from user.models import User


class Invite(Timestamp):
    """
    Model to store invites
    """
    pokerboard = models.ForeignKey(
        Pokerboard, on_delete=models.CASCADE, help_text='Pokerboard of which invite has been sent.',
        related_name="invite"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text='User which is invited.'
    )
    user_role = models.IntegerField(
        choices=constants.ROLE_CHOICES,
        default=constants.PLAYER,
        help_text='Default user role is player.',
    )
    status = models.IntegerField(
        choices=constants.INVITE_STATUS, default=constants.PENDING,
        help_text='Default status of the invite.'
    )
    group = models.ForeignKey(
        Group, null=True, on_delete=models.CASCADE, help_text='Group which is invited.'
    )

    def __str__(self):
        if self.group != None:
            return f'Invitee: {self.user} -> Pokerboard: {self.pokerboard} -> Group: {self.group}'
        else:
            return f'Invitee: {self.user} -> Pokerboard: {self.pokerboard}'
