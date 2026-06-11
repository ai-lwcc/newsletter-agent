import pytest
from django.urls import reverse

from core.models import Campaign
from core.models import Group
from core.models import Person


@pytest.mark.django_db
def test_campaign_recipients_page(authenticated_client):
    group = Group.objects.create(
        name="Pickleball Players"
    )

    campaign = Campaign.objects.create(
        title="Newsletter",
        email_subject="Test",
    )

    campaign.target_groups.add(group)

    person = Person.objects.create(
        full_name="John",
        email="john@test.com",
        email_consent=True,
    )

    person.groups.add(group)

    url = reverse(
        "campaign_recipients",
        kwargs={
            "campaign_id": campaign.id
        }
    )

    response = authenticated_client.get(url)

    assert response.status_code == 200

    assert b"john@test.com" in response.content