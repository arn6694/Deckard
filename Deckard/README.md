# Deckard: Personal AI Infrastructure for Elliott

**Deckard** is a Personal AI Infrastructure (PAI) system designed to augment your capabilities as a Linux infrastructure engineer. It integrates Claude Code with your existing homelab infrastructure (Checkmk, BIND9, Pi-hole, Nginx PM, Proxmox) and Jarvis (local Ollama backend) to provide an intelligent, conversational assistant for infrastructure operations.

## What You Get

Instead of manual web UI navigation, command-line fumbling, and error-prone configurations, you get:

```
You: "What's the status of the database servers?"
Deckard: [Queries Checkmk API, analyzes metrics, identifies issues]
Result: Instant report with status, recommendations, and direct links
```

- **Instant Infrastructure Queries** - Ask questions, get answers in seconds
- **Safe Infrastructure Changes** - Validate, preview, and approve before executing
- **Automated Troubleshooting** - Systematic diagnosis across multiple systems
- **Complete History** - Every action documented, searchable, and repeatable
- **Offline-First** - Uses Jarvis for local inference (no external API dependency)

## Quick Start

### For the Impatient

1. **Review the Documents** (30 minutes):
   - [`WHAT_CHANGES.md`](WHAT_CHANGES.md) - What you'll be able to do
   - [`ARCHITECTURE.md`](ARCHITECTURE.md) - How it works under the hood

2. **Follow the Implementation** (2-4 weeks):
   - [`GETTING_STARTED.md`](GETTING_STARTED.md) - Step-by-step setup guide
   - Follows a 4-phase rollout strategy

3. **Start Building** (This Week):
   - Begin Phase 1 (Foundation) in GETTING_STARTED.md
   - Initialize `.claude/` directory structure
   - Create core identity and infrastructure context

### For the Details-Focused

1. **Understand the Architecture** - Read [`ARCHITECTURE.md`](ARCHITECTURE.md) first
   - Three-layer design (Interface, Orchestration, Execution)
   - Skills-based organization
   - Context system (UFC)
   - Integration patterns

2. **Explore the Reference** - Check `/reference/pai-reference/`
   - Daniel Miessler's complete PAI implementation
   - Real examples of skills, workflows, and hooks
   - Clone this to understand the patterns

3. **Plan Your Implementation** - Use [`GETTING_STARTED.md`](GETTING_STARTED.md)
   - 4-phase rollout with checkpoints
   - Critical files to create
   - Success metrics at each phase

## Project Structure

```
Deckard/
├── ARCHITECTURE.md          # System design and patterns
├── WHAT_CHANGES.md          # Concrete examples of new capabilities
├── GETTING_STARTED.md       # Step-by-step implementation guide
├── README.md               # This file
├── .claude/                # Your PAI infrastructure (to be created)
│   ├── skills/             # Domain expertise containers
│   ├── agents/             # Orchestration workers
│   ├── hooks/              # Event processing
│   ├── documentation/      # Infrastructure knowledge
│   └── history/            # Session archives
└── reference/
    └── pai-reference/      # Miessler's PAI (reference implementation)
```

## Key Concepts

### Skills (Domain Expertise Containers)

Each skill encapsulates expertise for a specific domain:

- **infrastructure-ops** - Checkmk, capacity planning, system health
- **monitoring** - Alert analysis, SLA tracking, trend reports
- **dns-management** - BIND9 and Pi-hole integration
- **automation** - Ansible playbook orchestration
- **troubleshooting** - Systematic issue diagnosis
- **research** - Information gathering and analysis

### Workflows (Discrete Tasks)

Each skill contains workflows - specific operational procedures:

- `infrastructure-ops/workflows/checkmk-query.md` - Query host status
- `dns-management/workflows/record-add.md` - Add DNS records safely
- `automation/workflows/run-playbook.md` - Execute Ansible playbooks
- etc.

### Context System (UFC)

All knowledge lives in `~/.claude/` as markdown files:
- **Tier 1**: Always-active essentials (identity, contacts, security)
- **Tier 2**: On-demand comprehensive context (full infrastructure, extended docs)

### Hooks (Event Processing)

Automatic processors that capture interactions and manage context:
- SessionStart → Load core context
- UserPromptSubmit → Update statusline
- SessionEnd → Archive history

## Infrastructure Integration

Deckard integrates with your existing infrastructure:

| Component | IP | Role | Integration |
|-----------|----|----|-------------|
| Checkmk | 10.10.10.5 | Monitoring | API queries for host/service status |
| BIND9 Primary | 10.10.10.4 | DNS | Zone management via SSH |
| BIND9 Secondary | 10.10.10.2 | DNS | Replication verification |
| Pi-hole Primary | 10.10.10.22 | DNS Filtering | Query statistics, filter management |
| Pi-hole Secondary | 10.10.10.23 | DNS Filtering | Replication verification |
| Nginx PM | 10.10.10.3 | Reverse Proxy | Proxy config, SSL certificate management |
| Home Assistant | 10.10.10.6 | Automation | Status monitoring, automation triggers |
| Proxmox | 10.10.10.17 | Virtualization | VM/LXC management, resource monitoring |
| Jarvis | 10.10.10.49 | AI Backend | Ollama models, local inference |

## Technology Stack

- **Backend**: Jarvis (10.10.10.49) - Ubuntu 24.04, Ollama, OpenWebUI
- **GPU**: NVIDIA RTX 3050 (6GB VRAM)
- **Interface**: Claude Code with skills and hooks
- **Models**: Mistral 7B, Qwen2.5 7B
- **Automation**: Ansible (existing playbooks)
- **History**: Filesystem-based (markdown in ~/.claude/)

## Implementation Timeline

### Week 1: Foundation
- Create `.claude/` structure
- Define core identity
- Document infrastructure
- Configure settings

**Success**: You can ask "What's our infrastructure?" and get coherent answers

### Week 2-3: First Integration
- Checkmk queries working
- DNS management workflow
- Can get instant status reports

**Success**: Infrastructure queries work better than manual web UI navigation

### Week 3-4: Automation
- Ansible integration working
- Can run playbooks safely
- Check-mode preview available

**Success**: Run a complete patching job through Deckard with approval workflow

### Week 4+: Enhancement
- History system capturing everything
- Multiple skills coordinated
- Proactive suggestions

**Success**: Ask "How did we fix that issue before?" and get the answer

## Success Metrics

**Operational**:
- 90% reduction in time for infrastructure queries
- 80% reduction in time for DNS updates
- 70% reduction in patching time
- 75% reduction in troubleshooting time

**Quality**:
- Zero unintended infrastructure changes
- 100% correctness on safety-critical operations
- Complete audit trail for all actions
- Searchable history of all decisions

**Knowledge**:
- Capture infrastructure expertise in system
- Reduce knowledge silos
- Enable new team members to self-serve
- Build library of proven solutions

## Important Notes

### Security

- `~/.claude/` contains **EXTREMELY SENSITIVE** private data - NEVER commit to public repos
- Always verify git remote before committing: `git remote -v`
- Check three times before `git add/commit` from any directory
- Jarvis backend access is local (no external APIs needed for core operations)

### Safety

- All infrastructure changes require approval (check-mode preview first)
- Complete audit trail for every action
- Read-only operations are safe to run frequently
- All modifications are validated before execution

### Practical Considerations

- Deckard augments your expertise, doesn't replace your judgment
- You remain the decision-maker - Deckard executes what you approve
- First few weeks will feel slower (setup overhead), then becomes much faster
- Knowledge captured in system scales across team

## Next Steps

1. **Start Here**: Read [`WHAT_CHANGES.md`](WHAT_CHANGES.md) - 10 minutes
2. **Understand the Design**: Read [`ARCHITECTURE.md`](ARCHITECTURE.md) - 30 minutes
3. **Plan Implementation**: Read [`GETTING_STARTED.md`](GETTING_STARTED.md) - 20 minutes
4. **Begin Phase 1**: Follow Week 1 steps in GETTING_STARTED.md - 2-3 hours

## Documentation

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [`WHAT_CHANGES.md`](WHAT_CHANGES.md) | Concrete examples of new capabilities | 10 min |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | System design and patterns | 30 min |
| [`GETTING_STARTED.md`](GETTING_STARTED.md) | Implementation guide (4 phases) | 20 min |
| [`reference/pai-reference/README.md`](reference/pai-reference/README.md) | Daniel Miessler's PAI system | 20 min |

## References

- **Miessler's PAI Video**: https://www.youtube.com/watch?v=iKwRWwabkEc
- **PAI Blog**: https://danielmiessler.com/blog/personal-ai-infrastructure
- **PAI GitHub**: https://github.com/danielmiessler/Personal_AI_Infrastructure
- **Claude Code Docs**: https://docs.claude.com/
- **Local Reference**: `/home/brian/claude/Deckard/reference/pai-reference/`

## Quick Reference: What to Read

**TL;DR - Just tell me what to do**:
- Go to [`GETTING_STARTED.md`](GETTING_STARTED.md) → Phase 1 → Week 1

**I want to understand the vision first**:
- Read [`WHAT_CHANGES.md`](WHAT_CHANGES.md) → Then GETTING_STARTED.md

**I want to understand the architecture**:
- Read [`ARCHITECTURE.md`](ARCHITECTURE.md) → Then explore `reference/pai-reference/.claude/skills/CORE/SKILL.md`

**I want to see real examples**:
- Explore `reference/pai-reference/.claude/skills/` → Look at SKILL.md and workflows/

**I'm concerned about safety/security**:
- Read ARCHITECTURE.md → Security Model section
- Read WHAT_CHANGES.md → "What Remains Unchanged" section

## Status

- **Current**: Architecture defined, reference implementation available
- **Next**: Implementation begins (Phase 1)
- **Goal**: Fully operational PAI system by end of November 2025

## Questions?

- Check [`GETTING_STARTED.md`](GETTING_STARTED.md) for implementation questions
- Check [`WHAT_CHANGES.md`](WHAT_CHANGES.md) for capability questions
- Check [`ARCHITECTURE.md`](ARCHITECTURE.md) for design questions
- Explore `reference/pai-reference/` for pattern examples
- Reference Miessler's PAI documentation for PAI-specific concepts

---

**Created**: November 13, 2025
**Version**: 1.0 (Architecture & Foundation)
**Status**: Ready for Phase 1 Implementation
