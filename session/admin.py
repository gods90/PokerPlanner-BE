from django.contrib import admin

from session.models import Session, UserEstimate


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'pokerboard', 'status']

@admin.register(UserEstimate)
class UserEstimate(admin.ModelAdmin):
    list_display = ['id', 'user', 'ticket', 'estimate']
