from django.db import models


class Timestamp(models.Model):
    """
    Model containing common fields for all models.
    """
    created_at = models.DateTimeField(auto_now_add=True, help_text='Time at which object was created')
    updated_at = models.DateTimeField(auto_now=True, help_text='Time at which object was updated')
    
    class Meta:
        abstract = True
