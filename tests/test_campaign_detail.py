import pytest
from django.urls import reverse

from core.models import Campaign, DeliveryLog, Person, UserActionLog


@pytest.mark.django_db
def test_campaign_detail_page_loads(authenticated_client):
    campaign = Campaign.objects.create(
        title="Test Campaign",
        email_subject="Test Subject",
        email_body="Hello.",
    )

    response = authenticated_client.get(
        reverse(
            "campaign_detail",
            kwargs={"campaign_id": campaign.id},
        )
    )

    assert response.status_code == 200
    assert b"Test Campaign" in response.content
    assert b"Delivery Summary" in response.content
    assert b"Workflow Actions" in response.content


@pytest.mark.django_db
def test_campaign_detail_shows_delivery_summary(authenticated_client):
    campaign = Campaign.objects.create(
        title="Test Campaign",
        email_subject="Test Subject",
        email_body="Hello.",
    )

    person = Person.objects.create(
        full_name="Jane Test",
        email="jane@example.com",
        email_consent=True,
    )

    DeliveryLog.objects.create(
        campaign=campaign,
        person=person,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_SENT,
    )

    response = authenticated_client.get(
        reverse(
            "campaign_detail",
            kwargs={"campaign_id": campaign.id},
        )
    )

    assert response.status_code == 200
    assert b"Sent: 1" in response.content


@pytest.mark.django_db
def test_campaign_detail_shows_recent_audit_logs(authenticated_client, django_user_model):
    user = django_user_model.objects.create_user(
        username="staffuser",
        password="password",
    )

    campaign = Campaign.objects.create(
        title="Test Campaign",
        email_subject="Test Subject",
        email_body="Hello.",
    )

    UserActionLog.objects.create(
        user=user,
        campaign=campaign,
        action=UserActionLog.ACTION_TEST_EMAIL_SENT,
    )

    response = authenticated_client.get(
        reverse(
            "campaign_detail",
            kwargs={"campaign_id": campaign.id},
        )
    )

    assert response.status_code == 200
    assert b"staffuser" in response.content
    assert b"Test Email Sent" in response.content