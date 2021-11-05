from django.db import models

from pokerboard.models import Pokerboard, Ticket

from user.models import User

from common.models import Timestamp


class Session(Timestamp):
    """
    Model to store sessions
    """

    ONGOING = 0
    HASENDED = 1

    STATUS_CHOICES = (
        (ONGOING, "ongoing"),
        (HASENDED, "hasended"),
    )

    pokerboard = models.ForeignKey(Pokerboard, on_delete=models.CASCADE, related_name="session")
    title = models.CharField(max_length=100, help_text='Title of the session.')
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=ONGOING,
        help_text="Session ongoing or ended",
    )
    time_started_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.title} -> {self.pokerboard}"


class UserEstimate(Timestamp):
    """
    Model to store user estimates
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,help_text='User which has estimated the ticket.'
    )
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, help_text='Ticket to which estimate belongs.'
    )
    estimation_duration = models.DurationField(help_text='Duration for voting(in secs)')
    estimate = models.PositiveIntegerField(help_text='Value of estimate done by the user.')

    def __str__(self):
        return f"{self.ticket} -> {self.user} -> {self.estimate}"
