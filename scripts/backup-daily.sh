#!/bin/bash
#
# Daily Backup Script - Zeus to OMV
# Runs daily at 3:00 AM
# Retention: 7 days
# Creates daily incremental backups with hard-link deduplication
#

set -euo pipefail

# Configuration
# For Synology NAS backup, include important directories
BACKUP_SOURCES=(
    "/volume1/homes"
    "/volume1/docker"
    "/volume1/web"
    "/volume1/surveillance"
    "/volume1/Family"
    "/volume1/NetBackup"
)
BACKUP_DEST="/mnt/omv_backup/zeus_backups"
LOG_FILE="/var/log/backup-daily.log"
RETENTION_DAYS=7
BACKUP_TYPE="daily"
DATE=$(date '+%Y-%m-%d')
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
BACKUP_NAME="${DATE}_${BACKUP_TYPE}"

# Ensure backup destination exists
mkdir -p "${BACKUP_DEST}"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

# Error handler
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Start backup
log "=========================================="
log "Daily Backup Starting (${TIMESTAMP})"
log "Destination: ${BACKUP_DEST}/${BACKUP_NAME}"
log "Retention: ${RETENTION_DAYS} days"
log "Sources to backup:"
for src in "${BACKUP_SOURCES[@]}"; do
    log "  - ${src}"
done

# Verify at least one source exists
VALID_SOURCES=0
for src in "${BACKUP_SOURCES[@]}"; do
    if [ -d "${src}" ]; then
        ((VALID_SOURCES++))
    else
        log "WARNING: Source directory not found: ${src}"
    fi
done

if [ ${VALID_SOURCES} -eq 0 ]; then
    error_exit "No valid source directories found"
fi

# Verify destination is mounted and writable
if ! touch "${BACKUP_DEST}/.write_test" 2>/dev/null; then
    error_exit "Destination is not writable: ${BACKUP_DEST}"
fi
rm -f "${BACKUP_DEST}/.write_test"

# Create backup directory
CURRENT_BACKUP="${BACKUP_DEST}/${BACKUP_NAME}"
if [ -d "${CURRENT_BACKUP}" ]; then
    log "WARNING: Backup directory already exists, removing: ${CURRENT_BACKUP}"
    rm -rf "${CURRENT_BACKUP}"
fi
mkdir -p "${CURRENT_BACKUP}"

# Get previous backup for hard-link deduplication (for incremental backup)
PREVIOUS_BACKUP=""
if [ -d "${BACKUP_DEST}" ]; then
    PREVIOUS_BACKUP=$(find "${BACKUP_DEST}" -maxdepth 1 -type d -name "*_daily" ! -name "${BACKUP_NAME}" -printf '%T@ %p\n' | sort -rn | head -1 | cut -d' ' -f2-)
fi

# Perform rsync backup with hard-link deduplication for each source
RSYNC_OPTIONS="-avz --delete"
TOTAL_ERRORS=0

if [ -n "${PREVIOUS_BACKUP}" ] && [ -d "${PREVIOUS_BACKUP}" ]; then
    log "Incremental backup using: ${PREVIOUS_BACKUP}"
    RSYNC_OPTIONS="${RSYNC_OPTIONS} --link-dest=${PREVIOUS_BACKUP}"
fi

log "Starting rsync with options: ${RSYNC_OPTIONS}"

for src in "${BACKUP_SOURCES[@]}"; do
    if [ ! -d "${src}" ]; then
        log "Skipping ${src} (not found)"
        continue
    fi

    # Create subdirectory for each source
    SRC_NAME=$(basename "${src}")
    DST_DIR="${CURRENT_BACKUP}/${SRC_NAME}"
    mkdir -p "${DST_DIR}"

    log "Backing up: ${src} -> ${SRC_NAME}/"
    if ! rsync ${RSYNC_OPTIONS} "${src}/" "${DST_DIR}/" >> "${LOG_FILE}" 2>&1; then
        log "WARNING: rsync failed for ${src}"
        ((TOTAL_ERRORS++))
    fi
done

if [ ${TOTAL_ERRORS} -gt 0 ]; then
    log "WARNING: ${TOTAL_ERRORS} backup(s) had errors"
fi

BACKUP_SIZE=$(du -sh "${CURRENT_BACKUP}" 2>/dev/null | cut -f1)
BACKUP_FILES=$(find "${CURRENT_BACKUP}" -type f 2>/dev/null | wc -l)
log "Backup completed"
log "Backup size: ${BACKUP_SIZE}"
log "File count: ${BACKUP_FILES}"

# Cleanup old backups (keep only RETENTION_DAYS)
log "Cleaning up backups older than ${RETENTION_DAYS} days"
RETENTION_DATE=$(date -d "${RETENTION_DAYS} days ago" '+%Y-%m-%d')
find "${BACKUP_DEST}" -maxdepth 1 -type d -name "*_daily" -newer "${BACKUP_DEST}" | while read -r old_backup; do
    BACKUP_DATE=$(basename "${old_backup}" | cut -d'_' -f1)
    if [[ "${BACKUP_DATE}" < "${RETENTION_DATE}" ]]; then
        log "Removing old backup: ${old_backup}"
        rm -rf "${old_backup}"
    fi
done

log "Daily backup completed successfully"
log "=========================================="
