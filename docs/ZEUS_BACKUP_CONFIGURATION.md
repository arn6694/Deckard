# Zeus Synology → OMV Backup Configuration

**Created:** 2025-12-12
**Source:** Zeus Synology NAS (10.10.10.2)
**Destination:** OMV NAS (10.10.10.24) - 22.2 TB available
**Backup Type:** Complete user data + critical infrastructure backups
**Total Size:** 6.5 TB
**Remaining Space After Backup:** 15.7 TB

---

## Backup Job Configuration

### Shares to Include

Use this list when configuring the backup job in OMV:

#### Tier 1: Critical Media (Required)
```
/volume1/TV Shows        → 3.8 TB
/volume1/Movies          → 2.2 TB
/volume1/Family          → 126 GB
/volume1/Tunes           → 75 GB
```

#### Tier 2: Infrastructure Backups (Required)
```
/volume1/NetBackup       → 245 GB
  (Contains Proxmox dumps 238 GB - CRITICAL for DR)
```

#### Tier 3: User Directories (Optional but included)
```
/volume1/homes           → 48 KB
```

**Total to backup: 6.5 TB**

### Shares to Exclude

```
/volume1/docker                    (101 GB - rebuilding preferred)
/volume1/@*                        (All @ prefixed system dirs)
/volume1/surveillance              (Empty, not in use)
/volume1/web                       (4.0K - system files)
/volume1/web_packages              (System files)
```

---

## SMB Connection Details

**Host:** 10.10.10.2
**Share Name:** `TV Shows`, `Movies`, `Family`, `Tunes`, `homes`, `NetBackup`

**OMV NFS Mount (recommended for efficiency):**
```
NFS Server: 10.10.10.2
NFS Shares: /volume1/TV\ Shows, /volume1/Movies, /volume1/Family,
            /volume1/Tunes, /volume1/homes, /volume1/NetBackup
```

---

## Pre-Backup Verification

Run these commands on Zeus (10.10.10.2) before starting backup:

```bash
# Verify all shares exist and report correct sizes
du -sh /volume1/TV\ Shows /volume1/Movies /volume1/Family /volume1/Tunes /volume1/homes /volume1/NetBackup

# Expected output:
# 3.8T	/volume1/TV Shows
# 2.2T	/volume1/Movies
# 126G	/volume1/Family
# 75G	/volume1/Tunes
# 48K	/volume1/homes
# 245G	/volume1/NetBackup

# Check volume capacity
df -h /volume1

# Expected: 27T total capacity, ~6.5T used, ~20.5T available
```

---

## OMV Side Verification

Run on OMV (10.10.10.24) before starting backup:

```bash
# Verify destination space
df -h /mnt/backup_pool

# Must show >6.5 TB available
# Expected: 22.2 TB available (plenty of headroom)

# Test SMB connectivity to Zeus
smbclient -L 10.10.10.2 -N
# Should list all shares

# Or test NFS if using NFS mounts
showmount -e 10.10.10.2
```

---

## Backup Job Recommendations

### Schedule
- **Initial Full Backup:** Off-peak hours (2 AM - 6 AM recommended)
- **Frequency:** Daily or weekly incremental backups
- **Window:** Allow 4-8 hours for initial 6.5 TB backup (depends on network speed)

### Performance Expectations
- **Network Speed:** 1 Gbps standard = ~125 MB/s theoretical max
- **Estimated Duration:** 6.5 TB ÷ 125 MB/s ≈ 14-15 hours
- **Actual Duration:** Likely 20-24 hours due to overhead, filesystem latency

### Retention Policy
- **Snapshots to Keep:** 4 weekly full backups (rotated)
- **Total Space Used:** ~26 TB (4 × 6.5 TB) with incremental deltas
- **Space Safety:** Keep 2-3 TB reserved free on OMV
- **Recommendation:** Implement automated cleanup (oldest backup deleted after 4 weeks)

---

## Backup Verification

After backup completes, verify:

1. **Size Check:** Backup directory should be ~6.5 TB
   ```bash
   du -sh /mnt/backup_pool/zeus_backup/
   ```

2. **File Count Check:** Verify key folders exist
   ```bash
   ls -l /mnt/backup_pool/zeus_backup/
   # Should show: TV Shows, Movies, Family, Tunes, homes, NetBackup
   ```

3. **Sample Restore Test:** Verify restore from backup works
   ```bash
   # Copy sample file from backup to test location
   cp /mnt/backup_pool/zeus_backup/Family/sample.txt /tmp/test.txt
   # Verify file integrity
   md5sum /tmp/test.txt
   ```

4. **NetBackup Verification:** Confirm Proxmox dumps are present
   ```bash
   ls -lh /mnt/backup_pool/zeus_backup/NetBackup/Proxmox/ | head -5
   # Should show .img or .dump files from Proxmox VMs
   ```

---

## Critical Information

### Why NetBackup is Essential
The `/volume1/NetBackup/Proxmox` directory contains **238 GB** of Proxmox VM dumps. These are **irreplaceable** and essential for complete infrastructure disaster recovery. Without these backups:
- Cannot restore Proxmox infrastructure
- Cannot recover VMs from hardware failure
- Cannot test disaster recovery procedures

### Why Docker is Excluded
- Docker images can be rebuilt from registries
- Application data is stored in other shares (Family, Movies, etc.)
- Container definitions are version-controlled separately
- Backup time can be better spent on irreplaceable data

### Restore Procedures
- **User Data (Movies, Family, Tunes):** Standard SMB/NFS restore via OMV
- **Proxmox Dumps:** Can be imported back into Proxmox at 10.10.10.17
- **Archived Photos:** Standard file restoration via NFS/SMB
- **Infrastructure Docs:** Use for reference in DR procedures

---

## Next Steps

1. Configure backup job in OMV:
   - Source: 10.10.10.2 (Zeus)
   - Destination: /mnt/backup_pool/zeus_backup
   - Include: All 6 shares listed above
   - Exclude: docker and @* system directories

2. Run initial backup during off-peak hours
3. Monitor backup process for errors
4. Verify backup contents after completion
5. Test restore of sample files
6. Configure retention policy (4 weekly snapshots)
7. Set up monitoring/alerts for backup failures

---

## File Reference
Complete detailed analysis: `/home/brian/claude/docs/ZEUS_NAS_SHARE_STRUCTURE.md`
