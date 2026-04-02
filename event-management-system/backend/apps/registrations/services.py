import secrets
from django.db import transaction
from apps.core.providers import get_email_provider, get_payment_provider
from apps.events.models import TicketTier
from apps.checkin.models import AdmissionToken
from .models import Registration, WaitlistEntry

def confirmed_count(ticket_tier: TicketTier) -> int:
    return Registration.objects.filter(ticket_tier=ticket_tier, status=Registration.Status.CONFIRMED).count()

@transaction.atomic
def checkout(event, ticket_tier, full_name, email):
    if confirmed_count(ticket_tier) >= ticket_tier.capacity:
        raise ValueError('Ticket tier is sold out')

    payment_provider = get_payment_provider()
    payment = payment_provider.charge(ticket_tier.price_cents)
    registration = Registration.objects.create(
        event=event,
        ticket_tier=ticket_tier,
        full_name=full_name,
        email=email,
        payment_reference=payment.provider_reference,
    )
    AdmissionToken.objects.create(registration=registration, token=secrets.token_urlsafe(24))
    get_email_provider().send(email, 'Registration confirmed', f'You are confirmed for {event.title}.')
    return registration

@transaction.atomic
def join_waitlist(event, ticket_tier, full_name, email):
    return WaitlistEntry.objects.create(event=event, ticket_tier=ticket_tier, full_name=full_name, email=email)

@transaction.atomic
def promote_waitlist(waitlist_entry):
    if waitlist_entry.promoted:
        raise ValueError('Entry already promoted')
    registration = checkout(waitlist_entry.event, waitlist_entry.ticket_tier, waitlist_entry.full_name, waitlist_entry.email)
    waitlist_entry.promoted = True
    waitlist_entry.save(update_fields=['promoted'])
    return registration
