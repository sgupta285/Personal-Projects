from django.contrib import admin
from django.urls import include, path
from apps.core.views import healthcheck

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', healthcheck),
    path('api/', include('apps.events.urls')),
    path('api/', include('apps.registrations.urls')),
    path('api/', include('apps.checkin.urls')),
]
