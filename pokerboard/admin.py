from django.contrib import admin

from pokerboard.models import Pokerboard, PokerboardUserGroup, Session, UserEstimate, Invite, Ticket

admin.site.register(Pokerboard)
admin.site.register(PokerboardUserGroup)
admin.site.register(Ticket)
admin.site.register(UserEstimate)
admin.site.register(Invite)
admin.site.register(Session)
