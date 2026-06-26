from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Campaign, DeliveryLog, Group, Person, CampaignAttachment, UserActionLog, ContactImport


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "created_at")
    search_fields = ("name",)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "whatsapp_number",
        "email_consent",
        "whatsapp_consent",
        "is_active",
    )
    list_filter = ("groups", "email_consent", "whatsapp_consent", "is_active")
    search_fields = ("full_name", "email", "whatsapp_number")
    filter_horizontal = ("groups",)


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "email_subject",
        "status",
        "preview_link",
        "automatically_send_when_due",
        "scheduled_send_time",
        "dry_run_completed_at",
        "primary_attachment",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "target_groups",
        "scheduled_send_time",
        "automatically_send_when_due",
    )

    search_fields = (
        "title",
        "email_subject",
        "email_body",
        "whatsapp_message",
    )

    filter_horizontal = ("target_groups",)

    readonly_fields = (
        "preview_page",
        "dry_run_completed_at",
    )

    fieldsets = (
        (
            "Campaign Content",
            {
                "fields": (
                    "title",
                    "email_subject",
                    "email_body",
                    "whatsapp_message",
                    "primary_attachment",
                    "target_groups",
                )
            },
        ),
        (
            "Sending Status",
            {
                "fields": (
                    "status",
                    "scheduled_send_time",
                    "automatically_send_when_due",
                    "dry_run_completed_at",
                    "preview_page",
                )
            },
        ),
    )

    def preview_link(self, obj):
        if not obj.id:
            return "-"

        url = reverse("campaign_preview", kwargs={"campaign_id": obj.id})
        return format_html('<a href="{}">Preview</a>', url)

    preview_link.short_description = "Preview"

    def preview_page(self, obj):
        if not obj.id:
            return "Save this campaign first to preview it."

        url = reverse("campaign_preview", kwargs={"campaign_id": obj.id})
        return format_html('<a href="{}">Open preview page</a>', url)

    preview_page.short_description = "Preview Page"


@admin.register(DeliveryLog)
class DeliveryLogAdmin(admin.ModelAdmin):
    list_display = (
        "campaign",
        "person",
        "channel",
        "status",
        "sent_at",
        "created_at",
    )

    list_filter = (
        "channel",
        "status",
        "campaign",
        "created_at",
        "sent_at",
    )

    search_fields = (
        "campaign__title",
        "person__full_name",
        "person__email",
        "person__whatsapp_number",
        "error_message",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 50

    autocomplete_fields = (
        "campaign",
        "person",
    )

    readonly_fields = (
        "campaign",
        "person",
        "channel",
        "status",
        "error_message",
        "sent_at",
        "created_at",
        "updated_at",
    )

@admin.register(CampaignAttachment)
class CampaignAttachmentAdmin(admin.ModelAdmin):
    list_display = ("campaign", "file", "uploaded_at")
    search_fields = ("campaign__title", "file")

@admin.register(UserActionLog)
class UserActionLogAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "user",
        "campaign",
        "action",
    )

    list_filter = (
        "action",
        "created_at",
    )

    search_fields = (
        "user__username",
        "campaign__title",
        "action",
    )

    readonly_fields = (
        "user",
        "campaign",
        "action",
        "details",
        "created_at",
    )

    ordering = ("-created_at",)
    list_per_page = 50

@admin.register(ContactImport)
class ContactImportAdmin(admin.ModelAdmin):
    list_display = (
        "original_filename",
        "status",
        "created_by",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "original_filename",
        "error_message",
    )
    readonly_fields = (
        "preview_result",
        "import_result",
        "error_message",
        "created_at",
        "updated_at",
    )