# Phase 8 Dashboard Architecture

## System Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     THREAT DETECTION & BLOCKING                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ FIREWALLA (10.10.10.1) - Threat Detection                       │
├─────────────────────────────────────────────────────────────────┤
│ • Monitors: SSH attempts, port scans, malicious patterns         │
│ • Generates: ALARM_INTEL events when threat detected            │
│ • Sends: Events to Wazuh Agent (port 1514)                      │
│ • Stores: Logs in `/log/firewalla/firelog.log`                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                    TCP Port 1514/1515
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ WAZUH SERVER (10.10.10.40) - Alert Processing                  │
├─────────────────────────────────────────────────────────────────┤
│ • Receives: ALARM_INTEL events from Firewalla agent            │
│ • Processes: Rules enrichment, GeoIP lookup                     │
│ • Triggers: Webhook to n8n on ALARM_INTEL detection            │
│ • Stores: Alerts in /var/ossec/logs/alerts/alerts.json         │
│ • Enriches: Geolocation data (country, coordinates)             │
├─────────────────────────────────────────────────────────────────┤
│ Alert Fields Captured:                                           │
│ • timestamp: Date/time of detection                             │
│ • data.srcip: Source IP of attacker                             │
│ • rule.level: Severity (1-15 scale)                             │
│ • GeoIP.country: Country of origin                              │
│ • GeoIP.location: Latitude/longitude for mapping                │
└─────────────────────────────────────────────────────────────────┘
                            ↓
            [Webhook to n8n for automated blocking]
                            ↓
                    [Phase 6: Blocking Flow]
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ [DATA STORED IN WAZUH ALERTS INDEX FOR DASHBOARD]               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ WAZUH DASHBOARD (10.10.10.40) - This is Phase 8                │
├─────────────────────────────────────────────────────────────────┤
│ Visualizes Threat Intelligence Data:                            │
│                                                                  │
│ 1. TIMELINE (Line Chart)                                        │
│    └─ Shows: Attack frequency over time                         │
│    └─ Data: Count of ALARM_INTEL per day                        │
│    └─ Expected: 9 points over 26 days                           │
│                                                                  │
│ 2. GEOGRAPHIC DISTRIBUTION (Bar Chart + Heatmap)               │
│    └─ Shows: Country breakdown of attacks                       │
│    └─ Data: GeoIP.country aggregation                           │
│    └─ Expected: US (4), RO (3), SG (1), Other (1)              │
│                                                                  │
│ 3. TOP MALICIOUS IPs (Table)                                    │
│    └─ Shows: All detected IPs with metadata                     │
│    └─ Data: srcip field, grouped by frequency                   │
│    └─ Columns: IP, Country, Alert Count, Dates                  │
│                                                                  │
│ 4. SEVERITY DISTRIBUTION (Pie Chart)                            │
│    └─ Shows: Alert severity levels                              │
│    └─ Data: rule.level field distribution                       │
│    └─ Categories: Critical, High, Medium, Low                   │
│                                                                  │
│ 5. WORLD HEATMAP (Geographic Visualization)                     │
│    └─ Shows: Physical locations of attackers                    │
│    └─ Data: GeoIP.location (lat/lon) with color intensity       │
│    └─ Expected: Clusters in US, Romania, scattered SG           │
│                                                                  │
│ 6. ACTIVE BLOCKED IPs (Metric Card)                             │
│    └─ Shows: Total count of blocked IPs                         │
│    └─ Data: Unique count of srcip values                        │
│    └─ Expected: 9                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Types & Transformations

```
FIREWALLA EVENT                    WAZUH ALERT
┌──────────────────┐              ┌──────────────────┐
│ ALARM_INTEL      │              │ timestamp        │
│ source: 1.2.3.4  │─────────────→│ srcip: 1.2.3.4   │
│ time: 10:30 UTC  │              │ rule.level: 10   │
└──────────────────┘              │ GeoIP.country    │
                                   │ GeoIP.location   │
                                   └──────────────────┘
                                          ↓
                                   DASHBOARD QUERY
                                   ┌──────────────────┐
                                   │ Group by Country │
                                   │ Count per IP     │
                                   │ Aggregate by Day │
                                   │ Unique IPs       │
                                   └──────────────────┘
                                          ↓
                                   VISUALIZATION
                                   ┌──────────────────┐
                                   │ Bar chart        │
                                   │ Table rows       │
                                   │ Timeline points  │
                                   │ Map markers      │
                                   └──────────────────┘
```

---

## Dashboard Queries (Simplified)

### Widget 1: Attack Timeline

```
SELECT COUNT(*) as alert_count
FROM wazuh-alerts
WHERE rule.level >= 8
GROUP BY DATE(timestamp)
ORDER BY timestamp
```

**Visual:** Line starting at Oct 22, showing 9 data points through Nov 16

---

### Widget 2: Top Countries

```
SELECT GeoIP.country, COUNT(*) as attack_count
FROM wazuh-alerts
WHERE rule.level >= 8
GROUP BY GeoIP.country
ORDER BY attack_count DESC
```

**Visual:** Horizontal bar chart showing US (4), RO (3), SG (1), Other (1)

---

### Widget 3: Top Malicious IPs

```
SELECT srcip,
       GeoIP.country,
       COUNT(*) as alerts,
       MIN(timestamp) as first_seen,
       MAX(timestamp) as last_seen
FROM wazuh-alerts
WHERE rule.level >= 8
GROUP BY srcip
ORDER BY alerts DESC
LIMIT 50
```

**Visual:** Table with 9 rows, one per IP

---

### Widget 4: World Map

```
SELECT GeoIP.location.lat, GeoIP.location.lon, COUNT(*) as intensity
FROM wazuh-alerts
WHERE rule.level >= 8
AND GeoIP.location IS NOT NULL
GROUP BY GeoIP.location
```

**Visual:** Heatmap showing attack intensity by location

---

### Widget 5: Severity Distribution

```
SELECT rule.level, COUNT(*) as alert_count
FROM wazuh-alerts
WHERE rule.level >= 3
GROUP BY rule.level
ORDER BY rule.level DESC
```

**Visual:** Pie chart slices by severity level

---

### Widget 6: Blocked IPs Count

```
SELECT COUNT(DISTINCT srcip) as blocked_ips
FROM wazuh-alerts
WHERE rule.level >= 8
```

**Visual:** Single large number: "9"

---

## Index Structure

```
Index Name: wazuh-alerts-*
├─ timestamp (datetime)
├─ agent
│  ├─ id
│  ├─ name ("firewalla")
│  └─ ip (10.10.10.1)
├─ rule
│  ├─ id (numerical)
│  ├─ level (1-15)
│  ├─ description
│  └─ groups ("ALARM_INTEL", "threat_intel")
├─ data
│  ├─ srcip (source IP address)
│  └─ protocol
├─ GeoIP
│  ├─ country (e.g., "United States")
│  ├─ country_iso_code (e.g., "US")
│  ├─ location
│  │  ├─ lat (latitude)
│  │  └─ lon (longitude)
│  └─ city
└─ full_log (raw log text)
```

---

## Integration Points

### With Phase 6 (n8n Blocking)

```
Wazuh Alert                n8n Webhook              Firewalla Block
┌────────────┐    POST     ┌────────────┐    SSH    ┌────────────┐
│ ALARM_INTEL│─────────────→│ Webhook    │─────────→│ iptables   │
│ IP: 1.2.3.4│             │ Node       │   cmd    │ DROP rule  │
└────────────┘             └────────────┘          └────────────┘
     ↓                                                    ↓
  Stored in                                        Blocks traffic
  alerts.json                                      from that IP
     ↓
  QUERIED BY DASHBOARD (Phase 8)
     ↓
  Shows that IP in table & map
```

### With Future Phases

**Phase 9 (Notifications):**
- Dashboard link sent in Slack alerts
- Dashboard snapshot embedded in email reports
- Dashboard URL in SMS notifications

**Phase 10+ (Advanced Analytics):**
- Machine learning on attack patterns
- Predictive blocking of similar IPs
- Automated threshold adjustment based on trends

---

## Data Volume & Performance

### Current Scale (Historical Data)

```
Total Alerts: ~500 (mostly system events)
ALARM_INTEL Alerts: 9 (malicious IPs)
Date Range: Oct 22 - Nov 16, 2025 (26 days)
Time Interval: ~1 attack per 3 days
```

### Query Performance

- **Timeline Query:** <100ms (9 data points)
- **Country Query:** <100ms (3-4 groups)
- **Top IPs Query:** <200ms (50 rows)
- **Map Query:** <300ms (4 location clusters)
- **Total Dashboard Load:** <1 second

### Future Scaling

If attack frequency increases (e.g., 10/day):
- **Current indices:** Handle easily (still <1s loads)
- **Recommended:** Split alerts index by date (daily shards)
- **Consider:** Archive old ALARM_INTEL to separate index

---

## Security & Access

### Dashboard Access Control

```
URL: https://10.10.10.40
Auth: Wazuh admin credentials
HTTPS: Required (SSL/TLS enabled)
Port: 443 (standard HTTPS)
```

### Data Isolation

- Dashboard queries filtered to Firewalla agent only (agent.id: "001")
- ALARM_INTEL events only (rule.groups contains "ALARM_INTEL")
- No access to system logs or sensitive data
- GeoIP data is public information only

---

## Maintenance & Updates

### Daily
- Dashboard auto-refreshes every 5 minutes
- New alerts appear automatically in visualizations

### Weekly
- Review dashboard for new attack patterns
- Check if new IPs appear in the table

### Monthly
- Export metrics for trend analysis
- Archive old dashboard snapshots
- Verify GeoIP data freshness

### Yearly
- Update dashboard design if needed
- Retire very old alerts (>1 year)
- Review and optimize queries

---

## Troubleshooting Guide

| Problem | Cause | Solution |
|---------|-------|----------|
| "No data" in all widgets | Wrong index selected | Verify index is `wazuh-alerts-*` |
| Map widget empty | GeoIP not enriched | Check Wazuh config for GeoIP module |
| Wrong IP count | Filter not applied | Ensure filtering on `rule.level >= 8` |
| Time range wrong | Dashboard time window too narrow | Expand to "Last 90 days" |
| Slow dashboard | Too many data points | Reduce time window or add filters |

---

## Related Documentation

- **Quick Start:** `docs/WAZUH_DASHBOARD_QUICK_REFERENCE.md`
- **Implementation Details:** `PHASE8_DASHBOARD_IMPLEMENTATION.md`
- **Threat Data:** `docs/THREAT_INTELLIGENCE_TRACKING.md`
- **Phase 6 Context:** `PHASE6_FINAL_STATUS.md`
- **n8n Workflow:** `docs/PHASE6_N8N_WORKFLOW_SETUP.md`

---

**Updated:** November 17, 2025
**Status:** Architecture defined, ready for UI implementation

