import pytest
from django.urls import reverse

from core.models import Campaign, Group


@pytest.mark.django_db
def test_generate_ai_draft_view_queues_task(authenticated_client, monkeypatch):
    Group.objects.create(name="General Newsletter")

    campaign = Campaign.objects.create(
        title="AI Campaign",
        email_subject="Old Subject",
        email_body="Old Body",
        whatsapp_message="Old WhatsApp",
    )

    queued_campaign_ids = []

    class FakeTask:
        def delay(self, campaign_id):
            queued_campaign_ids.append(campaign_id)

    monkeypatch.setattr(
        "core.views.generate_campaign_ai_draft_task",
        FakeTask(),
    )

    url = reverse(
        "campaign_generate_ai_draft",
        kwargs={"campaign_id": campaign.id},
    )

    response = authenticated_client.get(url)

    campaign.refresh_from_db()

    assert response.status_code == 302
    assert campaign.email_subject == "Old Subject"
    assert campaign.email_body == "Old Body"
    assert campaign.whatsapp_message == "Old WhatsApp"
    assert campaign.ai_status == Campaign.AI_PENDING
    assert queued_campaign_ids == [campaign.id]