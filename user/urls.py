from django.urls import path

from user.views import UserViewSet, ChangePasswordView


urlpatterns = [
    path("", UserViewSet.as_view(),name="user"),
    path('changepassword/', ChangePasswordView.as_view())

]

