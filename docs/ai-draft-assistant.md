# AI Draft Assistant

## Purpose

The AI Draft Assistant helps create campaign content from an uploaded PDF.

## Workflow

1. Admin uploads PDF.
2. Admin clicks Generate AI Draft.
3. AI extracts and summarizes PDF text.
4. AI fills:
   - email_subject
   - email_body
   - whatsapp_message
5. AI suggests target groups.
6. Admin reviews preview page.
7. Admin accepts suggested groups if appropriate.
8. Admin edits if needed.
9. Admin runs dry run.
10. Admin confirms send.

## Safety Rules

The AI cannot:

- send emails
- bypass preview
- bypass dry run
- bypass confirm send
- silently finalize recipient groups

AI group choices are only suggestions until a human accepts them.