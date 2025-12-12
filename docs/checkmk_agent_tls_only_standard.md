# Checkmk Agent TLS-Only Installation Standard

**Effective Date:** November 17, 2025
**Version:** 1.0
**Status:** Standard - MANDATORY for all future installations
**Related Document:** FreeIPA TLS Installation (November 17, 2025)

---

## Executive Summary

This document establishes the **mandatory standard** for all Checkmk agent installations in the homelab. All agents **MUST** use TLS-encrypted registration with the modern `cmk-agent-ctl` agent controller. The legacy unencrypted TCP pull method (via xinetd on port 6556) is **deprecated and forbidden**.

**Key Requirement:** Every agent installation requires explicit TLS registration before being added to Checkmk monitoring.

---

## Why TLS-Only?

### Security Benefits
- ✅ **End-to-End Encryption:** All monitoring data encrypted in transit (TLS 1.2+)
- ✅ **Mutual Certificate Authentication:** Both server and agent verify each other's identity
- ✅ **Certificate-Based Trust:** No shared secrets or passwords in monitoring data
- ✅ **Forward Secrecy:** Certificates auto-renew; old certificates don't compromise future data
- ✅ **Detection Prevention:** Attackers cannot intercept, modify, or replay monitoring data

### Operational Benefits
- ✅ **Audit Trail:** All agent connections logged with UUID for accountability
- ✅ **Centralized Management:** Single registration process for all OS types
- ✅ **Automatic Updates:** Certificate renewal managed by agent controller
- ✅ **Consistency:** Same method works across Linux, Windows, and other platforms

### Legacy Fallback Issues
- ❌ **No Encryption:** Unencrypted TCP on port 6556 exposes all metrics
- ❌ **No Authentication:** Any system can query the agent
- ❌ **xinetd Dependency:** Adds unnecessary complexity and service overhead
- ❌ **Inconsistency:** Different OS types required different legacy methods

---

## Installation Standard: TLS-Only Method

### Prerequisites

**Before installing the agent, you must:**

1. Host already exists in Checkmk (created via REST API or web UI)
2. Have the automation user's password: `/omd/sites/monitoring/var/check_mk/web/automation/automation.secret`
3. Network connectivity to Checkmk server on port 8000 (HTTPS)
4. Checkmk server version: 2.1.0 or later (required for TLS agent registration)

**Checkmk Server Details:**
- Server IP: `10.10.10.5`
- Site: `monitoring`
- Registration Port: `8000` (HTTPS)

### Step 1: Download the Agent Package

The agent package is available from your Checkmk server at:
```
http://10.10.10.5/monitoring/check_mk/agents/
```

**Determine the correct package for your OS:**

#### For Linux (RPM-based: RHEL, CentOS, Oracle Linux, Rocky Linux)
```bash
wget http://10.10.10.5/monitoring/check_mk/agents/check-mk-agent-2.4.0p15-1.noarch.rpm
```

#### For Linux (DEB-based: Debian, Ubuntu)
```bash
wget http://10.10.10.5/monitoring/check_mk/agents/check-mk-agent_2.4.0p15-1_all.deb
```

#### For Windows
Download via web browser:
```
http://10.10.10.5/monitoring/check_mk/agents/windows/check_mk_agent.msi
```

### Step 2: Install the Agent Package

#### For Linux (RPM-based)
```bash
sudo rpm -U /tmp/check-mk-agent-2.4.0p15-1.noarch.rpm
```

#### For Linux (DEB-based)
```bash
sudo dpkg -i /tmp/check-mk-agent_2.4.0p15-1_all.deb
```

#### For Windows
- Run the `.msi` installer with Administrator rights
- The service starts automatically

### Step 3: Register the Agent with TLS Encryption

**Critical:** This step **MUST** be performed before the host is added to active monitoring.

#### Get the Automation Secret
```bash
ssh brian@10.10.10.5 'sudo su - monitoring -c "cat var/check_mk/web/automation/automation.secret"'
```

Example output: `%*URahF3Q6dul6sd` (save this securely)

#### Register the Agent (Linux)
```bash
sudo /usr/bin/cmk-agent-ctl register \
  --hostname <HOSTNAME> \
  --server 10.10.10.5 \
  --site monitoring \
  --user automation \
  --password "<AUTOMATION_SECRET>" \
  --trust-cert
```

**Example for FreeIPA:**
```bash
sudo /usr/bin/cmk-agent-ctl register \
  --hostname freeipa \
  --server 10.10.10.5 \
  --site monitoring \
  --user automation \
  --password "%*URahF3Q6dul6sd" \
  --trust-cert
```

#### Register the Agent (Windows)
```powershell
& "C:\Program Files (x86)\checkmk\service\check_mk_agent.exe" register `
  --hostname <HOSTNAME> `
  --server 10.10.10.5 `
  --site monitoring `
  --user automation `
  --password "<AUTOMATION_SECRET>" `
  --trust-cert
```

#### Expected Output
```
Registration complete.
```

### Step 4: Verify TLS Registration

**On the monitored host:**
```bash
sudo /usr/bin/cmk-agent-ctl status
```

**Expected output:**
```
Version: 2.4.0p15
Agent socket: operational
IP allowlist: any
Connection: 10.10.10.5/monitoring
  UUID: ee61c6e8-fd6f-4e07-b565-3f30fa32bbf6
  Connection mode: pull-agent
  Certificate issuer: Site 'monitoring' agent signing CA
  Certificate validity: Tue, 18 Nov 2025 02:15:46 +0000 - Mon, 18 Nov 2030 02:15:46 +0000
```

**Key indicators:**
- ✅ `Agent socket: operational`
- ✅ `Connection mode: pull-agent` (TLS-based)
- ✅ `Certificate validity` shows 5-year validity (until 2030)
- ✅ `allow_legacy_pull` is `false` (TLS-only mode)

### Step 5: Add Host to Checkmk (if not already added)

**Via REST API:**
```bash
curl -X POST "http://10.10.10.5/monitoring/check_mk/api/1.0/domain-types/host_config/collections/all" \
  -H "Authorization: Bearer automation %*URahF3Q6dul6sd" \
  -H "Content-Type: application/json" \
  -d '{
    "host_name": "<HOSTNAME>",
    "folder": "/",
    "attributes": {
      "ipaddress": "<IP_ADDRESS>"
    }
  }'
```

**Via Web UI:**
1. Navigate to: http://10.10.10.5/monitoring/
2. Go to: Setup → Hosts → Create new host
3. Enter hostname and IP address
4. Click "Create host"

### Step 6: Run Service Discovery and Activate Configuration

```bash
ssh brian@10.10.10.5 'sudo su - monitoring -c "cmk -I <HOSTNAME> && cmk -R"'
```

**Expected output:**
```
Generating configuration for core (type nagios)...
Precompiling host checks...OK
Validating Nagios configuration...OK
Restarting monitoring core...OK
```

---

## Verification Checklist

After installation, verify these points:

### Agent Verification
- [ ] Agent registration shows `Agent socket: operational`
- [ ] Registration shows `Connection mode: pull-agent`
- [ ] Agent has valid TLS certificate (5-year validity)
- [ ] `allow_legacy_pull` is `false` in agent status

### Checkmk Server Verification
```bash
ssh brian@10.10.10.5 'sudo su - monitoring -c "tail -5 var/log/agent-receiver/agent-receiver.log | grep <HOSTNAME>"'
```

Should show:
```
registered host <HOSTNAME>
```

### Monitoring Verification
1. In Checkmk web UI, navigate to: Monitor → All hosts
2. Find the new host
3. Verify services are discovered and monitoring
4. Check that agent connection shows TLS status in service details

---

## Critical Requirements (Mandatory)

### ✅ MUST DO
1. **Always register with the `automation` user** (NOT `agent_registration`)
2. **Always use `--trust-cert` flag** to accept Checkmk's certificate
3. **Verify TLS registration** before adding to active monitoring
4. **Never use legacy xinetd or TCP port 6556 directly**
5. **Document the registration** in your notes with the UUID

### ❌ NEVER DO
1. **Do NOT use `--user agent_registration`** - this user is for API calls only
2. **Do NOT skip the `--trust-cert` flag**
3. **Do NOT install xinetd for agent service**
4. **Do NOT configure the agent to listen on TCP port 6556 manually**
5. **Do NOT use legacy check_mk_agent script as the primary agent**

---

## Troubleshooting

### Issue: "Wrong credentials (Bearer header)"
**Root Cause:** Using wrong user (agent_registration instead of automation)

**Solution:**
```bash
sudo /usr/bin/cmk-agent-ctl delete-all
# Then re-register with --user automation
```

### Issue: "No route to host" when registering
**Root Cause:** Network connectivity to Checkmk on port 8000

**Solution:**
```bash
# Test connectivity
curl -k https://10.10.10.5:8000/monitoring/

# If it fails, check firewall and network routing
ssh brian@10.10.10.5 "sudo ufw status | grep 8000"
```

### Issue: Agent shows "Certificate validity" in the past
**Root Cause:** System clock is out of sync

**Solution:**
```bash
# Sync time
sudo ntpdate -s time.nist.gov
# Or for modern systems:
sudo systemctl restart systemd-timesyncd
```

### Issue: Agent won't register (timeout)
**Root Cause:** Checkmk server not responding or host doesn't exist in Checkmk

**Solution:**
1. Verify host exists: `ssh brian@10.10.10.5 'sudo su - monitoring -c "cmk --list-hosts" | grep <HOSTNAME>'`
2. Verify server responds: `curl -k https://10.10.10.5:8000/monitoring/`
3. Check Checkmk logs: `ssh brian@10.10.10.5 'sudo su - monitoring -c "tail -50 var/log/agent-receiver/agent-receiver.log"'`

---

## Agent Status Commands

### Check Registration Status
```bash
sudo /usr/bin/cmk-agent-ctl status
```

### Dump Agent Data (for testing)
```bash
sudo /usr/bin/cmk-agent-ctl dump
```

### Delete All Connections (reset registration)
```bash
sudo /usr/bin/cmk-agent-ctl delete-all
```

### Renew Certificate Before Expiration
```bash
sudo /usr/bin/cmk-agent-ctl renew-certificate --hostname <HOSTNAME>
```

---

## Certificate Management

### Certificate Validity
- **Issued:** Upon successful registration
- **Duration:** 5 years (auto-renewal before expiration)
- **Issuer:** Site 'monitoring' agent signing CA
- **Stored Location:** `/var/lib/cmk-agent/registered_connections.json`

### Automatic Renewal
- The agent automatically attempts certificate renewal 30 days before expiration
- No manual intervention required
- Renewal happens transparently without service interruption

---

## Migration from Legacy Agents

If you have existing agents using the legacy xinetd method:

### Step 1: Identify Legacy Agents
```bash
ssh brian@10.10.10.5 'sudo su - monitoring -c "cmk -d <OLD_HOST> | grep Version"'
# If shows xinetd-based agent, it's legacy
```

### Step 2: Remove Legacy Configuration
```bash
# SSH to the legacy agent host
sudo systemctl stop xinetd
sudo systemctl disable xinetd
```

### Step 3: Register with TLS
Follow the standard installation steps above.

### Step 4: Verify TLS Operation
```bash
sudo /usr/bin/cmk-agent-ctl status
```

---

## Future Upgrades

### When Checkmk Server is Upgraded
1. New agent packages are immediately available on the server
2. On monitored hosts, install new package: `sudo dpkg -i` or `sudo rpm -U`
3. Agent TLS registration is preserved automatically
4. No re-registration needed

### When Agent Certificate Expires (unlikely)
The agent automatically renews certificates 30 days before expiration. If needed manually:
```bash
sudo /usr/bin/cmk-agent-ctl renew-certificate --hostname <HOSTNAME>
```

---

## Compliance and Auditing

### Check Agent Compliance
List all registered agents:
```bash
ssh brian@10.10.10.5 'sudo su - monitoring -c "tail -100 var/log/agent-receiver/agent-receiver.log" | grep "registered host"'
```

### Verify No Legacy Agents
```bash
# Should return NO results (no xinetd agents)
ssh brian@10.10.10.5 'sudo su - monitoring -c "for host in $(cmk --list-hosts); do echo \"$host:\" && cmk -d $host 2>&1 | grep -i xinetd; done"'
```

### Monitor Certificate Expiration
Checkmk automatically monitors agent certificate validity. Any agent with a certificate expiring within 30 days will show a warning.

---

## Documentation Requirements

For each agent installed, document:

1. **Hostname:** (in Checkmk)
2. **OS:** (Linux distribution / Windows version)
3. **IP Address:** (10.10.10.X)
4. **Registration Date:** (YYYY-MM-DD)
5. **Agent UUID:** (from `cmk-agent-ctl status`)
6. **Certificate Expiry:** (from `cmk-agent-ctl status`)
7. **Notes:** (any special configuration or issues)

### Example Documentation
```
Host: freeipa
OS: Oracle Linux 9.6
IP: 10.10.10.92
Registered: 2025-11-17
UUID: ee61c6e8-fd6f-4e07-b565-3f30fa32bbf6
Certificate Valid Until: 2030-11-18
Notes: RHEL9-compatible, FreeIPA identity server
```

---

## Summary

| Aspect | Standard |
|--------|----------|
| **Registration Method** | TLS with `cmk-agent-ctl register` |
| **Authentication User** | `automation` (not `agent_registration`) |
| **Trust Method** | Certificate-based with `--trust-cert` |
| **Port** | 8000 (HTTPS, Checkmk → Agent) |
| **Encryption** | TLS 1.2+ (mandatory) |
| **Legacy Method** | Forbidden ❌ |
| **xinetd** | Not used with modern agent |
| **Certificate Duration** | 5 years with auto-renewal |
| **Monitoring Mode** | Pull-agent (server initiates) |

---

## Approved Implementations

✅ **Approved for use:**
- Linux (RPM-based): `check-mk-agent-*.noarch.rpm` with TLS
- Linux (DEB-based): `check-mk-agent_*.deb` with TLS
- Windows: `check_mk_agent.msi` with TLS
- Any platform with Checkmk 2.1.0+

❌ **Deprecated (no longer used):**
- xinetd-based agents
- Raw check_mk_agent script on TCP port 6556
- Agent-less monitoring (SNMP only)
- Legacy unencrypted pull mode

---

## Reference Implementation

**FreeIPA TLS Installation (November 17, 2025):**
```bash
# Host: freeipa (10.10.10.92)
# OS: Oracle Linux 9.6
# Status: ✅ TLS-registered and monitored

ssh brian@10.10.10.92 'sudo /usr/bin/cmk-agent-ctl register \
  --hostname freeipa \
  --server 10.10.10.5 \
  --site monitoring \
  --user automation \
  --password "%*URahF3Q6dul6sd" \
  --trust-cert'

# Result: Registration complete.
# UUID: ee61c6e8-fd6f-4e07-b565-3f30fa32bbf6
# Certificate Valid Until: Mon, 18 Nov 2030 02:15:46 +0000
```

---

**Document Version:** 1.0
**Effective Date:** November 17, 2025
**Last Updated:** November 17, 2025
**Status:** STANDARD - Mandatory for all installations
**Review Cycle:** Annually or with Checkmk major version updates
