# WhatsApp Workflow

WhatsApp message generation is currently supported.

Real WhatsApp sending is not implemented.

## Current Workflow

Upload Files
    ↓
AI Draft Generation
    ↓
Generate WhatsApp Message
    ↓
Staff Review
    ↓
Manual WhatsApp Distribution

## Generated Content

AI produces:

- English WhatsApp message
- Campaign summary
- Suggested target groups

## Future Plans

### Planned Features

- WhatsApp provider integration
- WhatsApp delivery logs
- Test WhatsApp messages
- Dry run support
- Real WhatsApp sending

### Candidate Providers

- Twilio
- Meta WhatsApp Business API
- Other approved providers

## Design Goal

Keep WhatsApp workflows separate from email workflows.

Email delivery tracking and WhatsApp delivery tracking should remain independent.