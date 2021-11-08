from django.contrib import admin

from pokerboard.models import Pokerboard, PokerboardUserGroup, Ticket


@admin.register(Pokerboard)
class PokerboardAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'manager']


@admin.register(PokerboardUserGroup)
class PokerboardUserGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'pokerboard', 'user', 'group', 'role']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'ticket_id', 'pokerboard', 'status']
