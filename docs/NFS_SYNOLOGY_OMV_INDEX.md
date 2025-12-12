# NFS Synology → OMV Configuration Index

**Status:** OPERATIONAL (2025-12-12)
**Mount Point:** `/mnt/omv_backup` (Synology) → `10.10.10.23:/export/Synology_Backup`

---

## Quick Start

**Check Mount Status:**
```bash
ssh brian@10.10.10.2 'mount | grep omv_backup && df -h /mnt/omv_backup'
```

**Expected Output:**
```
10.10.10.23:/export/Synology_Backup on /mnt/omv_backup type nfs (...)
Filesystem                           Size  Used Avail Use%
10.10.10.23:/export/Synology_Backup   30G  3.7G   25G   14%
```

---

## Documentation Files

### In Obsidian Vault
1. **NFS_Mount_Synology_to_OMV.md**
   - Location: `/home/brian/Documents/Notes/Infrastructure/`
   - Content: Complete technical reference
   - Use: Detailed configuration information

2. **NFS_Quick_Reference.md**
   - Location: `/home/brian/Documents/Notes/Infrastructure/`
   - Content: One-page summary
   - Use: Quick lookup for commands

### In Repository
3. **NFS_SYNOLOGY_OMV_CONFIGURATION.md**
   - Location: `/home/brian/claude/docs/`
   - Content: Full configuration guide with troubleshooting
   - Use: Team reference and documentation

4. **NFS_SYNOLOGY_OMV_INDEX.md** (This File)
   - Quick reference and file index

---

## Key Commands

| Task | Command |
|------|---------|
| Check mount | `mount \| grep omv_backup` |
| Check storage | `df -h /mnt/omv_backup` |
| Test write | `echo "test" > /mnt/omv_backup/test.txt` |
| View config | `grep omv_backup /etc/fstab` |
| Remount | `sudo mount /mnt/omv_backup` |
| Check OMV | `ssh brian@10.10.10.23 'sudo exportfs -v'` |

---

## Configuration Summary

| Item | Value |
|------|-------|
| **Source System** | Synology Zeus (10.10.10.2) |
| **Destination** | OpenMediaVault (10.10.10.23) |
| **Mount Point** | /mnt/omv_backup |
| **NFS Export** | /export/Synology_Backup |
| **Capacity** | 30GB (25GB available) |
| **Protocol** | NFSv3 over TCP |
| **Performance** | 7.7 MB/s (verified) |
| **Status** | Operational ✅ |

---

## Configuration Files

**OMV (`/etc/exports`):**
```bash
/export/Synology_Backup 10.10.10.2(rw,subtree_check,insecure,no_root_squash)
```

**Synology (`/etc/fstab`):**
```bash
10.10.10.23:/export/Synology_Backup /mnt/omv_backup nfs \
  rw,hard,timeo=150,retrans=3,rsize=65536,wsize=65536 0 0
```

**Synology (`/etc/rc.local`):**
```bash
mount /mnt/omv_backup
```

---

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| Mount not found | `sudo mount /mnt/omv_backup` |
| Permission denied | `ssh brian@10.10.10.23 'sudo chmod 777 /export/Synology_Backup'` |
| Connection timeout | `ping 10.10.10.23` then check NFS server |
| Not mounted after reboot | `sudo mount -a` or `sudo bash /etc/rc.local` |

See full troubleshooting: `/home/brian/claude/docs/NFS_SYNOLOGY_OMV_CONFIGURATION.md`

---

## Next Steps

1. Configure Synology Backup & Replication to use `/mnt/omv_backup`
2. Run initial full backup test
3. Verify backup files appear on OMV
4. Add NFS mount health check to Checkmk (optional)

---

## Test Results (2025-12-12)

- Mount Status: ✅ PASS
- Storage Access: ✅ PASS (30GB visible)
- Write Permissions: ✅ PASS
- Data Integrity: ✅ PASS
- Performance: ✅ PASS (7.7 MB/s)
- Auto-mount: ✅ PASS
- Cross-system Visibility: ✅ PASS

**All 7 tests: PASSED**

---

## Backup Readiness

✅ NFS mount operational
✅ 25GB capacity available
✅ Read/write access confirmed
✅ Performance verified (7.7 MB/s)
✅ Persistence configured
✅ Documentation complete

**Status: READY FOR BACKUP CONFIGURATION**

---

**Last Updated:** 2025-12-12
**Next Review:** 2025-12-19

