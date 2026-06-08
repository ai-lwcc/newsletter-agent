from django.conf import settings
from django.utils import timezone

from core.email_provider import get_email_provider
from core.models import DeliveryLog


class RealEmailSendingDisabled(Exception):
    pass


class DailyEmailLimitExceeded(Exception):
    pass


def get_emails_sent_today_count():
    today = timezone.localdate()

    return DeliveryLog.objects.filter(
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_SENT,
        sent_at__date=today,
    ).count()


def send_pending_campaign_emails(campaign):
    if not settings.SEND_REAL_EMAILS:
        raise RealEmailSendingDisabled(
            "Real email sending is disabled. Set SEND_REAL_EMAILS=True to enable it."
        )

    pending_logs = DeliveryLog.objects.filter(
        campaign=campaign,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_PENDING,
    ).select_related("person")

    already_sent_today = get_emails_sent_today_count()
    remaining_today = settings.MAX_EMAILS_PER_DAY - already_sent_today

    if pending_logs.count() > remaining_today:
        raise DailyEmailLimitExceeded(
            f"Campaign has {pending_logs.count()} pending emails, "
            f"but only {remaining_today} sends remain today."
        )

    provider = get_email_provider()

    sent_count = 0
    failed_count = 0

    for log in pending_logs:
        try:
            provider.send_campaign_email(
                campaign,
                log.person,
            )

            log.mark_sent()
            sent_count += 1

        except Exception as error:
            log.mark_failed(str(error))
            failed_count += 1

    remaining_pending = DeliveryLog.objects.filter(
        campaign=campaign,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_PENDING,
    ).count()

    if remaining_pending == 0 and sent_count > 0:
        campaign.status = campaign.STATUS_SENT
        campaign.save(update_fields=["status", "updated_at"])

    return {
        "sent": sent_count,
        "failed": failed_count,
        "remaining_pending": remaining_pending,
    }