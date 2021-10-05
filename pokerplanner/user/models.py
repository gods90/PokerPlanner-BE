from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    A custom user model to store details about a user.
    """
    email = models.EmailField(
        unique=True, max_length=50, help_text='Email should be valid email address')
    first_name = models.CharField(
        blank=False, max_length=50, help_text='First Name of User')
    username = models.CharField(
        blank=True, max_length=50, help_text='Username of User')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
