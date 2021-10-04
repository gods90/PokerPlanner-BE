from rest_framework.routers import DefaultRouter

from django.urls import path,include

from pokerplanner.user.views import UserViewSet

router=DefaultRouter()
router.register('', UserViewSet)

urlpatterns=[
    path("",include(router.urls)),
]