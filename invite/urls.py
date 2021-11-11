from django.urls import path

from invite.views import InviteViewSet, ValidateInviteView

urlpatterns = [
    path('invite/<int:pk>/',
         InviteViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'})),
    path('invite/', InviteViewSet.as_view({'get': 'list'})),
    path('pokerboard/<int:pokerboard_id>/invite/', InviteViewSet.as_view({'post' : 'create'})),
    path('validate', ValidateInviteView.as_view())
]
