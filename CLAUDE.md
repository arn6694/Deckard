# CLAUDE.md - Repository Guidance

This file provides guidance to Claude Code when working with this repository.

## Critical: Context and Token Management

**Token budget is limited - be mindful of context usage.**

### Token Conservation Rules:
1. **Use Task tool with specialized agents** for exploratory work (Explore, Plan, code-analysis:detective)
2. **Avoid unnecessary file reads** - only read files directly needed for current task
3. **Summarize outputs** - don't keep full command outputs in context
4. **Use specialized tools** - Grep/Glob for searches, Read/Edit/Write for files (not bash)
5. **Delegate exploration** - prefer agent delegation over inline investigation

### When to Delegate vs. Inline:
- **Inline**: Simple, targeted file edits or specific command execution
- **Delegate to Task**: Codebase exploration, research, investigation, architecture questions

---

## Repository Overview

Homelab operations repository containing scripts and documentation for:
- **Monitoring**: Checkmk 2.4 and Wazuh security monitoring
- **DNS**: Technitium DNS (Primary 10.10.10.22, Backup on Zeus 10.10.10.2)
- **Services**: Nginx Proxy Manager for reverse proxy and SSL/TLS
- **Integration**: Home Assistant monitoring via Checkmk

## Current Status (Last Updated: 2025-12-10)

### Services Fully Operational
- Technitium HA DNS - Primary 10.10.10.22 + Backup on Zeus 10.10.10.2
- PiKVM (10.10.10.14) - KVM-over-IP for Proxmox (pikvm.ratlm.com)
- Wazuh IDS Detection - 100% coverage with Geo-Visualization
- Nginx Proxy Manager (10.10.10.3) - All reverse proxy and SSL/TLS
- Checkmk (10.10.10.5) - Enterprise monitoring
- Calibre-Web (10.10.10.44) - Ebook management

### Deprecated Services
- Pi-hole DNS (replaced by Technitium)
- BIND9 Primary (replaced by Technitium)

### Known Issues
- Wazuh firewall alert workflow not posting to Discord (n8n broken - not critical)
- n8n.ratlm.com showing Google Safe Browsing warning (false positive)

---

## Quick Navigation

| Task | Document |
|------|----------|
| Run production scripts | [`docs/SCRIPTS.md`](docs/SCRIPTS.md) |
| Understand code architecture | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| Add or modify scripts | [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) |
| Perform infrastructure operations | [`docs/OPERATIONS.md`](docs/OPERATIONS.md) |
| Debug or troubleshoot issues | [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) |
| Follow code/doc standards | [`docs/STYLE.md`](docs/STYLE.md) |
| **Skills & agents documentation** | [`docs/SKILLS-REGISTRY.md`](docs/SKILLS-REGISTRY.md) |

---

## Key Infrastructure Reference

### Most-Used Commands

| Task | Command |
|------|---------|
| Validate script syntax | `bash -n script.sh` |
| Check Checkmk version | `sudo su - monitoring -c 'omd version'` |
| Test host connectivity | `ssh brian@<host> 'echo ok'` |
| Test DNS (Primary) | `dig @10.10.10.22 hostname.lan +short` |
| Test DNS (Backup) | `dig @10.10.10.2 hostname.lan +short` |
| Force service discovery | `sudo su - monitoring -c 'cmk -I <hostname>'` |
| Access Technitium Primary | `http://10.10.10.22:5380` |
| Access Wazuh Dashboard | `https://10.10.10.40:443` |
| Access Wazuh Manager (LXC 112) | `ssh brian@10.10.10.17 'sudo pct exec 112 -- <command>'` |

### Infrastructure Components

| Service | IP | Purpose |
|---------|-----|---------|
| Firewalla | 10.10.10.1 | Gateway/Firewall/IDS |
| Zeus | 10.10.10.2 | Synology NAS, Technitium Backup |
| Nginx Proxy Manager | 10.10.10.3 | Reverse proxy |
| Checkmk | 10.10.10.5 | Monitoring |
| Home Assistant | 10.10.10.6 | Home automation |
| PiKVM | 10.10.10.14 | KVM-over-IP |
| Proxmox | 10.10.10.17 | Hypervisor |
| Technitium DNS Primary | 10.10.10.22 | DNS (LXC) |
| Wazuh | 10.10.10.40 | Security monitoring (LXC 112) |
| Calibre-Web | 10.10.10.44 | Ebook management (LXC 121) |

---

## Available Skills & Agents

Skills and agents auto-activate when relevant topics are mentioned.

### Project Skills (`.claude/skills/`)
- **`checkmk/`** - Checkmk 2.4 expertise with workflows, safety checks, troubleshooting
- **`frontend-design/`** - Beautiful UI design (avoids AI slop aesthetics)
- **`n8n.md`** - n8n workflow automation

### Project Agents (`.claude/agents/`)
- **`Checkmk.md`** - Monitoring questions (prefer the skill for comprehensive guidance)
- **`network_engineer.md`** - DNS, Technitium, networking
- **`ansible.md`** - Ansible automation
- **`brutal-critic.md`** - Harsh technical critique
- **`black-friday-shopper.md`** - Deal hunting and shopping
- **`session_closer.md`** - Session wrap-up

### Global Skills (`~/.claude/skills/`)
- **`senior-it-director/`** - Model selection, strategic decisions
- **`wellness/`** - Health, fitness, nutrition
- **`growth/`** - Learning, habits, goals
- **`reflection/`** - Reviews, introspection
- **`create-agent-skills/`** - Build new skills
- **`debug-like-expert/`** - Systematic debugging

> **Full documentation:** See [`docs/SKILLS-REGISTRY.md`](docs/SKILLS-REGISTRY.md) for detailed skill/agent usage.

---

## Documentation Files

| File | Purpose |
|------|---------|
| [`docs/SCRIPTS.md`](docs/SCRIPTS.md) | Production script reference |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Code design patterns |
| [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md) | Development tasks |
| [`docs/OPERATIONS.md`](docs/OPERATIONS.md) | Operational procedures |
| [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) | Debugging and diagnostics |
| [`docs/STYLE.md`](docs/STYLE.md) | Code standards |
| [`docs/SKILLS-REGISTRY.md`](docs/SKILLS-REGISTRY.md) | Skills & agents documentation |

---

*Updated: 2026-01-01*
