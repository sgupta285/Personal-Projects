from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.events.models import Event, TicketTier

class Command(BaseCommand):
    help = 'Seed demo data for local development'

    def handle(self, *args, **options):
        organizer, _ = User.objects.get_or_create(username='organizer@example.com', defaults={'email': 'organizer@example.com'})
        organizer.set_password('demo12345')
        organizer.save()
        staff, _ = User.objects.get_or_create(username='staff@example.com', defaults={'email': 'staff@example.com'})
        staff.set_password('demo12345')
        staff.save()

        event, created = Event.objects.get_or_create(
            slug='madison-product-summit',
            defaults={
                'title': 'Madison Product Summit',
                'description': 'A one-day meetup for product, data, and engineering teams.',
                'location': 'Union South, Madison, WI',
                'starts_at': '2026-05-10T09:00:00Z',
                'ends_at': '2026-05-10T17:00:00Z',
                'organizer': organizer,
                'status': Event.Status.PUBLISHED,
            }
        )
        TicketTier.objects.get_or_create(event=event, name='General Admission', defaults={'price_cents': 4900, 'capacity': 100})
        TicketTier.objects.get_or_create(event=event, name='Student', defaults={'price_cents': 1500, 'capacity': 25})
        self.stdout.write(self.style.SUCCESS('Demo data seeded.'))
