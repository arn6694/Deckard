# Wazuh Setup - Quick Reference Guide
**Use this to quickly verify everything is working next session**

---

## 1-Minute Health Check

```bash
# Check Wazuh server is running
ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.40 'systemctl status wazuh-manager --no-pager | head -5'

# Check Firewalla agent is connected
ssh brian@10.10.10.1 'sudo systemctl status wazuh-agent --no-pager | head -5'

# Check n8n is accessible
curl -s http://10.10.10.52:5678 | grep -q "n8n" && echo "n8n OK" || echo "n8n DOWN"
```

---

## Access URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| Wazuh Dashboard | `https://10.10.10.40` | [Your saved credentials] |
| Wazuh via SSH | `ssh -i ~/.ssh/id_rsa brian@10.10.10.40` | brian user |
| n8n Web | `https://n8n.ratlm.com` or `http://10.10.10.52:5678` | [Check n8n setup] |
| n8n via SSH | `ssh brian@10.10.10.52` | brian user |
| Firewalla via SSH | `ssh brian@10.10.10.1` | brian user |

---

## Verify Logs Are Flowing

```bash
# Login to Wazuh dashboard at https://10.10.10.40
# Go to: Dashboard → Modules → File Integrity → View Agent Summary
# Look for "firewalla" agent
# Should show green "ACTIVE" status and log count > 0

# Or check via command:
ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.40 'tail -50 /var/ossec/logs/ossec.log' | grep -i "firewalla"
```

---

## Verify Detection Rules Are Loaded

```bash
ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.40 'sudo cat /var/ossec/etc/rules/firewalla_intel.xml'

# Should show 3 rules: 100050, 100051, 100052
```

---

## Find Artifact Files for Phase 6

```bash
# Blocking script
ls -la /tmp/block-malicious-ip.sh

# n8n workflow template
ls -la /tmp/wazuh_alert_blocker_workflow.json

# If missing, recreate from this session's records
```

---

## Check for Recent ALARM_INTEL Events

```bash
# On Firewalla, look at recent logs
ssh brian@10.10.10.1 'tail -100 /log/firewalla/FireMain66.log | grep -i "ALARM_INTEL" | head -5'

# Should show any recent intelligence alerts from Firewalla
```

---

## Phase 6 Readiness Checklist

Before starting Phase 6, run:

```bash
#!/bin/bash
echo "=== Phase 6 Readiness Check ==="

# 1. Wazuh accessible
echo -n "Wazuh Server (10.10.10.40): "
ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.40 'systemctl is-active wazuh-manager' && echo "✓" || echo "✗"

# 2. Firewalla agent connected
echo -n "Firewalla Agent: "
ssh brian@10.10.10.1 'sudo systemctl is-active wazuh-agent' && echo "✓" || echo "✗"

# 3. n8n accessible
echo -n "n8n Server (10.10.10.52:5678): "
curl -s http://10.10.10.52:5678 | grep -q "n8n" && echo "✓" || echo "✗"

# 4. Blocking script exists
echo -n "Blocking script: "
[ -f /tmp/block-malicious-ip.sh ] && echo "✓" || echo "✗"

# 5. Workflow template exists
echo -n "n8n workflow template: "
[ -f /tmp/wazuh_alert_blocker_workflow.json ] && echo "✓" || echo "✗"

echo ""
echo "If all show ✓, ready for Phase 6!"
```

---

## Troubleshooting Commands

### If Wazuh Manager Won't Start
```bash
ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.40 'sudo /var/ossec/bin/wazuh-control restart'
# Wait 30 seconds then check:
ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.40 'systemctl status wazuh-manager'
```

### If Agent Not Connected
```bash
ssh brian@10.10.10.1 'sudo /var/ossec/bin/wazuh-control restart'
# Check logs:
ssh brian@10.10.10.1 'sudo tail -50 /var/ossec/logs/ossec.log'
# Should show: "Valid key received" and "Waiting for server connection"
```

### If Rules Not Loading
```bash
# Check for syntax errors:
ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.40 'sudo /var/ossec/bin/wazuh-control restart'
# View logs for errors:
ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.40 'grep ERROR /var/ossec/logs/ossec.log | tail -5'
```

### Check Agent Configuration
```bash
ssh brian@10.10.10.1 'cat /var/ossec/etc/ossec.conf'
# Should show:
#   - Server address: 10.10.10.40
#   - Port: 1514 or 1515
#   - Log files being monitored (FireMain66, FireMon1, etc.)
```

---

## File Locations Reference

| Service | Config | Logs | Rules |
|---------|--------|------|-------|
| **Wazuh Manager** | `/var/ossec/etc/ossec.conf` | `/var/ossec/logs/ossec.log` | `/var/ossec/etc/rules/firewalla_intel.xml` |
| **Firewalla Agent** | `/var/ossec/etc/ossec.conf` | `/var/ossec/logs/ossec.log` | N/A |
| **Firewalla Source** | N/A | `/log/firewalla/FireMain66.log` | N/A |

---

## Key Infrastructure IPs

```
10.10.10.1   - Firewalla (sends alerts)
10.10.10.4   - BIND9 Primary (blocking target)
10.10.10.40  - Wazuh Server (monitoring)
10.10.10.52  - n8n Server (automation)
```

---

## Next Session Tasks (Phase 6)

1. [ ] Verify all services up (use health check above)
2. [ ] Access Wazuh dashboard, verify logs flowing
3. [ ] Configure Wazuh webhook to n8n
4. [ ] Build n8n workflow for alert processing
5. [ ] Deploy blocking script to control host
6. [ ] Test with simulated alert
7. [ ] Go live with automated blocking

**Estimated Time:** 1.5-2 hours

---

Last Updated: 2025-11-17
Status: All systems operational ✅
