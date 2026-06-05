import pytest
from django.urls import reverse

from core.models import Campaign, Group


@pytest.mark.django_db
def test_generate_ai_draft_view_updates_campaign(client, monkeypatch):
    Group.objects.create(name="General Newsletter")

    campaign = Campaign.objects.create(
        title="AI Campaign",
        email_subject="Old Subject",
        email_body="Old Body",
        whatsapp_message="Old WhatsApp",
    )

    def fake_generate_campaign_ai_draft(campaign):
        return {
            "email_subject": "AI Subject",
            "email_body": "AI Email Body",
            "whatsapp_message": "AI WhatsApp Message",
            "suggested_groups": ["General Newsletter"],
            "summary": "AI Summary",
        }

    monkeypatch.setattr(
        "core.views.generate_campaign_ai_draft",
        fake_generate_campaign_ai_draft,
    )

    url = reverse(
        "campaign_generate_ai_draft",
        kwargs={"campaign_id": campaign.id},
    )

    response = client.get(url)

    campaign.refresh_from_db()

    assert response.status_code == 302
    assert campaign.email_subject == "AI Subject"
    assert campaign.email_body == "AI Email Body"
    assert campaign.whatsapp_message == "AI WhatsApp Message"
    assert campaign.ai_summary == "AI Summary"
    assert campaign.ai_suggested_groups == ["General Newsletter"]
    assert campaign.ai_review_required is True