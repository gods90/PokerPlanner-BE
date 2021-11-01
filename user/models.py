from django.contrib.auth.models import AbstractUser
from django.db import models

from common.models import Timestamp


class User(AbstractUser, Timestamp):
    """
    A custom user model to store details about a user.
    """
    email = models.EmailField(
        unique=True, max_length=50, help_text='Email should be valid email address'
    )
    first_name = models.CharField(
        blank=False, max_length=50, help_text='First Name of User'
    )
    username = models.CharField(
        blank=True, max_length=50, help_text='Username of User'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    
    def full_name(self):
        """
        Get fullname of the user
        """
        return self.first_name + self.last_name
    
    def save_base(self, raw=False, force_insert=False,
                 force_update=False, using=None, update_fields=None):
        self.set_password(self.password)
        return super().save_base(raw=raw, force_insert=force_insert,
                                force_update=force_update, using=using, update_fields=update_fields)
                                