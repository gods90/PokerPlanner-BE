from django.db import models
from pokerplanner.user.models import User

class Pokerboard(models.Model):
    "Pokerboard setting class"
    SERIES = 1
    EVEN = 2
    ODD = 3
    FIBONACCI = 4
    ESTIMATION_CHOICES = (
        (SERIES, "Series"),
        (EVEN, "Even"),
        (ODD, "Odd"),
        (FIBONACCI, "Fibonacci"),
    )
    
    CREATED = 1
    STARTED = 2
    ENDED = 3
    STATUS_CHOICES = (
        (CREATED, "Created"),
        (STARTED, "Started"),
        (ENDED, "Ended")
    )
    manager=models.ForeignKey(User,on_delete=models.CASCADE,help_text="Owner of pokerboard")
    title = models.CharField(unique=True, max_length=20, help_text='Name of Pokerboard')
    description = models.CharField(max_length=100, help_text='Description of POkerboard')
    configuration = models.IntegerField(choices=ESTIMATION_CHOICES, help_text='Estimation type', default=SERIES)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=CREATED)
    
    def __str__(self) -> str:
        return self.title