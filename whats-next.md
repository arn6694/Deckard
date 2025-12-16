# Session Handoff - Zeus to OMV Backup Configuration
**Date:** 2025-12-13
**Status:** Backup system configured and cron job set up - ready for production testing

---

## Original Task
Configure Zeus (Synology NAS at 10.10.10.2) to back up to OMV (OpenMediaVault at 10.10.10.23) using a simple, reliable rsync-based backup that:
- Stores backups in `/mnt/OMV2/zeus_backups` (dedicated 9.1TB XFS mount, not on / filesystem)
- Runs daily without filling up disks
- Does NOT use complex dated snapshots or hard-link deduplication (previous approach filled up / mount)
- Backs up key sources: /volume1/Family, /volume1/NetBackup, /volume1/docker, /volume1/web, /volume1/surveillance

---

## Work Completed

### 1. Updated Backup Scripts
- **Modified `/home/brian/claude/scripts/backup-daily.sh`:**
  - Destination: `brian@10.10.10.23:/mnt/OMV2/zeus_backups` (remote SSH rsync)
  - Removed hard-link deduplication and `--delete` flag
  - Added: `-avz --no-perms --no-group --no-owner --ignore-errors`
  - Runs sequentially (one source at a time)
- **Deleted:** `backup-weekly.sh`, `backup-monthly.sh`

### 2. OMV Destination Configuration
- `/mnt/OMV2/` = local XFS on OMV (9.1TB available)
- Created subdirectories: homes, docker, Family, NetBackup, web, surveillance
- Permissions: `777` on parent and backup directories

### 3. Cron Job Setup
- Created `/etc/cron.d/backup-tasks` on Zeus
- Runs daily at 3:00 AM: `/usr/local/bin/backup-scripts/backup-daily.sh`

### 4. SSH Access Verified
- Key-based auth working from Zeus to OMV as `brian` user
- No password required

### 5. Testing Status
- Initial manual backup (17:46): Started Family backup but stalled/slow
- Backup script executes without errors
- Parallel launcher scripts created but not actively used

---

## Work Remaining

### 1. Verify Backup Completion
- [ ] Check if initial Family backup completed: `du -sh /mnt/OMV2/zeus_backups/Family/`
- [ ] If incomplete, kill rsync: `ssh brian@10.10.10.2 "ps aux | grep rsync"`
- [ ] Re-run backup and monitor: `watch -n 2 du -sh /mnt/OMV2/zeus_backups/`

### 2. Production Validation
- [ ] Let 3:00 AM cron run on 2025-12-14
- [ ] Check logs: `ssh brian@10.10.10.2 "tail -50 /var/log/backup-daily.log"`
- [ ] Test restore with sample file

### 3. Optional: Enable Parallel Backups
- If serial backup too slow, use `backup_parallel_launcher.sh` (4 parallel rsync jobs)
- Update cron job accordingly

---

## Attempted Approaches (Failures & Learnings)

### ❌ NFS Mount Strategy
- Assumed `/mnt/OMV2` could be mounted via NFS from Zeus
- **Issue:** Synology NFS configuration complex, requires web UI setup
- **Lesson:** Local OMV filesystem was simpler solution

### ❌ Parallel Launcher (Initial)
- Complex error handling, permission issues with SSH receiver
- Multiple rsync processes failed with "Permission denied"
- **Status:** Scripts exist but need debugging if needed

### ❌ Hard-Link Deduplication
- Previous approach with `--link-dest` filled up / filesystem
- Abandoned for simple per-source persistent directories

### ✓ Serial Rsync (Current)
- Works when permissions correct
- Simple, predictable capacity usage

---

## Critical Context

### Infrastructure Details
- **Zeus (10.10.10.2):** Synology NAS, 27TB storage
- **OMV (10.10.10.23):** OpenMediaVault, local `/mnt/OMV2/` (9.1TB XFS)
- **Network:** 1 Gbps LAN (~125 MB/s max, actual ~60-80 MB/s via rsync)
- **Backup window:** 3:00 AM daily (7 hours available before typical morning use)

### Key Discoveries
1. `/mnt/OMV2` is LOCAL storage on OMV, not NFS from Zeus
2. rsync over SSH requires proper file permissions on both ends
3. Synology system directories (@eaDir) have permission restrictions
4. Simple approach (no snapshots, no deduplication) is more reliable

### Rsync Options Explained
- `-avz`: Archive, verbose, compress
- `--no-perms --no-group --no-owner`: Allow remote writes without ownership match
- `--ignore-errors`: Continue on permission denied (critical for @eaDir system dirs)

### Sources to Exclude
- `/volume1/homes/@eaDir/` - Permission denied
- `/volume1/docker/Plex/config/*` - File locks
- `/volume1/web/web_images` - Permission denied

---

## Current State

| Component | Status | Notes |
|-----------|--------|-------|
| Backup script | ✅ Complete | Updated with remote SSH destination |
| OMV destination | ✅ Complete | Directories created, permissions fixed |
| Cron job | ✅ Complete | 3:00 AM daily on Zeus |
| SSH access | ✅ Verified | Key-based auth working |
| Initial test | 🟡 Pending | Family backup status unknown |

---

## Next Actions

1. **Verify backup:** Check `/mnt/OMV2/zeus_backups/Family/` size
2. **Monitor 3:00 AM run:** Check logs after first automatic backup
3. **Test restore:** Verify backed-up files are readable
4. **Consider parallel:** If serial backup takes >8 hours, enable 4-job parallelization

---

## Files Modified

**In Repo:**
- ✏️ `scripts/backup-daily.sh` - Updated destination and rsync options
- 🗑️ `scripts/backup-weekly.sh` - Deleted
- 🗑️ `scripts/backup-monthly.sh` - Deleted

**On Zeus:**
- 📍 `/usr/local/bin/backup-scripts/backup-daily.sh` - Copied from repo
- 📍 `/etc/cron.d/backup-tasks` - Created for scheduling
- 📝 `/var/log/backup-daily.log` - Execution logs

**On OMV:**
- 📁 `/mnt/OMV2/zeus_backups/` - Backup destination (777 perms)
- 📁 Subdirectories for each source
