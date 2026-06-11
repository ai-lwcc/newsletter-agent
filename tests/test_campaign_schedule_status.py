import pytest
from django.urls import reverse
from django.utils import timezone

from core.models import Campaign, DeliveryLog, Person


@pytest.mark.django_db
def test_campaign_schedule_status_page_loads(authenticated_client):
    campaign = Campaign.objects.create(
        title="Scheduled Campaign",
        email_subject="Scheduled Subject",
        status=Campaign.STATUS_SCHEDULED,
        automatically_send_when_due=True,
        scheduled_send_time=timezone.now(),
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
        status=DeliveryLog.STATUS_PENDING,
    )

    url = reverse(
        "campaign_schedule_status",
        kwargs={"campaign_id": campaign.id},
    )

    response = authenticated_client.get(url)

    assert response.status_code == 200
    assert b"Schedule Status" in response.content
    assert b"Ready for auto-send" in response.content