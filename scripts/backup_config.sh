#!/bin/bash
#
# Backup Configuration File
# Shared configuration for parallel rsync backup system
#
# This file is sourced by backup_parallel_launcher.sh
# Do not execute directly
#

# Source directories on Zeus (10.10.10.2 - Synology NAS)
# Complete backup of all user data
BACKUP_SOURCES=(
    "/volume1/homes"
    "/volume1/docker"
    "/volume1/web"
    "/volume1/surveillance"
    "/volume1/Family"
    "/volume1/NetBackup"
    "/volume1/Movies"
    "/volume1/TV Shows"
    "/volume1/Tunes"
    "/volume1/web_packages"
)

# Destination path on OMV (10.10.10.23 - OpenMediaVault) - remote via SSH
# Each source will be backed up to its own persistent subdirectory
BACKUP_DEST="brian@10.10.10.23:/mnt/OMV2/zeus_backups"

# Parallel execution settings
# Number of simultaneous rsync jobs to run
PARALLEL_JOBS=4

# Rsync options
# -a: archive mode (preserves permissions, timestamps, etc.)
# -v: verbose output
# -z: compress during transfer
RSYNC_OPTIONS="-avz"

# Timeout for individual rsync jobs (2 hours)
TIMEOUT_SECONDS=7200

# Log directory for backup operations
LOG_LOCATION="/var/log/backup_parallel"

# Minimum free space required on destination (in GB)
MIN_FREE_SPACE_GB=50
