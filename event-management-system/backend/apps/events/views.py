from rest_framework import generics
from .models import Event
from .serializers import EventSerializer

class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.order_by('starts_at')
    serializer_class = EventSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get('status', 'published')
        return qs.filter(status=status) if status else qs

class EventDetailView(generics.RetrieveAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
