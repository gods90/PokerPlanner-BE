from django.urls import include, path
from rest_framework.routers import DefaultRouter

from pokerboard.views import (
    PokerBoardViewSet,PokerboardMemberViewSet, PokerboardGroupViewSet, TicketViewSet
)

router = DefaultRouter()
router.register('(?P<pokerboard_id>\d+)/members', PokerboardMemberViewSet, basename="members")
router.register('(?P<pokerboard_id>\d+)/group', PokerboardGroupViewSet, basename="groups")
router.register('(?P<pokerboard_id>\d+)/tickets', TicketViewSet, basename="tickets")
router.register('', PokerBoardViewSet, basename="pokerboard")

urlpatterns = [
    path("", include(router.urls))
]
