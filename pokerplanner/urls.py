from django.contrib import admin
from django.urls import path, include

from user.views import LoginView


from rest_framework_swagger.views import get_swagger_view
schema_view = get_swagger_view(title='PokerPlanner API')
urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('login/', LoginView.as_view(), name='token-auth'),
    path('api/docs/', schema_view)
]
