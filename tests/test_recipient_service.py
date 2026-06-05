import pytest

from core.models import Campaign
from core.models import Group
from core.models import Person
from core.recipient_service import get_campaign_recipients


@pytest.mark.django_db
def test_get_campaign_recipients():
    group = Group.objects.create(
        name="Pickleball Players"
    )

    campaign = Campaign.objects.create(
        title="Newsletter",
        email_subject="Test",
    )

    campaign.target_groups.add(group)

    good_person = Person.objects.create(
        full_name="John",
        email="john@test.com",
        email_consent=True,
    )

    good_person.groups.add(group)

    bad_person = Person.objects.create(
        full_name="Jane",
        email="jane@test.com",
        email_consent=False,
    )

    bad_person.groups.add(group)

    recipients = get_campaign_recipients(
        campaign
    )

    assert good_person in recipients
    assert bad_person not in recipients