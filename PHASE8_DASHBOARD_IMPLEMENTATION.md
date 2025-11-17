# Phase 8: Dashboard Implementation - In Progress

**Date Started:** November 17, 2025
**Status:** Implementation In Progress
**Estimated Completion:** 2-3 hours

---

## Overview

Creating visual dashboards in Wazuh to track attack metrics, geographic origins, and block effectiveness. This dashboard will provide at-a-glance visibility into the threat intelligence system and automated blocking workflow.

**Goal:** Build "Threat Intelligence Summary" dashboard with 6 key widgets showing:
1. Attack timeline and frequency trends
2. Geographic distribution of attacks (heatmap)
3. Top malicious IPs
4. Alert severity breakdown
5. Currently blocked IPs status
6. Block effectiveness metrics

---

## Dashboard Access & Credentials

**URL:** https://10.10.10.40
**Credentials:** Use Wazuh admin credentials
**Browser:** Navigate to **Dashboards** → **Create Dashboard**

---

## Historical Threat Data Reference

### Currently Blocked IPs (9 Total)

| # | IP | Country | Date | Status |
|---|----|---------|----|--------|
| 1 | 142.93.115.5 | US (DigitalOcean) | Nov 16, 12:29am | ✅ Blocked |
| 2 | 78.153.140.177 | Romania | Nov 12, 3:30pm | ✅ Blocked |
| 3 | 78.153.140.179 | Romania | Nov 7, 8:30pm | ✅ Blocked |
| 4 | 66.240.205.34 | US | Nov 7, 1:13pm | ✅ Blocked |
| 5 | 178.128.95.222 | Singapore | Nov 5, 12:20am | ✅ Blocked |
| 6 | 45.148.10.243 | US | Nov 2, 10:29pm | ✅ Blocked |
| 7 | 66.235.168.222 | US | Nov 2, 1am | ✅ Blocked |
| 8 | 66.240.205.34 | US | Oct 23, 2:00pm | ✅ Blocked |
| 9 | 78.153.140.224 | Romania | Oct 22, 9:14am | ✅ Blocked |

**Geographic Distribution:**
- 🇷🇴 Romania: 3 IPs (33%)
- 🇺🇸 United States: 4 IPs (44%)
- 🇸🇬 Singapore: 1 IP (11%)
- Other: 1 IP (11%)

**Attack Pattern:**
- Peak activity: October 22 - November 16 (26 days)
- Frequency: ~1 attack every 3 days
- All detected via Firewalla threat intelligence
- All blocked via n8n automation

---

## Implementation Steps

### Step 1: Create New Dashboard

1. Open Wazuh Dashboard: https://10.10.10.40
2. Navigate to **Dashboards** (left sidebar)
3. Click **Create Dashboard**
4. Name: `Threat Intelligence Summary`
5. Description: `Real-time visualization of malicious IP detection, geolocation analysis, and automated blocking effectiveness`
6. Click **Create**

**Status:** ⏳ [To be completed in Wazuh UI]

---

### Step 2: Add Widgets

#### Widget 1: Attack Timeline (Line Chart)

**Type:** Line Chart
**Title:** `Malicious IP Detections - Timeline`
**Description:** `Attack frequency over time`

**Data Configuration:**
- **Index:** Select Wazuh alerts index
- **Date Histogram:** Use `timestamp` field
- **Time Interval:** Daily
- **Y-Axis:** Count of ALARM_INTEL events
- **Metric:** Count
- **Buckets:** Date histogram (daily)

**Expected Output:** Line showing ~9 attacks over 26-day period (Oct 22 - Nov 16)

**Status:** ⏳ [To be completed in Wazuh UI]

---

#### Widget 2: Top Countries (Bar Chart)

**Type:** Bar Chart
**Title:** `Attack Origins by Country`
**Description:** `Geographic distribution of malicious IPs`

**Data Configuration:**
- **Index:** Wazuh alerts index
- **Buckets:** Terms aggregation on GeoIP country field
- **Metric:** Count
- **Top:** 10 countries
- **Order:** Count descending

**Expected Data:**
- United States: 4 attacks
- Romania: 3 attacks
- Singapore: 1 attack
- Other: 1 attack

**Status:** ⏳ [To be completed in Wazuh UI]

---

#### Widget 3: World Map (Geolocation)

**Type:** Geographic Coordinate Map or Region Map
**Title:** `Attack Origins - World Heatmap`
**Description:** `Visual heatmap of malicious IP locations`

**Data Configuration:**
- **Index:** Wazuh alerts index
- **GeoJSON:** World map
- **Location Field:** GeoIP location (latitude/longitude)
- **Metric:** Count of attacks per location
- **Color Scale:** Red (more attacks) → Yellow (fewer attacks)

**Expected Output:** Heatmap showing:
- 🔴 Romania: 3 clusters
- 🟠 United States: 4 scattered points
- 🟡 Singapore: 1 point

**Status:** ⏳ [To be completed in Wazuh UI]

---

#### Widget 4: Top Malicious IPs (Table)

**Type:** Data Table
**Title:** `Top Malicious IPs`
**Description:** `All detected malicious IPs with metadata`

**Columns to Display:**
- Source IP (srcip)
- Country (GeoIP country_iso_code)
- Alert Count
- First Detected (timestamp - earliest)
- Last Detected (timestamp - latest)
- Block Status

**Data Configuration:**
- **Index:** Wazuh alerts index
- **Buckets:** Terms on `srcip` field
- **Metric:** Count
- **Sort:** Count descending
- **Limit:** 50 rows

**Expected Output:** Table showing 9 IPs sorted by detection frequency

**Status:** ⏳ [To be completed in Wazuh UI]

---

#### Widget 5: Severity Distribution (Pie Chart)

**Type:** Pie Chart
**Title:** `Alert Severity Distribution`
**Description:** `Breakdown of alert severity levels`

**Data Configuration:**
- **Index:** Wazuh alerts index
- **Buckets:** Terms on `alert.level` field
- **Metric:** Count
- **Color Scheme:** Critical (Red) → High (Orange) → Medium (Yellow)

**Expected Output:** Pie chart showing:
- Critical (Level 8-10): Highest percentage
- High (Level 5-7): Medium percentage
- Medium (Level 3-4): Lower percentage

**Status:** ⏳ [To be completed in Wazuh UI]

---

#### Widget 6: Blocked IPs Status (Metric Card)

**Type:** Metric/Single Stat
**Title:** `Active Blocked IPs`
**Description:** `Total IPs currently in blocklist`

**Data Configuration:**
- **Index:** Custom blocklist or Wazuh alerts
- **Metric:** Unique count of `srcip` from ALARM_INTEL alerts
- **Expected Value:** 9

**Display:** Large number display showing "9"

**Status:** ⏳ [To be completed in Wazuh UI]

---

## Query Reference for Manual Data Verification

### Check Wazuh Alerts Structure

```bash
# SSH to Wazuh server
ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.40

# View sample alert with geolocation data
sudo cat /var/ossec/logs/alerts/alerts.json | jq '.data.srcip, .rule.description' | head -20

# Count alerts by rule
sudo cat /var/ossec/logs/alerts/alerts.json | jq -r '.rule.description' | sort | uniq -c | sort -rn

# Check if GeoIP is enriched
sudo cat /var/ossec/logs/alerts/alerts.json | jq '.data | has("GeoIP")' | head -10
```

### Historical Attack Data

```bash
# Get all unique source IPs from alerts
sudo cat /var/ossec/logs/alerts/alerts.json | jq -r '.data.srcip // "unknown"' | sort | uniq

# Count by source IP
sudo cat /var/ossec/logs/alerts/alerts.json | jq -r '.data.srcip // "unknown"' | sort | uniq -c | sort -rn
```

---

## Dashboard JSON Export

Once dashboard is created in Wazuh UI, export it:

1. Open dashboard in Wazuh
2. Click **More** (⋮) menu
3. Select **Export**
4. Copy JSON
5. Save to: `docs/wazuh-threat-intelligence-dashboard.json`

**Command to save:**
```bash
# After exporting from UI, save to git
cat > docs/wazuh-threat-intelligence-dashboard.json << 'EOF'
[paste exported JSON here]
EOF

# Commit
git add docs/wazuh-threat-intelligence-dashboard.json
git commit -m "FEAT: Add Wazuh Threat Intelligence Summary dashboard"
```

**Status:** ⏳ [To be completed after dashboard creation]

---

## Integration with Existing Systems

### Connection to Phase 6 (n8n Blocking)

```
Firewalla Detects Attack
    ↓
Wazuh Receives Alert (ALARM_INTEL)
    ↓
n8n Workflow Triggered → Blocks IP
    ↓
[THIS DASHBOARD VISUALIZES THE RESULTS]
    ↓
Dashboard Shows:
- When attacks occurred (timeline)
- Where attacks came from (geolocation)
- Which IPs were blocked (table)
- Effectiveness (metrics)
```

---

## Monitoring & Maintenance

### Daily Checks
- [ ] Dashboard loads without errors
- [ ] Data refreshes automatically (alerts appear within 5 minutes)
- [ ] Geolocation data is accurate

### Weekly Review
- [ ] Review attack patterns for new trends
- [ ] Verify all new blocked IPs appear in dashboard
- [ ] Check for any false positives

### Monthly Review
- [ ] Export dashboard metrics for reporting
- [ ] Analyze attack patterns
- [ ] Update blocklist strategies if needed

---

## Known Limitations & Notes

**GeoIP Requirements:**
- Wazuh uses MaxMind GeoIP database for geolocation
- Ensure GeoIP database is current
- Some private IPs may not have geolocation data

**Data Retention:**
- Wazuh alerts stored in JSON format
- Dashboard visualizations are real-time queries against alert data
- Older alerts may be archived/compressed

**Performance:**
- Dashboard queries only recent alerts (configurable)
- If performance degrades, adjust time window in widgets

---

## Status Checklist

- [ ] Step 1: Dashboard created in Wazuh
- [ ] Step 2a: Attack Timeline widget added
- [ ] Step 2b: Top Countries widget added
- [ ] Step 2c: World Map widget added
- [ ] Step 2d: Top Malicious IPs table added
- [ ] Step 2e: Severity Distribution widget added
- [ ] Step 2f: Blocked IPs metric added
- [ ] Step 3: Dashboard JSON exported
- [ ] Step 4: Documentation completed
- [ ] Step 5: Dashboard linked from main docs
- [ ] Final verification: All widgets load correctly

---

## Next Steps After Dashboard Completion

1. **Documentation:**
   - Link dashboard from README.md
   - Add screenshot to docs/

2. **Alerts & Notifications:**
   - Add dashboard link to Slack alerts
   - Include link in automated reports

3. **Integration:**
   - Consider exporting metrics to Grafana
   - Set up automated dashboard snapshots

4. **Phase 9:**
   - Enhanced notifications with dashboard link
   - Email reports with dashboard embeds

---

**Implementation Started:** November 17, 2025
**Target Completion:** November 17, 2025 (same day)
**Estimated Time:** 1-2 hours of manual UI work in Wazuh

