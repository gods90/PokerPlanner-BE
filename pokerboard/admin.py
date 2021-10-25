from django.contrib import admin

from pokerboard.models import Pokerboard, PokerboardUserGroup, Invite

@admin.register(Pokerboard)
class PokerboardAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'manager']

@admin.register(PokerboardUserGroup)
class PokerboardUserGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'pokerboard', 'user', 'group', 'role']


@admin.register(Invite)
class Invite(admin.ModelAdmin):
    list_display = ['id', 'user', 'pokerboard', 'user_role', 'status']

