# Deckard: Personal AI Infrastructure Architecture

## Project Vision

**Deckard** is a Personal AI Infrastructure (PAI) system designed to augment your operational capabilities as a Linux infrastructure engineer at Elliott. It integrates with your existing homelab infrastructure (Checkmk, BIND9, Pi-hole, Nginx Proxy Manager) and Jarvis (local LLM backend) to provide an intelligent assistant for automation, monitoring, and infrastructure management.

**Core Philosophy**: System design over model intelligence. The infrastructure, orchestration, and scaffolding matter more than the underlying model's raw capabilities.

---

## Infrastructure Foundation

### Backend: Jarvis (10.10.10.49)
- **OS**: Ubuntu 24.04 LTS
- **Hardware**: RTX 3050 GPU, 23GB RAM, 98GB storage
- **Services**:
  - **Ollama** - Local LLM inference engine
    - Mistral 7B (4.4GB)
    - Qwen2.5 7B (4.7GB)
  - **OpenWebUI** (Docker) - Web interface on port 3000
- **Capability**: Runs local models without external API dependencies

### Infrastructure Integration Points
These systems become accessible to Deckard through custom skills and tools:

- **Checkmk** (10.10.10.5) - Monitoring API for system health and alerting
- **BIND9** (10.10.10.4 primary, 10.10.10.2 secondary) - DNS management and zone operations
- **Pi-hole** (10.10.10.22 primary, 10.10.10.23 secondary) - DNS filtering and statistics
- **Nginx Proxy Manager** (10.10.10.3) - Reverse proxy and SSL/TLS management
- **Home Assistant** (10.10.10.6) - Home automation integration
- **Firewalla** (10.10.10.1) - Network firewall and security
- **Proxmox** (10.10.10.17) - Virtual infrastructure management

---

## System Architecture

### Three-Layer Design

```
┌─────────────────────────────────────────────────────────┐
│  Interface Layer                                         │
│  ├─ Claude Code (Primary interaction)                  │
│  ├─ Shell aliases and commands                         │
│  ├─ OpenWebUI chat (Jarvis web interface)             │
│  └─ Custom statusline integration                      │
└─────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────┐
│  Orchestration Layer                                    │
│  ├─ Skills (domain expertise containers)              │
│  │  ├─ infrastructure-ops                             │
│  │  ├─ monitoring                                     │
│  │  ├─ dns-management                                 │
│  │  ├─ automation                                     │
│  │  ├─ troubleshooting                                │
│  │  └─ research                                       │
│  ├─ Workflows (discrete tasks within skills)          │
│  ├─ Agents (parallel execution orchestration)         │
│  ├─ Context System (~/.claude/)                       │
│  └─ Hooks (pre/post processing, event capture)        │
└─────────────────────────────────────────────────────────┘
          ↓
┌─────────────────────────────────────────────────────────┐
│  Execution Layer                                        │
│  ├─ Local CLI tools and scripts                        │
│  ├─ Ansible playbooks (existing infrastructure)        │
│  ├─ API integrations (Checkmk, Pi-hole, etc.)         │
│  ├─ Jarvis inference (Ollama models)                   │
│  └─ Infrastructure operations                          │
└─────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
/home/brian/claude/Deckard/
├── .claude/                          # Core PAI system (mirrors ~/.claude/)
│   ├── CLAUDE.md                     # Core context and customization
│   ├── PAI.md                        # PAI system documentation
│   ├── settings.json                 # Claude Code configuration with hooks
│   ├── agents/                       # Orchestration agents
│   │   ├── infrastructure-ops.md
│   │   ├── monitoring-agent.md
│   │   ├── dns-agent.md
│   │   ├── researcher.md
│   │   └── [others as needed]
│   ├── skills/                       # Domain expertise containers
│   │   ├── CORE/
│   │   │   └── SKILL.md             # Core identity, contacts, preferences
│   │   ├── infrastructure-ops/
│   │   │   ├── SKILL.md
│   │   │   ├── CLAUDE.md
│   │   │   └── workflows/
│   │   │       ├── checkmk-query.md
│   │   │       ├── dns-update.md
│   │   │       ├── host-remediation.md
│   │   │       ├── capacity-planning.md
│   │   │       └── [others]
│   │   ├── monitoring/
│   │   │   ├── SKILL.md
│   │   │   └── workflows/
│   │   ├── dns-management/
│   │   │   ├── SKILL.md
│   │   │   └── workflows/
│   │   ├── automation/
│   │   │   ├── SKILL.md
│   │   │   └── workflows/
│   │   ├── troubleshooting/
│   │   │   ├── SKILL.md
│   │   │   └── workflows/
│   │   ├── research/
│   │   │   ├── SKILL.md
│   │   │   └── workflows/
│   │   └── [additional skills]
│   ├── hooks/                        # Event processing
│   │   ├── load-core-context.ts
│   │   ├── capture-all-events.ts
│   │   ├── update-tab-titles.ts
│   │   └── [others]
│   ├── documentation/                # System docs
│   │   ├── architecture.md
│   │   ├── skills-system.md
│   │   ├── context-loading.md
│   │   └── [others]
│   └── history/                      # Session history and upgrades
│       ├── sessions/
│       └── upgrades/
├── reference/
│   └── pai-reference/                # Miessler's PAI reference implementation
├── docs/                             # Project documentation
│   ├── DESIGN_DECISIONS.md
│   ├── INFRASTRUCTURE_GUIDE.md
│   ├── API_REFERENCE.md
│   └── [others]
├── scripts/                          # Utility scripts
│   ├── install-deckard.sh
│   ├── setup-hooks.sh
│   └── [others]
├── CLAUDE.md                         # Project guidance for Claude Code
├── README.md                         # User-facing documentation
└── ARCHITECTURE.md                   # This file
```

---

## Core Components

### 1. Skills System (Domain Expertise Containers)

Skills are domain-specific containers that bundle knowledge, context, and workflows. Each skill encapsulates expertise for a particular domain.

#### Infrastructure Operations Skill
```yaml
name: infrastructure-ops
description: |
  Infrastructure operations including Checkmk monitoring, remediation,
  capacity planning, and health analysis. Handles system integration
  with Checkmk, Pi-hole, BIND9, Nginx Proxy Manager, and Proxmox.
```

**Workflows within infrastructure-ops:**
- `checkmk-query.md` - Query Checkmk API for host/service status
- `dns-update.md` - Manage DNS records via BIND9
- `host-remediation.md` - Execute remediation steps for failed hosts
- `capacity-planning.md` - Analyze system capacity and predict scaling needs
- `network-audit.md` - Audit network configuration and compliance

#### Monitoring Skill
```yaml
name: monitoring
description: |
  Proactive monitoring, alert triage, and performance analysis.
  Integrates with Checkmk for metric collection and alerting.
```

**Workflows within monitoring:**
- `alert-analysis.md` - Analyze alert patterns and trends
- `performance-baseline.md` - Establish and monitor performance baselines
- `sla-tracking.md` - Track SLA compliance and reporting
- `health-report.md` - Generate comprehensive system health reports

#### DNS Management Skill
```yaml
name: dns-management
description: |
  DNS zone management via BIND9, Pi-hole filtering,
  and DNS resolution troubleshooting across the infrastructure.
```

**Workflows within dns-management:**
- `zone-update.md` - Create, modify, or delete DNS zones
- `record-management.md` - Manage individual DNS records
- `zone-transfer.md` - Manage primary/secondary DNS synchronization
- `pihole-management.md` - Configure Pi-hole filtering policies
- `dns-troubleshooting.md` - Diagnose DNS resolution issues

#### Automation Skill
```yaml
name: automation
description: |
  Ansible playbook execution and infrastructure-as-code management.
  Integrates with existing Ansible infrastructure.
```

**Workflows within automation:**
- `run-playbook.md` - Execute Ansible playbooks with validation
- `check-mode.md` - Run playbooks in check mode (dry-run)
- `playbook-development.md` - Create and test new playbooks
- `patching.md` - Execute system patching workflows
- `bootstrap.md` - Bootstrap new hosts with standardized configurations

#### Troubleshooting Skill
```yaml
name: troubleshooting
description: |
  System diagnostics, issue investigation, and remediation strategies.
  Integrates with monitoring and infrastructure operations.
```

**Workflows within troubleshooting:**
- `log-analysis.md` - Parse and analyze system logs
- `network-diagnosis.md` - Diagnose network connectivity issues
- `performance-investigation.md` - Investigate performance problems
- `escalation-guide.md` - Determine escalation path for issues
- `post-mortem.md` - Generate incident post-mortems

#### Research Skill
```yaml
name: research
description: |
  Information gathering using Claude WebSearch and external APIs.
  Support for investigating solutions, exploring technologies, and gathering intelligence.
```

**Workflows within research:**
- `quick-research.md` - Fast information lookup
- `comprehensive-research.md` - In-depth investigation with multiple sources
- `competitive-analysis.md` - Analyze competing solutions or approaches
- `technology-evaluation.md` - Evaluate new technologies for adoption

### 2. Context System (UFC - Unified Filesystem-based Context)

All knowledge lives in `~/.claude/` as organized markdown files, ensuring the AI has the right information at the right time.

#### Tier 1: Always-Active Context (System Prompt)
**~1500-2000 tokens constantly available**:
- Core identity (name, role, personality)
- Essential contacts and relationships
- Stack preferences (languages, tools, package managers)
- Critical security warnings
- Response format requirements

#### Tier 2: On-Demand Context
**Loaded when explicitly needed**:
- Complete contact list and social accounts
- Extended security procedures
- Infrastructure-specific configurations
- Detailed workflow instructions
- Voice IDs for agent routing

#### Key Context Files
```
~/.claude/
├── CLAUDE.md                  # Core identity, essentials, security
├── skills/CORE/SKILL.md       # Extended contacts and preferences
├── documentation/
│   ├── infrastructure.md       # Infrastructure topology and access
│   ├── contacts.md             # Complete contact list
│   ├── security.md             # Security procedures and cautions
│   ├── api-credentials.md      # API endpoint references (no secrets)
│   └── preferences.md          # Personal and operational preferences
├── context/
│   ├── infrastructure-topology.md
│   ├── api-endpoints.md
│   ├── security-requirements.md
│   └── [domain-specific context]
└── scratchpad/
    └── [timestamped working directories]
```

### 3. Hooks System (Event Processing)

Hooks intercept Claude Code events and perform automated actions, enabling passive context management and observability.

```
SessionStart → Load core context, initialize PAI
UserPromptSubmit → Update status line, capture event
PreToolUse → Observe tool execution
PostToolUse → Capture tool output
SessionEnd → Summarize session, archive history
```

**Hook Location**: `~/.claude/hooks/` with TypeScript implementations

### 4. Agents (Parallel Orchestration)

Agents execute tasks in parallel, enabling distributed work and faster results.

**Example Agent: Checkmk Monitor**
```
Input: "Check the status of database servers"
→ Decompose into:
  - Query Checkmk for all database-tagged hosts
  - Collect performance metrics for each host
  - Analyze trends and anomalies
  - Generate status report
→ Execute in parallel with 3-minute timeout
→ Synthesize results with Deckard
```

---

## Integration Patterns

### Pattern 1: Checkmk Integration
**Skill**: infrastructure-ops
**Workflow**: checkmk-query.md

```
User: "What's the status of production systems?"
↓
Deckard: Query Checkmk API → Parse host/service states
         Categorize by severity
         Identify action items
↓
Response: Structured report with links to Checkmk dashboards
```

### Pattern 2: DNS Management
**Skill**: dns-management
**Workflow**: record-management.md

```
User: "Add a new A record for api.example.com pointing to 10.10.10.20"
↓
Deckard: 1. Validate DNS zone ownership
         2. Generate BIND9 record syntax
         3. Test via dig before committing
         4. Reload BIND9 on primary/secondaries
↓
Response: Confirmation with verification results
```

### Pattern 3: Infrastructure Automation
**Skill**: automation
**Workflow**: run-playbook.md

```
User: "Run patching on all non-production servers"
↓
Deckard: 1. Load playbook (patch_systems.yml)
         2. Execute in check mode for preview
         3. Show changes to be made
         4. Execute with approval
         5. Monitor execution and report results
↓
Response: Patching report with affected systems and changes
```

### Pattern 4: Troubleshooting
**Skill**: troubleshooting
**Workflow**: network-diagnosis.md

```
User: "The firewall is blocking traffic to the new service"
↓
Deckard: 1. Gather network topology context
         2. Analyze firewall rules
         3. Identify blocking rules
         4. Suggest remediation
         5. Generate firewall update command
↓
Response: Diagnosis with recommended firewall changes
```

---

## Critical Design Decisions

### 1. Offline-First with Jarvis
**Decision**: Use local Ollama models via Jarvis rather than cloud APIs exclusively

**Rationale**:
- No external API dependencies for core operations
- Lower latency for real-time infrastructure queries
- Privacy for sensitive infrastructure data
- Cost predictability

**Trade-off**: Local models have smaller context windows; compensated with skill-based context management

### 2. Skills-as-Containers Pattern
**Decision**: Organize all capabilities into domain-specific skills

**Rationale**:
- Clear ownership and responsibility
- Easy discovery and composition
- Natural language routing (user intent → skill activation)
- Easier maintenance and evolution
- Scales horizontally as new domains emerge

**Implementation**: Each skill lives in `~/.claude/skills/{skill-name}/` with SKILL.md, workflows/, and optional CLAUDE.md

### 3. Filesystem-based Context (UFC)
**Decision**: All knowledge lives in markdown files, not databases

**Rationale**:
- Integrates seamlessly with Claude Code (reads files naturally)
- Version-controlled and auditable
- Human-readable and debuggable
- No external state management
- Portable across systems

**Implementation**: Hierarchical directory structure with progressive disclosure (tier 1 always active, tier 2 on-demand)

### 4. Infrastructure as Code First
**Decision**: Leverage existing Ansible playbooks rather than rebuilding in custom tools

**Rationale**:
- Existing playbook library covers 95% of use cases
- Deckard orchestrates rather than duplicates
- Lower maintenance burden
- Team consistency

**Implementation**: Automation skill wraps Ansible with validation and monitoring

### 5. Event-Driven History
**Decision**: Hooks capture all interactions for session history and learning

**Rationale**:
- Enables session continuity across instances
- Builds artifact of what Deckard did and how it solved problems
- Supports agent observability and debugging
- Creates audit trail for compliance

**Implementation**: Pre/post hooks capture tool I/O, sessions archive to `~/.claude/history/`

---

## API Integration Reference

### Checkmk API
- **Endpoint**: https://checkmk.ratlm.com/monitoring/live
- **Pattern**: REST API via livestatus or HTTP API
- **Key Operations**: Query hosts, services, metrics; trigger diagnostics

### BIND9
- **Interfaces**: SSH + rndc (remote DNS control)
- **Endpoints**: 10.10.10.4 (primary), 10.10.10.2 (secondary)
- **Key Operations**: Zone transfers, record updates, configuration changes

### Pi-hole
- **Interfaces**: API endpoints
- **Endpoints**: 10.10.10.22 (primary), 10.10.10.23 (secondary)
- **Key Operations**: Query statistics, manage whitelists/blacklists, gravity updates

### Nginx Proxy Manager
- **Interface**: 10.10.10.3
- **Key Operations**: Proxy configuration, SSL certificate management, access logs

### Proxmox
- **Interface**: 10.10.10.17 API
- **Key Operations**: VM/LXC creation, resource monitoring, backup management

---

## Security Model

### Tier 1: Identity & Authentication
- Local operation via Jarvis (no external auth required)
- SSH keys for infrastructure access
- API tokens stored in secure `.env` files (excluded from version control)

### Tier 2: Authorization
- Role-based context (different skills for different operations)
- Infrastructure-specific caution warnings
- Three-check git safety before commits

### Tier 3: Data Protection
- `~/.claude/` marked as extremely sensitive
- No secrets in version control
- Infrastructure credentials in local `.env` only
- Session history in `~/.claude/history/` (local only)

### Critical Security Rules
1. **NEVER commit from the wrong directory** - Verify with `git remote -v` before every commit
2. **`~/.claude/` IS SENSITIVE** - Never commit to public repos
3. **CHECK THREE TIMES** before git add/commit from any directory
4. **BE EXTREMELY CAUTIOUS** with infrastructure modifications - prompt for approval
5. **VALIDATE CHANGES** in check mode before executing

---

## Scaling Strategy

### Phase 1: Foundation (Current)
- Core identity and context system
- Infrastructure operations and monitoring skills
- Jarvis integration
- Session history and hooks

### Phase 2: Enrichment
- Additional domain-specific skills (e.g., capacity planning, cost analysis)
- Enhanced agent orchestration
- Voice interface integration (optional)
- Advanced analytics and reporting

### Phase 3: Autonomy
- Proactive anomaly detection
- Self-healing workflows
- Cross-domain orchestration
- Learning from historical patterns

---

## Development Workflow

### Adding a New Skill

1. **Create skill directory**:
   ```bash
   mkdir -p ~/.claude/skills/{skill-name}/workflows
   ```

2. **Write SKILL.md** with frontmatter and description
3. **Create workflows** for discrete tasks
4. **Write CLAUDE.md** for development context (optional)
5. **Test workflows** with manual invocation
6. **Document integration points** in docs/

### Updating Infrastructure Context

1. **Edit context files** in `~/.claude/documentation/`
2. **Validate syntax** and references
3. **Test with agents** to ensure discoverability
4. **Commit with descriptive messages**

### Adding Integration Points

1. **Research target service** (API, authentication, endpoints)
2. **Create integration workflow** in appropriate skill
3. **Test with dry-run** (check-mode, preview mode, etc.)
4. **Document API reference** in docs/API_REFERENCE.md
5. **Create error handling** for common failure modes

---

## Success Metrics

### Operational Efficiency
- Reduction in manual infrastructure queries
- Faster problem identification and remediation
- Fewer escalations to manual investigation

### Context Quality
- Increase in first-attempt solution rate
- Reduction in clarification requests
- Improvement in solution relevance

### System Reliability
- Zero unintended infrastructure changes
- 100% correctness on safety-critical operations
- Full audit trail for all actions

---

## References

- **Miessler's PAI**: `/home/brian/claude/Deckard/reference/pai-reference/`
- **Jarvis Backend**: 10.10.10.49 (Ollama + OpenWebUI)
- **Existing Infrastructure**: See Elliott homelab documentation
- **Ansible Playbooks**: `/home/brian/ai_projects/ansible_playbooks/`

---

## Next Steps

1. **Initialize `.claude/` directory** structure based on this architecture
2. **Customize CORE/SKILL.md** with Deckard identity and preferences
3. **Create infrastructure-ops skill** with initial workflows
4. **Set up hooks** for event capture and history
5. **Create settings.json** with proper permissions and integrations
6. **Document first success** (e.g., simple Checkmk query workflow)

---

**Last Updated**: November 13, 2025
**Status**: Architecture Definition (Ready for Implementation)
