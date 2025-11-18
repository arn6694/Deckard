# CLAUDE.md - Repository Guidance

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository. The documentation is split into focused, topic-specific files for easier navigation.

## Repository Overview

This is a homelab operations repository containing scripts and documentation for managing:
- **Monitoring**: Enterprise monitoring via Checkmk 2.4
- **DNS**: Pi-hole DNS/ad-blocking with BIND9 authoritative DNS
- **Services**: Nginx Proxy Manager for reverse proxy and SSL/TLS
- **Integration**: Home Assistant monitoring via Checkmk

## Quick Navigation

### I want to...
| Task | Document | Section |
|------|----------|---------|
| Run production scripts | [`docs/SCRIPTS.md`](docs/SCRIPTS.md) | Quick Start |
| Understand code architecture | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Code Architecture |
| Add or modify scripts | [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) | Common Development Tasks |
| Perform infrastructure operations | [`docs/OPERATIONS.md`](docs/OPERATIONS.md) | Task-specific procedures |
| Debug or troubleshoot issues | [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) | Diagnostics & Fixes |
| Follow code/doc standards | [`docs/STYLE.md`](docs/STYLE.md) | Guidelines |
| Ask about Checkmk | (auto-activates) | `.claude/agents/Checkmk.md` |
| Ask about DNS/networking | (auto-activates) | `.claude/agents/network_engineer.md` |
| Ask about Ansible | (auto-activates) | `.claude/agents/ansible.md` |

## Specialized Agents (Auto-Activate)

These agents activate automatically when relevant questions are asked:
- **`Checkmk.md`** - Checkmk monitoring, alerts, APIs, checks
- **`network_engineer.md`** - DNS, BIND9, Pi-hole, networking infrastructure
- **`ansible.md`** - Ansible automation, infrastructure-as-code, playbooks

No manual activation needed - just ask questions about these topics.

## Key Infrastructure Reference

### Most-Used Commands
| Task | Command |
|------|---------|
| Validate script syntax | `bash -n script.sh` |
| Check Checkmk version | `sudo su - monitoring -c 'omd version'` |
| Test host connectivity | `ssh brian@<host> 'echo ok'` |
| Test DNS resolution | `dig @10.10.10.4 hostname.lan +short` |
| Force service discovery | `sudo su - monitoring -c 'cmk -I <hostname>'` |
| Check agent version (Debian) | `ssh brian@<host> 'dpkg -l \| grep check-mk-agent'` |
| View Checkmk logs | `tail /tmp/checkmk_upgrade_*.log` |
| Reload BIND9 | `ssh brian@10.10.10.4 'sudo rndc reload'` |
| Check backup exists | `ls -la /tmp/checkmk_upgrade_backups/` |
| Test NPM service | `curl -I https://checkmk.ratlm.com` |

### Infrastructure Components Summary
- **Checkmk**: 10.10.10.5 (monitoring site)
- **BIND9 Primary**: 10.10.10.4 (Proxmox LXC 119)
- **BIND9 Secondary**: 10.10.10.2 (Zeus Docker)
- **Pi-hole Primary**: 10.10.10.22 (Proxmox LXC 105)
- **Pi-hole Secondary**: 10.10.10.23 (Zeus Docker)
- **Nginx Proxy Manager**: 10.10.10.3
- **Home Assistant**: 10.10.10.6
- **Firewalla**: 10.10.10.1
- **Proxmox**: 10.10.10.17

## Documentation Files

All detailed information is organized into topic-specific files in the `docs/` directory:

- **[docs/SCRIPTS.md](docs/SCRIPTS.md)** - Production script reference and quick start
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Code design patterns and infrastructure details
- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Adding/modifying scripts and development tasks
- **[docs/OPERATIONS.md](docs/OPERATIONS.md)** - Infrastructure tasks and operational procedures
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Debugging scripts and diagnostics
- **[docs/STYLE.md](docs/STYLE.md)** - Code standards, documentation guidelines, and security practices

## Quick Reference Guide

Use this when you need to find information fast:

1. **Quick reference?** → Start with **[CLAUDE.md](CLAUDE.md)**
2. **Running scripts?** → See **[docs/SCRIPTS.md](docs/SCRIPTS.md)**
3. **Adding/modifying code?** → See **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)**
4. **Doing infrastructure work?** → See **[docs/OPERATIONS.md](docs/OPERATIONS.md)**
5. **Something broke?** → See **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)**
6. **Need to know standards?** → See **[docs/STYLE.md](docs/STYLE.md)**
7. **Understanding the design?** → See **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**

## Available Agents

The following specialized agents are available and will auto-activate when relevant:

### Project-Specific Agents (`.claude/agents/` in this repository)
- **`Checkmk.md`** - Checkmk monitoring, alerts, APIs, checks (auto-activates on Checkmk questions)
- **`network_engineer.md`** - DNS, BIND9, Pi-hole, networking (auto-activates on network questions)
- **`ansible.md`** - Ansible automation, infrastructure-as-code (auto-activates on Ansible questions)
- **`session_closer.md`** - Session management for wrapping up work sessions

### Global Agents (`~/.claude/agents/`)
- **`Python-Instructor.md`** - Python advice, tips, and best practices (auto-activates on Python questions)
- **`youtube_transcript_extractor.md`** - Extract detailed technical transcripts from YouTube videos and save to Obsidian (auto-activates when extracting YouTube content)

## Custom Prompts and Skills Registry

This section documents all custom prompts, agents, and skills created for this repository. Use this as a reference when you need specialized functionality.

### YouTube Transcript Extraction

**File:** `~/.claude/agents/youtube_transcript_extractor.md`

**Purpose:** Extract detailed technical transcripts from YouTube videos with full command documentation and save them to Obsidian notebook.

**When to Use:**
- You want to preserve video content about technical topics
- You need to extract commands, examples, or procedures from a video
- You want reproducible steps from a tutorial formatted for your Obsidian vault

**How to Activate:**
Just ask something like:
- "Extract the transcript from this YouTube video: [URL]"
- "Grab the detailed transcript and save it to Obsidian: [URL]"
- "Create a technical transcript guide from: [URL]"

**What It Does:**
- Extracts complete transcript with timestamps
- Identifies and documents all commands with exact syntax
- Captures examples with input/output
- Documents prerequisites and tool versions
- Creates reproducible step-by-step procedures
- Saves formatted markdown to `/home/brian/Documents/Notes/`

**Output Format:**
- Video metadata (title, channel, date, duration)
- Overview of main topics
- Prerequisites section
- Commands and examples with explanations
- Step-by-step procedures
- Best practices and troubleshooting
- Related commands and references
- Proper markdown with code blocks (language-specific)

---

### Brutal Critic

**File:** `.claude/agents/brutal-critic.md`

**Purpose:** Ruthlessly critique scripts, code, outlines, ideas, and technical work with intentionally harsh, framework-focused feedback that exposes weaknesses and forces better decisions.

**When to Use:**
- You want to **tear apart a script** before it goes to production
- You need **honest feedback on an outline** before writing documentation
- You want to **validate architectural decisions** (or expose them as wrong)
- You need someone to **call out lazy thinking** or dangerous shortcuts
- You're **designing a new process** and want it bulletproofed before rollout
- You want **framework-based feedback** grounded in industry standards and best practices

**How to Activate:**
Just ask something like:
- "Brutal critic: review this script"
- "Give me brutal criticism on this approach"
- "Tear apart this outline - what's wrong with it?"
- "Brutal critic mode: is this a good way to handle X?"
- "Critique this design - don't hold back"

**What It Does:**
- Analyzes work through 7 critical frameworks (Pattern Matching, Risk Assessment, Maintainability, Scalability, Security, Efficiency, Clarity)
- Identifies specific issues and their consequences
- Compares against industry standards and best practices
- Forces examination of assumptions and failure modes
- Provides concrete recommendations for improvement
- Grades the work with honest assessment

**Analysis Framework:**
1. **Pattern Matching** - Does this follow best practices?
2. **Risk Assessment** - What breaks and what's the blast radius?
3. **Maintainability** - Can someone else understand this?
4. **Scalability** - Does this design scale?
5. **Security & Safety** - What's exposed or unsafe?
6. **Efficiency** - Is this the simplest solution?
7. **Documentation & Clarity** - Is the intention clear?

**Output Format:**
- **The Verdict** - One-line core problem summary
- **What's Actually Wrong** - Specific issues identified
- **Why This Matters** - Impact and consequences
- **What You Should Do Instead** - Concrete recommendations
- **Questions You Didn't Ask** - Holes in your thinking
- **Grade** - F/D/C/B/A rating with reasoning

**Key Characteristics:**
- Harsh about the work, never about the person
- Always provides path forward (criticism + solutions)
- Compares against proven standards and frameworks
- Questions assumptions without accepting excuses
- Acknowledges genuinely good work
- Refuses to sugarcoat obvious problems

---

## Linux Engineering Skills

The following skills provide comprehensive automation and management capabilities for Linux engineering tasks. These skills are stored in `~/.claude/skills/` and are available globally.

### Ansible Playbook Runner

**File:** `~/.claude/skills/ansible-runner/SKILL.md`

**Purpose:** Run, test, validate, and troubleshoot Ansible playbooks with best practices for infrastructure automation.

**When to Use:**
- Executing Ansible playbooks with proper safety checks
- Running dry-run tests before production changes
- Validating playbook syntax and inventory
- Installing and managing Ansible Galaxy roles
- Troubleshooting failed playbook executions
- Managing vault-encrypted variables

**How to Activate:**
The skill is invoked automatically when you work with Ansible playbooks or request Ansible operations.

**What It Does:**
- Validates playbook syntax before execution
- Always runs in check mode (dry-run) first
- Tests host connectivity and inventory
- Installs role dependencies from `requirements.yml`
- Handles vault-encrypted files securely
- Provides detailed troubleshooting for failures
- Asks for user approval before making changes
- Documents all changes made

**Key Features:**
- Pre-flight validation (syntax, inventory, connectivity)
- Mandatory dry-run before execution
- User approval workflow for safety
- Comprehensive error handling and debugging
- Support for tags, limits, and vault operations
- Best practices enforcement

---

### Checkmk Automation

**File:** `~/.claude/skills/checkmk-automation/SKILL.md`

**Purpose:** Automate Checkmk operations via REST API including host management, service discovery, and bulk operations.

**When to Use:**
- Adding or removing monitored hosts
- Discovering services on existing hosts
- Managing alert rules and notifications
- Bulk operations on multiple hosts
- Deploying or updating monitoring agents
- Querying monitoring status and metrics
- Configuring HBAC and notification rules

**How to Activate:**
The skill is invoked automatically when you work with Checkmk or request monitoring operations.

**What It Does:**
- Manages hosts via Checkmk REST API
- Performs automatic service discovery
- Activates changes after modifications
- Bulk imports hosts from various sources
- Manages monitoring agents across fleet
- Configures alerting and notifications
- Provides health checks and diagnostics
- Integrates with Ansible inventories

**Key Features:**
- Full REST API integration with Checkmk 2.0+
- Bulk operations for efficiency
- Automatic change activation
- Agent deployment and management
- Service discovery automation
- Integration with existing infrastructure
- Comprehensive error handling

---

### Proxmox Management

**File:** `~/.claude/skills/proxmox-manager/SKILL.md`

**Purpose:** Manage Proxmox VE infrastructure including VMs, LXC containers, storage, networking, and backups via API and CLI.

**When to Use:**
- Creating or cloning virtual machines
- Deploying LXC containers
- Managing VM/container lifecycle (start, stop, migrate)
- Creating snapshots and backups
- Configuring storage pools
- Managing network bridges and VLANs
- Monitoring resource usage
- Performing restore operations

**How to Activate:**
The skill is invoked automatically when you work with Proxmox or request virtualization operations.

**What It Does:**
- Creates and manages VMs and containers
- Handles snapshots and backups
- Manages storage configurations
- Configures network settings
- Monitors resource utilization
- Performs migration operations
- Manages cluster operations
- Automates common provisioning tasks

**Key Features:**
- Full `qm` and `pct` command support
- Template-based VM deployment
- Snapshot management for rollback
- Backup and restore automation
- Resource monitoring and optimization
- Network and storage configuration
- Cluster-aware operations

---

### DNS/BIND9 Management

**File:** `~/.claude/skills/dns-manager/SKILL.md`

**Purpose:** Manage DNS infrastructure including BIND9 zones, Pi-hole configuration, DNS records, and troubleshooting.

**When to Use:**
- Adding or modifying DNS zones
- Managing DNS records (A, AAAA, CNAME, MX, TXT, PTR)
- Configuring zone transfers between primary/secondary
- Managing Pi-hole local DNS entries
- Enabling DNSSEC for zones
- Troubleshooting DNS resolution issues
- Performing bulk DNS record imports
- Migrating DNS infrastructure

**How to Activate:**
The skill is invoked automatically when you work with DNS or BIND9 operations.

**What It Does:**
- Creates and manages BIND9 zones
- Updates DNS records with serial increment
- Configures primary/secondary replication
- Manages reverse DNS (PTR records)
- Integrates with Pi-hole for local DNS
- Enables DNSSEC signing
- Validates zone files before reload
- Provides comprehensive troubleshooting

**Key Features:**
- Automatic serial number management
- Zone file validation before changes
- Primary/secondary synchronization
- Pi-hole integration
- DNSSEC support
- Reverse DNS management
- Bulk record imports from CSV
- Safety checks and backups

---

### FreeIPA Identity Management

**File:** `~/.claude/skills/freeipa-manager/SKILL.md`

**Purpose:** Manage FreeIPA identity and access management including users, groups, hosts, RBAC, Kerberos, and LDAP.

**When to Use:**
- Creating and managing user accounts
- Managing groups and RBAC
- Enrolling hosts to IPA domain
- Configuring SUDO rules
- Setting up HBAC (host-based access control)
- Managing Kerberos principals
- Issuing and managing certificates
- Onboarding/offboarding employees
- Integrating services with FreeIPA

**How to Activate:**
The skill is invoked automatically when you work with FreeIPA or identity management operations.

**What It Does:**
- Creates and manages user accounts
- Handles group memberships and nesting
- Enrolls hosts to IPA domain
- Configures centralized SUDO rules
- Manages HBAC policies
- Handles Kerberos authentication
- Issues service certificates
- Integrates DNS with IPA
- Manages service principals

**Key Features:**
- Complete user lifecycle management
- RBAC with groups and roles
- Host enrollment automation
- Centralized SUDO configuration
- HBAC rule testing and validation
- Kerberos ticket management
- Service principal creation
- Certificate issuance and management
- Replication health monitoring

---

### Netbox Infrastructure Documentation

**File:** `~/.claude/skills/netbox-documenter/SKILL.md`

**Purpose:** Document and manage infrastructure in Netbox DCIM/IPAM including devices, IPs, VLANs, circuits, and relationships.

**When to Use:**
- Documenting physical and virtual infrastructure
- Managing IP address allocations (IPAM)
- Tracking devices, racks, and sites
- Managing VLANs and network segments
- Documenting circuits and providers
- Tracking cable connections
- Generating infrastructure documentation
- Syncing from existing infrastructure (Proxmox, etc.)
- Maintaining source of truth

**How to Activate:**
The skill is invoked automatically when you work with Netbox or infrastructure documentation.

**What It Does:**
- Documents devices and virtual machines
- Manages IP address allocations
- Tracks physical and logical connections
- Manages sites, racks, and locations
- Documents circuits and providers
- Creates VLANs and network segments
- Generates infrastructure reports
- Syncs data from infrastructure tools
- Provides bulk import/export

**Key Features:**
- Full REST API integration
- Python `pynetbox` library support
- Bulk operations via CSV import
- Infrastructure synchronization
- IP address planning and allocation
- Cable and connection tracking
- Custom fields and tags
- Documentation generation
- Relationship mapping

---

### RHEL/Oracle Linux Engineering

**File:** `~/.claude/skills/rhel-engineering/SKILL.md`

**Purpose:** Senior-level Red Hat Enterprise Linux and Oracle Linux system administration, performance tuning, troubleshooting, and security hardening for enterprise production environments.

**When to Use:**
- RHEL/OEL system administration and optimization
- Performance tuning (CPU, memory, disk, network)
- Troubleshooting production issues systematically
- SELinux configuration and troubleshooting
- Security hardening and compliance
- Storage management (LVM, filesystems)
- Kernel tuning and module management
- Systemd service management
- Container operations (Podman/Buildah)
- Subscription and repository management

**How to Activate:**
The skill is invoked automatically when you work with RHEL/OEL systems or request Linux system administration tasks.

**What It Does:**
- System administration fundamentals (packages, services, users)
- Performance optimization across all subsystems
- Systematic troubleshooting methodology
- SELinux policy management and troubleshooting
- Security hardening (firewalld, AIDE, fail2ban)
- LVM and filesystem operations
- Network configuration (bonding, VLANs, tuning)
- Kernel parameter tuning and module management
- Enterprise container management with systemd integration
- RHEL subscription and repository management

**Key Features:**
- Production-focused best practices
- Systematic troubleshooting approach
- Performance tuning for all subsystems
- Comprehensive SELinux management
- Security compliance (CIS, STIG)
- LVM and storage optimization
- Advanced networking (bonding, VLANs)
- Kernel tuning and crash analysis
- Rootless containers with systemd
- Enterprise change management procedures

**Supported Distributions:**
- Red Hat Enterprise Linux 7, 8, 9
- Oracle Linux 7, 8, 9
- CentOS Stream 8, 9
- Rocky Linux 8, 9
- AlmaLinux 8, 9

---

### Python Security Projects

**File:** `~/.claude/skills/python-projects-security/SKILL.md`

**Purpose:** Senior Python engineer teaching secure programming from beginner to professional through hands-on projects focused on Linux automation, containers, security, and web development.

**When to Use:**
- Learning Python from scratch to professional level
- Building security-focused Python applications
- Linux system automation with Python
- Container management with Python
- Web application development (Flask/FastAPI)
- Security tool development
- Network programming and scanning
- Project-based skill development

**How to Activate:**
The skill is invoked automatically when you work on Python programming or request Python project guidance.

**What It Does:**
- Teaches Python with patient, wizard-level expertise
- Provides beginner to professional project ideas
- Security-first approach in all code
- Covers Linux automation, containers, web dev, security tools
- Comprehensive error handling and best practices
- Input validation and secure coding patterns
- Real-world project examples with full code
- Code review and improvement suggestions

**Key Features:**
- Project-based learning (6+ complete projects)
- Security best practices in every lesson
- Professional code patterns from day one
- Focus areas: Linux, containers, security, web dev, games
- Password hashing, API security, authentication
- Network programming and scanning tools
- Web frameworks (FastAPI) with security
- Comprehensive testing and validation

---

### Podman Container Infrastructure

**File:** `~/.claude/skills/podman-infrastructure/SKILL.md`

**Purpose:** Senior Podman engineer for designing and deploying production container infrastructure on RHEL/Oracle Linux with security-first principles and latest technology.

**When to Use:**
- Designing container infrastructure from scratch
- Installing and configuring Podman on RHEL/OEL
- Implementing rootless container environments
- Systemd integration for containers
- Container networking and storage design
- Security hardening containers
- Production container operations
- Migrating from Docker to Podman

**How to Activate:**
The skill is invoked automatically when you work with Podman or container infrastructure.

**What It Does:**
- Complete Podman installation on RHEL/OEL
- Infrastructure design from ground up
- Rootless container configuration
- Systemd service integration
- Network configuration (CNI, pods, custom networks)
- Storage management and optimization
- Image signing and verification
- Secrets management
- Production monitoring and troubleshooting

**Key Features:**
- RHEL/OEL 8/9 installation procedures
- Rootless containers by default
- Systemd integration for auto-start
- Security hardening (SELinux, signing, secrets)
- Pod networking for multi-container apps
- Volume and storage best practices
- Latest Podman 4.x/5.x features
- Production-ready patterns

---

### Bash Scripting Professional

**File:** `~/.claude/skills/bash-scripting-pro/SKILL.md`

**Purpose:** Senior Bash scripting engineer teaching from beginner to professional with project-based learning, useful automation scripts, and Black Hat techniques for authorized security testing.

**When to Use:**
- Learning Bash scripting from fundamentals
- Building system automation scripts
- Creating security testing tools
- Network scanning and enumeration
- Log monitoring and alerting
- Database backup automation
- Privilege escalation testing (authorized)
- Production script development

**How to Activate:**
The skill is invoked automatically when you work with Bash scripts or shell automation.

**What It Does:**
- Teaches Bash from beginner to professional
- Project-based learning approach
- Security-focused script development
- Black Hat techniques for authorized testing
- Error handling and validation
- Parallel processing techniques
- Professional logging frameworks
- Production-grade patterns

**Key Features:**
- Comprehensive best practices (set -euo pipefail)
- Input validation and sanitization
- Secure temp file handling
- No command injection vulnerabilities
- System backup and automation scripts
- Network reconnaissance tools
- Privilege escalation enumeration
- Reverse shell generators (authorized use!)
- Professional error handling

**Security Tools (Authorized Use Only):**
- Network discovery and scanning
- Port enumeration
- Service detection
- Password cracking helpers
- Privilege escalation checks
- Reconnaissance automation

---

### Katello/Foreman Deployment

**File:** `~/.claude/skills/katello-foreman/SKILL.md`

**Purpose:** Deploy and manage Katello/Foreman on Oracle Linux for enterprise content management, provisioning, patch management, and Ansible integration.

**When to Use:**
- Deploying Katello/Foreman on Oracle Linux
- Enterprise lifecycle management setup
- Content and subscription management
- Kickstart/PXE provisioning configuration
- Ansible integration for configuration management
- Patch and errata management
- Host lifecycle management
- Security and compliance management

**How to Activate:**
The skill is invoked automatically when you work with Katello/Foreman or enterprise lifecycle management.

**What It Does:**
- Latest Katello/Foreman installation on OEL 8/9
- Complete deployment from prerequisites to production
- Content management (RPM, containers, files)
- Lifecycle environment configuration
- Kickstart provisioning setup
- Ansible role integration
- Patch management workflows
- Security hardening
- Backup and recovery procedures
- Troubleshooting and maintenance

**Key Features:**
- Oracle Linux 8/9 deployment
- Latest version installation
- Content views and lifecycle environments
- Kickstart template management
- PXE boot configuration
- Ansible playbook integration
- Errata and patch management
- RBAC and access control
- SSL/TLS configuration
- Hammer CLI automation
- Health monitoring
- Backup procedures

---

## How to Add New Prompts/Skills

When creating new custom prompts, agents, or skills:

1. **Create the file** in appropriate location:
   - Project-specific agents: `.claude/agents/agent-name.md`
   - Global agents: `~/.claude/agents/agent-name.md`
   - Skills: Follow MCP server conventions

2. **Add to CLAUDE.md** immediately under "Custom Prompts and Skills Registry":
   - Include filename/location
   - Describe purpose and use cases
   - Explain how to activate it
   - Detail what it does
   - Show example usage
   - Note any output locations or special behaviors

3. **Follow this template:**
   ```markdown
   ### Feature Name

   **File:** location/filename.md

   **Purpose:** One-line description

   **When to Use:**
   - Use case 1
   - Use case 2

   **How to Activate:**
   Example command or trigger

   **What It Does:**
   - Bullet point 1
   - Bullet point 2

   **Output Format:**
   - Details about output
   - File locations
   - Format specifications
   ```

4. **Commit with message:**
   ```
   FEAT: Add [feature name] prompt/skill

   Description of what it does and when to use it.
   ```

This ensures nothing is forgotten and you always have a reference guide!
