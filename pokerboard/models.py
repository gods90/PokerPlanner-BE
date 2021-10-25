from django.db import models

from group.models import Group
from user.models import User
from pokerboard import constants


class Pokerboard(models.Model):
    """ Model to store Pokerboard settings."""
    SERIES = 1
    EVEN = 2
    ODD = 3
    FIBONACCI = 4
    ESTIMATION_CHOICES = (
        (SERIES, 'Series'),
        (EVEN, 'Even'),
        (ODD, 'Odd'),
        (FIBONACCI, 'Fibonacci'),
    )

    CREATED = 1
    STARTED = 2
    ENDED = 3
    STATUS_CHOICES = (
        (CREATED, 'Created'),
        (STARTED, 'Started'),
        (ENDED, 'Ended')
    )
    manager = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text='Owner of pokerboard.')
    title = models.CharField(max_length=50, help_text='Name of Pokerboard.')
    description = models.CharField(
        max_length=100, help_text='Description of Pokerboard.')
    configuration = models.IntegerField(
        choices=ESTIMATION_CHOICES, default=SERIES, help_text='Estimation type.')
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICES, default=CREATED, help_text='Default pokerboard status is created.')

    def __str__(self) -> str:
        return self.title


class PokerboardUserGroup(models.Model):
    """
    Model to store users/groups of pokerboard.
    """
    pokerboard = models.ForeignKey(Pokerboard, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    role = models.IntegerField(
        choices=constants.ROLE_CHOICES,
        default=constants.PLAYER,
        help_text='Default user role is player.',
    )

    def __str__(self):
        if self.user:
            return f'{self.pokerboard} -> {self.user}'
        return f'{self.pokerboard} -> {self.group}'


class Invite(models.Model):
    """
    Model to store invites
    """
    pokerboard = models.ForeignKey(
        Pokerboard, on_delete=models.CASCADE, help_text='Pokerboard of which invite has been sent.')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text='User which is invited.')
    user_role = models.IntegerField(
        choices=constants.ROLE_CHOICES,
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
