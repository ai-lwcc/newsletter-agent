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