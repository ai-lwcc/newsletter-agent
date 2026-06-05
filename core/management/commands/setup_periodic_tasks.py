from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule, PeriodicTask


class Command(BaseCommand):
    help = "Create or update required Celery Beat periodic tasks."

    def handle(self, *args, **options):
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.MINUTES,
        )

        task, created = PeriodicTask.objects.update_or_create(
            name="Send due scheduled campaigns every minute",
            defaults={
                "interval": schedule,
                "task": "core.tasks.send_due_scheduled_campaigns",
                "enabled": True,
            },
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS("Created scheduled campaign periodic task.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("Updated scheduled campaign periodic task.")
            )