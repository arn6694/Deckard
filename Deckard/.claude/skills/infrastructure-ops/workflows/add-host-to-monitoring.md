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

## Troubleshooting Methodology for Checkmk Issues

**IMPORTANT**: Always check log files BEFORE making assumptions about bugs. Many "bug" reports are actually configuration issues, corrupted files, or service startup failures.

### Step-by-Step Troubleshooting Process

1. **Check Service Status**
   ```bash
   sudo su - monitoring -c 'omd status'
   ```
   Verify all required services are running (nagios, apache, ui-job-scheduler, etc.)

2. **Review Relevant Log Files** (IN THIS ORDER)
   - **Web UI logs**: `/omd/sites/monitoring/var/log/web.log`
   - **Automation helper**: `/omd/sites/monitoring/var/log/automation-helper/error.log`
   - **UI job scheduler**: `/omd/sites/monitoring/var/log/ui-job-scheduler/error.log`
   - **Nagios logs**: `/omd/sites/monitoring/var/log/nagios.log`

   Look for:
   - `SyntaxError` - Malformed configuration files
   - `NameError` - Missing variables/definitions
   - `ERROR` or `Exception` - Service startup failures
   - Actual error messages (not just exit codes)

3. **Validate Configuration Syntax**
   ```bash
   sudo python3 -m py_compile /omd/sites/monitoring/etc/check_mk/conf.d/wato/FILENAME.mk
   ```
   This catches Python syntax errors before they break the system

4. **Check Configuration Files for Corruption**
   - Look for files with literal escape sequences (`\n` instead of newlines)
   - Check for incomplete or malformed Python dictionaries
   - Verify files aren't truncated

5. **Test Compilation with Output**
   ```bash
   sudo su - monitoring -c 'cmk -R 2>&1'
   ```
   Capture full output including errors

---

## Actual Issue Resolved - November 14, 2025

**Status**: ✅ RESOLVED

**Root Cause**: A corrupted configuration file, NOT a Checkmk bug

The file `/omd/sites/monitoring/etc/check_mk/conf.d/wato/discover_all_interfaces.mk` contained literal escape sequences:
```
rules.update({'network_interface_discovery_rules': [\n  {'condition': [],\n ...
```

Instead of proper newlines in the Python code. This caused a `SyntaxError` that broke the entire configuration loading system, preventing:
- Configuration compilation (`cmk -R`)
- Change activation (Web UI timeouts)
- New host additions from being compiled into Nagios objects

**How It Was Found**:
1. Reviewed automation-helper error logs
2. Found: `SyntaxError: unexpected character after line continuation character`
3. Located the file: `discover_all_interfaces.mk`
4. Identified the literal `\n` characters in the Python code
5. Deleted the corrupted file
6. System immediately worked correctly

**Solution**: Delete the corrupted file
```bash
sudo rm /omd/sites/monitoring/etc/check_mk/conf.d/wato/discover_all_interfaces.mk
sudo su - monitoring -c 'omd restart'
```

**Result**:
- ✅ Configuration compiler works correctly
- ✅ Plex now appears in monitoring (verified: `plex;0`)
- ✅ New hosts can be added successfully
- ✅ Changes can be activated without timeouts

---

**Last Updated**: November 14, 2025
**Status**: Phase 1 - Foundation Workflow (COMPLETE)
**Lesson Learned**: Always check logs before assuming bugs exist. Configuration file corruption is more common than framework bugs.

### Prevention for Future Issues

1. **Monitor log files** during any configuration changes
2. **Validate syntax** before and after making changes
3. **Keep backups** of working configuration states
4. **Check error logs** FIRST when things break - they always tell the story
5. **Don't make assumptions** - let the error messages guide you

