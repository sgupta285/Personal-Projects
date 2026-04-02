from django.db import models
from apps.registrations.models import Registration

class AdmissionToken(models.Model):
    registration = models.OneToOneField(Registration, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    checked_in_at = models.DateTimeField(null=True, blank=True)
