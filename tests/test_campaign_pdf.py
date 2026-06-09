import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import Campaign


@pytest.mark.django_db
def test_campaign_can_have_primary_attachment():
    fake_pdf = SimpleUploadedFile(
        "newsletter.pdf",
        b"%PDF-1.4 fake pdf content",
        content_type="application/pdf",
    )

    campaign = Campaign.objects.create(
        title="June Newsletter",
        email_subject="June Updates",
        primary_attachment=fake_pdf,
    )

    assert campaign.primary_attachment.name.startswith(
        "campaign_pdfs/"
    )

    assert campaign.primary_attachment.name.endswith(
        ".pdf"
    )