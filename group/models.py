from django.db import models

from common.models import Timestamp

from user.models import User


class Group(Timestamp):
    """ 
    Model to store a group of users participating in poker planning.
    """
    name = models.CharField(max_length=250, help_text='Name of the group')
    users = models.ManyToManyField(
        User, help_text='Members of the group', related_name='members'
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['name', 'created_by']

    def __str__(self):
        return self.name
