from django.urls import path
from .views import EventListCreateView, EventDetailView

urlpatterns = [
    path('events/', EventListCreateView.as_view()),
    path('events/<int:pk>/', EventDetailView.as_view()),
]
