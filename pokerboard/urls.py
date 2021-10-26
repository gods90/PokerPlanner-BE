from django.urls import include, path
from rest_framework.routers import DefaultRouter

from pokerboard.views import PokerBoardViewSet,PokerboardMemberViewSet

router = DefaultRouter()
router.register('', PokerBoardViewSet,basename="pokerboard")
router.register('<int:pk>/members',PokerboardMemberViewSet,basename="members")

urlpatterns = [
    path("", include(router.urls)),
    path("<int:pk>/members/", PokerboardMemberViewSet.as_view({'get': 'list'}), name="members")
]

