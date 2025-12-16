#!/bin/bash
#
# Daily Backup Script - Zeus to OMV (Parallel Version)
# Runs daily at 3:00 AM
# Syncs Zeus sources to OMV via parallel rsync workers
#
# This script delegates to the parallel launcher system for faster backups
#

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Launcher script location
LAUNCHER_SCRIPT="${SCRIPT_DIR}/backup_parallel_launcher.sh"
if [ ! -f "${LAUNCHER_SCRIPT}" ]; then
    echo "ERROR: Parallel launcher script not found: ${LAUNCHER_SCRIPT}"
    exit 2
fi

# Run the parallel launcher
exec "${LAUNCHER_SCRIPT}"
