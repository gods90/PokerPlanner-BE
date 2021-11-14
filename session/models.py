from django.db import models

from common.models import Timestamp
from pokerboard import (
    models as pokerboard_models,
    constants as pokerboard_constants
)
from user.models import User


class Session(Timestamp):
    """
    Model to store sessions
    """
    pokerboard = models.ForeignKey(pokerboard_models.Pokerboard, on_delete=models.CASCADE, related_name="session")
    title = models.CharField(max_length=100, help_text='Title of the session.')
    status = models.IntegerField(
        choices=pokerboard_constants.SESSION_STATUS_CHOICES,
        default=pokerboard_constants.ONGOING,
        help_text="Session ongoing or ended",
    )
    time_started_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.title} -> {self.pokerboard}"    
    
    def started_at(self):
        if self.time_started_at is None:
            return 'NOT STARTED YET'
        return self.time_started_at.strftime(" %H:%M:%S %B %d, %Y")


class UserEstimate(Timestamp):
    """
    Model to store user estimates
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,help_text='User which has estimated the ticket.'
    )
    ticket = models.ForeignKey(
        pokerboard_models.Ticket, on_delete=models.CASCADE, help_text='Ticket to which estimate belongs.'
    )
    estimation_duration = models.DurationField(help_text='Duration for voting(in secs)')
    estimate = models.PositiveIntegerField(help_text='Value of estimate done by the user.')

    def __str__(self):
        return f"{self.ticket} -> {self.user} -> {self.estimate}"
