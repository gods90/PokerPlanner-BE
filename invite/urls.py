from rest_framework.routers import DefaultRouter

from django.urls import path, include

from invite.views import InviteViewSet, ValidateInviteView

router = DefaultRouter()
router.register('', InviteViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('validate', ValidateInviteView.as_view())
]
