import pytest
from django.contrib.auth.models import User
from apps.events.models import Event, TicketTier
from apps.registrations.models import Registration
from apps.registrations.services import checkout, join_waitlist, promote_waitlist
from apps.checkin.models import AdmissionToken

@pytest.mark.django_db
def test_capacity_and_waitlist_promotion():
    organizer = User.objects.create(username='org')
    event = Event.objects.create(
        title='Demo', slug='demo', description='x', location='Madison',
        starts_at='2026-05-10T09:00:00Z', ends_at='2026-05-10T10:00:00Z', organizer=organizer, status='published'
    )
    tier = TicketTier.objects.create(event=event, name='GA', price_cents=1000, capacity=1)
    checkout(event, tier, 'Alice', 'alice@example.com')
    with pytest.raises(ValueError):
        checkout(event, tier, 'Bob', 'bob@example.com')
    entry = join_waitlist(event, tier, 'Bob', 'bob@example.com')
    first = Registration.objects.first()
    first.status = Registration.Status.CANCELLED
    first.save(update_fields=['status'])
    promoted = promote_waitlist(entry)
    assert promoted.status == Registration.Status.CONFIRMED
    assert AdmissionToken.objects.filter(registration=promoted).exists()
