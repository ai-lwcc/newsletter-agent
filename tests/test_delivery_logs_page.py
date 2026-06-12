import pytest
from django.urls import reverse

from core.models import Campaign, DeliveryLog, Person


@pytest.mark.django_db
def test_delivery_logs_page_loads(authenticated_client):
    campaign = Campaign.objects.create(
        title="Test Campaign",
        email_subject="Test Subject",
        email_body="Hello.",
    )

    person = Person.objects.create(
        full_name="Jane Test",
        email="jane@example.com",
        email_consent=True,
    )

    DeliveryLog.objects.create(
        campaign=campaign,
        person=person,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_SENT,
    )

    response = authenticated_client.get(
        reverse("delivery_logs")
    )

    assert response.status_code == 200
    assert b"Delivery Logs" in response.content
    assert b"Test Campaign" in response.content
    assert b"Jane Test" in response.content


@pytest.mark.django_db
def test_delivery_logs_page_filters_by_status(authenticated_client):
    campaign = Campaign.objects.create(
        title="Test Campaign",
        email_subject="Test Subject",
        email_body="Hello.",
    )

    sent_person = Person.objects.create(
        full_name="Sent Person",
        email="sent@example.com",
        email_consent=True,
    )

    failed_person = Person.objects.create(
        full_name="Failed Person",
        email="failed@example.com",
        email_consent=True,
    )

    DeliveryLog.objects.create(
        campaign=campaign,
        person=sent_person,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_SENT,
    )

    DeliveryLog.objects.create(
        campaign=campaign,
        person=failed_person,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_FAILED,
    )

    response = authenticated_client.get(
        reverse("delivery_logs"),
        {"status": DeliveryLog.STATUS_FAILED},
    )

    assert response.status_code == 200
    assert b"Failed Person" in response.content
    assert b"Sent Person" not in response.content