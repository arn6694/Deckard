# AGENTS.md - Repository Guidelines for Coding Agents

## Build/Lint/Test Commands

**Shell Scripts:**
- Syntax check: `bash -n script.sh`
- Lint: `shellcheck script.sh` (if available)
- Test single function: `source script.sh && function_name arg1 arg2`

**Python Scripts:**
- Syntax check: `python3 -m py_compile script.py`
- Run: `python3 script.py`

No formal test framework - validate manually on non-critical hosts first.

## Code Style Guidelines

### Shell Scripts
- Shebang: `#!/bin/bash`
- Error handling: `set -e; set -o pipefail`
- Variables: `UPPER_CASE` constants, `lower_case` locals, quote all `"$vars"`
- Functions: `lower_case_with_underscores()`, declare before main logic
- Logging: `log_success()`, `log_error()`, `log_warning()`, `log_info()`, `error_exit()`
- Tests: `[[ ]]` for strings, `(( ))` for arithmetic

### Python Scripts
- Shebang: `#!/usr/bin/env python3`
- Imports: Standard library first, then third-party, then local
- Functions: `snake_case()`, docstrings with purpose
- Error handling: Try/except with specific exceptions
- Logging: Use `logging` module, not print statements

### General
- Naming: descriptive, lowercase with underscores
- Comments: Explain why, not what
- Security: No hardcoded passwords, SSH keys only, validate input
- Commit messages: `TYPE: Brief description` (FEAT, FIX, DOCS, etc.)

## Agent-Specific Rules
- Checkmk questions: Use `.claude/agents/Checkmk.md`
- Network/DNS questions: Use `.claude/agents/network_engineer.md`
- Ansible questions: Use `.claude/agents/ansible.md`</content>
<parameter name="filePath">docs/AGENTS.md