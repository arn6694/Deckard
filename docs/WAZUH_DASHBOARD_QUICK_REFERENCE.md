# Wazuh Dashboard Quick Reference - Phase 8

**Status:** Ready to implement
**Complexity:** Medium (UI-based, no coding)
**Estimated Time:** 1-2 hours

---

## Quick Start

1. **URL:** https://10.10.10.40
2. **Navigate:** Dashboards → Create Dashboard
3. **Name:** `Threat Intelligence Summary`
4. **Description:** Real-time visualization of malicious IP detection and automated blocking

---

## Data You'll Visualize

### Historical Blocked IPs (9 Total)

```
US (4 IPs)          Romania (3 IPs)      Singapore (1 IP)
142.93.115.5        78.153.140.177       178.128.95.222
66.240.205.34       78.153.140.179
45.148.10.243       78.153.140.224
66.235.168.222

Time Range: Oct 22 - Nov 16, 2025
Frequency: ~1 attack every 3 days
```

---

## Widget Types & Configuration

| # | Widget | Type | Field | Result |
|---|--------|------|-------|--------|
| 1 | Attack Timeline | Line Chart | timestamp | 9 alerts over 26 days |
| 2 | Top Countries | Bar Chart | Country | US:4, RO:3, SG:1 |
| 3 | World Map | Geo Map | GeoIP location | Red hotspots on map |
| 4 | Top IPs | Table | srcip | All 9 IPs sorted |
| 5 | Alert Severity | Pie Chart | alert.level | Critical > High > Med |
| 6 | Blocked Count | Metric | Unique count | Shows "9" |

---

## Step-by-Step Widget Creation

### For Each Widget:

1. Click **Add Widget** button
2. Select widget type
3. Configure:
   - **Title:** Use names from table above
   - **Data:** Select Wazuh alerts index
   - **Metric:** Count (most cases)
   - **Buckets:** See field names in table above
4. Click **Save**
5. Adjust size/position as needed

---

## Index Selection

When asked to select an index:
- **Look for:** `wazuh-alerts-*` or `alerts-*`
- **Not:** `metrics-*` or `logs-*`
- **Time Field:** `timestamp`

---

## Field Names to Use

**For Aggregations:**
- Dates: `timestamp` (for timeline)
- Locations: `GeoIP.location` or `geoip.location`
- Countries: `GeoIP.country_iso_code` or `geoip.country_code`
- Source IPs: `srcip` or `source.ip`
- Severity: `alert.level` or `severity`

**Exact field names may vary - check your Wazuh schema**

---

## Testing Widgets

After adding each widget:

1. **Check for data:** Widget should show results immediately
2. **If empty:** Click widget → Edit → Verify field names
3. **Check counts:**
   - Total alerts should match historical data
   - Countries should be US, RO, SG
   - Unique IPs should be 9

---

## Export for Version Control

After all widgets are added:

1. Open dashboard
2. Click **More** (⋮) → **Export**
3. Copy full JSON
4. Save to: `docs/wazuh-threat-intelligence-dashboard.json`

```bash
# Command to save (after copying JSON):
cat > docs/wazuh-threat-intelligence-dashboard.json << 'EOF'
[paste JSON here]
EOF

git add docs/wazuh-threat-intelligence-dashboard.json
git commit -m "FEAT: Add Wazuh Threat Intelligence Summary dashboard"
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Widget shows "No data" | Check index name and field names match Wazuh schema |
| Map widget won't load | Ensure GeoIP enrichment is enabled in Wazuh |
| Wrong time range | Click time filter → Adjust to "Last 60 days" |
| Can't find index | Go to Discover first to verify available indices |

---

## Links to Detailed Docs

- **Full Implementation Guide:** `PHASE8_DASHBOARD_IMPLEMENTATION.md`
- **Threat Data Reference:** `docs/THREAT_INTELLIGENCE_TRACKING.md`
- **Query Examples:** `PHASE8_DASHBOARD_IMPLEMENTATION.md` → "Query Reference"
- **Phase 6 (Blocking Context):** `PHASE6_FINAL_STATUS.md`

---

## After Dashboard is Complete

1. ✅ Export dashboard JSON
2. ✅ Commit to git
3. ✅ Update README.md with dashboard link
4. ✅ Document in PHASE8_DASHBOARD_IMPLEMENTATION.md
5. ✅ Consider: Add dashboard URL to monitoring alerts

---

**Ready to start?** Open https://10.10.10.40 and begin creating!

