#!/bin/bash

BACKUP_DIR="/backups/adx-shares"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="adx_prod_db"
DB_USER="adx_prod_user"
BACKUP_FILE="${BACKUP_DIR}/backup_${DATE}.sql"

mkdir -p $BACKUP_DIR

echo "🔄 Starting database backup..."

docker exec adx_postgres_prod pg_dump -U $DB_USER $DB_NAME > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ Backup created: $BACKUP_FILE"
    gzip $BACKUP_FILE
    echo "✅ Compressed: ${BACKUP_FILE}.gz"
    
    # Delete backups older than 30 days
    find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
    echo "✅ Old backups cleaned"
else
    echo "❌ Backup failed"
    exit 1
fi