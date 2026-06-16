from django.core.management.base import BaseCommand

from core.models import Group, Person


class Command(BaseCommand):
    help = "Delete test recipients from a specific group."

    def add_arguments(self, parser):
        parser.add_argument(
            "--group",
            type=str,
            default="Test Recipients",
        )

        parser.add_argument(
            "--delete-group",
            action="store_true",
        )

    def handle(self, *args, **options):
        group_name = options["group"]
        delete_group = options["delete_group"]

        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    f"Group '{group_name}' does not exist."
                )
            )
            return

        people = Person.objects.filter(
            groups=group,
        )

        count = people.count()

        people.delete()

        if delete_group:
            group.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {count} test recipients from '{group_name}'."
            )
        )