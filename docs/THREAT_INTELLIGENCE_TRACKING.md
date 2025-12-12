# Threat Intelligence Tracking & Geolocation Analysis

**Status:** Ready for Integration with Wazuh Dashboard

This document describes how to use Wazuh's built-in capabilities to track malicious IPs and visualize attack patterns with geolocation heatmaps.

---

## Currently Blocked IPs (9 Total)

| IP | Alert Date | Country Code | Status |
|----|------------|--------------|--------|
| 142.93.115.5 | 11/16/2025 12:29am | US-DigitalOcean | ✅ Blocked |
| 78.153.140.177 | 11/12/2025 3:30pm | RO | ✅ Blocked |
| 78.153.140.179 | 11/7/2025 8:30pm | RO | ✅ Blocked |
| 66.240.205.34 | 11/7/2025 1:13pm | US | ✅ Blocked |
| 178.128.95.222 | 11/5/2025 12:20am | SG | ✅ Blocked |
| 45.148.10.243 | 11/2/2025 10:29pm | US | ✅ Blocked |
| 66.235.168.222 | 11/2/2025 1am | US | ✅ Blocked |
| 66.240.205.34 | 10/23/2025 2:00pm | US | ✅ Blocked |
| 78.153.140.224 | 10/22/2025 9:14am | RO | ✅ Blocked |

**Pattern Observed:**
- 🇷🇴 Romania (78.153.x.x range): 3 IPs (heaviest concentration)
- 🇺🇸 United States: 4 IPs (DigitalOcean, AWS, etc.)
- 🇸🇬 Singapore: 1 IP
- **Peak Activity:** November 7-16 (recent week)

---

## Wazuh Threat Intelligence Integration

Wazuh can automatically fetch threat intelligence data and correlate it with incoming alerts.

### Available TI Sources in Wazuh

1. **AbusIPDB** - Crowd-sourced IP reputation database
2. **AlienVault OTX** - Open Threat Exchange
3. **Custom TI Feeds** - Feed URLs you provide

### Setup Steps

#### Step 1: Access Wazuh Manager

```bash
ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.40
```

#### Step 2: Enable Vulnerability Detection

Edit `/var/ossec/etc/ossec.conf`:

```xml
<!-- Enable IP reputation lookups -->
<vulnerability-detection>
  <enabled>yes</enabled>
  <feed-update-interval>3600</feed-update-interval>
</vulnerability-detection>
```

#### Step 3: Add Custom IP Blocklist

Create file: `/var/ossec/etc/custom_blocklist.txt`

```
# Format: IP | Description | Severity
142.93.115.5 | Old attack - DigitalOcean | 10
78.153.140.177 | Old attack - Romania botnet | 10
78.153.140.179 | Old attack - Romania botnet | 10
66.240.205.34 | Old attack - US attacker | 10
178.128.95.222 | Old attack - Singapore | 10
45.148.10.243 | Old attack - US attacker | 10
66.235.168.222 | Old attack - US attacker | 10
78.153.140.224 | Old attack - Romania botnet | 10
```

#### Step 4: Create Detection Rules for Custom Blocklist

Add to `/var/ossec/etc/rules/custom_ti.xml`:

```xml
<group name="threat_intelligence,">
  <!-- Detect access from custom blocklist -->
  <rule id="100060" level="10">
    <if_sid>5701</if_sid>
    <field name="srcip">^(142\.93\.115\.5|78\.153\.140\.(177|179|224)|66\.240\.205\.34|178\.128\.95\.222|45\.148\.10\.243|66\.235\.168\.222)$</field>
    <description>Access from known malicious IP (custom blocklist)</description>
    <group>intrusion_attempt,custom_ti</group>
  </rule>
</group>
```

---

## Geolocation Heatmap Setup

### Using Wazuh Dashboard

#### Method 1: Built-in Geolocation Widget

1. **Access Wazuh Dashboard:** https://10.10.10.40
2. **Navigate to:** Threat Intelligence → Geolocation
3. **Widget appears automatically** once IPs have geolocation data

#### Method 2: Custom Visualization (Advanced)

In Wazuh Dashboard → Discover:

1. **Filter:** `alert.data.srcip:*`
2. **Visualize:** Create new dashboard
3. **Add Map widget:**
   - X-axis: `alert.GeoIP.country_iso_code`
   - Size: Count of occurrences
   - Color: Alert severity level

### Expected Map View

```
World Map Showing Attack Origins:
╔═══════════════════════════════════╗
║  🟥 Romania (3 attacks)           ║
║  🟧 USA (4 attacks)               ║
║  🟨 Singapore (1 attack)          ║
║  Color intensity = frequency      ║
╚═══════════════════════════════════╝
```

---

## Query Patterns for Analysis

### Query 1: All Attacks This Month

```
alert.data.srcip:* AND timestamp:[2025-11-01 TO 2025-11-30]
```

### Query 2: Top 5 Attacking Countries

```
Terms aggregation on: alert.GeoIP.country_name
Size: 5
```

### Query 3: Attacks by Hour of Day

```
Date histogram on: timestamp
Interval: hourly
Filter: ALARM_INTEL alerts only
```

### Query 4: Most Attacked Internal Device

```
Terms aggregation on: alert.data.destip
Size: 10
Filter: alert.rule.id:100050 (ALARM_INTEL)
```

---

## Automated TI Updates

### Option 1: Wazuh's Built-in TI Feeds

Add to `/var/ossec/etc/ossec.conf`:

```xml
<vulnerability-detection>
  <enabled>yes</enabled>
  <feed>
    <name>AlienVault OTX</name>
    <url>https://otx.alienvault.com/api/v1/pulses/subscribed?limit=20</url>
    <update_interval>3600</update_interval>
  </feed>
</vulnerability-detection>
```

### Option 2: Custom Feed (Your Blocklist)

Create `/var/ossec/etc/custom_ti_feed.json`:

```json
{
  "threat_intelligence": [
    {
      "ip": "142.93.115.5",
      "description": "Old attack - DigitalOcean",
      "severity": 10,
      "first_seen": "2025-10-23",
      "last_seen": "2025-11-16",
      "attack_count": 4
    },
    {
      "ip": "78.153.140.0/24",
      "description": "Romania botnet C&C range",
      "severity": 9,
      "country": "RO",
      "attack_count": 3
    }
  ]
}
```

---

## Analytics Dashboard Creation

### Manual Dashboard in Wazuh

1. **Create new dashboard:** Dashboards → + New Dashboard
2. **Name:** "Threat Intelligence Summary"
3. **Add widgets:**

| Widget Name | Type | Data Source |
|-------------|------|-------------|
| Attacks Timeline | Line Chart | timestamp vs alert count |
| Top Countries | Bar Chart | country_iso_code vs frequency |
| Top IPs | Table | srcip, country, alert_count |
| World Map | Geolocation Map | srcip geolocation |
| Severity Distribution | Pie Chart | alert.level distribution |

### Example JSON Export

Once created, export dashboard as JSON for version control:

```bash
# In Wazuh UI:
# Dashboard → Settings → Export → Download JSON
# Save as: /home/brian/claude/docs/wazuh-ti-dashboard.json
```

---

## Metrics to Track

### Real-Time Metrics

- **Attacks per hour** - Detect surge patterns
- **Top attacking countries** - Identify geographic threats
- **Top attacking IPs** - Spot repeat offenders
- **Most targeted devices** - Prioritize defense

### Trend Analysis

- **Weekly comparison** - Increasing or decreasing trend?
- **Seasonal patterns** - More attacks at certain times?
- **New IP detection rate** - How many unique attackers per week?
- **Blocklist effectiveness** - Repeat blocked IPs dropped?

### KPIs for Reporting

- **Mean Time to Block (MTTB)** - Currently ~0-5 seconds with n8n
- **Unique IPs blocked per week** - Track blocklist growth
- **Attack volume trend** - Increasing/stable/decreasing
- **Geographic diversity** - How many countries represented?

---

## Future Enhancements

### Phase 8 (Planned)

1. **Automated TI Feed Updates**
   - Daily pull from AlienVault OTX
   - Auto-update blocklist

2. **Predictive Analytics**
   - ML models for attack pattern prediction
   - Anomaly detection on new attack types

3. **Integration with External TI**
   - MISP (Malware Information Sharing Platform)
   - Shodan API lookups

4. **Historical Correlation**
   - Link similar attacks across weeks
   - Identify coordinated campaigns

---

## Data Export & Archival

### Weekly Export

```bash
# Schedule with cron
0 0 * * 1  # Every Monday at midnight

# Export alerts to CSV
curl -s -k \
  -H "Authorization: Bearer <WAZUH_TOKEN>" \
  "https://10.10.10.40/api/events?query=ALARM_INTEL" \
  > /var/backups/ti_export_$(date +%Y-%m-%d).csv
```

### Data Retention

- **Live dashboard:** Last 30 days (configurable)
- **Archive:** 90-day rolling backup
- **Historical:** Compress monthly summaries

---

## Security Considerations

### TI Feed Validation

- **Trust Score:** Only accept high-confidence feeds
- **Source Verification:** Validate TI feed signatures
- **False Positive Rate:** Monitor blocklist for mistakes

### Privacy

- **IP Anonymization:** Option to mask internal IPs in reports
- **GeoIP Accuracy:** Note that city-level GeoIP has 50-100km variance
- **Data Retention:** Comply with any regulatory requirements

---

## Quick Commands

```bash
# View Wazuh TI integration status
ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.40 \
  'sudo systemctl status wazuh-manager | grep -i threat'

# Check custom blocklist
ssh -i /home/brian/.ssh/id_rsa brian@10.10.10.40 \
  'sudo cat /var/ossec/etc/custom_blocklist.txt'

# Query Wazuh API for TI events
curl -k -u admin:password \
  'https://10.10.10.40/api/events?query=ALARM_INTEL&limit=100'

# Export blocklist from Firewalla
ssh brian@10.10.10.1 'sudo cat /etc/malware-blocklist.txt | grep -v "^#"'
```

---

## References

- **Wazuh TI Docs:** https://documentation.wazuh.com/current/user-manual/capabilities/threat-intelligence/
- **AlienVault OTX:** https://otx.alienvault.com/
- **GeoIP2 Free:** https://dev.maxmind.com/geoip/geolite2-free-geolocation-data/

---

**Status:** Setup documentation complete. Ready for implementation in Phase 8 (Dashboard Analytics).

**Next Steps:**
1. Configure Wazuh geolocation in dashboard
2. Create custom TI feed for blocked IPs
3. Set up automated weekly exports
4. Build threat intelligence dashboard

