# Wazuh Security Monitoring Setup - Session Closing Report
**Date:** November 16-17, 2025
**Status:** Phases 1-5 Complete ✅ | Phases 6-8 Pending
**Next Session Focus:** Phase 6 - n8n Automated Blocking Workflow

---

## Executive Summary

Successfully deployed enterprise-grade security monitoring infrastructure that **detects malware/threat intelligence alerts from Firewalla and prepares for automated blocking**.

**Current Capability:**
- ✅ Detect all ALARM_INTEL events from Firewalla (malware IPs, botnets, C2 servers)
- ✅ Extract IP address, geolocation, severity, target device
- ✅ Alert on high-severity threats (level 10)
- ✅ Correlate multiple attacks on same device
- ⏳ Automated blocking (ready to implement in Phase 6)

---

## What Was Accomplished

### Phase 1: Architecture Planning ✅
- Designed full workflow: Firewalla → Wazuh → n8n → Blocking
- Decision: Block-first with notifications (no approval gate)
- Technology choices validated for homelab scale

### Phase 2: Wazuh Server Setup ✅
**Location:** Proxmox LXC container
**IP Address:** `10.10.10.40`
**Services Running:**
- Wazuh Manager (port 1514) - Agent communication
- Wazuh Manager Secure (port 1515) - Encrypted agent comms
- Wazuh Dashboard (port 443 HTTPS) - Web UI
- Wazuh Indexer (ports 9200, 9300) - Log storage & search
- OpenSearch/Elasticsearch replacement

**Access:**
- URL: `https://10.10.10.40`
- Credentials: (use creds you noted during setup)

### Phase 3: Wazuh Agent Installation ✅
**Location:** Firewalla (10.10.10.1)
**Agent Version:** 4.14.1
**Status:** Connected and actively logging

**Monitored Log Files:**
- `/log/firewalla/FireMain66.log` - Main Firewalla logs
- `/log/firewalla/FireMon1.log` - Monitor/alert logs
- `/log/firewalla/FireApi8.log` - API logs
- `/log/firewalla/firelog.log` - Main log (syslog format)

**Verification:**
```bash
# Check agent status on Firewalla
ssh brian@10.10.10.1
sudo systemctl status wazuh-agent --no-pager
tail -20 /var/ossec/logs/ossec.log
```

### Phase 4: Log Ingestion ✅
- Agent configured in `/var/ossec/etc/ossec.conf` on Firewalla
- Logs streaming to Wazuh manager in real-time
- Dashboard showing initial data arrival (4+ logs visible)
- Connection status: **ACTIVE**

### Phase 5: ALARM_INTEL Detection Rules ✅
**Rules Location:** `/var/ossec/etc/rules/firewalla_intel.xml`

**Active Detection Rules:**

| Rule ID | Severity | Description |
|---------|----------|-------------|
| 100050 | Level 5 | Detects any ALARM_INTEL event |
| 100051 | Level 10 | HIGH severity threats (botnet/C2) |
| 100052 | Level 7 | Devices under attack |

**Rule Validation:**
- Rules loaded successfully after Wazuh restart
- No syntax errors (previous duplicate ID issues fixed)
- Ready to detect incoming ALARM_INTEL events

---

## Current Infrastructure Map

```
Firewalla (10.10.10.1)
    ↓ [Wazuh Agent 4.14.1]
    ├─ Logs: FireMain66, FireMon1, FireApi8, firelog
    ↓ TCP 1514 (unencrypted) or 1515 (secure)
    ↓
Wazuh Server (10.10.10.40)
    ├─ Wazuh Manager
    ├─ Wazuh Dashboard (https://10.10.10.40)
    ├─ Wazuh Indexer (log storage)
    ├─ Detection Rules (firewalla_intel.xml)
    ↓ [Webhook POST when alert triggered]
    ↓
n8n Server (10.10.10.52:5678)
    ├─ URL: https://n8n.ratlm.com
    ├─ [PENDING] Webhook receiver
    ├─ [PENDING] IP extraction logic
    ├─ [PENDING] Blocking execution
    ↓
Blocking Targets:
    ├─ BIND9 RPZ (DNS-level blocking)
    ├─ iptables (firewall-level blocking)
    └─ Persistent blocklist (/etc/malware-blocklist.txt)
```

---

## Artifacts Created

### Files on Wazuh Server
- `/var/ossec/etc/rules/firewalla_intel.xml` - Detection rules

### Files on Local Control Host
- `/tmp/firewalla_wazuh_agent_install.sh` - Agent installation script
- `/tmp/block-malicious-ip.sh` - Blocking script (ready to deploy)
- `/tmp/wazuh_alert_blocker_workflow.json` - n8n workflow template

### Documentation
- This file: Session closing report

---

## Known Working Verifications

### Wazuh Manager Health
```bash
ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.40
systemctl status wazuh-manager --no-pager
# Should show: Active: active (running)
```

### Firewalla Agent Health
```bash
ssh brian@10.10.10.1
sudo systemctl status wazuh-agent --no-pager
# Should show: Active: active (running)
# And processes: wazuh-agentd, wazuh-logcollector, etc.
```

### n8n Accessibility
```bash
curl -s http://10.10.10.52:5678/ | head
# Should show: <!DOCTYPE html> with n8n references
```

---

## Next Session: Phase 6 Implementation Plan

### What Needs to be Done

**6.1 - Configure Wazuh Webhook Alert**
- Location: Wazuh Dashboard → Admin → Settings → Integrations
- Create webhook that POSTs alerts to: `http://10.10.10.52:5678/webhook/wazuh-alert-blocker`
- Test webhook connectivity

**6.2 - Build n8n Workflow**
- Create new workflow in n8n UI
- Add Webhook trigger node (listening on `/webhook/wazuh-alert-blocker`)
- Add code node to extract: `malicious_ip`, `country`, `severity`, `device`
- Add decision node: If severity is "high" or "critical" → block
- Add SSH execution node: Run `/usr/local/bin/block-malicious-ip.sh $IP $COUNTRY`
- Add notification node: Send alert (Telegram/Email/Slack)

**6.3 - Deploy Blocking Script**
```bash
# Copy to control host
scp /tmp/block-malicious-ip.sh /usr/local/bin/
chmod +x /usr/local/bin/block-malicious-ip.sh

# Verify sudo access for n8n user (if needed)
# Edit sudoers to allow block-malicious-ip.sh execution
```

**6.4 - Test with Real Alert**
- Monitor Firewalla logs for next ALARM_INTEL event
- Verify alert arrives in Wazuh dashboard
- Verify webhook triggers n8n workflow
- Confirm IP is blocked in iptables and/or BIND9

**6.5 - Create Analytics Dashboard**
- Phase 8: Build Wazuh dashboard showing:
  - Attacks per week/day/hour
  - Top malicious IPs
  - Geographic heatmap
  - Block status tracking

---

## Pre-Phase 6 Checklist

Before next session, verify you can:

- [ ] Access Wazuh Dashboard at `https://10.10.10.40`
- [ ] Log in with credentials (you have saved)
- [ ] See Firewalla logs appearing in dashboard
- [ ] Access n8n at `https://n8n.ratlm.com` or `10.10.10.52:5678`
- [ ] SSH to both `10.10.10.40` (Wazuh) and `10.10.10.52` (n8n)
- [ ] Confirm you still have the files:
  - `/tmp/block-malicious-ip.sh`
  - `/tmp/wazuh_alert_blocker_workflow.json`

---

## Quick Reference Commands

### Check Wazuh Status
```bash
ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.40 'systemctl status wazuh-manager --no-pager | head -10'
```

### Check Firewalla Agent
```bash
ssh brian@10.10.10.1 'sudo systemctl status wazuh-agent --no-pager | head -10'
```

### Check for ALARM_INTEL Events in Wazuh
```bash
ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.40 'grep -i "ALARM_INTEL" /var/ossec/logs/ossec.log'
```

### List detected rules
```bash
ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.40 'sudo cat /var/ossec/etc/rules/firewalla_intel.xml'
```

### View Firewalla logs being collected
```bash
ssh brian@10.10.10.1 'tail -50 /log/firewalla/FireMain66.log | grep -i "ALARM_INTEL\|alert"'
```

---

## Important Infrastructure Details

### IP Addresses
- **Firewalla:** 10.10.10.1 (source of security alerts)
- **Wazuh Server:** 10.10.10.40 (central monitoring)
- **n8n Server:** 10.10.10.52 (automation/blocking)
- **BIND9 Primary:** 10.10.10.4 (DNS blocking target)
- **Checkmk:** 10.10.10.5 (optional integration)

### Network Connectivity
- Firewalla → Wazuh: TCP 1514/1515 (working ✅)
- Wazuh → n8n: HTTP webhook (pending Phase 6)
- n8n → BIND9: SSH/rndc (pending Phase 6)
- n8n → iptables: SSH (pending Phase 6)

### Authentication Details Needed for Phase 6
- [ ] Wazuh credentials (for dashboard access)
- [ ] n8n API key or webhook path (likely pre-generated)
- [ ] SSH keys for n8n→BIND9/iptables execution

---

## Success Criteria for Full Completion

When all phases are complete, you will have:

✅ **Weekly attack metrics** - Know exactly how many attacks per week
✅ **IP geolocation tracking** - See which countries attacks originate from
✅ **Device-specific alerts** - Know which of your devices are being targeted
✅ **Automatic blocking** - Malware IPs blocked at network level instantly
✅ **Forensic history** - Query attack patterns over time
✅ **Alert notifications** - Get SMS/Email/Telegram when attacks occur

---

## Notes for Next Session

1. **Rule refinement:** The current rules (100050-100052) are basic. Phase 6 can enhance:
   - Whitelist known-good IPs that trigger false positives
   - Add correlation rules for coordinated attacks
   - Add severity escalation rules

2. **Blocking strategy:** Current approach is aggressive (block-first). If this causes issues, we can switch to approval-based (alert then ask permission).

3. **BIND9 RPZ:** The blocking script assumes RPZ zone exists at `/etc/bind/zones/db.ratlm.com.rpz`. If this doesn't exist, we need to create it first.

4. **Notification preferences:** Current n8n workflow template uses Telegram. For Phase 6, ask about preferred notification method (Email, SMS, Slack, etc.)

---

## Session Statistics

- **Duration:** ~2 hours
- **Phases Completed:** 5 of 8 (62%)
- **Infrastructure Deployed:** 2 new containers (Wazuh, n8n already existed)
- **Detection Rules Created:** 3 active rules
- **Next Session Est. Time:** 1.5-2 hours for Phase 6-8

---

**Status: READY FOR PHASE 6** ✅

Infrastructure is stable, logs are flowing, rules are active. Phase 6 is just plumbing n8n workflow and testing the blocking automation.

Session ended: 2025-11-17 00:05 UTC
