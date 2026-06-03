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