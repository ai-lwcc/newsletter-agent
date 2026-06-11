from django.db import models
from django.utils import timezone


class Group(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Person(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    whatsapp_number = models.CharField(max_length=30, blank=True)

    email_consent = models.BooleanField(default=False)
    whatsapp_consent = models.BooleanField(default=False)

    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    groups = models.ManyToManyField(
        Group,
        related_name="people",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["whatsapp_number"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.full_name


class Campaign(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_SCHEDULED = "scheduled"
    STATUS_SENT = "sent"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_SENT, "Sent"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    AI_PENDING = "pending"
    AI_PROCESSING = "processing"
    AI_COMPLETED = "completed"
    AI_FAILED = "failed"

    AI_STATUS_CHOICES = [
        (AI_PENDING, "Pending"),
        (AI_PROCESSING, "Processing"),
        (AI_COMPLETED, "Completed"),
        (AI_FAILED, "Failed"),
    ]

    title = models.CharField(max_length=200)
    email_subject = models.CharField(max_length=200)
    email_body = models.TextField(blank=True)
    email_body_zh = models.TextField(blank=True)
    whatsapp_message = models.TextField(blank=True)

    primary_attachment = models.FileField(
        upload_to="campaign_pdfs/",
        blank=True,
        null=True,
    )

    cover_link_url = models.URLField(blank=True)

    cover_image = models.ImageField(
        upload_to="campaign_covers/",
        blank=True,
        null=True,
    )

    target_groups = models.ManyToManyField(
        Group,
        related_name="campaigns",
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )

    scheduled_send_time = models.DateTimeField(
        null=True,
        blank=True,
    )

    automatically_send_when_due = models.BooleanField(
        default=False,
    )

    dry_run_completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    ai_summary = models.TextField(blank=True)

    ai_suggested_groups = models.JSONField(
        default=list,
        blank=True,
    )

    ai_generated_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    ai_review_required = models.BooleanField(
        default=False,
    )

    ai_status = models.CharField(
        max_length=20,
        choices=AI_STATUS_CHOICES,
        default=AI_PENDING,
    )

    email_length = models.CharField(
        max_length=20,
        default="short",
    )

    tone = models.CharField(
        max_length=20,
        default="professional",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["scheduled_send_time"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.title


class CampaignAttachment(models.Model):
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="attachments",
    )

    file = models.FileField(
        upload_to="campaign_attachments/",
    )

    cover_image = models.ImageField(
        upload_to="campaign_covers/",
        blank=True,
        null=True,
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name


class DeliveryLog(models.Model):
    CHANNEL_EMAIL = "email"
    CHANNEL_WHATSAPP = "whatsapp"

    CHANNEL_CHOICES = [
        (CHANNEL_EMAIL, "Email"),
        (CHANNEL_WHATSAPP, "WhatsApp"),
    ]

    STATUS_PENDING = "pending"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    STATUS_SKIPPED = "skipped"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SENT, "Sent"),
        (STATUS_FAILED, "Failed"),
        (STATUS_SKIPPED, "Skipped"),
    ]

    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name="delivery_logs",
    )

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="delivery_logs",
    )

    channel = models.CharField(
        max_length=20,
        choices=CHANNEL_CHOICES,
        default=CHANNEL_EMAIL,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    error_message = models.TextField(blank=True)

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("campaign", "person", "channel")
        indexes = [
            models.Index(fields=["campaign", "channel", "status"]),
            models.Index(fields=["status", "sent_at"]),
            models.Index(fields=["person", "campaign"]),
        ]

    def mark_sent(self):
        self.status = self.STATUS_SENT
        self.sent_at = timezone.now()
        self.save(update_fields=["status", "sent_at", "updated_at"])

    def mark_failed(self, error_message):
        self.status = self.STATUS_FAILED
        self.error_message = error_message
        self.save(update_fields=["status", "error_message", "updated_at"])

    def __str__(self):
        return f"{self.campaign.title} -> {self.person.full_name} ({self.channel})"