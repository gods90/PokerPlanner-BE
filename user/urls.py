from django.urls import path

from user.views import UserViewSet

urlpatterns = [
    path("", UserViewSet.as_view())
]

