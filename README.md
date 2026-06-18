# Newsletter Agent

A local Django-based campaign management tool for creating, previewing, scheduling, and sending bilingual newsletter campaigns by email.

## Current Features

* Contact and group management
* Excel / Google Sheets contact import
* AI campaign creation from uploaded files
* Supports PDF, PNG, JPG, JPEG, and WEBP files
* Multiple campaign attachments
* AI-generated:

  * Email subject
  * English email body
  * Traditional Chinese email body
  * WhatsApp message draft
  * Suggested recipient groups
  * Internal summary
* Clickable cover image in email body
* Optional cover link URL
* PDF/image/file attachments in outgoing emails
* Test email sending
* Dry run delivery logs
* Real email sending through SMTP / Google Workspace
* Scheduled campaign sending with Celery and Redis
* AI processing through Ollama
* Staff preview and confirmation pages

## Tech Stack

* Python
* Django
* PostgreSQL
* Celery
* Redis
* Ollama
* PyMuPDF
* Pillow
* Tesseract OCR
* SMTP / Google Workspace

## Local Setup

Create and activate virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install system dependencies:

```bash
sudo apt install redis-server tesseract-ocr tesseract-ocr-eng tesseract-ocr-chi-tra
```

Run migrations:

```bash
python manage.py migrate
```

Create admin user:

```bash
python manage.py createsuperuser
```

## Required Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=newsletter_agent
DB_USER=newsletter_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@example.com

TEST_RECIPIENT_EMAIL=your-test-email@example.com
SEND_REAL_EMAILS=False
MAX_EMAILS_PER_DAY=2000

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

AI_MODEL=qwen3:8b
```

## Running the App

Terminal 1:

```bash
source .venv/bin/activate
python manage.py runserver
```

Terminal 2:

```bash
source .venv/bin/activate
celery -A config worker -l info
```

Terminal 3, for scheduled campaigns:

```bash
source .venv/bin/activate
celery -A config beat -l info
```

## Campaign Workflow

1. Create AI Campaign
2. Upload one or more campaign files
3. Add optional cover link URL
4. Choose AI writing settings
5. Generate AI draft
6. Review English and Traditional Chinese content
7. Accept suggested groups
8. Send test email
9. Create dry run
10. Confirm real send or schedule campaign

## Safety Notes

* Real sending is blocked unless `SEND_REAL_EMAILS=True`
* Dry run is blocked if required campaign information is missing
* Real send is blocked if campaign validation fails
* AI-generated content must be reviewed before sending
* Staff should always send a test email first

## Additional Features

### Campaign Management
- Campaign detail page
- Full campaign preview page
- Readiness checklist
- Delivery summary dashboard
- Recent audit activity panel

### Logging & Auditing
- Delivery log dashboard
- Audit log dashboard
- Filtering
- Pagination
- Sortable delivery log columns

### Testing Utilities
- Generate hundreds of fake recipients
- Bulk delete test recipients
- Local email testing support

### Security
- User action audit trail
- Rate limiting
- Permission checks
- Daily email send limits

## WhatsApp Sending Status

WhatsApp message generation exists, but real WhatsApp sending is not implemented yet.

Planned implementation:

* Add WhatsApp provider service
* Add WhatsApp delivery logs
* Add dry run support for WhatsApp
* Add test WhatsApp sending
* Add real WhatsApp sending with provider configuration
* Keep WhatsApp sending separate from email sending
