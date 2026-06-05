from django.contrib import admin

from .models import Campaign, DeliveryLog, Group, Person

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
        "scheduled_send_time",
        "dry_run_completed_at",
        "pdf_attachment",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "target_groups", "scheduled_send_time")
    search_fields = ("title", "email_subject", "email_body", "whatsapp_message")
    filter_horizontal = ("target_groups",)


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
    list_filter = ("channel", "status", "campaign")
    search_fields = (
        "campaign__title",
        "person__full_name",
        "person__email",
        "error_message",
    )