# Phase 8 Dashboard - Visual Implementation Guide

## Dashboard Layout (What You're Building)

```
╔════════════════════════════════════════════════════════════════════════════╗
║               THREAT INTELLIGENCE SUMMARY DASHBOARD                        ║
║                      https://10.10.10.40                                  ║
╠════════════════════════════════════════════════════════════════════════════╣
║                                                                            ║
║  ┌──────────────────────────┐      ┌──────────────────────────┐           ║
║  │    ATTACK TIMELINE       │      │   TOP ATTACK ORIGINS     │           ║
║  │    (Line Chart)          │      │    (Bar Chart)           │           ║
║  │                          │      │                          │           ║
║  │     Count                │      │  🇺🇸 US        ████████  4           ║
║  │      ▲                   │      │  🇷🇴 Romania   ██████    3           ║
║  │    9 │     •             │      │  🇸🇬 Singapore █        1           ║
║  │      │   •   •  •        │      │                          │           ║
║  │    6 │ •   •  •  •       │      │                          │           ║
║  │      │               •   │      │                          │           ║
║  │    3 │                   │      │                          │           ║
║  │      └─────────────────→ │      │                          │           ║
║  │      Oct 22  Oct 29  Nov 5      │                          │           ║
║  │            Date                  │                          │           ║
║  └──────────────────────────┘      └──────────────────────────┘           ║
║                                                                            ║
║  ┌──────────────────────────┐      ┌──────────────────────────┐           ║
║  │   WORLD HEATMAP          │      │  SEVERITY DISTRIBUTION   │           ║
║  │  (Geographic Map)        │      │    (Pie Chart)           │           ║
║  │                          │      │                          │           ║
║  │    🌍 Map View           │      │    Critical 60%  ███████ │           ║
║  │                          │      │    High 30%      ████    │           ║
║  │  Red dots:               │      │    Medium 10%    ██      │           ║
║  │  🔴 Romania (3 clusters) │      │                          │           ║
║  │  🔴 US (scattered)       │      │                          │           ║
║  │  🟡 Singapore (1 point)  │      │                          │           ║
║  │                          │      │                          │           ║
║  └──────────────────────────┘      └──────────────────────────┘           ║
║                                                                            ║
║  ┌──────────────────────────────────────────────────────────────┐         ║
║  │              TOP MALICIOUS IPs (Table)                       │         ║
║  ├────────────────┬──────────┬───────┬──────────┬──────────┤   ║
║  │ IP             │ Country  │ Count │ 1st Seen │ Last Seen│   ║
║  ├────────────────┼──────────┼───────┼──────────┼──────────┤   ║
║  │ 142.93.115.5   │ US       │   1   │ Nov 16   │ Nov 16   │   ║
║  │ 78.153.140.177 │ Romania  │   1   │ Nov 12   │ Nov 12   │   ║
║  │ 78.153.140.179 │ Romania  │   1   │ Nov 7    │ Nov 7    │   ║
║  │ 66.240.205.34  │ US       │   2   │ Oct 23   │ Nov 7    │   ║
║  │ 178.128.95.222 │ Singapore│   1   │ Nov 5    │ Nov 5    │   ║
║  │ 45.148.10.243  │ US       │   1   │ Nov 2    │ Nov 2    │   ║
║  │ 66.235.168.222 │ US       │   1   │ Nov 2    │ Nov 2    │   ║
║  │ 78.153.140.224 │ Romania  │   1   │ Oct 22   │ Oct 22   │   ║
║  │ [... more]     │          │       │          │          │   ║
║  └─────────────────────────────────────────────────────────────┘  ║
║                                                                    ║
║  ┌────────────────┐  ┌────────────────────────────────────────┐  ║
║  │ ACTIVE BLOCKS  │  │ System Status                          │  ║
║  │       9        │  │ ✅ n8n Blocking: Active                │  ║
║  │     Blocked    │  │ ✅ Wazuh Alerts: Live                 │  ║
║  │       IPs      │  │ ✅ Geolocation: Enriched              │  ║
║  └────────────────┘  │ ⏳ Last Update: 5 min ago             │  ║
║                      └────────────────────────────────────────┘  ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════════════╝
```

---

## Creation Steps (Visual Order)

### Step 1: Create Dashboard Container

```
Wazuh UI > Dashboards > [Create Dashboard]

Name:        "Threat Intelligence Summary"
Description: "Real-time visualization of malicious IP detection, geolocation
             analysis, and automated blocking effectiveness"

✓ Click Create
```

---

### Step 2: Add Widget #1 - Attack Timeline

```
┌─ Dashboard Edit Mode
│
├─ [Add Widget]
│  ├─ Type: Line Chart
│  ├─ Title: "Malicious IP Detections - Timeline"
│  ├─ Index: wazuh-alerts-*
│  ├─ Metric: Count
│  ├─ Time Field: timestamp
│  ├─ Bucket: Date Histogram (daily)
│  └─ [Save]
│
└─ Result: Line showing 9 attacks over 26 days
```

**Expected Visual:**
```
Count
  9 │     •
    │   •   •  •
  6 │ •   •  •  •
    │               •
  3 │
    └─────────────────────→
    Oct 22  Oct 29  Nov 5  Nov 16
```

---

### Step 3: Add Widget #2 - Top Countries

```
┌─ Dashboard Edit Mode
│
├─ [Add Widget]
│  ├─ Type: Bar Chart (Horizontal)
│  ├─ Title: "Attack Origins by Country"
│  ├─ Index: wazuh-alerts-*
│  ├─ Metric: Count
│  ├─ Bucket: Terms (country field)
│  ├─ Sort: Count descending
│  ├─ Limit: 10
│  └─ [Save]
│
└─ Result: Bars showing US:4, RO:3, SG:1
```

**Expected Visual:**
```
🇺🇸 US        ████████ (4)
🇷🇴 Romania   ██████   (3)
🇸🇬 Singapore █        (1)
```

---

### Step 4: Add Widget #3 - World Map

```
┌─ Dashboard Edit Mode
│
├─ [Add Widget]
│  ├─ Type: Geographic Map (or Region Map)
│  ├─ Title: "Attack Origins - World Heatmap"
│  ├─ Index: wazuh-alerts-*
│  ├─ Metric: Count
│  ├─ Location Field: GeoIP.location
│  ├─ Color Scale: Red hottest → Yellow coolest
│  └─ [Save]
│
└─ Result: World map with colored markers showing attack density
```

**Expected Visual:**
```
        🌍 WORLD MAP
    🔴 (Romania - 3 clusters)
         🔴 (US - scattered)
            🟡 (Singapore)
```

---

### Step 5: Add Widget #4 - Top Malicious IPs Table

```
┌─ Dashboard Edit Mode
│
├─ [Add Widget]
│  ├─ Type: Data Table
│  ├─ Title: "Top Malicious IPs"
│  ├─ Index: wazuh-alerts-*
│  ├─ Columns to Show:
│  │  ├─ Source IP (srcip)
│  │  ├─ Country (GeoIP.country)
│  │  ├─ Alert Count
│  │  ├─ First Seen (earliest timestamp)
│  │  ├─ Last Seen (latest timestamp)
│  │  └─ Status (always "Blocked")
│  ├─ Bucket: Terms (srcip)
│  ├─ Metric: Count
│  ├─ Sort: Count descending
│  ├─ Limit: 50
│  └─ [Save]
│
└─ Result: Table showing all 9 unique IPs with details
```

**Expected Visual:**
```
┌──────────────────┬────────┬───────┬──────────┬──────────┬────────┐
│ IP               │Country │Count  │1stSeen   │LastSeen  │Status  │
├──────────────────┼────────┼───────┼──────────┼──────────┼────────┤
│142.93.115.5      │US      │ 1     │Nov 16    │Nov 16    │Blocked │
│78.153.140.177    │RO      │ 1     │Nov 12    │Nov 12    │Blocked │
│... (9 total)     │        │       │          │          │        │
└──────────────────┴────────┴───────┴──────────┴──────────┴────────┘
```

---

### Step 6: Add Widget #5 - Severity Distribution Pie Chart

```
┌─ Dashboard Edit Mode
│
├─ [Add Widget]
│  ├─ Type: Pie Chart
│  ├─ Title: "Alert Severity Distribution"
│  ├─ Index: wazuh-alerts-*
│  ├─ Metric: Count
│  ├─ Bucket: Terms (alert.level)
│  ├─ Color Scheme:
│  │  ├─ Level 8-10 (Critical): Red
│  │  ├─ Level 5-7 (High): Orange
│  │  └─ Level 3-4 (Medium): Yellow
│  └─ [Save]
│
└─ Result: Pie chart showing severity distribution
```

**Expected Visual:**
```
    Critical 60%  ███████
    High 30%      ████
    Medium 10%    ██
```

---

### Step 7: Add Widget #6 - Blocked IPs Metric Card

```
┌─ Dashboard Edit Mode
│
├─ [Add Widget]
│  ├─ Type: Metric / Single Stat
│  ├─ Title: "Active Blocked IPs"
│  ├─ Index: wazuh-alerts-*
│  ├─ Metric: Unique count (cardinality)
│  ├─ Field: srcip
│  ├─ Display: Large number
│  └─ [Save]
│
└─ Result: Large card showing "9"
```

**Expected Visual:**
```
┌─────────────┐
│   ACTIVE    │
│   BLOCKED   │
│      9      │
│     IPs     │
└─────────────┘
```

---

## Verification Checklist

After adding all 6 widgets, verify:

```
✓ Widget 1: Timeline shows 9 data points over 26 days
✓ Widget 2: Bar chart shows US:4, RO:3, SG:1
✓ Widget 3: Map displays with red hotspots (Romania, US)
✓ Widget 4: Table shows all 9 IPs with correct metadata
✓ Widget 5: Pie chart shows severity levels
✓ Widget 6: Metric card displays "9"

✓ Dashboard title: "Threat Intelligence Summary"
✓ All widgets load without errors
✓ Time range: Last 60 days (or custom range)
✓ Data refreshes automatically (every 5 minutes)
```

---

## Save & Export

### In Dashboard UI

```
Dashboard > [Save] > [Confirm]
Dashboard > [⋮ More] > [Export] > [Copy JSON]
```

### In Terminal

```bash
# Create file with exported JSON
cat > docs/wazuh-threat-intelligence-dashboard.json << 'EOF'
[paste the copied JSON here]
EOF

# Verify file created
ls -lh docs/wazuh-threat-intelligence-dashboard.json

# Add to git
git add docs/wazuh-threat-intelligence-dashboard.json

# Commit
git commit -m "FEAT: Export Wazuh Threat Intelligence Summary dashboard

Exported dashboard JSON from Wazuh UI after creating:
- Attack Timeline widget (line chart)
- Top Countries widget (bar chart)
- World Heatmap widget (geographic visualization)
- Top Malicious IPs table widget
- Alert Severity Distribution pie chart
- Active Blocked IPs metric card

Dashboard shows 9 historically blocked IPs with geolocation
and alert severity information. Updates automatically as
new ALARM_INTEL events arrive from Firewalla."

# Push to remote
git push origin main
```

---

## Time Estimate Breakdown

```
Task                           Estimated Time    Cumulative
─────────────────────────────────────────────────────────
Create dashboard container     3 minutes         3 min
Add Timeline widget            7 minutes         10 min
Add Top Countries widget       7 minutes         17 min
Add World Map widget          8 minutes         25 min
Add Top IPs table             7 minutes         32 min
Add Severity chart            7 minutes         39 min
Add Blocked Count metric      5 minutes         44 min
Test all widgets              10 minutes        54 min
Export dashboard JSON         5 minutes         59 min
Commit to git                 5 minutes         64 min
─────────────────────────────────────────────────────────
TOTAL                         ~64 minutes       ~1 hour
```

---

## Dashboard Access After Creation

### View Dashboard

```
URL: https://10.10.10.40/app/dashboards/dashboard/threat-intelligence-summary
(exact URL depends on Wazuh auto-generated ID)
```

### Share Dashboard

```
1. In Wazuh, click [Share]
2. Copy dashboard link
3. Share with team
```

### Integrate with Other Systems

```
1. Export dashboard JSON (done above)
2. Share JSON with Grafana team
3. Import in other monitoring tools
4. Link from Slack notifications (Phase 9)
```

---

## If Something Goes Wrong

### Widget shows "No Data"

1. Check index name (should be `wazuh-alerts-*`)
2. Check time range (expand to "Last 90 days")
3. Verify field names (see PHASE8_DASHBOARD_ARCHITECTURE.md)
4. Check if Wazuh alerts are actually being collected

### Map widget won't load

1. Verify GeoIP enrichment enabled in Wazuh
2. Check if GeoIP.location field exists
3. Try refreshing dashboard
4. Check browser console for errors

### Wrong IP count in table

1. Verify filtering on ALARM_INTEL events
2. Check if all historical alerts are present
3. Expand time range if needed
4. Verify srcip field is populated

### Dashboard loads slowly

1. Narrow time range (e.g., "Last 30 days")
2. Reduce number of rows in table (limit to 20)
3. Check Wazuh server performance
4. Consider archiving old alerts

---

## Next Steps After Dashboard Complete

1. **Documentation:**
   - Add dashboard link to README.md
   - Add screenshot to docs/

2. **Notifications (Phase 9):**
   - Add dashboard link to Slack alerts
   - Include in automated email reports

3. **Integration:**
   - Mirror dashboard in Grafana
   - Export metrics to external systems

4. **Monitoring:**
   - Set up alerts for attack spikes
   - Review dashboard weekly for trends

---

**Ready to start building your dashboard?** 🎯

Open https://10.10.10.40 and follow the steps above!

