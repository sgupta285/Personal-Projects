from django.db import models
from apps.events.models import Event, TicketTier

class Registration(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = 'confirmed', 'Confirmed'
        WAITLISTED = 'waitlisted', 'Waitlisted'
        CANCELLED = 'cancelled', 'Cancelled'

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ticket_tier = models.ForeignKey(TicketTier, null=True, blank=True, on_delete=models.SET_NULL)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.CONFIRMED)
    payment_reference = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class WaitlistEntry(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ticket_tier = models.ForeignKey(TicketTier, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    promoted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
