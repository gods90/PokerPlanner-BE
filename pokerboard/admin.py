from django.contrib import admin

from pokerboard.models import Pokerboard, PokerboardUserMapping, UserEstimate, Invite, Ticket

admin.site.register(Pokerboard)
admin.site.register(PokerboardUserMapping)
admin.site.register(Ticket)
admin.site.register(UserEstimate)
admin.site.register(Invite)

