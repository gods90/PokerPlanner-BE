from django.contrib import admin
from django.urls import include, path
from django.conf import settings

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='PokerPlanner API')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('pokerboard/', include('pokerboard.urls')),
    path('invite/', include('invite.urls')),
    path('group/', include('group.urls')),
    path('login/', ObtainAuthToken.as_view(), name='login'),
    path('api/docs/', schema_view),
    path('session/', include('session.urls'))
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns+= path('__debug__/', include(debug_toolbar.urls)),