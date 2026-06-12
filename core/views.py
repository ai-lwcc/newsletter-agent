import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from core.attachment_cover_service import generate_attachment_cover_image
from core.audit_service import create_user_action_log
from core.rate_limit_helpers import safe_ratelimit
from core.tasks import generate_campaign_ai_draft_task

from .campaign_send_service import (
    DailyEmailLimitExceeded,
    RealEmailSendingDisabled,
    send_pending_campaign_emails,
)
from .dry_run_service import create_campaign_dry_run_logs
from .email_service import send_campaign_test_email
from .forms import AICampaignCreateForm
from .models import Campaign, CampaignAttachment, DeliveryLog, Group, UserActionLog
from .recipient_service import get_campaign_recipients
from .retry_service import retry_failed_campaign_emails
from .schedule_status_service import get_campaign_schedule_status


logger = logging.getLogger(__name__)


def health_check(request):
    return JsonResponse({"status": "ok"})


@login_required
def dashboard(request):
    campaign_list = Campaign.objects.all().order_by("-created_at")
    paginator = Paginator(campaign_list, 10)

    page_number = request.GET.get("page")
    campaigns = paginator.get_page(page_number)

    return render(
        request,
        "core/dashboard.html",
        {
            "campaigns": campaigns,
        },
    )


@login_required
def campaign_preview(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    return render(
        request,
        "core/campaign_preview.html",
        {
            "campaign": campaign,
        },
    )


@login_required
@safe_ratelimit(key="user", rate="5/h", block=True)
def send_campaign_test_email_view(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    send_campaign_test_email(campaign)

    create_user_action_log(
        user=request.user,
        campaign=campaign,
        action=UserActionLog.ACTION_TEST_EMAIL_SENT,
    )

    logger.info(
        "Test email sent",
        extra={
            "user_id": request.user.id,
            "username": request.user.username,
            "campaign_id": campaign.id,
        },
    )

    return render(
        request,
        "core/test_email_sent.html",
        {
            "campaign": campaign,
        },
    )


@login_required
def campaign_recipients(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    recipients = get_campaign_recipients(campaign)

    return render(
        request,
        "core/campaign_recipients.html",
        {
            "campaign": campaign,
            "recipients": recipients,
        },
    )


@login_required
def campaign_dry_run(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    if not campaign.email_subject:
        messages.error(request, "Add an email subject before creating a dry run.")
        logger.warning(
            "Dry run blocked: missing email subject",
            extra={
                "user_id": request.user.id,
                "username": request.user.username,
                "campaign_id": campaign.id,
            },
        )
        return redirect("campaign_preview", campaign_id=campaign.id)

    if not campaign.email_body:
        messages.error(request, "Add an English email body before creating a dry run.")
        logger.warning(
            "Dry run blocked: missing email body",
            extra={
                "user_id": request.user.id,
                "username": request.user.username,
                "campaign_id": campaign.id,
            },
        )
        return redirect("campaign_preview", campaign_id=campaign.id)

    if campaign.ai_review_required:
        messages.error(
            request,
            (
                "Please review and accept the AI suggested groups "
                "before creating a dry run."
            ),
        )
        logger.warning(
            "Dry run blocked: AI review required",
            extra={
                "user_id": request.user.id,
                "username": request.user.username,
                "campaign_id": campaign.id,
            },
        )
        return redirect("campaign_preview", campaign_id=campaign.id)

    if not campaign.target_groups.exists():
        messages.error(
            request,
            "Select at least one target group before creating a dry run.",
        )
        logger.warning(
            "Dry run blocked: no target groups",
            extra={
                "user_id": request.user.id,
                "username": request.user.username,
                "campaign_id": campaign.id,
            },
        )
        return redirect("campaign_preview", campaign_id=campaign.id)

    if not campaign.attachments.exists() and not campaign.primary_attachment:
        messages.error(
            request,
            "Add at least one campaign attachment before creating a dry run.",
        )
        logger.warning(
            "Dry run blocked: no attachments",
            extra={
                "user_id": request.user.id,
                "username": request.user.username,
                "campaign_id": campaign.id,
            },
        )
        return redirect("campaign_preview", campaign_id=campaign.id)

    result = create_campaign_dry_run_logs(campaign)

    create_user_action_log(
        user=request.user,
        campaign=campaign,
        action=UserActionLog.ACTION_DRY_RUN_CREATED,
        details={
            "created": result.get("created"),
            "existing": result.get("existing"),
            "recipients": result.get("recipients"),
        },
    )

    logger.info(
        "Dry run created",
        extra={
            "user_id": request.user.id,
            "username": request.user.username,
            "campaign_id": campaign.id,
            "logs_created": result.get("created"),
            "existing": result.get("existing"),
            "recipients": result.get("recipients"),
        },
    )

    logs = DeliveryLog.objects.filter(
        campaign=campaign,
        channel=DeliveryLog.CHANNEL_EMAIL,
    ).select_related("person")

    return render(
        request,
        "core/campaign_dry_run.html",
        {
            "campaign": campaign,
            "result": result,
            "logs": logs,
        },
    )


@login_required
def campaign_confirm_send(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    pending_logs = DeliveryLog.objects.filter(
        campaign=campaign,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_PENDING,
    ).select_related("person")

    sent_count = DeliveryLog.objects.filter(
        campaign=campaign,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_SENT,
    ).count()

    failed_count = DeliveryLog.objects.filter(
        campaign=campaign,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_FAILED,
    ).count()

    skipped_count = DeliveryLog.objects.filter(
        campaign=campaign,
        channel=DeliveryLog.CHANNEL_EMAIL,
        status=DeliveryLog.STATUS_SKIPPED,
    ).count()

    return render(
        request,
        "core/campaign_confirm_send.html",
        {
            "campaign": campaign,
            "pending_logs": pending_logs,
            "send_real_emails": settings.SEND_REAL_EMAILS,
            "max_emails_per_day": settings.MAX_EMAILS_PER_DAY,
            "sent_count": sent_count,
            "failed_count": failed_count,
            "skipped_count": skipped_count,
        },
    )


@login_required
@safe_ratelimit(key="user", rate="5/h", block=True)
def campaign_send_real_emails(request, campaign_id):
    if request.method != "POST":
        return redirect("campaign_confirm_send", campaign_id=campaign_id)

    campaign = get_object_or_404(Campaign, id=campaign_id)

    logger.info(
        "Real send requested",
        extra={
            "user_id": request.user.id,
            "username": request.user.username,
            "campaign_id": campaign.id,
        },
    )

    create_user_action_log(
        user=request.user,
        campaign=campaign,
        action=UserActionLog.ACTION_REAL_SEND_REQUESTED,
    )

    if campaign.ai_review_required:
        messages.error(
            request,
            "Please review and accept AI suggested groups before sending.",
        )
        logger.warning(
            "Real send blocked: AI review required",
            extra={
                "user_id": request.user.id,
                "username": request.user.username,
                "campaign_id": campaign.id,
            },
        )
        return redirect("campaign_confirm_send", campaign_id=campaign.id)

    if not campaign.email_subject:
        messages.error(request, "Cannot send campaign without an email subject.")
        logger.warning(
            "Real send blocked: missing email subject",
            extra={
                "user_id": request.user.id,
                "username": request.user.username,
                "campaign_id": campaign.id,
            },
        )
        return redirect("campaign_confirm_send", campaign_id=campaign.id)

    if not campaign.email_body:
        messages.error(
            request,
            "Cannot send campaign without an English email body.",
        )
        logger.warning(
            "Real send blocked: missing email body",
            extra={
                "user_id": request.user.id,
                "username": request.user.username,
                "campaign_id": campaign.id,
            },
        )
        return redirect("campaign_confirm_send", campaign_id=campaign.id)

    if not campaign.target_groups.exists():
        messages.error(
            request,
            "Cannot send campaign without at least one target group.",
        )
        logger.warning(
            "Real send blocked: no target groups",
            extra={
                "user_id": request.user.id,
                "username": request.user.username,
                "campaign_id": campaign.id,
            },
        )
        return redirect("campaign_confirm_send", campaign_id=campaign.id)

    if not campaign.attachments.exists() and not campaign.primary_attachment:
        messages.error(
            request,
            "Cannot send campaign without at least one attachment.",
        )
        logger.warning(
            "Real send blocked: no attachments",
            extra={
                "user_id": request.user.id,
                "username": request.user.username,
                "campaign_id": campaign.id,
            },
        )
        return redirect("campaign_confirm_send", campaign_id=campaign.id)

    try:
        result = send_pending_campaign_emails(campaign)

        logger.info(
            "Real send completed",
            extra={
                "user_id": request.user.id,
                "username": request.user.username,
                "campaign_id": campaign.id,
                "sent": result.get("sent"),
                "failed": result.get("failed"),
                "remaining_pending": result.get("remaining_pending"),
            },
        )

        messages.success(
            request,
            f"Send complete. Sent: {result['sent']}, Failed: {result['failed']}.",
        )

    except RealEmailSendingDisabled as error:
        logger.warning(
            "Real send blocked: real email sending disabled",
            extra={
                "user_id": request.user.id,
                "username": request.user.username,
                "campaign_id": campaign.id,
                "error": str(error),
            },
        )
        messages.error(request, str(error))

    except DailyEmailLimitExceeded as error:
        logger.warning(
            "Real send blocked: daily limit exceeded",
            extra={
                "user_id": request.user.id,
                "username": request.user.username,
                "campaign_id": campaign.id,
                "error": str(error),
            },
        )
        messages.error(request, str(error))

    return redirect("campaign_confirm_send", campaign_id=campaign.id)


@login_required
def campaign_retry_failed_emails(request, campaign_id):
    if request.method != "POST":
        return redirect("campaign_confirm_send", campaign_id=campaign_id)

    campaign = get_object_or_404(Campaign, id=campaign_id)

    result = retry_failed_campaign_emails(campaign)

    create_user_action_log(
        user=request.user,
        campaign=campaign,
        action=UserActionLog.ACTION_FAILED_EMAILS_RETRIED,
        details={
            "retried": result.get("retried"),
        },
    )

    logger.info(
        "Failed emails retried",
        extra={
            "user_id": request.user.id,
            "username": request.user.username,
            "campaign_id": campaign.id,
            "retried": result.get("retried"),
        },
    )

    messages.success(
        request,
        f"Retried failed emails. Moved to pending: {result['retried']}.",
    )

    return redirect("campaign_confirm_send", campaign_id=campaign.id)


@login_required
def campaign_schedule_status(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    status = get_campaign_schedule_status(campaign)

    return render(
        request,
        "core/campaign_schedule_status.html",
        {
            "campaign": campaign,
            "status": status,
        },
    )


@login_required
@safe_ratelimit(key="user", rate="5/h", block=True)
def campaign_generate_ai_draft(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    campaign.ai_status = Campaign.AI_PENDING
    campaign.save(update_fields=["ai_status"])

    generate_campaign_ai_draft_task.delay(campaign.id)

    create_user_action_log(
        user=request.user,
        campaign=campaign,
        action=UserActionLog.ACTION_AI_DRAFT_QUEUED,
    )

    logger.info(
        "AI draft queued",
        extra={
            "user_id": request.user.id,
            "username": request.user.username,
            "campaign_id": campaign.id,
        },
    )

    return redirect("campaign_preview", campaign_id=campaign.id)


@login_required
def campaign_accept_ai_groups(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    suggested_group_names = campaign.ai_suggested_groups or []

    groups = Group.objects.filter(
        name__in=suggested_group_names,
    )

    campaign.target_groups.set(groups)
    campaign.ai_review_required = False
    campaign.save(update_fields=["ai_review_required", "updated_at"])

    create_user_action_log(
        user=request.user,
        campaign=campaign,
        action=UserActionLog.ACTION_AI_GROUPS_ACCEPTED,
        details={
            "groups": suggested_group_names,
        },
    )

    logger.info(
        "AI suggested groups accepted",
        extra={
            "user_id": request.user.id,
            "username": request.user.username,
            "campaign_id": campaign.id,
            "group_count": groups.count(),
        },
    )

    return redirect("campaign_preview", campaign_id=campaign.id)


@login_required
@safe_ratelimit(key="user", rate="5/h", block=True)
def ai_campaign_create(request):
    if request.method == "POST":
        form = AICampaignCreateForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            uploaded_files = request.FILES.getlist("attachments")

            if not uploaded_files:
                messages.error(
                    request,
                    "Please upload at least one campaign file.",
                )
                logger.warning(
                    "AI campaign create blocked: no uploaded files",
                    extra={
                        "user_id": request.user.id,
                        "username": request.user.username,
                    },
                )
                return render(
                    request,
                    "core/ai_campaign_create.html",
                    {
                        "form": form,
                    },
                )

            title = form.cleaned_data.get("title") or "AI Generated Campaign"
            scheduled_send_time = form.cleaned_data.get("scheduled_send_time")
            automatically_send_when_due = form.cleaned_data.get(
                "automatically_send_when_due",
                False,
            )

            campaign_status = Campaign.STATUS_DRAFT

            if scheduled_send_time and automatically_send_when_due:
                campaign_status = Campaign.STATUS_SCHEDULED

            first_file = uploaded_files[0]

            campaign = Campaign.objects.create(
                title=title,
                email_subject="",
                email_body="",
                email_body_zh="",
                whatsapp_message="",
                primary_attachment=first_file,
                scheduled_send_time=scheduled_send_time,
                automatically_send_when_due=automatically_send_when_due,
                status=campaign_status,
                ai_status=Campaign.AI_PENDING,
                email_length=form.cleaned_data["email_length"],
                tone=form.cleaned_data["tone"],
                cover_link_url=form.cleaned_data.get("cover_link_url", ""),
            )

            for uploaded_file in uploaded_files:
                CampaignAttachment.objects.create(
                    campaign=campaign,
                    file=uploaded_file,
                )

            generate_attachment_cover_image(campaign)
            generate_campaign_ai_draft_task.delay(campaign.id)

            create_user_action_log(
                user=request.user,
                campaign=campaign,
                action=UserActionLog.ACTION_AI_CAMPAIGN_CREATED,
                details={
                    "attachment_count": len(uploaded_files),
                    "status": campaign.status,
                    "scheduled": bool(scheduled_send_time),
                    "automatically_send_when_due": automatically_send_when_due,
                },
            )

            logger.info(
                "AI campaign created",
                extra={
                    "user_id": request.user.id,
                    "username": request.user.username,
                    "campaign_id": campaign.id,
                    "attachment_count": len(uploaded_files),
                    "status": campaign.status,
                },
            )

            return redirect(
                "campaign_preview",
                campaign_id=campaign.id,
            )

        logger.warning(
            "AI campaign create form invalid",
            extra={
                "user_id": request.user.id,
                "username": request.user.username,
                "errors": form.errors.as_json(),
            },
        )

    else:
        form = AICampaignCreateForm()

    return render(
        request,
        "core/ai_campaign_create.html",
        {
            "form": form,
        },
    )


@login_required
def delivery_logs(request):
    logs = DeliveryLog.objects.select_related(
        "campaign",
        "person",
    ).order_by("-created_at")

    status = request.GET.get("status")
    channel = request.GET.get("channel")
    campaign_id = request.GET.get("campaign")

    if status:
        logs = logs.filter(status=status)

    if channel:
        logs = logs.filter(channel=channel)

    if campaign_id:
        logs = logs.filter(campaign_id=campaign_id)

    paginator = Paginator(logs, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    summary = {
        "total": logs.count(),
        "pending": logs.filter(status=DeliveryLog.STATUS_PENDING).count(),
        "sent": logs.filter(status=DeliveryLog.STATUS_SENT).count(),
        "failed": logs.filter(status=DeliveryLog.STATUS_FAILED).count(),
        "skipped": logs.filter(status=DeliveryLog.STATUS_SKIPPED).count(),
    }

    campaigns = Campaign.objects.all().order_by("-created_at")

    query_params = request.GET.copy()

    if "page" in query_params:
        query_params.pop("page")

    query_string = query_params.urlencode()

    return render(
        request,
        "core/delivery_logs.html",
        {
            "logs": page_obj,
            "summary": summary,
            "campaigns": campaigns,
            "selected_status": status,
            "selected_channel": channel,
            "selected_campaign": campaign_id,
            "query_string": query_string,
        },
    )

@login_required
def audit_logs(request):
    logs = UserActionLog.objects.select_related(
        "user",
        "campaign",
    ).order_by("-created_at")

    action = request.GET.get("action")
    campaign_id = request.GET.get("campaign")

    if action:
        logs = logs.filter(action=action)

    if campaign_id:
        logs = logs.filter(campaign_id=campaign_id)

    summary = {
        "total": logs.count(),
        "ai_campaign_created": logs.filter(
            action=UserActionLog.ACTION_AI_CAMPAIGN_CREATED,
        ).count(),
        "ai_draft_queued": logs.filter(
            action=UserActionLog.ACTION_AI_DRAFT_QUEUED,
        ).count(),
        "test_email_sent": logs.filter(
            action=UserActionLog.ACTION_TEST_EMAIL_SENT,
        ).count(),
        "dry_run_created": logs.filter(
            action=UserActionLog.ACTION_DRY_RUN_CREATED,
        ).count(),
        "real_send_requested": logs.filter(
            action=UserActionLog.ACTION_REAL_SEND_REQUESTED,
        ).count(),
        "failed_emails_retried": logs.filter(
            action=UserActionLog.ACTION_FAILED_EMAILS_RETRIED,
        ).count(),
        "ai_groups_accepted": logs.filter(
            action=UserActionLog.ACTION_AI_GROUPS_ACCEPTED,
        ).count(),
    }

    paginator = Paginator(logs, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    query_params = request.GET.copy()

    if "page" in query_params:
        query_params.pop("page")

    query_string = query_params.urlencode()

    campaigns = Campaign.objects.all().order_by("-created_at")

    return render(
        request,
        "core/audit_logs.html",
        {
            "logs": page_obj,
            "campaigns": campaigns,
            "action_choices": UserActionLog.ACTION_CHOICES,
            "selected_action": action,
            "selected_campaign": campaign_id,
            "query_string": query_string,
            "summary": summary,
        },
    )