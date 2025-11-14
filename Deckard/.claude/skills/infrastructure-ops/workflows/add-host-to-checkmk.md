---
name: add-host-to-checkmk
description: |
  Add a new Linux host to Checkmk monitoring with the correct agent version and package type.
  Automatically detects OS type to install appropriate agent (deb/rpm).
  USE WHEN user asks to: add host to Checkmk, add monitoring, monitor new server
---

# Add Host to Checkmk Monitoring Workflow

## What This Does

Adds a new Linux host to Checkmk monitoring by:
1. Installing the matching Checkmk agent version (same as server version)
2. Auto-detecting the Linux distribution and installing correct package (deb for Debian/Ubuntu, rpm for RedHat/RHEL)
3. Verifying agent is responding on port 6556
4. Adding host to Checkmk configuration
5. Running service discovery
6. Verifying host appears in monitoring dashboard

---

## Prerequisites

- Target host IP address and hostname
- SSH access to target host as non-root user with sudo privileges
- Target host is reachable from Checkmk server (10.10.10.5)
- Checkmk server is running (currently 2.4.0p15)

---

## CRITICAL: Get Checkmk Server Version First

Before doing anything, determine the Checkmk version running on the monitoring server:

```bash
ssh brian@10.10.10.5 "sudo su - monitoring -c 'omd version'"
```

Look for the version line. Examples:
- `OMD - Open Monitoring Distribution Version 2.4.0p15.cre`
- `OMD - Open Monitoring Distribution Version 2.3.0p8.cre`

**Important:** You MUST use this exact version for the agent package. Agent version mismatch will cause monitoring failures.

---

## Step 1: Verify Target Host and Detect OS

Connect to the target host and determine which package type to install:

```bash
ssh brian@TARGET_IP "cat /etc/os-release"
```

**Look for these indicators:**

### Debian/Ubuntu (Use .deb packages)
Look for these in `/etc/os-release`:
```
ID=debian
ID_LIKE=debian
```

Or these lines present:
```
PRETTY_NAME="Debian GNU/Linux 12 (bookworm)"
PRETTY_NAME="Ubuntu 24.04 LTS"
```

### RedHat/RHEL/CentOS (Use .rpm packages)
Look for these in `/etc/os-release`:
```
ID=rhel
ID_LIKE=rhel fedora
```

Or these lines present:
```
PRETTY_NAME="Red Hat Enterprise Linux 9.7"
PRETTY_NAME="Rocky Linux 9"
```

### Oracle Linux (Use .rpm packages)
Look for:
```
ID=ol
PRETTY_NAME="Oracle Linux Server 7"
```

**Example Detection:**

```bash
# Debian
$ cat /etc/os-release | grep "^ID="
ID=debian
# Result: Use .deb package

# RedHat RHEL
$ cat /etc/os-release | grep "^ID="
ID=rhel
# Result: Use .rpm package

# Oracle Linux
$ cat /etc/os-release | grep "^PRETTY_NAME"
PRETTY_NAME="Oracle Linux Server 7.9"
# Result: Use .rpm package
```

---

## Step 2: Get the Correct Agent Package

From the Checkmk server, identify available agent packages for the version:

```bash
ssh brian@10.10.10.5 "ls /omd/sites/monitoring/share/check_mk/agents/ | grep 'check-mk-agent.*VERSION'"
```

Replace `VERSION` with the actual version (e.g., 2.4.0p15).

**Example output for 2.4.0p15:**
```
check-mk-agent_2.4.0p15-1_all.deb          # For Debian/Ubuntu
check-mk-agent-2.4.0p15-1.noarch.rpm       # For RedHat/RHEL/Oracle Linux
```

**Decision tree:**
- If OS is Debian/Ubuntu → Use `.deb` file
- If OS is RedHat/RHEL/CentOS/Oracle Linux → Use `.rpm` file

---

## Step 3: Copy and Install Agent

### For Debian/Ubuntu (.deb packages):

```bash
# Copy agent from Checkmk to local machine
scp brian@10.10.10.5:/omd/sites/monitoring/share/check_mk/agents/check-mk-agent_VERSION-1_all.deb /tmp/

# Copy to target host
scp /tmp/check-mk-agent_VERSION-1_all.deb brian@TARGET_IP:/tmp/

# Install on target host
ssh brian@TARGET_IP "sudo dpkg -i /tmp/check-mk-agent_VERSION-1_all.deb && echo 'Agent installed'"
```

### For RedHat/RHEL/Oracle Linux (.rpm packages):

```bash
# Copy agent from Checkmk to local machine
scp brian@10.10.10.5:/omd/sites/monitoring/share/check_mk/agents/check-mk-agent-VERSION-1.noarch.rpm /tmp/

# Copy to target host
scp /tmp/check-mk-agent-VERSION-1.noarch.rpm brian@TARGET_IP:/tmp/

# Install on target host
ssh brian@TARGET_IP "sudo rpm -i /tmp/check-mk-agent-VERSION-1.noarch.rpm && echo 'Agent installed'"
```

---

## Step 4: Open Firewall Port 6556 (CRITICAL!)

**IMPORTANT:** Port 6556 must be open on the target host for Checkmk to communicate with the agent. Many Linux distributions have firewalls enabled by default.

### For systems using firewalld (RHEL, CentOS, Oracle Linux):

```bash
ssh brian@TARGET_IP "sudo firewall-cmd --permanent --add-port=6556/tcp && sudo firewall-cmd --reload && echo 'Port 6556 opened'"
```

**Verify the rule is active:**
```bash
ssh brian@TARGET_IP "sudo firewall-cmd --list-all | grep 6556"
```

Should show: `ports: 6556/tcp`

### For systems using iptables (older Debian/Ubuntu):

```bash
ssh brian@TARGET_IP "sudo iptables -A INPUT -p tcp --dport 6556 -j ACCEPT"
ssh brian@TARGET_IP "sudo iptables-save > /etc/iptables/rules.v4"
```

**Verify the rule:**
```bash
ssh brian@TARGET_IP "sudo iptables -L -n | grep 6556"
```

### Test connectivity from Checkmk server:

```bash
ssh brian@10.10.10.5 "timeout 5 bash -c 'cat < /dev/null > /dev/tcp/TARGET_IP/6556' && echo 'Port 6556 is REACHABLE' || echo 'Port 6556 is BLOCKED'"
```

**Expected output:** `Port 6556 is REACHABLE`

If still blocked:
- Check for cloud firewalls/security groups
- Check host-based firewall status: `sudo systemctl status firewalld` or `sudo systemctl status iptables`
- Check SELinux rules if present: `sudo getenforce`

---

## Step 5: Verify Agent is Running and Accessible

```bash
ssh brian@TARGET_IP "sudo /usr/bin/check_mk_agent | head -20"
```

**Successful output should show:**
```
<<<check_mk>>>
Version: 2.4.0p15
AgentOS: linux
Hostname: ansible
...
```

**Key points to verify:**
- Version matches Checkmk server version ✓
- No errors in output ✓
- Hostname is correct ✓

**Also verify from Checkmk server:**
```bash
ssh brian@10.10.10.5 "sudo su - monitoring -c 'cmk -d TARGET_HOSTNAME' 2>&1 | head -20"
```

Should show agent output (not a connection error).

---

## Step 6: Add Host to Checkmk Configuration

Create a Python script to add the host to Checkmk:

```bash
cat > /tmp/add_host.py << 'EOF'
import subprocess

# Read the hosts.mk file
with open('/omd/sites/monitoring/etc/check_mk/conf.d/wato/hosts.mk', 'r') as f:
    content = f.read()

# Check if host already exists
if "'HOSTNAME'" in content:
    print('HOSTNAME already in hosts.mk')
else:
    # Add to all_hosts list (add before proxmox for consistency)
    content = content.replace(
        "'ansible', 'proxmox'",
        "'ansible', 'HOSTNAME', 'proxmox'"
    )

    # Add IP address mapping
    content = content.replace(
        "'ansible': '10.10.10.30',",
        "'ansible': '10.10.10.30', 'HOSTNAME': 'IP_ADDRESS',"
    )

    # Write back
    with open('/omd/sites/monitoring/etc/check_mk/conf.d/wato/hosts.mk', 'w') as f:
        f.write(content)

    print('Added HOSTNAME to hosts.mk')

# Rebuild configuration
result = subprocess.run(['cmk', '-R'], capture_output=True, text=True)
if result.returncode == 0:
    print('Configuration compiled successfully')
else:
    print(f'Compilation error: {result.stderr}')
EOF
```

Replace `HOSTNAME` with actual hostname and `IP_ADDRESS` with IP address.

Then run on Checkmk server:

```bash
scp /tmp/add_host.py brian@10.10.10.5:/tmp/
ssh brian@10.10.10.5 "sudo su - monitoring -c 'python3 /tmp/add_host.py'"
```

---

## Step 7: Verify Host in Monitoring

Check if host appears in Checkmk:

```bash
# Check if in hosts.mk
ssh brian@10.10.10.5 "sudo grep -i HOSTNAME /omd/sites/monitoring/etc/check_mk/conf.d/wato/hosts.mk"

# Check if in Nagios config
ssh brian@10.10.10.5 "sudo grep -c 'host_name.*HOSTNAME' /omd/sites/monitoring/etc/nagios/conf.d/check_mk_objects.cfg"

# Query livestatus for host status (should show state 0 = UP)
cat > /tmp/check_host.py << 'PYEOF'
import socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.connect('/omd/sites/monitoring/tmp/run/live')
query = 'GET hosts\nColumns: name state\nFilter: name = HOSTNAME\n\n'
sock.sendall(query.encode())
output = sock.recv(65536).decode()
sock.close()

if output.strip():
    for line in output.strip().split('\n'):
        if line.strip():
            host, state = line.split(';')
            if state == '0':
                print(f'{host}: UP')
            else:
                print(f'{host}: DOWN ({state})')
else:
    print('No results found')
PYEOF

scp /tmp/check_host.py brian@10.10.10.5:/tmp/
ssh brian@10.10.10.5 "sudo su - monitoring -c 'python3 /tmp/check_host.py'"
```

Expected output: `HOSTNAME: UP`

---

## Step 8: Run Service Discovery and Activate Changes (CRITICAL!)

This step ensures Checkmk fully picks up the new host and discovers all available services/checks.

### Option A: Via Checkmk Web UI (Recommended)

1. Open Checkmk Web UI: https://checkmk.ratlm.com
2. Use Quick Search to find the hostname
3. Click on **Host** → **Service Discovery**
4. Wait for discovery to complete (may take 30+ seconds)
5. Click **Apply changes** or **Activate changes**
6. Verify host now appears in the hosts list

### Option B: Via Command Line

```bash
# Run service discovery for the specific host
ssh brian@10.10.10.5 "sudo su - monitoring -c 'cmk -I HOSTNAME 2>&1'"

# Full configuration activation
ssh brian@10.10.10.5 "sudo su - monitoring -c 'cmk -O 2>&1'"
```

### Option C: Full System Refresh

For complete refresh (if discovery doesn't detect services):

```bash
# 1. Run discovery on specific host
ssh brian@10.10.10.5 "sudo su - monitoring -c 'cmk -I HOSTNAME'"

# 2. Rebuild and activate configuration
ssh brian@10.10.10.5 "sudo su - monitoring -c 'cmk -R && cmk -O'"

# 3. Restart Checkmk services to apply all changes
ssh brian@10.10.10.5 "sudo su - monitoring -c 'omd restart'"

# 4. Verify host and services appear
ssh brian@10.10.10.5 "sudo su - monitoring -c 'cmk -d HOSTNAME' | head -50"
```

**What happens in this step:**
- ✅ Checkmk scans the new host for available services (CPU, Memory, Disk, etc.)
- ✅ Configuration is compiled and validated
- ✅ Changes are activated across all Nagios/monitoring components
- ✅ Monitoring actively monitors the new host

**Wait for completion:**
- Configuration compilation takes 5-10 seconds
- Service discovery can take 30+ seconds
- Changes take effect after activation

**If host still doesn't appear:**
1. Check firewall is still open: `ssh brian@10.10.10.5 "timeout 5 bash -c 'cat < /dev/null > /dev/tcp/HOSTNAME_IP/6556'"`
2. Check logs: `ssh brian@10.10.10.5 "sudo tail -50 /omd/sites/monitoring/var/log/automation-helper/error.log"`
3. Verify host_attributes: `ssh brian@10.10.10.5 "sudo grep -i 'HOSTNAME.*ipaddress' /omd/sites/monitoring/etc/check_mk/conf.d/wato/hosts.mk"`

---

## Real-World Example: Adding Ansible Server

**Scenario:** Add new Ansible control server at 10.10.10.30 (RedHat 9.7)

### Step 1: Check Checkmk version
```bash
ssh brian@10.10.10.5 "sudo su - monitoring -c 'omd version'"
# Output: OMD - Open Monitoring Distribution Version 2.4.0p15.cre
```

### Step 2: Verify OS type on ansible
```bash
ssh brian@10.10.10.30 "cat /etc/os-release | head -5"
# Output shows: ID=rhel, PRETTY_NAME="Red Hat Enterprise Linux 9.7"
# Decision: Use .rpm package
```

### Step 3: Get agent package
```bash
ssh brian@10.10.10.5 "ls /omd/sites/monitoring/share/check_mk/agents/ | grep '2.4.0p15'"
# check-mk-agent-2.4.0p15-1.noarch.rpm  <-- This one for RHEL
```

### Step 4: Open Firewall Port 6556
```bash
ssh brian@10.10.10.30 "sudo firewall-cmd --permanent --add-port=6556/tcp && sudo firewall-cmd --reload"
# Verify: sudo firewall-cmd --list-all | grep 6556
# Should show: ports: 6556/tcp ✓
```

### Step 5: Install agent
```bash
scp brian@10.10.10.5:/omd/sites/monitoring/share/check_mk/agents/check-mk-agent-2.4.0p15-1.noarch.rpm /tmp/
scp /tmp/check-mk-agent-2.4.0p15-1.noarch.rpm brian@10.10.10.30:/tmp/
ssh brian@10.10.10.30 "sudo rpm -i /tmp/check-mk-agent-2.4.0p15-1.noarch.rpm"
```

### Step 6: Verify agent and connectivity
```bash
ssh brian@10.10.10.30 "sudo /usr/bin/check_mk_agent | head -5"
# Shows Version: 2.4.0p15 ✓

# Test from Checkmk server
ssh brian@10.10.10.5 "timeout 5 bash -c 'cat < /dev/null > /dev/tcp/10.10.10.30/6556' && echo 'REACHABLE' || echo 'BLOCKED'"
# Output: REACHABLE ✓
```

### Step 7: Add to Checkmk and verify
Create and run add_host.py script with HOSTNAME=ansible, IP_ADDRESS=10.10.10.30

Verify in livestatus:
```bash
ssh brian@10.10.10.5 "sudo su - monitoring -c 'python3 /tmp/check_ansible.py'"
# Output: ansible: UP ✓
```

### Step 8: Run Service Discovery and Activate
```bash
# Via Web UI: Search for ansible → Host → Service Discovery → Apply changes

# Or via CLI:
ssh brian@10.10.10.5 "sudo su - monitoring -c 'cmk -I ansible && cmk -R && cmk -O'"

# Full refresh (if needed):
ssh brian@10.10.10.5 "sudo su - monitoring -c 'cmk -I ansible && cmk -R && cmk -O && omd restart'"
```

Verify services are discovered:
```bash
ssh brian@10.10.10.5 "sudo su - monitoring -c 'cmk -d ansible' | grep '<<<' | wc -l"
# Should show multiple sections (10+) indicating services are discovered ✓
```

---

## Troubleshooting

### Problem: Agent Installation Fails

**For .deb packages:**
```bash
# Check if dpkg is available
ssh brian@TARGET_IP "which dpkg"

# Try with verbose output
ssh brian@TARGET_IP "sudo dpkg -i /tmp/check-mk-agent_*.deb --verbose"
```

**For .rpm packages:**
```bash
# Check if rpm is available
ssh brian@TARGET_IP "which rpm"

# Try with verbose output
ssh brian@TARGET_IP "sudo rpm -i /tmp/check-mk-agent-*.rpm -v"

# Check for dependency issues
ssh brian@TARGET_IP "sudo rpm -i /tmp/check-mk-agent-*.rpm --test"
```

### Problem: Agent Not Responding

**Check if agent service is running:**
```bash
# For socket-based agent
ssh brian@TARGET_IP "sudo systemctl status check-mk-agent.socket"

# For async agent service
ssh brian@TARGET_IP "sudo systemctl status check-mk-agent-async.service"
```

**Restart agent services:**
```bash
ssh brian@TARGET_IP "sudo systemctl restart check-mk-agent.socket check-mk-agent-async.service"
```

### Problem: Wrong OS Detected - Wrong Package Installed

**If .deb installed on RHEL:**
```bash
ssh brian@TARGET_IP "sudo dpkg -r check-mk-agent"
# Then install correct .rpm package
```

**If .rpm installed on Debian:**
```bash
ssh brian@TARGET_IP "sudo dpkg -r check-mk-agent"
# Then install correct .deb package
```

### Problem: Agent Version Mismatch

**Verify agent version matches server:**
```bash
# Server version
ssh brian@10.10.10.5 "sudo su - monitoring -c 'omd version'"

# Agent version
ssh brian@TARGET_IP "sudo /usr/bin/check_mk_agent | grep Version"
```

**If they don't match:**
- Remove agent: `sudo dpkg -r check-mk-agent` (Debian) or `sudo rpm -r check-mk-agent` (RHEL)
- Download correct version from Checkmk server
- Reinstall matching version

### Problem: Host Not Appearing in Monitoring

**Diagnosis steps:**

1. Check if in hosts.mk:
```bash
ssh brian@10.10.10.5 "sudo grep HOSTNAME /omd/sites/monitoring/etc/check_mk/conf.d/wato/hosts.mk"
```

2. Check if compilation succeeded:
```bash
ssh brian@10.10.10.5 "sudo su - monitoring -c 'cmk -R 2>&1'"
```

3. Check if in Nagios config:
```bash
ssh brian@10.10.10.5 "sudo grep 'host_name.*HOSTNAME' /omd/sites/monitoring/etc/nagios/conf.d/check_mk_objects.cfg"
```

4. Check automation-helper logs for errors:
```bash
ssh brian@10.10.10.5 "sudo tail -50 /omd/sites/monitoring/var/log/automation-helper/error.log | grep -i error"
```

---

## Common Mistakes to Avoid

1. **❌ Using wrong package type**
   - Installing .deb on RHEL or .rpm on Debian
   - **Check /etc/os-release first**

2. **❌ Agent version mismatch**
   - Installing agent version different from Checkmk server
   - **Must match exactly (e.g., both 2.4.0p15)**

3. **❌ Hostname conflicts**
   - Adding hostname that already exists
   - **Check hosts.mk first**

4. **❌ IP address duplication**
   - Assigning same IP to multiple hosts
   - **Verify IP is unique**

5. **❌ Not verifying agent is running**
   - Assuming installation worked without testing
   - **Always run `check_mk_agent | head -20` after install**

---

## Agent Package Reference

| Checkmk Version | Debian/Ubuntu Package | RedHat/RHEL Package |
|-----------------|----------------------|---------------------|
| 2.4.0p15 | check-mk-agent_2.4.0p15-1_all.deb | check-mk-agent-2.4.0p15-1.noarch.rpm |
| 2.4.0p14 | check-mk-agent_2.4.0p14-1_all.deb | check-mk-agent-2.4.0p14-1.noarch.rpm |
| 2.3.0p8 | check-mk-agent_2.3.0p8-1_all.deb | check-mk-agent-2.3.0p8-1.noarch.rpm |

All packages stored at: `/omd/sites/monitoring/share/check_mk/agents/`

---

## OS Detection Command Cheat Sheet

**Quick OS detection one-liner:**
```bash
cat /etc/os-release | grep "^ID=" && cat /etc/os-release | grep "^PRETTY_NAME"
```

**To determine package manager:**
```bash
# Debian/Ubuntu - has dpkg
which dpkg && echo "Use .deb"

# RedHat/RHEL - has rpm
which rpm && echo "Use .rpm"
```

---

## Key Decisions for Deckard

1. **ALWAYS check Checkmk version first** - All agents must match
2. **ALWAYS detect OS before installing** - Wrong package = non-functional agent
3. **ALWAYS open firewall port 6556** - Most Linux distros have firewalls enabled by default (firewalld or iptables)
4. **ALWAYS verify agent responds** - Test both locally and from Checkmk server
5. **ALWAYS run service discovery and activate** - Web UI won't fully recognize host without this critical step
6. **ALWAYS wait for configuration compilation** - Changes take 5-10 seconds to apply
7. **Document additions** - Keep track of which hosts added when and why

---

**Last Updated:** November 14, 2025
**Status:** Complete - Tested with ansible server (RHEL 9.7)
**Key Lessons:**
- Firewall port 6556 must be open (firewalld for RHEL, iptables for older Debian)
- Service discovery and configuration activation are critical - host won't fully appear in Web UI without these
- Test connectivity from Checkmk server to verify port is reachable
- Always run full service discovery (`cmk -I hostname`) to discover available services

