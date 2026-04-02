from rest_framework import serializers
from .models import Event, TicketTier

class TicketTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketTier
        fields = ['id', 'name', 'price_cents', 'capacity']

class EventSerializer(serializers.ModelSerializer):
    ticket_tiers = TicketTierSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'slug', 'description', 'location', 'starts_at', 'ends_at', 'status', 'ticket_tiers']
