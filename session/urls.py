from django.urls import include, path

from rest_framework.routers import DefaultRouter

from session.views import CommentView, SessionViewSet

router = DefaultRouter()
router.register('',SessionViewSet)

urlpatterns = [
    path('',include(router.urls)),
    path("comment/<str:issue_key>", CommentView.as_view(), name="comment")
]
