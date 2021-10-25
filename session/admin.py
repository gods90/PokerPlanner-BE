from django.contrib import admin

from session.models import Session, Ticket, UserEstimate

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'pokerboard', 'status']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'ticket_id', 'session', 'status']


@admin.register(UserEstimate)
class UserEstimate(admin.ModelAdmin):
    list_display = ['id', 'user', 'ticket', 'estimate']
