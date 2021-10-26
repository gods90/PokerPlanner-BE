from django.contrib import admin

from invite.models import Invite

# Register your models here.
@admin.register(Invite)
class Invite(admin.ModelAdmin):
    list_display = ['id', 'user', 'pokerboard', 'user_role', 'status']
