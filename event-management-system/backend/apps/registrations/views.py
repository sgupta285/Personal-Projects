from django.db.models import Count
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.events.models import Event
from .models import Registration, WaitlistEntry
from .serializers import CheckoutSerializer, PromoteSerializer, RegistrationSerializer, WaitlistEntrySerializer, WaitlistSerializer
from .services import checkout, join_waitlist, promote_waitlist

@api_view(['POST'])
def checkout_view(request):
    serializer = CheckoutSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    registration = checkout(serializer.validated_data['event'], serializer.validated_data['ticket_tier'], serializer.validated_data['full_name'], serializer.validated_data['email'])
    return Response(RegistrationSerializer(registration).data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def waitlist_view(request):
    serializer = WaitlistSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    entry = join_waitlist(serializer.validated_data['event'], serializer.validated_data['ticket_tier'], serializer.validated_data['full_name'], serializer.validated_data['email'])
    return Response(WaitlistEntrySerializer(entry).data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def promote_view(request):
    serializer = PromoteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    entry = WaitlistEntry.objects.get(pk=serializer.validated_data['waitlist_entry_id'])
    registration = promote_waitlist(entry)
    return Response(RegistrationSerializer(registration).data)

@api_view(['GET'])
def analytics_summary(request, event_id: int):
    event = Event.objects.get(pk=event_id)
    registrations = Registration.objects.filter(event=event)
    waitlist_count = WaitlistEntry.objects.filter(event=event, promoted=False).count()
    return Response({
        'event_id': event.id,
        'title': event.title,
        'confirmed_registrations': registrations.filter(status=Registration.Status.CONFIRMED).count(),
        'waitlist_count': waitlist_count,
        'revenue_cents': sum(r.ticket_tier.price_cents for r in registrations.select_related('ticket_tier')),
    })
