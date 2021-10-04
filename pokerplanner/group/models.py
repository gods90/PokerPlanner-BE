from django.db import models
from pokerplanner.user.models import User


# Create your models here.
class Group(models.Model):
    name = models.CharField(max_length=250,blank=False,help_text="Name of the group")
    members = models.ManyToManyField(User,help_text="Members of the group")

