from django.db import models

from pokerboard.models import Pokerboard
from user.models import User


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
    title = models.CharField(max_length=100,help_text='Title of the session.')
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=ONGOING,
        help_text="Session ongoing or ended",
    )

    def __str__(self):
        return f"{self.title} -> {self.pokerboard}"


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

    session = models.ForeignKey('Session', on_delete=models.CASCADE, help_text='Pokerboard to which ticket belongs.')
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
