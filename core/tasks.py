from celery import shared_task
from django.utils import timezone
from core.campaign_send_service import (
    DailyEmailLimitExceeded,
    RealEmailSendingDisabled,
    send_pending_campaign_emails,
)
from core.scheduling_service import get_due_scheduled_campaigns
from core.models import Campaign
from core.ai_service import generate_campaign_ai_draft

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

@shared_task
def generate_campaign_ai_draft_task(campaign_id):
    campaign = Campaign.objects.get(id=campaign_id)

    try:
        campaign.ai_status = Campaign.AI_PROCESSING
        campaign.save(update_fields=["ai_status"])

        ai_result = generate_campaign_ai_draft(campaign)

        campaign.email_subject = ai_result.get(
            "email_subject",
            campaign.email_subject,
        )

        campaign.email_body = ai_result.get(
            "email_body",
            campaign.email_body,
        )

        campaign.whatsapp_message = ai_result.get(
            "whatsapp_message",
            campaign.whatsapp_message,
        )

        campaign.ai_summary = ai_result.get(
            "summary",
            "",
        )

        campaign.ai_suggested_groups = ai_result.get(
            "suggested_groups",
            [],
        )

        campaign.ai_generated_at = timezone.now()
        campaign.ai_review_required = True
        campaign.ai_status = Campaign.AI_COMPLETED

        campaign.save()

    except Exception:
        campaign.ai_status = Campaign.AI_FAILED
        campaign.save(update_fields=["ai_status"])

        raise