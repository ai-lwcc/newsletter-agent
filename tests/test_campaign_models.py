import pytest

from core.models import Campaign, Group


@pytest.mark.django_db
def test_create_campaign():
    campaign = Campaign.objects.create(
        title="July Pickleball Newsletter",
        email_subject="Upcoming Pickleball Events",
        email_body="This is a test newsletter.",
        whatsapp_message="New pickleball updates are available.",
    )

    assert campaign.title == "July Pickleball Newsletter"
    assert campaign.status == Campaign.STATUS_DRAFT
    assert str(campaign) == "July Pickleball Newsletter"


@pytest.mark.django_db
def test_campaign_can_target_groups():
    group = Group.objects.create(name="Pickleball Players")

    campaign = Campaign.objects.create(
        title="July Pickleball Newsletter",
        email_subject="Upcoming Pickleball Events",
    )

    campaign.target_groups.add(group)

    assert group in campaign.target_groups.all()
    assert campaign in group.campaigns.all()