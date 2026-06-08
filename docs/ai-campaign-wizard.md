# AI Campaign Wizard

## Purpose

The AI Campaign Wizard lets an admin create a campaign directly from a PDF.

## Workflow

1. Admin opens the dashboard.
2. Admin clicks Create AI Campaign.
3. Admin uploads a PDF.
4. The app creates a Campaign record.
5. AI generates:
   - email_subject
   - email_body
   - whatsapp_message
   - ai_summary
   - ai_suggested_groups
6. Admin reviews the preview page.
7. Admin accepts AI suggested groups if appropriate.
8. Admin views recipients.
9. Admin creates a dry run.
10. Admin confirms send.

## Safety

The AI Campaign Wizard does not send emails.

The admin must still:

- review the preview page
- accept target groups
- create dry run logs
- confirm sending

## Scheduling During AI Campaign Creation

The AI Campaign Wizard allows the admin to optionally set:

- scheduled_send_time
- automatically_send_when_due

If both are provided, the campaign is created with status `scheduled`.

Safety rule:

Even if automatic sending is enabled, the campaign will not send until dry-run delivery logs exist.