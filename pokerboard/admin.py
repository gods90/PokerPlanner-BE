from django.contrib import admin

from pokerboard.models import Pokerboard, PokerboardUserGroup, Session, UserEstimate, Invite, Ticket

@admin.register(Pokerboard)
class PokerboardAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'manager']

@admin.register(PokerboardUserGroup)
class PokerboardUserGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'pokerboard', 'user', 'group', 'role']

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'ticket_id', 'pokerboard', 'status']

@admin.register(UserEstimate)
class UserEstimate(admin.ModelAdmin):
    list_display = ['id', 'user', 'ticket', 'estimate']

@admin.register(Invite)
class Invite(admin.ModelAdmin):
    list_display = ['id', 'user', 'pokerboard', 'user_role', 'status']

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'pokerboard', 'status']
