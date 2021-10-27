from django.urls import include, path
from rest_framework.routers import DefaultRouter

from group.views import GroupViewSet

router = DefaultRouter()
router.register('', GroupViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
