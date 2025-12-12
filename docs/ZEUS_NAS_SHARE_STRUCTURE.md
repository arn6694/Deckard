# Synology NAS (Zeus) Share Structure Documentation

**Date:** 2025-12-12
**NAS Host:** Zeus (10.10.10.2) - Synology 920+ (6.5 TB used of 27 TB total capacity)
**Available for Backup:** 20.5 TB free space

---

## Executive Summary

Zeus has **6.5 TB of used data** distributed across 6 major user-facing shares. OMV backup destination has **22.2 TB available**, providing sufficient capacity for a complete backup of all shares with significant headroom (15.7 TB remaining after backup).

---

## Share Structure - User-Facing Shares

### Primary Data Shares (4.2 TB of 6.5 TB)

| Share Name | Path | Size | Purpose | Backup Priority |
|-----------|------|------|---------|-----------------|
| **TV Shows** | `/volume1/TV Shows` | **3.8 TB** | Streaming media (TV series) | **CRITICAL** |
| **Movies** | `/volume1/Movies` | **2.2 TB** | Streaming media (films) | **CRITICAL** |
| **Family** | `/volume1/Family` | **126 GB** | Personal/family documents | **HIGH** |
| **Tunes** | `/volume1/Tunes` | **75 GB** | Music collection | **HIGH** |
| **homes** | `/volume1/homes/` | **48 KB** | User home directories (minimal use) | **MEDIUM** |

**Subtotal:** 6.3 TB (97% of all data)

---

### Secondary Data Shares

| Share Name | Path | Size | Purpose | Backup Priority |
|-----------|------|------|---------|-----------------|
| **NetBackup** | `/volume1/NetBackup` | **245 GB** | Infrastructure/archive backups | **HIGH** |
| **docker** | `/volume1/docker` | **101 GB** | Docker container data | **LOW/SKIP** |

#### NetBackup Subdirectories (245 GB total)

| Category | Path | Size | Content |
|----------|------|------|---------|
| Proxmox | `/volume1/NetBackup/Proxmox` | 238 GB | Proxmox VM dumps & NPM config backups |
| Pictures | `/volume1/NetBackup/Pics` | 3.6 GB | Archived photo collections (2013-2019) |
| SystemHosting | `/volume1/NetBackup/SystemHosting` | 1.2 GB | Change control, DR docs, infrastructure snapshots |
| Need to sort | `/volume1/NetBackup/Need to sort thru` | 837 MB | Unsorted archive data |
| ESXI | `/volume1/NetBackup/ESXI` | 687 MB | VMware ESXI infrastructure backups |
| 2023 Documents | `/volume1/NetBackup/2023 DOcuments` | 262 MB | Document archives |
| Icons | `/volume1/NetBackup/icons` | 208 MB | Desktop icon collections |
| DVR | `/volume1/NetBackup/DVR` | 139 MB | DVR software, firmware, drivers |
| Ansible | `/volume1/NetBackup/ansible` | 24 MB | Ansible playbooks and configurations |
| Admin Scripts | `/volume1/NetBackup/admin scripts` | 16 MB | System administration scripts |
| Other | Various | 2.4 MB | BA, shellclass, PowerShell modules, etc. |

**Key Finding:** The 238 GB Proxmox dump contains critical infrastructure backups that should definitely be protected.

---

## System Directories (Excluded from Backup)

The following system directories are excluded as they are Synology-specific and not needed for backup:

- `@S2S` - Synology S2S replication
- `@SynoFinder-*` - File finder indexes
- `@SynologyApplicationService` - System services
- `@SynologyDriveShareSync` - Drive sync metadata
- `@appconf`, `@appdata`, `@apphome`, `@appshare`, `@appstore`, `@apptemp` - Application directories
- `@autoupdate`, `@cloudsync`, `@config_backup` - System management
- `@database` - Synology database
- `@docker` - Docker system files
- `@eaDir` - Extended attributes (thumbnails, metadata)
- `@img_bkp_cache`, `@sharesnap`, `@ssbackup` - Snapshot/backup cache
- `@surveillance` - CCTV/surveillance data (empty - not currently in use)
- `@synoconfd`, `@synologydrive`, `@tmp` - Temporary/system
- `@userpreference` - User preference data
- `web`, `web_packages` - Web server packages
- `surveillance` - CCTV storage (empty)

---

## Volume Capacity Overview

```
Total Capacity:    27 TB
Used:              6.5 TB (25%)
Free:              20.5 TB (75%)
```

---

## Recommended Backup Strategy

### Option A: Complete Backup (Recommended)

**Backup all user-facing shares** (6.3 TB total):

1. ✅ TV Shows (3.8 TB)
2. ✅ Movies (2.2 TB)
3. ✅ Family (126 GB)
4. ✅ Tunes (75 GB)
5. ✅ homes (48 KB)

**Total backup size:** ~6.3 TB
**Space required on OMV:** 6.3 TB
**OMV space remaining after:** 15.9 TB
**Recommendation:** Proceed with this option

---

### Option B: Critical Media Only (Minimal)

**Backup streaming media and irreplaceable files** (6.1 TB):

1. ✅ TV Shows (3.8 TB)
2. ✅ Movies (2.2 TB)
3. ✅ Family (126 GB) - **Personal/irreplaceable content**

**Total backup size:** ~6.1 TB
**OMV space remaining after:** 16.1 TB
**Note:** Excludes music (Tunes) which is easily re-ripped

---

### Option C: With NetBackup Archive (RECOMMENDED)

**Include all user shares + infrastructure backups** (6.5 TB):

All shares from Option A + NetBackup (245 GB)

**Includes:**
- TV Shows (3.8 TB)
- Movies (2.2 TB)
- Family (126 GB)
- Tunes (75 GB)
- homes (48 KB)
- **NetBackup containing:**
  - **Proxmox dumps** (238 GB) - Critical infrastructure backups
  - Archived photos (3.6 GB)
  - System infrastructure docs (1.2 GB)
  - ESXI backups (687 MB)
  - Other archives (1.5 GB)

**Total backup size:** ~6.5 TB
**OMV space remaining after:** 15.7 TB
**Recommendation:** **PROCEED WITH THIS OPTION** - NetBackup contains critical Proxmox infrastructure backups that are essential for disaster recovery

---

## Backup Implementation Notes

### What NOT to Backup

- **docker** (101 GB): Container images and data can be rebuilt. Skip this share.
- **All `@` system directories**: These are Synology-specific and restore will fail on non-Synology systems
- **surveillance**: Currently empty; if populated with CCTV, handle separately as it's high volume + lower retention requirements

### Backup Schedule Recommendation

Given 6.3 TB backup size and OMV network bandwidth:

- **Initial full backup:** Schedule for off-peak hours (e.g., 2 AM - 6 AM)
- **Incremental backups:** Daily or weekly (depending on media update frequency)
- **Retention:** Keep 2-4 weekly backups on OMV (total 12-24 TB with rotation)

### Verification Steps

After backup configuration:

1. Verify all shares are mounted on OMV
2. Check available space before backup (must have >6.5 TB free)
3. Monitor first backup for performance/errors
4. Validate restore capabilities on sample files

---

## Technical Details

**NAS Model:** Synology DS920+
**Total Capacity:** 27 TB (cachedev_0 - RAID volume)
**Current Usage:** 6.5 TB (25%)
**OMV Destination Capacity:** 22.2 TB available
**Backup Window:** 15.7-15.9 TB available after backup

---

## Access Methods

The following shares are accessible via SMB/NFS:

- TV Shows
- Movies
- Family
- Tunes
- homes (user home directories)

System verification can be done via:
```bash
# On Zeus (10.10.10.2)
du -sh /volume1/TV\ Shows /volume1/Movies /volume1/Family /volume1/Tunes
df -h /volume1
```

---

## Summary

Zeus Synology NAS contains **6.5 TB of user data** across clearly organized shares. The backup to OMV is feasible with the available 22.2 TB capacity, providing excellent redundancy. **Recommend Option C** (complete backup including critical infrastructure backups) for comprehensive data protection.

### Why Option C is Best:
- **Proxmox dumps (238 GB)** are irreplaceable infrastructure backups essential for disaster recovery
- **Archived photos and infrastructure docs** provide historical context for system configuration
- **Total cost of storage: 6.5 TB** vs **Available space: 22.2 TB** = Excellent headroom (15.7 TB remaining)
- **No reason to exclude critical backups** when space is abundant
- Provides **2 independent backup copies** of all critical infrastructure
