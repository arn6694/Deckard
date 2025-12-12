# Wazuh Dashboard Import Guide - Phase 8

**Dashboard:** Threat Intelligence Summary
**Status:** Generated & Ready for Import
**File:** `docs/wazuh-threat-intelligence-dashboard.json`
**Created:** November 17, 2025

---

## Quick Import (5 Minutes)

### Method 1: Via Wazuh Dashboard UI (Easiest)

1. **Login to Wazuh Dashboard**
   - URL: https://10.10.10.40
   - Username: admin
   - Password: (your password)

2. **Navigate to Stack Management**
   - Click: Stack Management (left sidebar)
   - Or: Menu → Management → Stack Management

3. **Go to Saved Objects**
   - Click: Saved Objects
   - See: List of dashboards, visualizations, etc.

4. **Import Dashboard**
   - Click: Import
   - Select file: `docs/wazuh-threat-intelligence-dashboard.json`
   - Choose: "Check for existing objects"
   - Click: Import

5. **Verify Dashboard**
   - Navigate to: Dashboards
   - Find: "Threat Intelligence Summary"
   - Click: Open Dashboard
   - Expected: 6 widgets loading with data

---

## What Gets Imported

### Dashboard Container
- **Name:** Threat Intelligence Summary
- **ID:** threat-intelligence-summary
- **Description:** Real-time visualization of malicious IP detection, geolocation analysis, and automated blocking effectiveness

### 6 Visualizations
1. **Malicious IP Detections - Timeline** (line chart)
   - Shows: Attack frequency over time
   - Data: Count of alerts by date
   - Expected: ~9 data points over 26 days

2. **Attack Origins by Country** (horizontal bar chart)
   - Shows: Geographic distribution
   - Data: GeoIP.country field
   - Expected: US (4), Romania (3), Singapore (1)

3. **Attack Origins - World Heatmap** (geographic map)
   - Shows: Attack locations on world map
   - Data: GeoIP.location coordinates
   - Expected: Colored markers showing intensity

4. **Top Malicious IPs** (data table)
   - Shows: All detected IPs with metadata
   - Data: srcip + country + count
   - Expected: 9 rows with full details

5. **Alert Severity Distribution** (pie chart)
   - Shows: Severity level breakdown
   - Data: rule.level field
   - Expected: Critical > High > Medium

6. **Active Blocked IPs** (metric card)
   - Shows: Unique IP count
   - Data: Cardinality of srcip
   - Expected: "9"

---

## Troubleshooting Import

### "Import failed - invalid file format"
**Solution:**
- Verify file is valid JSON: `jq . docs/wazuh-threat-intelligence-dashboard.json`
- Check file size: `ls -lh docs/wazuh-threat-intelligence-dashboard.json`
- Expected: ~9 KB file size

### "Objects already exist"
**Solution:**
- If dashboard exists, choose "Overwrite existing objects"
- Or delete old dashboard first, then import

### "Visualizations not loading"
**Solution:**
- Check Wazuh alert data exists: https://10.10.10.40/app/dev_tools#/console
- Run query: `GET wazuh-alerts-*/_search`
- Verify results show alert data

### "Index pattern not found"
**Solution:**
- Dashboard expects: `wazuh-alerts-*` index
- Verify index exists in Wazuh
- If not: Check Wazuh agent is running on Firewalla

---

## After Import - Verification

### 1. Check Dashboard Loads

```bash
# Open in browser
https://10.10.10.40/app/dashboards/dashboard/threat-intelligence-summary
```

### 2. Verify Widgets Load

Each widget should show:
- ✅ Timeline: Line chart with data points
- ✅ Countries: Bars for US, Romania, Singapore
- ✅ Map: World map with colored markers
- ✅ IPs: Table showing 9 rows
- ✅ Severity: Pie chart with levels
- ✅ Metric: Number "9"

### 3. Test Auto-Refresh

```bash
# Dashboard should update every 5 minutes
# Verify by checking time display in Wazuh UI

# Or manually refresh
# Press: F5 in browser
```

### 4. Check Data Accuracy

Expected values:
- Total attacks: 9
- US attacks: 4
- Romania attacks: 3
- Singapore attacks: 1
- Date range: Oct 22 - Nov 16

---

## Dashboard Customization (Optional)

After import, you can customize:

### Change Title
1. Open Dashboard
2. Click: Edit
3. Change: Title field
4. Click: Save

### Adjust Widget Size
1. Open Dashboard
2. Click: Edit
3. Drag: Widget corners to resize
4. Click: Save

### Change Time Range
1. Open Dashboard
2. Top left: Time picker
3. Select: Last 30 days (or custom range)
3. Widgets: Auto-update

### Add More Widgets
1. Open Dashboard
2. Click: Add panel
3. Create new visualization
4. Click: Save

---

## Integration with Phase 6

Dashboard visualizes results from Phase 6 (n8n blocking):

```
Phase 6 → Firewalla detects attack → ALARM_INTEL event
         ↓
Wazuh → Receives alert → Triggers webhook → n8n blocks IP
         ↓
Blocked IP stored in Wazuh alerts.json
         ↓
Phase 8 → Dashboard QUERIES alerts.json
         ↓
Visualizations SHOW blocked IPs in real-time
```

When new attacks occur:
1. Firewalla detects → n8n blocks IP (Phase 6)
2. Alert appears in Wazuh
3. Dashboard auto-updates within 5 minutes
4. New IP appears in all widgets

---

## Data Refresh & Updates

### Auto-Refresh Settings
- **Interval:** Every 5 minutes (300 seconds)
- **Can be changed:** Top right of dashboard
- **Manual refresh:** Press F5 or click refresh icon

### Data Sources
- **Index:** wazuh-alerts-*
- **Update rate:** Real-time as alerts arrive
- **History:** Last 60 days (configurable)

### Expected Update Pattern
```
Time: 00:00 → 9 blocked IPs shown
Time: 01:00 → Auto-refresh checks for new alerts
Time: 02:00 → If new attack detected, all widgets update
            → Timeline shows new point
            → Table shows new IP
            → Country bar updates if new country
            → Metric increases if new unique IP
```

---

## Success Criteria

✅ **Import Successful** - Dashboard appears in Wazuh UI
✅ **Widgets Load** - All 6 widgets show data
✅ **Data Accurate** - Shows 9 blocked IPs with correct countries
✅ **Updates Real-time** - Auto-refresh working every 5 min
✅ **Integrated** - Shows Phase 6 blocking results

---

**Import Time:** ~5 minutes
**Difficulty:** Easy (UI-based)
**Data Accuracy:** 100% (automated from actual alerts)

Ready to import? Open the dashboard file and follow Method 1 above! 🚀
