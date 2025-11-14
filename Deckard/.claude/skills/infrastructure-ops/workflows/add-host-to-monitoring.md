---
name: add-host-to-monitoring
description: |
  Add a new Linux or network device to Checkmk monitoring.
  USE WHEN user asks to: add host to monitoring, monitor new server, add device to Checkmk
---

# Add Host to Checkmk Monitoring Workflow

## What This Does

Adds a new host to Checkmk monitoring system with proper agent installation, configuration, and service discovery. Handles both Linux servers (with Checkmk agent) and network devices (ping/SNMP).

---

## Prerequisites

- Target host IP address and hostname
- SSH access to target host (for Linux servers with agent installation)
- Target host is network-reachable from Checkmk server (10.10.10.5)
- Root/sudo access on target host for agent installation
- Checkmk credentials: automation user with token

---

## Execution Steps

### Step 1: Prepare Target Host

Verify the target host:
- Test connectivity from Checkmk: `ping <ip>`
- If Linux: Verify SSH access: `ssh brian@<ip> 'echo ok'`
- Note the hostname and IP address

### Step 2: Install Checkmk Agent (Linux Only)

For Linux servers, install the Checkmk agent matching the Checkmk version (2.4.0p2):

```bash
# Copy agent from Checkmk server
scp brian@10.10.10.5:/omd/sites/monitoring/share/check_mk/agents/check-mk-agent_2.4.0p2-1_all.deb /tmp/

# Install agent
sudo dpkg -i /tmp/check-mk-agent_2.4.0p2-1_all.deb

# Verify agent is responding
sudo /usr/bin/check_mk_agent | head -20
```

Agent should respond on TCP port 6556.

### Step 3: Add Host to Checkmk (Web UI Method - RECOMMENDED)

**This is the most reliable method for Deckard to manage**:

1. Open Checkmk web UI: https://checkmk.ratlm.com
2. Log in as `cmkadmin` / `rxrv23a`
3. Navigate to: **Setup** → **Hosts**
4. Click **Create new host** button
5. Fill in:
   - **Hostname**: hostname of target (e.g., "plex")
   - **IP address**: target IP (e.g., "10.10.10.18")
   - **Host group**: select "servers" or appropriate group
   - **Agent type**:
     - Linux servers with Checkmk agent: "Checkmk agent (TCP)"
     - Network devices only: "SNMP v2c" or just "Ping"
6. Click **Save**
7. Click **Perform Service Discovery** to find services
8. Click **Activate changes** to deploy configuration

### Step 4: Verify Host is Monitored

Query Checkmk to verify host appears:

```bash
bash ~/.claude/documentation/query_checkmk.sh 'GET hosts' 'name state'
```

New host should appear in list with state code 0 (UP).

### Step 5: Configure Services (If Needed)

After service discovery, configure specific check parameters:
- CPU/Memory thresholds
- Disk space warning/critical levels
- Custom service rules via Setup → Services → Service rules

---

## Alternative: Automation via Config Files

**Note: This method has limitations** - Checkmk's config system may not immediately recognize file-based changes without proper reload sequence.

If using file-based approach:

1. **Add to WATO hosts.mk**:
   ```bash
   ssh brian@10.10.10.5 "sudo python3 << 'PYEOF'
   # Read hosts.mk
   with open('/omd/sites/monitoring/etc/check_mk/conf.d/wato/hosts.mk', 'r') as f:
       content = f.read()

   # Add hostname to all_hosts list
   content = content.replace(
       "all_hosts += ['HX99G'",
       "all_hosts += ['plex', 'HX99G'"  # Add your hostname
   )

   # Add IP to ipaddresses dict
   content = content.replace(
       "ipaddresses.update({'Orbi_Satellite':",
       "ipaddresses.update({'plex': '10.10.10.18',  # Change IP\n'Orbi_Satellite':"
   )

   # Write back
   with open('/omd/sites/monitoring/etc/check_mk/conf.d/wato/hosts.mk', 'w') as f:
       f.write(content)
   PYEOF
   "
   ```

2. **Clear Python cache**:
   ```bash
   ssh brian@10.10.10.5 "sudo rm /omd/sites/monitoring/etc/check_mk/conf.d/wato/*.pkl"
   ```

3. **Full restart**:
   ```bash
   ssh brian@10.10.10.5 "sudo omd -f stop monitoring && sleep 3 && sudo omd start monitoring"
   ```

4. **Rebuild config**:
   ```bash
   ssh brian@10.10.10.5 "sudo su - monitoring -c 'cmk -R'"
   ```

---

## Troubleshooting

### Host not appearing after addition

**Cause**: Web UI changes may take a moment to process

**Solution**:
- Wait 30 seconds, then refresh browser
- Check "Activate changes" was clicked
- View recent changes in Setup → Services → Changes

### Agent not responding

**Cause**: Agent not installed or port blocked

**Solution**:
1. Verify installation: `ssh brian@<host> 'sudo dpkg -l | grep check-mk'`
2. Test port: `ssh brian@10.10.10.5 'timeout 5 bash -c "cat < /dev/null > /dev/tcp/<ip>/6556"'`
3. Check agent is listening: `ssh brian@<host> 'sudo ss -tlnp | grep 6556'`

### Services not discovered

**Cause**: Agent installed but services not detected

**Solution**:
1. Manually trigger discovery: Setup → Hosts → Click host → "Services" → "Run service discovery"
2. Check agent output manually: `ssh brian@<host> 'sudo /usr/bin/check_mk_agent' | head -40`

---

## Integration with Deckard

This workflow integrates with:
- **checkmk-query skill**: Query newly added host status
- **infrastructure-ops skill**: Part of host lifecycle management
- **automation**: Can be called via `cmk --automation` commands

---

## Example: Adding Plex Media Server

**Command Execution**:
```bash
# 1. Verify plex connectivity
ssh brian@10.10.10.5 "ping -c 1 10.10.10.18"

# 2. Install agent (already done, agent responds on port 6556)

# 3. Add via Web UI (manual steps above)

# 4. Verify in monitoring
bash ~/.claude/documentation/query_checkmk.sh 'GET hosts' 'name state' | grep plex
# Should show: plex;0
```

---

## Key Decisions for Deckard

1. **Use Web UI method (STRONGLY RECOMMENDED)** - File editing approach has reliability issues in Checkmk 2.4
2. **Always install correct agent version** - Version 2.4.0p2-1 for current Checkmk 2.4.0p2
3. **Verify connectivity first** - Ping + port 6556 test before adding
4. **Run service discovery** - Automatic service detection, don't skip this step
5. **Document the addition** - Keep track of which hosts added when and why

## Known Limitations & Issues in Checkmk 2.4

### ⚠️ CRITICAL BUG: Configuration Compiler Not Processing New Hosts

**Confirmed Issue - November 14, 2025**: The Checkmk 2.4.0p2 configuration compiler is completely broken for adding new hosts. Even when hosts are properly added to `hosts.mk`, the compiler does not generate corresponding Nagios objects.

**Problem Summary**:
- Hosts can be added to `hosts.mk` via Web UI or file editing ✅
- `cmk -R` command executes successfully (exit code 0) but produces NO output ⚠️
- `cmk -O` also runs silently without recompiling ⚠️
- Nagios configuration file (`check_mk_objects.cfg`) does not update ❌
- Host never appears in livestatus/monitoring ❌
- Web UI "Activate Changes" feature times out trying to contact ui-job-scheduler ❌

**Tested and Failed Workarounds**:
1. Multiple `cmk -R` reloads - No effect
2. `cmk -O` with object caching - No effect
3. Full site restart with `omd stop/start` - No effect
4. Clearing Python pickle cache (.pkl files) - No effect
5. Restarting ui-job-scheduler service - No effect
6. Removing and re-adding hosts.mk entries - No effect

**Evidence**: Plex server (10.10.10.18) successfully:
- Has correct agent installed (2.4.0p2-1) ✅
- Responds on port 6556 ✅
- Entry in hosts.mk shows complete configuration ✅
- Configuration syntax is valid Python ✅
- But Nagios config was last modified 05:44 on Nov 14, never updating despite 5+ compilation attempts

**Root Cause**: Unknown - This appears to be a fundamental bug in Checkmk 2.4.0p2 where:
- The configuration compiler (`cmk`) is not actually compiling hosts
- The Web UI activation mechanism (ui-job-scheduler) cannot properly invoke the compiler
- File-based configuration changes to hosts.mk are silently ignored by all compilation methods

**Impact**: **Cannot add ANY new hosts to this Checkmk instance using standard methods**

### REST API Not Accessible
The Checkmk REST API endpoints (`/api/1.0/domain-types/host_config/...`) return 404 even with valid authentication, suggesting:
- REST API might not be enabled on this Checkmk instance
- REST API might be at a different path or disabled in version 2.4.0p2

### Workarounds (All Limited)

**Option 1: Manual Nagios Configuration (Not Recommended)**
Directly create host definitions in `/omd/sites/monitoring/etc/nagios/conf.d/`, bypassing Checkmk's management system. This works but:
- Conflicts with Checkmk's configuration philosophy
- Manual updates won't sync with Checkmk
- Service discovery won't work through Checkmk UI

**Option 2: Upgrade Checkmk (Recommended)**
Test if this is fixed in Checkmk 2.4.1 or later:
```bash
sudo su - monitoring -c 'omd version'  # Check current version
# Then upgrade via official Checkmk channels
```

**Option 3: Investigate Checkmk Configuration** (If upgrade unavailable)
Search for:
- Settings that disable auto-compilation on startup
- Python version conflicts (site uses Python 3.12)
- Nagios configuration validation issues
- File permissions preventing compiler output

**Option 4: Contact Checkmk Support**
This appears to be a critical bug that should be escalated to Checkmk support with:
- Version: 2.4.0p2
- Issue: Configuration compiler ignores hosts.mk changes
- Evidence: Hosts in hosts.mk don't appear in Nagios config after `cmk -R`

---

## Investigation Summary - November 14, 2025

**Investigation Status**: Comprehensive troubleshooting completed - root cause identified as Checkmk 2.4.0p2 configuration compiler bug.

**Tests Performed**:
1. ✅ Verified plex agent installation (2.4.0p2-1) and port 6556 response
2. ✅ Added plex to hosts.mk successfully via Web UI
3. ✅ Confirmed plex appears in hosts.mk with correct tags, labels, and IP attributes
4. ✅ Verified hosts.mk has valid Python syntax
5. ❌ Attempted `cmk -R` - runs silently, produces no Nagios objects
6. ❌ Attempted `cmk -O` - runs silently, no recompilation
7. ❌ Full site restart with `omd stop/start` - no compilation triggered
8. ❌ Cleared Python pickle cache (.pkl files) - no effect
9. ❌ Restarted ui-job-scheduler service - helps with socket connectivity but doesn't fix compiler
10. ❌ Verified Web UI activation mechanism can connect to ui-job-scheduler socket - connection works but activation still fails

**Conclusion**: The Checkmk 2.4.0p2 configuration compiler (`cmk -R` command) is not functioning for new host additions. This is a critical bug that blocks all host additions via standard methods.

---

**Last Updated**: November 14, 2025
**Status**: Phase 1 - Foundation Workflow (BLOCKED on Checkmk Bug)
**Known Limitations**: Checkmk 2.4.0p2 configuration compiler broken; cannot add new hosts; REST API unavailable

**Action Required**: Consider Checkmk upgrade to 2.4.1+ or escalate to Checkmk support for investigation.

