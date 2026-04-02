from django.urls import path
from .views import analytics_summary, checkout_view, promote_view, waitlist_view

urlpatterns = [
    path('registrations/checkout/', checkout_view),
    path('registrations/waitlist/', waitlist_view),
    path('registrations/promote/', promote_view),
    path('analytics/events/<int:event_id>/summary/', analytics_summary),
]
