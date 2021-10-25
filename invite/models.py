from django.db import models

from pokerboard.models import Pokerboard
from  pokerboard import constants

from group.models import Group

from user.models import User

# Create your models here.

class Invite(models.Model):
    """
    Model to store invites
    """
    pokerboard = models.ForeignKey(
        Pokerboard, on_delete=models.CASCADE, help_text='Pokerboard of which invite has been sent.')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text='User which is invited.')
    user_role = models.IntegerField(
        choices=constants.PLAYER,
        default=constants.PLAYER,
        help_text='Default user role is player.',
    )
    status = models.IntegerField(choices=constants.INVITE_STATUS, default=constants.PENDING, help_text='Default status of the invite.')
    group = models.ForeignKey(
        Group, null=True, on_delete=models.CASCADE, help_text='Group which is invited.'
    )

    def __str__(self):
        if self.group != None:
            return f'Invitee: {self.user} -> Pokerboard: {self.pokerboard} -> Group: {self.group}'
        else:
            return f'Invitee: {self.user} -> Pokerboard: {self.pokerboard}'
