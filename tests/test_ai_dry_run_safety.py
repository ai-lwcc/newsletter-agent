import pytest
from django.urls import reverse

from core.models import Campaign


@pytest.mark.django_db
def test_dry_run_blocked_when_ai_review_required(client):
    campaign = Campaign.objects.create(
        title="AI Review Required Campaign",
        email_subject="Subject",
        email_body="Body",
        ai_review_required=True,
    )

    response = client.get(
        reverse(
            "campaign_dry_run",
            kwargs={"campaign_id": campaign.id},
        )
    )

    assert response.status_code == 302