import pytest

from core.models import Campaign, DeliveryLog, Person


@pytest.mark.django_db
def test_create_delivery_log():
    campaign = Campaign.objects.create(
        title="June Newsletter",
        email_subject="June Updates",
    )

    person = Person.objects.create(
        full_name="Jane Test",
        email="jane@example.com",
        email_consent=True,
    )

    log = DeliveryLog.objects.create(
        campaign=campaign,
        person=person,
        channel=DeliveryLog.CHANNEL_EMAIL,
    )

    assert log.status == DeliveryLog.STATUS_PENDING
    assert str(log) == "June Newsletter -> Jane Test (email)"


@pytest.mark.django_db
def test_delivery_log_mark_sent():
    campaign = Campaign.objects.create(
        title="June Newsletter",
        email_subject="June Updates",
    )

    person = Person.objects.create(
        full_name="Jane Test",
        email="jane@example.com",
        email_consent=True,
    )

    log = DeliveryLog.objects.create(
        campaign=campaign,
        person=person,
        channel=DeliveryLog.CHANNEL_EMAIL,
    )

    log.mark_sent()

    assert log.status == DeliveryLog.STATUS_SENT
    assert log.sent_at is not None


@pytest.mark.django_db
def test_delivery_log_mark_failed():
    campaign = Campaign.objects.create(
        title="June Newsletter",
        email_subject="June Updates",
    )

    person = Person.objects.create(
        full_name="Jane Test",
        email="jane@example.com",
        email_consent=True,
    )

    log = DeliveryLog.objects.create(
        campaign=campaign,
        person=person,
        channel=DeliveryLog.CHANNEL_EMAIL,
    )

    log.mark_failed("SMTP error")

    assert log.status == DeliveryLog.STATUS_FAILED
    assert log.error_message == "SMTP error"