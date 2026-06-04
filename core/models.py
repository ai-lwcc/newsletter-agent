from django.db import models


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

    groups = models.ManyToManyField(Group, related_name="people", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

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

    title = models.CharField(max_length=200)
    email_subject = models.CharField(max_length=200)
    email_body = models.TextField(blank=True)
    whatsapp_message = models.TextField(blank=True)

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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title