import pytest
from django.core import mail
from django.test import override_settings
from django.urls import reverse

from core.email_service import send_campaign_test_email
from core.models import Campaign


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="newsletter@example.com",
    TEST_RECIPIENT_EMAIL="sender@example.com",
)
def test_send_campaign_test_email_service():
    campaign = Campaign.objects.create(
        title="June Newsletter",
        email_subject="June Updates",
        email_body="This is a test email.",
    )

    send_campaign_test_email(campaign)

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "June Updates"
    assert mail.outbox[0].body == "This is a test email."
    assert mail.outbox[0].to == ["sender@example.com"]


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="newsletter@example.com",
    TEST_RECIPIENT_EMAIL="sender@example.com",
)
def test_send_campaign_test_email_view(client):
    campaign = Campaign.objects.create(
        title="June Newsletter",
        email_subject="June Updates",
        email_body="This is a test email.",
    )

    url = reverse(
        "send_campaign_test_email",
        kwargs={"campaign_id": campaign.id},
    )

    response = client.get(url)

    assert response.status_code == 200
    assert b"Test Email Sent" in response.content
    assert b"Back to Preview" in response.content
    assert len(mail.outbox) == 1