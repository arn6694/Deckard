# Infrastructure Operations Troubleshooting Methodology

## Core Principle: Check Logs FIRST

**Never assume a bug exists without checking logs. Configuration corruption, file issues, and service startup failures are more common than framework bugs.**

---

## Universal Troubleshooting Process

### 1. Verify Service Health
```bash
# For Checkmk
sudo su - monitoring -c 'omd status'

# For general systemd services
sudo systemctl status SERVICE_NAME

# Check if processes are actually running
ps aux | grep process_name
```

**What to look for:**
- Any service showing "stopped" or "failed"
- Exit codes indicating service startup failures
- Missing processes that should be running

### 2. Examine Error Logs (Most Important Step)
**Always read logs - they contain the actual error messages that guide you to the solution.**

#### Log File Locations (Checkmk)
| Log File | Purpose | What to Look For |
|----------|---------|-----------------|
| `/omd/sites/monitoring/var/log/web.log` | Web UI errors | SyntaxError, NameError, startup failures |
| `/omd/sites/monitoring/var/log/automation-helper/error.log` | Config loading errors | Configuration parsing failures, missing variables |
| `/omd/sites/monitoring/var/log/ui-job-scheduler/error.log` | Job scheduler issues | Timeouts, connection errors, job failures |
| `/omd/sites/monitoring/var/log/nagios.log` | Monitoring core | Nagios-specific errors |
| `/omd/sites/monitoring/var/log/mkeventd.log` | Event console | Event processing errors |

#### How to Read Logs Effectively
```bash
# View recent errors
sudo tail -100 /omd/sites/monitoring/var/log/automation-helper/error.log

# Search for specific error types
sudo grep -i "error\|exception\|failed" /omd/sites/monitoring/var/log/automation-helper/error.log

# Get context around errors
sudo grep -B 5 -A 5 "SyntaxError" /omd/sites/monitoring/var/log/automation-helper/error.log

# Filter for actionable messages (skip noise)
sudo grep -E "ERROR|Exception|Error" /omd/sites/monitoring/var/log/automation-helper/error.log
```

### 3. Validate Configuration Files
```bash
# Check Python syntax of configuration files
sudo python3 -m py_compile /path/to/file.mk

# Look for corruption in config files
sudo cat /path/to/file.mk | head -20
# Check for:
# - Literal \n characters (should be newlines)
# - Truncated files
# - Malformed Python dictionaries
# - Missing closing braces/brackets
```

### 4. Test System Functions with Full Output
```bash
# Checkmk configuration compilation
sudo su - monitoring -c 'cmk -R 2>&1'

# Look at full output, not just exit code
# Exit code 0 with no output ≠ success if logs show errors
```

### 5. Isolate the Problem
- **Is it a service issue?** (Check `omd status`)
- **Is it a configuration issue?** (Check logs for SyntaxError/NameError)
- **Is it a file corruption issue?** (Check file syntax and contents)
- **Is it a permission issue?** (Check file ownership and permissions)
- **Is it an actual bug?** (Only after ruling out the above)

---

## Common Checkmk Issues and Root Causes

### Issue: Configuration Compiler Fails (`cmk -R` returns error)

**DO NOT assume it's a compiler bug!**

**Step-by-step diagnosis:**
1. Check if all services are running: `omd status`
2. Read automation-helper error log (THIS TELLS YOU WHAT'S WRONG)
3. Look for SyntaxError - means a .mk file has Python syntax errors
4. Look for NameError - means a variable is not defined in the config context
5. Validate the syntax of suspect files: `python3 -m py_compile filename.mk`

**Common actual causes:**
- Corrupted configuration file with literal escape sequences
- Incomplete or truncated .mk file
- Missing closing braces in Python dictionaries
- File with wrong encoding or line endings

### Issue: Web UI Changes Don't Activate

**DO NOT restart services blindly!**

**Step-by-step diagnosis:**
1. Check automation-helper error.log for the actual error
2. Check if ui-job-scheduler is running and healthy
3. Verify configuration can be loaded (check for SyntaxError in logs)
4. Check Nagios configuration validation (nagios.log)

**Common actual causes:**
- Configuration error preventing system load (will show in automation-helper log)
- ui-job-scheduler crashed or hung (check service status and log)
- Nagios configuration validation failure (check nagios.log)

### Issue: New Hosts Not Appearing in Monitoring

**Diagnosis checklist:**
1. Is the host in hosts.mk? `grep hostname /omd/sites/monitoring/etc/check_mk/conf.d/wato/hosts.mk`
2. Did compilation succeed? `sudo su - monitoring -c 'cmk -R 2>&1'`
3. Is the host in Nagios config? `grep hostname /omd/sites/monitoring/etc/nagios/conf.d/check_mk_objects.cfg`
4. Is the host in livestatus? Query via livestatus socket

If host is in hosts.mk but NOT in Nagios config:
- Check automation-helper error log for compilation errors
- Validate hosts.mk syntax: `python3 -m py_compile hosts.mk`
- Check for corrupted files that prevent configuration loading

---

## Real-World Example: Checkmk Corruption Fix

**Symptoms (November 14, 2025):**
- `cmk -R` fails silently
- Changes won't activate in Web UI
- New hosts can't be added to monitoring

**Diagnosis Process:**
1. Checked service status → all running
2. Checked web.log → empty (no errors recorded)
3. Checked automation-helper/error.log → **FOUND IT**: `SyntaxError: unexpected character after line continuation character`
4. Located file: `discover_all_interfaces.mk`
5. Checked file contents: contained literal `\n` instead of newlines
6. **Root cause**: File corruption from improper write/edit

**Solution:**
```bash
sudo rm /omd/sites/monitoring/etc/check_mk/conf.d/wato/discover_all_interfaces.mk
sudo su - monitoring -c 'omd restart'
```

**Result:** System immediately worked correctly. No "bug" existed - it was file corruption.

---

## Best Practices

### For System Changes
1. **Before:** Check current state (logs, status, configuration)
2. **During:** Monitor error logs in real-time if possible
3. **After:** Verify changes worked by checking logs and running tests

### For Troubleshooting
1. **Always start with logs** - they contain the truth
2. **Read full error messages**, not just error names
3. **Follow the error message** - it usually tells you exactly what to do
4. **Check file syntax** before assuming framework bugs
5. **Verify file integrity** - corruption is common from incomplete writes

### For Documentation
- **Document root causes**, not symptoms
- **Include the error message** that revealed the problem
- **Explain the diagnostic process** so others can follow it
- **Include the solution** with exact commands
- **Note the lesson learned** to prevent future recurrence

---

## Key Takeaways

✅ **DO:**
- Check logs first
- Read error messages carefully
- Validate configuration syntax
- Check file integrity
- Follow diagnostic processes systematically

❌ **DON'T:**
- Assume bugs without checking logs
- Restart services as first step
- Make wild guesses about causes
- Skip error message reading
- Rewrite code without understanding the error

---

**Last Updated:** November 14, 2025
**Author:** Deckard Infrastructure Team
**Status:** Living Document - Update as new patterns emerge
