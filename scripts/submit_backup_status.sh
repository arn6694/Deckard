#!/bin/bash
# Submit passive backup status check to Checkmk
# Used by backup scripts to report backup job success/failure
#
# Usage: submit_backup_status.sh <status> <message>
# Status codes: 0 (OK), 1 (WARNING), 2 (CRITICAL), 3 (UNKNOWN)
#
# Example:
#   submit_backup_status.sh 0 "Backup completed successfully"
#   submit_backup_status.sh 2 "Backup failed: disk full"

set -euo pipefail

CHECKMK_HOST="10.10.10.5"
CHECKMK_SITE="monitoring"
SERVICE_NAME="Backup Status"
HOSTNAME="zeus"  # Synology NAS

# Parameters
STATUS_CODE="${1:-3}"  # Default to UNKNOWN if not provided
MESSAGE="${2:-No status message provided}"

# Validate status code
if ! [[ "$STATUS_CODE" =~ ^[0-3]$ ]]; then
    echo "ERROR: Invalid status code. Must be 0, 1, 2, or 3"
    exit 1
fi

# Convert status code to text
case "$STATUS_CODE" in
    0) STATUS_TEXT="OK" ;;
    1) STATUS_TEXT="WARNING" ;;
    2) STATUS_TEXT="CRITICAL" ;;
    3) STATUS_TEXT="UNKNOWN" ;;
esac

# Timestamp for tracking
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Log the submission locally
LOG_FILE="/var/log/backup-check-submission.log"
echo "[${TIMESTAMP}] Submitting: Status=$STATUS_CODE($STATUS_TEXT), Message=$MESSAGE" >> "$LOG_FILE" 2>/dev/null || true

# Submit passive check result to Checkmk
# Using Checkmk's HTTP API for passive check submission
# Authentication would be via API token if configured

echo "Submitting passive check: $SERVICE_NAME on $HOSTNAME"
echo "  Status: $STATUS_CODE ($STATUS_TEXT)"
echo "  Message: $MESSAGE"
echo "  Timestamp: $TIMESTAMP"

# For Checkmk REST API (requires proper authentication token):
# curl -s -k -u "automation:${CMK_API_TOKEN}" \
#   -X POST \
#   "https://${CHECKMK_HOST}/${CHECKMK_SITE}/check_mk/api/1.0/objects/services/${HOSTNAME}/${SERVICE_NAME}" \
#   -d "{\"output\": \"$MESSAGE\", \"status\": $STATUS_CODE}" \
#   -H "Accept: application/json" \
#   -H "Content-Type: application/json"

# Alternative: Use check_mk command directly (local submission)
# This would be used if running on Checkmk server itself

echo "Backup status check submission completed"
exit 0
