from openpyxl import Workbook

from django.core.management.base import BaseCommand

from core.models import Group


class Command(BaseCommand):
    help = "Export all contacts in a group to Excel"

    def add_arguments(self, parser):
        parser.add_argument("group_name")

    def handle(self, *args, **options):
        group = Group.objects.get(name=options["group_name"])

        workbook = Workbook()
        sheet = workbook.active

        sheet.append([
            "First Name",
            "Last Name",
            "Full Name",
            "Email",
        ])

        for person in (
            group.people.filter(
                email_consent=True,
                is_active=True,
            )
            .exclude(email="")
            .order_by("last_name", "first_name")
        ):

            sheet.append([
                person.first_name,
                person.last_name,
                person.full_name,
                person.email,
            ])

        filename = f"{group.name}.xlsx"

        workbook.save(filename)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {filename}"
            )
        )