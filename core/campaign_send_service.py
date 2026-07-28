import logging
import time
import random
from django.conf import settings
from django.utils import timezone

from core.email_provider import get_email_provider
from core.models import DeliveryLog


logger = logging.getLogger(__name__)


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
    logger.info(
        "Real email send requested for campaign_id=%s title=%s",
        campaign.id,
        campaign.title,
    )

    if not settings.SEND_REAL_EMAILS:
        logger.warning(
            "Real email sending blocked because SEND_REAL_EMAILS=False "
            "campaign_id=%s",
            campaign.id,
        )

        raise RealEmailSendingDisabled(
            "Real email sending is disabled. Set SEND_REAL_EMAILS=True to enable it."
        )

    pending_logs = DeliveryLog.objects.filter(
        campaign=campaign,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_PENDING,
    ).select_related("person")

    pending_count = pending_logs.count()
    already_sent_today = get_emails_sent_today_count()
    remaining_today = settings.MAX_EMAILS_PER_DAY - already_sent_today

    logger.info(
        (
            "Campaign email send count check campaign_id=%s "
            "pending_count=%s already_sent_today=%s remaining_today=%s"
        ),
        campaign.id,
        pending_count,
        already_sent_today,
        remaining_today,
    )

    if pending_count > remaining_today:
        logger.warning(
            (
                "Daily email limit exceeded campaign_id=%s "
                "pending_count=%s remaining_today=%s"
            ),
            campaign.id,
            pending_count,
            remaining_today,
        )

        raise DailyEmailLimitExceeded(
            f"Campaign has {pending_count} pending emails, "
            f"but only {remaining_today} sends remain today."
        )

    provider = get_email_provider()

    sent_count = 0
    failed_count = 0

    send_delay_seconds = getattr(
        settings,
        "EMAIL_SEND_DELAY_SECONDS",
        0,
    )

    logger.info(
        "Email send delay configured campaign_id=%s delay_seconds=%s",
        campaign.id,
        send_delay_seconds,
    )

    for log in pending_logs:
        try:
            provider.send_campaign_email(
                campaign,
                log.person,
            )

            log.mark_sent()
            sent_count += 1

            logger.info(
                (
                    "Campaign email sent campaign_id=%s "
                    "delivery_log_id=%s person_id=%s"
                ),
                campaign.id,
                log.id,
                log.person_id,
            )

            if send_delay_seconds > 0:
                logger.info(
                    (
                        "Waiting before next email campaign_id=%s "
                        "delay_seconds=%s"
                    ),
                    campaign.id,
                    send_delay_seconds,
                )

                minimum_delay = getattr(settings, "EMAIL_SEND_DELAY_MIN_SECONDS", 20)
                maximum_delay = getattr(settings, "EMAIL_SEND_DELAY_MAX_SECONDS", 30)

                delay_seconds = random.randint(
                    minimum_delay,
                    maximum_delay,
                )

                time.sleep(delay_seconds)

        except Exception as error:
            log.mark_failed(str(error))
            failed_count += 1

            logger.exception(
                (
                    "Campaign email failed campaign_id=%s "
                    "delivery_log_id=%s person_id=%s error=%s"
                ),
                campaign.id,
                log.id,
                log.person_id,
                error,
            )

    remaining_pending = DeliveryLog.objects.filter(
        campaign=campaign,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_PENDING,
    ).count()

    if remaining_pending == 0 and sent_count > 0:
        campaign.status = campaign.STATUS_SENT
        campaign.save(update_fields=["status", "updated_at"])

        logger.info(
            "Campaign marked as sent campaign_id=%s sent_count=%s failed_count=%s",
            campaign.id,
            sent_count,
            failed_count,
        )

    logger.info(
        (
            "Real email send completed campaign_id=%s "
            "sent_count=%s failed_count=%s remaining_pending=%s"
        ),
        campaign.id,
        sent_count,
        failed_count,
        remaining_pending,
    )

    return {
        "sent": sent_count,
        "failed": failed_count,
        "remaining_pending": remaining_pending,
    }