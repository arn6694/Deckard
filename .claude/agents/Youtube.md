# YouTube Transcript Formatting Guide

**Purpose:** Format YouTube transcripts for easy reference and quick lookup in Obsidian vault.

---

## Folder Structure

Organize transcripts by **content creator** for easy navigation:

```
YouTube Transcripts/
├── NetworkChuck/
│   ├── n8n Now Runs My ENTIRE Homelab - NetworkChuck.md
│   ├── AI in the Terminal - NetworkChuck.md
│   └── MCP - Model Context Protocol - NetworkChuck.md
├── [Creator Name]/
│   ├── Video Title - [Creator Name].md
│   └── Another Video - [Creator Name].md
└── [Another Creator]/
    └── Video Title - [Another Creator].md
```

**Naming convention:** `Video Title - [Creator Name].md`

Each creator gets their own folder for easy filtering and discovery.

---

## Video Metadata Header

Always include at the top:

```markdown
# [Video Title]

**Channel:** [Channel Name]
**Duration:** [Minutes]
**Upload Date:** [Date]
**URL:** [YouTube URL]

---

## Overview

[1-3 sentence summary of what the video covers and why it matters]
```

---

## Content Organization

### Structure

Organize the transcript by **major topics and concepts**, NOT chronologically by timestamp.

Use hierarchical headers:
- `## Main Section` - Major topics
- `### Subsection` - Related concepts
- `#### Detail` - Specific points (use sparingly)

### Section Format

Each section should follow this pattern:

1. **Topic introduction** (what is this about?)
2. **Problem or context** (why does this matter?)
3. **Solution/explanation** (what is it?)
4. **Commands/code** (how to do it)
5. **Examples/demos** (see it in action)
6. **Key takeaways** (remember this)

---

## Command and Code Formatting

### Critical Rules

- **ALL commands go in code blocks** with syntax highlighting
- **Commands must be near their explanation** (not separated)
- **Every command should include context**

### Code Block Format

```bash
# What this command does in plain language
command_here

# For multi-step procedures:
step1_command
step2_command

# With explanation after
result_description
```

### Examples

**Good:**
```markdown
### Installing Gemini CLI

**Installation:**

```bash
geminiai CLI  # or on Mac with Homebrew:
brew install gemini-cli
```

Launch Gemini:

```bash
gemini
```
```

**Bad:**
```markdown
### Installing Gemini CLI

First run geminiai CLI. On Mac you can use brew install gemini-cli. Then type gemini to launch it.
```

---

## Formatting Elements

### Bold Text
Use for:
- Important technical terms
- Key concepts
- Things to remember
- File/directory names
- New ideas

```markdown
**Model Context Protocol (MCP)** - A standardized way...
```

### Code Blocks
Use for:
- Bash commands
- Configuration files
- Code snippets
- File paths (when technical)
- Terminal output

### Blockquotes
Use for:
- Definitions
- Important quotes
- Key insights
- Warnings

```markdown
> "This is the game-changer"

> **Note:** This is important
```

### Lists
Use for:
- Steps in a procedure
- Features of a tool
- Benefits or advantages
- Multiple options

```markdown
**Steps:**
1. First do this
2. Then do this
3. Finally do this

**Features:**
- Feature one
- Feature two
- Feature three
```

### Nested Lists
Use for complex hierarchies:

```markdown
### Benefits

1. **Benefit Name**
   - Detail one
   - Detail two
   - Detail three

2. **Another Benefit**
   - Detail one
   - Detail two
```

---

## Video Sections

### Timestamps Section

Include a "Key Timestamps" section listing major topics and their timestamps:

```markdown
## Key Timestamps

- **0:00** - Intro
- **2:40** - Main Concept Explained
- **8:43** - Hands-On Demo
- **15:20** - Advanced Techniques
```

### Resources Section

List all links and resources mentioned:

```markdown
## Resources

- **GitHub:** https://github.com/user/repo
- **Documentation:** https://docs.example.com
- **Official Site:** https://example.com
```

### Notable Quotes Section

Capture important or memorable quotes:

```markdown
## Notable Quotes

> "Key insight that stuck with you"

> "Another memorable quote"
```

---

## Content Density

### What to Include

- ✅ All technical commands and code
- ✅ Configuration examples
- ✅ Step-by-step procedures
- ✅ Explanations of concepts
- ✅ Examples and demos
- ✅ Key takeaways
- ✅ Links and resources
- ✅ Timestamps

### What to Exclude

- ❌ Filler words and phrases
- ❌ Sponsor segments (link only if relevant)
- ❌ Off-topic tangents
- ❌ Repeated explanations
- ❌ "Um"s and "uh"s
- ❌ Long rambling sections (summarize instead)

---

## Special Cases

### Installation Instructions

Group all installation methods together:

```markdown
### Installation

**Mac (Homebrew):**
```bash
brew install tool-name
```

**Linux (apt):**
```bash
sudo apt install tool-name
```

**Windows (npm):**
```bash
npm install -g tool-name
```
```

### Configuration Examples

Show real, usable configurations:

```markdown
### Configuration

Edit the config file:

```bash
nano ~/.config/tool/config.yaml
```

Set these values:

```yaml
key1: value1
key2: value2
nested:
  subkey: value3
```
```

### Before/After Comparisons

When showing improvements:

```markdown
### The Problem (Before)

Old approach description with command:

```bash
old_command
```

### The Solution (After)

Better approach with command:

```bash
new_command
```

**Why it's better:**
- Reason 1
- Reason 2
- Reason 3
```

---

## Organization Examples

### Good Organization

```markdown
## Main Concept

### What It Is
[Explanation]

### Why It Matters
[Context and benefits]

### How to Use It

**Installation:**
[Command]

**Basic Usage:**
[Command and explanation]

**Advanced Usage:**
[More commands and examples]

### Key Takeaways
- Point 1
- Point 2
```

### Poor Organization

```markdown
## Rambling Section
[Mixed explanation, commands, random details]
[No clear structure]
[Commands buried in paragraphs]
```

---

## Style Guidelines

### Tone
- **Clear and direct** - Get to the point
- **Technical but accessible** - Explain jargon
- **Action-oriented** - Focus on "how to do it"
- **No hyperbole** - Be accurate

### Sentence Structure
- Keep sentences short and clear
- One idea per sentence when possible
- Use active voice

### Terminology
- Use the exact names from the video
- Capitalize properly (Python, Docker, etc.)
- Define technical acronyms on first use

---

## Checklist Before Completing

- [ ] All metadata present (title, channel, duration, URL)
- [ ] Overview section written
- [ ] Content organized by topic (not chronological)
- [ ] ALL commands in code blocks
- [ ] Commands near their explanations
- [ ] Bold used for key terms
- [ ] Blockquotes for definitions/quotes
- [ ] Lists for procedures
- [ ] Examples included where helpful
- [ ] Timestamps section included
- [ ] Resources/links listed
- [ ] No rambling sections (summarized instead)
- [ ] File ready to search and reference
- [ ] No copy/paste walls of text

---

## Final Goal

The transcript should be:

✅ **Scannable** - Find information quickly
✅ **Searchable** - Use Obsidian search to locate topics
✅ **Referenceable** - Quick copy/paste of commands
✅ **Self-contained** - Don't need to rewatch video
✅ **Well-organized** - Logical flow and hierarchy
✅ **Easy to follow** - Clear instructions and examples

A person should be able to:
1. Search for a specific command
2. Find it instantly
3. See the context around it
4. Copy and use it immediately

Without rewatching a second of the video.
