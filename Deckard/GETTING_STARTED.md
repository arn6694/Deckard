# Getting Started with Deckard

## Prerequisites

Before building Deckard, verify you have:

- ✅ **Jarvis Backend**: 10.10.10.49 running Ollama + OpenWebUI
- ✅ **Claude Code**: Latest version installed
- ✅ **Git**: Repository access for Deckard
- ✅ **SSH Access**: To infrastructure servers (already configured)
- ✅ **API Access**: To Checkmk, BIND9, Pi-hole (document endpoints)

## Phase 1: Foundation (Week 1-2)

### Step 1: Initialize `.claude/` Directory Structure

```bash
# Create base directory structure
mkdir -p ~/.claude/{agents,skills,hooks,documentation,history/sessions,context}

# Create core skills subdirectories
mkdir -p ~/.claude/skills/{CORE,infrastructure-ops,monitoring,dns-management,automation,troubleshooting,research}
mkdir -p ~/.claude/skills/{CORE,infrastructure-ops,monitoring,dns-management,automation,troubleshooting,research}/workflows
```

### Step 2: Create Core Identity (CORE/SKILL.md)

**What to customize**:

```yaml
name: Deckard
description: |
  Personal AI Infrastructure for Elliott infrastructure operations.
  Provides integrated monitoring, automation, and infrastructure management
  for homelab infrastructure including Checkmk, BIND9, Pi-hole, and Ansible.

Core Identity:
  Your Name: Deckard
  Your Role: Infrastructure operations assistant for Elliott homelab
  Personality: Methodical, thorough, security-conscious. Verify before executing.

Essential Contacts:
  - Brian [Owner]: brian@ratlm.com
  - Checkmk Primary: checkmk@10.10.10.5
  - BIND9 Primary: bind@10.10.10.4
  - Pi-hole Primary: pihole@10.10.10.22

Core Stack Preferences:
  - Primary Language: Bash, Python, YAML (for Ansible)
  - Preferred Tools: Ansible, dig, sqlite3, jq
  - Infrastructure First: Always validate in check mode first
```

**Copy template from**: `reference/pai-reference/.claude/skills/CORE/SKILL.md`

### Step 3: Create Infrastructure Context

**Create**: `~/.claude/documentation/infrastructure-topology.md`

```markdown
# Elliott Homelab Infrastructure

## Network Overview
- Gateway: 10.10.10.1 (Firewalla)
- DNS Primary: 10.10.10.4 (BIND9 in Proxmox 119)
- DNS Secondary: 10.10.10.2 (BIND9 in Zeus)
- Pi-hole Primary: 10.10.10.22 (Proxmox 105)
- Pi-hole Secondary: 10.10.10.23 (Zeus Docker)
- Checkmk: 10.10.10.5
- Nginx PM: 10.10.10.3
- Home Assistant: 10.10.10.6
- Proxmox: 10.10.10.17
- Jarvis (Ollama/OpenWebUI): 10.10.10.49

## Service Endpoints
- Checkmk Web UI: https://checkmk.ratlm.com
- Checkmk API: https://checkmk.ratlm.com/monitoring/live
- OpenWebUI: http://10.10.10.49:3000
- Ollama: http://10.10.10.49:11434

## Access Methods
- SSH: Available to all infrastructure hosts
- BIND9: rndc commands via SSH to 10.10.10.4
- Pi-hole: API at http://10.10.10.22/admin/api.php
- Checkmk: REST API via HTTPS
```

### Step 4: Create Initial Settings

**Copy and customize**: `reference/pai-reference/.claude/settings.json`

Key changes for Deckard:
```json
{
  "env": {
    "DA": "Deckard",
    "PAI_DIR": "$HOME/.claude"
  },
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${PAI_DIR}/hooks/load-core-context.ts"
          }
        ]
      }
    ]
  }
}
```

### Step 5: Create First Workflow

**Create**: `~/.claude/skills/infrastructure-ops/workflows/checkmk-query.md`

```markdown
---
name: checkmk-query
description: |
  Query Checkmk API for host status, metrics, and service information.
  USE WHEN user asks about: host status, service state, metrics, alerting
---

# Checkmk Query Workflow

## What This Does
Queries Checkmk API to retrieve infrastructure status in real-time.

## Prerequisites
- Checkmk API access
- Query type (hosts, services, metrics)
- Optional: filter criteria (host group, service state, etc.)

## Execution Steps

1. **Determine Query Type**
   - Host status: All hosts and their state
   - Service status: Services for specific hosts
   - Metrics: Performance data for hosts/services
   - Alerts: Current alerting status

2. **Build API Query**
   - Use livestatus protocol or HTTP API
   - Format: GET /monitoring/live
   - Example: `hostgroup = "production"`

3. **Execute Query**
   ```bash
   curl -s "https://checkmk.ratlm.com/monitoring/live" \
     -H "Accept: application/json" \
     --data "GET hosts\nColumns: name state\n"
   ```

4. **Parse Results**
   - Extract relevant fields
   - Categorize by severity
   - Identify anomalies

5. **Format Response**
   - Structured output with host groups
   - Color coding for severity
   - Direct links to Checkmk dashboards

## Example: Query All Production Hosts

```
User: "What's the status of all production systems?"

Deckard:
1. Query Checkmk for hosts in "production" group
2. Get state, last check time, check count
3. Identify any DOWN or UNREACHABLE hosts
4. Calculate uptime percentage
5. Return:
   - Summary (X hosts, Y down, Z degraded)
   - List of each host with state
   - Anomaly alerts
   - Links to drill down in Checkmk
```

## Error Handling
- API unavailable: Fall back to SSH check
- Authentication: Use stored credentials
- Parse errors: Log and ask for clarification

## Safety Notes
- Read-only operation (no risk)
- No infrastructure changes
- Safe to execute frequently
```

### Step 6: Test the Foundation

```bash
# Start Claude Code
claude

# In Claude Code, test:
"Hello Deckard, what infrastructure components are available?"
# Should load your core context and list infrastructure
```

---

## Phase 2: First Integration (Week 2-3)

### Step 7: Create Checkmk Integration

**Create**: `~/.claude/documentation/api-endpoints.md`

```markdown
# API Endpoints Reference

## Checkmk
- **Type**: REST API via livestatus protocol
- **Endpoint**: https://checkmk.ratlm.com/monitoring/live
- **Auth**: Configured in ~/.env
- **Key Operations**:
  - GET hosts
  - GET services
  - GET hostgroups
  - Acknowledge alerts
  - Trigger diagnostics

## BIND9
- **Primary**: 10.10.10.4 (SSH access)
- **Secondary**: 10.10.10.2 (SSH access)
- **Commands**:
  - Zone file editing (direct)
  - `rndc reload` (reload after changes)
  - `rndc zonestatus <zone>`
  - `/etc/bind/zones/db.<domain>`

## Pi-hole
- **Primary**: 10.10.10.22
- **Secondary**: 10.10.10.23
- **API**: http://<ip>/admin/api.php
- **Key Operations**:
  - Query statistics
  - Get gravity (whitelist/blacklist)
  - Add/remove filters
  - Check replication status

## Nginx Proxy Manager
- **Endpoint**: 10.10.10.3
- **Web UI**: https://10.10.10.3
- **Operations**:
  - Create/update proxy hosts
  - Manage SSL certificates
  - View access logs
```

### Step 8: Create Checkmk Workflow

**Create**: `~/.claude/skills/infrastructure-ops/workflows/host-status.md`

This workflow queries Checkmk for host status and provides detailed reporting.

### Step 9: Create DNS Management Workflow

**Create**: `~/.claude/skills/dns-management/workflows/record-add.md`

This workflow safely adds DNS records with validation.

### Step 10: Test Integration

```bash
# In Claude Code:
"Show me the status of the Checkmk server"
# Should query infrastructure-ops skill and return status

"Check the BIND9 primary server"
# Should query primary DNS server status
```

---

## Phase 3: Automation Integration (Week 3-4)

### Step 11: Create Ansible Skill

**Create**: `~/.claude/skills/automation/workflows/run-playbook.md`

- Find playbooks in `~/ai_projects/ansible_playbooks/`
- Execute with check mode preview
- Show changes before applying
- Request approval for execution

### Step 12: Connect to Existing Ansible

Map existing playbooks to workflows:
- `patch_systems.yml` → workflow: `patch.md`
- `bootstrap.yml` → workflow: `bootstrap.md`
- `add_users_2_group.yml` → workflow: `user-management.md`
- etc.

### Step 13: Create Troubleshooting Skill

**Create**: `~/.claude/skills/troubleshooting/workflows/network-diagnosis.md`

Enable systematic troubleshooting workflows.

---

## Phase 4: Enhancement (Week 4+)

### Step 14: Add Hooks

Copy hooks from reference and customize:
- `load-core-context.ts` - Load core context on session start
- `capture-all-events.ts` - Capture interactions for history
- `update-tab-titles.ts` - Update statusline

### Step 15: Create History System

Enable `~/.claude/history/` with:
- `sessions/` - Archive of past sessions
- `solutions/` - Documented solutions
- `incidents/` - Post-mortems and learnings

### Step 16: Add Monitoring Skill

Create workflows for:
- Health reports
- Alert analysis
- SLA tracking
- Trend analysis

---

## Quick Reference: Critical Files to Create

| File | Purpose | Complexity |
|------|---------|-----------|
| `~/.claude/skills/CORE/SKILL.md` | Core identity | Simple |
| `~/.claude/documentation/infrastructure-topology.md` | Infrastructure map | Simple |
| `~/.claude/documentation/api-endpoints.md` | API reference | Simple |
| `~/.claude/settings.json` | Claude Code config | Simple |
| `~/.claude/skills/infrastructure-ops/SKILL.md` | Skill description | Medium |
| `~/.claude/skills/infrastructure-ops/workflows/checkmk-query.md` | First workflow | Medium |
| `~/.claude/hooks/load-core-context.ts` | Event hooks | Complex |

---

## Rollout Strategy

### Week 1: Foundation
- Initialize structure
- Create core identity
- Document infrastructure
- Configure settings

**Success Metric**: You can ask "What's our infrastructure?" and get a coherent answer

### Week 2-3: First Integration
- Checkmk queries working
- DNS management workflow available
- Can query host status

**Success Metric**: You get instant status reports instead of manual web UI navigation

### Week 3-4: Automation
- Ansible integration working
- Can run playbooks safely
- Check mode preview working

**Success Metric**: You run a patching job through Deckard with approval workflow

### Week 4+: Enhancement
- History system capturing everything
- Multiple skills active
- Proactive suggestions

**Success Metric**: You ask "How did we fix that DNS issue?" and get the answer from history

---

## Common Pitfalls to Avoid

1. **Don't skip the infrastructure documentation**
   - Deckard needs to know your topology
   - Without it, it can't make intelligent decisions

2. **Don't hardcode credentials**
   - Use `~/.env` with proper permissions
   - Reference endpoints, not secrets

3. **Don't skip validation in early workflows**
   - Always test in check mode first
   - Show changes before executing
   - Require approval for modifications

4. **Don't rush to Phase 4**
   - Foundation matters more than features
   - Better to have 1 working workflow than 5 broken ones
   - Build incrementally

5. **Don't forget security**
   - `~/.claude/` is sensitive - exclude from public repos
   - Always verify git remotes before committing
   - Document infrastructure cautions

---

## Success Checklist

- [ ] `.claude/` directory structure created
- [ ] Core identity documented in CORE/SKILL.md
- [ ] Infrastructure topology documented
- [ ] API endpoints cataloged
- [ ] settings.json configured
- [ ] First workflow (checkmk-query) created
- [ ] Can ask infrastructure questions and get answers
- [ ] Checkmk integration working
- [ ] DNS workflow functional
- [ ] Ansible integration active
- [ ] Troubleshooting skill available
- [ ] History system capturing sessions
- [ ] Multiple skills working in coordination

---

## Getting Help

- **Reference Implementation**: `/home/brian/claude/Deckard/reference/pai-reference/.claude/`
- **Architecture Guide**: `ARCHITECTURE.md`
- **What Changes**: `WHAT_CHANGES.md`
- **Claude Code Docs**: https://docs.claude.com/

---

**Next Action**: Start with Step 1 - create the directory structure and move to Phase 1.

Last Updated: November 13, 2025
