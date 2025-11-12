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
| Run production scripts | [`SCRIPTS.md`](SCRIPTS.md) | Quick Start |
| Understand code architecture | [`ARCHITECTURE.md`](ARCHITECTURE.md) | Code Architecture |
| Add or modify scripts | [`DEVELOPMENT.md`](DEVELOPMENT.md) | Common Development Tasks |
| Perform infrastructure operations | [`OPERATIONS.md`](OPERATIONS.md) | Task-specific procedures |
| Debug or troubleshoot issues | [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) | Diagnostics & Fixes |
| Follow code/doc standards | [`STYLE.md`](STYLE.md) | Guidelines |
| Ask about Checkmk | (auto-activates) | `Checkmk.md` agent |
| Ask about DNS/networking | (auto-activates) | `network_engineer.md` agent |
| Ask about Ansible | (auto-activates) | `ansible.md` agent |

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

All detailed information is organized into topic-specific files:

- **[SCRIPTS.md](SCRIPTS.md)** - Production script reference and quick start
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Code design patterns and infrastructure details
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Adding/modifying scripts and development tasks
- **[OPERATIONS.md](OPERATIONS.md)** - Infrastructure tasks and operational procedures
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Debugging scripts and diagnostics
- **[STYLE.md](STYLE.md)** - Code standards, documentation guidelines, and security practices

## Quick Reference Guide

Use this when you need to find information fast:

1. **Quick reference?** → Start with **[CLAUDE.md](CLAUDE.md)**
2. **Running scripts?** → See **[SCRIPTS.md](SCRIPTS.md)**
3. **Adding/modifying code?** → See **[DEVELOPMENT.md](DEVELOPMENT.md)**
4. **Doing infrastructure work?** → See **[OPERATIONS.md](OPERATIONS.md)**
5. **Something broke?** → See **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**
6. **Need to know standards?** → See **[STYLE.md](STYLE.md)**
7. **Understanding the design?** → See **[ARCHITECTURE.md](ARCHITECTURE.md)**

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
