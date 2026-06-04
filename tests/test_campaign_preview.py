import pytest
from django.urls import reverse

from core.models import Campaign, Group


@pytest.mark.django_db
def test_campaign_preview_page_loads(client):
    group = Group.objects.create(name="Pickleball Players")

    campaign = Campaign.objects.create(
        title="June Pickleball Newsletter",
        email_subject="Upcoming Pickleball Events",
        email_body="This is the email body.",
        whatsapp_message="This is the WhatsApp message.",
    )

    campaign.target_groups.add(group)

    url = reverse(
        "campaign_preview",
        kwargs={"campaign_id": campaign.id},
    )

    response = client.get(url)

    assert response.status_code == 200
    assert b"June Pickleball Newsletter" in response.content
    assert b"Upcoming Pickleball Events" in response.content
    assert b"This is the email body." in response.content
    assert b"Pickleball Players" in response.content