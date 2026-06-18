# Email Safety

## Purpose

Real email sending is disabled by default.

This protects against accidentally sending newsletters to real contacts during development.

## Environment Variables

```env
SEND_REAL_EMAILS=False
MAX_EMAILS_PER_DAY=300
```
## Confirm Send Page

Real campaign sends must go through a confirmation page.

URL format:

```txt
/campaigns/<campaign_id>/confirm-send/
```
## Retry Failed Emails

Failed email delivery logs can be moved back to pending.

This does not send emails immediately.

It only prepares them to be retried by the normal send process.

## Current Safety Controls

AI Review Required

Dry Run Required

Rate Limits:
5 requests per hour

Daily Send Limit:
MAX_EMAILS_PER_DAY

Permission Checks:
Newsletter Managers only

Test Email Workflow:
Recommended before every send