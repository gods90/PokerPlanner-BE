from django.urls import path

from user.views import UserViewSet, ChangePasswordView

urlpatterns = [
    path("", UserViewSet.as_view()),
    path('changepassword/', ChangePasswordView.as_view())

]

