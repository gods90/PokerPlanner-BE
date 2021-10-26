from django.urls import include, path
from rest_framework.routers import DefaultRouter

from invite.views import InviteViewSet

router = DefaultRouter()
router.register('', InviteViewSet)

urlpatterns = [
    path("", include(router.urls))
]

