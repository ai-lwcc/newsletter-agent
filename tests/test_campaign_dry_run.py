import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from core.models import Campaign, DeliveryLog, Group, Person


@pytest.mark.django_db
def test_campaign_dry_run_page_creates_pending_logs(client):
    group = Group.objects.create(name="Pickleball Players")

    fake_file = SimpleUploadedFile(
        "newsletter.pdf",
        b"%PDF-1.4 fake pdf content",
        content_type="application/pdf",
    )

    campaign = Campaign.objects.create(
        title="June Newsletter",
        email_subject="June Updates",
        email_body="Hello everyone.",
        primary_attachment=fake_file,
        ai_review_required=False,
    )

    campaign.target_groups.add(group)

    person = Person.objects.create(
        full_name="Jane Test",
        email="jane@example.com",
        email_consent=True,
    )
    person.groups.add(group)

    url = reverse(
        "campaign_dry_run",
        kwargs={"campaign_id": campaign.id},
    )

    response = client.get(url)

    assert response.status_code == 200
    assert b"No real emails were sent." in response.content
    assert b"jane@example.com" in response.content
    assert DeliveryLog.objects.count() == 1