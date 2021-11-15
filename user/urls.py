from django.conf.urls import include
from django.urls import path

from rest_framework.routers import DefaultRouter

from user.views import ChangePasswordView, EstimateViewSet, UserViewSet, UserTicketViewSet

router = DefaultRouter()
router.register(r'estimate', EstimateViewSet, basename='estimate')
router.register(r'tickets', UserTicketViewSet, basename='tickets')

urlpatterns = [
    path('', UserViewSet.as_view(), name="user"),
    path('', include(router.urls)),
    path('changepassword/', ChangePasswordView.as_view()),
]
