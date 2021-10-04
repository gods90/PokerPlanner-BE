from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """ Custom user class. """
    username=None
    email=models.EmailField(unique=True,max_length=50,help_text='Email Address')
    first_name = models.CharField(blank=False,max_length=50, help_text="First Name of User")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']
    
    def __str__(self):
        return self.email
    