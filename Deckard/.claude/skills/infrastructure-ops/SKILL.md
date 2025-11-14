---
name: infrastructure-ops
description: |
  Infrastructure operations covering monitoring, host remediation, capacity planning, and system health analysis.

  Provides operational procedures for:
  - Checkmk queries and monitoring integration
  - Host status investigation and remediation
  - Capacity planning and resource analysis
  - Network auditing and compliance

  USE WHEN user asks about: host status, service health, infrastructure monitoring, system remediation, capacity planning, performance analysis
---

# Infrastructure Operations Skill

## Skill Overview

The infrastructure-ops skill handles day-to-day operational tasks across the homelab infrastructure. It provides systematic approaches to:

- **Monitoring**: Query Checkmk for real-time infrastructure status
- **Diagnosis**: Investigate failures and anomalies
- **Remediation**: Correct operational issues
- **Capacity**: Plan for growth and resource optimization
- **Auditing**: Verify compliance and configuration correctness

---

## Available Workflows

### checkmk-query
Query Checkmk monitoring API for host status, service health, metrics, and alerting.

**Use When**:
- "What's the status of database servers?"
- "Show me all critical alerts"
- "Get performance metrics for disk usage"
- "Which services are down?"

**File**: `workflows/checkmk-query.md`

### [Additional Workflows - Coming in Phase 2]

#### host-remediation
Execute remediation steps for failed hosts (service restart, connection reset, etc.)

#### capacity-planning
Analyze metrics to forecast resource needs and identify bottlenecks.

#### network-audit
Verify network configuration, DNS resolution, and connectivity across infrastructure.

---

## Operational Philosophy

### Safety-First Approach
- All queries are read-only and low-risk
- Remediation requires explicit approval
- Check-mode preview before any changes
- Complete audit trail of modifications

### Systematic Diagnosis
- Gather complete context before deciding
- Question assumptions in critical areas
- Validate changes thoroughly
- Document findings for future reference

### Minimal Intervention
- Use monitoring data to guide decisions
- Automate repeatable procedures
- Require approval for critical operations
- Fail safe (preserve functionality first)

---

## Core Procedures

### Infrastructure Status Check
1. Query Checkmk for overall host/service status
2. Identify any DOWN or CRITICAL items
3. Categorize by severity
4. Document anomalies
5. Recommend actions

### Host Investigation
1. Get host status and recent checks
2. Query all services on host
3. Review performance metrics if available
4. Check for acknowledged alerts
5. Determine if intervention needed

### Service Troubleshooting
1. Identify problematic service
2. Review plugin output and metrics
3. Check dependencies (other services, hosts, network)
4. Determine root cause
5. Plan remediation steps

### Capacity Analysis
1. Collect performance metrics
2. Analyze trends
3. Identify approaching limits
4. Forecast future requirements
5. Recommend upgrades or optimizations

---

## Integration Points

### Checkmk
- Query API for monitoring data
- Get host and service status
- Retrieve performance metrics
- Acknowledge alerts
- Trigger on-demand checks

### Infrastructure Components
- Query host and service dependencies
- Verify connectivity and replication
- Check configuration consistency

### Automation
- Trigger Ansible playbooks for remediation
- Execute configuration changes
- Run diagnostic commands

---

## Context Requirements

This skill uses the following context:

- **Infrastructure Topology** (`../documentation/infrastructure-topology.md`)
  - Network overview and component roles
  - Service dependencies
  - Access methods for each system

- **API Endpoints** (`../documentation/api-endpoints.md`)
  - Checkmk API details
  - Query format and examples
  - Authentication requirements

- **Core Identity** (`../CORE/SKILL.md`)
  - Infrastructure cautions
  - Security procedures
  - Approval requirements

---

## State Management

All queries are read-only; no state is modified unless explicitly requested and approved.

---

**Last Updated**: November 13, 2025
**Status**: Phase 1 - Foundation Skill
