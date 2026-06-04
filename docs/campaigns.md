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

## PDF Attachments

Campaigns can include one uploaded PDF attachment.

Uploaded PDFs are stored in:

```txt
media/campaign_pdfs/