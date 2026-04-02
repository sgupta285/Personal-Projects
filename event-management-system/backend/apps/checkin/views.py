from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import AdmissionToken

@api_view(['POST'])
def validate_token(request):
    token = request.data.get('token')
    admission = AdmissionToken.objects.select_related('registration').get(token=token)
    if admission.checked_in_at is None:
        admission.checked_in_at = timezone.now()
        admission.save(update_fields=['checked_in_at'])
    return Response({
        'valid': True,
        'registration_id': admission.registration_id,
        'checked_in_at': admission.checked_in_at,
    })
