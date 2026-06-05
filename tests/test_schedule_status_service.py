import pytest
from django.utils import timezone

from core.models import Campaign, DeliveryLog, Person
from core.schedule_status_service import get_campaign_schedule_status


@pytest.mark.django_db
def test_schedule_status_ready_when_scheduled_with_pending_logs():
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

    status = get_campaign_schedule_status(campaign)

    assert status["pending_count"] == 1
    assert status["is_ready_for_auto_send"] is True


@pytest.mark.django_db
def test_schedule_status_not_ready_without_pending_logs():
    campaign = Campaign.objects.create(
        title="Scheduled Campaign",
        email_subject="Scheduled Subject",
        status=Campaign.STATUS_SCHEDULED,
        automatically_send_when_due=True,
        scheduled_send_time=timezone.now(),
    )

    status = get_campaign_schedule_status(campaign)

    assert status["pending_count"] == 0
    assert status["is_ready_for_auto_send"] is False