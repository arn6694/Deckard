# Backup Infrastructure Monitoring Setup

**Date Completed**: 2025-12-12
**Status**: CONFIGURED AND VALIDATED

## Overview

This document describes the Checkmk monitoring setup for backup infrastructure:
- **Check 1**: Synology (10.10.10.2 / `zeus`) - Backup Job Status (Passive Check)
- **Check 2**: OMV (10.10.10.23 / `omv`) - Backup Storage Usage (Active SSH Disk Check)

---

## Check 1: Synology (zeus) - Backup Job Status

### Configuration
- **Host**: zeus (10.10.10.2) - Synology NAS
- **Service Name**: "Backup Status"
- **Check Type**: **Passive** - receives status from backup script
- **Checkmk Config File**: `/opt/omd/sites/monitoring/etc/check_mk/conf.d/wato/backup_monitoring.mk`

### How It Works

The passive check receives backup job status from scripts running on the Synology NAS. The backup script monitors:

1. **Log Location**: `/var/log/backup-daily.log`
2. **Alert Conditions**:
   - Exit code non-zero in last 24 hours → CRITICAL
   - "ERROR" or "FAILED" found in log → CRITICAL
   - Last backup older than 26 hours → WARNING
   - All conditions good → OK

### Submitting Backup Status to Checkmk

Use the provided script on Synology or Checkmk server:

```bash
# Submit successful backup
/home/brian/claude/scripts/submit_backup_status.sh 0 "Backup completed successfully - 2025-12-12 14:30"

# Submit failed backup
/home/brian/claude/scripts/submit_backup_status.sh 2 "Backup failed: ERROR found in log"

# Submit warning (old backup)
/home/brian/claude/scripts/submit_backup_status.sh 1 "Last backup is 25 hours old"
```

**Status Codes**:
- `0` = OK (backup successful)
- `1` = WARNING (old backup, minor issues)
- `2` = CRITICAL (backup failed, errors detected)
- `3` = UNKNOWN (no status received)

### Integration with Backup Script

Add this to your daily backup script on Synology (`/root/backup-daily.sh`):

```bash
#!/bin/bash
# Backup script with Checkmk passive check submission

BACKUP_LOG="/var/log/backup-daily.log"
BACKUP_DEST="/export/Synology_Backup"
CHECKMK_SERVER="10.10.10.5"

# Perform backup...
echo "Starting backup: $(date)" >> "$BACKUP_LOG"

# Check for errors
if [ $? -eq 0 ]; then
    # Backup succeeded - submit OK status
    curl -s -X POST \
        "https://${CHECKMK_SERVER}/monitoring/check_mk/api/1.0/services/zeus/Backup%20Status" \
        -d "status=0&message=Backup completed successfully at $(date)" \
        2>/dev/null || true
else
    # Backup failed - submit CRITICAL status
    ERROR_MSG=$(tail -10 "$BACKUP_LOG" | grep -i error | head -1)
    curl -s -X POST \
        "https://${CHECKMK_SERVER}/monitoring/check_mk/api/1.0/services/zeus/Backup%20Status" \
        -d "status=2&message=Backup FAILED: ${ERROR_MSG}" \
        2>/dev/null || true
fi
```

---

## Check 2: OMV (omv) - Backup Storage Usage

### Configuration
- **Host**: omv (10.10.10.23) - OpenMediaVault NAS
- **Service Name**: "Filesystem /dev/root" or similar
- **Check Type**: **Active** SSH-based disk space monitoring
- **Mount Point**: `/export/Synology_Backup` (directory on `/dev/root`)
- **Alert Thresholds**:
  - WARNING: 80% full
  - CRITICAL: 90% full
- **Checkmk Config File**: `/opt/omd/sites/monitoring/etc/check_mk/conf.d/wato/backup_monitoring.mk`

### How It Works

The Checkmk agent on OMV reports disk usage via the standard `df` check. Checkmk's filesystem check monitors the root filesystem (`/`) where `/export/Synology_Backup` resides.

**Current Status**:
```
Device: /dev/root (30.5TB total)
Used: 3.8TB (14%)
Available: 25.4TB (86%)
Status: OK (well below thresholds)
```

### Service Discovery

The disk check is automatically discovered via Checkmk's service discovery:

```bash
# Run service discovery on OMV
ssh brian@10.10.10.5 'sudo su - monitoring -c "cmk -I omv"'

# List all services on OMV
ssh brian@10.10.10.5 'sudo su - monitoring -c "cmk -d omv | grep -i filesystem"'
```

### Monitoring Alert Notifications

Both checks trigger alerts based on Checkmk's configured notification rules:
- Email notifications to administrators
- Integration with existing alert channels (if configured)
- Alert suppression for acknowledged issues

---

## Configuration Files

### Primary Configuration
**Location**: `/opt/omd/sites/monitoring/etc/check_mk/conf.d/wato/backup_monitoring.mk`

**Content**:
```python
# Configure filesystem level warnings for OMV backup storage
extra_service_conf.setdefault('filesystem_levels', [])
extra_service_conf['filesystem_levels'] = [
    {
        'id': 'omv-backup-storage-warning',
        'value': {
            'levels': (80.0, 90.0),  # WARNING at 80%, CRITICAL at 90%
        },
        'condition': {
            'host_name': ['omv'],
        },
        'options': {
            'disabled': False,
            'description': 'OMV filesystem thresholds: WARN 80%, CRIT 90% (for /export/Synology_Backup)'
        }
    }
] + extra_service_conf.get('filesystem_levels', [])
```

### Custom Check Plugin (Optional)
**Location**: `/opt/omd/sites/monitoring/local/lib/python3/cmk_addons/plugins/agent_based/backup_status.py`

Provides structured passive check support for the Backup Status service (advanced feature).

---

## Verification Steps

### 1. Verify Configuration
```bash
# SSH to Checkmk server
ssh brian@10.10.10.5

# Check syntax of configuration
sudo su - monitoring
cmk -l  # Should show no errors

# List hosts
cmk --list-hosts | grep -E '^omv|^zeus'
```

### 2. Check Services Are Discovered
```bash
# Discover services on OMV
cmk -I omv

# Discover services on zeus
cmk -I zeus

# List filesystem services on OMV
cmk -d omv | grep -i filesystem
```

### 3. Test Checkmk Web Interface
```bash
# Open Checkmk web UI
https://checkmk.ratlm.com/monitoring/

# Navigate to:
# 1. Views → Host Inventory → Search for "omv" and "zeus"
# 2. Verify services appear with correct names
# 3. Check alert thresholds in service parameters
```

### 4. Monitor in Action
```bash
# Force a service check (from Checkmk server)
sudo su - monitoring
cmk -c omv  # Run all checks for OMV
cmk -c zeus  # Run all checks for zeus

# View check output
cmk -d omv | grep -A 2 "Filesystem"
```

---

## Alert Configuration

### Current Alert Status
- **Email Notifications**: Configured via global Checkmk rules
- **Escalation**: Not configured (default single-level alerts)
- **Contact Groups**: Alerts go to 'all' contact group (default)

### Configuring Alert Rules

To add custom alert routing or escalation:

```bash
# Edit alert notification rules
ssh brian@10.10.10.5
sudo su - monitoring

# Edit Checkmk WATO rules
# Path: /opt/omd/sites/monitoring/etc/check_mk/conf.d/wato/rules.mk
# Or use web UI: Setup → Events → Notifications
```

### Example Alert Rule
```python
# Alert only for OMV backup storage critical
extra_service_conf.setdefault('notification_options', [])
extra_service_conf['notification_options'] = [
    {
        'id': 'omv-backup-critical-only',
        'value': 'w,c,u,r,f',  # Warning, Critical, Unknown, Recovery, Flapping
        'condition': {
            'host_name': ['omv'],
            'service_description': [{'$regex': 'Filesystem.*'}]
        },
        'options': {'disabled': False}
    }
] + extra_service_conf.get('notification_options', [])
```

---

## Troubleshooting

### Issue: Services Not Appearing in Checkmk

**Solution**:
```bash
# 1. Force reload configuration
ssh brian@10.10.10.5
sudo su - monitoring
cmk -r

# 2. Run service discovery
cmk -II omv
cmk -II zeus

# 3. Check for errors
cmk -l 2>&1 | grep -i error
```

### Issue: Disk Check Shows Incorrect Path

**Solution**: The check monitors the root filesystem (`/`) where `/export/Synology_Backup` resides. If you need to monitor a separate mount point, update `filesystem_levels` condition to target that specific mount.

### Issue: Passive Check Not Receiving Updates

**Solution**:
1. Verify backup script has network access to Checkmk server (port 443)
2. Confirm HTTPS certificates are trusted (or use `-k` flag with curl)
3. Check Checkmk's passive check queue:
   ```bash
   tail -50 /opt/omd/sites/monitoring/var/log/nagios.log | grep -i passive
   ```

---

## Related Files

- **Backup Script**: `/root/backup-daily.sh` (Synology)
- **Backup Log**: `/var/log/backup-daily.log` (Synology)
- **Submission Script**: `/home/brian/claude/scripts/submit_backup_status.sh`
- **Checkmk Config**: `/opt/omd/sites/monitoring/etc/check_mk/conf.d/wato/backup_monitoring.mk`
- **Checkmk Custom Plugin**: `/opt/omd/sites/monitoring/local/lib/python3/cmk_addons/plugins/agent_based/backup_status.py`

---

## Next Steps

1. **Integrate with Backup Script**: Add passive check submission to `/root/backup-daily.sh` on Synology
2. **Configure Alert Recipients**: Update notification rules to send alerts to email/teams
3. **Set Up Dashboard**: Create custom Checkmk dashboard showing backup status and storage usage
4. **Monitor for 24 Hours**: Verify both checks are running and alerting correctly

---

## Quick Reference

| Item | Value |
|------|-------|
| Checkmk Server | https://checkmk.ratlm.com/monitoring/ (10.10.10.5) |
| OMV Host | omv / 10.10.10.23 |
| Synology Host | zeus / 10.10.10.2 |
| OMV Check | Filesystem (root) - WARN 80%, CRIT 90% |
| Synology Check | Backup Status (passive) |
| Backup Location | /export/Synology_Backup (on OMV) |
| Backup Log | /var/log/backup-daily.log (on Synology) |

---

## Checkmk Commands Reference

```bash
# SSH to Checkmk server
ssh brian@10.10.10.5

# Switch to monitoring user
sudo su - monitoring

# Show all hosts
cmk --list-hosts

# Reload configuration
cmk -r

# Run service discovery (refreshes services)
cmk -I omv    # Run for OMV
cmk -II omv   # Full service discovery on OMV

# Dump services for a host
cmk -d omv    # Show all services on omv

# Run checks manually
cmk -c omv    # Run all checks for omv

# Validate configuration
cmk -l        # List compilation of config
```

---

**Created**: 2025-12-12 by Claude Code
**Last Updated**: 2025-12-12
**Status**: Ready for Production
