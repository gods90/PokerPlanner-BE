from django.contrib import admin

from pokerboard.models import Pokerboard, PokerboardUserGroup

@admin.register(Pokerboard)
class PokerboardAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'manager']

@admin.register(PokerboardUserGroup)
class PokerboardUserGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'pokerboard', 'user', 'group', 'role']

