import pytest
from django.urls import reverse

from core.models import Campaign, DeliveryLog, Person
from core.retry_service import retry_failed_campaign_emails


@pytest.mark.django_db
def test_retry_failed_campaign_emails_service():
    campaign = Campaign.objects.create(
        title="June Newsletter",
        email_subject="June Updates",
    )

    person = Person.objects.create(
        full_name="Jane Test",
        email="jane@example.com",
        email_consent=True,
    )

    log = DeliveryLog.objects.create(
        campaign=campaign,
        person=person,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_FAILED,
        error_message="SMTP error",
    )

    result = retry_failed_campaign_emails(campaign)

    log.refresh_from_db()

    assert result["retried"] == 1
    assert log.status == DeliveryLog.STATUS_PENDING
    assert log.error_message == ""


@pytest.mark.django_db
def test_retry_failed_campaign_emails_view(client):
    campaign = Campaign.objects.create(
        title="June Newsletter",
        email_subject="June Updates",
    )

    person = Person.objects.create(
        full_name="Jane Test",
        email="jane@example.com",
        email_consent=True,
    )

    log = DeliveryLog.objects.create(
        campaign=campaign,
        person=person,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_FAILED,
        error_message="SMTP error",
    )

    url = reverse(
        "campaign_retry_failed_emails",
        kwargs={"campaign_id": campaign.id},
    )

    response = client.post(url)

    log.refresh_from_db()

    assert response.status_code == 302
    assert log.status == DeliveryLog.STATUS_PENDING