---
name: checkmk-query
description: |
  Query Checkmk API for host status, metrics, and service information.
  USE WHEN user asks about: host status, service state, metrics, alerting, infrastructure health, monitoring status
---

# Checkmk Query Workflow

## What This Does
Queries the Checkmk monitoring API to retrieve real-time infrastructure status, host states, service health, and performance metrics. Provides comprehensive infrastructure visibility without manual web UI navigation.

---

## Prerequisites

- Checkmk API accessibility (10.10.10.5 via https://checkmk.ratlm.com/monitoring/live)
- API token configured in `~/.env` as `CHECKMK_TOKEN` (or retrieve from system if available)
- Query type identified (hosts, services, metrics, specific host, specific service)
- Optional: filter criteria (host group, service state, time range, etc.)

---

## Execution Steps

### Step 1: Determine Query Type

Identify what information is being requested:

- **All Hosts**: Every monitored host and state
- **Problem Hosts**: Hosts in DOWN or UNREACHABLE state
- **Specific Host**: Single host and its services
- **Service Status**: Services across hosts (filter by state if needed)
- **Performance Metrics**: Metrics for capacity planning
- **Alerts**: Current alerting status and acknowledgements

### Step 2: Build API Query

Construct the Checkmk livestatus API query:

```bash
# Query format:
GET <table>
Columns: <column1> <column2> ...
Filter: <column> <operator> <value>
And: <additional conditions>
```

**Common Tables**:
- `hosts` - All monitored hosts
- `services` - Services on hosts
- `hostgroups` - Host group membership
- `servicegroups` - Service group membership

**Common Columns**:
- For hosts: `name`, `state`, `plugin_output`, `last_check`, `perf_data`
- For services: `host_name`, `service_description`, `state`, `plugin_output`, `perf_data`

**Common Filters**:
- `state != 0` - Problem states only (1=DOWN, 2=UNREACHABLE for hosts)
- `state != 0` - Service problems (1=WARNING, 2=CRITICAL for services)
- `groups >= database` - Filter by host group containing "database"

### Step 3: Execute Query

Use the Checkmk query helper script:

```bash
bash ~/.claude/documentation/query_checkmk.sh 'GET <table>' '<columns>'
```

The script queries the Checkmk livestatus socket via SSH and returns results.

**Example: Get all hosts and their state**
```bash
bash ~/.claude/documentation/query_checkmk.sh 'GET hosts' 'name state'
```

**Example: Get all hosts with detailed output**
```bash
bash ~/.claude/documentation/query_checkmk.sh 'GET hosts' 'name state plugin_output last_check'
```

**Example: Get all services**
```bash
bash ~/.claude/documentation/query_checkmk.sh 'GET services' 'host_name service_description state'
```

### Step 4: Parse Results

Parse the JSON response:

```bash
curl -s "https://checkmk.ratlm.com/monitoring/live" \
  -H "Accept: application/json" \
  -k \
  --data "GET hosts" | jq '.[] | {name: .[0], state: .[1], output: .[2]}'
```

**State Codes**:
- **Hosts**: 0=UP, 1=DOWN, 2=UNREACHABLE
- **Services**: 0=OK, 1=WARNING, 2=CRITICAL, 3=UNKNOWN

Categorize by severity and identify anomalies.

### Step 5: Format Response

Return structured output with:
- Summary (X hosts monitored, Y problems, Z critical)
- Problematic items listed with state and message
- Grouped by severity (critical, warning, unknown)
- Timestamp of data collection
- Direct link to Checkmk dashboard for drill-down

---

## Example Queries

### Example 1: What's the overall infrastructure status?

**Query**: Get all hosts and their current state

```bash
curl -s "https://checkmk.ratlm.com/monitoring/live" \
  -H "Accept: application/json" \
  -k \
  --data "GET hosts
Columns: name state plugin_output last_check"
```

**Expected Response** (formatted):
```
Total Hosts: 15
Up: 14
Down: 1
Unreachable: 0

Problem Hosts:
- backup-server (DOWN): Ping timeout, last check 2 mins ago
```

### Example 2: Show only problem services

**Query**: Get all services not in OK state

```bash
curl -s "https://checkmk.ratlm.com/monitoring/live" \
  -H "Accept: application/json" \
  -k \
  --data "GET services
Columns: host_name service_description state plugin_output
Filter: state != 0"
```

**Expected Response** (formatted):
```
Problem Services: 2

Critical:
- webserver (HTTP): Connection refused - last check 5 mins ago

Warning:
- database (Disk Space): 85% full - /var is 85% utilized
```

### Example 3: Check specific host and all its services

**Query**: Get all services for a specific host

```bash
curl -s "https://checkmk.ratlm.com/monitoring/live" \
  -H "Accept: application/json" \
  -k \
  --data "GET services
Columns: host_name service_description state plugin_output
Filter: host_name = database-server"
```

**Expected Response** (formatted):
```
Host: database-server (UP)

Services:
✓ CPU Load: OK
✓ Memory: OK
✗ Disk Space (/var): WARNING - 80% full
✓ Network: OK
✓ Process: MySQL: OK
```

### Example 4: Performance metrics for capacity planning

**Query**: Get metrics for specific service

```bash
curl -s "https://checkmk.ratlm.com/monitoring/live" \
  -H "Accept: application/json" \
  -k \
  --data "GET services
Columns: host_name service_description perf_data
Filter: service_description = Disk"
```

**Expected Response**: Performance data showing disk usage trends

---

## Error Handling

### API Unavailable
If Checkmk API returns no response:
1. Verify https://checkmk.ratlm.com is accessible
2. Check if Checkmk service is running on 10.10.10.5
3. Verify network connectivity to 10.10.10.5
4. Fall back to SSH check: `ssh brian@10.10.10.5 'sudo sv status monitoring'`

### Authentication Failure
If API returns 401 Unauthorized:
1. Check if `CHECKMK_TOKEN` is set correctly in `~/.env`
2. Verify token hasn't expired
3. Check Checkmk permissions for user/token

### Parse Errors
If JSON parsing fails:
1. Check if response is valid JSON (sometimes HTML errors returned)
2. Verify column names are correct
3. Try simpler query first (e.g., `GET hosts`)

### No Results
If query returns empty results:
1. Verify filter syntax is correct
2. Check if data actually matches filter (e.g., no DOWN hosts = no results for `Filter: state = 1`)
3. Try without filters first, then add filters incrementally

---

## Safety Notes

This is a **read-only operation** with:
- ✅ Zero risk of changing infrastructure
- ✅ No modifications made
- ✅ Safe to execute frequently for monitoring
- ✅ No approval required
- ✅ Perfect for automated status checks

---

## Integration Points

This workflow integrates with:
- **Checkmk API**: Real-time status data source
- **infrastructure-ops skill**: Part of monitoring capability
- **Other workflows**: Results used in remediation decisions

---

## Common Use Cases

1. **Morning Infrastructure Check**: Get overall status of all systems
2. **Alert Investigation**: Find all services in CRITICAL state
3. **Capacity Planning**: Query disk/memory metrics to plan upgrades
4. **Troubleshooting**: Get detailed status of problematic system
5. **Automation Trigger**: Query specific metrics to make decisions
6. **Health Reports**: Generate comprehensive infrastructure health summary

---

## Tips & Best Practices

1. **Always include `state` column** - Helps identify problems immediately
2. **Use `plugin_output`** - Gives you the actual error/status message
3. **Filter early** - Use Checkmk filters rather than post-processing if possible
4. **Include `last_check`** - Shows if data is fresh or stale
5. **Test small queries first** - Start with `GET hosts` to verify API works, then build up
6. **Parse with jq** - Makes output human-readable when needed

---

**Last Updated**: November 13, 2025
**Status**: Phase 1 - Foundation Workflow
