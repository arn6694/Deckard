# NTP Monitoring Strategy

## Overview
Your infrastructure uses Proxmox as the hypervisor with all critical services (BIND9, Checkmk, Pi-hole) running as LXC containers. Time synchronization flows from **Proxmox → Containers/VMs → Applications**.

## Current Configuration

```python
"ntp_time": {
    "proxmox": {
        "levels": (50, 200)    # HYPERVISOR: Stricter thresholds
    },
    "ansible": {
        "levels": (100, 500)   # VM: More lenient thresholds
    }
}
```

Location: `/omd/sites/monitoring/etc/check_mk/conf.d/wato/alert_reduction_checks.mk`

## Host Monitoring Strategy

### ✅ MONITORING ENABLED

**Proxmox (10.10.10.17) - HYPERVISOR**
- Status: Running Chrony
- Thresholds: 50ms warning, 200ms critical
- Current offset: ~0.3ms (Excellent)
- Why stricter: This is the time source for all 18+ containers and VMs
- Impact: Time drift here cascades to ALL dependent systems

**Ansible VM (100) - GENERAL COMPUTE**
- Status: Running Chronyd
- Thresholds: 100ms warning, 500ms critical
- Current offset: ~0.5ms (Excellent)
- Why more lenient: Non-critical VM; only affects its own operations
- No dependent systems rely on its specific time accuracy

### ❌ MONITORING DISABLED (Intentional)

**BIND9 Primary (LXC 119 on Proxmox)**
- Status: No independent NTP service
- Why not monitored: Inherits time from Proxmox container
- Monitoring redundant: If Proxmox drifts, so does BIND9
- Single point of monitoring: Proxmox NTP check covers this

**Checkmk (LXC 107 on Proxmox)**
- Status: No independent NTP service
- Why not monitored: Same as BIND9 - inherits from Proxmox
- Monitoring benefit: Checking Proxmox time is sufficient

**Pi-hole Primary & Secondary (LXC 105 & Docker on Zeus)**
- Status: No independent NTP monitoring
- Why: Pi-hole relies on system time from container
- Secondary (Zeus/Docker) is on separate infrastructure, not critical

**Other VMs/Containers (Jellyfin, Jarvis, OMV, etc.)**
- Status: Using system defaults
- Why: Not critical for monitoring accuracy
- Default thresholds: Let Checkmk apply standard checks

## Threshold Selection Rationale

### Why Proxmox (50, 200)?
1. **Single Point of Failure**: All containers depend on Proxmox's time
2. **DNS Consequences**: Dropped or delayed NTP causes DNS issues
3. **Monitoring Accuracy**: Checkmk relies on accurate time for alerting
4. **Certificate Validation**: VMs with TLS depend on accurate time
5. **Conservative Approach**: 50ms warning catches drift early

### Why Ansible (100, 500)?
1. **Self-Contained**: Only affects its own operations
2. **No Dependents**: Other systems don't rely on its time
3. **Transient Tolerance**: 100ms acceptable for general compute
4. **Practical Threshold**: Avoids false positives while catching real issues

## Current Status

### Health Check (Nov 16, 2025)
```
Proxmox:  0.301 milliseconds offset   ✅ HEALTHY
Ansible:  0.503 milliseconds offset   ✅ HEALTHY
```

Both well within their respective thresholds.

## Operational Guide

### What Triggers Alerts
- **Proxmox Warning**: NTP offset > 50ms
- **Proxmox Critical**: NTP offset > 200ms (serious NTP failure)
- **Ansible Warning**: NTP offset > 100ms
- **Ansible Critical**: NTP offset > 500ms

### Common Causes of High Offset
1. **NTP server unreachable**: Check firewall/network connectivity to NTP servers
2. **Stratum too high**: If Reference ID shows high stratum level, NTP source is poor quality
3. **System load**: Very high CPU load can cause timing issues
4. **VM clock drift**: Virtual machine clock issues (rare with Proxmox/Chrony)

### Remediation Steps
```bash
# Check NTP status
ssh brian@proxmox 'chronyc tracking'
ssh brian@proxmox 'chronyc sources'

# Check NTP service
ssh brian@proxmox 'systemctl status chrony'

# Force time sync
ssh brian@proxmox 'sudo chronyc makestep'
```

## Infrastructure Architecture

```
Internet NTP Servers
        ↓
Proxmox (10.10.10.17) [STRICT: 50/200ms]
    ├─ LXC 107: Checkmk (inherits time)
    ├─ LXC 119: BIND9 Primary (inherits time)
    ├─ LXC 105: Pi-hole Primary (inherits time)
    ├─ VM 100: Ansible [LENIENT: 100/500ms]
    └─ Other VMs/Containers
```

## Summary

- **2 hosts actively monitored** for NTP accuracy
- **Proxmox gets stricter thresholds** because it's the single source of truth
- **VMs get more lenient thresholds** (less critical, no dependents)
- **LXC containers not separately monitored** (inherit from Proxmox)
- **This design avoids alert noise** while protecting critical infrastructure

## Why This Approach Works

1. **Centralized Time Management**: Proxmox time is authoritative; containers inherit it
2. **Reduced Alert Fatigue**: No redundant monitoring of dependent systems
3. **Critical Path Focus**: Alerts catch issues that impact the whole infrastructure
4. **Practical Thresholds**: Based on actual infrastructure dependencies, not generic standards
