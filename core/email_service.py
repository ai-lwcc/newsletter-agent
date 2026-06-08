from django.conf import settings

from core.email_provider import get_email_provider


class TestPerson:
    def __init__(self, email):
        self.email = email
        self.full_name = "Test Recipient"


def send_campaign_test_email(campaign):
    if not settings.TEST_RECIPIENT_EMAIL:
        raise ValueError(
            "TEST_RECIPIENT_EMAIL is not configured."
        )

    provider = get_email_provider()

    provider.send_campaign_email(
        campaign,
        TestPerson(settings.TEST_RECIPIENT_EMAIL),
    )