from rest_framework.routers import DefaultRouter

from django.urls import path, include

from invite.views import InviteViewSet

router = DefaultRouter()
router.register('', InviteViewSet)

urlpatterns = [
    path("", include(router.urls))
]

