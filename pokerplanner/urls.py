from django.contrib import admin
from django.urls import include, path
from rest_framework_swagger.views import get_swagger_view

from user.views import LoginView, LogoutView

schema_view = get_swagger_view(title='PokerPlanner API')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('pokerboard/', include('pokerboard.urls')),
    path('', include('invite.urls')),
    path('group/', include('group.urls')),
    path('login/', LoginView.as_view(), name='login'),
    path('api/docs/', schema_view),
    path('session/', include('session.urls')),
    path('logout/', LogoutView.as_view(), name='logout')
]
