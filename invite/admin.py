from django.contrib import admin

from invite.models import Invite


@admin.register(Invite)
class Invite(admin.ModelAdmin):
    """
    Registering invite model
    """
    list_display = ['id', 'user', 'pokerboard', 'user_role', 'status']
