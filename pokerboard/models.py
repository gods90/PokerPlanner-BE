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


class Ticket(models.Model):
    """
    Model to store ticket detail
    """
    NOTSTARTED = 0
    ONGOING = 0
    HASENDED = 1

    STATUS_CHOICES = (
        (NOTSTARTED, 'notstarted'),
        (ONGOING, 'ongoing'),
        (HASENDED, 'hasended'),
    )

    pokerboard = models.ForeignKey(
        Pokerboard, on_delete=models.CASCADE, help_text='Pokerboard to which ticket belongs.')
    ticket_id = models.CharField(
        unique=True,
        max_length=100, help_text='Ticket ID imported from JIRA.')
    order = models.PositiveSmallIntegerField(help_text='Rank of ticket.')
    estimation_date = models.DateField(
        null=True, blank=True, help_text="Date on which ticket was estimated")
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=NOTSTARTED,
        help_text='Default ticket status is not started.',
    )

    def __str__(self):
        return f'{self.ticket_id} -> {self.pokerboard}'


class UserEstimate(models.Model):
    """
    Model to store user estimates
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             help_text='User which has estimated the ticket.')
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, help_text='Ticket to which estimate belongs.')
    estimation_duration = models.DurationField(
        help_text='Duration for voting(in secs)')
    estimate = models.PositiveIntegerField(
        help_text='Value of estimate done by the user.')

    def __str__(self):
        return f"{self.ticket} -> {self.user} -> {self.estimate}"


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
        default=constants.ROLE_CHOICES[0],
        help_text='Default user role is player',
    )
    is_accepted = models.BooleanField(default=False)
    group = models.ForeignKey(
        Group, null=True, on_delete=models.CASCADE, help_text='Group which is invited.'
    )

    def __str__(self):
        if self.group != None:
            return f'Invitee: {self.user} -> Pokerboard: {self.pokerboard} -> Group: {self.group}'
        else:
            return f'Invitee: {self.user} -> Pokerboard: {self.pokerboard}'


class Session(models.Model):
    """
    Model to store sessions
    """

    ONGOING = 0
    HASENDED = 1

    STATUS_CHOICES = (
        (ONGOING, "ongoing"),
        (HASENDED, "hasended"),
    )

    pokerboard = models.ForeignKey(Pokerboard, on_delete=models.CASCADE)
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=ONGOING,
        help_text="Session ongoing or ended",
    )

    def __str__(self):
        return
