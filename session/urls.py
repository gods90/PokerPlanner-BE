from django import urls
from django.urls import include, path

from rest_framework.routers import DefaultRouter

from session.views import SessionViewSet

router = DefaultRouter()
router.register('',SessionViewSet)

urlpatterns = [
    path('',include(router.urls))
]



