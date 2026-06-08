import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from core.models import Campaign


@pytest.mark.django_db
def test_ai_campaign_create_page_loads(client):
    response = client.get(reverse("ai_campaign_create"))

    assert response.status_code == 200
    assert b"Create AI Campaign" in response.content


@pytest.mark.django_db
def test_ai_campaign_create_creates_campaign(client, monkeypatch):
    queued_campaign_ids = []

    class FakeTask:
        def delay(self, campaign_id):
            queued_campaign_ids.append(campaign_id)

    monkeypatch.setattr(
        "core.views.generate_campaign_ai_draft_task",
        FakeTask(),
    )

    fake_pdf = SimpleUploadedFile(
        "annual_report.pdf",
        b"%PDF-1.4 fake pdf content",
        content_type="application/pdf",
    )

    response = client.post(
        reverse("ai_campaign_create"),
        {
            "title": "AI Annual Report Campaign",
            "pdf_attachment": fake_pdf,
            "email_length": "short",
            "tone": "professional",
        },
    )

    campaign = Campaign.objects.get(title="AI Annual Report Campaign")

    assert response.status_code == 302
    assert campaign.email_subject == ""
    assert campaign.email_body == ""
    assert campaign.whatsapp_message == ""
    assert campaign.ai_status == Campaign.AI_PENDING
    assert campaign.email_length == "short"
    assert campaign.tone == "professional"
    assert queued_campaign_ids == [campaign.id]


@pytest.mark.django_db
def test_ai_campaign_create_can_set_scheduling(client, monkeypatch):
    queued_campaign_ids = []

    class FakeTask:
        def delay(self, campaign_id):
            queued_campaign_ids.append(campaign_id)

    monkeypatch.setattr(
        "core.views.generate_campaign_ai_draft_task",
        FakeTask(),
    )

    fake_pdf = SimpleUploadedFile(
        "annual_report.pdf",
        b"%PDF-1.4 fake pdf content",
        content_type="application/pdf",
    )

    response = client.post(
        reverse("ai_campaign_create"),
        {
            "title": "Scheduled AI Campaign",
            "pdf_attachment": fake_pdf,
            "scheduled_send_time": "2026-06-15T10:00",
            "automatically_send_when_due": "on",
            "email_length": "medium",
            "tone": "donor",
        },
    )

    campaign = Campaign.objects.get(title="Scheduled AI Campaign")

    assert response.status_code == 302
    assert campaign.status == Campaign.STATUS_SCHEDULED
    assert campaign.scheduled_send_time is not None
    assert campaign.automatically_send_when_due is True
    assert campaign.ai_status == Campaign.AI_PENDING
    assert campaign.email_length == "medium"
    assert campaign.tone == "donor"
    assert queued_campaign_ids == [campaign.id]