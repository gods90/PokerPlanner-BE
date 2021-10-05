from django.db import models

from pokerplanner.user.models import User


class Group(models.Model):
    """ Model to store a group of users participating in poker planning."""
    name = models.CharField(max_length=250, blank=False,
                            help_text='Name of the group')

    users = models.ManyToManyField(User, help_text='Members of the group')

    def __str__(self):
        return self.name
