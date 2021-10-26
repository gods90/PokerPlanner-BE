from django.urls import path

from user.views import ChangePasswordView, UserViewSet

urlpatterns = [
    path("", UserViewSet.as_view(),name="user"),
    path('changepassword/', ChangePasswordView.as_view())

]

