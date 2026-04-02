from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4


@dataclass
class BookingConfirmation:
    provider_name: str
    confirmation_code: str
    accepted_time: datetime


class MockBookingProvider:
    name = "mock-opentable"

    def create_booking(self, *, restaurant_slug: str, reservation_time: datetime, party_size: int) -> BookingConfirmation:
        code = f"RES-{restaurant_slug[:4].upper()}-{uuid4().hex[:8].upper()}"
        return BookingConfirmation(provider_name=self.name, confirmation_code=code, accepted_time=reservation_time)
