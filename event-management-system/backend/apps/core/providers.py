import os
from dataclasses import dataclass

@dataclass
class PaymentResult:
    success: bool
    provider_reference: str

class PaymentProvider:
    def charge(self, amount_cents: int, currency: str = 'USD') -> PaymentResult:
        raise NotImplementedError

class StubPaymentProvider(PaymentProvider):
    def charge(self, amount_cents: int, currency: str = 'USD') -> PaymentResult:
        return PaymentResult(success=True, provider_reference=f'stub_{amount_cents}_{currency.lower()}')

class EmailProvider:
    def send(self, to_email: str, subject: str, body: str) -> None:
        raise NotImplementedError

class ConsoleEmailProvider(EmailProvider):
    def send(self, to_email: str, subject: str, body: str) -> None:
        print({'to': to_email, 'subject': subject, 'body': body})

def get_payment_provider() -> PaymentProvider:
    return StubPaymentProvider()

def get_email_provider() -> EmailProvider:
    return ConsoleEmailProvider()
