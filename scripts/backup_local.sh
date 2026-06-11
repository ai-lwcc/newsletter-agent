#!/bin/bash

set -e

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

mkdir -p backups/database
mkdir -p backups/media

pg_dump -U newsletter_user -h localhost newsletter_agent > \
"backups/database/newsletter_agent_${TIMESTAMP}.sql"

tar -czf \
"backups/media/media_${TIMESTAMP}.tar.gz" \
media/

echo "Backup complete: ${TIMESTAMP}"
