from django.db import models

from common.models import Timestamp

from group.models import Group

from pokerboard import constants

from user.models import User


class Pokerboard(Timestamp):
    """
    Model to store Pokerboard settings.
    """
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

    manager = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text='Owner of pokerboard.'
    )
    title = models.CharField(
        max_length=50, help_text='Name of Pokerboard.'
    )
    description = models.CharField(
        max_length=100, help_text='Description of Pokerboard.'
    )
    estimation_type = models.IntegerField(
        choices=ESTIMATION_CHOICES, default=SERIES, help_text='Estimation type.'
    )
    game_duration = models.DurationField(
        null=False, help_text="Duration for game in pokerboard."
    )
    
    def __str__(self) -> str:
        return self.title


class Ticket(Timestamp):
    """
    Model to store ticket detail
    """
    ESTIMATED = 0
    NOTESTIMATED = 1

    STATUS_CHOICES = (
        (ESTIMATED, 'estimated'),
        (NOTESTIMATED, 'notestimated'),
    )

    pokerboard = models.ForeignKey(
        Pokerboard, on_delete=models.CASCADE, help_text='Pokerboard to which ticket belongs.'
    )
    ticket_id = models.CharField(
        unique=True, max_length=100, help_text='Ticket ID imported from JIRA.'
    )
    order = models.PositiveSmallIntegerField(help_text='Rank of ticket.')
    estimation_date = models.DateField(
        null=True, blank=True, help_text="Date on which ticket was estimated"
    )
    status = models.IntegerField(
        choices=constants.STATUS_CHOICES,
        default=constants.NOTESTIMATED,
        help_text='Default ticket status is not estimated.',
    )

    def __str__(self):
        return f'{self.ticket_id} -> {self.pokerboard}'


class PokerboardUserGroup(Timestamp):
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

    def __str__(self) -> str:
        if self.user:
            return f'{self.pokerboard} -> {self.user}'
        return f'{self.pokerboard} -> {self.group}'

