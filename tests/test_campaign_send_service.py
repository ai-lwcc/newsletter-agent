import pytest
from django.core import mail
from django.test import override_settings

from core.campaign_send_service import (
    DailyEmailLimitExceeded,
    RealEmailSendingDisabled,
    send_pending_campaign_emails,
)
from core.dry_run_service import create_campaign_dry_run_logs
from core.models import Campaign, DeliveryLog, Group, Person


@pytest.mark.django_db
def test_send_pending_campaign_emails_blocked_when_disabled():
    campaign = Campaign.objects.create(
        title="June Newsletter",
        email_subject="June Updates",
        email_body="Hello everyone.",
    )

    with override_settings(SEND_REAL_EMAILS=False):
        with pytest.raises(RealEmailSendingDisabled):
            send_pending_campaign_emails(campaign)


@pytest.mark.django_db
@override_settings(
    SEND_REAL_EMAILS=True,
    MAX_EMAILS_PER_DAY=300,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="newsletter@example.com",
)
def test_send_pending_campaign_emails_marks_logs_sent():
    group = Group.objects.create(name="Pickleball Players")

    campaign = Campaign.objects.create(
        title="June Newsletter",
        email_subject="June Updates",
        email_body="Hello everyone.",
    )
    campaign.target_groups.add(group)

    person = Person.objects.create(
        full_name="Jane Test",
        email="jane@example.com",
        email_consent=True,
    )
    person.groups.add(group)

    create_campaign_dry_run_logs(campaign)

    result = send_pending_campaign_emails(campaign)

    log = DeliveryLog.objects.get(
        campaign=campaign,
        person=person,
        channel=DeliveryLog.CHANNEL_EMAIL,
    )

    assert result["sent"] == 1
    assert result["failed"] == 0
    assert log.status == DeliveryLog.STATUS_SENT
    assert log.sent_at is not None
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["jane@example.com"]


@pytest.mark.django_db
@override_settings(
    SEND_REAL_EMAILS=True,
    MAX_EMAILS_PER_DAY=0,
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
def test_send_pending_campaign_emails_respects_daily_limit():
    group = Group.objects.create(name="Pickleball Players")

    campaign = Campaign.objects.create(
        title="June Newsletter",
        email_subject="June Updates",
        email_body="Hello everyone.",
    )
    campaign.target_groups.add(group)

    person = Person.objects.create(
        full_name="Jane Test",
        email="jane@example.com",
        email_consent=True,
    )
    person.groups.add(group)

    create_campaign_dry_run_logs(campaign)

    with pytest.raises(DailyEmailLimitExceeded):
        send_pending_campaign_emails(campaign)