from django.contrib import admin
from django.urls import path, include

from user.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('login/', LoginView.as_view(), name='token-auth'),
]
