from django.contrib import admin

from pokerboard.models import Pokerboard, PokerboardUserMapping, UserEstimate, Invite

admin.site.register(Pokerboard)
admin.site.register(PokerboardUserMapping)
admin.site.register(UserEstimate)
admin.site.register(Invite)

