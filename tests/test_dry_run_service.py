import pytest

from core.dry_run_service import create_campaign_dry_run_logs
from core.models import Campaign, DeliveryLog, Group, Person


@pytest.mark.django_db
def test_create_campaign_dry_run_logs():
    group = Group.objects.create(name="Pickleball Players")

    campaign = Campaign.objects.create(
        title="June Newsletter",
        email_subject="June Updates",
    )
    campaign.target_groups.add(group)

    person = Person.objects.create(
        full_name="Jane Test",
        email="jane@example.com",
        email_consent=True,
    )
    person.groups.add(group)

    result = create_campaign_dry_run_logs(campaign)

    assert result["recipients"] == 1
    assert result["created"] == 1
    assert result["existing"] == 0
    assert DeliveryLog.objects.count() == 1

    log = DeliveryLog.objects.first()

    assert log.campaign == campaign
    assert log.person == person
    assert log.status == DeliveryLog.STATUS_PENDING


@pytest.mark.django_db
def test_dry_run_does_not_duplicate_logs():
    group = Group.objects.create(name="Pickleball Players")

    campaign = Campaign.objects.create(
        title="June Newsletter",
        email_subject="June Updates",
    )
    campaign.target_groups.add(group)

    person = Person.objects.create(
        full_name="Jane Test",
        email="jane@example.com",
        email_consent=True,
    )
    person.groups.add(group)

    first_result = create_campaign_dry_run_logs(campaign)
    second_result = create_campaign_dry_run_logs(campaign)

    assert first_result["created"] == 1
    assert second_result["created"] == 0
    assert second_result["existing"] == 1
    assert DeliveryLog.objects.count() == 1