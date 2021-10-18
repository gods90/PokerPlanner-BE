from rest_framework.routers import DefaultRouter

from django.urls import path, include

from group.views import GroupViewSet

router = DefaultRouter()
router.register('', GroupViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

