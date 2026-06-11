# Backup and Restore Guide

## Overview

This project stores important data in two places:

1. PostgreSQL database
2. `media/` folder

Both must be backed up regularly.

The database contains:

* Contacts
* Groups
* Campaigns
* Delivery logs
* Scheduling information
* AI-generated content

The media folder contains:

* Campaign attachments
* Uploaded PDFs
* Uploaded images
* Cover images
* Generated assets

A complete backup requires both.

---

# Creating Backups

## Run the Backup Script

From the project root:

```bash
./scripts/backup_local.sh
```

This automatically creates:

```txt
backups/database/newsletter_agent_TIMESTAMP.sql
backups/media/media_TIMESTAMP.tar.gz
```

Example:

```txt
backups/database/newsletter_agent_2026-06-10_09-30-00.sql
backups/media/media_2026-06-10_09-30-00.tar.gz
```

---

# Manual Database Backup

If needed, create a PostgreSQL backup manually:

```bash
pg_dump newsletter_agent > backups/database/newsletter_agent_backup.sql
```

Or with a database user:

```bash
pg_dump -U newsletter_user newsletter_agent > backups/database/newsletter_agent_backup.sql
```

---

# Manual Media Backup

Create a backup of uploaded files:

```bash
tar -czf backups/media/media_backup.tar.gz media/
```

---

# Restoring the Database

Before restoring:

1. Stop Django
2. Stop Celery workers
3. Stop Celery Beat

Example:

```bash
pkill -f celery
```

Then restore the database:

```bash
psql -U newsletter_user newsletter_agent < backups/database/YOUR_BACKUP_FILE.sql
```

Example:

```bash
psql -U newsletter_user newsletter_agent < backups/database/newsletter_agent_2026-06-10_09-30-00.sql
```

---

# Restoring Media Files

Restore uploaded files:

```bash
tar -xzf backups/media/YOUR_MEDIA_BACKUP.tar.gz
```

Example:

```bash
tar -xzf backups/media/media_2026-06-10_09-30-00.tar.gz
```

This restores:

* Campaign attachments
* PDFs
* Images
* Cover images

---

# Full Disaster Recovery

If the server is completely lost:

## Step 1

Set up a new server.

Install:

* Python
* PostgreSQL
* Redis
* Tesseract OCR

## Step 2

Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
```

## Step 3

Create and activate virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

## Step 4

Install dependencies:

```bash
pip install -r requirements.txt
```

## Step 5

Create the `.env` file.

## Step 6

Create the database:

```bash
createdb newsletter_agent
```

## Step 7

Restore the database backup.

## Step 8

Restore the media backup.

## Step 9

Start Django, Celery worker, and Celery Beat.

The application should now be fully restored.

---

# Backup Frequency Recommendations

Recommended minimum:

```txt
Database: Daily
Media files: Daily
```

For active campaign periods:

```txt
Database: Before every campaign send
Media files: Daily
```

---

# Security Notes

Never commit backups to Git.

Ensure the following are ignored:

```txt
backups/
.env
media/
```

Store backups outside the repository whenever possible.

Consider keeping a second copy on:

* External drive
* Company file server
* Cloud storage

---

# Important Reminder

Database backups do not contain uploaded files.

Media backups do not contain contacts, campaigns, groups, or delivery logs.

Always back up both the PostgreSQL database and the media folder.

A backup is only considered complete when both have been successfully created.
