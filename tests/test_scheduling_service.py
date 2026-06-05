import pytest
from django.utils import timezone

from core.models import Campaign, DeliveryLog, Group, Person
from core.scheduling_service import get_due_scheduled_campaigns


@pytest.mark.django_db
def test_get_due_scheduled_campaigns_returns_due_campaign():
    group = Group.objects.create(name="Pickleball Players")

    campaign = Campaign.objects.create(
        title="Scheduled Newsletter",
        email_subject="Scheduled Test",
        status=Campaign.STATUS_SCHEDULED,
        automatically_send_when_due=True,
        scheduled_send_time=timezone.now(),
    )
    campaign.target_groups.add(group)

    person = Person.objects.create(
        full_name="Jane Test",
        email="jane@example.com",
        email_consent=True,
    )
    person.groups.add(group)

    DeliveryLog.objects.create(
        campaign=campaign,
        person=person,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_PENDING,
    )

    due_campaigns = get_due_scheduled_campaigns()

    assert campaign in due_campaigns


@pytest.mark.django_db
def test_get_due_scheduled_campaigns_excludes_draft_campaign():
    campaign = Campaign.objects.create(
        title="Draft Newsletter",
        email_subject="Draft Test",
        status=Campaign.STATUS_DRAFT,
        automatically_send_when_due=True,
        scheduled_send_time=timezone.now(),
    )

    due_campaigns = get_due_scheduled_campaigns()

    assert campaign not in due_campaigns


@pytest.mark.django_db
def test_get_due_scheduled_campaigns_excludes_future_campaign():
    future_time = timezone.now() + timezone.timedelta(days=1)

    campaign = Campaign.objects.create(
        title="Future Newsletter",
        email_subject="Future Test",
        status=Campaign.STATUS_SCHEDULED,
        automatically_send_when_due=True,
        scheduled_send_time=future_time,
    )

    due_campaigns = get_due_scheduled_campaigns()

    assert campaign not in due_campaigns

@pytest.mark.django_db
def test_get_due_scheduled_campaigns_excludes_campaign_without_pending_logs():
    campaign = Campaign.objects.create(
        title="Scheduled Without Logs",
        email_subject="Scheduled Test",
        status=Campaign.STATUS_SCHEDULED,
        automatically_send_when_due=True,
        scheduled_send_time=timezone.now(),
    )

    due_campaigns = get_due_scheduled_campaigns()

    assert campaign not in due_campaigns