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