# Campaigns

## Purpose

Campaigns represent newsletter drafts that can later be previewed, sent, or scheduled.

## Fields

- title
- email_subject
- email_body
- whatsapp_message
- target_groups
- status
- created_at
- updated_at

## Status Values

- draft
- scheduled
- sent
- cancelled

## Current Phase

Campaigns can be created and edited in Django Admin.

PDF attachments, email previews, sending, and scheduling will be added in later phases.

## Campaign Attachments

Campaigns can include one uploaded PDF attachment.

Uploaded PDFs are stored in:

```txt
media/campaign_pdfs/
```

## Email Preview

Campaigns can be previewed before sending.

Preview URL format:

```txt
/campaigns/<campaign_id>/preview/
```

## Test Email Safety

During development, emails use Django's console email backend.

This means emails are printed in the terminal instead of being sent to real people.

Environment variables:

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=newsletter@example.com
TEST_RECIPIENT_EMAIL=your_email@example.com
```

## Scheduling Fields

Campaigns include:

- scheduled_send_time
- dry_run_completed_at

`schedule_send_time` will be used in a later scheduling phase.

`dry_run_completed_at` records when a dry run was last completed.

## Dry Run

Campaigns can create pending delivery logs before real sending.

Dry-run URL:

```txt
/campaigns/<campaign_id>/dry-run/
```

## Campaign Detail Page

Displays:

- Readiness status
- Delivery summary
- AI status
- Target groups
- Attachments
- Recent audit activity

## Full Preview

Displays:

- Subject
- English email
- Chinese email
- WhatsApp message
- Cover image