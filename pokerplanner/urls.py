from django.contrib import admin
from django.urls import path, include

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='PokerPlanner API')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('pokerboard/', include('pokerboard.urls')),
    path('group/', include('group.urls')),
    path('login/', ObtainAuthToken.as_view(), name='token-auth'),
    path('api/docs/', schema_view)
]

