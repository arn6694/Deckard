# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Navigation Quick Links

**For working on scripts in this repository:**
- **Upgrading Checkmk** → See "Working with Existing Scripts" > `checkmk_upgrade_to_2.4.sh` + "Quick Reference: Operations Checklist"
- **Distributing Checkmk Agents** → See "Working with Existing Scripts" > `update_checkmk_agents.sh` + "Quick Reference: Operations Checklist"
- **Fixing a Script** → See "Debugging and Fixing Scripts" section
- **Adding/Modifying Scripts** → See "Common Development Tasks" section
- **DNS/Network Questions** → The `network_engineer.md` agent will auto-activate with relevant docs
- **Checkmk Configuration Questions** → The `Checkmk.md` agent will auto-activate with relevant docs

**Key Documents to Reference:**
- `dns_infrastructure_documentation.md` - Complete DNS architecture, BIND9 config, Pi-hole setup
- `checkmk_dns_monitoring_setup.md` - How Checkmk monitors DNS infrastructure
- `checkmk_agent_update_guide.md` - Detailed walkthrough of agent deployment procedures

## Repository Purpose

This is a homelab operations repository containing scripts and documentation for managing enterprise monitoring (Checkmk), DNS/ad-blocking (Pi-hole), reverse proxy (Nginx Proxy Manager), and Home Assistant integrations. The content serves as operational runbooks and automation tools for system administration tasks.

## Quick Start

### Running Production Scripts

Both production scripts are interactive and will prompt for confirmation before making destructive changes:

```bash
# Checkmk server upgrade (full backup + version check + rollback capability)
# Current versions: checkmk_upgrade_to_2.4.sh supports 2.4.0p1 → 2.4.0p2+
sudo ./checkmk_upgrade_to_2.4.sh

# Update Checkmk agents (menu-driven: select hosts or bulk update all)
# Automatically detects Debian (deb) vs RHEL/CentOS (rpm) systems
./update_checkmk_agents.sh
```

### Script Validation and Testing

Before running or modifying scripts, validate syntax and understand the scripts:

```bash
# Syntax check (required before any script modification)
bash -n script.sh

# Code quality check (optional but recommended)
shellcheck script.sh

# Preview what the script will do (read-only, safe to run)
less checkmk_upgrade_to_2.4.sh  # Review version config and pre-flight checks
less update_checkmk_agents.sh    # Review host list and package paths
```

**Safety Note:** Both scripts use `set -e` and `set -o pipefail` - they will halt immediately on any error and provide clear logging. Check `/tmp/` for timestamped log files after execution.

### Prerequisites

- **Bash 4.0+** on control host (where scripts run)
- **SSH access** to managed hosts with passwordless key authentication
- **Standard utilities**: `grep`, `awk`, `sed`, `tar`, `gzip`, `scp`, `ssh`
- **Checkmk server**: `omd` CLI tool available for diagnostics
- **DNS testing**: `dig` command (part of `bind-tools`)
- **Root access** for local system changes (upgrade scripts use `sudo`)

## Repository Structure

### Main Directory Contents
- **Production Scripts** (`*.sh`):
  - `checkmk_upgrade_to_2.4.sh` (373 lines) - Upgrades Checkmk with backups and version verification
  - `update_checkmk_agents.sh` (330 lines) - Distributes Checkmk agents to managed hosts
- **Documentation** (`*.md`): Operational guides, implementation procedures, and troubleshooting
- **Specialized Agents** (`.claude/agents/`): Auto-activating domain experts with official documentation:
  - `Checkmk.md` - Checkmk 2.4 expertise with automatic doc sourcing (https://docs.checkmk.com/)
  - `network_engineer.md` - DNS, BIND9, Pi-hole infrastructure (https://bind9.readthedocs.io/, https://docs.pi-hole.net/)
  - `ansible.md` - Infrastructure automation (https://docs.ansible.com/)
  - `session_closer.md` - Session management for wrapping up work

### Key File Locations
- **Production Scripts**: `/home/brian/claude/*.sh` - Execute with `sudo` for upgrades, without for agent updates
- **Version Configuration**: Top 20 lines of each script (all dynamic values here)
- **Backup/Logs**: `/tmp/checkmk_upgrade_backups/` and `/tmp/checkmk_upgrade_*.log` files
- **Documentation**: Mix of guides (checkmk_dns_monitoring_setup.md, dns_infrastructure_documentation.md, etc.)

### Required CLI Tools
All scripts rely on these tools (verify with `which <tool>`):
- `bash` - Script runtime (version 4.0+)
- `ssh`, `scp` - Remote host access (passwordless key auth required)
- `dpkg`, `rpm` - Package detection and installation
- `curl`, `wget` - HTTP operations for Checkmk downloads
- `dig` - DNS diagnostics
- `omd` - Checkmk OMD (OpenMonitoring Distribution) CLI for version checks and diagnostics
- Standard utilities: `grep`, `awk`, `sed`, `tar`, `gzip`, `date`, `du`

## Code Architecture

### Shell Scripts Design Pattern

All shell scripts follow this standardized architecture for safety and auditability:

**File Structure:**
```bash
#!/bin/bash
set -e           # Line 1: Exit on error
set -o pipefail  # Line 2: Exit on pipe failures

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
...

# === CONFIGURATION BLOCK ===
VARIABLE_NAME="value"  # ALL dynamic values here (versions, IPs, paths)
CHECKMK_VERSION_SHORT="2.4.0p2"  # Example: version to upgrade TO
CHECKMK_SERVER="10.10.10.5"      # Example: server IP
BACKUP_DIR="/tmp/checkmk_upgrade_backups"

# === LOGGING FUNCTIONS ===
log() { ... }           # Internal logging with timestamps
log_success() { ... }   # Green ✓ - success
log_error() { ... }     # Red - failure
log_warning() { ... }   # Yellow - caution
log_info() { ... }      # Blue - information
error_exit() { ... }    # Log error and exit(1)

# === UTILITY FUNCTIONS ===
check_root() { ... }              # Verify sudo/root
check_connectivity() { ... }      # Test SSH access
verify_prerequisites() { ... }    # Check all required tools

# === MAIN LOGIC ===
main() {
    pre_flight_checks
    backup_state
    apply_changes
    verify_changes
    cleanup
}

main "$@"  # Execute with command line args
```

**Execution Flow:**
1. **Shebang + Error Handling** - Script fails immediately on any error
2. **Configuration Block** - All `UPPER_CASE` variables grouped at top
3. **Logging Functions** - Color-coded, timestamped output for all user messages
4. **Utility Functions** - Reusable checks and helpers
5. **Pre-flight Validation** - Root check, connectivity, dependencies, version detection
6. **Main Operation** - Backup → Execute → Verify → Cleanup
7. **Error Recovery** - Scripts halt on failure; logs provide rollback instructions

**Key Safety Features:**
- **Atomic Changes**: Backup before any modification; restore if needed
- **Explicit Confirmations**: Interactive prompts for destructive operations with context
- **Timestamped Logs**: Every operation logged to `/tmp/` for audit trail and debugging
- **No Silent Failures**: Color-coded output + comprehensive logging
- **Clear Error Context**: Error messages include what failed and where to find logs

### Infrastructure State Pattern

Scripts maintain idempotent operations where appropriate:
- **Safe to Re-Run**: Version detection before upgrades prevents duplicate upgrades
- **Destructive Operations**: Always require explicit confirmation (read prompts)
- **Failed Operations**: Script halts immediately; no partial state changes
- **Recovery Options**: Backup in `/tmp/checkmk_upgrade_backups/` for manual restoration

### Specialized Agents Overview

The repository uses AI agents configured in `.claude/agents/` that automatically activate for relevant question domains:

- **Agents auto-activate** based on question topic (no manual invocation needed)
- Each agent has YAML metadata (name, description trigger, model preference, color)
- Agents automatically search and cite official documentation for their domain

See "Specialized AI Agents" section below for details on each agent's capabilities and documentation sources.

### Specialized AI Agents

The repository includes three specialized agents in `.claude/agents/` that provide domain expertise and automatically activate when relevant. Each agent uses YAML frontmatter (`---`) to define metadata:

1. **Checkmk Agent** (`Checkmk.md`)
   - Activates for: Checkmk monitoring, alerting, APIs, checks, configuration
   - Expertise: Checkmk 2.4 administration, REST API integration, custom checks
   - Behavior: Automatically searches official Checkmk docs (https://docs.checkmk.com/latest/en/) with topic-based routing (notifications, API, custom checks, agent config, etc.)
   - Key capability: Always cites specific official documentation sources in responses

2. **Network Engineer Agent** (`network_engineer.md`)
   - Activates for: DNS, BIND9, Pi-hole, network infrastructure questions
   - Expertise: BIND9 configuration, DNS architecture, Pi-hole setup, network monitoring
   - Behavior: Automatically references BIND9 docs (https://bind9.readthedocs.io/) and Pi-hole docs (https://docs.pi-hole.net/)
   - Key capability: Provides complete network infrastructure guidance with official sources

3. **Ansible Agent** (`ansible.md`)
   - Activates for: Ansible automation, infrastructure-as-code, playbooks
   - Expertise: Infrastructure automation, configuration management, network automation
   - Behavior: References Ansible official documentation at https://docs.ansible.com/
   - Key capability: Production-ready patterns with idempotency and error handling

**When asking questions about these domains, the specialized agents will automatically activate and provide expert guidance backed by official documentation.**

#### Modifying Agents

Agents use YAML metadata at the top:
```yaml
---
name: Agent Name
description: when ... questions are asked  # triggers activation
model: sonnet                             # claude model to use
color: blue                               # visual indicator
---
```

To add new agent or modify existing:
1. Edit the `.claude/agents/*.md` file
2. Update `description` field to control activation triggers
3. Include documentation sources as comments in the agent prompt
4. Use `AUTOMATIC URL ROUTING` pattern for topic-based documentation links
5. No restart needed - agents load dynamically

### Infrastructure Components

**Checkmk Monitoring** (`checkmk` - 10.10.10.5):
- Version: 2.4.0p2 (scripts support p1 and p2)
- Site name: `monitoring`
- Agent distribution path: `/omd/sites/monitoring/share/check_mk/agents/`
- Managed via `cmk` CLI and REST API

**Pi-hole DNS** (Primary: `zero` - 10.10.10.22, Secondary: `zeus` - 10.10.10.23):
- Pi-hole v6 with custom dnsmasq configuration
- Primary runs in Proxmox LXC 105, secondary in Docker on Zeus
- Wildcard DNS enabled for `*.ratlm.com` → NPM
- Configuration: `/etc/dnsmasq.d/02-ratlm-local.conf`
- Custom config requires `etc_dnsmasq_d = true` in `/etc/pihole/pihole.toml`
- Forwards .lan queries to BIND9 servers

**BIND9 DNS** (Primary: 10.10.10.4, Secondary: 10.10.10.2):
- Authoritative DNS for .lan domain
- Master-slave zone replication for redundancy
- Primary on Proxmox LXC 119, secondary on Zeus Docker
- Handles all local hostname resolution
- Access: SSH as brian (passwordless), sudo enabled
- Zone file: `/etc/bind/zones/db.lan`
- Container access: `sudo pct enter 119` from Proxmox host

**Nginx Proxy Manager** (10.10.10.3):
- Receives all `*.ratlm.com` traffic via wildcard DNS
- Handles SSL/TLS termination for internal services

**Home Assistant** (10.10.10.6):
- Running on Home Assistant OS (Alpine Linux base)
- Monitored via Checkmk with SSH-based agent

### Network Architecture

The homelab uses internal `10.10.10.0/24` network with `.ratlm.com` domain for services:
- DNS resolution handled by Pi-hole with wildcard support
- All external-facing services proxied through NPM
- Monitoring centralized in Checkmk

## Working with Existing Scripts

### Understanding Each Script's Purpose

**`checkmk_upgrade_to_2.4.sh`** - Checkmk Server Upgrade
- **Purpose**: Upgrade Checkmk Raw Edition server from one version to another
- **Requires**: `sudo` (runs as root for system package operations)
- **Entry Point**: Line ~360 - `check_root`, then upgrade flow
- **Key Functions** (in order of use):
  - `check_checkmk_running()` - Verify OMD site is running
  - `check_version()` - Compare current vs target version, skip if already at target
  - `backup_site()` - Create timestamped backup of entire monitoring site
  - `download_package()` - Fetch Checkmk DEB from download.checkmk.com
  - `install_package()` - Use dpkg to install upgrade
  - `verify_upgrade()` - Check site started cleanly post-upgrade
- **Version Config**: Lines 18-22
  - `CHECKMK_VERSION_SHORT="2.4.0p1"` - What version to upgrade TO (update this)
  - `DOWNLOAD_URL` - Derives from version, usually doesn't need changes
- **Safety Checks**: Pre-flight validation (lines ~200-250) checks for required tools, existing backups, and current version

**`update_checkmk_agents.sh`** - Checkmk Agent Distribution
- **Purpose**: Deploy Checkmk agents to monitored hosts for metrics collection
- **Requires**: No sudo (SSH to remote hosts as `brian` user with key auth)
- **Entry Point**: Line ~300 - Menu-driven interface with host selection
- **Key Functions**:
  - `menu_interface()` - Interactive menu to select individual hosts or bulk update
  - `download_agent_package()` - Fetch DEB/RPM from Checkmk server's agent directory
  - `detect_os()` - SSH to host and check if Debian (dpkg) or RHEL (rpm)
  - `install_agent()` - SCP package to host and install via dpkg/rpm
  - `verify_agent()` - SSH back to host and verify agent connectivity
- **Host List**: Lines 23-30 - Array of target hosts (IP addresses)
- **Version Config**: Lines 16-22
  - `TARGET_VERSION="2.4.0p2"` - Version of agents to deploy (update when distributing new agents)
  - `AGENT_DEB` and `AGENT_RPM` - Paths on Checkmk server's agent directory
- **Important**: Script auto-detects OS type; check at lines ~270 for how it handles mixed Debian/RHEL infrastructure

### Script Modification Reference

When modifying scripts, always update these sections in order:

1. **Configuration variables** (top 30 lines) - Version numbers, IPs, paths
2. **Logging functions** (skip unless changing output format)
3. **Utility functions** (skip unless fixing bugs)
4. **Main function** - The actual operation logic
5. **Test syntax**: `bash -n script.sh`
6. **Test on non-critical host**: Run preview or with test flag if available

Example: To update agent distribution target version:
```bash
# 1. Edit the TARGET_VERSION in update_checkmk_agents.sh
TARGET_VERSION="2.4.0p3"  # Changed from p2

# 2. Verify the agent packages exist on Checkmk server
#    Check that /omd/sites/monitoring/share/check_mk/agents/ has:
#    - check-mk-agent_2.4.0p3-1_all.deb
#    - check-mk-agent-2.4.0p3-1.noarch.rpm

# 3. Validate syntax
bash -n update_checkmk_agents.sh

# 4. Test on a single host first (use menu to select one)
./update_checkmk_agents.sh
```

## Common Development Tasks

### Adding a New Bash Script

When creating a new operational script (beyond the two existing ones):

1. **Start with the template structure:**
   - Shebang: `#!/bin/bash`
   - Error handling: `set -e` and `set -o pipefail` at top
   - Color definitions for logging (copy from existing scripts)
   - Configuration block with `UPPER_CASE` variables

2. **Implement standard functions:**
   ```bash
   log_success "Message"    # Green - operation succeeded
   log_error "Message"      # Red - operation failed
   log_warning "Message"    # Yellow - warning/caution
   log_info "Message"       # Blue - informational
   error_exit "Message"     # Log error and exit with code 1
   ```

3. **For destructive operations:**
   - Create backups before modifications
   - Use `read -p "Continue? (y/N): "` for confirmation
   - Log the backup location clearly
   - Provide manual rollback instructions if needed

4. **Before committing:**
   - Run `bash -n script.sh` to validate syntax
   - Test on non-critical hosts first
   - Document any new configuration variables at the top
   - Verify all logging calls use standard functions

### Modifying Existing Scripts

Follow these rules to maintain code consistency:

1. **Never remove the logging system** - All user-facing output goes through `log_*()` functions
2. **Preserve error handling** - Keep `set -e`, `set -o pipefail`, and error handlers intact
3. **Update configuration block** - If changing versions, IPs, or paths, update the variables at the top
4. **Test syntax immediately** - Run `bash -n script.sh` after any change
5. **Document changes in comments** - Add context for why modifications were made

**Example workflow for a version update:**
```bash
# 1. Edit the VERSION variable at the top of script
CHECKMK_VERSION_SHORT="2.4.0p2"  # Updated from p1
CHECKMK_VERSION="2.4.0p2.cre"

# 2. Update download URL if needed
DOWNLOAD_URL="https://download.checkmk.com/checkmk/${CHECKMK_VERSION_SHORT}/..."

# 3. Validate syntax
bash -n script.sh

# 4. Test on non-critical host
sudo ./script.sh

# 5. Document what changed and why
```

### Updating Documentation

Documentation should reflect the current state of infrastructure and scripts:

- Update IP addresses when hosts change
- Update version numbers when software is upgraded
- Add new procedures when operational patterns change
- Remove or mark procedures as archived if they become obsolete
- Include dates in status tables so readers know how current information is

Always validate:
- Commands referenced are tested and working
- IP addresses and hostnames match actual infrastructure
- Version numbers match deployed software
- External documentation links still resolve

## Key Operational Patterns

### Checkmk Agent Updates

When updating agents across the infrastructure:
1. Download appropriate package (DEB/RPM) from server's agent directory
2. Use `update_checkmk_agents.sh` for bulk updates
3. Script auto-detects OS type and applies correct package
4. Verification via `cmk -d <hostname>` from monitoring server

### Adding New Services

When adding a new service to the infrastructure:
1. Deploy service on appropriate host
2. Configure in NPM with `<service>.ratlm.com` hostname
3. No Pi-hole changes needed (wildcard DNS handles it)
4. Add monitoring in Checkmk via WATO/REST API

### Managing DNS and DHCP (Preventing IP Drift)

**Problem**: Hosts using DHCP can get new IPs after reboots, breaking DNS resolution and monitoring.

**Solution**: Use DHCP reservations in Firewalla Gold + static DNS entries in BIND9.

#### Setting DHCP Reservations in Firewalla

1. Open Firewalla app → **Devices** tab
2. Find the device (e.g., jarvis)
3. Tap on device → scroll to IP allocation
4. Change from **Dynamic** to **Reserved**
5. Set desired IP address
6. Save

After setting reservation, reboot the device to get the new reserved IP.

#### Updating BIND9 DNS Records

**Access BIND9 Primary (10.10.10.4):**
```bash
# Option 1: Direct SSH (preferred)
ssh brian@10.10.10.4

# Option 2: Via Proxmox container
ssh brian@10.10.10.17
sudo pct enter 119
```

**Edit DNS zone file:**
```bash
# Edit the zone file
sudo nano /etc/bind/zones/db.lan

# Make changes:
# 1. Update host IP: hostname    IN    A    10.10.10.XX
# 2. INCREMENT SERIAL NUMBER (critical!)
#    Format: YYYYMMDDNN (e.g., 2025110301 → 2025110302)

# Validate syntax
sudo named-checkzone lan /etc/bind/zones/db.lan

# Reload BIND9
sudo rndc reload

# Verify
dig @localhost hostname.lan +short
```

**Workflow for changing a host's IP:**
1. Update DNS record in BIND9 (increment serial!)
2. Set DHCP reservation in Firewalla to match
3. Reboot host to get new IP
4. Verify: `dig hostname.lan +short` should match new IP
5. Secondary BIND9 (Zeus) auto-syncs via zone transfer

**Important**: Always increment the serial number when editing zone files. BIND9 uses it to track versions and trigger zone transfers to secondary servers.

### Documentation Standards

All documentation follows this structure:
- **Overview section**: Purpose and context
- **Current Status tables**: For tracking multi-host operations (with dates)
- **Step-by-step procedures**: Commands with expected output
- **Troubleshooting section**: Common issues and solutions
- **Metadata footer**: Creation date and version info

#### When to Update Documentation

Update operational docs when:
- Infrastructure IPs or hostnames change
- Versions are upgraded (Checkmk, Pi-hole, BIND9)
- New hosts are added to the homelab
- Procedures are discovered to have missing steps
- Commands change due to OS or software updates
- Status of systems changes (online/offline, active/retired)

**Important:** Keep documentation in sync with actual infrastructure. Stale docs cause confusion and operational errors.

#### Documentation Validation

Before committing documentation changes:
1. Commands referenced are tested and working
2. IP addresses match actual infrastructure
3. Version numbers match deployed software
4. Step numbers are sequential and complete
5. Table data is current (check dates)
6. Links to external docs still resolve

## Debugging and Fixing Scripts

### When a Script Fails

**Immediate Actions:**
1. Check the timestamped log file: `ls -lt /tmp/checkmk_*.log | head -1`
2. Review the error message and log context
3. If backup exists, check: `ls -la /tmp/checkmk_upgrade_backups/`

**Common Failure Scenarios:**

| Failure | Cause | Fix |
|---------|-------|-----|
| "command not found" (omd, dpkg, ssh) | Missing prerequisite tool | Install tool on control host or target host |
| "Permission denied (publickey)" | SSH key auth not working | Verify `~/.ssh/id_rsa` exists and SSH agent is running |
| "Connection refused" | Target host unreachable | Test: `ping <host>` and `ssh brian@<host> 'echo ok'` |
| "Already at version 2.4.0p1" | Script detected version match | This is safe - script auto-skips duplicate upgrades |
| "dpkg: error processing" | Checkmk package conflict | Check if site is running: `sudo su - monitoring -c 'omd status'` |

**To Debug a Specific Line:**
```bash
# Add debug flag and run with set -x to trace execution
bash -x ./checkmk_upgrade_to_2.4.sh 2>&1 | tee debug.log

# Or run individual functions directly (after sourcing the script):
source ./checkmk_upgrade_to_2.4.sh
check_version    # Run just this function
verify_prerequisites  # Check dependencies
```

### Making Quick Fixes

**Pattern for fixing a bug in a script:**
```bash
# 1. Read the problematic section
head -100 checkmk_upgrade_to_2.4.sh | tail -20  # Lines 80-100 for example

# 2. Identify the issue (syntax, logic, version mismatch)

# 3. Make minimal edit using the Edit tool
# Example: Fix a version number
OLD_TEXT='CHECKMK_VERSION_SHORT="2.4.0p1"'
NEW_TEXT='CHECKMK_VERSION_SHORT="2.4.0p2"'

# 4. Validate syntax immediately
bash -n checkmk_upgrade_to_2.4.sh

# 5. Review the change worked
grep "CHECKMK_VERSION_SHORT" checkmk_upgrade_to_2.4.sh
```

## Common Troubleshooting Commands

### Checkmk Diagnostics
```bash
# Check agent connectivity from monitoring server
sudo su - monitoring -c 'cmk -d <hostname>'

# View site status
omd status

# Check Checkmk version
omd version

# List all monitored hosts
sudo su - monitoring -c 'cmk --list-hosts'

# Force service discovery on a host
sudo su - monitoring -c 'cmk -I <hostname>'
```

### DNS Diagnostics
```bash
# Test Pi-hole DNS resolution (primary and secondary)
dig @10.10.10.22 example.lan
dig @10.10.10.23 example.lan

# Test wildcard DNS for .ratlm.com
dig @10.10.10.22 test.ratlm.com

# Check dnsmasq wildcard config
cat /etc/dnsmasq.d/02-ratlm-local.conf

# Pi-hole logs (tail mode)
pihole -t

# Check BIND9 zone transfer status
sudo rndc status
dig @10.10.10.4 example.lan AXFR
```

### Network Connectivity
```bash
# Test SSH access to managed hosts
ssh brian@<host-ip> 'hostname && uptime'

# Check service availability via NPM
curl -I https://checkmk.ratlm.com
curl -I https://proxmox.ratlm.com

# Verify DNS servers are responding
for dns in 10.10.10.22 10.10.10.23; do
  echo "=== Testing DNS $dns ==="
  dig @$dns google.com +short
done

# Test agent port connectivity
nc -zv <host-ip> 6556
```

## Modifying Scripts

When updating production scripts, maintain these patterns:

### Script Modification Checklist

1. **Preserve error handling structure:**
   - Keep `set -e` and `set -o pipefail` at the top
   - Maintain `error_exit()` function and error handlers
   - All subprocess calls should have `|| { error handler }`

2. **Update logging consistently:**
   - Use existing logging functions: `log_success()`, `log_error()`, `log_warning()`, `log_info()`
   - All user-facing messages go through logging functions (not bare `echo`)
   - Include context in log messages (hostname, version, file path, etc.)

3. **Maintain configuration block:**
   - All dynamic values (IPs, versions, paths) at top of script in `UPPER_CASE`
   - Version strings should match actual target versions
   - Update comments when configuration changes

4. **Preserve backup strategy:**
   - Critical file changes must create timestamped backups before modification
   - Backup path should be documented in logs
   - Include backup file content verification in pre-flight checks

5. **Before committing changes:**
   - Run syntax check: `bash -n script.sh`
   - Review all variable assignments for proper quoting
   - Verify backup/restore logic works as intended
   - Test on non-critical host first

### Script Testing Guidelines

**Safe to test immediately:**
- Syntax validation (bash -n)
- Version detection (check_version function)
- Connectivity checks (ssh -O check)
- Read-only operations (dig, curl, status commands)

**Requires careful testing:**
- Backup/restore logic (test on non-critical host)
- Agent updates (test on one host before rolling out)
- Checkmk configuration changes (test in staging first)

**Emergency procedures if script fails:**
1. Stop the script immediately (Ctrl+C)
2. Check log file in `/tmp/` for error location
3. Review backup in `/tmp/checkmk_upgrade_backups/` if applicable
4. Restore from backup manually using documented commands
5. Investigate root cause before retrying

## Quick Reference: Operations Checklist

### Upgrading Checkmk Server

**Pre-Upgrade Checklist:**
- [ ] Verify current version: `sudo su - monitoring -c 'omd version'`
- [ ] Check site is healthy: `sudo su - monitoring -c 'omd status'`
- [ ] Verify backup directory exists: `ls -d /tmp/checkmk_upgrade_backups`
- [ ] Verify network connectivity to checkmk.download.com: `curl -I https://download.checkmk.com/`
- [ ] Edit `checkmk_upgrade_to_2.4.sh` line 18 with target version (if needed)

**Execution:**
```bash
bash -n ./checkmk_upgrade_to_2.4.sh  # Validate first
sudo ./checkmk_upgrade_to_2.4.sh      # Run upgrade (will prompt for confirmation)
```

**Post-Upgrade:**
- [ ] Check version upgraded: `sudo su - monitoring -c 'omd version'`
- [ ] Review backup location in logs: `tail /tmp/checkmk_upgrade_*.log`
- [ ] Test Checkmk web UI: `curl -I https://checkmk.ratlm.com`
- [ ] Force host rediscovery if needed: `sudo su - monitoring -c 'cmk -I <hostname>'`

### Updating Checkmk Agents

**Pre-Update Checklist:**
- [ ] Verify target version packages exist on Checkmk server:
  ```bash
  ssh brian@10.10.10.5 'ls -la /omd/sites/monitoring/share/check_mk/agents/check-mk-agent_2.4.0p2*'
  ```
- [ ] Test SSH access to at least one target host: `ssh brian@<host> 'echo ok'`
- [ ] Edit `update_checkmk_agents.sh` lines 16-22 if updating target version

**Execution:**
```bash
bash -n ./update_checkmk_agents.sh   # Validate first
./update_checkmk_agents.sh            # Run with interactive menu
# Select single host to test, then "Bulk update all" when confident
```

**Post-Update:**
- [ ] Verify agent installed: `ssh brian@<host> 'dpkg -l | grep check-mk-agent'` (Debian)
- [ ] Or for RPM: `ssh brian@<host> 'rpm -qa | grep check-mk-agent'` (RHEL/CentOS)
- [ ] Force service discovery on hosts: `sudo su - monitoring -c 'cmk -I <hostname>'`

### Adding a Host to Infrastructure

1. **Set static IP in Firewalla** (DHCP reservation)
2. **Add DNS record in BIND9** (on 10.10.10.4):
   - Edit `/etc/bind/zones/db.lan`
   - Add: `hostname    IN    A    10.10.10.XX`
   - Increment serial number
   - Run: `sudo rndc reload`
3. **Update Checkmk agents script** (if it should monitor):
   - Add IP to array in `update_checkmk_agents.sh` lines 23-30
   - Validate: `bash -n update_checkmk_agents.sh`
   - Run agent deployment: `./update_checkmk_agents.sh`
4. **Add to Checkmk monitoring** (via WATO or REST API):
   - SSH to Checkmk: `ssh brian@10.10.10.5`
   - Or use REST API: `curl -X POST https://checkmk.ratlm.com/...`

## Style Guidelines

### Shell Scripts

**Naming and Structure:**
- Shebang: `#!/bin/bash`
- Variables: `UPPER_CASE` for constants and configuration, `lower_case` for local variables
- Functions: `lower_case_with_underscores()` - declare functions before main logic
- Quote all variables: `"$variable"` - prevents word splitting and glob expansion bugs
- Use `[[ ]]` for all string comparisons (not `[ ]` or `test`)
- Use `(( ))` for all arithmetic operations

**Safety Practices:**
- Enable error handling at the top: `set -e` (exit on error) and `set -o pipefail` (exit on pipe failure)
- Define an `error_exit()` function that logs and cleans up before exiting
- For optional operations that might fail, use `|| { error_handler }` to catch failures
- Never use interactive commands in loops - causes scripts to hang
- Always quote loop variables: `for host in "${HOSTS[@]}"` not `for host in $HOSTS`
- Use explicit exit codes: `exit 0` for success, `exit 1` for errors

**Common Patterns:**
```bash
#!/bin/bash
set -e
set -o pipefail

# Configuration (top of file)
VERSION="2.4.0p2"
BACKUP_DIR="/tmp/backups"

# Logging functions
log_success() { echo "✓ $1"; }

# Main execution
main() {
    # Pre-flight checks
    check_root
    validate_config

    # Operation with error handling
    backup_data || error_exit "Backup failed"
    apply_changes || { restore_backup; error_exit "Changes failed"; }
}

main "$@"
```

### Markdown

**Formatting:**
- Use ATX-style headers: `# H1`, `## H2`, `### H3` (not underline style)
- Include table of contents for documentation with >5 sections
- Code blocks with language specifiers: ` ```bash `, ` ```yaml `, ` ```dns `
- Tables for structured data: host lists, status tracking, configuration comparisons
- **Bold** for important terms, file names, and technical concepts
- Links to external docs should be specific (e.g., docs URL + topic, not just homepage)

**Content Standards:**
- Keep docs in sync with actual infrastructure state - stale docs cause operational errors
- Include metadata: creation date, last updated, software versions
- Step-by-step procedures should be numbered and tested before documentation
- Troubleshooting sections organized by symptom → diagnosis → solution
- Examples should be realistic and tested (not theoretical)

### Security Practices

**Access Control:**
- No hardcoded passwords in scripts or documentation
- SSH key authentication required (password-based auth disabled)
- Validate user input before processing (especially `read` prompts - check for empty/invalid values)
- Document any SSH access requirements or key setup needed

**Safe Operations:**
- Clean up temporary files after execution, especially in error handlers
- Use `sudo` only when necessary, with specific user context: `sudo su - monitoring -c 'command'`
- Set restrictive permissions on sensitive files: `chmod 700` for private directories, `chmod 600` for files
- Log operations for audit trail - include timestamps and context in all log messages
- Never log sensitive data (passwords, API tokens, private keys)
