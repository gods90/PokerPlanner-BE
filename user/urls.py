from django.urls import path, include

from user.views import InviteViewSet, UserViewSet, ChangePasswordView

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('',InviteViewSet, basename='user-invite')

urlpatterns = [
    path("", UserViewSet.as_view(),name="user"),
    path('changepassword/', ChangePasswordView.as_view()),
    path('invite/', include(router.urls))

]

