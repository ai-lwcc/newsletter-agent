import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import Campaign


@pytest.mark.django_db
def test_campaign_ai_fields_exist():
    campaign = Campaign.objects.create(
        title="AI Test",
        email_subject="",
        email_body="",
        whatsapp_message="",
        ai_summary="Summary",
        ai_suggested_groups=["General Newsletter"],
        ai_review_required=True,
    )

    assert campaign.ai_summary == "Summary"
    assert campaign.ai_suggested_groups == ["General Newsletter"]
    assert campaign.ai_review_required is True