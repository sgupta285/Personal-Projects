from django.contrib.auth.models import User
from django.db import models

class Event(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        ARCHIVED = 'archived', 'Archived'

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    location = models.CharField(max_length=255)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class TicketTier(models.Model):
    event = models.ForeignKey(Event, related_name='ticket_tiers', on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    price_cents = models.PositiveIntegerField(default=0)
    capacity = models.PositiveIntegerField()

    class Meta:
        unique_together = ('event', 'name')

    def __str__(self):
        return f'{self.event.title} - {self.name}'
