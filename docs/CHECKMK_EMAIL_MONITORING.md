# Checkmk Email Alert Monitoring

## Overview

Automated email monitoring system that watches your Gmail inbox for Checkmk alerts and triggers remediation actions based on alert severity and type.

**Status**: ✅ Active and running

## How It Works

1. **Email Connection**: Connects to Gmail via IMAP every 5 minutes
2. **Alert Detection**: Filters emails from Checkmk
3. **Subject Parsing**: Extracts alert type and severity
4. **Rule Matching**: Matches alert subject against remediation rules
5. **Action Execution**: Runs configured remediation scripts/commands
6. **Logging**: All actions logged to `/tmp/checkmk_email_monitor.log`

## Setup Details

### Credentials Storage
- **Location**: `/home/brian/.env`
- **Email**: brian.j.arnett@gmail.com
- **App Password**: Securely stored (Gmail app-specific password)
- **Note**: Gmail password is different from your regular Gmail password

### Script Location
```bash
/home/brian/claude/scripts/checkmk_email_monitor.py
```

### Automation
- **Frequency**: Every 5 minutes via cron
- **Cron Job**: `*/5 * * * * /home/brian/claude/scripts/checkmk_email_monitor.py --daemon`
- **Log File**: `/tmp/checkmk_email_monitor.log`

## Philosophy: Prevention > Reaction

⚠️ **Important**: Email monitoring is a **notification + investigation tool**, not an auto-fix system. The approach is:

1. **Threshold Tuning (Prevention)**: Adjust Checkmk thresholds to industry standards
2. **Email Alerts (Notification)**: Get notified when real issues occur
3. **Logged Diagnostics (Investigation)**: Log investigation steps, not auto-restart

This prevents the "reboot loop" where auto-fixes mask root causes.

## Remediation Rules

### Rule: NTP Time CRITICAL
**Pattern**: `NTP Time.*CRIT`
**Action**: Log investigation steps
```
NTP CRITICAL: Check network connectivity to NTP servers
Expected offset < 200ms for proxmox, < 500ms for ansible
Run: chronyc sources (proxmox), chronyd status (ansible)
```
**Why not auto-restart?** NTP issues are usually network/DNS problems, not service issues

### Rule: DNS CRITICAL
**Pattern**: `DNS.*CRIT`
**Action**: Log investigation steps
```
DNS CRITICAL: Check BIND9 status and zone transfers
Run: systemctl status bind9, sudo rndc status
```
**Why not auto-reload?** May indicate zone transfer failure, data corruption, or upstream issues

### Rule: Memory CRITICAL
**Pattern**: `Memory.*CRIT`
**Action**: Log alert for manual review
```
CRITICAL: Memory issue detected - check application logs
Review running processes and recent deployments
```
**Why manual?** Memory exhaustion requires application-level investigation

### Rule: Checkmk Service CRITICAL
**Pattern**: `Checkmk.*CRIT`
**Action**: Log investigation guidance
```
CRITICAL: Checkmk monitoring issue
Run: sudo su - monitoring -c "omd status"
```
**Why manual?** Need to preserve monitoring data before any restart

### Rule: Warning State Transitions
**Pattern**: `OK -> WARN`
**Action**: Log state change
```
WARNING: Service transitioned to warning state - monitor for escalation
```

### Rule: Service Flapping
**Pattern**: `Flapping`
**Action**: Log instability warning
```
FLAPPING: Service is unstable - check recent changes and network
```

### Rule: Generic CRITICAL
**Pattern**: `CRIT` (catch-all)
**Action**: Log for visibility
```
CRITICAL alert received from Checkmk - review dashboard
```

## Real-Time Monitoring

### Check Current Status
```bash
tail -f /tmp/checkmk_email_monitor.log
```

### Manual Run (Test Mode)
```bash
python3 /home/brian/claude/scripts/checkmk_email_monitor.py
```

### Daemon Mode
```bash
python3 /home/brian/claude/scripts/checkmk_email_monitor.py --daemon
```

## Email Subject Examples

Your Checkmk sends alerts like:
- `Checkmk: proxmox/NTP Time OK -> WARN`
- `Checkmk: ansible/NTP Time WARN -> OK`
- `Checkmk: HX99G/Memory WARN -> CRIT`
- `Checkmk: HX99G/Memory Stopped Flapping (WARN)`

All are monitored and reacted to based on pattern matching.

## Adding New Remediation Rules

Edit `/home/brian/claude/scripts/checkmk_email_monitor.py` and add to the `REMEDIATION_RULES` dict:

```python
REMEDIATION_RULES = {
    "Your Pattern Here": {
        "description": "What this does",
        "hosts": ["target", "hosts"],
        "actions": [
            "command to run 1",
            "command to run 2"
        ]
    }
}
```

**Pattern Examples**:
- `"NTP.*CRIT"` - Matches any subject with "NTP" and "CRIT"
- `"DNS.*CRITICAL"` - Case-insensitive regex patterns work
- `"Memory.*"` - Matches anything starting with Memory
- `"OK -> WARN"` - Literal string matching also works

## Logging & Monitoring

### Email Monitor Log
```bash
tail -100 /tmp/checkmk_email_monitor.log
```

### System Logger Messages (from remediation actions)
```bash
grep checkmk_monitor /var/log/syslog | tail -20
```

### Check Cron Execution
```bash
grep CRON /var/log/syslog | grep checkmk_email_monitor | tail -10
```

## Troubleshooting

### No logs appearing in `/tmp/checkmk_email_monitor.log`
- Check crontab: `crontab -l | grep checkmk`
- Run manually to see errors: `python3 scripts/checkmk_email_monitor.py`
- Check that app password is correct in `.env`

### "Cannot connect to Gmail"
- Verify app password is correct (not regular Gmail password)
- Check network connectivity: `curl -I imap.gmail.com`
- Verify 2FA is enabled on Gmail account

### "Action timed out"
- SSH command taking too long - increase timeout in script (line ~240)
- Check that SSH keys are set up for passwordless access

### Remediation not triggering
- Check the pattern in REMEDIATION_RULES matches subject exactly
- Test with: `python3 scripts/checkmk_email_monitor.py --verbose`
- Check Checkmk email subject format matches your rules

## Performance Impact

- **CPU**: Negligible (~1-2% per check, 5 min intervals)
- **Network**: IMAP check ~50KB
- **Disk**: Log file ~10MB/month
- **Memory**: ~15-20MB Python process (on-demand)

## Security Considerations

1. **App Password**: Securely stored in `.env` - not your real Gmail password
2. **SSH Access**: Uses existing SSH key authentication (no passwords)
3. **Logging**: Actions logged but sensitive data filtered
4. **No Storage**: Emails are marked read and left in inbox, not stored locally

## Future Enhancements

- [ ] Slack/Discord notifications before remediation
- [ ] Dry-run mode (log actions without executing)
- [ ] Alert throttling (don't remediate same issue twice in 5 min)
- [ ] Webhook integration for complex remediation
- [ ] Graphite/Prometheus metrics export

## Related Documentation

- [CLAUDE.md](../CLAUDE.md) - Quick reference
- [OPERATIONS.md](./OPERATIONS.md) - Infrastructure operations
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Debugging guides
