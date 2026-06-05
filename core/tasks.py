from celery import shared_task

from core.campaign_send_service import (
    DailyEmailLimitExceeded,
    RealEmailSendingDisabled,
    send_pending_campaign_emails,
)
from core.scheduling_service import get_due_scheduled_campaigns


@shared_task
def debug_celery_task():
    return "Celery is working"


@shared_task
def send_due_scheduled_campaigns():
    results = []

    due_campaigns = get_due_scheduled_campaigns()

    for campaign in due_campaigns:
        try:
            result = send_pending_campaign_emails(campaign)

            results.append(
                {
                    "campaign_id": campaign.id,
                    "title": campaign.title,
                    "sent": result["sent"],
                    "failed": result["failed"],
                    "status": "processed",
                }
            )

        except RealEmailSendingDisabled as error:
            results.append(
                {
                    "campaign_id": campaign.id,
                    "title": campaign.title,
                    "status": "blocked",
                    "error": str(error),
                }
            )

        except DailyEmailLimitExceeded as error:
            results.append(
                {
                    "campaign_id": campaign.id,
                    "title": campaign.title,
                    "status": "daily_limit_exceeded",
                    "error": str(error),
                }
            )

    return results