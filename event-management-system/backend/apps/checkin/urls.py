from django.urls import path
from .views import validate_token

urlpatterns = [
    path('checkin/validate/', validate_token),
]
