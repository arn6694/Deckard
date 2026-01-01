# Custom Prompts and Skills Registry

This document catalogs all custom prompts, agents, and skills available in this repository. Reference this when you need specialized functionality.

> **Note:** This documentation is kept separate from CLAUDE.md to avoid loading 300+ lines of meta-documentation on every prompt. Skills auto-activate when relevant topics are mentioned.

---

## Quick Reference

| Skill/Agent | Location | Auto-Activates On |
|-------------|----------|-------------------|
| Checkmk Expert | `.claude/skills/checkmk/` | Checkmk, monitoring, hosts, agents |
| Frontend Design | `.claude/skills/frontend-design/` | UI, frontend, components, design |
| Network Engineer | `.claude/agents/network_engineer.md` | DNS, networking, Technitium |
| Ansible | `.claude/agents/ansible.md` | Ansible, playbooks, automation |
| Brutal Critic | `.claude/agents/brutal-critic.md` | "brutal critic", "tear apart" |
| Black Friday Shopper | `.claude/agents/black-friday-shopper.md` | Shopping, deals, gifts |
| Session Closer | `.claude/agents/session_closer.md` | "wrap up", "close session" |

### Global Skills (`~/.claude/skills/`)

| Skill | Purpose |
|-------|---------|
| `checkmk/` | Checkmk 2.4 monitoring expertise |
| `senior-it-director/` | Model selection, strategic decisions |
| `wellness/` | Health, fitness, sleep, nutrition |
| `growth/` | Learning, habits, goals |
| `reflection/` | Reviews, introspection |
| `create-agent-skills/` | Build new skills |
| `create-hooks/` | Claude Code hooks |
| `create-plans/` | Project planning |
| `debug-like-expert/` | Systematic debugging |

---

## Detailed Skill Documentation

### Checkmk Expert Skill

**File:** `.claude/skills/checkmk/`

**Purpose:** Comprehensive Checkmk 2.4.0p15 domain expertise with mandatory research protocols, safety checks, and systematic troubleshooting. Prevents configuration failures and ensures all actions are grounded in official documentation.

**When to Use:**
- Adding or managing Checkmk hosts (new host, modify IP, remove host)
- Troubleshooting monitoring issues (host not visible, services missing, agent problems)
- Configuring services and monitoring rules (service discovery, check parameters, alerts)
- Using REST API for automation (add hosts, discover services, activate changes)
- Fixing configuration problems (WATO sync issues, plugin errors, activation failures)
- Learning Checkmk concepts (architecture, workflows, how monitoring works)

**How to Activate:**
Just mention any Checkmk task or question:
- "Add dns01 host to Checkmk monitoring"
- "Fix services not being discovered"
- "Troubleshoot agent connectivity issue"
- "Explain how Checkmk monitoring works"
- "Automate host addition via REST API"

**What It Does:**
- Routes to appropriate workflow based on your task (7 comprehensive workflows)
- Enforces research-first protocol: consults docs.checkmk.com and GitHub docs before any action
- Provides step-by-step procedures with built-in safety checks
- Includes diagnostic methodology for systematic troubleshooting
- Provides reference materials on configuration files, errors, architecture
- Prevents repeat of past failures (2025-12-12 plugin incompatibility, dns01 struggles)
- Requires evidence-based verification (not just assumptions)

**Workflows Included:**
1. **add-host.md** - Step-by-step: add new host with agent installation and service discovery
2. **manage-host.md** - Modify existing host or remove from monitoring
3. **troubleshoot.md** - Systematic diagnostic methodology for issues
4. **manage-services.md** - Service discovery, monitoring rules, alert configuration
5. **use-rest-api.md** - REST API operations with Python examples
6. **fix-configuration.md** - Configuration issues, activation failures, WATO sync
7. **learn-checkmk.md** - Understand Checkmk concepts and architecture

**Reference Materials Included:**
- **checkmk-api-guide.md** - Complete REST API reference with examples
- **configuration-file-formats.md** - hosts.mk, rules.mk, contacts.mk syntax and structure
- **error-diagnosis.md** - Common error messages and their meanings
- **common-issues.md** - Frequent problems with solutions
- **checkmk-architecture.md** - System design, data flow, components
- **api-credentials.md** - Authentication details and API secrets

**Key Features:**
- Research-first: Always consults official Checkmk documentation before action
- Safety checks: Mandatory validation before configuration changes
- Systematic troubleshooting: Diagnostic procedures instead of blind fixes
- Evidence-based: Requires proof that fixes actually work
- Version-aware: 2.4.0p15 specific guidance
- Escalation path: Clear when to ask for help instead of guessing

**Related Documentation:**
- Full README: `.claude/skills/checkmk/README.md`
- Official Docs: https://docs.checkmk.com/2.4.0p15/en/
- GitHub Docs: https://github.com/Checkmk/checkmk-docs
- REST API: https://docs.checkmk.com/2.4.0p15/en/rest_api.html

---

### Frontend Design Skill

**File:** `.claude/skills/frontend-design/`

**Purpose:** Create distinctive, production-grade frontend interfaces with high design quality. Avoids generic "AI slop" aesthetics.

**When to Use:**
- Building web components, pages, or applications
- Designing landing pages, dashboards, settings panels
- Any UI/UX work

**How to Activate:**
Auto-activates when you mention frontend, UI, components, or design work.

**What It Does:**
- Forces bold aesthetic direction (brutalist, retro-futuristic, luxury, etc.)
- Distinctive typography (no Inter, Roboto, Arial)
- Bold color palettes with sharp accents
- Purposeful animations and micro-interactions
- Creative layouts with unexpected compositions

---

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

---

### Black Friday Shopper

**File:** `.claude/agents/black-friday-shopper.md`

**Purpose:** Comprehensive deal-hunting and gift recommendation agent that finds the best prices across major retailers for family members with tracked interests and budgets.

**When to Use:**
- Black Friday / Cyber Monday shopping season
- Christmas gift planning and research
- Birthday gifts throughout the year
- Product research and price comparison
- Finding alternatives within specific budgets
- Comparing products across multiple retailers

**How to Activate:**
Just ask something like:
- "Find Black Friday deals for my family"
- "Research gaming laptops for my 10-year-old under $1000"
- "Find the best deals on mini PCs with high RAM"
- "Compare coffee machines for my wife"
- "What are good gifts for a 12-year-old who likes Minecraft and fishing?"

**What It Does:**
- Searches major retailers (Amazon, Best Buy, Walmart, Target, Newegg, etc.)
- Compares prices across 3+ sources for each product
- Verifies deal authenticity (checks if discount is genuine)
- Researches product reviews and ratings from expert sources
- Generates tiered recommendations (Best Value, Budget, Premium)
- Provides creative gift alternatives
- Calculates total cost including accessories
- Advises on deal timing (buy now vs. wait)
- Tracks price history and trends when possible

**Family Profile:**
- **12-year-old son:** Roblox/Minecraft gaming, fishing, potential bike interest
- **10-year-old son:** Gaming laptop (primary request), gaming peripherals
- **Wife:** Coffee equipment, slippers, blankets, comfort items
- **User:** Mini PC with AMD Ryzen AI Max+ 395 CPU, 128GB RAM, under $2500 budget

---

## How to Add New Prompts/Skills

When creating new custom prompts, agents, or skills:

1. **Create the file** in appropriate location:
   - Project-specific agents: `.claude/agents/agent-name.md`
   - Global agents: `~/.claude/agents/agent-name.md`
   - Skills: `.claude/skills/skill-name/SKILL.md`

2. **Add to this registry** with:
   - Filename/location
   - Purpose and use cases
   - How to activate it
   - What it does
   - Example usage
   - Output locations or special behaviors

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

---

*Last Updated: 2026-01-01*
