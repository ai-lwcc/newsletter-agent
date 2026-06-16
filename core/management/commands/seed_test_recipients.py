from django.core.management.base import BaseCommand

from core.models import Group, Person


class Command(BaseCommand):
    help = "Create test recipients for campaign testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=100,
        )

        parser.add_argument(
            "--group",
            type=str,
            default="Test Recipients",
        )

        parser.add_argument(
            "--email-domain",
            type=str,
            default="example.com",
        )

    def handle(self, *args, **options):
        count = options["count"]
        group_name = options["group"]
        email_domain = options["email_domain"]

        group, _ = Group.objects.get_or_create(
            name=group_name,
        )

        created_count = 0

        for number in range(1, count + 1):
            email = f"testuser{number:04d}@{email_domain}"

            person, created = Person.objects.get_or_create(
                email=email,
                defaults={
                    "full_name": f"Test User {number:04d}",
                    "email_consent": True,
                    "whatsapp_number": f"+1416555{number:04d}",
                    "whatsapp_consent": True,
                    "is_active": True,
                },
            )

            person.groups.add(group)

            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_count} new test recipients in group '{group_name}'."
            )
        )