#!/bin/bash
#
# Backup Parallel Launcher Script - Simplified
# Launches parallel rsync backup jobs for speed
#
# Exit codes:
#   0 - All backups succeeded
#   1 - Partial success (some backups failed)
#   2 - Critical failure (all backups failed)
#

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source configuration
CONFIG_FILE="${SCRIPT_DIR}/backup_config.sh"
if [ ! -f "${CONFIG_FILE}" ]; then
    echo "ERROR: Configuration file not found: ${CONFIG_FILE}"
    exit 2
fi

source "${CONFIG_FILE}"

# Ensure log directory exists
mkdir -p "${LOG_LOCATION}"

TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
MASTER_LOG="${LOG_LOCATION}/master.log"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "${MASTER_LOG}"
}

# Start backup
log "=========================================="
log "Parallel Backup Starting"
log "Timestamp: ${TIMESTAMP}"
log "Destination: ${BACKUP_DEST}"
log "Parallel jobs: ${PARALLEL_JOBS}"
log "=========================================="

# Check sources exist
for src in "${BACKUP_SOURCES[@]}"; do
    if [ ! -d "${src}" ]; then
        log "ERROR: Source not found: ${src}"
        exit 2
    fi
done
log "Sources verified: ${#BACKUP_SOURCES[@]} directories"
log "=========================================="

# Arrays to track jobs
declare -a JOB_PIDS=()
declare -a JOB_SOURCES=()

# Rsync options with compression disabled for speed, partial for resumable transfers
RSYNC_OPTS="-av --partial --no-perms --no-group --no-owner --ignore-errors"

# Launch parallel rsync jobs
log "Launching rsync jobs (${#BACKUP_SOURCES[@]} total)..."

for src in "${BACKUP_SOURCES[@]}"; do
    SRC_NAME=$(basename "${src}")
    DST="${BACKUP_DEST}/${SRC_NAME}"

    log "Starting: ${src} -> ${SRC_NAME}/"

    # Run rsync in background with logging
    # SSH options: aggressive keep-alive, connection pooling, longer timeouts
    rsync ${RSYNC_OPTS} -e "ssh -o ServerAliveInterval=30 -o ServerAliveCountMax=10 -o ConnectTimeout=30 -o TCPKeepAlive=yes -o BatchMode=yes" "${src}/" "${DST}/" >> "${LOG_LOCATION}/${SRC_NAME}_${TIMESTAMP}.log" 2>&1 &
    RSYNC_PID=$!

    JOB_PIDS+=("${RSYNC_PID}")
    JOB_SOURCES+=("${src}")
done

log "All ${#JOB_SOURCES[@]} jobs launched"
log "=========================================="

# Wait for all jobs to complete and collect exit codes
log "Waiting for all jobs to complete..."
declare -a JOB_EXIT_CODES=()
SUCCESS_COUNT=0
FAILED_COUNT=0

for i in "${!JOB_PIDS[@]}"; do
    PID="${JOB_PIDS[$i]}"
    SRC="${JOB_SOURCES[$i]}"
    SRC_NAME=$(basename "${SRC}")

    wait "${PID}"
    EXIT_CODE=$?
    JOB_EXIT_CODES+=("${EXIT_CODE}")

    if [ ${EXIT_CODE} -eq 0 ]; then
        log "✓ SUCCESS: ${SRC_NAME}"
        ((SUCCESS_COUNT++))
    else
        log "✗ FAILED:  ${SRC_NAME} (exit code: ${EXIT_CODE})"
        ((FAILED_COUNT++))
    fi
done

# Summary
log "=========================================="
log "Backup Summary"
log "=========================================="
log "Total sources:  ${#JOB_SOURCES[@]}"
log "Successful:     ${SUCCESS_COUNT}"
log "Failed:         ${FAILED_COUNT}"
log "=========================================="

# Exit code
if [ ${SUCCESS_COUNT} -eq ${#JOB_SOURCES[@]} ]; then
    log "✓ All backups completed successfully"
    exit 0
elif [ ${SUCCESS_COUNT} -gt 0 ]; then
    log "⚠ Partial success"
    exit 1
else
    log "✗ All backups failed"
    exit 2
fi
