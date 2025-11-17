# GeoIP Visualizations Setup Guide

## Overview

The Threat Intelligence Summary dashboard now includes two geolocation visualizations that display where attacks are originating from geographically:

1. **Attack Origins - World Map** - Interactive map showing source IP locations
2. **Attack Origins by Country** - Bar chart showing attack counts by country

## Architecture

### Data Flow

```
Wazuh Alerts
    ↓
OpenSearch (Index: wazuh-alerts-*)
    ↓
Ingest Pipeline: wazuh-geoip
    ↓
GeoIP Processor (processes data.srcip)
    ↓
Enriched with geoip.* fields
    ↓
Visualizations
```

### Field Mapping

- **Existing Alerts**: Use `GeoLocation.location` field (Wazuh's default enrichment)
- **New Alerts**: Use `geoip.*` fields from ingest pipeline enrichment

#### GeoLocation Fields (Wazuh Default)
```
GeoLocation.country_name
GeoLocation.country_code2
GeoLocation.country_code3
GeoLocation.city_name
GeoLocation.region_name
GeoLocation.location (coordinates: lat, lon)
GeoLocation.latitude
GeoLocation.longitude
```

#### GeoIP Fields (Ingest Pipeline)
```
geoip.country_name
geoip.country_iso_code
geoip.city_name
geoip.location (geo_point: lat, lon)
```

## Configuration

### 1. OpenSearch Ingest Pipeline

**Name**: `wazuh-geoip`

**Configuration**:
```json
{
  "description": "GeoIP enrichment for Wazuh alerts",
  "processors": [
    {
      "geoip": {
        "field": "data.srcip",
        "target_field": "geoip",
        "ignore_missing": true,
        "ignore_failure": true
      }
    }
  ]
}
```

**Verification**:
```bash
curl -k -u admin:PASSWORD https://10.10.10.40:9200/_ingest/pipeline/wazuh-geoip | jq .
```

### 2. Index Template

**Template**: `wazuh` (applied to all `wazuh-alerts-*` indices)

**Key Setting**:
```json
"default_pipeline": "wazuh-geoip"
```

This ensures all new documents automatically flow through the GeoIP enrichment pipeline.

**Verification**:
```bash
curl -k -u admin:PASSWORD https://10.10.10.40:9200/_index_template/wazuh | jq .
```

### 3. MaxMind GeoIP Database

**Location**: `/usr/share/wazuh-indexer/geoip/`

**Database**: GeoLite2-City.mmdb (61MB)

**Permissions**:
```
-rw-r--r-- 1 wazuh-indexer wazuh-indexer
```

The OpenSearch GeoIP processor uses this database internally. The database was downloaded via MaxMind account with license key stored in `.env.wazuh`.

## Visualizations

### Attack Origins - World Map

- **Type**: Geographic coordinates/map visualization
- **Data Source**: `wazuh-alerts-*` index
- **Geospatial Field**: `GeoLocation.location` or `geoip.location`
- **Display**: Interactive map with pins showing attack origins
- **Controls**: Zoom, pan, toggle layers

### Attack Origins by Country

- **Type**: Horizontal bar chart
- **Data Source**: `wazuh-alerts-*` index
- **Aggregation**: Terms on `GeoLocation.country_name` (size: 15)
- **Metric**: Count of attacks per country
- **Sorting**: Descending by count

## Data Population

### Current Status

- **Existing Alerts** (before GeoIP pipeline setup): `GeoLocation.country_name` = null
- **New Alerts** (after GeoIP pipeline setup): Will have `geoip.country_name` populated

### Timeline

1. **Nov 17, 2025** - GeoIP pipeline configured and deployed
2. **Going Forward** - New threat alerts will be enriched with geolocation data
3. **Visualization Updates** - Charts will populate as new data flows in

### Expected Timeline

- Map visualization: Should show data immediately for any alerts with coordinates
- Country chart: Will populate once new threat alerts with source IPs arrive

## Troubleshooting

### Chart Shows "No results found"

**Cause**: The `GeoLocation.country_name` field has no data yet

**Solution**:
1. Wait for new threat alerts to be generated
2. Check that the `wazuh-geoip` pipeline is active:
   ```bash
   curl -k -u admin:PASSWORD https://10.10.10.40:9200/_ingest/pipeline/wazuh-geoip | jq .
   ```
3. Verify template has `default_pipeline` set:
   ```bash
   curl -k -u admin:PASSWORD https://10.10.10.40:9200/_index_template/wazuh | jq '.index_templates[0].template.settings.index.default_pipeline'
   ```

### Map Shows No Data

**Cause**: No geolocation coordinates available

**Solution**:
1. Check if `GeoLocation.location` field exists:
   ```bash
   curl -k -u admin:PASSWORD https://10.10.10.40:9200/wazuh-alerts-*/_search \
     -d '{"query":{"exists":{"field":"GeoLocation.location"}}}' | jq '.hits.total'
   ```

## Monitor GeoIP Enrichment

### Query for Enriched Alerts

```bash
# Check for geoip field in new alerts
curl -k -u admin:PASSWORD https://10.10.10.40:9200/wazuh-alerts-*/_search \
  -d '{"query":{"exists":{"field":"geoip"}}}' | jq '.hits.total'
```

### Sample Enriched Alert

```json
{
  "data": {
    "srcip": "203.0.113.42"
  },
  "geoip": {
    "country_name": "United States",
    "country_iso_code": "US",
    "city_name": "Los Angeles",
    "location": {
      "lat": 34.0522,
      "lon": -118.2437
    }
  }
}
```

## Future Improvements

1. **Update Country Chart** - Switch to `geoip.country_name` once data is populated
2. **Create Regional Heatmap** - Visualize attack density by region
3. **Add Time Series** - Show geolocation trends over time
4. **Filter by Severity** - Only show high-risk geolocation alerts
5. **Export Functionality** - Export geolocation threat reports

## Related Documentation

- [Wazuh GeoIP Configuration](https://documentation.wazuh.com/current/index.html)
- [OpenSearch Ingest Pipelines](https://opensearch.org/docs/latest/ingest-pipelines/)
- [MaxMind GeoLite2 Database](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data)
- [Threat Intelligence Dashboard](./THREAT_INTELLIGENCE_DASHBOARD.md)
