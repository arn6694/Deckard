# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

**Deckard** is a Personal AI Infrastructure (PAI) system designed to augment infrastructure operations capabilities. It integrates Claude Code with existing homelab infrastructure (Checkmk, BIND9, Pi-hole, Nginx PM, Proxmox) and Jarvis (local Ollama LLM backend) to enable intelligent, conversational infrastructure management.

The repository contains:
- **Comprehensive architecture documentation** explaining the PAI design, three-layer architecture (Interface → Orchestration → Execution)
- **Implementation guide** with 4-phase rollout strategy for building out the PAI system
- **Reference implementation** (476 files) from Daniel Miessler's PAI showing real skill/workflow/hook patterns
- **Foundation for Phase 1** - directory structure, core concepts, and integration patterns

## Quick Navigation

| Task | Document | Section |
|------|----------|---------|
| Understand what Deckard is | [`README.md`](README.md) | Overview & Key Concepts |
| See concrete benefits | [`WHAT_CHANGES.md`](WHAT_CHANGES.md) | Before/after examples |
| Understand architecture | [`ARCHITECTURE.md`](ARCHITECTURE.md) | Three-layer design & components |
| Build implementation | [`GETTING_STARTED.md`](GETTING_STARTED.md) | Phase-by-phase guide |
| See real examples | [`reference/pai-reference/.claude/skills/`](reference/pai-reference/.claude/skills/) | Working skill implementations |

## High-Level Architecture

### Three-Layer Design
```
Interface Layer (Claude Code, shell, statusline)
    ↓
Orchestration Layer (Skills, Workflows, Context System, Hooks, Agents)
    ↓
Execution Layer (Local tools, Ansible, API integrations, Jarvis inference)
```

### Core Components

**Skills** - Domain expertise containers living in `~/.claude/skills/{skill-name}/`:
- Each skill bundles knowledge, context, and workflows for a specific domain
- Examples: infrastructure-ops, monitoring, dns-management, automation, troubleshooting, research
- Pattern: SKILL.md (description) + workflows/ (discrete tasks) + optional CLAUDE.md (dev context)

**Context System (UFC)** - All knowledge in markdown files in `~/.claude/`:
- Tier 1: Always-active essentials (~1500-2000 tokens: identity, security, contacts)
- Tier 2: On-demand comprehensive context (infrastructure topology, full documentation)
- Files auto-loaded by Claude Code based on `.claude/CLAUDE.md` and hooks

**Workflows** - Discrete operational procedures within skills:
- Located at `~/.claude/skills/{skill-name}/workflows/{workflow-name}.md`
- Format: Frontmatter (name, description, use cases) + step-by-step execution
- Examples: checkmk-query.md, record-add.md, run-playbook.md

**Hooks** - Event-driven processors in `~/.claude/hooks/`:
- Intercept Claude Code events (SessionStart, UserPromptSubmit, PostToolUse, SessionEnd)
- Perform automated actions: load context, update statusline, capture history
- TypeScript implementations

**Agents** - Parallel execution orchestrators for complex tasks

### Integration Points

Key infrastructure systems Deckard connects to:
- **Checkmk** (10.10.10.5) - Monitoring API for system health queries
- **BIND9 Primary** (10.10.10.4), Secondary (10.10.10.2) - DNS zone management via SSH
- **Pi-hole** (10.10.10.22/23) - DNS filtering and statistics
- **Nginx PM** (10.10.10.3) - Reverse proxy and SSL/TLS
- **Proxmox** (10.10.10.17) - VM/LXC management
- **Jarvis** (10.10.10.49) - Ollama models (Mistral 7B, Qwen2.5 7B) for local inference
- **Home Assistant** (10.10.10.6), **Firewalla** (10.10.10.1) - Monitoring/integration

## Key Implementation Patterns

### 1. Skill Development Pattern
```
~/.claude/skills/{skill-name}/
├── SKILL.md                           # Skill frontmatter + description
├── workflows/
│   ├── {workflow-1}.md               # First discrete task
│   └── {workflow-2}.md               # Additional workflows
└── CLAUDE.md                          # Optional: dev-specific context
```

**Pattern for workflow frontmatter**:
```yaml
---
name: workflow-name
description: |
  One-sentence description.
  USE WHEN user asks about: [trigger phrases]
---
```

### 2. Context Organization
Files in `~/.claude/` follow progressive disclosure:
- **CLAUDE.md** - Core identity, contacts, security warnings (always active)
- **skills/CORE/SKILL.md** - Extended personality, preferences
- **documentation/** - Infrastructure topology, API endpoints, security procedures, contacts
- **context/** - Domain-specific knowledge loaded on-demand

### 3. Workflow Execution Pattern
Most workflows follow this structure:
1. **Validate prerequisites** - Check access, authentication, required data
2. **Build request/query** - Format API call, command, or operation
3. **Execute safely** - Use check-mode/preview when possible
4. **Parse results** - Extract relevant information, identify anomalies
5. **Format response** - Return structured output with actionable next steps

### 4. Safety-First Approach
- Always validate in check/preview mode before executing changes
- Require explicit approval for infrastructure modifications
- Generate audit trail of all actions
- Document error handling and failure modes in workflows
- Read-only operations safe to run frequently

## Infrastructure Reference

### Most-Used Commands
```bash
# Test infrastructure access
ssh brian@<host> 'echo ok'

# Query DNS
dig @10.10.10.4 hostname.lan +short

# Check Checkmk status
curl -s "https://checkmk.ratlm.com/monitoring/live" \
  -H "Accept: application/json" \
  --data "GET hosts\nColumns: name state\n"

# Reload BIND9
ssh brian@10.10.10.4 'sudo rndc reload'

# Test Pi-hole
curl -s "http://10.10.10.22/admin/api.php?stats"
```

### Infrastructure Topology
- **Network**: 10.10.10.0/24 (firewalla gateway at 10.10.10.1)
- **DNS**: Primary 10.10.10.4 (BIND9), Secondary 10.10.10.2
- **Pi-hole**: Primary 10.10.10.22, Secondary 10.10.10.23
- **Monitoring**: Checkmk 10.10.10.5
- **Proxy**: Nginx PM 10.10.10.3
- **Automation**: Proxmox 10.10.10.17, Jarvis 10.10.10.49

## Implementation Status

**Current Phase**: Phase 1 (Foundation) planning
- Architecture and design complete
- Reference implementation available (476 files)
- `.claude/` directory structure documented
- Critical files list identified

**What Exists**:
- Complete architecture documentation (ARCHITECTURE.md)
- Phase-by-phase implementation guide (GETTING_STARTED.md)
- Working reference system (reference/pai-reference/)
- This guidance file (CLAUDE.md)

**What You'll Build**:
- `.claude/skills/{skill-name}/` - Domain expertise containers
- `.claude/documentation/` - Infrastructure knowledge
- `.claude/hooks/` - Event processors
- Workflows for common operational tasks
- Custom context system tailored to Elliott infrastructure

## Critical Design Decisions

1. **Offline-first** - Use Jarvis Ollama models, not cloud APIs exclusively (privacy, latency, cost)
2. **Skills as containers** - Organize all capabilities by domain (discovery, composition, maintenance)
3. **Filesystem context (UFC)** - All knowledge in markdown files (integration, versioning, debugging)
4. **Infrastructure-as-code leverage** - Orchestrate existing Ansible playbooks vs. rebuilding
5. **Event-driven history** - Hooks capture all interactions for session continuity and learning

## Common Development Tasks

### Add a New Skill
1. Create `~/.claude/skills/{skill-name}/` with `workflows/` subdirectory
2. Write SKILL.md with name, description, and use cases
3. Create workflow files for discrete tasks (see workflow pattern above)
4. Optional: Add CLAUDE.md for development-specific context

### Create a Workflow
1. Plan execution steps (validate → build → execute → parse → format)
2. Reference integration points (APIs, SSH hosts, tools)
3. Include error handling and fallback paths
4. Add examples showing typical use and output
5. Test with manual invocation via Claude Code

### Add Infrastructure Context
1. Edit files in `~/.claude/documentation/`
2. Validate syntax and references
3. Test discoverability with Claude Code prompts
4. Document API endpoints and access methods

### Integrate External Services
1. Research service API and authentication method
2. Create workflow in appropriate skill
3. Test in dry-run/check mode first
4. Document API reference in docs/
5. Add error handling for common failures

## Security & Safety

### Critical Rules
1. **`~/.claude/` is EXTREMELY SENSITIVE** - Never commit to public repos
2. **Always verify git remote** before committing: `git remote -v`
3. **Check three times before `git add/commit`** from any directory
4. **All infrastructure changes require approval** - Show check-mode preview first
5. **Generate complete audit trail** for safety-critical operations

### Credentials & Secrets
- Never hardcode credentials in workflows
- Use `~/.env` files (excluded from version control)
- Reference endpoints and API paths, not secrets
- Document required credentials in workflow prerequisites

### Validation Pattern
For any infrastructure modification:
1. Validate in check/preview mode
2. Show what would change
3. Request explicit approval
4. Execute only if approved
5. Log results for audit trail

## Testing & Validation

When working with Deckard:
- Test read-only operations frequently (they're safe)
- Always use check-mode/preview before modifications
- Validate API connectivity with simple queries first
- Test workflows with non-production data initially
- Capture workflow output for documentation

## Where to Look for Answers

| Question | Best Resource |
|----------|---|
| How should I structure a skill? | `reference/pai-reference/.claude/skills/CORE/SKILL.md` |
| How do I write a workflow? | `reference/pai-reference/.claude/skills/infrastructure-ops/workflows/` |
| What hooks exist? | `reference/pai-reference/.claude/hooks/` |
| How's Checkmk integrated? | `ARCHITECTURE.md` → Integration Patterns section |
| What's the security model? | `ARCHITECTURE.md` → Security Model section |
| How do I get started? | `GETTING_STARTED.md` → Follow 4-phase plan |

## Next Steps for Implementation

**Phase 1 (Week 1) - Foundation**:
- Initialize `~/.claude/` directory structure
- Create core identity (CORE/SKILL.md)
- Document infrastructure topology
- Configure settings.json
- Success: Can ask infrastructure questions and get answers

**Phase 2 (Weeks 2-3) - First Integration**:
- Create checkmk-query workflow
- Create DNS management workflow
- Success: Instant status reports vs. manual UI navigation

**Phase 3 (Weeks 3-4) - Automation**:
- Create Ansible execution workflows
- Connect to existing playbooks
- Success: Run complete patching jobs safely

**Phase 4 (Week 4+) - Enhancement**:
- Add hooks for history capture
- Create additional skills (troubleshooting, research)
- Success: Deckard becomes primary infrastructure assistant

## Important Notes

### Philosophy
Deckard augments your expertise, doesn't replace your judgment. You remain the decision-maker—Deckard executes what you approve.

### Context Management
The context system is designed to give Claude the right information at the right time:
- Tier 1 (~1500-2000 tokens) always active
- Tier 2 loaded on-demand by reading documentation files
- Hooks can programmatically load context based on events

### Why This Architecture Matters
- **Skills system** ensures knowledge is organized, discoverable, and reusable
- **UFC (filesystem context)** integrates seamlessly with Claude Code and version control
- **Hooks** enable passive context management and observability
- **Workflows** make complex operations repeatable and auditable
- **Agents** enable parallel execution for faster results

---

## Current Status (Last Updated: November 14, 2025)

### Today's Work
- Verified pihole1 and ansible monitoring in Checkmk (both operational)
- Recovered from critical hosts.mk deletion by restoring from backup
- Created comprehensive troubleshooting methodology guide
- Enhanced Checkmk workflows with firewall and service discovery requirements
- Corrected documentation about WATO configuration compiler issues

### Decisions Made
- Always verify backup exists before modifying Checkmk configuration
- pihole2 will be set up on pi5 hardware in next session (awaiting hardware)
- Created systematic troubleshooting framework to prevent destructive actions

### Current Focus
Phase 1 foundation work with real operational tasks:
- Building infrastructure-ops skill with real-world workflows
- Documenting actual incident recovery procedures
- Next: pihole2 setup on pi5 hardware

### Known Issues
- WATO web interface configuration compiler has cosmetic bugs (does NOT affect core monitoring)
- pihole2 not yet configured (pending pi5 hardware setup)

### Next Steps
1. Set up pihole2 on pi5 hardware and integrate with Checkmk
2. Validate all monitored hosts comprehensively
3. Implement backup validation workflow
4. Continue Phase 1 infrastructure-ops skill development

---

**Created**: November 13, 2025
**Version**: 1.1
**Status**: Phase 1 In Progress - Infrastructure-ops skill active, real-world operational testing
