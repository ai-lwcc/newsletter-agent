import pytest
from django.core.management import call_command
from django_celery_beat.models import PeriodicTask


@pytest.mark.django_db
def test_setup_periodic_tasks_command_creates_task():
    call_command("setup_periodic_tasks")

    task = PeriodicTask.objects.get(
        name="Send due scheduled campaigns every minute"
    )

    assert task.task == "core.tasks.send_due_scheduled_campaigns"
    assert task.enabled is True
    assert task.interval.every == 1