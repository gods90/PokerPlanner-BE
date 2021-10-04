from django.contrib import admin
from django.urls import path,include

from pokerplanner.user.views import CustomAuthToken

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/',include('pokerplanner.user.urls')),
    path('login/', CustomAuthToken.as_view(), name='token-auth'),
]

