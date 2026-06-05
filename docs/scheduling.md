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