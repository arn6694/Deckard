# Phase 8: Dashboard Analytics - Planning Document

**Status:** Ready for Implementation
**Complexity:** Medium
**Est. Time:** 2-3 hours

---

## Overview

Create visual dashboards in Wazuh to track:
- Attack metrics (timeline, frequency, trends)
- Geographic origin of attacks (heatmap)
- Top malicious IPs
- Devices being targeted
- Block effectiveness

---

## What Needs to Be Done

### 1. Wazuh Dashboard Setup
- Access: https://10.10.10.40
- Create new dashboard named "Threat Intelligence Summary"
- Add widgets for attack visualization

### 2. Widget Types Needed
| Widget | Type | Data |
|--------|------|------|
| Attacks Timeline | Line Chart | timestamp vs alert count |
| Top Countries | Bar Chart | country_iso_code vs frequency |
| Top Malicious IPs | Table | srcip, country, alert_count |
| World Map | Geolocation | srcip locations |
| Severity Distribution | Pie Chart | alert.level distribution |
| Blocked IPs | Table | IPs from blocklist.txt |

### 3. Key Metrics to Track
- Attacks per hour/day/week
- Unique attacker IPs per week
- Countries with most attacks
- Most targeted internal devices
- Block success rate

### 4. Data Sources Available
- **Wazuh Alerts:** `/var/ossec/logs/alerts/alerts.json`
- **Blocked IPs:** `/etc/malware-blocklist.txt` (Firewalla)
- **Block Logs:** `/var/log/malware-blocks.log` (Firewalla)
- **Rules:** Custom ALARM_INTEL rules in Wazuh

---

## Resources Already Available

✅ **Documentation:** `docs/THREAT_INTELLIGENCE_TRACKING.md`
✅ **Data:** 9 historical attacks with geolocation
✅ **Integration:** Wazuh fully configured
✅ **Infrastructure:** All systems in place

---

## Implementation Approach

### Option A: Wazuh Native Dashboard (Recommended)
- Use Wazuh Dashboard UI
- Create visualizations directly in browser
- Export as JSON for version control
- **Pros:** Fast, no coding needed
- **Cons:** Limited customization

### Option B: Custom Kibana/OpenSearch
- Use Wazuh's Kibana integration
- Build custom visualizations
- More control over appearance
- **Pros:** Fully customizable
- **Cons:** Steeper learning curve

### Option C: Grafana Integration
- Query Wazuh API
- Build external dashboard
- **Pros:** Professional appearance
- **Cons:** Requires API auth setup

---

## Next Session Checklist

- [ ] Access Wazuh Dashboard at https://10.10.10.40
- [ ] Create new dashboard
- [ ] Add first widget (Attacks Timeline)
- [ ] Test geolocation visualization
- [ ] Export dashboard JSON
- [ ] Document in PHASE8_DASHBOARD_IMPLEMENTATION.md

---

## Quick Start Commands

```bash
# View sample alert data
ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.40 \
  'sudo cat /var/ossec/logs/alerts/alerts.json | jq '.agent,.rule,.data' | head -50'

# Count attacks by country (if GeoIP available)
ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.40 \
  'sudo grep "country" /var/ossec/logs/alerts/alerts.json | sort | uniq -c'

# Check Wazuh API availability
curl -s -u admin:password https://10.10.10.40/api/version
```

---

## Related Documentation

- `docs/THREAT_INTELLIGENCE_TRACKING.md` - TI setup guide
- `PHASE6_FINAL_STATUS.md` - Current system status
- `SESSION_CLOSING_REPORT_PHASE6_2025-11-17.md` - Phase 6 details

---

**Ready to start Phase 8 whenever you are!**
