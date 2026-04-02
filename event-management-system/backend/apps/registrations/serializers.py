from rest_framework import serializers
from apps.events.models import Event, TicketTier
from .models import Registration, WaitlistEntry

class CheckoutSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    ticket_tier_id = serializers.IntegerField()
    full_name = serializers.CharField(max_length=200)
    email = serializers.EmailField()

    def validate(self, attrs):
        attrs['event'] = Event.objects.get(pk=attrs['event_id'])
        attrs['ticket_tier'] = TicketTier.objects.get(pk=attrs['ticket_tier_id'])
        return attrs

class WaitlistSerializer(CheckoutSerializer):
    pass

class PromoteSerializer(serializers.Serializer):
    waitlist_entry_id = serializers.IntegerField()

class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = ['id', 'event_id', 'ticket_tier_id', 'full_name', 'email', 'status', 'payment_reference', 'created_at']

class WaitlistEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitlistEntry
        fields = ['id', 'event_id', 'ticket_tier_id', 'full_name', 'email', 'promoted', 'created_at']
