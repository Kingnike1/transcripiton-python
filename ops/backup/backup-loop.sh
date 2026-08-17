#!/bin/sh
set -eu

BACKUP_INTERVAL_SECONDS="${BACKUP_INTERVAL_SECONDS:-86400}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-14}"
POSTGRES_HOST="${POSTGRES_HOST:-db}"
POSTGRES_DB="${POSTGRES_DB:-amip}"
POSTGRES_USER="${POSTGRES_USER:-amip}"

mkdir -p /backups/database /backups/storage

while true; do
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  pg_dump -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc -f "/backups/database/amip-$stamp.dump"
  tar -czf "/backups/storage/amip-storage-$stamp.tar.gz" -C /data storage
  find /backups/database /backups/storage -type f -mtime "+$BACKUP_RETENTION_DAYS" -delete
  sleep "$BACKUP_INTERVAL_SECONDS"
done
