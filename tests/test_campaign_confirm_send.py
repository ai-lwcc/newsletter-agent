import pytest
from django.test import override_settings
from django.urls import reverse

from core.dry_run_service import create_campaign_dry_run_logs
from core.models import Campaign, DeliveryLog, Group, Person


@pytest.mark.django_db
@override_settings(SEND_REAL_EMAILS=False, MAX_EMAILS_PER_DAY=300)
def test_confirm_send_page_loads(client):
    group = Group.objects.create(name="Pickleball Players")

    campaign = Campaign.objects.create(
        title="June Newsletter",
        email_subject="June Updates",
        email_body="Hello.",
    )
    campaign.target_groups.add(group)

    person = Person.objects.create(
        full_name="Jane Test",
        email="jane@example.com",
        email_consent=True,
    )
    person.groups.add(group)

    create_campaign_dry_run_logs(campaign)

    url = reverse(
        "campaign_confirm_send",
        kwargs={"campaign_id": campaign.id},
    )

    response = client.get(url)

    assert response.status_code == 200
    assert b"Confirm Campaign Send" in response.content
    assert b"jane@example.com" in response.content
    assert b"Real sending is currently disabled" in response.content


@pytest.mark.django_db
@override_settings(SEND_REAL_EMAILS=False, MAX_EMAILS_PER_DAY=300)
def test_real_send_post_blocked_when_disabled(client):
    group = Group.objects.create(name="Pickleball Players")

    campaign = Campaign.objects.create(
        title="June Newsletter",
        email_subject="June Updates",
        email_body="Hello.",
    )
    campaign.target_groups.add(group)

    person = Person.objects.create(
        full_name="Jane Test",
        email="jane@example.com",
        email_consent=True,
    )
    person.groups.add(group)

    create_campaign_dry_run_logs(campaign)

    url = reverse(
        "campaign_send_real_emails",
        kwargs={"campaign_id": campaign.id},
    )

    response = client.post(url)

    assert response.status_code == 302

    log = DeliveryLog.objects.get(
        campaign=campaign,
        person=person,
    )

    assert log.status == DeliveryLog.STATUS_PENDING