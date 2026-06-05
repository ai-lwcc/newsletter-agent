from celery import shared_task


@shared_task
def debug_celery_task():
    return "Celery is working"