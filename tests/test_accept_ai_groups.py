import pytest
from django.urls import reverse

from core.models import Campaign, Group


@pytest.mark.django_db
def test_accept_ai_groups_applies_suggested_groups(authenticated_client):
    group = Group.objects.create(name="General Newsletter")

    campaign = Campaign.objects.create(
        title="AI Campaign",
        email_subject="AI Subject",
        ai_suggested_groups=["General Newsletter"],
        ai_review_required=True,
    )

    url = reverse(
        "campaign_accept_ai_groups",
        kwargs={"campaign_id": campaign.id},
    )

    response = authenticated_client.get(url)

    campaign.refresh_from_db()

    assert response.status_code == 302
    assert group in campaign.target_groups.all()
    assert campaign.ai_review_required is False