from django.contrib import admin

from .models import Group, Person


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