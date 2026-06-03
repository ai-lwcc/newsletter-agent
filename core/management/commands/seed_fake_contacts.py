from django.core.management.base import BaseCommand

from core.models import Group, Person


class Command(BaseCommand):
    help = "Create fake sample groups and contacts for development/testing."

    def handle(self, *args, **options):
        group_names = [
            "Pickleball Players",
            "Women’s Small Groups",
            "Sponsors",
            "Volunteers",
            "General Newsletter",
            "Staff",
            "Parents",
            "Youth",
        ]

        groups = {}

        for name in group_names:
            group, _created = Group.objects.get_or_create(name=name)
            groups[name] = group

        fake_people = [
            {
                "full_name": "Jane Test",
                "email": "jane@example.com",
                "whatsapp_number": "+14165550001",
                "email_consent": True,
                "whatsapp_consent": True,
                "groups": ["Pickleball Players", "General Newsletter"],
            },
            {
                "full_name": "John Sample",
                "email": "john@example.com",
                "whatsapp_number": "+14165550002",
                "email_consent": True,
                "whatsapp_consent": False,
                "groups": ["Sponsors"],
            },
            {
                "full_name": "Mary Demo",
                "email": "mary@example.com",
                "whatsapp_number": "+14165550003",
                "email_consent": False,
                "whatsapp_consent": True,
                "groups": ["Women’s Small Groups", "Volunteers"],
            },
        ]

        for data in fake_people:
            person, _created = Person.objects.get_or_create(
                email=data["email"],
                defaults={
                    "full_name": data["full_name"],
                    "whatsapp_number": data["whatsapp_number"],
                    "email_consent": data["email_consent"],
                    "whatsapp_consent": data["whatsapp_consent"],
                },
            )

            person.groups.set([groups[group_name] for group_name in data["groups"]])

        self.stdout.write(self.style.SUCCESS("Fake contacts created successfully."))