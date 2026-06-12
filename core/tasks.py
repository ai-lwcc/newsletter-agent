import logging

from celery import shared_task
from django.utils import timezone

from core.ai_service import generate_campaign_ai_draft
from core.campaign_send_service import (
    DailyEmailLimitExceeded,
    RealEmailSendingDisabled,
    send_pending_campaign_emails,
)
from core.models import Campaign
from core.scheduling_service import get_due_scheduled_campaigns


logger = logging.getLogger(__name__)


@shared_task
def debug_celery_task():
    logger.info("Debug Celery task executed.")
    return "Celery is working"


@shared_task
def send_due_scheduled_campaigns():
    logger.info("Scheduled campaign send task started.")

    results = []
    due_campaigns = get_due_scheduled_campaigns()

    logger.info(
        "Found %s due scheduled campaigns.",
        due_campaigns.count(),
    )

    for campaign in due_campaigns:
        logger.info(
            "Processing scheduled campaign %s: %s",
            campaign.id,
            campaign.title,
        )

        try:
            result = send_pending_campaign_emails(campaign)

            logger.info(
                "Scheduled campaign %s processed. Sent=%s Failed=%s",
                campaign.id,
                result["sent"],
                result["failed"],
            )

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
            logger.warning(
                "Scheduled campaign %s blocked because real email sending is disabled: %s",
                campaign.id,
                error,
            )

            results.append(
                {
                    "campaign_id": campaign.id,
                    "title": campaign.title,
                    "status": "blocked",
                    "error": str(error),
                }
            )

        except DailyEmailLimitExceeded as error:
            logger.warning(
                "Scheduled campaign %s blocked by daily email limit: %s",
                campaign.id,
                error,
            )

            results.append(
                {
                    "campaign_id": campaign.id,
                    "title": campaign.title,
                    "status": "daily_limit_exceeded",
                    "error": str(error),
                }
            )

        except Exception as error:
            logger.exception(
                "Unexpected error while processing scheduled campaign %s.",
                campaign.id,
            )

            results.append(
                {
                    "campaign_id": campaign.id,
                    "title": campaign.title,
                    "status": "failed",
                    "error": str(error),
                }
            )

    logger.info("Scheduled campaign send task finished.")

    return results


@shared_task
def generate_campaign_ai_draft_task(campaign_id):
    logger.info(
        "AI generation task started for campaign %s.",
        campaign_id,
    )

    campaign = Campaign.objects.get(id=campaign_id)

    try:
        campaign.ai_status = Campaign.AI_PROCESSING
        campaign.save(update_fields=["ai_status"])

        ai_result = generate_campaign_ai_draft(campaign)

        logger.info(
            "AI generation completed for campaign %s. Keys=%s",
            campaign.id,
            list(ai_result.keys()),
        )

        campaign.email_subject = ai_result.get(
            "email_subject",
            campaign.email_subject,
        )

        campaign.email_body = ai_result.get(
            "email_body",
            campaign.email_body,
        )

        campaign.email_body_zh = ai_result.get(
            "email_body_zh",
            "",
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

        campaign.save(
            update_fields=[
                "email_subject",
                "email_body",
                "email_body_zh",
                "whatsapp_message",
                "ai_summary",
                "ai_suggested_groups",
                "ai_generated_at",
                "ai_review_required",
                "ai_status",
                "updated_at",
            ]
        )

        logger.info(
            "AI draft saved successfully for campaign %s.",
            campaign.id,
        )

    except Exception as error:
        logger.exception(
            "AI generation failed for campaign %s.",
            campaign_id,
        )

        campaign.ai_status = Campaign.AI_FAILED
        campaign.ai_summary = f"AI generation failed: {error}"

        campaign.save(
            update_fields=[
                "ai_status",
                "ai_summary",
                "updated_at",
            ]
        )

        raise