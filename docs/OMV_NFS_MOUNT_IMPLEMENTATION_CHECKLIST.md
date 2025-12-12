# OMV NFS Mount Implementation - Quick Checklist

**Status:** Ready for Implementation
**Date:** 2025-12-12
**Target:** Mount OMV NFS (10.10.10.23) on n8n/Zeus (10.10.10.52)

---

## PRE-IMPLEMENTATION CHECKLIST

- [ ] Backup OMV /etc/exports (save to safe location)
- [ ] Backup n8n /etc/fstab (save to safe location)
- [ ] Verify OMV NFS daemon is running: `systemctl status nfs-server`
- [ ] Test connectivity from n8n to OMV: `nc -zv 10.10.10.23 2049`
- [ ] Document current mount status: `mount | grep -i nfs`

---

## STEP 1: CONFIGURE OMV NFS EXPORT (5 min)

**SSH to OMV:**
```bash
ssh brian@10.10.10.23
```

**Step 1.1: Back up /etc/exports**
```bash
sudo cp /etc/exports /etc/exports.backup.$(date +%Y%m%d)
```

**Step 1.2: Edit /etc/exports to add n8n access**
```bash
sudo nano /etc/exports
```

**Step 1.3: Update the /export/OMV2 line**

Find this line:
```
/export/OMV2 10.10.10.96(fsid=526cde7f-0564-44ea-bce5-2788fb63ec2e,rw,subtree_check,insecure)
```

Replace with:
```
/export/OMV2 10.10.10.96(fsid=526cde7f-0564-44ea-bce5-2788fb63ec2e,rw,subtree_check,insecure) \
             10.10.10.52(fsid=526cde7f-0564-44ea-bce5-2788fb63ec2e,rw,subtree_check,insecure)
```

Save with Ctrl+X, then Y, then Enter.

**Step 1.4: Reload NFS exports**
```bash
sudo exportfs -ra
```

**Step 1.5: Verify configuration**
```bash
sudo exportfs -v | grep -A1 "export/OMV2"
```

Expected output:
```
/export/OMV2
    10.10.10.96(fsid=526cde7f-0564-44ea-bce5-2788fb63ec2e,rw,subtree_check,insecure)
    10.10.10.52(fsid=526cde7f-0564-44ea-bce5-2788fb63ec2e,rw,subtree_check,insecure)
```

**Status:** ✅ Complete if export shows both IPs

---

## STEP 2: PREPARE n8n FOR NFS MOUNT (5 min)

**SSH to n8n:**
```bash
ssh brian@10.10.10.52
```

**Step 2.1: Install NFS client (if not already installed)**
```bash
sudo apt-get update -qq && sudo apt-get install -y nfs-common 2>&1 | tail -5
```

**Step 2.2: Create mount point directory**
```bash
sudo mkdir -p /mnt/omv_backup
sudo chown root:root /mnt/omv_backup
sudo chmod 755 /mnt/omv_backup
ls -la /mnt/omv_backup
```

**Status:** ✅ Complete if directory created and permissions correct (755)

---

## STEP 3: TEST TEMPORARY NFS MOUNT (5 min)

**Step 3.1: Perform test mount**
```bash
sudo mount -t nfs -o vers=3,proto=tcp,rw,hard,intr,timeo=600,retrans=3,nosuid,nodev \
  10.10.10.23:/export/OMV2 /mnt/omv_backup
```

**Step 3.2: Verify mount succeeded**
```bash
mount | grep omv_backup
```

Expected output:
```
10.10.10.23:/export/OMV2 on /mnt/omv_backup type nfs (rw,hard,intr,...)
```

**Step 3.3: Check available space**
```bash
df -h /mnt/omv_backup
```

Expected output:
```
Filesystem      Size  Used Avail Use% Mounted on
10.10.10.23:/export/OMV2  8.8T  300G  8.5T   4% /mnt/omv_backup
```

**Step 3.4: Test read/write capability**
```bash
sudo touch /mnt/omv_backup/TEST_WRITE.txt
ls -la /mnt/omv_backup/TEST_WRITE.txt
sudo rm /mnt/omv_backup/TEST_WRITE.txt
```

**Step 3.5: Verify on OMV that file was accessible**
```bash
ssh brian@10.10.10.23 'ls -la /export/OMV2/ | grep -i test'
```

**Step 3.6: Unmount test mount**
```bash
sudo umount /mnt/omv_backup
```

**Step 3.7: Verify unmounted**
```bash
mount | grep omv_backup
```

Should return nothing (no output = successfully unmounted).

**Status:** ✅ Complete if all tests passed with no errors

---

## STEP 4: CONFIGURE PERSISTENT MOUNT IN fstab (5 min)

**Step 4.1: Back up /etc/fstab**
```bash
sudo cp /etc/fstab /etc/fstab.backup.$(date +%Y%m%d)
```

**Step 4.2: Add NFS mount to /etc/fstab**
```bash
sudo nano /etc/fstab
```

**Step 4.3: Add this line at the end of the file:**
```
# OMV NFS Backup Storage (Mount for Zeus/Docker backups)
10.10.10.23:/export/OMV2  /mnt/omv_backup  nfs  vers=3,proto=tcp,rw,hard,intr,timeo=600,retrans=3,nosuid,nodev,_netdev  0  0
```

Save with Ctrl+X, then Y, then Enter.

**Step 4.4: Verify fstab syntax**
```bash
sudo mount -a --verbose
```

Should mount without errors.

**Step 4.5: Confirm persistent mount**
```bash
mount | grep omv_backup
df -h /mnt/omv_backup
```

**Status:** ✅ Complete if mount shows in both commands

---

## STEP 5: CREATE BACKUP DIRECTORY STRUCTURE (5 min)

**Step 5.1: Create organized backup subdirectories**
```bash
sudo mkdir -p /mnt/omv_backup/zeus_backups/{daily,weekly,monthly}
```

**Step 5.2: Set proper permissions**
```bash
sudo chown -R brian:brian /mnt/omv_backup/zeus_backups
sudo chmod -R 755 /mnt/omv_backup/zeus_backups
```

**Step 5.3: Verify structure**
```bash
tree /mnt/omv_backup/zeus_backups
```

Expected:
```
/mnt/omv_backup/zeus_backups
├── daily
├── weekly
└── monthly
```

If `tree` not available:
```bash
find /mnt/omv_backup/zeus_backups -type d
```

**Status:** ✅ Complete if directory structure created

---

## STEP 6: DOCUMENT CONFIGURATION (5 min)

**Step 6.1: Record mount configuration in Obsidian**
```bash
cat > /tmp/mount_config.txt << 'EOF'
# OMV NFS Mount Configuration
Date: $(date)
Hostname: n8n (10.10.10.52)
NFS Server: OMV (10.10.10.23)
Mount Point: /mnt/omv_backup
Export: /export/OMV2
Protocol: NFS v3 over TCP
Status: MOUNTED and PERSISTENT via fstab

Current Mount Options:
- vers=3 (NFS v3 - stable protocol)
- proto=tcp (TCP only - reliable)
- hard (retry indefinitely on failure)
- intr (allow Ctrl+C to interrupt)
- timeo=600 (60 second RPC timeout)
- retrans=3 (retry 3 times before major timeout)
- nosuid (security - disable SUID bit)
- nodev (security - disable device special files)
- _netdev (systemd flag - wait for network before mounting)

Available Space: 8.8TB (97% free)
Current Usage: 300GB
Recommended Max: 4TB for Zeus backups

Backup Subdirectories:
- /mnt/omv_backup/zeus_backups/daily
- /mnt/omv_backup/zeus_backups/weekly
- /mnt/omv_backup/zeus_backups/monthly
EOF
cat /tmp/mount_config.txt
```

**Step 6.2: Add to documentation**
```bash
# Note: You can manually add this to your Obsidian vault or documentation
```

**Status:** ✅ Complete if configuration documented

---

## STEP 7: TEST BACKUP WORKFLOW (10 min)

**Step 7.1: Create small test backup**
```bash
# Example: backup a small Docker volume
sudo rsync -av --delete /var/lib/docker/volumes/test_vol/ /mnt/omv_backup/zeus_backups/daily/test_backup/ 2>&1 | head -20
```

**Step 7.2: Verify files on OMV**
```bash
ssh brian@10.10.10.23 'ls -lah /export/OMV2/zeus_backups/daily/test_backup/ | head -10'
```

**Step 7.3: Monitor backup space**
```bash
df -h /mnt/omv_backup
```

**Status:** ✅ Complete if test backup successful and visible on OMV

---

## POST-IMPLEMENTATION VERIFICATION

**Run these commands to verify everything works:**

```bash
# 1. Verify NFS mount is persistent
mount | grep omv_backup

# 2. Check available space
df -h /mnt/omv_backup

# 3. List backup directories
ls -la /mnt/omv_backup/zeus_backups/

# 4. Test write access
sudo touch /mnt/omv_backup/health_check.txt && ls -la /mnt/omv_backup/health_check.txt

# 5. Test read from OMV
ssh brian@10.10.10.23 'ls -la /export/OMV2/ | wc -l'

# 6. Check NFS connection stats
netstat -an | grep 2049 | wc -l

# 7. Verify mount survives reboot (recommended: reboot and re-run)
```

---

## ROLLBACK PLAN (If needed)

**If something goes wrong:**

**Option 1: Unmount and revert (immediate)**
```bash
sudo umount /mnt/omv_backup
sudo nano /etc/fstab  # Remove the OMV NFS line
sudo mount -a
```

**Option 2: Revert OMV exports**
```bash
ssh brian@10.10.10.23 'sudo cp /etc/exports.backup.* /etc/exports && sudo exportfs -ra'
```

**Option 3: Full revert to backup**
```bash
# On n8n:
sudo cp /etc/fstab.backup.* /etc/fstab

# On OMV:
ssh brian@10.10.10.23 'sudo cp /etc/exports.backup.* /etc/exports && sudo exportfs -ra'
```

---

## MONITORING AFTER IMPLEMENTATION

**Daily Health Check (add to crontab):**
```bash
# Run daily at 6 AM
0 6 * * * mount | grep -q omv_backup && echo "✅ OMV NFS mounted" || echo "⚠️ OMV NFS NOT MOUNTED"
```

**Weekly Space Check:**
```bash
# Run weekly (e.g., Sunday at 8 AM)
0 8 * * 0 df -h /mnt/omv_backup | mail -s "OMV NFS Space Report" brian@example.com
```

**Monthly Restore Test:**
- First Friday of month: Restore small backup subset to verify data integrity
- Log results: `echo "2025-12-12 Restore test: OK" >> /var/log/backup_validation.log`

---

## TROUBLESHOOTING QUICK REFERENCE

| Problem | Diagnosis | Solution |
|---------|-----------|----------|
| **Mount fails** | `sudo mount -a` shows error | Check: `nc -zv 10.10.10.23 2049` |
| **Permission denied** | Can't write to mount | Verify: `sudo exportfs -v` includes 10.10.10.52 |
| **Slow performance** | Backup taking >100 MB/s | Check network: `ping -c 5 10.10.10.23` |
| **Mount disappears after reboot** | fstab entry not working | Check: `sudo mount -a --verbose` |
| **Out of space** | df shows <100MB free | Reduce backup retention or use secondary OMV disk |
| **NFS connection timeout** | Operations hang | Change to soft mount: `soft` instead of `hard` in fstab |

---

## SUCCESS CRITERIA

All of the following must be true:

- [ ] OMV /etc/exports shows both 10.10.10.96 and 10.10.10.52
- [ ] n8n can mount /export/OMV2 without errors
- [ ] `df -h /mnt/omv_backup` shows 8.8TB available
- [ ] Can create files on mount point
- [ ] Files visible from OMV SSH session
- [ ] Mount persists after `sudo mount -a`
- [ ] Backup directories created: daily, weekly, monthly
- [ ] Test backup completes without errors
- [ ] No permission denied errors in operation

**When all criteria met: IMPLEMENTATION COMPLETE**

---

## TIME ESTIMATE

| Step | Time | Status |
|------|------|--------|
| Configure OMV exports | 5 min | |
| Prepare n8n | 5 min | |
| Test mount | 5 min | |
| Configure fstab | 5 min | |
| Create structure | 5 min | |
| Documentation | 5 min | |
| Test workflow | 10 min | |
| **TOTAL** | **40 min** | **Estimated** |

---

## NEXT STEPS (After Implementation)

1. **Test first backup** (30 min)
   - Schedule daily rsync job for Docker volumes
   - Monitor first run for performance/errors
   - Verify files appear on OMV

2. **Configure backup automation** (1-2 hours)
   - Create cron job or systemd timer
   - Add monitoring/alerting
   - Test automated restore

3. **Plan retention policy** (30 min)
   - Decide: keep 7, 14, or 30 days of backups?
   - Create cleanup script for old backups
   - Document retention policy

4. **Test quarterly restore** (1 hour)
   - Monthly: Verify one backup can restore successfully
   - Document restore procedure
   - Update disaster recovery runbook

