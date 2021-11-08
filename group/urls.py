from django.urls import include, path

from rest_framework.routers import DefaultRouter

from group.views import GroupMemberDeleteViewSet, GroupViewSet

router = DefaultRouter()
router.register('(?P<group_id>\d+)/removemembers',
                 GroupMemberDeleteViewSet, basename="groupmembers")
router.register('', GroupViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
