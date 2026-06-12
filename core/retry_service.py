import logging

from core.models import DeliveryLog

logger = logging.getLogger(__name__)


def retry_failed_campaign_emails(campaign):
    logger.info(
        "Retry failed emails started for campaign_id=%s",
        campaign.id,
    )

    failed_logs = DeliveryLog.objects.filter(
        campaign=campaign,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_FAILED,
    )

    failed_count = failed_logs.count()

    updated_count = failed_logs.update(
        status=DeliveryLog.STATUS_PENDING,
        error_message="",
    )

    logger.info(
        (
            "Retry failed emails completed "
            "campaign_id=%s "
            "failed_found=%s "
            "moved_to_pending=%s"
        ),
        campaign.id,
        failed_count,
        updated_count,
    )

    return {
        "retried": updated_count,
    }