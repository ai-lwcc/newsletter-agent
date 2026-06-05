# Scheduling Architecture

The newsletter platform supports scheduled campaign delivery.

Components:

- Django
- Redis
- Celery
- Celery Beat

Flow:

Campaign
→ Scheduled Time
→ Celery Beat
→ Redis Queue
→ Celery Worker
→ Email Delivery Service

Benefits:

- Automatic sends
- Reliable retry behavior
- Future WhatsApp scheduling support

## Campaign Scheduling Fields

Campaigns use these fields for scheduled sending:

- scheduled_send_time
- automatically_send_when_due
- status

A campaign is due for automatic sending when:

- status is `scheduled`
- automatically_send_when_due is `true`
- scheduled_send_time is now or in the past

## Celery and Redis Setup

Redis is used as the broker for Celery.

Environment variables:

```env
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```
## Running Celery Beat

Celery Beat is the scheduler that triggers recurring background tasks.

Run Django:

```bash
python manage.py runserver
```

Run Celery Worker
```bash
celery -A config worker -l info
```

Run Celery Beat
```bash
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

Required Periodic Task

In Django Admin, create:

Name: Send due scheduled campaigns every minute
Task: core.tasks.send_due_scheduled_campaigns
Interval: every 1 minute
Enabled: true

## How to Schedule a Campaign in Admin

To schedule a campaign:

1. Create or edit a campaign.
2. Select target groups.
3. Run preview.
4. View recipients.
5. Create dry run delivery logs.
6. Set campaign status to `scheduled`.
7. Set `scheduled_send_time`.
8. Check `automatically_send_when_due`.
9. Save.

Celery Beat will check every minute and trigger due campaigns.