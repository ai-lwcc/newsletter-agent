from core.models import DeliveryLog


def retry_failed_campaign_emails(campaign):
    failed_logs = DeliveryLog.objects.filter(
        campaign=campaign,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_FAILED,
    )

    updated_count = failed_logs.update(
        status=DeliveryLog.STATUS_PENDING,
        error_message="",
    )

    return {
        "retried": updated_count,
    }